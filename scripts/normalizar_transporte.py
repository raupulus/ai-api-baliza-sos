#!/usr/bin/env python3
"""Filtra el GTFS unificado de CTAN por los consorcios de Cádiz y genera CSV.

Consorcios de Cádiz en el GTFS unificado:
  - agency_id 2 = CMTBC (Bahía de Cádiz)
  - agency_id 5 = CTMCG (Campo de Gibraltar)

Salida: `data/processed/csv/transporte_publico_cadiz.csv` con paradas únicas
(stop_id, stop_name, lat, lon) de ambos consorcios, más un listado de líneas.
"""
from __future__ import annotations

import csv
import io
import sys
import zipfile
from pathlib import Path

CONSORCIOS_CADIZ = {"CMTBC": "Bahía de Cádiz", "CTMCG": "Campo de Gibraltar"}


def _read_zip_txt(zip_path: Path, nombre: str) -> list[dict]:
    with zipfile.ZipFile(zip_path) as z:
        data = z.read(nombre).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(data))
    return list(reader)


def main() -> int:
    zip_path = Path("data/raw/downloads/transporte-publico/2026-08-28/ctan/ctan_unificado_gtfs.zip")
    if not zip_path.exists():
        print(f"ERROR: no existe {zip_path}", file=sys.stderr)
        return 2

    routes = _read_zip_txt(zip_path, "routes.txt")
    trips = _read_zip_txt(zip_path, "trips.txt")
    stops = _read_zip_txt(zip_path, "stops.txt")
    stop_times = _read_zip_txt(zip_path, "stop_times.txt")

    # Rutas de los consorcios de Cádiz (agency_id 2 o 5).
    routes_cadiz = [r for r in routes if r["agency_id"] in CONSORCIOS_CADIZ]
    route_ids = {r["route_id"] for r in routes_cadiz}

    # Trips de esas rutas.
    trips_cadiz = [t for t in trips if t["route_id"] in route_ids]
    trip_ids = {t["trip_id"] for t in trips_cadiz}

    # Stop IDs únicos usados por esos trips.
    stop_ids = {s["stop_id"] for s in stop_times if s["trip_id"] in trip_ids}

    # Paradas únicas de Cádiz.
    stops_cadiz = [s for s in stops if s["stop_id"] in stop_ids]

    print(f"Rutas Cádiz: {len(routes_cadiz)}")
    print(f"Trips Cádiz: {len(trips_cadiz)}")
    print(f"Paradas Cádiz: {len(stops_cadiz)}")

    # Salida CSV conforme a PLANTILLA.csv.
    filas = []
    for i, s in enumerate(sorted(stops_cadiz, key=lambda s: s["stop_name"]), 1):
        lat = round(float(s["stop_lat"]), 6)
        lon = round(float(s["stop_lon"]), 6)
        filas.append({
            "id": f"TRANS-PAR-{i:04d}",
            "categoria": "transporte",
            "subcategoria": "parada_autobus",
            "titulo": s["stop_name"],
            "contenido": f"Parada de autobús: {s['stop_name']}. WGS84: {lat}, {lon}.",
            "fuente": "Red de Consorcios de Transporte de Andalucía (GTFS)",
            "fuente_url": "https://api.ctan.es/v1/datos/UNIFICADO/gtfs.zip",
            "nivel_confianza": "alta",
            "provincia": "Cádiz",
            "municipio": "",
            "lat": lat,
            "lon": lon,
            "fecha_verificacion": "2026-08-28",
        })

    dest = Path("data/processed/csv/transporte_publico_cadiz.csv")
    cols = ["id", "categoria", "subcategoria", "titulo", "contenido", "fuente",
            "fuente_url", "nivel_confianza", "provincia", "municipio", "lat", "lon",
            "fecha_verificacion"]
    with open(dest, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(filas)

    print(f"Escritas {len(filas)} paradas en {dest}")

    # Guardar también listado de líneas (route_short_name) para referencia.
    lineas = sorted({r["route_short_name"] for r in routes_cadiz if r.get("route_short_name")})
    lineas_path = Path("data/processed/csv/lineas_autobus_cadiz.csv")
    with open(lineas_path, "w", encoding="utf-8", newline="") as f:
        f.write("linea\n")
        for l in lineas:
            f.write(f"{l}\n")
    print(f"Líneas únicas: {len(lineas)} (guardadas en {lineas_path})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
