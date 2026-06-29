from __future__ import annotations

from pathlib import Path

import pytest

from common.models import Categoria, Fragmento
from updater import staging


@pytest.fixture()
def staging_tmp(tmp_path, monkeypatch):
    monkeypatch.setattr(staging, "_base", lambda: tmp_path)
    return tmp_path


def _frag(texto="protocolo rcp"):
    return Fragmento(texto=texto, fuente="ERC", categoria=Categoria.PRIMEROS_AUXILIOS)


def test_stage_y_aprobar_flujo(staging_tmp: Path):
    f = _frag()
    assert staging.stage([f]) == 1
    pendientes = staging.listar_pendientes()
    assert len(pendientes) == 1

    frag_aprobado = staging.aprobar(pendientes[0], operador="raul")
    assert frag_aprobado.validado is True
    assert frag_aprobado.validado_por == "raul"
    assert staging.listar_pendientes() == []
    assert len(staging.listar_aprobados()) == 1


def test_stage_idempotente(staging_tmp: Path):
    f = _frag()
    assert staging.stage([f]) == 1
    assert staging.stage([f]) == 0  # mismo hash, no duplica


def test_rechazar(staging_tmp: Path):
    f = _frag("otro")
    staging.stage([f])
    ruta = staging.listar_pendientes()[0]
    staging.rechazar(ruta)
    assert staging.listar_pendientes() == []


def test_consumir_aprobados_vacia_la_cola(staging_tmp: Path):
    f = _frag("para indexar")
    staging.stage([f])
    staging.aprobar(staging.listar_pendientes()[0], operador="op")
    frags = staging.consumir_aprobados()
    assert len(frags) == 1
    assert staging.listar_aprobados() == []
