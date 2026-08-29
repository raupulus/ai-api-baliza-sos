#!/usr/bin/env python3
"""Normaliza los términos municipales de DERA (WFS) a CSV WGS84.

Entrada: snapshot XML de la capa `g13_01_TerminoMunicipal` filtrada por Cádiz.
Salida: `data/processed/csv/municipios_cadiz.csv` conforme a PLANTILLA.csv.

La geometría del WFS viene en EPSG:25830 (ETRS89/UTM 30N). Para el RAG se
calcula el centroide de cada municipio y se convierte a WGS84 (lat/lon) usando
la fórmula inversa de UTM (determinista, sin dependencias externas).
"""
from __future__ import annotations

import csv
import math
import re
import sys
from pathlib import Path
from typing import TypedDict


class MunicipioRaw(TypedDict):
    cod_mun: str
    nombre: str
    provincia: str
    verts: list[tuple[float, float]]


def _parse_municipios(xml: str) -> list[MunicipioRaw]:
    """Extrae (cod_mun, nombre, provincia, lista de vértices) de cada municipio."""
    out: list[MunicipioRaw] = []
    for m in re.finditer(
        r"<[^>]*g13_01_TerminoMunicipal[^>]*>(.*?)</[^>]*g13_01_TerminoMunicipal>",
        xml,
        re.S,
    ):
        body = m.group(1)
        cod = re.search(r"<[^>]*cod_mun>(\d+)</[^>]*cod_mun>", body)
        nombre = re.search(r"<[^>]*nombre>([^<]+)</[^>]*nombre>", body)
        prov = re.search(r"<[^>]*provincia>([^<]+)</[^>]*provincia>", body)
        pos = re.search(r"<gml:posList[^>]*>([^<]+)</gml:posList>", body)
        if not (cod and nombre and prov and pos):
            continue
        vals = [float(v) for v in pos.group(1).split()]
        # posList = secuencia x1 y1 x2 y2 ...
        verts = [(vals[i], vals[i + 1]) for i in range(0, len(vals), 2)]
        out.append({
            "cod_mun": cod.group(1),
            "nombre": nombre.group(1).strip(),
            "provincia": prov.group(1).strip(),
            "verts": verts,
        })
    return out


def _centroide(verts: list[tuple[float, float]]) -> tuple[float, float]:
    """Centroide de un polígono simple (fórmula del área). Aproximación válida."""
    n = len(verts)
    if n == 0:
        return 0.0, 0.0
    if verts[0] != verts[-1]:
        verts = verts + [verts[0]]
        n += 1
    area = 0.0
    cx = 0.0
    cy = 0.0
    for i in range(n - 1):
        x0, y0 = verts[i]
        x1, y1 = verts[i + 1]
        cross = x0 * y1 - x1 * y0
        area += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    area *= 0.5
    if abs(area) < 1e-9:
        # Polígono degenerado: usar media aritmética.
        xs = [p[0] for p in verts]
        ys = [p[1] for p in verts]
        return sum(xs) / n, sum(ys) / n
    return cx / (6.0 * area), cy / (6.0 * area)


def _utm_to_wgs84(easting: float, northing: float, zone: int = 30, northern: bool = True) -> tuple[float, float]:
    """Convierte UTM (ETRS89 ~ WGS84) a latitud/longitud (fórmula inversa UTM)."""
    # Constantes del elipsoide WGS84.
    a = 6378137.0
    f = 1 / 298.257223563
    k0 = 0.9996
    e2 = f * (2 - f)
    ep2 = e2 / (1 - e2)

    x = easting - 500000.0
    y = northing if northern else northing - 10000000.0

    m = y / k0
    mu = m / (a * (1 - e2 / 4 - 3 * e2 * e2 / 64 - 5 * e2**3 / 256))

    e1 = (1 - math.sqrt(1 - e2)) / (1 + math.sqrt(1 - e2))
    phi1 = (
        mu
        + (3 * e1 / 2 - 27 * e1**3 / 32) * math.sin(2 * mu)
        + (21 * e1**2 / 16 - 55 * e1**4 / 32) * math.sin(4 * mu)
        + (151 * e1**3 / 96) * math.sin(6 * mu)
        + (1097 * e1**4 / 512) * math.sin(8 * mu)
    )

    n1 = a / math.sqrt(1 - e2 * math.sin(phi1) ** 2)
    t1 = math.tan(phi1) ** 2
    c1 = ep2 * math.cos(phi1) ** 2
    r1 = a * (1 - e2) / (1 - e2 * math.sin(phi1) ** 2) ** 1.5
    d = x / (n1 * k0)

    lat = phi1 - (n1 * math.tan(phi1) / r1) * (
        d * d / 2
        - (5 + 3 * t1 + 10 * c1 - 4 * c1 * c1 - 9 * ep2) * d**4 / 24
        + (61 + 90 * t1 + 298 * c1 + 45 * t1 * t1 - 252 * ep2 - 3 * c1 * c1) * d**6 / 720
    )
    lon = (
        (d - (1 + 2 * t1 + c1) * d**3 / 6
         + (5 - 2 * c1 + 28 * t1 - 3 * c1 * c1 + 8 * ep2 + 24 * t1 * t1) * d**5 / 120)
        / math.cos(phi1)
    )
    lon0 = (zone * 6 - 183) * math.pi / 180
    lon_deg = math.degrees(lon0 + lon)
    lat_deg = math.degrees(lat)
    return round(lat_deg, 6), round(lon_deg, 6)


def main() -> int:
    src = Path("data/raw/downloads/municipios-geografia/2026-08-28/dera/dera_municipios_cadiz.xml")
    if not src.exists():
        print(f"ERROR: no existe {src}", file=sys.stderr)
        return 2

    xml = src.read_text(encoding="utf-8")
    munis = _parse_municipios(xml)
    print(f"Municipios parseados: {len(munis)}")

    filas = []
    for i, m in enumerate(sorted(munis, key=lambda m: m["nombre"]), 1):
        cx, cy = _centroide(m["verts"])
        lat, lon = _utm_to_wgs84(cx, cy)
        filas.append({
            "id": f"GEO-MUN-{i:03d}",
            "categoria": "geografia",
            "subcategoria": "municipio",
            "titulo": m["nombre"],
            "contenido": (
                f"Municipio de {m['nombre']} (Cádiz). "
                f"Código INE {m['cod_mun']}. "
                f"Coordenadas WGS84 (centroide): {lat}, {lon}."
            ),
            "fuente": "DERA / IECA (WFS g13_01_TerminoMunicipal)",
            "fuente_url": "https://www.ideandalucia.es/services/DERA_g13_limites_administrativos/wfs",
            "nivel_confianza": "alta",
            "provincia": "Cádiz",
            "municipio": m["nombre"],
            "lat": lat,
            "lon": lon,
            "fecha_verificacion": "2026-08-28",
        })

    dest = Path("data/processed/csv/municipios_cadiz.csv")
    cols = ["id", "categoria", "subcategoria", "titulo", "contenido", "fuente",
            "fuente_url", "nivel_confianza", "provincia", "municipio", "lat", "lon",
            "fecha_verificacion"]
    with open(dest, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(filas)

    print(f"Escritas {len(filas)} filas en {dest}")
    for r in filas[:5]:
        print(f"  {r['titulo']:30s} {r['lat']}, {r['lon']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
