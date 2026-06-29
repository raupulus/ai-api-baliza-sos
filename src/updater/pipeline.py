"""Orquestador del actualizador de contexto.

Por cada fuente: adquirir -> normalizar (política) -> separar -> indexar los
directos y dejar los sensibles en staging (checkpoint humano). Registra la
ejecución en la tabla `ingestas`.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from updater import normalize, staging
from updater.sources import get_source

_log = logging.getLogger(__name__)


@dataclass
class ResultadoIngesta:
    fuente: str
    adquiridos: int = 0
    nuevos: int = 0
    actualizados: int = 0
    en_staging: int = 0
    errores: int = 0
    detalle: str = ""


def _registrar(res: ResultadoIngesta) -> None:
    """Inserta el resultado en la tabla de auditoría (best-effort)."""
    try:
        from common.db import cursor

        with cursor() as cur:
            cur.execute(
                """
                INSERT INTO ingestas
                  (fuente, finalizado_en, fragmentos_nuevos, fragmentos_actualizados,
                   fragmentos_en_staging, errores, detalle)
                VALUES (%s, now(), %s, %s, %s, %s, %s)
                """,
                (res.fuente, res.nuevos, res.actualizados, res.en_staging,
                 res.errores, res.detalle),
            )
    except Exception as exc:  # no romper la ingesta por el log de auditoría
        _log.warning("No se pudo registrar la ingesta de %s: %s", res.fuente, exc)


def ingerir(nombre_fuente: str, *, dry_run: bool = False) -> ResultadoIngesta:
    """Ejecuta el pipeline para una fuente."""
    res = ResultadoIngesta(fuente=nombre_fuente)
    fuente = get_source(nombre_fuente)

    if not fuente.disponible():
        res.detalle = "Fuente no disponible (¿falta clave de API o QID de provincia?)."
        _log.warning("[%s] %s", nombre_fuente, res.detalle)
        return res

    try:
        fragmentos = fuente.fetch()
    except NotImplementedError:
        res.detalle = "Fuente aún no implementada (stub)."
        _log.info("[%s] %s", nombre_fuente, res.detalle)
        return res
    except Exception as exc:
        res.errores += 1
        res.detalle = f"Error al adquirir: {exc}"
        _log.error("[%s] %s", nombre_fuente, res.detalle)
        return res

    res.adquiridos = len(fragmentos)
    fragmentos = normalize.aplicar_politica(fragmentos)
    directos, checkpoint = normalize.separar(fragmentos)

    if dry_run:
        res.detalle = (
            f"DRY-RUN: {len(directos)} indexables, {len(checkpoint)} a checkpoint."
        )
        _log.info("[%s] %s", nombre_fuente, res.detalle)
        return res

    # Sensibles -> staging (no se indexan sin validación).
    res.en_staging = staging.stage(checkpoint)

    # Directos -> indexado.
    if directos:
        from api.rag.indexing import index_fragmentos

        res.nuevos, res.actualizados = index_fragmentos(directos)

    res.detalle = "OK"
    _registrar(res)
    _log.info(
        "[%s] adquiridos=%d nuevos=%d actualizados=%d staging=%d",
        nombre_fuente, res.adquiridos, res.nuevos, res.actualizados, res.en_staging,
    )
    return res


def ingerir_todas(nombres: list[str], *, dry_run: bool = False) -> list[ResultadoIngesta]:
    return [ingerir(n, dry_run=dry_run) for n in nombres]
