"""Pruebas de la política de reintentos del cliente LLM (hallazgo 3a auditoría).

Reintenta solo errores de conexión; nunca timeouts.
"""

from __future__ import annotations

import httpx
import pytest

from api.llm_client import LLMClient
from common.errors import LLMTimeoutError, LLMUnavailableError


class _FakeClient:
    """Sustituto de httpx.Client que ejecuta un comportamiento inyectado."""

    contador = {"n": 0}
    comportamiento = None  # callable() que devuelve una respuesta o lanza

    def __init__(self, *a, **k):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def post(self, *a, **k):
        type(self).contador["n"] += 1
        return type(self).comportamiento()


class _Resp:
    def raise_for_status(self):
        pass

    def json(self):
        return {"content": "hola "}


@pytest.fixture()
def fake_httpx(monkeypatch):
    _FakeClient.contador = {"n": 0}
    monkeypatch.setattr(httpx, "Client", _FakeClient)
    return _FakeClient


def test_timeout_no_se_reintenta(fake_httpx):
    fake_httpx.comportamiento = staticmethod(
        lambda: (_ for _ in ()).throw(httpx.TimeoutException("t"))
    )
    c = LLMClient(connect_retries=2, connect_backoff=0)
    with pytest.raises(LLMTimeoutError):
        c.generate("x")
    assert fake_httpx.contador["n"] == 1


def test_connect_error_se_reintenta(fake_httpx):
    fake_httpx.comportamiento = staticmethod(
        lambda: (_ for _ in ()).throw(httpx.ConnectError("c"))
    )
    c = LLMClient(connect_retries=2, connect_backoff=0)
    with pytest.raises(LLMUnavailableError):
        c.generate("x")
    assert fake_httpx.contador["n"] == 3  # 1 + 2 reintentos


def test_respuesta_ok(fake_httpx):
    fake_httpx.comportamiento = staticmethod(_Resp)
    c = LLMClient(connect_retries=2, connect_backoff=0)
    assert c.generate("x") == "hola"
