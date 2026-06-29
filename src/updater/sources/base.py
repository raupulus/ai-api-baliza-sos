"""Interfaz común de las fuentes de datos.

Cada conector implementa `fetch()` y produce una lista de `Fragmento` ya
normalizados. El pipeline del actualizador se encarga del staging, el checkpoint
humano y el indexado; la fuente solo adquiere y normaliza.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from common.config import settings
from common.models import Fragmento


class Source(ABC):
    #: identificador único de la fuente (para CLI y registro de ingestas)
    nombre: str = "base"
    #: licencia de los datos (rellenar en cada fuente)
    licencia: str | None = None
    #: "api" | "scraping_pdf"
    metodo: str = "api"

    def __init__(self) -> None:
        self.provincia = settings.provincia
        self.bbox = settings.bbox_tuple

    @abstractmethod
    def fetch(self) -> list[Fragmento]:
        """Adquiere y normaliza los datos. Devuelve fragmentos listos para staging."""
        raise NotImplementedError

    def disponible(self) -> bool:
        """Indica si la fuente puede ejecutarse (p. ej. tiene clave de API)."""
        return True
