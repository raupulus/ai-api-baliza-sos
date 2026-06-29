#!/usr/bin/env python3
"""Herramienta de revisión humana (checkpoint) de fragmentos sensibles.

Recorre los fragmentos pendientes en staging y permite aprobar / editar /
rechazar cada uno. Sin aprobación NO se indexan. Tras aprobar, indexa con:
    python -m updater.cli --reindex-aprobados

Uso:
    python3 scripts/review.py            # modo interactivo
    python3 scripts/review.py --status   # solo recuento
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from updater import staging  # noqa: E402


def _mostrar(frag, ruta: Path) -> None:
    print("\n" + "=" * 70)
    print(f"Fuente:     {frag.fuente}")
    print(f"Categoría:  {frag.categoria.value}  (peligrosa={frag.peligrosa})")
    print(f"Confianza:  {frag.nivel_confianza.value}")
    print(f"URL:        {frag.fuente_url}")
    print(f"Fichero:    {ruta.name}")
    print("-" * 70)
    print(frag.texto)
    print("=" * 70)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", action="store_true", help="Solo mostrar recuentos.")
    parser.add_argument("--operador", default="operador", help="Nombre del revisor.")
    args = parser.parse_args()

    pendientes = staging.listar_pendientes()
    aprobados = staging.listar_aprobados()
    print(f"Pendientes: {len(pendientes)} · Aprobados sin indexar: {len(aprobados)}")
    if args.status:
        return 0
    if not pendientes:
        print("Nada que revisar.")
        return 0

    for ruta in pendientes:
        frag = staging.cargar(ruta)
        _mostrar(frag, ruta)
        while True:
            accion = input("[a]probar / [r]echazar / [s]altar / [q]salir: ").strip().lower()
            if accion in ("a", "r", "s", "q"):
                break
        if accion == "q":
            break
        if accion == "a":
            staging.aprobar(ruta, args.operador)
            print("  -> aprobado.")
        elif accion == "r":
            staging.rechazar(ruta)
            print("  -> rechazado.")
        else:
            print("  -> saltado.")

    print("\nRevisión terminada. Para indexar lo aprobado:")
    print("  python -m updater.cli --reindex-aprobados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
