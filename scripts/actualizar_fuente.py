#!/usr/bin/env python3
"""Script de actualización manual de fuentes de conocimiento para el RAG.

Permite actualizar bajo demanda (sin automatizaciones) las fuentes de datos
médicos, flora, fauna, municipios, fiestas e historia en la base de datos vectorial.

Uso:
    python3 scripts/actualizar_fuente.py --list
    python3 scripts/actualizar_fuente.py --fuente primeros-auxilios-avanzado
    python3 scripts/actualizar_fuente.py --fuente flora-fauna-cadiz
    python3 scripts/actualizar_fuente.py --fuente municipios-cadiz
    python3 scripts/actualizar_fuente.py --fuente fiestas-cadiz
    python3 scripts/actualizar_fuente.py --fuente historia-cadiz
    python3 scripts/actualizar_fuente.py --todas
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Añadir src al PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from api.rag.indexing import index_fragmentos  # noqa: E402
from common.logging import setup_logging  # noqa: E402
from updater.sources import IMPLEMENTADAS, SOURCES, get_source  # noqa: E402

_log = setup_logging("actualizar-fuente")

# Fuentes ampliadas prioritarias para Cádiz
FUENTES_AMPLIADAS = [
    "primeros-auxilios-avanzado",
    "flora-fauna-cadiz",
    "municipios-cadiz",
    "fiestas-cadiz",
    "historia-cadiz",
]


def _listar_fuentes() -> int:
    print("\n📦 Fuentes de conocimiento disponibles para actualización manual:")
    print("=" * 70)
    for nombre in SOURCES:
        es_ampliada = "⭐ Ampliada" if nombre in FUENTES_AMPLIADAS else "Estándar"
        es_impl = "Implementada" if nombre in IMPLEMENTADAS else "Stub"
        print(f"  • {nombre:28} [{es_ampliada:10}] [{es_impl}]")
    print("=" * 70)
    print("Ejecuta: python3 scripts/actualizar_fuente.py --fuente <nombre>")
    print("O bien:  python3 scripts/actualizar_fuente.py --todas\n")
    return 0


def _procesar_fuente(nombre: str) -> tuple[int, int, int]:
    """Descarga, procesa y vectoriza los fragmentos de una fuente concreta."""
    t0 = time.monotonic()
    print(f"\n🚀 Iniciando actualización de: {nombre}...")

    try:
        source_inst = get_source(nombre)
        fragmentos = source_inst.fetch()
    except Exception as exc:
        print(f"❌ Error al adquirir datos de {nombre}: {exc}")
        return 0, 0, 0

    if not fragmentos:
        print(f"⚠️ La fuente {nombre} no devolvió fragmentos.")
        return 0, 0, 0

    print(f"  📥 Adquiridos {len(fragmentos)} fragmentos. Generando embeddings y guardando en PostgreSQL...")

    try:
        nuevos, actualizados = index_fragmentos(fragmentos)
        ms = int((time.monotonic() - t0) * 1000)
        print(
            f"  ✅ Completado en {ms} ms: {nuevos} nuevos, {actualizados} actualizados "
            f"(Total procesados: {len(fragmentos)})."
        )
        return len(fragmentos), nuevos, actualizados
    except Exception as exc:
        print(f"❌ Error durante la indexación/vectorización de {nombre}: {exc}")
        return len(fragmentos), 0, 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Actualizador manual de fuentes de conocimiento en el RAG."
    )
    parser.add_argument("--list", action="store_true", help="Listar fuentes disponibles.")
    parser.add_argument("--fuente", help="Nombre de la fuente a actualizar.")
    parser.add_argument(
        "--todas",
        action="store_true",
        help="Actualiza todas las fuentes enriquecidas de Cádiz.",
    )
    args = parser.parse_args(argv)

    if args.list or (not args.fuente and not args.todas):
        return _listar_fuentes()

    if args.todas:
        fuentes_a_ejecutar = FUENTES_AMPLIADAS
    else:
        # Permitir nombres con guiones o guiones bajos
        nombre = args.fuente.replace("_", "-")
        if nombre not in SOURCES:
            print(f"❌ Fuente desconocida: '{args.fuente}'. Usa --list para ver las disponibles.")
            return 1
        fuentes_a_ejecutar = [nombre]

    total_adq = total_nuevos = total_act = 0
    for f in fuentes_a_ejecutar:
        adq, nuevos, act = _procesar_fuente(f)
        total_adq += adq
        total_nuevos += nuevos
        total_act += act

    print("\n" + "=" * 70)
    print(f"📊 RESUMEN FINAL: {total_adq} adquiridos | {total_nuevos} nuevos | {total_act} actualizados")
    print("=" * 70 + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
