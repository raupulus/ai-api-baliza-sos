"""Fuente Overpass / OpenStreetMap: geografía, playas, accesos y referencias.

Riesgo bajo, 100% API. Produce fragmentos de orientación/geografía con puntos de
referencia útiles para una persona perdida (playas, faros, agua potable,
hospitales, centros de salud, refugios).

Licencia OSM: ODbL. Se registra y se cita la fuente.
"""

from __future__ import annotations

import logging

from common.models import Categoria, Fragmento, NivelConfianza
from updater.http_client import HttpClient
from updater.sources.base import Source

_log = logging.getLogger(__name__)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# (clave OSM, valor, etiqueta legible, categoría)
_OBJETIVOS = [
    ("natural", "beach", "playa", Categoria.GEOGRAFIA),
    ("man_made", "lighthouse", "faro", Categoria.ORIENTACION),
    ("amenity", "drinking_water", "agua potable", Categoria.SUPERVIVENCIA),
    ("amenity", "hospital", "hospital", Categoria.GEOGRAFIA),
    ("amenity", "clinic", "centro de salud", Categoria.GEOGRAFIA),
    ("amenity", "pharmacy", "farmacia", Categoria.GEOGRAFIA),
    ("tourism", "alpine_hut", "refugio", Categoria.SUPERVIVENCIA),
    ("amenity", "shelter", "refugio", Categoria.SUPERVIVENCIA),
]


class OverpassSource(Source):
    nombre = "overpass-osm"
    licencia = "ODbL (OpenStreetMap)"
    metodo = "api"

    def _query(self) -> str:
        min_lon, min_lat, max_lon, max_lat = self.bbox
        bbox = f"{min_lat},{min_lon},{max_lat},{max_lon}"  # S,W,N,E
        partes = []
        for clave, valor, _etq, _cat in _OBJETIVOS:
            partes.append(f'node["{clave}"="{valor}"]({bbox});')
            partes.append(f'way["{clave}"="{valor}"]({bbox});')
        cuerpo = "\n".join(partes)
        return f"[out:json][timeout:60];\n(\n{cuerpo}\n);\nout center tags;"

    def fetch(self) -> list[Fragmento]:
        fragmentos: list[Fragmento] = []
        with HttpClient(min_interval=2.0) as http:
            data = http.post(OVERPASS_URL, data={"data": self._query()}).json()

        etiquetas = {(c, v): (e, cat) for c, v, e, cat in _OBJETIVOS}
        for el in data.get("elements", []):
            tags = el.get("tags", {})
            etq_cat = None
            for (clave, valor), (etq, cat) in etiquetas.items():
                if tags.get(clave) == valor:
                    etq_cat = (etq, cat)
                    break
            if not etq_cat:
                continue
            etq, cat = etq_cat

            nombre = tags.get("name") or etq
            lat = el.get("lat") or el.get("center", {}).get("lat")
            lon = el.get("lon") or el.get("center", {}).get("lon")
            if lat is None or lon is None:
                continue

            texto = self._describir(nombre, etq, lat, lon, tags)
            fragmentos.append(
                Fragmento(
                    texto=texto,
                    fuente="OpenStreetMap (Overpass)",
                    fuente_url=f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}",
                    categoria=cat,
                    subcategoria=etq,
                    provincia=self.provincia,
                    nivel_confianza=NivelConfianza.ALTA,
                    licencia=self.licencia,
                )
            )
        _log.info("Overpass: %d fragmentos", len(fragmentos))
        return fragmentos

    @staticmethod
    def _describir(nombre: str, tipo: str, lat: float, lon: float, tags: dict) -> str:
        extra = []
        if tags.get("addr:city"):
            extra.append(f"en {tags['addr:city']}")
        if tags.get("emergency") == "yes":
            extra.append("con servicio de emergencias")
        cola = (" " + ", ".join(extra)) if extra else ""
        return (
            f"{nombre} ({tipo}){cola}. Coordenadas aprox: {lat:.4f}, {lon:.4f}. "
            f"Punto de referencia en la provincia de {tags.get('addr:province', '')}".strip()
        )
