"""Orquestación del pipeline de consulta: embed → recuperar → contexto →
generar → post-procesar. Es el corazón del servicio API.
"""

from __future__ import annotations

import logging
import time

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


async def responder(req: ConsultaRequest, *, llm: LLMClient | None = None) -> ConsultaResponse:
    """Procesa una consulta completa y devuelve la respuesta formateada."""
    inicio = time.monotonic()
    llm = llm or LLMClient()

    # 1-2. Recuperación (incluye el embedding de la consulta).
    provincia = settings.provincia
    recuperados = retrieval.buscar(
        req.consulta,
        categoria=req.categoria_sugerida,
        provincia=provincia if req.ubicacion else None,
    )

    # 3. Construcción del contexto.
    contexto = ctx_mod.construir_contexto(recuperados)

    # 4. Prompt.
    prompt = construir_prompt(
        req.consulta, contexto.texto, suficiente=contexto.suficiente
    )

    # 5. Generación, serializada por el semáforo (una inferencia a la vez).
    async with inference_semaphore:
        texto_crudo = await llm.generate_async(prompt)

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
