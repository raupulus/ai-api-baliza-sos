"""Configuración de pytest. `pythonpath=src` está en pyproject.toml."""

from __future__ import annotations

import sys
from pathlib import Path

# Refuerzo por si se ejecuta pytest sin leer pyproject (p. ej. IDE).
SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
