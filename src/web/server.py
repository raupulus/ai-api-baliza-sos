"""Servidor web de pruebas para el Bot de Emergencias.

Expone una interfaz de chat interactiva en el puerto configurado (por defecto 8443)
y actúa como proxy hacia el backend FastAPI (puerto 8870) para evitar bloqueos CORS
en navegadores locales.
"""

from __future__ import annotations

import asyncio
import os
import shutil
import time
from pathlib import Path
from typing import Any

import httpx
import uvicorn
from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse

API_BASE_URL = os.environ.get("API_BASE_URL", "http://api:8870").rstrip("/")
API_AUTH_TOKEN = os.environ.get("API_AUTH_TOKEN", "")
WEB_PORT = int(os.environ.get("WEB_PORT", "8443"))
WEB_HOST = os.environ.get("WEB_HOST", "0.0.0.0")

INDEX_FILE = Path(__file__).resolve().parent / "index.html"

app = FastAPI(title="Bot Emergencias Cádiz - Web UI")

_last_cpu_times: tuple[float, float] | None = None


def _get_cpu_usage() -> float:
    global _last_cpu_times
    try:
        stat_path = Path("/proc/stat")
        if stat_path.exists():
            with open(stat_path, "r", encoding="utf-8") as fp:
                line = fp.readline()
            parts = [float(x) for x in line.strip().split()[1:8]]
            idle = parts[3] + (parts[4] if len(parts) > 4 else 0)
            total = sum(parts)
            if _last_cpu_times is not None:
                last_idle, last_total = _last_cpu_times
                diff_idle = idle - last_idle
                diff_total = total - last_total
                _last_cpu_times = (idle, total)
                if diff_total > 0:
                    return max(0.0, min(100.0, round((1.0 - (diff_idle / diff_total)) * 100, 1)))
            _last_cpu_times = (idle, total)
    except Exception:
        pass

    try:
        load1, _, _ = os.getloadavg()
        cpu_count = os.cpu_count() or 1
        return round(min(100.0, (load1 / cpu_count) * 100), 1)
    except Exception:
        return 0.0


def _get_temp() -> float | None:
    for tz in (
        "/sys/class/thermal/thermal_zone0/temp",
        "/sys/devices/virtual/thermal/thermal_zone0/temp",
    ):
        p = Path(tz)
        if p.exists():
            try:
                val = float(p.read_text().strip())
                return round(val / 1000.0 if val > 100 else val, 1)
            except Exception:
                pass
    return None


def _get_mem_info() -> dict[str, Any]:
    try:
        mem_path = Path("/proc/meminfo")
        if mem_path.exists():
            mem: dict[str, float] = {}
            with open(mem_path, "r", encoding="utf-8") as fp:
                for line in fp:
                    parts = line.split(":")
                    if len(parts) == 2:
                        k = parts[0].strip()
                        v = parts[1].strip().split()[0]
                        mem[k] = float(v)
            total_kb = mem.get("MemTotal", 0)
            avail_kb = mem.get("MemAvailable", mem.get("MemFree", 0))
            used_kb = total_kb - avail_kb
            if total_kb > 0:
                pct = round((used_kb / total_kb) * 100, 1)
                return {
                    "total_mb": round(total_kb / 1024, 0),
                    "used_mb": round(used_kb / 1024, 0),
                    "percent": pct,
                }
    except Exception:
        pass
    return {"total_mb": 0, "used_mb": 0, "percent": 0.0}


def get_system_telemetry() -> dict[str, Any]:
    cpu_pct = _get_cpu_usage()
    temp_c = _get_temp()
    mem = _get_mem_info()

    try:
        du = shutil.disk_usage("/")
        disk_total_gb = round(du.total / (1024**3), 1)
        disk_used_gb = round(du.used / (1024**3), 1)
        disk_pct = round((du.used / du.total) * 100, 1) if du.total > 0 else 0.0
    except Exception:
        disk_total_gb = 0.0
        disk_used_gb = 0.0
        disk_pct = 0.0

    return {
        "timestamp": int(time.time()),
        "cpu_percent": cpu_pct,
        "temp_c": temp_c,
        "ram_total_mb": mem["total_mb"],
        "ram_used_mb": mem["used_mb"],
        "ram_percent": mem["percent"],
        "disk_total_gb": disk_total_gb,
        "disk_used_gb": disk_used_gb,
        "disk_percent": disk_pct,
    }


@app.get("/api/telemetry")
async def api_telemetry() -> dict[str, Any]:
    """Devuelve una captura instantánea de la telemetría del sistema."""
    return get_system_telemetry()


@app.websocket("/ws/telemetry")
async def ws_telemetry(websocket: WebSocket) -> None:
    """Canal WebSocket para streaming en tiempo real de telemetría del hardware."""
    await websocket.accept()
    try:
        while True:
            data = get_system_telemetry()
            await websocket.send_json(data)
            await asyncio.sleep(2.0)
    except (WebSocketDisconnect, Exception):
        pass


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
