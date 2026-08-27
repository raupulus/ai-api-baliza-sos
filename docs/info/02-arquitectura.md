# 02 · Arquitectura

Dos servicios Python principales (`api` y `updater`) y una interfaz web de pruebas (`web`),
orquestados mediante **Docker Compose** sobre una red aislada (`bot-net`) junto a los servicios
de infraestructura (LLM `llama-server` y base de datos `PostgreSQL + pgvector`).

```
         Clientes externos (otros repos / navegador)
    ┌───────────────┐   ┌────────────────────┐   ┌──────────────────────┐
    │ Bot Telegram  │   │ Gateway Meshtastic │   │ Navegador (Web UI)   │
    └───────┬───────┘   └─────────┬──────────┘   └──────────┬───────────┘
            │                     │                         │
            │   HTTP :8870 (JSON) │                         ▼ HTTP :8443
            └──────────┬──────────┘              ┌──────────────────────┐
                       │                         │ SERVICIO WEB DE TEST │ (src/web, :8443)
                       │◄────────────────────────┤ proxy /api/v1/...    │
                       ▼                         └──────────────────────┘
         ┌─────────────────────────────┐
         │    SERVICIO API DEL BOT     │ (src/api, FastAPI :8870)
         │  ───────────────────────    │
         │  1. valida/normaliza query  │
         │  2. embed query             │──► fastembed (MiniLM-L12-v2, 384d)
         │  3. recupera top-k          │──► PostgreSQL + pgvector (HNSW)
         │  4. construye prompt+ctx    │
         │  5. genera respuesta        │──► llama-server (:8869)
         │  6. post-procesa a 250×3    │
         │  7. devuelve JSON           │
         └─────────────────────────────┘
                       ▲
                       │ comparte BD y embeddings
                       ▼
         ┌─────────────────────────────┐
         │ SERVICIO ACTUALIZADOR CTX   │ (src/updater, perfil tools)
         │  ───────────────────────    │
         │  fuentes → normaliza →      │
         │  STAGING → checkpoint       │──► revisión humana
         │  humano → embed → indexa    │──► PostgreSQL + pgvector
         └─────────────────────────────┘

    Infra (Docker / bot-net):
    - bot-llm: llama-server ARM (:8869)
    - bot-db:  PostgreSQL 17 + pgvector (interno :5432, host :5433)
```

## 2. Servicios de infraestructura y Puertos

| Contenedor | Puerto Host | Puerto Interno | Servicio / Rol |
| :--- | :--- | :--- | :--- |
| **`bot-llm`** | **`8869`** | `8869` | Servidor `llama-server` nativo ARM (`qwen2.5-3b-instruct-q4_k_m.gguf`). |
| **`bot-api`** | **`8870`** | `8870` | API REST FastAPI del bot con pipeline RAG. |
| **`bot-web`** | **`8443`** | `8443` | Interfaz web de pruebas y chat interactivo para simular paquetes RF. |
| **`bot-db`**  | **`5433`** | `5432` | PostgreSQL 17 con extensión `pgvector` e índice HNSW (evita choque con PG5432 host). |

### llama-server (llama.cpp)
- Contenedor independiente basado en `ghcr.io/ggml-org/llama.cpp:server`.
- Carga el GGUF indicado por `LLM_MODEL_FILE` montado desde el host (`/var/ia/bot-emergencias/models/`).
- Escucha en el puerto **`8869`**.
- Desacopla el cambio de modelo: editar `.env` + `docker compose restart llm`.
- Una sola inferencia concurrente serializada por la API para preservar CPU y RAM.

### PostgreSQL + pgvector
- Contenedor basado en `pgvector/pgvector:pg17`.
- Datos persistidos en el host en `/var/ia/bot-emergencias/data/postgres`.
- Mapeado externamente al puerto `5433` para evitar conflicto con cualquier PostgreSQL del sistema anfitrión.
- Índice vectorial **HNSW** (Hierarchical Navigable Small World) para inserciones incrementales dinámicas y recall óptimo desde 0 filas.

## 3. Servicio API del bot (`src/api`)

Responsabilidad: convertir una consulta en una respuesta breve y fiable.

Pipeline por petición:

1. **Validación** del cuerpo (pydantic): texto de consulta, idioma, metadatos
   opcionales (categoría sugerida, coordenadas si las hay).
2. **Embedding de la consulta** con e5-small (prefijo `query:`), en proceso.
3. **Recuperación** top-k en pgvector por similitud coseno, filtrando por
   umbral y opcionalmente por categoría/zona.
4. **Construcción del prompt**: plantilla del sistema (rol, reglas de brevedad,
   español, "no inventes") + fragmentos recuperados + consulta.
5. **Generación** llamando a `llama-server` con `LLM_MAX_TOKENS` y timeout.
6. **Post-proceso**: recortar/segmentar a ≤ 250 caracteres × ≤ 3 mensajes,
   añadir aviso médico si la categoría lo requiere.
7. **Respuesta JSON** con la lista de mensajes y metadatos (fuentes, confianza).

Concurrencia: un único worker Uvicorn con **semáforo de 1** para la inferencia.
Las peticiones extra esperan en cola (hasta el límite de tiempo del cliente).

## 4. Servicio actualizador de contexto (`src/updater`)

Responsabilidad: construir y mantener la base de conocimiento, con seguridad.

Flujo:

1. **Adquisición** por fuente (`src/updater/sources/*`): API directa (GBIF,
   Overpass, AEMET, IGN, Wikidata) o scraping puntual de PDF (primeros auxilios,
   manuales de supervivencia).
2. **Normalización** al formato de fragmento común
   `{ texto, fuente, fecha, categoria, nivel_confianza, ... }`.
3. **Staging**: los fragmentos sensibles (primeros auxilios, especies
   peligrosas) se dejan en `data/staging` **pendientes de revisión humana**.
4. **Checkpoint humano**: un operador aprueba/edita/rechaza. Sin aprobación, no
   se indexa.
5. **Embedding + indexado**: se generan embeddings (prefijo `passage:`) y se
   hace upsert en pgvector con idempotencia (hash de contenido).

Se ejecuta **bajo demanda** o mediante **systemd timer** (no es crítico en
tiempo y puede correr de noche). No comparte proceso con la API.

## 5. Por qué dos servicios separados

- **Aislamiento de recursos.** La ingesta/scraping puede ser intensiva; no debe
  competir con la latencia de la API ni arriesgar la RAM durante una consulta.
- **Ciclos de vida distintos.** La API corre siempre; el actualizador, a
  ratos.
- **Seguridad.** El checkpoint humano vive en el actualizador, lejos del camino
  de respuesta en caliente.
- **Despliegue.** Unidades systemd independientes, reiniciables por separado.

## 6. Arranque y dependencias (systemd)

Orden lógico de arranque: `postgresql-local` → `llama-server` → `bot-api`.
El `context-updater` depende de `postgresql-local` (y de red para adquirir).
Las dependencias se expresan con `After=`/`Requires=` en las unidades
(`deploy/systemd/`). Todo debe levantar solo tras un reinicio de la Pi.

## 7. Datos en el directorio de trabajo

Bajo `data/` (no trackeado):
- `data/postgres/` — clúster PostgreSQL local.
- `data/staging/` — fragmentos pendientes de revisión.
- `models/` (raíz, ignorado) — ficheros GGUF/ONNX descargados.
