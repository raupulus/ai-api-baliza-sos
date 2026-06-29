"""Recuperación de fragmentos por similitud vectorial (pgvector, coseno)."""

from __future__ import annotations

import logging
from typing import Optional

from api.rag.embeddings import get_embedder
from common.config import settings
from common.db import cursor
from common.models import (
    Categoria,
    Fragmento,
    FragmentoRecuperado,
    NivelConfianza,
)

_log = logging.getLogger(__name__)

# pgvector: el operador `<=>` es distancia coseno (0 = idéntico). La similitud
# es 1 - distancia. Filtramos por similitud mínima (settings.rag_min_score).
_SELECT = """
SELECT
    id, texto, fuente, fuente_url, fecha, categoria, subcategoria, provincia,
    nivel_confianza, licencia, peligrosa, validado_por, validado_fecha,
    hash_contenido,
    1 - (embedding <=> %(qvec)s) AS score
FROM fragmentos
{where}
ORDER BY embedding <=> %(qvec)s
LIMIT %(limit)s;
"""


def _build_where(categoria: Optional[str], provincia: Optional[str]) -> tuple[str, dict]:
    clausulas = []
    params: dict = {}
    if categoria:
        clausulas.append("categoria = %(categoria)s")
        params["categoria"] = categoria
    if provincia:
        clausulas.append("provincia = %(provincia)s")
        params["provincia"] = provincia
    where = ("WHERE " + " AND ".join(clausulas)) if clausulas else ""
    return where, params


def _to_fragmento(row: dict) -> Fragmento:
    return Fragmento(
        id=str(row["id"]),
        texto=row["texto"],
        fuente=row["fuente"],
        fuente_url=row["fuente_url"],
        fecha=row["fecha"],
        categoria=Categoria(row["categoria"]),
        subcategoria=row["subcategoria"],
        provincia=row["provincia"],
        nivel_confianza=NivelConfianza(row["nivel_confianza"]),
        licencia=row["licencia"],
        peligrosa=row["peligrosa"],
        validado_por=row["validado_por"],
        validado_fecha=row["validado_fecha"],
        hash_contenido=row["hash_contenido"],
    )


def buscar(
    consulta: str,
    *,
    top_k: Optional[int] = None,
    min_score: Optional[float] = None,
    categoria: Optional[str] = None,
    provincia: Optional[str] = None,
) -> list[FragmentoRecuperado]:
    """Recupera los fragmentos más similares a la consulta.

    Filtra por umbral de similitud y, opcionalmente, por categoría/provincia.
    """
    top_k = top_k or settings.rag_top_k
    min_score = settings.rag_min_score if min_score is None else min_score

    qvec = get_embedder().embed_query(consulta)
    where, params = _build_where(categoria, provincia)
    params.update({"qvec": qvec, "limit": top_k})

    sql = _SELECT.format(where=where)
    resultados: list[FragmentoRecuperado] = []
    with cursor() as cur:
        # psycopg con row_factory dict para acceso por nombre.
        from psycopg.rows import dict_row

        cur.row_factory = dict_row
        cur.execute(sql, params)
        for row in cur.fetchall():
            score = float(row["score"])
            if score >= min_score:
                resultados.append(FragmentoRecuperado(_to_fragmento(row), score))

    _log.debug("Recuperados %d fragmentos (>= %.2f) para: %s",
               len(resultados), min_score, consulta[:60])
    return resultados
