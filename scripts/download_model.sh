#!/usr/bin/env bash
# Descarga un modelo GGUF a models/. Por defecto, el modelo recomendado para
# RPi4 4GB (Qwen2.5-1.5B-Instruct Q4_K_M). Cambia las variables para otro modelo.
#
# Uso:
#   scripts/download_model.sh                 # modelo por defecto
#   MODEL_URL=... MODEL_FILE=... scripts/download_model.sh
set -euo pipefail

# Catálogo de modelos sugeridos (ver docs/info/03-decisiones-stack.md):
#   - RPi4 4GB (def.): Qwen2.5-1.5B-Instruct Q4_K_M  (~1.1 GB)
#   - RPi5 / 8GB:      Qwen2.5-3B-Instruct  Q4_K_M    (~2.0 GB)
MODEL_REPO="${MODEL_REPO:-Qwen/Qwen2.5-1.5B-Instruct-GGUF}"
MODEL_FILE="${MODEL_FILE:-qwen2.5-1.5b-instruct-q4_k_m.gguf}"
MODEL_URL="${MODEL_URL:-https://huggingface.co/${MODEL_REPO}/resolve/main/${MODEL_FILE}}"

DEST_DIR="${DEST_DIR:-models}"
mkdir -p "${DEST_DIR}"
DEST="${DEST_DIR}/${MODEL_FILE}"

if [[ -f "${DEST}" ]]; then
    echo "==> Ya existe ${DEST}; no se vuelve a descargar."
    exit 0
fi

echo "==> Descargando ${MODEL_FILE}"
echo "    desde ${MODEL_URL}"
if command -v curl >/dev/null; then
    curl -L --fail -o "${DEST}.part" "${MODEL_URL}"
elif command -v wget >/dev/null; then
    wget -O "${DEST}.part" "${MODEL_URL}"
else
    echo "ERROR: necesito curl o wget." >&2
    exit 1
fi
mv "${DEST}.part" "${DEST}"

echo "==> Descargado: ${DEST}"
echo "    Tamaño: $(du -h "${DEST}" | cut -f1)"
echo "    Ajusta LLM_MODEL_PATH en env.py a: ./${DEST}"
