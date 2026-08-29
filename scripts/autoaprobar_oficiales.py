#!/usr/bin/env python3
"""Auto-aprueba los fragmentos procedentes de fuentes oficiales (estado/UE/autonómicas).

Política (decisión del usuario 2026-08-28): el contenido de fuentes oficiales ya
está revisado por la propia institución, así que se marca `validado_por = "Fuente
oficial (estado/UE)"` y se aprueba sin revisor humano. Solo quedan en `pendientes`
los fragmentos de fuentes externas/comunitarias (Overpass, Wikidata, GBIF,
Wikipedia, Meshtastic) o de origen no identificable.

Uso:
    python3 scripts/autoaprobar_oficiales.py [--dry-run]
"""
from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from updater import staging  # noqa: E402

OPERADOR = "Fuente oficial (estado/UE)"

# Dominios de fuentes oficiales (incluye subdominios). ".gob.es" cubre sanidad,
# aemps, datos.gob.es, etc. ".europa.eu" cubre EUR-Lex, european-union, etc.
DOMINIOS_OFICIALES = {
    "gob.es", "boe.es", "policia.es", "europa.eu", "juntadeandalucia.es",
    "ideandalucia.es", "guardiacivil.es", "cruzroja.es", "proteccioncivil.es",
    "dipucadiz.es", "sepe.es", "bopcadiz.es", "cadizturismo.com", "dgt.es",
    "renfe.com", "adif.es", "ctan.es", "112.es",
}

# Palabras clave de organismos oficiales/sociedades científicas para fragmentos
# sin URL (bug de migración) o cuyo host no se resuelve.
ORGANISMOS_OFICIALES = (
    "ingesa", "dgpce", "ministerio de sanidad", "ministerio de igualdad",
    "junta de andalucía", "boja", "guardia civil", "carta de los derechos",
    "constitución española", "112.es", "boe", "policía", "cruz roja",
    "protección civil", "sas", "aesan", "aemps", "ign", "ieca", "adif",
    "renfe", "ctan", "european resuscitation council", "erc", "eur-lex",
)


def es_oficial(fuente_url: str | None, fuente: str | None) -> bool:
    if fuente_url:
        host = (urlparse(fuente_url).hostname or "").lower()
        if host:
            return any(host == d or host.endswith("." + d) for d in DOMINIOS_OFICIALES)
    # Sin URL o host vacío → decidir por el texto del campo fuente.
    texto = (fuente or "").lower()
    return any(org in texto for org in ORGANISMOS_OFICIALES)


def main() -> int:
    from common.models import CATEGORIAS_SENSIBLES  # noqa: E402
    dry = "--dry-run" in sys.argv
    aprobados = 0
    pendientes = 0
    for ruta in staging.listar_pendientes():
        frag = staging.cargar(ruta)
        es_sensible = frag.peligrosa or frag.categoria in CATEGORIAS_SENSIBLES
        # Revisar solo si: fuente externa Y contenido sensible/peligroso.
        if (not es_oficial(frag.fuente_url, frag.fuente)) and es_sensible:
            pendientes += 1
        else:
            if not dry:
                staging.aprobar(ruta, OPERADOR)
            aprobados += 1

    print(f"Aprobados: {aprobados}")
    print(f"Pendientes (externo sensible/peligroso): {pendientes}")
    if dry:
        print("(modo --dry-run: no se movió nada)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
