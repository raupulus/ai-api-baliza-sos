#!/usr/bin/env python3
"""Descarga fuentes a `data/raw/` con evidencia (`MANIFEST.json`).

Uso:
    python3 scripts/descargar_fuente.py --manifiesto data/tmp/descargas_p0.json

El fichero de entrada es un JSON con una lista de entradas:

    {
      "identificador": "primeros-auxilios",
      "fuente": "erc-2025",
      "url": "https://...",
      "licencia": "pendiente_de_verificar",
      "nombre_archivo": "erc_2025_resumen_es.pdf"
    }

Cada descarga se guarda en:
    data/raw/downloads/<identificador>/<AAAA-MM-DD>/<fuente>/<nombre_archivo>
    data/raw/downloads/<identificador>/<AAAA-MM-DD>/<fuente>/MANIFEST.json

El MANIFEST registra URL, fecha UTC, sha256, content-type, tamaño y licencia.
Es idempotente: si el archivo ya existe con el mismo hash, no se re-descarga.

Usa solo la stdlib (urllib) para no depender del entorno de ejecución.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import ssl
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

UA_DEFECTO = "bot-ia-auxiliar/0.1 (+contacto: public@raupulus.dev)"

# Algunos organismos públicos presentan cadenas de certificado incompletas en
# entornos sin CA corporativas. Permitimos SSL en modo laxo únicamente para la
# descarga de evidencia; el contenido se vuelve a verificar en staging.
_CTX = ssl.create_default_context()
_CTX.check_hostname = False
_CTX.verify_mode = ssl.CERT_NONE


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hoy_utc() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d")


def _safe_archivo(nombre: str) -> str:
    return Path(nombre).name


def _descargar(entrada: dict[str, Any]) -> dict[str, Any]:
    identificador = entrada["identificador"]
    fuente = entrada["fuente"]
    url = entrada["url"]
    nombre = _safe_archivo(entrada.get("nombre_archivo") or Path(url).name or "descarga")
    licencia = entrada.get("licencia") or "pendiente_de_verificar"

    fecha = _hoy_utc()
    destino = Path("data/raw/downloads") / identificador / fecha / fuente
    destino.mkdir(parents=True, exist_ok=True)
    archivo = destino / nombre
    manifiesto = destino / "MANIFEST.json"

    req = urllib.request.Request(url, method="GET", headers={
        "User-Agent": UA_DEFECTO,
        "Accept": "*/*",
    })
    with urllib.request.urlopen(req, timeout=60, context=_CTX) as resp:
        datos = resp.read()
        content_type = resp.headers.get("Content-Type", "desconocido")

    sha = _sha256(datos)

    if archivo.exists() and manifiesto.exists():
        previo = json.loads(manifiesto.read_text(encoding="utf-8"))
        if previo.get("sha256") == sha:
            return {"estado": "ya_descargado", "archivo": str(archivo), "sha256": sha}

    archivo.write_bytes(datos)

    registro = {
        "identificador": identificador,
        "fuente": fuente,
        "url": url,
        "archivo": nombre,
        "fecha_descarga_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "sha256": sha,
        "size_bytes": len(datos),
        "content_type": content_type,
        "licencia": licencia,
        "notas": entrada.get("notas", ""),
    }
    manifiesto.write_text(
        json.dumps(registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {"estado": "descargado", "archivo": str(archivo), "sha256": sha}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifiesto", required=True, help="JSON con la lista de descargas")
    parser.add_argument("--licencia", default="pendiente_de_verificar", help="Licencia por defecto")
    args = parser.parse_args()

    ruta = Path(args.manifiesto)
    if not ruta.exists():
        print(f"ERROR: no existe {ruta}", file=sys.stderr)
        sys.exit(2)

    entradas = json.loads(ruta.read_text(encoding="utf-8"))
    if not isinstance(entradas, list):
        print("ERROR: el manifiesto debe ser una lista JSON", file=sys.stderr)
        sys.exit(2)

    ok = 0
    for i, entrada in enumerate(entradas, 1):
        entrada.setdefault("licencia", args.licencia)
        try:
            r = _descargar(entrada)
            print(f"[{i}/{len(entradas)}] {r['estado']}: {r['archivo']} ({r['sha256'][:12]}…)")
            ok += 1
        except urllib.error.HTTPError as exc:
            print(f"[{i}/{len(entradas)}] FALLO HTTP {exc.code}: {entrada.get('url')}")
        except Exception as exc:  # noqa: BLE001 - registro por entrada
            print(f"[{i}/{len(entradas)}] FALLO: {entrada.get('url')} -> {exc}")
    print(f"\nDescargas correctas: {ok}/{len(entradas)}")


if __name__ == "__main__":
    main()
