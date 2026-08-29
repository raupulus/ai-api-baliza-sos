#!/usr/bin/env python3
"""Normaliza el Nomenclátor Geográfico de Andalucía (NGA) a CSV para Cádiz.

El WFS de deegree tiene el filtro espacial roto (`intersects()` no existe) y el
filtro por `provincia` devuelve 0 (encoding). Se filtra por los campos escalares
`coordenadaX`/`coordenadaY` (UTM 30N) dentro del BBOX de Cádiz, vía POST WFS
1.1.0. Las coordenadas UTM se convierten a WGS84 con la fórmula inversa.

Salida: `data/processed/csv/nga_toponimos_cadiz.csv` (referencia estructurada).
"""
from __future__ import annotations

import csv
import math
import re
import sys
import urllib.request
from pathlib import Path

ENDPOINT = "https://www.ideandalucia.es/wfs-nga/services"
# BBOX Cádiz en UTM 30N (EPSG:25830).
MIN_X, MIN_Y, MAX_X, MAX_Y = 184293.0, 3984068.0, 313261.0, 4102481.0
MAX_FEATURES = 15000  # límite del servidor (DefaultMaxFeatures)


def _utm_to_wgs84(easting: float, northing: float, zone: int = 30) -> tuple[float, float]:
    a = 6378137.0
    f = 1 / 298.257223563
    k0 = 0.9996
    e2 = f * (2 - f)
    ep2 = e2 / (1 - e2)
    x = easting - 500000.0
    y = northing
    m = y / k0
    mu = m / (a * (1 - e2 / 4 - 3 * e2 * e2 / 64 - 5 * e2 ** 3 / 256))
    e1 = (1 - math.sqrt(1 - e2)) / (1 + math.sqrt(1 - e2))
    phi1 = (
        mu + (3 * e1 / 2 - 27 * e1 ** 3 / 32) * math.sin(2 * mu)
        + (21 * e1 ** 2 / 16 - 55 * e1 ** 4 / 32) * math.sin(4 * mu)
        + (151 * e1 ** 3 / 96) * math.sin(6 * mu)
        + (1097 * e1 ** 4 / 512) * math.sin(8 * mu)
    )
    n1 = a / math.sqrt(1 - e2 * math.sin(phi1) ** 2)
    t1 = math.tan(phi1) ** 2
    c1 = ep2 * math.cos(phi1) ** 2
    r1 = a * (1 - e2) / (1 - e2 * math.sin(phi1) ** 2) ** 1.5
    d = x / (n1 * k0)
    lat = phi1 - (n1 * math.tan(phi1) / r1) * (
        d * d / 2 - (5 + 3 * t1 + 10 * c1 - 4 * c1 * c1 - 9 * ep2) * d ** 4 / 24
        + (61 + 90 * t1 + 298 * c1 + 45 * t1 * t1 - 252 * ep2 - 3 * c1 * c1) * d ** 6 / 720
    )
    lon = (d - (1 + 2 * t1 + c1) * d ** 3 / 6
           + (5 - 2 * c1 + 28 * t1 - 3 * c1 * c1 + 8 * ep2 + 24 * t1 * t1) * d ** 5 / 120) / math.cos(phi1)
    lon0 = (zone * 6 - 183) * math.pi / 180
    return math.degrees(lat), math.degrees(lon0 + lon)


def _post_filtrar(start_index: int) -> str:
    filtro = f"""<ogc:And>
      <ogc:PropertyIsGreaterThanOrEqualTo><ogc:PropertyName>app:coordenadaX</ogc:PropertyName><ogc:Literal>{MIN_X}</ogc:Literal></ogc:PropertyIsGreaterThanOrEqualTo>
      <ogc:PropertyIsLessThanOrEqualTo><ogc:PropertyName>app:coordenadaX</ogc:PropertyName><ogc:Literal>{MAX_X}</ogc:Literal></ogc:PropertyIsLessThanOrEqualTo>
      <ogc:PropertyIsGreaterThanOrEqualTo><ogc:PropertyName>app:coordenadaY</ogc:PropertyName><ogc:Literal>{MIN_Y}</ogc:Literal></ogc:PropertyIsGreaterThanOrEqualTo>
      <ogc:PropertyIsLessThanOrEqualTo><ogc:PropertyName>app:coordenadaY</ogc:PropertyName><ogc:Literal>{MAX_Y}</ogc:Literal></ogc:PropertyIsLessThanOrEqualTo>
    </ogc:And>"""
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<wfs:GetFeature service="WFS" version="1.1.0" xmlns:wfs="http://www.opengis.net/wfs" xmlns:app="http://www.deegree.org/app" xmlns:ogc="http://www.opengis.net/ogc" maxFeatures="{MAX_FEATURES}" startIndex="{start_index}" srsName="EPSG:25830">
  <wfs:Query typeName="app:Entidad">
    <ogc:Filter>{filtro}</ogc:Filter>
  </wfs:Query>
</wfs:GetFeature>"""
    req = urllib.request.Request(
        ENDPOINT, data=xml.encode("utf-8"),
        headers={"Content-Type": "text/xml", "User-Agent": "bot-ia-auxiliar/0.1"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode("utf-8", "replace")


def _extraer(body: str) -> list[dict]:
    filas = []
    for m in re.finditer(
        r"<app:Entidad[^>]*>(.*?)</app:Entidad>", body, re.S
    ):
        b = m.group(1)
        nombre = re.search(r"<app:nombre>([^<]+)</app:nombre>", b)
        tipo = re.search(r"<app:tipo>([^<]+)</app:tipo>", b)
        mun = re.search(r"<app:municipio>([^<]+)</app:municipio>", b)
        x = re.search(r"<app:coordenadaX>([^<]+)</app:coordenadaX>", b)
        y = re.search(r"<app:coordenadaY>([^<]+)</app:coordenadaY>", b)
        if not (nombre and tipo and x and y):
            continue
        lat, lon = _utm_to_wgs84(float(x.group(1)), float(y.group(1)))
        filas.append({
            "nombre": nombre.group(1).strip(),
            "tipo": tipo.group(1).strip(),
            "municipio": mun.group(1).strip() if mun else "",
            "lat": round(lat, 6),
            "lon": round(lon, 6),
        })
    return filas


def main() -> int:
    todas: list[dict] = []
    start = 0
    while True:
        body = _post_filtrar(start)
        filas = _extraer(body)
        if not filas:
            break
        todas.extend(filas)
        start += len(filas)
        print(f"  start={start}: {len(todas)} acumulados", file=sys.stderr)

    # Deduplicar por (nombre, tipo, municipio).
    unicas = {f"{f['nombre']}|{f['tipo']}|{f['municipio']}": f for f in todas}
    filas = list(unicas.values())
    print(f"NGA Cádiz: {len(todas)} registros, {len(filas)} únicos")

    dest = Path("data/processed/csv/nga_toponimos_cadiz.csv")
    cols = ["id", "categoria", "subcategoria", "titulo", "contenido", "fuente",
            "fuente_url", "nivel_confianza", "provincia", "municipio", "lat", "lon",
            "fecha_verificacion"]
    with open(dest, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for i, r in enumerate(sorted(filas, key=lambda x: x["nombre"]), 1):
            w.writerow({
                "id": f"NGA-{i:05d}",
                "categoria": "geografia",
                "subcategoria": "toponimo",
                "titulo": r["nombre"],
                "contenido": f"{r['nombre']} ({r['tipo']}) en {r['municipio'] or 'Cádiz'}. WGS84: {r['lat']}, {r['lon']}.",
                "fuente": "IECA — Nomenclátor Geográfico de Andalucía (WFS app:Entidad)",
                "fuente_url": "https://www.ideandalucia.es/wfs-nga/services",
                "nivel_confianza": "alta",
                "provincia": "Cádiz",
                "municipio": r["municipio"],
                "lat": r["lat"],
                "lon": r["lon"],
                "fecha_verificacion": "2026-08-28",
            })
    print(f"Escritos {len(filas)} topónimos en {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
