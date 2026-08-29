#!/usr/bin/env python3
"""Extrae del RAIF (olivar) solo los registros de la provincia de Cádiz.

El ZIP fuente usa compresión DEFLATE64 (compress_type 9), que el módulo
`zipfile` de Python no soporta. Se delega la descompresión en `7z` (presente en
el entorno) y se filtra el XML en streaming, sin materializar los ~2.2 GB.

Salida: `data/raw/downloads/agricultura-ganaderia/<fecha>/raif/cadiz/`
  - `2006_2016_Cadiz_RAIF_Olivar_Muestreos.xml`  (ya era Cádiz: copia directa)
  - `<periodo>_Cadiz_RAIF_Olivar_{Muestreos,Parcelas}.xml` (filtrados)

El registro se detecta por el elemento cuyo tag empieza por `AAA_` y se conserva
solo si su hijo `PROVINCIA` es exactamente `Cádiz`.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path("data/raw/downloads/agricultura-ganaderia/2026-08-28/raif")
ZIP = BASE / "raif_olivar_andalucia.zip"
OUT = BASE / "cadiz"

# (archivo dentro del ZIP, es_cadiz_directo)
FICHEROS = [
    ("2006_2016_Cadiz_RAIF_Olivar_Muestreos.xml", True),
    ("2017_2024_RAIF_Olivar_Muestreos.xml", False),
    ("2025_RAIF_Olivar_Muestreos.xml", False),
    ("2026_RAIF_Olivar_Muestreos.xml", False),
    ("2006_2016_RAIF_Olivar_Parcelas.xml", False),
    ("2017_2024_RAIF_Olivar_Parcelas.xml", False),
    ("2025_RAIF_Olivar_Parcelas.xml", False),
    ("2026_RAIF_Olivar_Parcelas.xml", False),
]


def _run_7z(nombre: str) -> subprocess.Popen:
    return subprocess.Popen(
        ["7z", "x", "-so", str(ZIP), nombre],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )


def _filtrar(nombre: str, destino: Path) -> int:
    """Extrae en streaming y escribe solo los registros con PROVINCIA=Cádiz."""
    proc = _run_7z(nombre)
    n = 0
    with destino.open("w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<dataroot>\n')
        for _event, elem in ET.iterparse(proc.stdout, events=("end",)):
            if not elem.tag.startswith("AAA_"):
                continue
            if elem.findtext("PROVINCIA") == "Cádiz":
                f.write(ET.tostring(elem, encoding="unicode"))
                f.write("\n")
                n += 1
            elem.clear()
        f.write("</dataroot>\n")
    proc.stdout.close()
    proc.wait()
    return n


def main() -> int:
    if not ZIP.exists():
        print(f"ERROR: no existe {ZIP}", file=sys.stderr)
        return 2
    if shutil.which("7z") is None:
        print("ERROR: se necesita `7z` para descomprimir DEFLATE64", file=sys.stderr)
        return 2

    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for nombre, es_cadiz_directo in FICHEROS:
        destino = OUT / nombre
        if es_cadiz_directo:
            # Copia directa (ya filtrado por provincia en origen).
            proc = _run_7z(nombre)
            datos = proc.stdout.read()
            proc.wait()
            destino.write_bytes(datos)
            # Contar registros para el resumen.
            import re
            n = len(re.findall(rb"<AAA_", datos))
            print(f"Copiado {nombre} ({len(datos)/1e6:.1f} MB, {n} registros)")
        else:
            n = _filtrar(nombre, destino)
            print(f"Filtrado {nombre} → {n} registros Cádiz ({destino.stat().st_size/1e6:.2f} MB)")
        total += n

    print(f"\nRegistros Cádiz totales: {total}")
    print(f"Salida en: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
