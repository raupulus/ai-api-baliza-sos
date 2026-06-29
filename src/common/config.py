"""
Carga única de configuración del proyecto.

Importa `env.py` (config real, no trackeada) desde la raíz del repositorio y
expone un objeto `settings` tipado e inmutable. Si `env.py` no existe (p. ej. en
CI o en un clon recién hecho), cae a `env.example.py` con un aviso, de modo que
el código y las pruebas puedan importarse sin fallar.

Regla del proyecto: ningún otro módulo lee `os.environ` ni importa `env.py`
directamente; todo pasa por aquí (ver AGENTS.md).
"""

from __future__ import annotations

import importlib.util
import logging
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

_log = logging.getLogger(__name__)


def _repo_root() -> Path:
    """Localiza la raíz del repo subiendo hasta encontrar env.py / env.example.py."""
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "env.py").exists() or (parent / "env.example.py").exists():
            return parent
    # Fallback: dos niveles por encima de src/common/.
    return here.parents[2]


def _load_env_module() -> ModuleType:
    root = _repo_root()
    env_path = root / "env.py"
    if not env_path.exists():
        example = root / "env.example.py"
        if example.exists():
            _log.warning("env.py no encontrado; usando env.example.py (valores por defecto).")
            env_path = example
        else:  # pragma: no cover - situación anómala
            raise FileNotFoundError("No se encontró env.py ni env.example.py en la raíz del repo.")
    spec = importlib.util.spec_from_file_location("project_env", env_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class Settings:
    """Configuración tipada del proyecto (instantánea inmutable de env.py)."""

    # --- Contexto geográfico ---
    provincia: str
    provincia_slug: str
    pais: str
    pais_codigo_iso: str
    bbox: str
    provincia_codigo_ine: str
    idioma: str

    # --- LLM ---
    llm_server_host: str
    llm_server_port: int
    llm_model_path: str
    llm_threads: int
    llm_context_size: int
    llm_max_tokens: int
    llm_temperature: float
    llm_timeout_seconds: int

    # --- Embeddings ---
    embedding_model: str
    embedding_dim: int
    embedding_query_prefix: str
    embedding_passage_prefix: str

    # --- RAG ---
    rag_top_k: int
    rag_min_score: float
    rag_max_context_chars: int

    # --- Base de datos ---
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    db_data_dir: str

    # --- API ---
    api_host: str
    api_port: int
    api_auth_token: str
    api_max_concurrent_inferences: int

    # --- Formato de respuesta ---
    resp_max_chars_per_msg: int
    resp_max_messages: int
    resp_disclaimer_medico: str

    # --- Actualizador ---
    updater_staging_dir: str
    updater_user_agent: str
    aemet_api_key: str

    # --- Logging ---
    log_level: str
    log_dir: str

    @property
    def bbox_tuple(self) -> tuple[float, float, float, float]:
        """BBOX como (min_lon, min_lat, max_lon, max_lat)."""
        parts = [float(x) for x in self.bbox.split(",")]
        if len(parts) != 4:
            raise ValueError(f"BBOX inválido: {self.bbox!r} (se esperan 4 valores).")
        return parts[0], parts[1], parts[2], parts[3]

    @property
    def llm_base_url(self) -> str:
        return f"http://{self.llm_server_host}:{self.llm_server_port}"

    @property
    def db_dsn(self) -> str:
        return (
            f"host={self.db_host} port={self.db_port} dbname={self.db_name} "
            f"user={self.db_user} password={self.db_password}"
        )


def _build_settings() -> Settings:
    env = _load_env_module()

    def get(name: str):
        try:
            return getattr(env, name)
        except AttributeError as exc:  # pragma: no cover
            raise AttributeError(
                f"Falta la variable {name!r} en env.py. Añádela (y a env.example.py)."
            ) from exc

    settings = Settings(
        provincia=get("PROVINCIA"),
        provincia_slug=get("PROVINCIA_SLUG"),
        pais=get("PAIS"),
        pais_codigo_iso=get("PAIS_CODIGO_ISO"),
        bbox=get("BBOX"),
        provincia_codigo_ine=get("PROVINCIA_CODIGO_INE"),
        idioma=get("IDIOMA"),
        llm_server_host=get("LLM_SERVER_HOST"),
        llm_server_port=get("LLM_SERVER_PORT"),
        llm_model_path=get("LLM_MODEL_PATH"),
        llm_threads=get("LLM_THREADS"),
        llm_context_size=get("LLM_CONTEXT_SIZE"),
        llm_max_tokens=get("LLM_MAX_TOKENS"),
        llm_temperature=get("LLM_TEMPERATURE"),
        llm_timeout_seconds=get("LLM_TIMEOUT_SECONDS"),
        embedding_model=get("EMBEDDING_MODEL"),
        embedding_dim=get("EMBEDDING_DIM"),
        embedding_query_prefix=get("EMBEDDING_QUERY_PREFIX"),
        embedding_passage_prefix=get("EMBEDDING_PASSAGE_PREFIX"),
        rag_top_k=get("RAG_TOP_K"),
        rag_min_score=get("RAG_MIN_SCORE"),
        rag_max_context_chars=get("RAG_MAX_CONTEXT_CHARS"),
        db_host=get("DB_HOST"),
        db_port=get("DB_PORT"),
        db_name=get("DB_NAME"),
        db_user=get("DB_USER"),
        db_password=get("DB_PASSWORD"),
        db_data_dir=get("DB_DATA_DIR"),
        api_host=get("API_HOST"),
        api_port=get("API_PORT"),
        api_auth_token=get("API_AUTH_TOKEN"),
        api_max_concurrent_inferences=get("API_MAX_CONCURRENT_INFERENCES"),
        resp_max_chars_per_msg=get("RESP_MAX_CHARS_PER_MSG"),
        resp_max_messages=get("RESP_MAX_MESSAGES"),
        resp_disclaimer_medico=get("RESP_DISCLAIMER_MEDICO"),
        updater_staging_dir=get("UPDATER_STAGING_DIR"),
        updater_user_agent=get("UPDATER_USER_AGENT"),
        aemet_api_key=get("AEMET_API_KEY"),
        log_level=get("LOG_LEVEL"),
        log_dir=get("LOG_DIR"),
    )
    _validate(settings)
    return settings


def _validate(s: Settings) -> None:
    """Validaciones tempranas; fallan al arranque con mensaje claro."""
    if s.embedding_dim <= 0:
        raise ValueError("EMBEDDING_DIM debe ser > 0.")
    if s.rag_top_k <= 0:
        raise ValueError("RAG_TOP_K debe ser > 0.")
    if not 0 <= s.rag_min_score <= 1:
        raise ValueError("RAG_MIN_SCORE debe estar en [0, 1].")
    if s.resp_max_messages <= 0 or s.resp_max_chars_per_msg <= 0:
        raise ValueError("RESP_MAX_MESSAGES y RESP_MAX_CHARS_PER_MSG deben ser > 0.")
    # Validar BBOX (lanza si está mal formado).
    _ = s.bbox_tuple


# Singleton de configuración del proceso.
settings: Settings = _build_settings()


def reload_settings() -> Settings:
    """Recarga la configuración (útil en pruebas). Devuelve la nueva instancia."""
    global settings
    settings = _build_settings()
    return settings
