# 06 · Estado de implementación

Resumen de lo implementado en la primera sesión de desarrollo (módulos 01–07) y
qué falta por ejecutar en la Raspberry Pi. La planificación por módulos lleva los
checklists marcados con la misma información.

## Qué está hecho (código + verificado en sandbox)

- **Módulo 01 · Infra/common**: `config.py` (carga tipada de `env.py` con
  validación), `errors.py`, `logging.py`, `models.py` (Fragmento/Fuente +
  política de validación), `db.py` (pool psycopg + pgvector, importación
  perezosa). Esquema SQL `0001_init.sql`, `migrate.py`, `init_cluster.sh`,
  `env_export.py`.
- **Módulo 02 · LLM**: `llm_client.py` (cliente a llama-server con timeout,
  errores y health), `build_llama.sh`, `download_model.sh`.
- **Módulo 03 · RAG**: `embeddings.py` (e5-small vía fastembed, lazy),
  `retrieval.py` (pgvector coseno + filtros), `context.py` (construcción acotada
  + señal "sin contexto"), `indexing.py` (upsert idempotente + bloqueo de
  sensibles sin validar). `eval_rag.py` y casos en `tests/data/`.
- **Módulo 04 · API**: `app.py` (FastAPI, auth Bearer, `/health`,
  `/v1/consulta`), `schemas.py`, `pipeline.py`, `prompt.py`, `postprocess.py`
  (250×3 + aviso médico), `concurrency.py` (semáforo de 1 inferencia).
- **Módulo 05 · Actualizador**: `pipeline.py`, `normalize.py` (política de
  confianza + separación), `staging.py` (checkpoint humano), `cli.py`,
  `scripts/review.py`.
- **Módulo 06 · Fuentes**: `http_client.py` (UA, rate limit, reintentos),
  conectores reales **Overpass/OSM**, **GBIF** (con heurístico de peligrosidad →
  checkpoint) y **Wikidata**; resto como stubs que siguen la interfaz.
- **Módulo 07 · Calidad**: anti-alucinación en el prompt, avisos médicos,
  bloqueo de indexado sin validación, `backup.sh`, `healthcheck.sh`, y una suite
  de **pruebas unitarias** (`tests/`).
- **Despliegue**: unidades systemd de los 4 servicios + timer, `install.sh`,
  `bootstrap.sh`, `seed_corpus.py`.

### Verificación realizada en sandbox

- `py_compile` de todo `src/` y `scripts/`: sin errores de sintaxis.
- Smoke test de lógica pura (config, models, normalize, postprocess, prompt,
  context, staging, bloqueo de indexado sensible): **todos OK**.
- Las pruebas en `tests/` están escritas para `pytest`; en el sandbox no hay red
  para instalar dependencias, así que se validó la misma lógica con la stdlib.

## Qué falta (requiere la Raspberry Pi o servicios en vivo)

Estos puntos están como `[ ]` en los checklists:

- Compilar **llama.cpp** en ARM y descargar el modelo GGUF (`build_llama.sh`,
  `download_model.sh`).
- Levantar **PostgreSQL local** + pgvector, aplicar migraciones y cargar el
  corpus semilla (`init_cluster.sh`, `migrate.py`, `seed_corpus.py`).
- Pruebas de **integración** end-to-end (API→RAG→LLM) y medición de RAM/tiempos
  reales en la Pi.
- Conectores restantes (IGN, AEMET, MITECO, supervivencia y primeros auxilios) y
  el extractor de PDF.
- Métricas/observabilidad y hardening final.

## Cómo arrancar en local (desarrollo)

```bash
scripts/bootstrap.sh                 # venv + dependencias + env.py
source .venv/bin/activate
pytest                               # ejecuta la suite de pruebas
```

## Cómo desplegar en la Raspberry Pi

```bash
scripts/install.sh                   # paquetes, llama.cpp, modelo, BD, systemd
# revisa env.py (DB_PASSWORD, API_AUTH_TOKEN, LLM_MODEL_PATH) antes
python3 scripts/seed_corpus.py       # corpus de prueba (opcional)
python -m updater.cli --all          # ingesta por API (Overpass/GBIF/Wikidata)
python3 scripts/review.py            # checkpoint humano de lo sensible
python -m updater.cli --reindex-aprobados
scripts/healthcheck.sh
```
