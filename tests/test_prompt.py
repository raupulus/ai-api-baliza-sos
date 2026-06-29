from __future__ import annotations

from api.prompt import construir_prompt
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
    assert "vacío" in p or "vacio" in p.lower()
