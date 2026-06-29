#!/usr/bin/env python3
"""Exporta la configuración de env.py como sentencias `export KEY=VALUE`.

Permite que los scripts de shell y las unidades systemd usen la misma fuente de
verdad (env.py) sin duplicar valores.

Uso en shell:
    eval "$(python3 scripts/env_export.py)"

Uso para systemd (genera un EnvironmentFile):
    python3 scripts/env_export.py --no-export > deploy/systemd/bot.env
"""

from __future__ import annotations

import argparse
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from common.config import settings  # noqa: E402

# Mapea atributos de Settings -> nombres de variable de entorno (en mayúsculas).
_KEYS = {
    "PROVINCIA": settings.provincia,
    "PROVINCIA_SLUG": settings.provincia_slug,
    "PAIS": settings.pais,
    "PAIS_CODIGO_ISO": settings.pais_codigo_iso,
    "BBOX": settings.bbox,
    "PROVINCIA_CODIGO_INE": settings.provincia_codigo_ine,
    "IDIOMA": settings.idioma,
    "LLM_SERVER_HOST": settings.llm_server_host,
    "LLM_SERVER_PORT": settings.llm_server_port,
    "LLM_MODEL_PATH": settings.llm_model_path,
    "LLM_THREADS": settings.llm_threads,
    "LLM_CONTEXT_SIZE": settings.llm_context_size,
    "LLM_MAX_TOKENS": settings.llm_max_tokens,
    "LLM_TEMPERATURE": settings.llm_temperature,
    "LLM_TIMEOUT_SECONDS": settings.llm_timeout_seconds,
    "EMBEDDING_MODEL": settings.embedding_model,
    "EMBEDDING_DIM": settings.embedding_dim,
    "DB_HOST": settings.db_host,
    "DB_PORT": settings.db_port,
    "DB_NAME": settings.db_name,
    "DB_USER": settings.db_user,
    "DB_PASSWORD": settings.db_password,
    "DB_DATA_DIR": settings.db_data_dir,
    "API_HOST": settings.api_host,
    "API_PORT": settings.api_port,
    "LOG_LEVEL": settings.log_level,
    "LOG_DIR": settings.log_dir,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-export",
        action="store_true",
        help="Genera KEY=VALUE (formato EnvironmentFile de systemd) en vez de export.",
    )
    args = parser.parse_args()

    for key, value in _KEYS.items():
        val = shlex.quote(str(value))
        if args.no_export:
            print(f"{key}={value}")
        else:
            print(f"export {key}={val}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
