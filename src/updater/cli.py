"""CLI del servicio actualizador de contexto.

Ejemplos:
    python -m updater.cli --list
    python -m updater.cli --source overpass-osm
    python -m updater.cli --all --dry-run
    python -m updater.cli --reindex-aprobados
"""

from __future__ import annotations

import argparse

from common.logging import setup_logging
from updater import pipeline, staging
from updater.sources import IMPLEMENTADAS, SOURCES

_log = setup_logging("context-updater")


def _list() -> int:
    print("Fuentes disponibles:")
    for nombre in SOURCES:
        estado = "implementada" if nombre in IMPLEMENTADAS else "stub"
        print(f"  - {nombre:18} [{estado}]")
    return 0


def _reindex_aprobados() -> int:
    """Indexa los fragmentos aprobados que esperan en staging."""
    from api.rag.indexing import index_fragmentos

    frags = staging.consumir_aprobados()
    if not frags:
        print("No hay fragmentos aprobados pendientes de indexar.")
        return 0
    nuevos, actualizados = index_fragmentos(frags)
    print(f"Indexados desde staging: {nuevos} nuevos, {actualizados} actualizados.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Actualizador de contexto del bot.")
    parser.add_argument("--list", action="store_true", help="Lista las fuentes.")
    parser.add_argument("--source", help="Ejecuta una fuente concreta.")
    parser.add_argument("--all", action="store_true", help="Ejecuta todas las fuentes.")
    parser.add_argument("--dry-run", action="store_true", help="No indexa ni hace staging.")
    parser.add_argument(
        "--reindex-aprobados",
        action="store_true",
        help="Indexa los fragmentos aprobados en staging.",
    )
    args = parser.parse_args(argv)

    if args.list:
        return _list()
    if args.reindex_aprobados:
        return _reindex_aprobados()

    if args.all:
        nombres = list(SOURCES)
    elif args.source:
        nombres = [args.source]
    else:
        parser.print_help()
        return 1

    resultados = pipeline.ingerir_todas(nombres, dry_run=args.dry_run)
    print("\nResumen:")
    for r in resultados:
        print(
            f"  {r.fuente:18} adq={r.adquiridos} nuevos={r.nuevos} "
            f"act={r.actualizados} staging={r.en_staging} err={r.errores}  {r.detalle}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
