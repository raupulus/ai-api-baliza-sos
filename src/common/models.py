"""Modelos de datos compartidos por la API y el actualizador.

Se usan dataclasses (ligeras, sin dependencia de pydantic en el dominio). Los
esquemas de entrada/salida HTTP viven aparte en `api/schemas.py`.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class Categoria(str, Enum):
    PRIMEROS_AUXILIOS = "primeros_auxilios"
    FAUNA = "fauna"
    FLORA = "flora"
    GEOGRAFIA = "geografia"
    SUPERVIVENCIA = "supervivencia"
    ORIENTACION = "orientacion"
    CLIMA = "clima"
    CULTURA_HISTORIA = "cultura_historia"


class NivelConfianza(str, Enum):
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"


# Categorías cuyo contenido es sensible y SIEMPRE requiere validación humana
# antes de indexarse (ver módulo 05/07).
CATEGORIAS_SENSIBLES: frozenset[Categoria] = frozenset(
    {Categoria.PRIMEROS_AUXILIOS}
)


@dataclass
class Fragmento:
    """Unidad indexable de conocimiento (ver docs/info/05-contratos-datos.md)."""

    texto: str
    fuente: str
    categoria: Categoria
    nivel_confianza: NivelConfianza = NivelConfianza.MEDIA
    fuente_url: Optional[str] = None
    fecha: Optional[date] = None
    subcategoria: Optional[str] = None
    provincia: Optional[str] = None
    licencia: Optional[str] = None
    peligrosa: bool = False  # marca explícita de especie tóxica/peligrosa
    validado_por: Optional[str] = None
    validado_fecha: Optional[date] = None
    hash_contenido: str = ""
    id: Optional[str] = None
    embedding: Optional[list[float]] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if not self.hash_contenido:
            self.hash_contenido = self.calcular_hash()

    def calcular_hash(self) -> str:
        """Hash estable del contenido para idempotencia en la reindexación."""
        base = f"{self.fuente}|{self.categoria.value}|{self.texto.strip()}"
        return hashlib.sha256(base.encode("utf-8")).hexdigest()

    @property
    def requiere_validacion(self) -> bool:
        """True si no puede indexarse sin checkpoint humano."""
        return self.categoria in CATEGORIAS_SENSIBLES or self.peligrosa

    @property
    def validado(self) -> bool:
        return self.validado_por is not None


@dataclass
class Fuente:
    """Catálogo de una fuente de datos."""

    nombre: str
    url: Optional[str] = None
    licencia: Optional[str] = None
    metodo: str = "api"  # "api" | "scraping_pdf"
    frecuencia: Optional[str] = None
    activa: bool = True


@dataclass
class FragmentoRecuperado:
    """Fragmento devuelto por la recuperación, con su puntuación de similitud."""

    fragmento: Fragmento
    score: float
