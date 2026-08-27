# AGENTS.md — Guía para agentes de IA y colaboradores

Este archivo orienta a cualquier agente de IA (o persona) que trabaje en el
repositorio. Léelo antes de proponer o escribir código.

## 1. Qué es este proyecto

Backend de un **asistente de emergencia/supervivencia offline** para la
provincia de **Cádiz (España)**, pensado para ejecutarse en una **Raspberry Pi
4 (4 GB)** sin conexión a internet en operación. Responde consultas de IA
(modelo LLM pequeño local + RAG) que llegan desde clientes externos
(bots de Telegram y, sobre todo, **Meshtastic/LoRa**).

Este repositorio contiene **solo el backend**. Los clientes (Telegram,
Meshtastic) viven en otros proyectos y consumen la API HTTP.

Se compone de **dos servicios independientes**:

1. **API del bot** (`src/api`): recibe la consulta, recupera contexto del RAG,
   llama al LLM local y devuelve **siempre un JSON** con la respuesta breve
   (máx. 250 caracteres × máx. 3 mensajes).
2. **Actualizador de contexto** (`src/updater`): ingesta y scraping de fuentes
   (fauna, geografía, primeros auxilios, supervivencia), normalización al
   formato de fragmento del RAG, **checkpoint humano** y volcado a la base
   vectorial.

## 2. Principios de diseño (no negociables)

- **Lenguaje: Python.** No introducir otro lenguaje sin un motivo de peso
  documentado y acordado.
- **Objetivo Linux.** Solo Linux; foco en **Raspberry Pi OS** (última versión).
  No escribir código condicional para Windows/macOS.
- **Hardware mínimo: RPi4 4 GB.** Cada decisión debe respetar el presupuesto de
  RAM (ver `docs/info/04-presupuesto-recursos.md`). Si algo no cabe, no entra.
- **Modelo LLM dinámico.** El modelo se elige por variable de entorno
  (`LLM_MODEL_PATH`). Nunca hardcodear un modelo en el código.
- **Provincia parametrizable.** Todo lo geográfico sale de `env.py` (`PROVINCIA`,
  `BBOX`, etc.). Cambiar de provincia = cambiar config, no código.
- **Respuestas breves y en español.** Formato fijo: JSON con lista de mensajes,
  cada uno ≤ 250 caracteres, máximo 3.
- **Seguridad del contenido.** El contenido médico y de especies peligrosas
  **requiere validación humana** antes de indexarse. Nunca generar protocolos
  médicos a partir de scraping no verificado.
- **Documentación técnica obligatoria en `docs/info/`.** Cualquier cambio
  arquitectónico, de configuración, de puertos, de endpoints o de stack técnico
  debe quedar documentado obligatoria e inmediatamente en `docs/info/`.
  Es una regla estricta: `docs/info/` es la fuente única de verdad del proyecto.

## 3. Configuración

- La config real vive en **`env.py`** (NO trackeado). La plantilla es
  **`env.example.py`** (trackeada). Cualquier variable nueva se añade primero a
  `env.example.py` con un valor por defecto y un comentario.
- El código accede a la config **solo** vía `src/common/config.py`. No leer
  `os.environ` ni importar `env.py` directamente desde otros módulos.

## 4. Estructura del repositorio

```
src/
  common/     Config, conexión a BD, logging, modelos de datos compartidos.
  api/        Servicio del bot (FastAPI): endpoints, pipeline RAG, post-proceso.
  api/rag/    Embeddings, recuperación, construcción de contexto.
  updater/    Servicio actualizador: orquestación, normalización, checkpoint.
  updater/sources/  Un módulo por fuente de datos (GBIF, Overpass, AEMET...).
docs/info/            Documentación técnica y decisiones de arquitectura.
docs/planning/        Planificación por módulos (fases + checklists).
deploy/systemd/       Unidades systemd de cada servicio.
deploy/postgres/      Scripts de init del clúster local y del esquema.
scripts/              Utilidades de operación (init, descarga de modelos...).
tests/                Pruebas.
data/                 Directorio de trabajo (BD, staging, modelos). NO trackeado.
```

## 5. Stack acordado (resumen)

- **Inferencia LLM:** `llama.cpp` (`llama-server`), compilado nativo para ARM.
- **Modelo por defecto (4 GB):** Qwen2.5-1.5B-Instruct Q4_K_M. Alternativa en
  hardware mayor: Qwen2.5-3B-Instruct.
- **Embeddings:** `multilingual-e5-small` (384 dim) vía fastembed/ONNX.
- **Base vectorial:** PostgreSQL + **pgvector** (clúster local en `data/`).
- **API:** FastAPI + Uvicorn (1 worker, semáforo de 1 inferencia).
- **Despliegue:** nativo con **systemd** (sin Docker).

Justificación detallada en `docs/info/03-decisiones-stack.md`.

## 6. Flujo de trabajo para implementar

1. Localiza el módulo en `docs/planning/initial_plan/`.
2. Sigue las **fases en orden**; respeta las dependencias entre módulos.
3. Al completar una tarea, **marca su casilla** en el checklist del módulo.
4. Añade pruebas mínimas y actualiza la doc afectada en `docs/info/`.
5. Mantén los commits pequeños y descriptivos.

## 7. Convenciones de código

- Estilo: PEP 8, formateo con `ruff`/`black`, tipos con anotaciones.
- Logging por el helper de `src/common`, nunca `print` en servicios.
- Sin secretos en el repo. Todo secreto va a `env.py`.
- Toda llamada de red en el `updater` respeta `UPDATER_USER_AGENT`, rate limits
  y la licencia de la fuente.

## 8. Estado actual
 
**Backend y despliegue Docker operativos.** Los servicios centrales (`bot-api`,
`bot-llm` con Qwen 2.5-3B, `bot-db` con PostgreSQL 17 + pgvector y `bot-web` para
pruebas) están containerizados en Docker y desplegados de forma autónoma. La
documentación técnica completa y contratos de API residen en `docs/info/`.
