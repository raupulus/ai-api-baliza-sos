#!/usr/bin/env python3
"""Script de pruebas de integración E2E automatizado para el Asistente de Emergencias.

Verifica la disponibilidad y el contrato de la API HTTP REST en producción o entorno local:
1. Endpoint /health (servicios saludables).
2. Seguridad: 401 si no hay token o es erróneo.
3. Consulta médica/montaña: respuesta JSON, fuentes, confianza y paquetes <= 250 caracteres.
4. Memoria conversacional multi-turno: coherencia entre turnos correlados.
5. Reseteo de conversación: endpoint /v1/conversacion/reset.

Uso:
    python3 scripts/test_e2e.py --url http://172.18.1.121:8870 --token 4d7a1d7affbeb459814d1fa220b2a70b
    python3 scripts/test_e2e.py --url http://localhost:8870
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Test E2E de integración de la API del bot.")
    parser.add_argument(
        "--url",
        type=str,
        default="http://172.18.1.121:8870",
        help="URL base de la API (ej. http://172.18.1.121:8870 o http://localhost:8870).",
    )
    parser.add_argument(
        "--token",
        type=str,
        default=os.environ.get("API_AUTH_TOKEN", "4d7a1d7affbeb459814d1fa220b2a70b"),
        help="Token Bearer de autenticación.",
    )
    return parser.parse_args()


def _request(
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    data: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any] | str]:
    headers = headers or {}
    encoded_data = json.dumps(data).encode("utf-8") if data is not None else None
    if data is not None:
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            body = resp.read().decode("utf-8")
            try:
                return resp.status, json.loads(body)
            except Exception:
                return resp.status, body
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8")
        try:
            return err.code, json.loads(body)
        except Exception:
            return err.code, body


def main() -> int:
    args = parse_args()
    base_url = args.url.rstrip("/")
    token = args.token

    print(f"\n🚀 Iniciando suite de pruebas E2E contra: {base_url}")
    print(f"🔑 Token configurado: {token[:6]}...{token[-4:] if len(token) > 10 else ''}\n")

    exitos = 0
    total = 6
    id_test_conv = f"e2e-test-{int(time.time())}"

    # 1. Healthcheck
    try:
        status, body = _request("GET", f"{base_url}/health")
        if status == 200 and isinstance(body, dict) and body.get("ok") is True:
            print("  ✅ 1. Healthcheck (/health) -> OK (200)")
            exitos += 1
        else:
            print(f"  ❌ 1. Healthcheck falló: {status} -> {body}")
    except Exception as exc:
        print(f"  ❌ 1. Healthcheck no pudo conectar: {exc}")

    # 2. Auth: 401 si falta token
    status, _ = _request("POST", f"{base_url}/v1/consulta", data={"consulta": "hola"})
    if status == 401:
        print("  ✅ 2. Seguridad: Rechazo 401 sin Bearer Token -> OK")
        exitos += 1
    else:
        print(f"  ❌ 2. Falló control de seguridad: devolvió {status} en vez de 401")

    # 3. Auth: 401 si token erróneo
    status, _ = _request(
        "POST",
        f"{base_url}/v1/consulta",
        headers={"Authorization": "Bearer token-invalido-1234"},
        data={"consulta": "hola"},
    )
    if status == 401:
        print("  ✅ 3. Seguridad: Rechazo 401 con Token erróneo -> OK")
        exitos += 1
    else:
        print(f"  ❌ 3. Falló control de token inválido: devolvió {status} en vez de 401")

    # 4. Consulta Turno 1: Emergencia médica y límites RF
    auth_headers = {"Authorization": f"Bearer {token}"}
    t0 = time.time()
    payload_t1 = {
        "consulta": "Me he caido en una ruta de Grazalema y no puedo apoyar el pie, ¿qué hago?",
        "id_conversacion": id_test_conv,
        "cliente": "e2e-runner",
    }
    status, body_t1 = _request("POST", f"{base_url}/v1/consulta", headers=auth_headers, data=payload_t1)
    duracion_t1 = time.time() - t0

    if status == 200 and isinstance(body_t1, dict) and body_t1.get("ok") is True:
        mensajes = body_t1.get("mensajes", [])
        largos_bytes = [len(m.encode("utf-8")) for m in mensajes]
        todos_validos = all(l <= 200 for l in largos_bytes) and 1 <= len(mensajes) <= 3
        if todos_validos:
            print(
                f"  ✅ 4. Consulta Turno 1 -> OK ({duracion_t1:.1f}s) | "
                f"{len(mensajes)} msgs, max_bytes={max(largos_bytes)} UTF-8 (límite 200)"
            )
            exitos += 1
        else:
            print(f"  ❌ 4. Consulta Turno 1 superó límites RF: {largos_bytes} bytes UTF-8 (límite 200)")
    else:
        print(f"  ❌ 4. Consulta Turno 1 falló con HTTP {status}: {body_t1}")

    # 5. Consulta Turno 2: Seguimiento con memoria multi-turno
    t0 = time.time()
    payload_t2 = {
        "consulta": "Me duele muchísimo el tobillo, ¿debo quitarme la bota?",
        "id_conversacion": id_test_conv,
        "cliente": "e2e-runner",
    }
    status, body_t2 = _request("POST", f"{base_url}/v1/consulta", headers=auth_headers, data=payload_t2)
    duracion_t2 = time.time() - t0

    if status == 200 and isinstance(body_t2, dict) and body_t2.get("ok") is True:
        mensajes_t2 = body_t2.get("mensajes", [])
        largos_bytes_t2 = [len(m.encode("utf-8")) for m in mensajes_t2]
        todos_validos_t2 = all(l <= 200 for l in largos_bytes_t2) and 1 <= len(mensajes_t2) <= 3
        if todos_validos_t2:
            print(
                f"  ✅ 5. Consulta Turno 2 (Memoria Multi-Turno) -> OK ({duracion_t2:.1f}s) | "
                f"{len(mensajes_t2)} msgs, max_bytes={max(largos_bytes_t2)} UTF-8 (límite 200)"
            )
            exitos += 1
        else:
            print(f"  ❌ 5. Turno 2 superó límites RF: {largos_bytes_t2} bytes UTF-8 (límite 200)")
    else:
        print(f"  ❌ 5. Consulta Turno 2 falló con HTTP {status}: {body_t2}")

    # 6. Reseteo de conversación
    status, body_reset = _request(
        "POST",
        f"{base_url}/v1/conversacion/reset",
        headers=auth_headers,
        data={"id_conversacion": id_test_conv},
    )
    if status == 200 and isinstance(body_reset, dict) and body_reset.get("ok") is True:
        print("  ✅ 6. Reseteo de Conversación (/v1/conversacion/reset) -> OK (200)")
        exitos += 1
    else:
        print(f"  ❌ 6. Reseteo falló con HTTP {status}: {body_reset}")

    print(f"\n🏁 Resultado: {exitos}/{total} pruebas superadas.")
    return 0 if exitos == total else 1


if __name__ == "__main__":
    sys.exit(main())
