# Módulo 01 · Infraestructura base

## Resumen

Cimientos del proyecto: estructura ya creada, gestión de configuración
(`env.py`/`config.py`), entorno Python, **PostgreSQL + pgvector** como clúster
local autocontenido en `data/postgres`, esquema de base de datos, capa común
(conexión a BD, logging, modelos de datos) y el esqueleto de las unidades
systemd. Al terminar este módulo existe una base sobre la que montar el LLM, el
RAG y los servicios. **Sin este módulo no se puede empezar nada más.**

Dependencias: ninguna. Habilita: 02, 03, 04, 05.

## Fase 1 — Entorno y dependencias

- Definir `pyproject.toml` (o `requirements/`) con dependencias separadas por
  servicio (api, updater, dev) para no instalar de más en la Pi.
- Entorno virtual (`.venv`) y fijado de versiones.
- Herramientas de calidad: `ruff`, `black`, `mypy`, `pytest`.

## Fase 2 — Capa de configuración (`src/common/config.py`)

- Cargador único que importa `env.py` y expone un objeto/`dataclass` de config
  tipado. Ningún otro módulo lee `os.environ` ni `env.py` directamente.
- Validación temprana: si falta una variable crítica o el modelo no existe,
  fallar al arranque con mensaje claro.
- Verificar que `env.example.py` y `env.py` están sincronizados (test simple).

## Fase 3 — PostgreSQL + pgvector local

- Script `deploy/postgres/init_cluster.sh`: `initdb` del clúster en
  `DB_DATA_DIR`, configuración (`postgresql.conf`: `shared_buffers`,
  `work_mem`, `max_connections` bajos; `listen_addresses`).
- Instalar/compilar la extensión **pgvector** para la versión de PostgreSQL de
  Raspberry Pi OS.
- Crear rol y base (`bot_emergencias`), `CREATE EXTENSION vector`.
- Script de arranque/parada del clúster local (lo usará la unidad systemd).

## Fase 4 — Esquema de datos (`deploy/postgres/schema.sql`)

- Tabla `fragmentos` (ver `docs/info/05-contratos-datos.md`), con
  `embedding vector(EMBEDDING_DIM)`.
- Tablas `fuentes`, `ingestas` y (opcional) `consultas`.
- Índice vectorial: empezar con búsqueda exacta o IVFFlat; dejar comentado el
  HNSW para escalado futuro.
- Migraciones simples (carpeta `deploy/postgres/migrations/` o herramienta
  ligera). Decidir mecanismo y documentarlo.

## Fase 5 — Capa común (`src/common`)

- `db.py`: pool de conexiones (psycopg) y helpers de consulta.
- `logging.py`: configuración de logging a fichero/stdout según `LOG_LEVEL`.
- `models.py`: modelos de datos compartidos (Fragmento, Fuente, etc.).
- `errors.py`: excepciones del dominio.

## Fase 6 — Esqueleto systemd y scripts

- Plantillas de unidades en `deploy/systemd/` (vacías/mínimas de momento):
  `postgresql-local.service`, `llama-server.service`, `bot-api.service`,
  `context-updater.service` (+ `.timer`).
- `scripts/`: `bootstrap.sh` (prepara entorno), `healthcheck.sh`.
- Documentar el arranque manual en desarrollo.

## Verificación del módulo

- Levantar PostgreSQL local, conectar y comprobar `CREATE EXTENSION vector`.
- Insertar y recuperar un vector de prueba (sanity check de pgvector).
- `config.py` carga y valida correctamente; test de sincronía env.
- Logging escribe donde debe.

## Checklist

> Leyenda de estado (autogenerada en la fase de implementación): [x] = terminado en código y verificado en sandbox · [ ] = pendiente de ejecutar en la Raspberry Pi o con BD/red en vivo (compilar llama.cpp en ARM, descargar modelo, levantar PostgreSQL, pruebas de integración).


- [x] Fase 1: `pyproject.toml`/requirements y entorno virtual operativos.
- [x] Fase 1: ruff/black/mypy/pytest configurados.
- [x] Fase 2: `config.py` carga `env.py` y expone config tipada.
- [x] Fase 2: validación de variables críticas al arranque.
- [x] Fase 2: test de sincronía `env.example.py` ↔ `env.py`.
- [x] Fase 3: script `initdb` del clúster local en `data/postgres`.
- [ ] Fase 3: pgvector instalado y `CREATE EXTENSION vector` correcto.
- [ ] Fase 3: rol y base `bot_emergencias` creados.
- [x] Fase 4: `schema.sql` con tabla `fragmentos` y `embedding vector(N)`.
- [x] Fase 4: tablas `fuentes`, `ingestas` (y `consultas`).
- [x] Fase 4: índice vectorial inicial (exacto/IVFFlat) creado.
- [x] Fase 4: mecanismo de migraciones definido.
- [x] Fase 5: `db.py` con pool y helpers.
- [x] Fase 5: `logging.py` operativo.
- [x] Fase 5: `models.py` con modelos compartidos.
- [x] Fase 6: plantillas de unidades systemd creadas.
- [x] Fase 6: `bootstrap.sh` y `healthcheck.sh`.
- [ ] Verificación: sanity check de inserción/recuperación de vector.
