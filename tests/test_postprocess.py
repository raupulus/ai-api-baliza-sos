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
    assert all(len(m.encode("utf-8")) <= MAX for m in r.mensajes)
    assert len(r.mensajes) <= MAXM


def test_limite_de_bytes_con_caracteres_espanoles():
    # Texto con multitud de caracteres de 2 bytes (tildes, ñ, ¿, ¡)
    frase = "¿Atención en Cádiz! Inmovilización rápida del tobillo dañado con pañuelo. "
    texto = frase * 20
    r = formatear(texto, categoria=Categoria.PRIMEROS_AUXILIOS)
    assert len(r.mensajes) <= MAXM
    # Cada mensaje debe respetar estrictamente <= MAX bytes UTF-8 (230 bytes)
    for m in r.mensajes:
        tam_bytes = len(m.encode("utf-8"))
        assert tam_bytes <= MAX, f"Mensaje excede {MAX} bytes UTF-8 ({tam_bytes} bytes): {m!r}"
        # Asegurar que el string es UTF-8 válido y no termina con caracteres rotos
        m.encode("utf-8").decode("utf-8")

