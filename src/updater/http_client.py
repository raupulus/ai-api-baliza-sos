"""Cliente HTTP común para las fuentes de datos.

Centraliza User-Agent, rate limiting básico y reintentos con backoff. Lo usan
todos los conectores de `sources/`.
"""

from __future__ import annotations

import logging
import time

import httpx

from common.config import settings
from common.errors import SourceError

_log = logging.getLogger(__name__)


class HttpClient:
    def __init__(
        self,
        *,
        min_interval: float = 1.0,   # s mínimos entre peticiones (cortesía)
        max_retries: int = 3,
        timeout: float = 30.0,
    ) -> None:
        self.min_interval = min_interval
        self.max_retries = max_retries
        self.timeout = timeout
        self._last_request = 0.0
        self._client = httpx.Client(
            timeout=timeout,
            headers={"User-Agent": settings.updater_user_agent},
            follow_redirects=True,
        )

    def _throttle(self) -> None:
        delta = time.monotonic() - self._last_request
        if delta < self.min_interval:
            time.sleep(self.min_interval - delta)
        self._last_request = time.monotonic()

    def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        ultimo_error: Exception | None = None
        for intento in range(1, self.max_retries + 1):
            self._throttle()
            try:
                resp = self._client.request(method, url, **kwargs)
                if resp.status_code in (429, 500, 502, 503, 504):
                    raise httpx.HTTPStatusError(
                        f"status {resp.status_code}", request=resp.request, response=resp
                    )
                resp.raise_for_status()
                return resp
            except httpx.HTTPError as exc:
                ultimo_error = exc
                espera = min(2 ** intento, 30)
                _log.warning("Fallo HTTP (%s), reintento %d/%d en %ds: %s",
                             url, intento, self.max_retries, espera, exc)
                time.sleep(espera)
        raise SourceError(f"No se pudo obtener {url}: {ultimo_error}")

    def get(self, url: str, **kwargs) -> httpx.Response:
        return self._request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> httpx.Response:
        return self._request("POST", url, **kwargs)

    def get_json(self, url: str, **kwargs):
        return self.get(url, **kwargs).json()

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *exc) -> None:
        self.close()
