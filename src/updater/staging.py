"""Staging y checkpoint humano.

Los fragmentos sensibles (primeros auxilios, especies peligrosas) se serializan a
`UPDATER_STAGING_DIR` en JSON legible y NO se indexan hasta que un operador los
aprueba. Esta es la puerta única de validación humana (defensa del contenido).
"""

from __future__ import annotations

import json
import logging
from datetime import date
from pathlib import Path
from typing import Iterable

from common.config import settings
from common.models import Categoria, Fragmento, NivelConfianza

_log = logging.getLogger(__name__)

PENDIENTES = "pendientes"
APROBADOS = "aprobados"
RECHAZADOS = "rechazados"


def _base() -> Path:
    return Path(settings.updater_staging_dir)


def _dir(estado: str) -> Path:
    d = _base() / estado
    d.mkdir(parents=True, exist_ok=True)
    return d


def fragmento_a_dict(f: Fragmento) -> dict:
    return {
        "texto": f.texto,
        "fuente": f.fuente,
        "fuente_url": f.fuente_url,
        "fecha": f.fecha.isoformat() if f.fecha else None,
        "categoria": f.categoria.value,
        "subcategoria": f.subcategoria,
        "provincia": f.provincia,
        "nivel_confianza": f.nivel_confianza.value,
        "licencia": f.licencia,
        "peligrosa": f.peligrosa,
        "validado_por": f.validado_por,
        "validado_fecha": f.validado_fecha.isoformat() if f.validado_fecha else None,
        "hash_contenido": f.hash_contenido,
    }


def dict_a_fragmento(d: dict) -> Fragmento:
    return Fragmento(
        texto=d["texto"],
        fuente=d["fuente"],
        fuente_url=d.get("fuente_url"),
        fecha=date.fromisoformat(d["fecha"]) if d.get("fecha") else None,
        categoria=Categoria(d["categoria"]),
        subcategoria=d.get("subcategoria"),
        provincia=d.get("provincia"),
        nivel_confianza=NivelConfianza(d.get("nivel_confianza", "media")),
        licencia=d.get("licencia"),
        peligrosa=d.get("peligrosa", False),
        validado_por=d.get("validado_por"),
        validado_fecha=date.fromisoformat(d["validado_fecha"]) if d.get("validado_fecha") else None,
        hash_contenido=d.get("hash_contenido", ""),
    )


def stage(fragmentos: Iterable[Fragmento]) -> int:
    """Escribe fragmentos pendientes de validación. Idempotente por hash."""
    n = 0
    for f in fragmentos:
        ruta = _dir(PENDIENTES) / f"{f.hash_contenido}.json"
        if ruta.exists():
            continue
        ruta.write_text(
            json.dumps(fragmento_a_dict(f), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        n += 1
    if n:
        _log.info("Staging: %d fragmento(s) pendientes de validación en %s", n, _dir(PENDIENTES))
    return n


def listar_pendientes() -> list[Path]:
    return sorted(_dir(PENDIENTES).glob("*.json"))


def cargar(ruta: Path) -> Fragmento:
    return dict_a_fragmento(json.loads(ruta.read_text(encoding="utf-8")))


def aprobar(ruta: Path, operador: str) -> Fragmento:
    """Marca el fragmento como validado y lo mueve a 'aprobados'. Devuelve el fragmento."""
    frag = cargar(ruta)
    frag.validado_por = operador
    frag.validado_fecha = date.today()
    destino = _dir(APROBADOS) / ruta.name
    destino.write_text(
        json.dumps(fragmento_a_dict(frag), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    ruta.unlink(missing_ok=True)
    _log.info("Aprobado por %s: %s", operador, frag.fuente)
    return frag


def rechazar(ruta: Path) -> None:
    destino = _dir(RECHAZADOS) / ruta.name
    destino.write_text(ruta.read_text(encoding="utf-8"), encoding="utf-8")
    ruta.unlink(missing_ok=True)


def listar_aprobados() -> list[Path]:
    return sorted(_dir(APROBADOS).glob("*.json"))


def consumir_aprobados() -> list[Fragmento]:
    """Carga los aprobados y los retira de la cola (para indexar). """
    frags = []
    for ruta in listar_aprobados():
        frags.append(cargar(ruta))
        ruta.unlink(missing_ok=True)
    return frags
