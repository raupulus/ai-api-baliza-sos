"""Construcción del bloque de contexto para el prompt a partir de los fragmentos
recuperados. Lógica pura (sin red ni BD), fácilmente testeable.
"""

from __future__ import annotations

from dataclasses import dataclass

from common.config import settings
from common.models import Categoria, FragmentoRecuperado


@dataclass
class ContextoRAG:
    texto: str                       # bloque [CONTEXTO] para el prompt
    fuentes: list[dict]              # [{titulo, fecha, url}] para la respuesta
    categoria: Categoria | None     # categoría dominante de lo recuperado
    confianza: float                # score máximo (0 si no hay nada)
    suficiente: bool                # False => responder con cautela, no inventar


def _orden(frag: FragmentoRecuperado) -> tuple:
    # Prioriza confianza alta y luego score.
    peso_conf = {"alta": 2, "media": 1, "baja": 0}
    return (peso_conf.get(frag.fragmento.nivel_confianza.value, 0), frag.score)


def construir_contexto(
    recuperados: list[FragmentoRecuperado],
    *,
    max_chars: int | None = None,
) -> ContextoRAG:
    """Ensambla el contexto respetando el límite de caracteres.

    Si no hay fragmentos por encima del umbral, devuelve `suficiente=False` para
    que la API responda con cautela (nunca inventar).
    """
    max_chars = max_chars or settings.rag_max_context_chars

    if not recuperados:
        return ContextoRAG(texto="", fuentes=[], categoria=None, confianza=0.0, suficiente=False)

    ordenados = sorted(recuperados, key=_orden, reverse=True)

    lineas: list[str] = []
    fuentes: list[dict] = []
    vistas_fuentes: set[str] = set()
    usados = 0
    total = 0

    for r in ordenados:
        frag = r.fragmento
        entrada = f"- {frag.texto}"
        if total + len(entrada) > max_chars and usados > 0:
            break
        lineas.append(entrada)
        total += len(entrada)
        usados += 1
        clave = f"{frag.fuente}|{frag.fuente_url}"
        if clave not in vistas_fuentes:
            vistas_fuentes.add(clave)
            fuentes.append({
                "titulo": frag.fuente,
                "fecha": frag.fecha.isoformat() if frag.fecha else None,
                "url": frag.fuente_url,
            })

    # Categoría dominante = la del fragmento mejor situado.
    categoria = ordenados[0].fragmento.categoria
    confianza = max(r.score for r in ordenados)

    return ContextoRAG(
        texto="\n".join(lineas),
        fuentes=fuentes,
        categoria=categoria,
        confianza=round(confianza, 3),
        suficiente=True,
    )
