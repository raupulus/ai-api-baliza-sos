"""Generación de embeddings con multilingual-e5-small vía fastembed (ONNX).

fastembed se importa de forma perezosa (solo al instanciar el modelo) para que
las pruebas puras y otros módulos puedan importar este fichero sin tener el
modelo descargado. La familia e5 exige prefijos `query:` / `passage:`.
"""

from __future__ import annotations

import logging
import threading

from common.config import settings
from common.errors import EmbeddingError

_log = logging.getLogger(__name__)


class Embedder:
    """Envoltura singleton sobre fastembed. Carga el modelo una sola vez."""

    _instance: "Embedder | None" = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._model = None
        self.dim = settings.embedding_dim

    @classmethod
    def instance(cls) -> "Embedder":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _ensure_model(self):
        # Doble verificación con candado: evita que dos hilos del threadpool
        # (si se sube API_MAX_CONCURRENT_INFERENCES > 1) carguen el modelo a la
        # vez y dupliquen la RAM. (Hallazgo B de docs/planning/checks/check2.)
        if self._model is None:
            with self._lock:
                if self._model is None:
                    try:
                        from fastembed import TextEmbedding
                    except ImportError as exc:  # pragma: no cover
                        raise EmbeddingError(
                            "fastembed no está instalado. Instala requirements/api.txt."
                        ) from exc
                    _log.info("Cargando modelo de embeddings: %s", settings.embedding_model)
                    self._model = TextEmbedding(model_name=settings.embedding_model)
        return self._model

    def _embed(self, textos: list[str]) -> list[list[float]]:
        model = self._ensure_model()
        vectores = [list(map(float, v)) for v in model.embed(textos)]
        if vectores and len(vectores[0]) != self.dim:
            raise EmbeddingError(
                f"Dimensión de embedding {len(vectores[0])} != EMBEDDING_DIM {self.dim}. "
                "¿Has cambiado de modelo sin actualizar EMBEDDING_DIM y reindexar?"
            )
        return vectores

    def embed_query(self, texto: str) -> list[float]:
        """Embedding de una consulta (prefijo `query:`)."""
        prefijado = f"{settings.embedding_query_prefix}{texto}"
        return self._embed([prefijado])[0]

    def embed_passages(self, textos: list[str]) -> list[list[float]]:
        """Embeddings de fragmentos a indexar (prefijo `passage:`)."""
        prefijados = [f"{settings.embedding_passage_prefix}{t}" for t in textos]
        return self._embed(prefijados)


def get_embedder() -> Embedder:
    return Embedder.instance()
