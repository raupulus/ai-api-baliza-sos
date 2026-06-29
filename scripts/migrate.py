#!/usr/bin/env python3
"""Aplicador de migraciones SQL simple e idempotente.

Ejecuta en orden los ficheros `deploy/postgres/migrations/*.sql` que aún no se
hayan aplicado, registrándolos en una tabla `schema_migrations`. Suficiente para
un proyecto de un solo nodo; evita añadir Alembic y su peso en la Pi.

Uso:
    python3 scripts/migrate.py            # aplica las pendientes
    python3 scripts/migrate.py --status   # muestra el estado
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Permite importar `common` sin instalar el paquete.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from common.db import cursor  # noqa: E402

MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / "deploy" / "postgres" / "migrations"

_ENSURE_TABLE = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    nombre      TEXT PRIMARY KEY,
    aplicado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


def _aplicadas(cur) -> set[str]:
    cur.execute("SELECT nombre FROM schema_migrations")
    return {row[0] for row in cur.fetchall()}


def main() -> int:
    parser = argparse.ArgumentParser(description="Aplica migraciones SQL pendientes.")
    parser.add_argument("--status", action="store_true", help="Solo mostrar estado.")
    args = parser.parse_args()

    archivos = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not archivos:
        print("No hay migraciones en", MIGRATIONS_DIR)
        return 0

    with cursor() as cur:
        cur.execute(_ENSURE_TABLE)
        hechas = _aplicadas(cur)

        if args.status:
            for f in archivos:
                marca = "OK " if f.name in hechas else "PENDIENTE"
                print(f"[{marca}] {f.name}")
            return 0

        pendientes = [f for f in archivos if f.name not in hechas]
        if not pendientes:
            print("Base de datos al día. Nada que aplicar.")
            return 0

        for f in pendientes:
            print(f"==> Aplicando {f.name}")
            cur.execute(f.read_text(encoding="utf-8"))
            cur.execute("INSERT INTO schema_migrations (nombre) VALUES (%s)", (f.name,))
        print(f"Aplicadas {len(pendientes)} migración(es).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
