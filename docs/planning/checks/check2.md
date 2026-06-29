# Informe de Revisión 2 (check2.md)

## 1. Verificación de problemas anteriores

Se ha comprobado exhaustivamente el código para garantizar la resolución de los bloqueos detectados en la primera revisión.

- **Bloqueos síncronos en FastAPI (embeddings, DB, LLM)**: **Resuelto**. Las llamadas bloqueantes (`retrieval.buscar()`, `construir_contexto()` y `llm.generate()`) se han agrupado en la función `_procesar_sync` que es enviada correctamente a un worker a través de `await run_in_threadpool()`. El Event Loop de `uvicorn` queda libre para seguir aceptando peticiones, manejar el endpoint `/health` y encolar a los demás clientes sin sufrir interrupciones. El propio `/health` usa `run_in_threadpool` para el testeo a DB y LLM.
- **Protección completa de RAM (Semáforo de Inferencia)**: **Resuelto**. El semáforo global `inference_semaphore` restringe la ejecución estricta a una sola inferencia a la vez (por defecto), cubriendo tanto la vectorización por CPU (`fastembed`) como la llamada a `llama-server`. Esta serialización elimina los picos de memoria (OOM). A nivel de sistema, `llama-server.service` usa `OOMScoreAdjust=-200` y `LLM_CONTEXT_SIZE` acotados.
- **Retries del LLM**: **Resuelto**. `LLMClient` en `llm_client.py` ahora implementa un bucle explícito que captura `httpx.ConnectError` y realiza reintentos con *backoff* exponencial. Los errores de timeout (`TimeoutException`) no se reintentan, lo cual es la decisión arquitectónica correcta dado que las consultas pueden durar bastante y se violarían los SLA de respuesta de los clientes.
- **Healthcheck Ligero**: **Resuelto**. Se evalúa el endpoint real de llama-server y la DB, pero se evita instanciar/cargar en memoria el modelo de embeddings (pesado). En su lugar, comprueba que la librería es importable, lo cual ahorra muchísimos recursos valiosos de la Raspberry.
- **Validación de Token de Seguridad**: **Resuelto**. Usa `secrets.compare_digest` para la cabecera `Authorization` evitando ataques de temporización (timing attacks). Rechaza operar en modo productivo si detecta un token por defecto inseguro.

## 2. Nuevos hallazgos, inconsistencias y vulnerabilidades (Coste/Beneficio)

Aunque el pipeline general y el soporte asíncrono son excelentes, he detectado un fallo arquitectónico importante en cómo se comunica con el LLM, además de un par de mejoras menores de robustez.

### A. Incompatibilidad del Prompt con la Plantilla del Modelo (ChatML) - *Prioridad Alta*
- **El Problema**: El modelo seleccionado (`Qwen2.5-1.5B-Instruct`) es un modelo de "instrucción" fuertemente afianzado a la plantilla **ChatML** (`<|im_start|>system...`). Actualmente, el código en `api/llm_client.py` apunta a `/completion` (endpoint legacy crudo) y le manda texto plano con `[SISTEMA]...[CONSULTA]...[RESPUESTA]` (definido en `prompt.py`).
- **Impacto**: Ignorar la plantilla nativa del modelo dispara el riesgo de alucinaciones, respuestas que no paran de generar texto (fallo al obedecer el `stop token` de ChatML) o respuestas de bajísima calidad, desperdiciando ciclos de CPU.
- **Solución**: Usar el endpoint `/v1/chat/completions` (que `llama-server` soporta plenamente). Modificar `llm_client.py` para mandar un JSON con `"messages": [{"role": "system", "content": ...}, {"role": "user", "content": ...}]` y dejar que `llama-server` se encargue de aplicar la plantilla ChatML. Coste de desarrollo: muy bajo. Beneficio: inmenso en la calidad de respuesta.

### B. Condición de carrera (Race Condition) en carga de Embeddings - *Prioridad Media*
- **El Problema**: En `src/api/rag/embeddings.py`, el método `Embedder._ensure_model()` no está bajo la protección del hilo principal (el candado `_lock` solo protege la instancia del singleton, no su variable `self._model`). 
- **Impacto**: Con el semáforo a 1 petición concurrente, esto es seguro de facto. Pero si en el futuro se aumenta la concurrencia a `API_MAX_CONCURRENT_INFERENCES = 2` (ej. en una RPi5 de 8GB), dos hilos del threadpool podrían llegar a la vez, instanciar simultáneamente `TextEmbedding`, colisionar y consumir el doble de RAM (OOM de la Raspberry Pi).
- **Solución**: Añadir `with self._lock:` dentro de `_ensure_model()` justo antes de instanciar `TextEmbedding(model_name=...)`. Prevención total contra condiciones de carrera.

### C. Falta de cierre elegante del Pool de PostgreSQL - *Prioridad Baja*
- **El Problema**: `psycopg_pool` se inicializa dinámicamente y se usa durante la vida útil del worker. Sin embargo, no hay un hook de apagado (`shutdown`) en la aplicación.
- **Impacto**: Cuando `bot-api.service` se reinicia, se cortan las conexiones de forma abrupta, lo cual en un entorno PostgreSQL de largo uso ensucia el log y puede bloquear recursos transitoriamente.
- **Solución**: En `src/api/app.py`, añadir un `@app.on_event("shutdown")` que invoque a `close_pool()` de `src/common/db.py`.
