#!/usr/bin/env python3
"""Migra los fragmentos borrador de `data/processed/` a staging (checkpoint humano).

Los fragmentos generados en la fase de normalización viven como MD/CSV en
`data/processed/`, pero el flujo de validación (`scripts/review.py`) lee JSON de
`data/staging/pendientes/` (un `Fragmento` por fichero, clave = hash). Este script
los convierte y los envía a la cola de revisión SIN marcarlos como validados.

Uso:
    python3 scripts/migrar_a_staging.py
"""
from __future__ import annotations

import csv
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from common.models import Categoria, Fragmento, NivelConfianza  # noqa: E402
from updater import staging  # noqa: E402


def _parse_frontmatter(texto: str) -> dict[str, str]:
    """Extrae el bloque YAML del frontmatter Markdown.

    Soporta listas simples (clave: valor) y la lista anidada `fuentes:` con
    `nombre` y `url`. Devuelve un dict con claves normalizadas:
    `fuente_nombre`, `fuente_url`, `categoria`, `subcategoria`, `licencia`.
    """
    m = re.match(r"^---\n(.*?)\n---\n", texto, flags=re.S)
    if not m:
        return {}
    out: dict[str, str] = {}
    in_fuentes = False
    for line in m.group(1).splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped == "fuentes:":
            in_fuentes = True
            continue
        if in_fuentes and stripped.startswith("-"):
            # Dentro de la lista de fuentes: - nombre: "..."  o  - url: "..."
            mm = re.match(r"-\s*(nombre|url):\s*\"?(.*?)\"?$", stripped)
            if mm:
                key = "fuente_nombre" if mm.group(1) == "nombre" else "fuente_url"
                out[key] = mm.group(2).strip()
            continue
        if ":" in stripped:
            k, v = stripped.split(":", 1)
            out[k.strip()] = v.strip().strip('"')
    return out


def _md_a_fragmento(path: Path) -> Fragmento:
    texto = path.read_text(encoding="utf-8")
    meta = _parse_frontmatter(texto)
    cuerpo = re.sub(r"^---\n.*?\n---\n", "", texto, flags=re.S).strip()
    categoria_raw = (meta.get("categoria") or "").strip()
    try:
        categoria = Categoria(categoria_raw)
    except ValueError:
        raise ValueError(f"Categoría desconocida {categoria_raw!r} en {path.name}") from None
    return Fragmento(
        texto=cuerpo,
        fuente=meta.get("fuente_nombre") or "(sin fuente)",
        fuente_url=meta.get("fuente_url") or meta.get("url"),
        fecha=date.today(),
        categoria=categoria,
        subcategoria=meta.get("subcategoria"),
        provincia="Cádiz",
        nivel_confianza=NivelConfianza.MEDIA,  # sensible sin validar => media
        licencia=meta.get("licencia") or "pendiente_de_verificar",
        peligrosa=(meta.get("peligrosa") or "").strip().lower() == "true",
        validado_por=None,
        validado_fecha=None,
    )


def _csv_a_fragmentos(path: Path) -> list[Fragmento]:
    """Convierte un CSV de data/processed a fragmentos.

    Lee `categoria` y `subcategoria` de las columnas; el resto (fuente, URL,
    municipio, coordenadas) se compone en el texto. Es genérico para cualquier
    CSV que respete las columnas de PLANTILLA.csv. Si el CSV no tiene la
    columna `categoria`, se omite por completo.
    """
    frags: list[Fragmento] = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or "categoria" not in reader.fieldnames:
            print(f"OMITIDO {path.name}: sin columna 'categoria' (esquema no estándar)")
            return frags
        for row in reader:
            titulo = row.get("titulo", "").strip()
            contenido = row.get("contenido", "").strip()
            fuente = row.get("fuente", "").strip()
            fuente_url = row.get("fuente_url", "").strip()
            categoria_raw = row.get("categoria", "").strip()
            subcategoria = row.get("subcategoria", "").strip()
            mun = row.get("municipio", "").strip()
            lat = row.get("lat", "").strip()
            lon = row.get("lon", "").strip()
            try:
                categoria = Categoria(categoria_raw)
            except ValueError:
                print(f"OMITIDO {path.name} fila {titulo!r}: categoría desconocida {categoria_raw!r}")
                continue
            texto = contenido if contenido else f"{titulo} — {mun}. {lat}, {lon}."
            frags.append(
                Fragmento(
                    texto=texto,
                    fuente=fuente or "(sin fuente)",
                    fuente_url=fuente_url or None,
                    fecha=date.today(),
                    categoria=categoria,
                    subcategoria=subcategoria or None,
                    provincia="Cádiz",
                    nivel_confianza=NivelConfianza.MEDIA,
                    licencia="pendiente_de_verificar",
                    peligrosa=False,
                    validado_por=None,
                    validado_fecha=None,
                )
            )
    return frags


def main() -> int:
    md_dir = Path("data/processed/md")
    csv_dir = Path("data/processed/csv")

    fragmentos: list[Fragmento] = []

    # Todos los MD de data/processed/md (excluye plantillas).
    for path in sorted(md_dir.glob("*.md")):
        if path.name == "PLANTILLA.md":
            continue
        try:
            fragmentos.append(_md_a_fragmento(path))
        except ValueError as exc:
            print(f"OMITIDO {path.name}: {exc}")

    # CSVs estructurados (cualquiera que respete PLANTILLA.csv).
    for path in sorted(csv_dir.glob("*.csv")):
        if path.name == "PLANTILLA.csv":
            continue
        fragmentos.extend(_csv_a_fragmentos(path))

    n = staging.stage(fragmentos)
    print(f"Enviados a staging/pendientes: {n} fragmentos (nuevos)")
    print("Revisar con: python3 scripts/review.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
