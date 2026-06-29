"""Excepciones del dominio. Se mapean a respuestas JSON de error en la API."""

from __future__ import annotations


class BotError(Exception):
    """Base de todos los errores del dominio."""

    codigo = "error_interno"
    http_status = 500

    def __init__(self, detalle: str = "") -> None:
        super().__init__(detalle or self.codigo)
        self.detalle = detalle


class ConfigError(BotError):
    codigo = "config_invalida"
    http_status = 500


class LLMError(BotError):
    codigo = "llm_error"
    http_status = 502


class LLMTimeoutError(LLMError):
    codigo = "llm_timeout"
    http_status = 504


class LLMUnavailableError(LLMError):
    codigo = "llm_no_disponible"
    http_status = 503


class EmbeddingError(BotError):
    codigo = "embedding_error"
    http_status = 500


class RetrievalError(BotError):
    codigo = "retrieval_error"
    http_status = 500


class DatabaseError(BotError):
    codigo = "db_error"
    http_status = 503


class ValidationError(BotError):
    codigo = "entrada_invalida"
    http_status = 400


class SourceError(BotError):
    """Error al adquirir/normalizar datos de una fuente (servicio actualizador)."""

    codigo = "source_error"
    http_status = 502
