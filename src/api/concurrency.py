"""Control de concurrencia de inferencias.

En una RPi4 solo cabe una inferencia LLM a la vez (protege la RAM). Las
peticiones extra esperan en este semáforo hasta el límite de tiempo del cliente.
"""

from __future__ import annotations

import asyncio

from common.config import settings

inference_semaphore = asyncio.Semaphore(
    max(1, settings.api_max_concurrent_inferences)
)
