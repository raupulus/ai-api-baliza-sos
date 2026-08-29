# 06 · Estado de implementación

> **Última actualización:** 2026-08-29  
> **Ámbito:** Matriz de avance de módulos y estado operativo en producción.

[← Volver al Índice de Documentación Técnica](README.md)

---

## Estado del corpus RAG — Indexado en Producción (2026-08-29)

> El corpus cuenta con **4.615 fragmentos vectorizados e indexados en PostgreSQL (`pgvector`)** en la Raspberry Pi 5.
> La suite completa de pruebas por lotes ([`scripts/test_banco_completo.py`](file:///Users/fryntiz/git/bot-ia-auxiliar/scripts/test_banco_completo.py) / `make test-banco`) alcanza una **tasa de éxito del 100% (46/46 casos superados)**.
> La Web UI cuenta con **telemetría en tiempo real por WebSockets (`/ws/telemetry`)**, selectores jerárquicos de prueba en 3 niveles y límite calibrado a 200 bytes UTF-8.

| Categoría | Frag. | | Categoría | Frag. |
|---|---:|---|---|---:|
| Geografía | 3.266 | | Fauna | 34 |
| Supervivencia | 668 | | Orientación | 29 |
| Transporte | 457 | | Cultura / Historia | 17 |
| Directorios | 65 | | Flora | 13 |
| Primeros auxilios | 38 | | Protección civil | 11 |
| Apoyo psicosocial | 7 | | Toxicología | 4 |
| Clima | 3 | | Legislación | 2 |
| Agricultura | 1 | | **TOTAL** | **4.615** |

- **Validación:** 100% del corpus aprobado y validado (fuentes oficiales sanitarias, autonómicas, estatales y cartográficas).
- **Modo Asistente Offline (Último Recurso):** Respuestas prácticas sin pedir llamar al 112 ni desvariar en entornos urbanos/playa/hogar; teléfonos exclusivamente facilitados bajo petición explícita de directorios.
- **Gobierno:** 17 fichas temáticas + plantilla + auditoría + checklist en `docs/rag/`.

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
  (230 bytes UTF-8 × 3 + aviso médico), `concurrency.py` (semáforo de 1 inferencia).
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

## Estado de ejecución y despliegue en hardware real

Todos los hitos previstos para la Raspberry Pi 5 se han completado y validado en vivo:

- [x] Ejecución de **llama.cpp** (`llama-server`) en ARM con modelo Qwen2.5-3B Q4_K_M en puerto `8869`.
- [x] Despliegue de **PostgreSQL 17** + pgvector con migraciones `0001_init.sql` y `0002_conversaciones.sql` aplicadas.
- [x] Ingesta y vectorización de **89 fragmentos locales de Cádiz** (línea base desplegada en la Pi; el corpus ampliado a 4474 fragmentos está en `data/staging/aprobados/`, ver sección anterior).
- [x] Suite de **pruebas unitarias (51 tests)** ejecutándose dentro del contenedor API al 100% OK.
- [x] Batería de **pruebas de integración E2E (6/6 tests)** validada en caliente contra el endpoint HTTP `http://172.18.1.121:8870`.
- [x] Frontend Web UI de validación previa operativo en `http://172.18.1.121:8443`.


## Cómo arrancar en local (desarrollo)

```bash
scripts/bootstrap.sh                 # venv + dependencias + env.py
source .venv/bin/activate
pytest                               # ejecuta la suite de pruebas
```

## Estado en producción (Raspberry Pi 5 en vivo)

> **Última actualización:** 2026-08-28  
> **Estado global:** 100% Operativo y Desplegado en Docker

El backend se encuentra **desplegado y validado al 100% en Docker** sobre la Raspberry Pi 5 (`172.18.1.121`):

- **Contenedores activos (healthy):**
  - `bot-llm` en puerto `8869` (Qwen 2.5-3B-Instruct Q4_K_M en ARM).
  - `bot-api` en puerto `8870` (FastAPI + Embeddings MiniLM 384d + Memoria conversacional multi-turno).
  - `bot-web` en puerto `8443` (Interfaz web de chat con gestión de sesión y reseteo).
  - `bot-db` en puerto interno `5432` / host `5433` (PostgreSQL 17 + pgvector HNSW).
- **Memoria Conversacional y Persistencia (`0002_conversaciones.sql`):**
  - Historial multi-turno persistente en tablas `conversaciones` y `mensajes_conversacion`.
  - Ventana móvil de 20 turnos con compactación por IA y expiración por inactividad tras 1 hora (TTL 3600 s).
  - Endpoint `POST /v1/conversacion/reset` y parámetro `reset_conversacion: true`.
- **Triaje de Emergencias Activo:**
  - Sustituido el rechazo prematuro por un triaje activo que evalúa gravedad física, aporta pautas de estabilización/supervivencia y solicita referencias para el 112.
- **Corpus RAG en producción (89 fragmentos desplegados; 4474 preparados en staging):**
  - Primeros auxilios avanzados y montaña, flora y fauna peligrosa/comestible, los 45 municipios con coordenadas GPS oficiales y cotas, fiestas populares e historia.
  - Script manual bajo demanda: `python3 scripts/actualizar_fuente.py`.
- **Rendimiento validado:**
  - Latencia media en RPi5: ~6.8s – 8.6s por inferencia.
  - Memoria RAM consumida: ~3.6 GiB de 7.9 GiB (4.3 GiB libres para otros proyectos/Hailo-8).
  - Respuestas estrictas en paquetes $\le 250$ caracteres para radiofrecuencia (Meshtastic).
- **Aislamiento total:** Los servicios del host (Apache, MariaDB, PG17 local, Ollama) continúan intactos sin ninguna colisión.

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

---

[← Volver al Índice de Documentación Técnica](README.md)

