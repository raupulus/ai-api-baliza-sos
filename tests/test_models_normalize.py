from __future__ import annotations

from common.models import Categoria, Fragmento, NivelConfianza
from updater import normalize


def test_hash_estable():
    f1 = Fragmento(texto="hola", fuente="F", categoria=Categoria.GEOGRAFIA)
    f2 = Fragmento(texto="hola", fuente="F", categoria=Categoria.GEOGRAFIA)
    assert f1.hash_contenido == f2.hash_contenido


def test_primeros_auxilios_requiere_validacion():
    f = Fragmento(texto="x", fuente="Cruz Roja", categoria=Categoria.PRIMEROS_AUXILIOS)
    assert f.requiere_validacion is True
    assert f.validado is False


def test_especie_peligrosa_requiere_validacion():
    f = Fragmento(texto="medusa", fuente="GBIF", categoria=Categoria.FAUNA, peligrosa=True)
    assert f.requiere_validacion is True


def test_geografia_no_requiere_validacion():
    f = Fragmento(texto="playa", fuente="OSM", categoria=Categoria.GEOGRAFIA)
    assert f.requiere_validacion is False


def test_politica_capa_confianza_de_sensibles():
    f = Fragmento(
        texto="protocolo",
        fuente="X",
        categoria=Categoria.PRIMEROS_AUXILIOS,
        nivel_confianza=NivelConfianza.ALTA,
    )
    normalize.aplicar_politica([f])
    assert f.nivel_confianza == NivelConfianza.MEDIA  # rebajada por no estar validada


def test_separar_directos_y_checkpoint():
    geo = Fragmento(texto="playa", fuente="OSM", categoria=Categoria.GEOGRAFIA)
    med = Fragmento(texto="rcp", fuente="ERC", categoria=Categoria.PRIMEROS_AUXILIOS)
    directos, checkpoint = normalize.separar([geo, med])
    assert geo in directos and med in checkpoint
