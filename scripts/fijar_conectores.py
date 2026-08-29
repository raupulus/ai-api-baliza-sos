#!/usr/bin/env python3
"""Fija (snapshot) los conectores en vivo Overpass, Wikidata y GBIF a CSV.

Los conectores de `src/updater/sources/` consultan APIs en vivo y dependen de
`httpx` (no instalado en el entorno de operación). Este script replica las mismas
consultas usando solo stdlib (`urllib`) y vuelca el resultado a CSVs estables en
`data/processed/csv/`, conforme a `PLANTILLA.csv`.

Uso:
    python3 scripts/fijar_conectores.py [overpass|wikidata|gbif|todo]
"""
from __future__ import annotations

import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from common.config import settings  # noqa: E402

UA = settings.updater_user_agent
MIN_LON, MIN_LAT, MAX_LON, MAX_LAT = settings.bbox_tuple
HOY = date.today().isoformat()

COLS = ["id", "categoria", "subcategoria", "titulo", "contenido", "fuente",
        "fuente_url", "nivel_confianza", "provincia", "municipio", "lat", "lon",
        "fecha_verificacion"]


def _get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def _post(url: str, data: dict) -> str:
    body = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read().decode("utf-8")


def _escribir(nombre: str, filas: list[dict]) -> None:
    dest = Path(f"data/processed/csv/{nombre}")
    with open(dest, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(filas)
    print(f"  {nombre}: {len(filas)} registros → {dest}")


def overpass() -> None:
    """POIs de OSM (playas, faros, agua, hospitales, farmacias, refugios...)."""
    objetivos = [
        ("natural", "beach", "playa", "geografia"),
        ("man_made", "lighthouse", "faro", "orientacion"),
        ("amenity", "drinking_water", "agua potable", "supervivencia"),
        ("amenity", "hospital", "hospital", "geografia"),
        ("amenity", "clinic", "centro de salud", "geografia"),
        ("amenity", "pharmacy", "farmacia", "geografia"),
        ("tourism", "alpine_hut", "refugio", "supervivencia"),
        ("amenity", "shelter", "refugio", "supervivencia"),
    ]
    bbox = f"{MIN_LAT},{MIN_LON},{MAX_LAT},{MAX_LON}"
    partes = []
    for clave, valor, _etq, _cat in objetivos:
        partes.append(f'node["{clave}"="{valor}"]({bbox});')
        partes.append(f'way["{clave}"="{valor}"]({bbox});')
    query = f"[out:json][timeout:60];\n(\n" + "\n".join(partes) + "\n);\nout center tags;"
    data = json.loads(_post("https://overpass-api.de/api/interpreter", {"data": query}))

    etiquetas = {(c, v): (e, cat) for c, v, e, cat in objetivos}
    filas = []
    for i, el in enumerate(data.get("elements", []), 1):
        tags = el.get("tags", {})
        hit = next(((etq, cat) for (c, v), (etq, cat) in etiquetas.items() if tags.get(c) == v), None)
        if not hit:
            continue
        etq, cat = hit
        nombre = tags.get("name") or etq
        lat = el.get("lat") or (el.get("center") or {}).get("lat")
        lon = el.get("lon") or (el.get("center") or {}).get("lon")
        if lat is None or lon is None:
            continue
        extra = []
        if tags.get("addr:city"):
            extra.append(f"en {tags['addr:city']}")
        cola = (" " + ", ".join(extra)) if extra else ""
        contenido = f"{nombre} ({etq}){cola}. Coordenadas aprox: {lat:.4f}, {lon:.4f}."
        filas.append({
            "id": f"OVERPASS-{i:04d}", "categoria": cat, "subcategoria": etq,
            "titulo": nombre, "contenido": contenido,
            "fuente": "OpenStreetMap (Overpass)",
            "fuente_url": f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}",
            "nivel_confianza": "alta", "provincia": "Cádiz", "municipio": tags.get("addr:city", ""),
            "lat": round(float(lat), 6), "lon": round(float(lon), 6), "fecha_verificacion": HOY,
        })
    _escribir("overpass_pois_cadiz.csv", filas)


def wikidata() -> None:
    """Lugares naturales de Cádiz vía SPARQL (playas, faros, parques, cabos, ríos).

    La cadena `P131*` no alcanza a las playas/faros (carecen de vínculo a la
    provincia), así que se usa búsqueda por radio con el centro de la provincia.
    """
    tipos = ["Q40080", "Q39715", "Q46169", "Q185113", "Q4022"]
    valores = " ".join(f"wd:{t}" for t in tipos)
    lon_c = (MIN_LON + MAX_LON) / 2
    lat_c = (MIN_LAT + MAX_LAT) / 2
    sparql = f"""
SELECT ?item ?itemLabel ?itemDescription ?coord WHERE {{
  VALUES ?tipo {{ {valores} }}
  ?item wdt:P31 ?tipo .
  SERVICE wikibase:around {{
    ?item wdt:P625 ?coord .
    bd:serviceParam wikibase:center "Point({lon_c} {lat_c})"^^geo:wktLiteral .
    bd:serviceParam wikibase:radius "90" .
  }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "es". }}
}}
LIMIT 200
"""
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"format": "json", "query": sparql})
    data = json.loads(_get(url))
    filas = []
    i = 0
    for fila in data.get("results", {}).get("bindings", []):
        etiqueta = (fila.get("itemLabel") or {}).get("value")
        if not etiqueta:
            continue
        i += 1
        desc = (fila.get("itemDescription") or {}).get("value", "")
        item_url = (fila.get("item") or {}).get("value", "")
        texto = f"{etiqueta}. {desc}".strip().rstrip(".") + f". (provincia de Cádiz)"
        filas.append({
            "id": f"WIKIDATA-{i:04d}", "categoria": "geografia", "subcategoria": "lugar",
            "titulo": etiqueta, "contenido": texto,
            "fuente": "Wikidata", "fuente_url": item_url,
            "nivel_confianza": "media", "provincia": "Cádiz", "municipio": "",
            "lat": "", "lon": "", "fecha_verificacion": HOY,
        })
    _escribir("wikidata_lugares_cadiz.csv", filas)


def gbif() -> None:
    """Top de especies con presencia en el BBOX (ocurrencias georreferenciadas)."""
    params = {
        "decimalLatitude": f"{MIN_LAT},{MAX_LAT}",
        "decimalLongitude": f"{MIN_LON},{MAX_LON}",
        "hasCoordinate": "true", "limit": 0,
        "facet": "speciesKey", "facetLimit": 30,
    }
    occ_url = "https://api.gbif.org/v1/occurrence/search?" + urllib.parse.urlencode(params)
    data = json.loads(_get(occ_url))
    claves = []
    for f in data.get("facets", []):
        if f.get("field") == "SPECIES_KEY":
            claves = [c["name"] for c in f.get("counts", [])]
            break

    peligro = ("medusa", "carabela", "víbora", "vibora", "escorpión", "escorpion",
               "araña", "arana", "avispa", "pez araña", "raya", "alacrán", "alacran",
               "tejo", "adelfa", "estramonio", "cicuta")
    filas = []
    for i, clave in enumerate(claves, 1):
        try:
            info = json.loads(_get(f"https://api.gbif.org/v1/species/{clave}"))
            vern = json.loads(_get(f"https://api.gbif.org/v1/species/{clave}/vernacularNames"))
            cientifico = info.get("scientificName") or info.get("canonicalName")
            if not cientifico:
                continue
            nombre_es = next((v.get("vernacularName") for v in vern.get("results", [])
                              if v.get("language") == "spa"), None)
            nombre = nombre_es or cientifico
            reino = (info.get("kingdom") or "").lower()
            categoria = "flora" if reino == "plantae" else "fauna"
            texto = f"{nombre} ({cientifico}). Presente en la provincia de Cádiz. " \
                    f"Grupo: {info.get('class') or info.get('phylum') or reino or 'desconocido'}."
            es_peligrosa = any(p in f"{nombre} {cientifico}".lower() for p in peligro)
            if es_peligrosa:
                texto += " ATENCIÓN: posible especie peligrosa; requiere validación."
            filas.append({
                "id": f"GBIF-{i:04d}", "categoria": categoria, "subcategoria": "especie",
                "titulo": nombre, "contenido": texto,
                "fuente": "GBIF", "fuente_url": f"https://www.gbif.org/species/{clave}",
                "nivel_confianza": "media", "provincia": "Cádiz", "municipio": "",
                "lat": "", "lon": "", "fecha_verificacion": HOY,
            })
            time.sleep(1.0)
        except Exception as exc:
            print(f"  GBIF especie {clave} fallida: {exc}", file=sys.stderr)
    _escribir("gbif_especies_cadiz.csv", filas)


def main() -> int:
    sel = sys.argv[1] if len(sys.argv) > 1 else "todo"
    if sel in ("overpass", "todo"):
        print("Overpass...")
        overpass()
    if sel in ("wikidata", "todo"):
        print("Wikidata...")
        wikidata()
    if sel in ("gbif", "todo"):
        print("GBIF...")
        gbif()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
