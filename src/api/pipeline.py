"""Orquestación del pipeline de consulta: embed → recuperar → contexto →
generar → post-procesar. Es el corazón del servicio API.

Concurrencia (importante en RPi4 4GB):
  - Todo el trabajo local pesado (embedding ONNX, consulta a BD síncrona,
    generación) se ejecuta en un hilo del threadpool con `run_in_threadpool`,
    de modo que el event loop de FastAPI NO se bloquea (sigue atendiendo
    /health y encolando peticiones).
  - Ese bloque va dentro del semáforo de inferencia, así que el embedding y la
    generación quedan SERIALIZADOS: nunca corren dos a la vez y no se dispara la
    RAM. (Corrige los hallazgos 1 y 2 de la auditoría docs/planning/checks.)
"""

from __future__ import annotations

import logging
import time

from fastapi.concurrency import run_in_threadpool

from api.concurrency import inference_semaphore
from api.llm_client import LLMClient
from api.postprocess import formatear
from api.prompt import construir_prompt
from api.rag import context as ctx_mod
from api.rag import retrieval
from api.schemas import ConsultaRequest, ConsultaResponse, FuenteOut
from common.config import settings

_log = logging.getLogger(__name__)


def _nombre_modelo() -> str:
    # Nombre legible del modelo a partir de la ruta del GGUF.
    return settings.llm_model_path.rsplit("/", 1)[-1].removesuffix(".gguf")


def _procesar_sync(req: ConsultaRequest, llm: LLMClient) -> ConsultaResponse:
    """Pipeline completo y SÍNCRONO. Se ejecuta en un hilo del threadpool,
    bajo el semáforo de inferencia (una sola ejecución pesada a la vez)."""
    inicio = time.monotonic()

    # 1-2. Recuperación (incluye el embedding de la consulta, CPU-bound).
    recuperados = retrieval.buscar(
        req.consulta,
        categoria=req.categoria_sugerida,
        provincia=settings.provincia if req.ubicacion else None,
    )

    # 3. Construcción del contexto.
    contexto = ctx_mod.construir_contexto(recuperados)

    # 4. Prompt.
    prompt = construir_prompt(req.consulta, contexto.texto, suficiente=contexto.suficiente)

    # 5. Generación (llamada bloqueante a llama-server; este hilo espera).
    texto_crudo = llm.generate(prompt)

    # 6. Post-proceso a 1–3 mensajes de <=250 caracteres + aviso si procede.
    formateada = formatear(texto_crudo, categoria=contexto.categoria)

    tiempo_ms = int((time.monotonic() - inicio) * 1000)
    return ConsultaResponse(
        ok=True,
        mensajes=formateada.mensajes,
        categoria=contexto.categoria.value if contexto.categoria else None,
        confianza=contexto.confianza,
        fuentes=[FuenteOut(**f) for f in contexto.fuentes],
        modelo=_nombre_modelo(),
        tiempo_ms=tiempo_ms,
        truncado=formateada.truncado,
    )


async def responder(req: ConsultaRequest, *, llm: LLMClient | None = None) -> ConsultaResponse:
    """Procesa una consulta. Serializa el trabajo pesado y libera el event loop."""
    llm = llm or LLMClient()
    # El semáforo cubre TODO el trabajo local pesado (embedding + BD + LLM).
    async with inference_semaphore:
        return await run_in_threadpool(_procesar_sync, req, llm)
