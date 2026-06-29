from __future__ import annotations

import importlib.util
from pathlib import Path

from common.config import settings

ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _upper_names(mod) -> set[str]:
    return {n for n in dir(mod) if n.isupper() and not n.startswith("_")}


def test_settings_se_cargan():
    assert settings.provincia
    assert settings.embedding_dim > 0
    assert settings.resp_max_messages >= 1


def test_bbox_tuple_valido():
    a, b, c, d = settings.bbox_tuple
    assert a < c and b < d


def test_env_example_y_env_sincronizados():
    """env.py y env.example.py deben declarar las mismas variables."""
    env = ROOT / "env.py"
    example = ROOT / "env.example.py"
    assert example.exists()
    if env.exists():
        faltan = _upper_names(_load(example)) - _upper_names(_load(env))
        assert not faltan, f"Variables en example que faltan en env.py: {faltan}"


def test_llm_base_url():
    assert settings.llm_base_url.startswith("http")


def test_deteccion_token_inseguro():
    # El valor por defecto de la plantilla debe considerarse inseguro.
    assert settings.auth_token_es_inseguro == settings.api_auth_token.startswith("CAMBIA")
