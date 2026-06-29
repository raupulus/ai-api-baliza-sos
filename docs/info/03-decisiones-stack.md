# 03 · Decisiones de stack (con justificación)

Cada decisión se toma bajo una restricción dominante: **caber y funcionar en
una Raspberry Pi 4 con 4 GB de RAM, sin internet en operación**. Cuando una
opción es "más potente pero más pesada", gana la que deja margen de memoria.

## 1. Lenguaje: Python

Confirmado por el usuario y adecuado: ecosistema maduro para RAG, embeddings,
PostgreSQL y scraping. No hay motivo de peso para otro lenguaje. Las partes
realmente exigentes en CPU (inferencia, embeddings) las ejecutan binarios
nativos (`llama.cpp`, ONNX Runtime), así que el "ser interpretado" de Python no
es el cuello de botella.

## 2. Motor de inferencia: llama.cpp (`llama-server`)

**Elegido.** Es el estándar para correr LLM cuantizados en CPU ARM; compila
nativo con NEON y rinde lo máximo posible en RPi. Su `llama-server` expone una
API HTTP compatible OpenAI, lo que desacopla el modelo del código de la API.

Alternativas descartadas:
- **Ollama**: cómodo, pero por debajo usa llama.cpp añadiendo una capa de
  gestión y algo más de RAM/IO. En 4 GB preferimos el control directo y el
  mínimo overhead. (Se puede adoptar más adelante si se valora la comodidad.)
- **Frameworks Python pesados** (transformers + torch): inviables en 4 GB para
  inferencia.

El modelo es **dinámico vía `LLM_MODEL_PATH`**: cumple el requisito de poder
cambiarlo (p. ej. al migrar a RPi5) sin tocar código.

## 3. Modelo LLM por defecto: Qwen2.5-1.5B-Instruct (Q4_K_M)

**Razonamiento.** En 4 GB conviven SO + PostgreSQL + embeddings + servidor LLM.
Un modelo 3B Q4 (~2,2 GB sólo de pesos, +contexto) deja el sistema al límite y
con riesgo de OOM. Un **1.5B Q4_K_M (~1,1 GB)** deja margen, responde más rápido
(clave con el tope de tiempo) y mantiene calidad suficiente para respuestas
breves y guiadas por RAG (el contexto recuperado hace gran parte del trabajo).

- **Familia elegida: Qwen2.5-Instruct.** Buen rendimiento en español entre los
  modelos pequeños y disponibilidad de GGUF y de tamaños (0.5B/1.5B/3B) para
  escalar por env.
- **Por defecto en 4 GB:** `qwen2.5-1.5b-instruct-q4_k_m`.
- **Opción de calidad (RPi5/8 GB o si la RAM lo permite):**
  `qwen2.5-3b-instruct-q4_k_m`. Solo cambia `LLM_MODEL_PATH`.
- **Alternativas válidas a evaluar:** Gemma 2 2B, Llama 3.2 3B. Se documentan,
  pero Qwen2.5 es el punto de partida.

> El modelo no es una decisión irreversible: el diseño permite probar varios y
> quedarse con el que mejor responda en español dentro del presupuesto de RAM.

Cuantización: **Q4_K_M** como equilibrio estándar tamaño/calidad para CPU.

## 4. Embeddings: multilingual-e5-small (384 dim) vía fastembed

**Razonamiento.** Para "solo español" no necesitamos un modelo multilingüe
grande. `multilingual-e5-small` es muy ligero, rinde bien en español y produce
vectores de **384 dimensiones**: índice más pequeño, búsqueda más rápida y menos
RAM que alternativas de 768+ dim (p. ej. BGE-M3, 568M, demasiado para esta Pi).

- **Ejecución vía fastembed (ONNX Runtime):** ligero en CPU/ARM, sin arrastrar
  torch.
- **Dimensión configurable** (`EMBEDDING_DIM`): cambiar de modelo obliga a
  reindexar.
- **Mejora opcional de calidad** si sobra margen: `jina-embeddings-v2-base-es`
  (especializado en español, 768 dim) — más pesado, se deja documentado.

La familia e5 exige prefijos `query:` / `passage:`; se gestionan desde env.

## 5. Base vectorial: PostgreSQL + pgvector

**Confirmado por el usuario** (PostgreSQL en el directorio de trabajo) y es buena
elección: una sola tecnología para datos relacionales (metadatos, fuentes,
auditoría) y vectores, sin sumar otro servicio (FAISS/Qdrant) a la RAM.

- **Clúster local** inicializado en `data/postgres` (autocontenido).
- **Índice:** con un corpus pequeño (previsiblemente miles de fragmentos, no
  millones) la **búsqueda exacta** o un índice **IVFFlat** ligero bastan y
  evitan el alto consumo de RAM de HNSW. HNSW solo si el corpus crece mucho.
- **Tuning:** `shared_buffers` bajo (p. ej. 128 MB) para no comerse la RAM del
  LLM.

## 6. API: FastAPI + Uvicorn (1 worker)

Aunque el usuario propuso Flask, se recomienda **FastAPI** por motivos
concretos, manteniendo la simplicidad:
- **Validación con pydantic** del contrato JSON de entrada y salida (importante
  porque "siempre devuelve JSON" con formato estricto).
- **Espera asíncrona** sobre la llamada HTTP a `llama-server` (peticiones
  largas, hasta minutos) sin bloquear el proceso.
- **OpenAPI** automático para que los clientes externos integren fácil.

Es tan simple de operar como Flask. Concurrencia: **1 worker + semáforo de 1
inferencia**; la inferencia es CPU-bound y secuencial, así protegemos la RAM.
(Flask sigue siendo viable; la diferencia es comodidad y validación, no un
bloqueo.)

## 7. Despliegue: nativo + systemd (sin Docker)

**Elegido por el usuario y técnicamente correcto en 4 GB.** Docker añade consumo
de RAM y capas (especialmente con PostgreSQL en contenedor) que penalizan en
hardware tan ajustado. Con systemd:
- Cada servicio es una unidad (`llama-server`, `postgresql-local`, `bot-api`,
  `context-updater`), con arranque automático y dependencias declaradas.
- Reinicio automático ante fallo y recuperación tras corte de luz.

## 8. Tabla resumen

| Capa | Elección | Alternativa documentada |
|------|----------|-------------------------|
| Lenguaje | Python | — |
| Inferencia | llama.cpp (`llama-server`) | Ollama |
| Modelo (4 GB) | Qwen2.5-1.5B-Instruct Q4_K_M | Qwen2.5-3B (RPi5), Gemma 2 2B, Llama 3.2 3B |
| Embeddings | multilingual-e5-small (384d, fastembed) | jina-embeddings-v2-base-es |
| Vector store | PostgreSQL + pgvector (local) | FAISS/Qdrant (no, +RAM) |
| Índice ANN | Exacto / IVFFlat | HNSW (solo si crece) |
| API | FastAPI + Uvicorn | Flask |
| Despliegue | Nativo + systemd | Docker (no, +RAM) |

## 9. Fuentes consultadas (estado del arte, jun-2026)

- Best Small Language Models 2026 — localaimaster.com
- Best Open Source LLMs for Raspberry Pi in 2026 — siliconflow.com
- Qwen — llama.cpp quantization (Q4_K_M / Q8_0) — qwen.readthedocs.io
- The Best Open-Source Embedding Models in 2026 — bentoml.com
- Best Embedding Model for RAG 2026 — milvus.io
- HNSW Indexes with Postgres and pgvector — crunchydata.com
