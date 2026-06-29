from __future__ import annotations

from api.postprocess import formatear
from common.config import settings
from common.models import Categoria

MAX = settings.resp_max_chars_per_msg
MAXM = settings.resp_max_messages


def test_respuesta_corta_un_mensaje():
    r = formatear("Sal del agua y avisa a alguien.", categoria=Categoria.GEOGRAFIA)
    assert len(r.mensajes) == 1
    assert not r.truncado


def test_limite_de_caracteres_por_mensaje():
    texto = "Frase. " * 200
    r = formatear(texto, categoria=Categoria.SUPERVIVENCIA)
    assert len(r.mensajes) <= MAXM
    assert all(len(m) <= MAX for m in r.mensajes)


def test_maximo_tres_mensajes():
    texto = " ".join(f"Instruccion numero {i} con texto adicional." for i in range(50))
    r = formatear(texto, categoria=Categoria.SUPERVIVENCIA)
    assert len(r.mensajes) <= MAXM


def test_aviso_medico_presente_en_fauna():
    r = formatear("Retira el tentaculo con cuidado.", categoria=Categoria.FAUNA)
    unido = " ".join(r.mensajes).lower()
    assert "112" in unido


def test_aviso_no_en_geografia():
    r = formatear("El faro esta al norte.", categoria=Categoria.GEOGRAFIA)
    assert "112" not in " ".join(r.mensajes)


def test_texto_vacio():
    r = formatear("   ", categoria=Categoria.GEOGRAFIA)
    assert r.mensajes == []


def test_frase_unica_muy_larga_se_trocea():
    palabra = "palabra "
    r = formatear(palabra * 100, categoria=Categoria.SUPERVIVENCIA)
    assert all(len(m) <= MAX for m in r.mensajes)
    assert len(r.mensajes) <= MAXM
