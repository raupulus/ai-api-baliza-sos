#!/usr/bin/env bash
# ==============================================================================
# scripts/check.sh — Verificación de sintaxis, linters y tipos
# ==============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "🔍 1. Comprobando compilación de sintaxis Python (py_compile)..."
python3 -m compileall -q src scripts tests
echo "   ✅ Sintaxis correcta en src/, scripts/ y tests/."

if command -v ruff >/dev/null 2>&1; then
    echo "🔍 2. Ejecutando linter ruff..."
    ruff check src tests scripts
    echo "   ✅ Linter ruff sin incidencias."
else
    echo "ℹ️  2. ruff no instalado en el host local (omitido)."
fi

if command -v mypy >/dev/null 2>&1; then
    echo "🔍 3. Comprobando tipos con mypy..."
    mypy src
    echo "   ✅ mypy sin incidencias."
else
    echo "ℹ️  3. mypy no instalado en el host local (omitido)."
fi

echo "✨ Todas las validaciones de código completadas con éxito."
