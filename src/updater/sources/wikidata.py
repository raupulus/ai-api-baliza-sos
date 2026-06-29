"""Fuente Wikidata: descripciones generales de lugares naturales de la provincia.

Riesgo bajo-medio. Vía SPARQL recupera elementos (playas, faros, parques
naturales, cabos) ubicados en la provincia con etiqueta y descripción en español,
y genera fragmentos de geografía/orientación.

Para adaptar a otra provincia hay que añadir su QID de Wikidata en `_QID_PROVINCIA`
(ver docs/planning/initial_plan/06_fuentes_datos_scraping.md). Licencia: CC0.
"""

from __future__ import annotations

import logging

from common.config import settings
from common.models import Categoria, Fragmento, NivelConfianza
from updater.http_client import HttpClient
from updater.sources.base import Source

_log = logging.getLogger(__name__)

WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"

# QID de Wikidata por provincia (ampliar al adaptar a otras provincias).
_QID_PROVINCIA = {
    "cadiz": "Q15695",   # Provincia de Cádiz
}

# Tipos de interés (instance of / P31): playa, faro, parque natural, cabo, río.
_TIPOS = ["Q40080", "Q39715", "Q46169", "Q185113", "Q4022"]


class WikidataSource(Source):
    nombre = "wikidata"
    licencia = "CC0 (Wikidata)"
    metodo = "api"

    def disponible(self) -> bool:
        return settings.provincia_slug in _QID_PROVINCIA

    def _sparql(self, qid_provincia: str) -> str:
        valores = " ".join(f"wd:{t}" for t in _TIPOS)
        return f"""
SELECT ?item ?itemLabel ?itemDescription ?coord WHERE {{
  VALUES ?tipo {{ {valores} }}
  ?item wdt:P31 ?tipo .
  ?item wdt:P131* wd:{qid_provincia} .
  OPTIONAL {{ ?item wdt:P625 ?coord . }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "es". }}
}}
LIMIT 200
"""

    def fetch(self) -> list[Fragmento]:
        qid = _QID_PROVINCIA.get(settings.provincia_slug)
        if not qid:
            _log.warning("Wikidata: sin QID para %s; fuente desactivada.", settings.provincia_slug)
            return []

        fragmentos: list[Fragmento] = []
        with HttpClient(min_interval=1.5) as http:
            data = http.get_json(
                WIKIDATA_SPARQL,
                params={"format": "json", "query": self._sparql(qid)},
            )

        for fila in data.get("results", {}).get("bindings", []):
            etiqueta = fila.get("itemLabel", {}).get("value")
            descripcion = fila.get("itemDescription", {}).get("value", "")
            item_url = fila.get("item", {}).get("value")
            if not etiqueta:
                continue
            texto = f"{etiqueta}. {descripcion}".strip().rstrip(".") + "."
            fragmentos.append(
                Fragmento(
                    texto=f"{texto} (provincia de {self.provincia})",
                    fuente="Wikidata",
                    fuente_url=item_url,
                    categoria=Categoria.GEOGRAFIA,
                    subcategoria="lugar",
                    provincia=self.provincia,
                    nivel_confianza=NivelConfianza.MEDIA,
                    licencia=self.licencia,
                )
            )
        _log.info("Wikidata: %d fragmentos", len(fragmentos))
        return fragmentos
