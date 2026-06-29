#!/usr/bin/env bash
# Healthcheck de los tres componentes: BD, llama-server y API.
set -uo pipefail
eval "$(python3 scripts/env_export.py)"
ok=0
echo -n "PostgreSQL: "
if pg_isready -h "${DB_HOST}" -p "${DB_PORT}" >/dev/null 2>&1; then echo "OK"; else echo "FALLO"; ok=1; fi
echo -n "llama-server: "
if curl -sf "http://${LLM_SERVER_HOST}:${LLM_SERVER_PORT}/health" >/dev/null 2>&1; then echo "OK"; else echo "FALLO"; ok=1; fi
echo -n "API: "
if curl -sf "http://127.0.0.1:${API_PORT}/health" >/dev/null 2>&1; then echo "OK"; else echo "FALLO (¿arrancada?)"; ok=1; fi
exit $ok
