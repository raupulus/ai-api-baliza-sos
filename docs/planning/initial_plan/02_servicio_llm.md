# Módulo 02 · Servicio LLM (llama.cpp)

## Resumen

Pone a funcionar la inferencia local: compilar **llama.cpp** nativo para ARM,
gestionar la descarga de modelos **GGUF**, levantar **`llama-server`** con el
modelo indicado por `LLM_MODEL_PATH` y exponerlo en localhost para que la API lo
consuma. Incluye healthcheck, tuning de hilos/contexto y el mecanismo de
**cambio de modelo por variable de entorno**. Al terminar, la Pi genera texto
con un modelo pequeño en español dentro del presupuesto de RAM.

Dependencias: 01. Habilita: 03 (para reranking opcional) y 04.

## Fase 1 — Compilación de llama.cpp para ARM

- Clonar y compilar llama.cpp con optimizaciones ARM/NEON para RPi (flags de
  CPU adecuados). Documentar la versión/commit fijado.
- Verificar el binario `llama-server` y `llama-cli`.
- Decidir ubicación de binarios (p. ej. `vendor/llama.cpp/` o ruta del sistema)
  y documentarla.

## Fase 2 — Gestión de modelos GGUF

- `scripts/download_model.sh`: descarga el GGUF a `models/` (ignorado por git)
  con verificación de hash/tamaño.
- Modelo por defecto: `qwen2.5-1.5b-instruct-q4_k_m`. Documentar también la
  variante 3B para hardware mayor.
- Catálogo de modelos soportados (tabla: nombre, tamaño, RAM aprox., uso
  recomendado) en este doc o en `docs/info`.

## Fase 3 — Servicio `llama-server`

- Unidad systemd `llama-server.service` que arranca `llama-server` con:
  `--model $LLM_MODEL_PATH`, `--threads $LLM_THREADS`,
  `--ctx-size $LLM_CONTEXT_SIZE`, host/puerto de `env.py`, y flags de memoria.
- `EnvironmentFile` apuntando a la config (o exportación desde `env.py`).
- Reinicio automático ante fallo; arranque tras `postgresql-local` no es
  necesario, pero sí antes de `bot-api`.

## Fase 4 — Cliente LLM en el código (`src/common` o `src/api`)

- Cliente HTTP fino hacia `llama-server` (endpoint compatible OpenAI):
  parámetros de generación desde config, `timeout=LLM_TIMEOUT_SECONDS`.
- Manejo de errores: timeout, servidor caído, respuesta vacía → error
  controlado que la API convierte en JSON de error.
- Función de **healthcheck** del modelo (carga/responde).

## Fase 5 — Cambio dinámico de modelo

- Procedimiento documentado: editar `LLM_MODEL_PATH` en `env.py` →
  `systemctl restart llama-server`. Sin cambios de código.
- Validación: si el fichero no existe, fallo claro al arrancar la unidad.
- Probar con al menos dos modelos (1.5B y, si hay hardware, 3B) y registrar
  tiempos/RAM observados.

## Verificación del módulo

- `llama-server` responde a una petición de prueba con el modelo por defecto.
- Medir RAM y tokens/seg reales en la Pi; contrastar con el presupuesto.
- Probar el cambio de modelo vía env.
- Healthcheck integrable por systemd/script.

## Checklist

- [ ] Fase 1: llama.cpp compilado para ARM, versión fijada y documentada.
- [ ] Fase 1: binarios `llama-server`/`llama-cli` verificados.
- [ ] Fase 2: `download_model.sh` con verificación de integridad.
- [ ] Fase 2: modelo por defecto (1.5B Q4_K_M) descargado.
- [ ] Fase 2: catálogo de modelos documentado.
- [ ] Fase 3: `llama-server.service` arranca con parámetros de `env.py`.
- [ ] Fase 3: reinicio automático ante fallo configurado.
- [ ] Fase 4: cliente HTTP del LLM con timeout y manejo de errores.
- [ ] Fase 4: healthcheck del modelo.
- [ ] Fase 5: procedimiento de cambio de modelo probado (≥1 alternativo).
- [ ] Fase 5: validación de ruta de modelo inexistente.
- [ ] Verificación: RAM y velocidad reales medidas y anotadas.
