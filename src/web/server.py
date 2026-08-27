"""Servidor web de pruebas para el Bot de Emergencias.

Expone una interfaz de chat interactiva en el puerto configurado (por defecto 8443)
y actúa como proxy hacia el backend FastAPI (puerto 8870) para evitar bloqueos CORS
en navegadores locales.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import httpx
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse, HTMLResponse

API_BASE_URL = os.environ.get("API_BASE_URL", "http://api:8870").rstrip("/")
API_AUTH_TOKEN = os.environ.get("API_AUTH_TOKEN", "")
WEB_PORT = int(os.environ.get("WEB_PORT", "8443"))
WEB_HOST = os.environ.get("WEB_HOST", "0.0.0.0")

INDEX_FILE = Path(__file__).resolve().parent / "index.html"

app = FastAPI(title="Bot Emergencias Cádiz - Web UI")


@app.get("/", response_class=HTMLResponse)
async def index() -> FileResponse:
    """Entrega la interfaz de chat en HTML."""
    if not INDEX_FILE.exists():
        return Response("index.html no encontrado", status_code=404)
    return FileResponse(INDEX_FILE)


@app.get("/api/auth/token")
async def get_default_token() -> dict[str, str]:
    """Devuelve el token configurado en el servidor para auto-completar el frontend."""
    return {"token": API_AUTH_TOKEN}


@app.get("/api/health")
async def proxy_health() -> Response:
    """Proxy hacia el healthcheck del backend API."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{API_BASE_URL}/health")
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                media_type="application/json",
            )
    except Exception as exc:
        return Response(
            content=f'{{"ok": false, "error": "{str(exc)}"}}',
            status_code=502,
            media_type="application/json",
        )


@app.post("/api/v1/consulta")
async def proxy_consulta(request: Request) -> Response:
    """Proxy hacia el endpoint de inferencia /v1/consulta retransmitiendo la autenticación del cliente."""
    body = await request.body()
    headers: dict[str, str] = {"Content-Type": "application/json"}

    auth = request.headers.get("Authorization")
    if auth:
        headers["Authorization"] = auth

    try:
        # Timeout amplio (hasta 280s) para soportar inferencia en RPi
        async with httpx.AsyncClient(timeout=300.0) as client:
            resp = await client.post(
                f"{API_BASE_URL}/v1/consulta",
                content=body,
                headers=headers,
            )
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                media_type=resp.headers.get("content-type", "application/json"),
            )
    except Exception as exc:
        return Response(
            content=f'{{"detail": "Error comunicando con el backend API: {str(exc)}"}}',
            status_code=502,
            media_type="application/json",
        )


@app.post("/api/v1/conversacion/reset")
async def proxy_reset(request: Request) -> Response:
    """Proxy hacia el endpoint de reseteo de conversación."""
    body = await request.body()
    headers: dict[str, str] = {"Content-Type": "application/json"}

    auth = request.headers.get("Authorization")
    if auth:
        headers["Authorization"] = auth

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{API_BASE_URL}/v1/conversacion/reset",
                content=body,
                headers=headers,
            )
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                media_type="application/json",
            )
    except Exception as exc:
        return Response(
            content=f'{{"detail": "Error reseteando conversación: {str(exc)}"}}',
            status_code=502,
            media_type="application/json",
        )


def main() -> None:
    uvicorn.run(
        "web.server:app",
        host=WEB_HOST,
        port=WEB_PORT,
        workers=1,
        log_level="info",
    )


if __name__ == "__main__":
    main()
