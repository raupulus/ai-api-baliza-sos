"""Acceso a PostgreSQL (psycopg 3) con pool de conexiones y pgvector.

Las dependencias (`psycopg`, `pgvector`) se importan de forma perezosa para que
importar este módulo no falle en entornos donde aún no están instaladas (p. ej.
al ejecutar pruebas unitarias puras).
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Any, Iterator

from common.config import settings
from common.errors import DatabaseError

_log = logging.getLogger(__name__)
_pool: Any = None


def _build_pool() -> Any:
    try:
        from psycopg_pool import ConnectionPool
    except ImportError as exc:  # pragma: no cover
        raise DatabaseError(
            "psycopg[pool] no está instalado. Instala requirements/base.txt."
        ) from exc

    pool = ConnectionPool(
        conninfo=settings.db_dsn,
        min_size=1,
        max_size=4,  # pocas conexiones: hardware limitado
        open=True,
        kwargs={"autocommit": False},
    )
    return pool


def get_pool() -> Any:
    """Devuelve el pool de conexiones (lo crea la primera vez)."""
    global _pool
    if _pool is None:
        _pool = _build_pool()
    return _pool


def _register_vector(conn: Any) -> None:
    """Registra el adaptador de tipos vector de pgvector en la conexión."""
    try:
        from pgvector.psycopg import register_vector

        register_vector(conn)
    except ImportError as exc:  # pragma: no cover
        raise DatabaseError("pgvector no está instalado.") from exc


@contextmanager
def connection() -> Iterator[Any]:
    """Context manager que entrega una conexión del pool con pgvector listo."""
    pool = get_pool()
    with pool.connection() as conn:
        _register_vector(conn)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise


@contextmanager
def cursor() -> Iterator[Any]:
    """Context manager que entrega un cursor (commit/rollback automático)."""
    with connection() as conn:
        with conn.cursor() as cur:
            yield cur


def ping() -> bool:
    """Healthcheck: comprueba conectividad con la BD."""
    try:
        with cursor() as cur:
            cur.execute("SELECT 1")
            return cur.fetchone()[0] == 1
    except Exception as exc:  # pragma: no cover
        _log.error("Healthcheck de BD falló: %s", exc)
        return False


def close_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None
