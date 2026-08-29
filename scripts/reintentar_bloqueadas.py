#!/usr/bin/env python3
"""Reintenta URLs bloqueadas con cortesía de red (anti-bot).

Estrategia: cabecera de Safari en macOS, 3 s entre peticiones, pausa de 10 s cada
5 peticiones, y orden alternando dominios para no martillear el mismo host.
Solo registra el resultado (código, tipo, tamaño) y guarda el cuerpo si es 200.

Uso:
    python3 scripts/reintentar_bloqueadas.py
"""
from __future__ import annotations

import time
import urllib.request
from pathlib import Path

# Cabecera de Safari en macOS (reciente).
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15")

HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "identity",  # evitar contenido comprimido para inspeccionar
}

# (etiqueta, url) — orden alternando dominios.
URLS = [
    ("EUR-Lex Carta DFUE", "https://eur-lex.europa.eu/legal-content/ES/TXT/HTML/?uri=CELEX:12012P/TXT&from=ES"),
    ("EUDA (EMCDDA)", "https://www.euda.europa.eu/"),
    ("ADIF IDEADIF", "https://ideadif.adif.es/"),
    ("Puertos del Estado", "https://www.puertos.es/"),
    ("ROA Efemérides", "https://armada.defensa.gob.es/ArmadaPortal/page/Portal/ArmadaEspannola/cienciaobservatorio/prefLang-es/03Efemerides"),
    ("UIT HET", "https://www.itu.int/pub/D-HDB-HET/es"),
    ("RTOD collections", "https://apirtod.dipucadiz.es/api/collections.json"),
    ("RTOD proteccion_civil", "https://apirtod.dipucadiz.es/api/datos/proteccion_civil.json"),
    ("REDIAM flora GetCapabilities", "https://www.juntadeandalucia.es/medioambiente/mapwms/REDIAM_WFS_localizacion_flora_andaluza?service=WFS&version=2.0.0&request=GetCapabilities"),
]


def _probar(etiqueta: str, url: str) -> None:
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            codigo = r.status
            final = r.geturl()
            ctype = r.headers.get("content-type", "")
            cuerpo = r.read(4096)
            tam = r.headers.get("content-length", f"{len(cuerpo)}+")
            print(f"[{codigo:>3}] {etiqueta:32s} -> {final}")
            print(f"        type={ctype} | size={tam}")
    except urllib.error.HTTPError as e:
        print(f"[{e.code:>3}] {etiqueta:32s} -> HTTPError ({e.reason})")
    except Exception as e:
        print(f"[ERR] {etiqueta:32s} -> {type(e).__name__}: {e}")


def main() -> int:
    for i, (etiqueta, url) in enumerate(URLS, 1):
        _probar(etiqueta, url)
        if i < len(URLS):
            time.sleep(3)
        if i % 5 == 0 and i < len(URLS):
            print("  … pausa de cortesía 10 s …")
            time.sleep(10)
    print("Reintento completado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
