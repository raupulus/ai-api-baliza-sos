#!/usr/bin/env python3
"""Filtra el GTFS de Cercanías de Renfe por el núcleo de Cádiz y genera CSV.

El GTFS descargado cubre toda España (848 rutas). El núcleo de Cádiz se
identifica por el prefijo de `route_id`:

  - `31T` → núcleo de Cádiz (Cercanías C-1/C-1a + Tranvía de la Bahía T-1)
  - `30T` → núcleo de Sevilla (se descarta; solo roza el BBOX por Lebrija)
  - `10T` → núcleo de Madrid (se descarta)

Salida:
  - `data/processed/csv/transporte_publico_renfe_cadiz.csv` (paradas únicas)
  - `data/processed/csv/lineas_cercanias_cadiz.csv` (líneas de referencia)

Clasificación de subcategoría:
  - parada servida solo por T-1 (tranvía)  → `parada_tranvia`
  - parada servida por C-1/C-1a (tren)     → `estacion_cercanias`
"""
from __future__ import annotations

import csv
import io
import sys
import zipfile
from pathlib import Path

# Prefijo de route_id correspondiente al núcleo de Cádiz (verificado 2026-08-28).
PREFIJO_NUCLEO = "31T"

TREN = "estacion_cercanias"
TRANVIA = "parada_tranvia"


def _read_txt(z: zipfile.ZipFile, nombre: str) -> list[dict]:
    with z.open(nombre) as fh:
        reader = csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8-sig"))
        return [{k.strip(): (v or "").strip() for k, v in row.items()} for row in reader]


def main() -> int:
    zip_path = Path(
        "data/raw/downloads/transporte-publico/2026-08-28/renfe/renfe_cercanias_gtfs.zip"
    )
    if not zip_path.exists():
        print(f"ERROR: no existe {zip_path}", file=sys.stderr)
        return 2

    with zipfile.ZipFile(zip_path) as z:
        routes = _read_txt(z, "routes.txt")
        trips = _read_txt(z, "trips.txt")
        stops = _read_txt(z, "stops.txt")

        routes_cadiz = [r for r in routes if r["route_id"].startswith(PREFIJO_NUCLEO)]
        route_ids = {r["route_id"] for r in routes_cadiz}

        trips_cadiz = [t for t in trips if t["route_id"] in route_ids]
        trip_ids = {t["trip_id"] for t in trips_cadiz}

        # Mapa trip_id -> modo, precalculado para el streaming de stop_times.
        short_por_route = {r["route_id"]: r["route_short_name"] for r in routes_cadiz}
        modo_por_trip = {
            t["trip_id"]: (TRANVIA if short_por_route.get(t["route_id"]) == "T1" else TREN)
            for t in trips_cadiz
        }

        # stop_times.txt es grande (287 MB): se lee en streaming, sin cargarlo entero.
        stop_ids_por_modo: dict[str, set[str]] = {TREN: set(), TRANVIA: set()}
        with z.open("stop_times.txt") as fh:
            reader = csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8-sig"))
            for row in reader:
                trip_id = (row.get("trip_id") or "").strip()
                stop_id = (row.get("stop_id") or "").strip()
                if trip_id not in trip_ids or not stop_id:
                    continue
                stop_ids_por_modo[modo_por_trip[trip_id]].add(stop_id)

        # Una parada se clasifica como tranvía solo si NUNCA la sirve un tren.
        ids_tren = stop_ids_por_modo[TREN]
        ids_tranvia = stop_ids_por_modo[TRANVIA] - ids_tren

        stops_map = {s["stop_id"]: s for s in stops}

    def _filas(ids: set[str], subcategoria: str) -> list[dict]:
        filas = []
        for i, sid in enumerate(sorted(ids, key=lambda x: stops_map[x]["stop_name"]), 1):
            s = stops_map[sid]
            lat = round(float(s["stop_lat"]), 6)
            lon = round(float(s["stop_lon"]), 6)
            filas.append({
                "id": f"RENFE-PAR-{i:04d}" if subcategoria == TREN else f"TRANVIA-PAR-{i:04d}",
                "categoria": "transporte",
                "subcategoria": subcategoria,
                "titulo": s["stop_name"],
                "contenido": f"Estación/parada: {s['stop_name']}. WGS84: {lat}, {lon}.",
                "fuente": "Renfe Viajeros (GTFS Cercanías)",
                "fuente_url": "https://data.renfe.com/es/dataset/horarios-cercanias",
                "nivel_confianza": "alta",
                "provincia": "Cádiz",
                "municipio": "",
                "lat": lat,
                "lon": lon,
                "fecha_verificacion": "2026-08-28",
            })
        return filas

    filas = _filas(ids_tren, TREN) + _filas(ids_tranvia, TRANVIA)

    print(f"Rutas núcleo Cádiz (prefijo {PREFIJO_NUCLEO}): {len(routes_cadiz)}")
    print(f"Trips Cádiz: {len(trips_cadiz)}")
    print(f"Paradas tren (C-1/C-1a): {len(ids_tren)}")
    print(f"Paradas tranvía (T-1): {len(ids_tranvia)}")
    print(f"Paradas totales únicas: {len(filas)}")

    dest = Path("data/processed/csv/transporte_publico_renfe_cadiz.csv")
    cols = ["id", "categoria", "subcategoria", "titulo", "contenido", "fuente",
            "fuente_url", "nivel_confianza", "provincia", "municipio", "lat", "lon",
            "fecha_verificacion"]
    with open(dest, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(filas)
    print(f"Escritas {len(filas)} paradas en {dest}")

    # Listado de líneas de referencia.
    lineas = sorted(
        {
            (
                r["route_short_name"],
                r["route_long_name"],
                TRANVIA if r["route_short_name"] == "T1" else TREN,
            )
            for r in routes_cadiz
        }
    )
    lineas_path = Path("data/processed/csv/lineas_cercanias_cadiz.csv")
    with open(lineas_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["linea", "recorrido", "modo"])
        for short, long_, modo in lineas:
            w.writerow([short, long_, modo])
    print(f"Líneas únicas: {len(lineas)} (guardadas en {lineas_path})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
