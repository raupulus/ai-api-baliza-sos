"""Orquestación del pipeline de consulta: embed → recuperar → contexto →
generar → post-procesar → persistir memoria conversacional.
"""

from __future__ import annotations

import logging
import time

from fastapi.concurrency import run_in_threadpool

from api.concurrency import inference_semaphore
from api.llm_client import LLMClient
from api.memory import conversation_memory
from api.postprocess import formatear
from api.prompt import construir_mensajes
from api.rag import context as ctx_mod
from api.rag import retrieval
from api.schemas import ConsultaRequest, ConsultaResponse, FuenteOut
from common.config import settings

_log = logging.getLogger(__name__)


def _nombre_modelo() -> str:
    return settings.llm_model_path.rsplit("/", 1)[-1].removesuffix(".gguf")


def _procesar_sync(req: ConsultaRequest, llm: LLMClient) -> ConsultaResponse:
    """Pipeline completo con soporte multi-cliente y memoria conversacional."""
    inicio = time.monotonic()
    conv_id = req.id_conversacion or req.cliente
    cliente_id = req.cliente or conv_id or "desconocido"

    # 1. Manejo de reseteo explícito de conversación
    if req.reset_conversacion and conv_id:
        conversation_memory.resetear_conversacion(conv_id)
        if req.consulta.strip().lower() in ("/reset", "reset", "reiniciar", "nueva"):
            return ConsultaResponse(
                ok=True,
                mensajes=["Conversación reseteada. ¿En qué puedo ayudarte?"],
                categoria="general",
                confianza=1.0,
                modelo=_nombre_modelo(),
                tiempo_ms=int((time.monotonic() - inicio) * 1000),
            )

    # 2. Recuperar historial activo (hasta 20 turnos / TTL 1 hora)
    historial = conversation_memory.obtener_historial(conv_id) if conv_id else []

    # 3. Búsqueda vectorial en el RAG
    recuperados = retrieval.buscar(
        req.consulta,
        categoria=req.categoria_sugerida,
        provincia=settings.provincia if req.ubicacion else None,
    )

    # Si la consulta actual no recupera nada y hay historial previo, intentar con el tema reciente
    if not recuperados and historial:
        ultimos_usuarios = [m["content"] for m in historial if m["role"] == "user"]
        if ultimos_usuarios:
            consulta_ampliada = f"{ultimos_usuarios[-1]} {req.consulta}"
            recuperados = retrieval.buscar(
                consulta_ampliada,
                categoria=req.categoria_sugerida,
                provincia=settings.provincia if req.ubicacion else None,
            )

    # 4. Construcción del contexto y mensajes con triaje
    contexto = ctx_mod.construir_contexto(recuperados)
    mensajes = construir_mensajes(
        req.consulta,
        contexto.texto,
        suficiente=contexto.suficiente,
        historial=historial,
    )

    # 5. Generación de respuesta con el LLM
    texto_crudo = llm.chat(mensajes)

    # 6. Post-proceso a mensajes de <= 250 caracteres + aviso médico si procede
    formateada = formatear(texto_crudo, categoria=contexto.categoria)
    respuesta_completa = " ".join(formateada.mensajes)

    tiempo_ms = int((time.monotonic() - inicio) * 1000)

    # 7. Persistir turno en base de datos y compactar con IA si excede límite
    if conv_id:
        metadatos = {
            "tiempo_ms": tiempo_ms,
            "categoria": contexto.categoria.value if contexto.categoria else None,
            "confianza": contexto.confianza,
            "fuentes": [f.get("titulo") for f in contexto.fuentes],
            "aviso": formateada.aviso,
        }
        conversation_memory.guardar_turno(
            id_conversacion=conv_id,
            cliente_id=cliente_id,
            consulta_usuario=req.consulta,
            respuesta_asistente=respuesta_completa,
            metadatos=metadatos,
            llm=llm,
        )

    return ConsultaResponse(
        ok=True,
        mensajes=formateada.mensajes,
        categoria=contexto.categoria.value if contexto.categoria else None,
        confianza=contexto.confianza,
        fuentes=[FuenteOut(**f) for f in contexto.fuentes],
        aviso=formateada.aviso,
        modelo=_nombre_modelo(),
        tiempo_ms=tiempo_ms,
        truncado=formateada.truncado,
    )


async def responder(req: ConsultaRequest, *, llm: LLMClient | None = None) -> ConsultaResponse:
    """Procesa una consulta dentro del semáforo de inferencia."""
    llm = llm or LLMClient()
    async with inference_semaphore:
        return await run_in_threadpool(_procesar_sync, req, llm)
