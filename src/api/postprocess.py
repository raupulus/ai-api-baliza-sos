"""Post-proceso de la respuesta del LLM al formato de mensajería restringida.

Convierte el texto crudo en 1–3 mensajes de <= 230 bytes UTF-8 (configurable).
El límite de bytes garantiza que los paquetes entren limpiamente en el payload de
radio de Meshtastic (LoRa MTU ~237 bytes útiles), teniendo en cuenta tildes, ñ y
caracteres especiales en español.

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
    aviso: str | None = None


def _len_bytes(texto: str) -> int:
    """Devuelve la longitud en bytes de la cadena codificada en UTF-8."""
    return len(texto.encode("utf-8"))


def _slice_utf8_bytes(texto: str, max_bytes: int) -> str:
    """Recorta el texto a un máximo de max_bytes sin romper secuencias multibyte UTF-8."""
    encoded = texto.encode("utf-8")
    if len(encoded) <= max_bytes:
        return texto
    return encoded[:max_bytes].decode("utf-8", errors="ignore")


def _limpiar(texto: str) -> str:
    return _WS.sub(" ", texto).strip()


def _trocear_frases(texto: str) -> list[str]:
    frases = [f.strip() for f in _FRASE.findall(texto) if f.strip()]
    return frases or ([texto] if texto else [])


def _empaquetar(frases: list[str], max_bytes: int, max_msgs: int) -> tuple[list[str], bool]:
    """Empaqueta frases en mensajes <= max_bytes UTF-8, hasta max_msgs."""
    mensajes: list[str] = []
    actual = ""
    pendientes_truncadas = False

    for frase in frases:
        # Una frase sola más larga que el límite: se trocea de forma dura.
        if _len_bytes(frase) > max_bytes:
            if actual:
                mensajes.append(actual)
                actual = ""
            trozos = _trocear_duro(frase, max_bytes)
            for t in trozos:
                if len(mensajes) >= max_msgs:
                    pendientes_truncadas = True
                    break
                mensajes.append(t)
            continue

        candidato = f"{actual} {frase}".strip() if actual else frase
        if _len_bytes(candidato) <= max_bytes:
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


def _trocear_duro(texto: str, max_bytes: int) -> list[str]:
    """Trocea por palabras de forma segura cuando una frase excede max_bytes."""
    palabras = texto.split()
    trozos: list[str] = []
    actual = ""
    for p in palabras:
        candidato = f"{actual} {p}".strip() if actual else p
        if _len_bytes(candidato) <= max_bytes:
            actual = candidato
        else:
            if actual:
                trozos.append(actual)
            # Si la palabra sola excede el límite, recortar por bytes de forma segura
            actual = _slice_utf8_bytes(p, max_bytes)
    if actual:
        trozos.append(actual)
    return trozos


def _añadir_aviso(mensajes: list[str], max_bytes: int, max_msgs: int, aviso: str) -> list[str]:
    """Inserta el aviso médico sin romper el límite de max_bytes UTF-8."""
    if not mensajes:
        return [_slice_utf8_bytes(aviso, max_bytes)]
    # Si ya está presente, no duplicar.
    if any(aviso.lower() in m.lower() for m in mensajes):
        return mensajes
    # ¿Cabe pegado al último mensaje?
    ultimo = mensajes[-1]
    candidato = f"{ultimo} {aviso}"
    if _len_bytes(candidato) <= max_bytes:
        mensajes[-1] = candidato
        return mensajes
    # Si hay hueco de mensajes, añadir como mensaje propio.
    if len(mensajes) < max_msgs:
        mensajes.append(_slice_utf8_bytes(aviso, max_bytes))
        return mensajes
    # Sin hueco: sacrificar el final del último mensaje para encajar el aviso.
    espacio_bytes = max_bytes - _len_bytes(aviso) - 1
    if espacio_bytes > 0:
        mensajes[-1] = f"{_slice_utf8_bytes(ultimo, espacio_bytes).rstrip()} {aviso}"
    else:
        mensajes[-1] = _slice_utf8_bytes(aviso, max_bytes)
    return mensajes


def formatear(
    texto_crudo: str,
    *,
    categoria: Categoria | None = None,
    max_bytes: int | None = None,
    max_chars: int | None = None,
    max_msgs: int | None = None,
    aviso_medico: str | None = None,
    incluir_aviso_en_mensajes: bool = False,
) -> RespuestaFormateada:
    """Devuelve los mensajes listos para el cliente (1–N, cada uno <= max_bytes UTF-8).

    max_chars se mantiene por compatibilidad hacia atrás; si se especifica, actúa
    como límite en bytes.
    Por defecto, los metadatos y avisos médicos van fuera de `mensajes` (en `r.aviso`).
    """
    limite_bytes = (
        max_bytes
        or max_chars
        or getattr(settings, "resp_max_bytes_per_msg", 200)
    )
    max_msgs = max_msgs or settings.resp_max_messages
    aviso = aviso_medico if aviso_medico is not None else settings.resp_disclaimer_medico

    texto = _limpiar(texto_crudo)
    if not texto:
        return RespuestaFormateada(mensajes=[], truncado=False, aviso=None)

    frases = _trocear_frases(texto)
    mensajes, truncado = _empaquetar(frases, limite_bytes, max_msgs)

    aviso_aplicable = aviso if (categoria in CATEGORIAS_CON_AVISO and aviso) else None

    # Solo si explícitamente se solicita meter el aviso dentro de los paquetes de radio
    if incluir_aviso_en_mensajes and aviso_aplicable:
        antes = list(mensajes)
        mensajes = _añadir_aviso(mensajes, limite_bytes, max_msgs, aviso_aplicable)
        # Si para meter el aviso hubo que recortar, marcamos truncado.
        if mensajes != antes and any(_len_bytes(a) >= limite_bytes for a in antes):
            truncado = True

    # Garantía dura de los límites en bytes UTF-8.
    mensajes = [_slice_utf8_bytes(m, limite_bytes) for m in mensajes][:max_msgs]
    return RespuestaFormateada(mensajes=mensajes, truncado=truncado, aviso=aviso_aplicable)
