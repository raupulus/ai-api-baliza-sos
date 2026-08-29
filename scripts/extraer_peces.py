#!/usr/bin/env python3
"""Extrae un inventario de especies del OCR de los manuales de peces de la Junta.

Lee los `.ocr.txt` de tomo I y II, localiza los marcadores `Código FAO: XXX` y el
nombre científico (`Género especie`) más próximo, y genera un CSV de referencia.

Salida: `data/processed/csv/peces_especies_cadiz.csv` (referencia, no se migra a RAG).
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

FICHEROS = [
    Path("data/raw/downloads/flora-fauna/2026-08-28/junta/junta_manual_peces_tomo_i.ocr.txt"),
    Path("data/raw/downloads/flora-fauna/2026-08-28/junta/junta_manual_peces_tomo_ii_baja.ocr.txt"),
]

# Género especie (dos palabras capitalizadas; la 2ª puede estar capitalizada en OCR).
CIENTIFICO = re.compile(r"\b([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)\s+([a-záéíóúñ]{2,})\b")
FAO = re.compile(r"Código FAO:\s*([A-Z]{3})")


def _extraer(texto: str) -> list[tuple[str, str]]:
    """Devuelve [(codigo_fao, nombre_cientifico)] por cada marcador FAO."""
    pares = []
    lineas = texto.splitlines()
    for i, linea in enumerate(lineas):
        m = FAO.search(linea)
        if not m:
            continue
        codigo = m.group(1)
        # Buscar el nombre científico más próximo hacia atrás (hasta 8 líneas).
        cientifico = ""
        for j in range(i - 1, max(0, i - 9), -1):
            mm = CIENTIFICO.search(lineas[j])
            if mm:
                cientifico = f"{mm.group(1)} {mm.group(2)}"
                break
        if not cientifico:
            # Hacia delante (hasta 6 líneas).
            for j in range(i + 1, min(len(lineas), i + 7)):
                mm = CIENTIFICO.search(lineas[j])
                if mm:
                    cientifico = f"{mm.group(1)} {mm.group(2)}"
                    break
        pares.append((codigo, cientifico))
    return pares


def main() -> int:
    pares: list[tuple[str, str]] = []
    for f in FICHEROS:
        if not f.exists():
            continue
        pares.extend(_extraer(f.read_text(encoding="utf-8")))

    # Deduplicar por código FAO conservando el nombre científico más frecuente.
    por_codigo: dict[str, dict[str, int]] = {}
    for codigo, cientifico in pares:
        por_codigo.setdefault(codigo, {})
        if cientifico:
            por_codigo[codigo][cientifico] = por_codigo[codigo].get(cientifico, 0) + 1

    dest = Path("data/processed/csv/peces_especies_cadiz.csv")
    with open(dest, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["codigo_fao", "nombre_cientifico", "frecuencia"])
        for codigo in sorted(por_codigo):
            nombres = por_codigo[codigo]
            mejor = max(nombres, key=nombres.get) if nombres else ""
            w.writerow([codigo, mejor, nombres.get(mejor, 0)])
    print(f"Especies: {len(por_codigo)} códigos FAO únicos → {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
