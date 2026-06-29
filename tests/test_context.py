from __future__ import annotations

from api.rag.context import construir_contexto
from common.models import (
    Categoria,
    Fragmento,
    FragmentoRecuperado,
    NivelConfianza,
)


def _frag(texto, conf=NivelConfianza.MEDIA, cat=Categoria.GEOGRAFIA, fuente="F"):
    return Fragmento(texto=texto, fuente=fuente, categoria=cat, nivel_confianza=conf)


def test_sin_recuperados_no_es_suficiente():
    ctx = construir_contexto([])
    assert ctx.suficiente is False
    assert ctx.texto == ""
    assert ctx.confianza == 0.0


def test_contexto_basico():
    rec = [FragmentoRecuperado(_frag("El faro esta al norte."), 0.9)]
    ctx = construir_contexto(rec)
    assert ctx.suficiente is True
    assert "faro" in ctx.texto
    assert ctx.categoria == Categoria.GEOGRAFIA
    assert ctx.confianza == 0.9
    assert len(ctx.fuentes) == 1


def test_prioriza_confianza_alta():
    baja = FragmentoRecuperado(_frag("texto baja", NivelConfianza.BAJA), 0.95)
    alta = FragmentoRecuperado(_frag("texto alta", NivelConfianza.ALTA), 0.80)
    ctx = construir_contexto([baja, alta])
    # La de confianza alta debe aparecer primero pese a menor score.
    assert ctx.texto.index("alta") < ctx.texto.index("baja")


def test_respeta_max_chars():
    rec = [FragmentoRecuperado(_frag("x" * 100, fuente=f"F{i}"), 0.9) for i in range(20)]
    ctx = construir_contexto(rec, max_chars=250)
    assert len(ctx.texto) <= 250 + 120  # margen por una entrada
