"""Conectores pendientes de implementar (stubs documentados).

Siguen la interfaz `Source` para encajar ya en el registro y el CLI, pero su
`fetch()` aún no adquiere datos. Cada uno documenta su plan en
docs/planning/initial_plan/06_fuentes_datos_scraping.md.

IMPORTANTE: `PrimerosAuxiliosSource` produce contenido SENSIBLE; cuando se
implemente, todos sus fragmentos deben ir a checkpoint humano obligatorio
(categoría primeros_auxilios => requiere_validacion=True).
"""

from __future__ import annotations

from common.config import settings
from common.models import Fragmento
from updater.sources.base import Source


class _StubSource(Source):
    """Base de stubs: documenta y no produce fragmentos todavía."""

    def fetch(self) -> list[Fragmento]:
        raise NotImplementedError(
            f"La fuente '{self.nombre}' aún no está implementada. "
            "Ver docs/planning/initial_plan/06_fuentes_datos_scraping.md."
        )


class AemetSource(_StubSource):
    """Clima estacional (API AEMET). Requiere AEMET_API_KEY."""

    nombre = "aemet"
    licencia = "AEMET (uso conforme a sus condiciones)"
    metodo = "api"

    def disponible(self) -> bool:
        return bool(settings.aemet_api_key)


class IgnSource(_StubSource):
    """Topónimos y cartografía oficial (IGN)."""

    nombre = "ign"
    licencia = "IGN (CC-BY 4.0 / según producto)"
    metodo = "api"


class MitecoSource(_StubSource):
    """Inventario de especies e indicadores de peligrosidad (MITECO)."""

    nombre = "miteco"
    licencia = "MITECO (según conjunto)"
    metodo = "api"


class SupervivenciaSource(_StubSource):
    """Manuales de supervivencia oficiales con licencia abierta (PDF)."""

    nombre = "supervivencia"
    licencia = "Variada (solo licencias abiertas)"
    metodo = "scraping_pdf"


class PrimerosAuxiliosSource(_StubSource):
    """Guías de primeros auxilios oficiales (Cruz Roja, ERC, OMS, 112, SEMICYUC).

    CONTENIDO SENSIBLE: checkpoint humano obligatorio. No generar con LLM ni
    indexar scraping no verificado.
    """

    nombre = "primeros-auxilios"
    licencia = "Según organismo (solo material reutilizable)"
    metodo = "scraping_pdf"
