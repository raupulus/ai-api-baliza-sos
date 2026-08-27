"""Registro de fuentes de datos.

`SOURCES` mapea nombre -> clase Source. El CLI del actualizador usa este registro
para `--source <nombre>` y `--all`.
"""

from __future__ import annotations

from updater.sources.base import Source
from updater.sources.fiestas_cadiz import FiestasCadizSource
from updater.sources.flora_fauna_cadiz import FloraFaunaCadizSource
from updater.sources.gbif import GbifSource
from updater.sources.historia_cadiz import HistoriaCadizSource
from updater.sources.municipios_cadiz import MunicipiosCadizSource
from updater.sources.overpass import OverpassSource
from updater.sources.primeros_auxilios_avanzado import PrimerosAuxiliosAvanzadoSource
from updater.sources.stubs import (
    AemetSource,
    IgnSource,
    MitecoSource,
    PrimerosAuxiliosSource,
    SupervivenciaSource,
)
from updater.sources.wikidata import WikidataSource

# Registro global de fuentes
SOURCES: dict[str, type[Source]] = {
    PrimerosAuxiliosAvanzadoSource.nombre: PrimerosAuxiliosAvanzadoSource,
    FloraFaunaCadizSource.nombre: FloraFaunaCadizSource,
    MunicipiosCadizSource.nombre: MunicipiosCadizSource,
    FiestasCadizSource.nombre: FiestasCadizSource,
    HistoriaCadizSource.nombre: HistoriaCadizSource,
    OverpassSource.nombre: OverpassSource,
    WikidataSource.nombre: WikidataSource,
    GbifSource.nombre: GbifSource,
    AemetSource.nombre: AemetSource,
    IgnSource.nombre: IgnSource,
    MitecoSource.nombre: MitecoSource,
    SupervivenciaSource.nombre: SupervivenciaSource,
    PrimerosAuxiliosSource.nombre: PrimerosAuxiliosSource,
}

# Fuentes ya implementadas con lógica real y validada
IMPLEMENTADAS = {
    PrimerosAuxiliosAvanzadoSource.nombre,
    FloraFaunaCadizSource.nombre,
    MunicipiosCadizSource.nombre,
    FiestasCadizSource.nombre,
    HistoriaCadizSource.nombre,
    OverpassSource.nombre,
    WikidataSource.nombre,
    GbifSource.nombre,
}


def get_source(nombre: str) -> Source:
    if nombre not in SOURCES:
        raise KeyError(f"Fuente desconocida: {nombre}. Disponibles: {', '.join(SOURCES)}")
    return SOURCES[nombre]()


__all__ = ["SOURCES", "IMPLEMENTADAS", "get_source", "Source"]
