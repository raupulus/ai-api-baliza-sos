"""Registro de fuentes de datos.

`SOURCES` mapea nombre -> clase Source. El CLI del actualizador usa este registro
para `--source <nombre>` y `--all`.
"""

from __future__ import annotations

from updater.sources.base import Source
from updater.sources.gbif import GbifSource
from updater.sources.overpass import OverpassSource
from updater.sources.stubs import (
    AemetSource,
    IgnSource,
    MitecoSource,
    PrimerosAuxiliosSource,
    SupervivenciaSource,
)
from updater.sources.wikidata import WikidataSource

# Orden recomendado de ejecución: primero lo seguro y por API.
SOURCES: dict[str, type[Source]] = {
    OverpassSource.nombre: OverpassSource,
    WikidataSource.nombre: WikidataSource,
    GbifSource.nombre: GbifSource,
    AemetSource.nombre: AemetSource,
    IgnSource.nombre: IgnSource,
    MitecoSource.nombre: MitecoSource,
    SupervivenciaSource.nombre: SupervivenciaSource,
    PrimerosAuxiliosSource.nombre: PrimerosAuxiliosSource,
}

# Fuentes ya implementadas con lógica real (el resto son stubs).
IMPLEMENTADAS = {OverpassSource.nombre, WikidataSource.nombre, GbifSource.nombre}


def get_source(nombre: str) -> Source:
    if nombre not in SOURCES:
        raise KeyError(f"Fuente desconocida: {nombre}. Disponibles: {', '.join(SOURCES)}")
    return SOURCES[nombre]()


__all__ = ["SOURCES", "IMPLEMENTADAS", "get_source", "Source"]
