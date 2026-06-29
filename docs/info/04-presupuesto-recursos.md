# 04 · Presupuesto de recursos (RAM en RPi4 4 GB)

El recurso crítico es la **RAM**. Este documento fija un presupuesto y las
medidas para no superarlo. Es la referencia para validar cualquier decisión
técnica: *si algo no cabe aquí, no entra*.

## 1. Presupuesto estimado (modelo por defecto 1.5B)

| Componente | RAM aproximada | Notas |
|------------|---------------:|-------|
| Raspberry Pi OS Lite (sin escritorio) | 250–400 MB | Usar la edición **Lite**. |
| PostgreSQL + pgvector | 150–300 MB | `shared_buffers` ~128 MB, pocas conexiones. |
| Embeddings (e5-small, ONNX) | 250–450 MB | Cargado en el proceso que lo use. |
| llama-server con Qwen2.5-1.5B Q4_K_M | 1.3–1.8 GB | Pesos (~1.1 GB) + KV-cache del contexto. |
| API FastAPI/Uvicorn (1 worker) | 100–200 MB | Sin contar embeddings. |
| Margen / buffers del SO | resto | Imprescindible para estabilidad. |
| **Total estimado** | **~2.3–3.1 GB** | Deja margen en 4 GB. |

Con un **3B Q4_K_M** el llama-server sube a ~2.5–3.0 GB y el total se acerca o
supera los 4 GB → **no recomendado como defecto en 4 GB**; reservar para RPi5/8 GB.

## 2. Medidas para no pasarse

1. **Raspberry Pi OS Lite** (sin entorno gráfico).
2. **Una sola inferencia a la vez** (semáforo en la API). Nunca dos modelos
   generando en paralelo.
3. **Contexto LLM acotado** (`LLM_CONTEXT_SIZE=2048`): el KV-cache crece con el
   contexto; mantenerlo pequeño ahorra cientos de MB.
4. **Embeddings ligeros** (384 dim) y cargados una sola vez.
5. **PostgreSQL afinado**: `shared_buffers`, `work_mem` y `max_connections`
   bajos. Índice IVFFlat/exacto en vez de HNSW para no inflar memoria.
6. **El actualizador no corre durante picos de la API**: se programa aparte
   (systemd timer, p. ej. de madrugada). El scraping/embeddings masivo de la
   ingesta es lo más caro y no debe coincidir con consultas.
7. **zram / swap controlado** como red de seguridad ante picos, no como sustento.
8. **Sin Docker**: se evita el overhead de contenedores.

## 3. CPU y tiempos

- RPi4: 4 núcleos → `LLM_THREADS=4`.
- En CPU, un 1.5B Q4 genera del orden de unos pocos tokens/segundo. Para una
  respuesta de ~300 tokens, el orden de magnitud es de decenas de segundos,
  **dentro del límite de 5 minutos** del cliente. El 3B es bastante más lento.
- Se fija `LLM_MAX_TOKENS` bajo (respuestas breves) para acotar el tiempo.
- La API impone un timeout de generación (`LLM_TIMEOUT_SECONDS`) por debajo del
  límite del cliente para fallar de forma controlada.

## 4. Almacenamiento

- **Tarjeta SD de calidad o, mejor, SSD USB**: PostgreSQL y los modelos sufren
  con SD lentas/baratas. El clúster vive en `data/postgres`.
- Tamaño: modelos GGUF (~1–3 GB cada uno) + BD (modesta) + staging. Prever
  varios GB libres.

## 5. Escalado a hardware mayor (RPi5 / 8 GB)

Sin cambios de código:
- `LLM_MODEL_PATH` → modelo 3B (o mayor) Q4_K_M.
- Subir `LLM_THREADS` y, si interesa, `LLM_CONTEXT_SIZE`.
- Opcional: embeddings de 768 dim (jina-es) reindexando el corpus.
- Opcional: índice HNSW en pgvector si el corpus ha crecido mucho.
