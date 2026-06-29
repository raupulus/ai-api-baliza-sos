#!/usr/bin/env bash
# Prepara el entorno de desarrollo: venv + dependencias + env.py.
set -euo pipefail
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements/dev.txt
[[ -f env.py ]] || cp env.example.py env.py
echo "Entorno listo. Activa con: source .venv/bin/activate"
echo "Edita env.py con tu configuración real (DB_PASSWORD, API_AUTH_TOKEN, ...)."
