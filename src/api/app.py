"""Servicio API del bot (FastAPI).

Expone:
  - GET  /health           estado de BD, llama-server y embeddings
  - POST /v1/consulta      pipeline RAG -> LLM -> respuesta JSON breve

Autenticación por token Bearer (Authorization). Pensado para 1 worker Uvicorn
con un semáforo que serializa las inferencias.
"""

from __future__ import annotations

import secrets

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse

from api.llm_client import LLMClient
from api.memory import conversation_memory
from api.pipeline import responder
from api.schemas import (
    ConsultaRequest,
    ConsultaResponse,
    ErrorResponse,
    HealthResponse,
    ResetConversacionRequest,
    ResetConversacionResponse,
)
from common.config import settings
from common.errors import BotError
from common.logging import setup_logging

_log = setup_logging("bot-api")

app = FastAPI(
    title="bot-ia-auxiliar · API",
    version="0.1.0",
    description="Asistente de emergencia offline (RAG + LLM local) para la provincia de "
    + settings.provincia,
)


def auth(authorization: str = Header(default="")) -> None:
    """Valida la cabecera Authorization: Bearer <token>.

    - Comparación en tiempo constante (evita timing attacks).
    - Si el token sigue siendo el de por defecto y no se permite explícitamente
      el modo inseguro, la API se NIEGA a atender (en vez de quedar expuesta).
    """
    if settings.auth_token_es_inseguro and not settings.api_allow_insecure_token:
        raise HTTPException(
            status_code=503,
            detail="Servicio mal configurado: define API_AUTH_TOKEN en env.py.",
        )
    esperado = f"Bearer {settings.api_auth_token}"
    if not secrets.compare_digest(authorization, esperado):
        raise HTTPException(status_code=401, detail="No autorizado.")


@app.exception_handler(BotError)
async def bot_error_handler(_request, exc: BotError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.http_status,
        content=ErrorResponse(error=exc.codigo, detalle=exc.detalle).model_dump(),
    )


@app.on_event("shutdown")
def _cerrar_recursos() -> None:
    """Cierre elegante del pool de PostgreSQL al parar/reiniciar el servicio."""
    from common.db import close_pool

    close_pool()


@app.on_event("startup")
def _avisar_token_inseguro() -> None:
    if settings.auth_token_es_inseguro:
        if settings.api_allow_insecure_token:
            _log.critical(
                "API_AUTH_TOKEN es el de por defecto y API_ALLOW_INSECURE_TOKEN=true: "
                "modo INSEGURO (solo para desarrollo)."
            )
        else:
            _log.critical(
                "API_AUTH_TOKEN sin configurar: la API rechazará todas las peticiones "
                "(503) hasta que definas un token en env.py."
            )


def _estado_componentes() -> tuple[bool, bool]:
    """Comprueba BD y LLM (operaciones bloqueantes). Se llama en threadpool."""
    from common.db import ping

    llm_ok = LLMClient().health()
    try:
        db_ok = ping()
    except Exception:  # pragma: no cover
        db_ok = False
    return db_ok, llm_ok


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    # Se ejecuta fuera del event loop para no bloquearlo si la BD/LLM tardan.
    db_ok, llm_ok = await run_in_threadpool(_estado_componentes)
    # Embeddings: no forzamos la carga aquí (cara); informamos como disponible
    # si la librería está importable.
    try:
        import fastembed  # noqa: F401

        emb_ok = True
    except Exception:
        emb_ok = False

    return HealthResponse(ok=db_ok and llm_ok, db=db_ok, llm=llm_ok, embeddings=emb_ok)


@app.post(
    "/v1/consulta",
    response_model=ConsultaResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    dependencies=[Depends(auth)],
)
async def consulta(req: ConsultaRequest) -> ConsultaResponse:
    _log.info("Consulta (%s): %s", req.cliente or "?", req.consulta[:80])
    return await responder(req)


@app.post(
    "/v1/conversacion/reset",
    response_model=ResetConversacionResponse,
    dependencies=[Depends(auth)],
)
async def reset_conversacion(req: ResetConversacionRequest) -> ResetConversacionResponse:
    exito = conversation_memory.resetear_conversacion(req.id_conversacion)
    msg = "Conversación reseteada correctamente." if exito else "La conversación no existía o ya estaba inactiva."
    return ResetConversacionResponse(
        ok=True,
        mensaje=msg,
        id_conversacion=req.id_conversacion,
    )


def main() -> None:  # pragma: no cover
    import uvicorn

    uvicorn.run(
        "api.app:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=1,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":  # pragma: no cover
    main()
