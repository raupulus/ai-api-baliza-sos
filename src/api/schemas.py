"""Esquemas pydantic de entrada/salida de la API (contrato HTTP).

Ver docs/info/05-contratos-datos.md.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Ubicacion(BaseModel):
    lat: float
    lon: float


class ConsultaRequest(BaseModel):
    consulta: str = Field(..., min_length=1, max_length=2000)
    idioma: str = "es"
    categoria_sugerida: str | None = None
    ubicacion: Ubicacion | None = None
    cliente: str | None = None
    id_conversacion: str | None = None


class FuenteOut(BaseModel):
    titulo: str
    fecha: str | None = None
    url: str | None = None


class ConsultaResponse(BaseModel):
    ok: bool = True
    mensajes: list[str]
    categoria: str | None = None
    confianza: float = 0.0
    fuentes: list[FuenteOut] = Field(default_factory=list)
    modelo: str | None = None
    tiempo_ms: int = 0
    truncado: bool = False


class ErrorResponse(BaseModel):
    ok: bool = False
    error: str
    detalle: str | None = None


class HealthResponse(BaseModel):
    ok: bool
    db: bool
    llm: bool
    embeddings: bool
