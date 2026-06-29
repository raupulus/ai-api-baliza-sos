# Módulo 04 · API del bot

## Resumen

El servicio que atienden los clientes externos (Telegram/Meshtastic). Expone un
endpoint HTTP con **FastAPI**, valida la petición, ejecuta el pipeline RAG → LLM,
**post-procesa la respuesta al formato 250×3** y devuelve **siempre un JSON**
conforme al contrato. Implementa autenticación por token, control de
concurrencia (semáforo de 1 inferencia), límites de tiempo y avisos médicos.
Es el ensamblaje de los módulos 02 y 03 en un servicio operable.

Dependencias: 01, 02, 03. Habilita: Hito B y 07.

## Fase 1 — Esqueleto FastAPI (`src/api/app.py`)

- App FastAPI + Uvicorn (1 worker). Arranque desde config de `env.py`.
- Middleware de autenticación: cabecera `Authorization: Bearer API_AUTH_TOKEN`.
- Healthcheck `GET /health` (estado de BD, llama-server, embeddings).
- Modelos pydantic de petición/respuesta según `docs/info/05-contratos-datos.md`.

## Fase 2 — Endpoint de consulta (`POST /v1/consulta`)

- Validar y normalizar la entrada (texto no vacío, longitud máxima sensata).
- Orquestar el pipeline: embed → recuperar → construir contexto → generar.
- Devolver el JSON de respuesta con `mensajes`, `categoria`, `confianza`,
  `fuentes`, `modelo`, `tiempo_ms`, `truncado`.

## Fase 3 — Prompt y generación

- Plantilla de prompt (esquema en `docs/info/05-contratos-datos.md`):
  reglas de brevedad, español, "usa solo el contexto", no inventar.
- Llamar al cliente LLM (módulo 02) con parámetros de generación y timeout.
- Inyectar la `PROVINCIA` y el contexto recuperado.

## Fase 4 — Post-proceso a 250×3

- Función que toma la salida cruda del LLM y la convierte en **1–3 mensajes de
  ≤ 250 caracteres**: limpieza, corte por frases, segmentación inteligente.
- Preferir 1 mensaje; pasar a 2–3 solo si no cabe.
- Marcar `truncado: true` si se descartó contenido.
- Añadir el aviso (`RESP_DISCLAIMER_MEDICO`) en categorías médicas/riesgo.

## Fase 5 — Concurrencia, tiempos y errores

- Semáforo `API_MAX_CONCURRENT_INFERENCES` (=1): solo una inferencia a la vez;
  el resto espera en cola.
- Timeout de generación (`LLM_TIMEOUT_SECONDS`) por debajo del límite del
  cliente (5 min) → respuesta de error controlada si se excede.
- Mapeo de errores a JSON (`ok:false`, código, detalle) y a HTTP apropiado.
- Caso "sin contexto suficiente": responder con cautela, nunca inventar.

## Fase 6 — Documentación y pruebas de la API

- OpenAPI/Swagger disponible para los integradores de clientes.
- Ejemplos de petición/respuesta por categoría.
- Pruebas: validación de entrada, formato de salida (límite 250×3), camino sin
  contexto, timeout simulado, auth fallida.

## Verificación del módulo

- Petición real end-to-end devuelve JSON válido y dentro de 250×3.
- Auth obligatoria funciona (rechaza sin token).
- Bajo dos peticiones simultáneas, la segunda espera (no se duplica inferencia).
- Se respeta el timeout.

## Checklist

> Leyenda de estado (autogenerada en la fase de implementación): [x] = terminado en código y verificado en sandbox · [ ] = pendiente de ejecutar en la Raspberry Pi o con BD/red en vivo (compilar llama.cpp en ARM, descargar modelo, levantar PostgreSQL, pruebas de integración).


- [x] Fase 1: app FastAPI con auth por token y `GET /health`.
- [x] Fase 1: modelos pydantic de petición/respuesta.
- [x] Fase 2: `POST /v1/consulta` orquesta el pipeline completo.
- [x] Fase 3: plantilla de prompt con reglas de brevedad y no-inventar.
- [x] Fase 3: integración con el cliente LLM y `PROVINCIA`.
- [x] Fase 4: post-proceso a 1–3 mensajes ≤ 250 caracteres.
- [x] Fase 4: aviso médico añadido según categoría.
- [x] Fase 4: flag `truncado` correcto.
- [x] Fase 5: semáforo de 1 inferencia.
- [x] Fase 5: timeout de generación y errores en JSON.
- [x] Fase 5: respuesta cautelosa sin contexto suficiente.
- [x] Fase 6: OpenAPI y ejemplos por categoría.
- [x] Fase 6: pruebas de entrada/salida/auth/timeout.
- [ ] Verificación: end-to-end correcto y concurrencia serializada.
