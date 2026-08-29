#!/usr/bin/env python3
"""Normaliza las estaciones ferroviarias de Cádiz desde el WFS INSPIRE de ADIF.

La capa `tn-ra:RailwayStationNode` (INSPIRE RailwayTransportNetwork 3.0) expone
todos los nodos ferroviarios (estaciones, apartaderos, terminales). Se filtra por
el BBOX de Cádiz y se vuelca a CSV.

Nota: el WFS requiere cabecera de navegador (Safari macOS) + cortesía; antes
devolvía anti-bot. Coordenadas en EPSG:4258 (≈ WGS84, lat/lon).

Salida: `data/processed/csv/estaciones_ferrocarril_cadiz.csv`.
"""
from __future__ import annotations

import csv
import re
import sys
import urllib.request
from pathlib import Path

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15")

ENDPOINT = "https://ideadif.adif.es/services/wfs"
MIN_LON, MIN_LAT, MAX_LON, MAX_LAT = -6.5, 35.95, -5.1, 37.05


def _getfeature() -> str:
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<wfs:GetFeature service="WFS" version="2.0.0" xmlns:wfs="http://www.opengis.net/wfs/2.0" xmlns:tn-ra="urn:x-inspire:specification:gmlas:RailwayTransportNetwork:3.0" count="10000">
  <wfs:Query typeNames="tn-ra:RailwayStationNode"/>
</wfs:GetFeature>"""
    req = urllib.request.Request(
        ENDPOINT, data=xml.encode("utf-8"),
        headers={"Content-Type": "application/xml", "User-Agent": UA},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode("utf-8", "replace")


def _extraer(body: str) -> list[dict]:
    out = []
    for m in re.finditer(
        r"<gml:name>([^<]+)</gml:name>.*?<gml:pos>([\d.]+)\s+([\d.\-]+)</gml:pos>",
        body, re.S,
    ):
        nombre = m.group(1).strip()
        lat = float(m.group(2))
        lon = float(m.group(3))
        if MIN_LON <= lon <= MAX_LON and MIN_LAT <= lat <= MAX_LAT:
            out.append({"nombre": nombre, "lat": lat, "lon": lon})
    return out


def main() -> int:
    body = _getfeature()
    estaciones = _extraer(body)
    # Deduplicar por nombre (conservar la primera aparición).
    unicas = {s["nombre"]: s for s in estaciones}
    filas = list(unicas.values())
    print(f"Estaciones/instalaciones ferroviarias en Cádiz: {len(filas)}")

    dest = Path("data/processed/csv/estaciones_ferrocarril_cadiz.csv")
    cols = ["id", "categoria", "subcategoria", "titulo", "contenido", "fuente",
            "fuente_url", "nivel_confianza", "provincia", "municipio", "lat", "lon",
            "fecha_verificacion"]
    with open(dest, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for i, s in enumerate(sorted(filas, key=lambda x: x["nombre"]), 1):
            w.writerow({
                "id": f"ADIF-{i:03d}",
                "categoria": "transporte",
                "subcategoria": "estacion_ferrocarril",
                "titulo": s["nombre"],
                "contenido": f"Estación/instalación ferroviaria: {s['nombre']}. WGS84: {s['lat']:.6f}, {s['lon']:.6f}.",
                "fuente": "ADIF — IDEADIF (WFS INSPIRE RailwayStationNode)",
                "fuente_url": "https://ideadif.adif.es/services/wfs",
                "nivel_confianza": "alta",
                "provincia": "Cádiz",
                "municipio": "",
                "lat": round(s["lat"], 6),
                "lon": round(s["lon"], 6),
                "fecha_verificacion": "2026-08-28",
            })
    print(f"Escritas {len(filas)} en {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
