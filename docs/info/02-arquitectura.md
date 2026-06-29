# 02 · Arquitectura

## 1. Vista general

Dos servicios Python independientes sobre dos servicios de infraestructura
(LLM y base de datos), todo nativo en la Raspberry Pi y gestionado por systemd.

```
        Clientes externos (otros repos)
   ┌───────────────┐   ┌────────────────────┐
   │ Bot Telegram  │   │ Gateway Meshtastic │
   └───────┬───────┘   └─────────┬──────────┘
           │   HTTP (JSON)       │
           └──────────┬──────────┘
                      ▼
        ┌─────────────────────────────┐
        │   SERVICIO API DEL BOT      │   (src/api, FastAPI+Uvicorn)
        │  ───────────────────────    │
        │  1. valida/normaliza query  │
        │  2. embed query             │──► fastembed (e5-small, en proceso)
        │  3. recupera top-k          │──► PostgreSQL + pgvector
        │  4. construye prompt+ctx    │
        │  5. genera respuesta        │──► llama-server (HTTP localhost)
        │  6. post-procesa a 250×3    │
        │  7. devuelve JSON           │
        └─────────────────────────────┘
                      ▲
                      │ comparte BD y embeddings
                      ▼
        ┌─────────────────────────────┐
        │ SERVICIO ACTUALIZADOR CTX   │   (src/updater)
        │  ───────────────────────    │
        │  fuentes → normaliza →      │
        │  STAGING → checkpoint       │──► revisión humana
        │  humano → embed → indexa    │──► PostgreSQL + pgvector
        └─────────────────────────────┘

   Infra (systemd):  llama-server   ·   PostgreSQL(+pgvector)
```

## 2. Servicios de infraestructura

### llama-server (llama.cpp)
- Proceso aparte que carga el GGUF indicado por `LLM_MODEL_PATH` y expone una
  API HTTP compatible OpenAI en `127.0.0.1:LLM_SERVER_PORT`.
- Desacopla el cambio de modelo: editar env + `systemctl restart llama-server`.
- Una sola instancia; la API serializa las peticiones (semáforo).

### PostgreSQL + pgvector
- Clúster **local** inicializado en `data/postgres` (autocontenido en el
  proyecto, como pidió el requisito). Servicio systemd propio.
- Una base de datos (`bot_emergencias`) con la extensión `pgvector`.
- Almacena los fragmentos de conocimiento, sus metadatos y sus embeddings.

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
