from __future__ import annotations

from updater.sources.gbif import GbifSource
from updater.sources.overpass import OverpassSource


def test_gbif_heuristico_peligro():
    assert GbifSource._es_peligrosa("Carabela portuguesa Physalia physalis") is True
    assert GbifSource._es_peligrosa("Gorrión común Passer domesticus") is False


def test_overpass_query_incluye_bbox():
    q = OverpassSource()._query()
    assert "out:json" in q
    assert "natural" in q and "beach" in q
    # El BBOX debe haberse interpolado (4 números separados por comas).
    assert q.count(",") >= 4


def test_overpass_describir():
    desc = OverpassSource._describir("Faro de Trafalgar", "faro", 36.18, -6.03, {})
    assert "Faro de Trafalgar" in desc
    assert "36.18" in desc
