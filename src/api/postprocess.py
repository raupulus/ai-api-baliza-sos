"""Post-proceso de la respuesta del LLM al formato de mensajería restringida.

Convierte el texto crudo en 1–3 mensajes de <= 250 caracteres (configurable).
Objetivo: 1 mensaje; usar más solo si es estrictamente necesario. Añade el aviso
médico cuando corresponde. Lógica pura, sin dependencias de red/BD.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from common.config import settings
from common.models import Categoria

# Categorías en las que se añade el aviso "Llama al 112".
CATEGORIAS_CON_AVISO = {Categoria.PRIMEROS_AUXILIOS, Categoria.FAUNA}

_WS = re.compile(r"\s+")
# Corte por fin de frase manteniendo el signo de puntuación.
_FRASE = re.compile(r"[^.!?\n]+[.!?]?", re.UNICODE)


@dataclass
class RespuestaFormateada:
    mensajes: list[str]
    truncado: bool


def _limpiar(texto: str) -> str:
    return _WS.sub(" ", texto).strip()


def _trocear_frases(texto: str) -> list[str]:
    frases = [f.strip() for f in _FRASE.findall(texto) if f.strip()]
    return frases or ([texto] if texto else [])


def _empaquetar(frases: list[str], max_chars: int, max_msgs: int) -> tuple[list[str], bool]:
    """Empaqueta frases en mensajes <= max_chars, hasta max_msgs."""
    mensajes: list[str] = []
    actual = ""
    pendientes_truncadas = False

    for frase in frases:
        # Una frase sola más larga que el límite: se trocea de forma dura.
        if len(frase) > max_chars:
            if actual:
                mensajes.append(actual)
                actual = ""
            trozos = _trocear_duro(frase, max_chars)
            for t in trozos:
                if len(mensajes) >= max_msgs:
                    pendientes_truncadas = True
                    break
                mensajes.append(t)
            continue

        candidato = f"{actual} {frase}".strip() if actual else frase
        if len(candidato) <= max_chars:
            actual = candidato
        else:
            if actual:
                mensajes.append(actual)
            actual = frase
            if len(mensajes) >= max_msgs:
                pendientes_truncadas = True
                actual = ""
                break

    if actual and len(mensajes) < max_msgs:
        mensajes.append(actual)
    elif actual:
        pendientes_truncadas = True

    return mensajes[:max_msgs], pendientes_truncadas


def _trocear_duro(texto: str, max_chars: int) -> list[str]:
    """Trocea por palabras cuando una frase excede el límite."""
    palabras = texto.split()
    trozos: list[str] = []
    actual = ""
    for p in palabras:
        candidato = f"{actual} {p}".strip()
        if len(candidato) <= max_chars:
            actual = candidato
        else:
            if actual:
                trozos.append(actual)
            actual = p[:max_chars]
    if actual:
        trozos.append(actual)
    return trozos


def _añadir_aviso(mensajes: list[str], max_chars: int, max_msgs: int, aviso: str) -> list[str]:
    """Inserta el aviso médico sin romper los límites."""
    if not mensajes:
        return [aviso[:max_chars]]
    # Si ya está presente, no duplicar.
    if any(aviso.lower() in m.lower() for m in mensajes):
        return mensajes
    # ¿Cabe pegado al último mensaje?
    ultimo = mensajes[-1]
    if len(ultimo) + 1 + len(aviso) <= max_chars:
        mensajes[-1] = f"{ultimo} {aviso}"
        return mensajes
    # Si hay hueco de mensajes, añadir como mensaje propio.
    if len(mensajes) < max_msgs:
        mensajes.append(aviso[:max_chars])
        return mensajes
    # Sin hueco: sacrificar el final del último mensaje para encajar el aviso.
    espacio = max_chars - len(aviso) - 1
    if espacio > 0:
        mensajes[-1] = f"{ultimo[:espacio].rstrip()} {aviso}"
    else:
        mensajes[-1] = aviso[:max_chars]
    return mensajes


def formatear(
    texto_crudo: str,
    *,
    categoria: Categoria | None = None,
    max_chars: int | None = None,
    max_msgs: int | None = None,
    aviso_medico: str | None = None,
) -> RespuestaFormateada:
    """Devuelve los mensajes listos para el cliente (1–N, cada uno <= max_chars)."""
    max_chars = max_chars or settings.resp_max_chars_per_msg
    max_msgs = max_msgs or settings.resp_max_messages
    aviso = aviso_medico if aviso_medico is not None else settings.resp_disclaimer_medico

    texto = _limpiar(texto_crudo)
    if not texto:
        return RespuestaFormateada(mensajes=[], truncado=False)

    frases = _trocear_frases(texto)
    mensajes, truncado = _empaquetar(frases, max_chars, max_msgs)

    if categoria in CATEGORIAS_CON_AVISO and aviso:
        antes = list(mensajes)
        mensajes = _añadir_aviso(mensajes, max_chars, max_msgs, aviso)
        # Si para meter el aviso hubo que recortar, marcamos truncado.
        if mensajes != antes and any(len(a) >= max_chars for a in antes):
            truncado = True

    # Garantía dura de los límites.
    mensajes = [m[:max_chars] for m in mensajes][:max_msgs]
    return RespuestaFormateada(mensajes=mensajes, truncado=truncado)
