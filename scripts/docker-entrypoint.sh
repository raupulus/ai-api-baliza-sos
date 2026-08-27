#!/usr/bin/env bash
set -e

echo "==> Iniciando contenedor del Bot de Emergencias..."

# Esperar a que la base de datos PostgreSQL esté lista
if [ -n "$DB_HOST" ]; then
    echo "==> Esperando conexión a la base de datos en ${DB_HOST}:${DB_PORT:-5432}..."
    MAX_RETRIES=30
    COUNT=0
    until python3 -c "
import sys
from common.db import connection
try:
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT 1')
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; do
        COUNT=$((COUNT + 1))
        if [ "$COUNT" -ge "$MAX_RETRIES" ]; then
            echo "ERROR: Tiempo de espera agotado conectando a PostgreSQL."
            exit 1
        fi
        sleep 1
    done
    echo "==> Base de datos conectada correctamente."

    # Aplicar migraciones pendientes
    echo "==> Verificando y aplicando migraciones de base de datos..."
    python3 scripts/migrate.py || {
        echo "AVISO: No se pudieron aplicar las migraciones automáticamente (puede requerir verificación)."
    }
fi

echo "==> Ejecutando comando principal: $@"
exec "$@"
