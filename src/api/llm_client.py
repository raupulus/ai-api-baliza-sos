"""Cliente HTTP fino hacia `llama-server` (API compatible OpenAI de llama.cpp).

Mantiene el desacople: el código no sabe qué modelo hay detrás, solo habla con
el servidor en `settings.llm_base_url`. El modelo se elige por `LLM_MODEL_PATH`
en la configuración del servicio `llama-server` (no aquí).

Reintentos: solo ante errores de CONEXIÓN (p. ej. una pausa por GC del servidor
o un arranque en frío), con backoff corto. Los TIMEOUTS no se reintentan: una
generación puede durar minutos y reintentarla excedería el presupuesto de tiempo
del cliente (5 min). (Corrige el hallazgo 3a de la auditoría.)
"""

from __future__ import annotations

import logging
import time

import httpx

from common.config import settings
from common.errors import LLMError, LLMTimeoutError, LLMUnavailableError

_log = logging.getLogger(__name__)


class LLMClient:
    """Cliente síncrono/asíncrono hacia llama-server."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float | None = None,
        *,
        connect_retries: int = 2,
        connect_backoff: float = 1.5,
    ) -> None:
        self.base_url = (base_url or settings.llm_base_url).rstrip("/")
        self.timeout = timeout if timeout is not None else float(settings.llm_timeout_seconds)
        self.connect_retries = connect_retries
        self.connect_backoff = connect_backoff

    def _payload(self, prompt: str, *, max_tokens: int | None, temperature: float | None) -> dict:
        return {
            "prompt": prompt,
            "n_predict": max_tokens if max_tokens is not None else settings.llm_max_tokens,
            "temperature": (
                temperature if temperature is not None else settings.llm_temperature
            ),
            "stop": ["\n\n\n"],
            "cache_prompt": True,
        }

    @staticmethod
    def _extract(data: dict) -> str:
        # llama-server `/completion` devuelve {"content": "..."}.
        if "content" in data:
            return str(data["content"]).strip()
        # Compatibilidad con formato OpenAI `/v1/completions`.
        if "choices" in data and data["choices"]:
            return str(data["choices"][0].get("text", "")).strip()
        raise LLMError("Respuesta del LLM en formato inesperado.")

    def generate(
        self,
        prompt: str,
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        url = f"{self.base_url}/completion"
        payload = self._payload(prompt, max_tokens=max_tokens, temperature=temperature)
        intento = 0
        while True:
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.post(url, json=payload)
                    resp.raise_for_status()
                    return self._extract(resp.json())
            except httpx.TimeoutException as exc:
                # No se reintenta: excedería el presupuesto de tiempo.
                raise LLMTimeoutError(f"El LLM no respondió en {self.timeout}s.") from exc
            except httpx.ConnectError as exc:
                intento += 1
                if intento > self.connect_retries:
                    raise LLMUnavailableError(
                        "No se pudo conectar con llama-server tras varios intentos."
                    ) from exc
                espera = self.connect_backoff * intento
                _log.warning("Conexión con llama-server falló (intento %d); reintento en %.1fs",
                             intento, espera)
                time.sleep(espera)
            except httpx.HTTPStatusError as exc:
                raise LLMError(f"llama-server devolvió {exc.response.status_code}.") from exc

    async def generate_async(
        self,
        prompt: str,
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        import asyncio

        url = f"{self.base_url}/completion"
        payload = self._payload(prompt, max_tokens=max_tokens, temperature=temperature)
        intento = 0
        while True:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(url, json=payload)
                    resp.raise_for_status()
                    return self._extract(resp.json())
            except httpx.TimeoutException as exc:
                raise LLMTimeoutError(f"El LLM no respondió en {self.timeout}s.") from exc
            except httpx.ConnectError as exc:
                intento += 1
                if intento > self.connect_retries:
                    raise LLMUnavailableError(
                        "No se pudo conectar con llama-server tras varios intentos."
                    ) from exc
                await asyncio.sleep(self.connect_backoff * intento)
            except httpx.HTTPStatusError as exc:
                raise LLMError(f"llama-server devolvió {exc.response.status_code}.") from exc

    def health(self) -> bool:
        """Comprueba que llama-server está vivo (endpoint /health)."""
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(f"{self.base_url}/health")
                return resp.status_code == 200
        except httpx.HTTPError:
            return False
