# src — Código del backend

- `common/`  Config (`config.py`), BD (`db.py`), logging, modelos y errores compartidos.
- `api/`     Servicio del bot (FastAPI). Endpoints, pipeline y post-proceso.
- `api/rag/` Embeddings, recuperación y construcción de contexto.
- `updater/` Servicio actualizador de contexto (ingesta + checkpoint + indexado).
- `updater/sources/` Un conector por fuente de datos (GBIF, Overpass, AEMET, IGN...).

Estado: planificación. La implementación sigue `docs/planning/initial_plan/`.
