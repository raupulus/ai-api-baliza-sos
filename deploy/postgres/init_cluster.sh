#!/usr/bin/env bash
# Inicializa un clúster PostgreSQL LOCAL y autocontenido en DB_DATA_DIR.
# Pensado para Raspberry Pi OS / Debian. Idempotente: si el clúster ya existe,
# no lo recrea. Lee la configuración exportada desde env.py (ver scripts/env_export.py).
#
# Uso:
#   eval "$(python3 scripts/env_export.py)"   # exporta DB_* y demás
#   deploy/postgres/init_cluster.sh
set -euo pipefail

DB_DATA_DIR="${DB_DATA_DIR:-./data/postgres}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-bot_emergencias}"
DB_USER="${DB_USER:-bot}"
DB_PASSWORD="${DB_PASSWORD:-CAMBIA_ESTA_CLAVE}"

# Localiza binarios de PostgreSQL (Debian los pone en /usr/lib/postgresql/<ver>/bin).
PG_BIN="$(dirname "$(command -v pg_ctl || true)")"
if [[ -z "${PG_BIN}" || ! -x "${PG_BIN}/initdb" ]]; then
    PG_BIN="$(ls -d /usr/lib/postgresql/*/bin 2>/dev/null | sort -V | tail -1 || true)"
fi
if [[ -z "${PG_BIN}" || ! -x "${PG_BIN}/initdb" ]]; then
    echo "ERROR: no encuentro initdb. Instala PostgreSQL y pgvector:" >&2
    echo "  sudo apt-get install postgresql postgresql-<ver>-pgvector" >&2
    exit 1
fi

mkdir -p "${DB_DATA_DIR}"

if [[ ! -f "${DB_DATA_DIR}/PG_VERSION" ]]; then
    echo "==> initdb en ${DB_DATA_DIR}"
    "${PG_BIN}/initdb" -D "${DB_DATA_DIR}" -E UTF8 --locale=C.UTF-8 -U "${DB_USER}"

    # Ajustes de memoria para RPi4 4GB (ver docs/info/04-presupuesto-recursos.md).
    {
        echo ""
        echo "# --- Ajustes bot-ia-auxiliar (RPi4 4GB) ---"
        echo "listen_addresses = '127.0.0.1'"
        echo "port = ${DB_PORT}"
        echo "shared_buffers = 128MB"
        echo "work_mem = 16MB"
        echo "maintenance_work_mem = 64MB"
        echo "max_connections = 20"
        echo "effective_cache_size = 512MB"
    } >> "${DB_DATA_DIR}/postgresql.conf"
else
    echo "==> El clúster ya existe en ${DB_DATA_DIR}; no se reinicializa."
fi

echo "==> Arrancando clúster temporalmente para crear base y rol"
"${PG_BIN}/pg_ctl" -D "${DB_DATA_DIR}" -o "-p ${DB_PORT}" -w start

cleanup() { "${PG_BIN}/pg_ctl" -D "${DB_DATA_DIR}" -m fast stop || true; }
trap cleanup EXIT

# Crea la base si no existe.
if ! "${PG_BIN}/psql" -p "${DB_PORT}" -U "${DB_USER}" -d postgres -tAc \
        "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'" | grep -q 1; then
    echo "==> Creando base ${DB_NAME}"
    "${PG_BIN}/createdb" -p "${DB_PORT}" -U "${DB_USER}" "${DB_NAME}"
fi

# Fija la contraseña del rol.
"${PG_BIN}/psql" -p "${DB_PORT}" -U "${DB_USER}" -d postgres -c \
    "ALTER ROLE ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';"

echo "==> Clúster listo. Las migraciones se aplican con: python3 scripts/migrate.py"
