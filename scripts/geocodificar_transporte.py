#!/usr/bin/env python3
"""Asigna el municipio a cada parada de transporte usando point-in-polygon.

Usa los polígonos de los términos municipales de DERA (EPSG:25830, UTM 30N).
Convierte las coordenadas WGS84 de las paradas a UTM y las asigna al municipio
cuyo polígono las contiene (ray-casting). Sin dependencias externas.

Actualiza in-place los CSVs:
  - data/processed/csv/transporte_publico_cadiz.csv
  - data/processed/csv/transporte_publico_renfe_cadiz.csv
"""
from __future__ import annotations

import csv
import math
import re
import sys
from pathlib import Path

DERA_XML = Path("data/raw/downloads/municipios-geografia/2026-08-28/dera/dera_municipios_cadiz.xml")
CSVS = [
    Path("data/processed/csv/transporte_publico_cadiz.csv"),
    Path("data/processed/csv/transporte_publico_renfe_cadiz.csv"),
]


def _wgs84_a_utm(lat_deg: float, lon_deg: float, zone: int = 30) -> tuple[float, float]:
    """Convierte WGS84 → UTM (fórmula directa, elipsoide WGS84)."""
    a = 6378137.0
    f = 1 / 298.257223563
    k0 = 0.9996
    e2 = f * (2 - f)
    ep2 = e2 / (1 - e2)

    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    lon0 = math.radians(zone * 6 - 183)

    n = a / math.sqrt(1 - e2 * math.sin(lat) ** 2)
    t = math.tan(lat) ** 2
    c = ep2 * math.cos(lat) ** 2
    aa = math.cos(lat) * (lon - lon0)

    m = a * (
        (1 - e2 / 4 - 3 * e2 ** 2 / 64 - 5 * e2 ** 3 / 256) * lat
        - (3 * e2 / 8 + 3 * e2 ** 2 / 32 + 45 * e2 ** 3 / 1024) * math.sin(2 * lat)
        + (15 * e2 ** 2 / 256 + 45 * e2 ** 3 / 1024) * math.sin(4 * lat)
        - (35 * e2 ** 3 / 3072) * math.sin(6 * lat)
    )

    easting = k0 * n * (
        aa
        + (1 - t + c) * aa ** 3 / 6
        + (5 - 18 * t + t ** 2 + 72 * c - 58 * ep2) * aa ** 5 / 120
    ) + 500000.0

    northing = k0 * (
        m
        + n * math.tan(lat) * (
            aa ** 2 / 2
            + (5 - t + 9 * c + 4 * c ** 2) * aa ** 4 / 24
            + (61 - 58 * t + t ** 2 + 600 * c - 330 * ep2) * aa ** 6 / 720
        )
    )

    return easting, northing


def _parse_municipios(xml: str) -> dict[str, list[list[tuple[float, float]]]]:
    """Devuelve {nombre: [polígono1, polígono2, ...]} en coordenadas UTM."""
    out: dict[str, list[list[tuple[float, float]]]] = {}
    for m in re.finditer(
        r"<[^>]*g13_01_TerminoMunicipal[^>]*>(.*?)</[^>]*g13_01_TerminoMunicipal>",
        xml,
        re.S,
    ):
        body = m.group(1)
        nombre = re.search(r"<[^>]*nombre>([^<]+)</[^>]*nombre>", body)
        if not nombre:
            continue
        nombre = nombre.group(1).strip()
        poligonos = []
        for pos in re.finditer(r"<gml:posList[^>]*>([^<]+)</gml:posList>", body):
            vals = [float(v) for v in pos.group(1).split()]
            verts = [(vals[i], vals[i + 1]) for i in range(0, len(vals), 2)]
            poligonos.append(verts)
        if poligonos:
            out[nombre] = poligonos
    return out


def _punto_en_poligono(x: float, y: float, verts: list[tuple[float, float]]) -> bool:
    """Ray-casting: True si (x, y) está dentro del polígono."""
    dentro = False
    n = len(verts)
    j = n - 1
    for i in range(n):
        xi, yi = verts[i]
        xj, yj = verts[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            dentro = not dentro
        j = i
    return dentro


def _asignar(x: float, y: float, municipios: dict[str, list[list[tuple[float, float]]]]) -> str:
    for nombre, poligonos in municipios.items():
        for verts in poligonos:
            if _punto_en_poligono(x, y, verts):
                return nombre
    return ""


def main() -> int:
    xml = DERA_XML.read_text(encoding="utf-8")
    municipios = _parse_municipios(xml)
    print(f"Municipios con polígonos: {len(municipios)}")

    for csv_path in CSVS:
        if not csv_path.exists():
            continue
        filas = list(csv.DictReader(open(csv_path, encoding="utf-8", newline="")))
        asignados = 0
        for fila in filas:
            try:
                lat = float(fila["lat"])
                lon = float(fila["lon"])
            except (ValueError, KeyError):
                continue
            if lat == 0 and lon == 0:
                continue
            x, y = _wgs84_a_utm(lat, lon)
            mun = _asignar(x, y, municipios)
            fila["municipio"] = mun
            if mun:
                asignados += 1
                # Inyectar el municipio en el texto para que el RAG lo recupere.
                contenido = fila.get("contenido", "")
                if mun not in contenido:
                    contenido = contenido.replace(
                        ". WGS84:", f" ({mun}). WGS84:", 1
                    )
                    fila["contenido"] = contenido

        cols = list(filas[0].keys())
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(filas)
        print(f"{csv_path.name}: {asignados}/{len(filas)} con municipio asignado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
