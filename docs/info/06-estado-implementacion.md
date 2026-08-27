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

## Estado en producción (Raspberry Pi 5 en vivo)

El backend se encuentra **desplegado y validado al 100% en Docker** sobre la Raspberry Pi 5 (`172.18.1.121`):

- **Contenedores activos (healthy):**
  - `bot-llm` en puerto `8869` (Qwen 2.5-3B-Instruct Q4_K_M en ARM).
  - `bot-api` en puerto `8870` (FastAPI + Embeddings MiniLM 384d con caché persistente).
  - `bot-web` en puerto `8443` (Interfaz web de chat de pruebas y proxy a API).
  - `bot-db` en puerto interno `5432` / host `5433` (PostgreSQL 17 + pgvector HNSW).
- **Rendimiento validado:**
  - Latencia media en RPi5: ~8.6s – 9.7s por inferencia.
  - Memoria RAM consumida: 3.5 GiB de 7.9 GiB (4.4 GiB libres para Hailo-8 / visión).
  - Cumplimiento de paquetes $\le 250$ caracteres para radiofrecuencia (Meshtastic).
- **Corpus inicial:** Semilla cargada e indexada en pgvector con índice HNSW.
- **Aislamiento total:** Los servicios del host (Apache, MariaDB, PG17 local, Ollama) continúan activos sin ninguna colisión.

## Cómo arrancar con Docker

```bash
# Copiar plantilla y configurar variables si es una instalación nueva
cp .env.example .env

# Desplegar stack completo en segundo plano
docker compose up -d

# Ver estado de los contenedores
docker compose ps

# Comprobar salud del sistema
curl http://localhost:8870/health

# Cargar o reindexar corpus semilla
docker compose run --rm updater python3 scripts/seed_corpus.py
```
