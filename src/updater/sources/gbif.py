"""Fuente GBIF: biodiversidad geolocalizada (fauna/flora) de la provincia.

Riesgo medio. Adquiere por API las especies con más registros dentro del BBOX,
recupera sus nombres comunes y una breve descripción, y genera fragmentos de
fauna/flora. Toda especie que el heurístico marque como potencialmente peligrosa
se etiqueta `peligrosa=True` y se enruta a checkpoint humano (no se indexa sin
validación).

Licencia: datos GBIF (variada por dataset; se cita GBIF y el dataset cuando
aplica). El nivel de confianza de la descripción es MEDIA salvo validación.
"""

from __future__ import annotations

import logging

from common.models import Categoria, Fragmento, NivelConfianza
from updater.http_client import HttpClient
from updater.sources.base import Source

_log = logging.getLogger(__name__)

GBIF_OCC = "https://api.gbif.org/v1/occurrence/search"
GBIF_SPECIES = "https://api.gbif.org/v1/species"

# Heurístico de peligrosidad (dispara checkpoint humano). Ampliable.
_PALABRAS_PELIGRO = (
    "medusa", "carabela", "víbora", "vibora", "escorpión", "escorpion",
    "araña", "arana", "avispa", "araña reclusa", "pez araña", "raya",
    "alacrán", "alacran", "tejo", "adelfa", "estramonio", "cicuta",
)

# Familias/grupos de interés para acotar (opcional). Se deja amplio.
_LIMITE_ESPECIES = 30


class GbifSource(Source):
    nombre = "gbif"
    licencia = "GBIF (ver dataset de origen)"
    metodo = "api"

    def fetch(self) -> list[Fragmento]:
        min_lon, min_lat, max_lon, max_lat = self.bbox
        params = {
            "decimalLatitude": f"{min_lat},{max_lat}",
            "decimalLongitude": f"{min_lon},{max_lon}",
            "hasCoordinate": "true",
            "limit": 0,
            "facet": "speciesKey",
            "facetLimit": _LIMITE_ESPECIES,
        }
        fragmentos: list[Fragmento] = []
        with HttpClient(min_interval=1.0) as http:
            data = http.get_json(GBIF_OCC, params=params)
            facetas = data.get("facets", [])
            claves = []
            for f in facetas:
                if f.get("field") == "SPECIES_KEY":
                    claves = [c["name"] for c in f.get("counts", [])]
                    break

            for clave in claves:
                try:
                    frag = self._especie_a_fragmento(http, clave)
                    if frag:
                        fragmentos.append(frag)
                except Exception as exc:  # no abortar todo por una especie
                    _log.warning("GBIF: especie %s fallida: %s", clave, exc)

        _log.info("GBIF: %d fragmentos (%d marcados peligrosos)",
                  len(fragmentos), sum(f.peligrosa for f in fragmentos))
        return fragmentos

    def _especie_a_fragmento(self, http: HttpClient, species_key: str) -> Fragmento | None:
        info = http.get_json(f"{GBIF_SPECIES}/{species_key}")
        cientifico = info.get("scientificName") or info.get("canonicalName")
        if not cientifico:
            return None

        # Nombre común en español si existe.
        vernac = http.get_json(f"{GBIF_SPECIES}/{species_key}/vernacularNames")
        nombre_es = None
        for v in vernac.get("results", []):
            if v.get("language") == "spa":
                nombre_es = v.get("vernacularName")
                break

        nombre = nombre_es or cientifico
        reino = (info.get("kingdom") or "").lower()
        categoria = Categoria.FLORA if reino == "plantae" else Categoria.FAUNA

        texto = (
            f"{nombre} ({cientifico}). Presente en la provincia de {self.provincia}. "
            f"Grupo: {info.get('class') or info.get('phylum') or reino or 'desconocido'}."
        )
        peligrosa = self._es_peligrosa(f"{nombre} {cientifico}")
        if peligrosa:
            texto += " ATENCIÓN: posible especie peligrosa; requiere validación."

        return Fragmento(
            texto=texto,
            fuente="GBIF",
            fuente_url=f"https://www.gbif.org/species/{species_key}",
            categoria=categoria,
            subcategoria="especie",
            provincia=self.provincia,
            nivel_confianza=NivelConfianza.MEDIA,
            licencia=self.licencia,
            peligrosa=peligrosa,
        )

    @staticmethod
    def _es_peligrosa(texto: str) -> bool:
        t = texto.lower()
        return any(p in t for p in _PALABRAS_PELIGRO)
