"""Servicio API del bot (FastAPI).

Expone:
  - GET  /health           estado de BD, llama-server y embeddings
  - POST /v1/consulta      pipeline RAG -> LLM -> respuesta JSON breve

Autenticación por token Bearer (Authorization). Pensado para 1 worker Uvicorn
con un semáforo que serializa las inferencias.
"""

from __future__ import annotations

import logging

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse

from api.llm_client import LLMClient
from api.pipeline import responder
from api.schemas import (
    ConsultaRequest,
    ConsultaResponse,
    ErrorResponse,
    HealthResponse,
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
    """Valida la cabecera Authorization: Bearer <token>."""
    esperado = f"Bearer {settings.api_auth_token}"
    if not settings.api_auth_token or settings.api_auth_token.startswith("CAMBIA"):
        _log.warning("API_AUTH_TOKEN sin configurar; revisa env.py antes de producción.")
    if authorization != esperado:
        raise HTTPException(status_code=401, detail="No autorizado.")


@app.exception_handler(BotError)
async def bot_error_handler(_request, exc: BotError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.http_status,
        content=ErrorResponse(error=exc.codigo, detalle=exc.detalle).model_dump(),
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    from common.db import ping

    llm_ok = LLMClient().health()
    db_ok = False
    try:
        db_ok = ping()
    except Exception:  # pragma: no cover
        db_ok = False
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
    responses={4: {"model": ErrorResponse}, 5: {"model": ErrorResponse}},
    dependencies=[Depends(auth)],
)
async def consulta(req: ConsultaRequest) -> ConsultaResponse:
    _log.info("Consulta (%s): %s", req.cliente or "?", req.consulta[:80])
    return await responder(req)


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
