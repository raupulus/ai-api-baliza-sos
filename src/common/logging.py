"""Configuración de logging por servicio. Sin dependencias pesadas."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from common.config import settings

_FORMAT = "%(asctime)s %(levelname)-7s %(name)s :: %(message)s"
_configured = False


def setup_logging(service: str, *, to_file: bool = True) -> logging.Logger:
    """Configura el logging raíz una vez y devuelve un logger para el servicio.

    Escribe a stdout (lo recoge journald bajo systemd) y, opcionalmente, a un
    fichero en LOG_DIR/<service>.log.
    """
    global _configured
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    if not _configured:
        handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
        if to_file:
            log_dir = Path(settings.log_dir)
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
                handlers.append(logging.FileHandler(log_dir / f"{service}.log", encoding="utf-8"))
            except OSError:
                # Si no se puede escribir el fichero (p. ej. permisos), seguir con stdout.
                pass
        logging.basicConfig(level=level, format=_FORMAT, handlers=handlers)
        _configured = True

    return logging.getLogger(service)
