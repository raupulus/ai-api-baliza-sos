#!/usr/bin/env python3
"""OCR de PDFs escaneados en español (tesseract `spa`).

Convierte cada página a imagen con `pdftoppm` y la procesa con `tesseract -l spa`.
El resultado se escribe a un único fichero de texto con marcadores de página.

Uso:
    python3 scripts/ocr_pdf_es.py <entrada.pdf> <salida.txt> [--dpi 300]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada", type=Path)
    ap.add_argument("salida", type=Path)
    ap.add_argument("--dpi", type=int, default=300)
    args = ap.parse_args()

    if not args.entrada.exists():
        print(f"ERROR: no existe {args.entrada}", file=sys.stderr)
        return 2
    for tool in ("pdftoppm", "tesseract"):
        if subprocess.run(["which", tool], capture_output=True).returncode != 0:
            print(f"ERROR: falta {tool}", file=sys.stderr)
            return 2

    args.salida.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ocr_") as tmp:
        base = str(Path(tmp) / "pag")
        subprocess.run(
            ["pdftoppm", "-png", "-r", str(args.dpi), str(args.entrada), base],
            check=True,
        )
        paginas = sorted(Path(tmp).glob("pag-*.png"))
        with args.salida.open("w", encoding="utf-8") as out:
            for i, png in enumerate(paginas, 1):
                res = subprocess.run(
                    ["tesseract", str(png), "stdout", "-l", "spa"],
                    capture_output=True,
                    text=True,
                )
                texto = res.stdout.strip()
                out.write(f"\n\n===== PÁGINA {i} =====\n")
                out.write(texto)
                if i % 20 == 0:
                    print(f"  OCR página {i}/{len(paginas)}", file=sys.stderr)
        n_paginas = len(paginas)
    print(f"OCR completado: {n_paginas} páginas → {args.salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
