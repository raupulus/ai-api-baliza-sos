#!/usr/bin/env bash
# Compila llama.cpp nativo para Raspberry Pi (ARM/NEON) y deja los binarios en
# vendor/llama.cpp/build/bin. Fija un commit conocido para reproducibilidad.
#
# Requisitos: build-essential, cmake, git, libcurl4-openssl-dev.
#   sudo apt-get install -y build-essential cmake git libcurl4-openssl-dev
set -euo pipefail

LLAMA_REF="${LLAMA_REF:-master}"   # fija aquí un tag/commit concreto en producción
VENDOR_DIR="vendor/llama.cpp"

mkdir -p vendor
if [[ ! -d "${VENDOR_DIR}/.git" ]]; then
    echo "==> Clonando llama.cpp"
    git clone https://github.com/ggml-org/llama.cpp.git "${VENDOR_DIR}"
fi

cd "${VENDOR_DIR}"
git fetch --all --tags
git checkout "${LLAMA_REF}"

echo "==> Compilando (Release, optimizado para CPU ARM)"
cmake -B build -DCMAKE_BUILD_TYPE=Release -DGGML_NATIVE=ON
cmake --build build --config Release -j "$(nproc)"

echo "==> Binarios disponibles en ${VENDOR_DIR}/build/bin:"
ls -1 build/bin | grep -E 'llama-(server|cli)' || true
echo "Listo. Configura llama-server.service con la ruta a build/bin/llama-server."
