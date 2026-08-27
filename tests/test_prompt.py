from __future__ import annotations

from api.prompt import construir_mensajes, construir_prompt
from common.config import settings


def test_prompt_incluye_reglas_y_provincia():
    p = construir_prompt("¿dónde hay agua?", "- (OSM) Fuente en la plaza.", suficiente=True)
    assert settings.provincia in p
    assert "español" in p.lower()
    assert "[CONSULTA]" in p and "[CONTEXTO]" in p
    assert "agua" in p


def test_prompt_sin_contexto_avisa():
    p = construir_prompt("consulta rara", "", suficiente=False)
    assert "112" in p
    assert "sin datos" in p.lower() or "vacío" in p or "vacio" in p.lower()


def test_mensajes_estructura_chat():
    msgs = construir_mensajes("¿dónde hay agua?", "- (OSM) Fuente.", suficiente=True)
    assert [m["role"] for m in msgs] == ["system", "user"]
    assert settings.provincia in msgs[0]["content"]
    assert "agua" in msgs[1]["content"]
    assert "CONTEXTO" in msgs[1]["content"]


def test_mensajes_sin_contexto_avisa_112():
    msgs = construir_mensajes("rara", "", suficiente=False)
    assert "112" in msgs[1]["content"]
