from __future__ import annotations

import pytest

from api.rag.indexing import index_fragmentos
from common.models import Categoria, Fragmento


def test_no_indexa_sensibles_sin_validar():
    """Defensa en profundidad: indexar contenido sensible sin validación falla
    antes de tocar embeddings o la base de datos."""
    f = Fragmento(
        texto="Protocolo de RCP no verificado",
        fuente="scraping",
        categoria=Categoria.PRIMEROS_AUXILIOS,
    )
    with pytest.raises(ValueError):
        index_fragmentos([f])


def test_lista_vacia_no_falla():
    assert index_fragmentos([]) == (0, 0)
