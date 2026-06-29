#!/usr/bin/env bash
# Instalación reproducible en Raspberry Pi OS. Ejecutar desde la raíz del repo.
# Idempotente en lo posible. Requiere sudo para systemd y paquetes.
set -euo pipefail

echo "==> 1/7 Paquetes del sistema"
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip postgresql cmake build-essential \
    git libcurl4-openssl-dev pkg-config
# pgvector: paquete del sistema si está disponible (ajusta la versión de PG).
sudo apt-get install -y "postgresql-$(pg_config --version | grep -oE '[0-9]+' | head -1)-pgvector" || \
    echo "AVISO: instala pgvector manualmente si el paquete no existe."

echo "==> 2/7 Entorno Python"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements/api.txt -r requirements/updater.txt

echo "==> 3/7 Configuración"
[[ -f env.py ]] || cp env.example.py env.py
echo "   Revisa env.py (DB_PASSWORD, API_AUTH_TOKEN, LLM_MODEL_PATH...) antes de seguir."

echo "==> 4/7 Compilar llama.cpp y descargar modelo"
scripts/build_llama.sh
scripts/download_model.sh

echo "==> 5/7 PostgreSQL local + migraciones"
eval "$(python3 scripts/env_export.py)"
deploy/postgres/init_cluster.sh
python3 scripts/migrate.py

echo "==> 6/7 Unidades systemd"
python3 scripts/env_export.py --no-export | sudo tee /etc/default/bot-ia-auxiliar >/dev/null
sudo cp deploy/systemd/*.service deploy/systemd/*.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now postgresql-local.service llama-server.service bot-api.service
sudo systemctl enable --now context-updater.timer

echo "==> 7/7 Healthcheck"
scripts/healthcheck.sh || true
echo "Instalación terminada."
