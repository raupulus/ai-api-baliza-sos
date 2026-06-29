"""Indexado de fragmentos en pgvector (upsert idempotente por hash_contenido).

Lo usa el servicio actualizador al volcar fragmentos aprobados, y los scripts de
carga de corpus semilla.
"""

from __future__ import annotations

import logging
from typing import Iterable

from api.rag.embeddings import get_embedder
from common.db import cursor
from common.models import Fragmento

_log = logging.getLogger(__name__)

_UPSERT = """
INSERT INTO fragmentos (
    texto, fuente, fuente_url, fecha, categoria, subcategoria, provincia,
    nivel_confianza, licencia, peligrosa, validado_por, validado_fecha,
    hash_contenido, embedding
) VALUES (
    %(texto)s, %(fuente)s, %(fuente_url)s, %(fecha)s, %(categoria)s,
    %(subcategoria)s, %(provincia)s, %(nivel_confianza)s, %(licencia)s,
    %(peligrosa)s, %(validado_por)s, %(validado_fecha)s, %(hash_contenido)s,
    %(embedding)s
)
ON CONFLICT (hash_contenido) DO UPDATE SET
    texto = EXCLUDED.texto,
    fuente_url = EXCLUDED.fuente_url,
    fecha = EXCLUDED.fecha,
    subcategoria = EXCLUDED.subcategoria,
    provincia = EXCLUDED.provincia,
    nivel_confianza = EXCLUDED.nivel_confianza,
    licencia = EXCLUDED.licencia,
    peligrosa = EXCLUDED.peligrosa,
    validado_por = EXCLUDED.validado_por,
    validado_fecha = EXCLUDED.validado_fecha,
    embedding = EXCLUDED.embedding
RETURNING (xmax = 0) AS insertado;
"""


def _row(frag: Fragmento, embedding: list[float]) -> dict:
    return {
        "texto": frag.texto,
        "fuente": frag.fuente,
        "fuente_url": frag.fuente_url,
        "fecha": frag.fecha,
        "categoria": frag.categoria.value,
        "subcategoria": frag.subcategoria,
        "provincia": frag.provincia,
        "nivel_confianza": frag.nivel_confianza.value,
        "licencia": frag.licencia,
        "peligrosa": frag.peligrosa,
        "validado_por": frag.validado_por,
        "validado_fecha": frag.validado_fecha,
        "hash_contenido": frag.hash_contenido,
        "embedding": embedding,
    }


def index_fragmentos(fragmentos: Iterable[Fragmento]) -> tuple[int, int]:
    """Genera embeddings e inserta/actualiza los fragmentos.

    SEGURIDAD: rechaza fragmentos sensibles sin validar (defensa en profundidad;
    el actualizador ya filtra antes, pero aquí volvemos a comprobarlo).

    Devuelve (nuevos, actualizados).
    """
    frags = list(fragmentos)
    if not frags:
        return (0, 0)

    sin_validar = [f for f in frags if f.requiere_validacion and not f.validado]
    if sin_validar:
        raise ValueError(
            f"{len(sin_validar)} fragmento(s) sensibles sin validar; "
            "no se pueden indexar (requieren checkpoint humano)."
        )

    embeddings = get_embedder().embed_passages([f.texto for f in frags])

    nuevos = actualizados = 0
    with cursor() as cur:
        for frag, emb in zip(frags, embeddings):
            cur.execute(_UPSERT, _row(frag, emb))
            insertado = cur.fetchone()[0]
            if insertado:
                nuevos += 1
            else:
                actualizados += 1
    _log.info("Indexados: %d nuevos, %d actualizados", nuevos, actualizados)
    return (nuevos, actualizados)
