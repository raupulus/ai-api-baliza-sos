#!/usr/bin/env bash
# Backup de la base de conocimiento (pg_dump) y del staging aprobado.
set -euo pipefail
eval "$(python3 scripts/env_export.py)"
OUT_DIR="${1:-backups}"
mkdir -p "${OUT_DIR}"
STAMP="$(date +%Y%m%d-%H%M%S)"
PG_BIN="$(ls -d /usr/lib/postgresql/*/bin 2>/dev/null | sort -V | tail -1 || echo)"
DUMP="${OUT_DIR}/${DB_NAME}-${STAMP}.sql.gz"
echo "==> pg_dump -> ${DUMP}"
"${PG_BIN:+${PG_BIN}/}pg_dump" -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" "${DB_NAME}" \
    | gzip > "${DUMP}"
# Staging aprobado (no se pierde el trabajo de validación).
if [[ -d "${UPDATER_STAGING_DIR:-data/staging}/aprobados" ]]; then
    tar czf "${OUT_DIR}/staging-aprobados-${STAMP}.tar.gz" \
        -C "${UPDATER_STAGING_DIR:-data/staging}" aprobados
fi
echo "==> Backup completado en ${OUT_DIR}"
