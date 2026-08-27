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
- **Documentación técnica obligatoria en `docs/info/` y `docs/rag/`.** Cualquier
  cambio arquitectónico, de configuración, de endpoints o de fuentes de conocimiento
  debe quedar documentado obligatoria e inmediatamente en su directorio respectivo.
  Es una regla estricta: `docs/info/` y `docs/rag/` son las fuentes únicas de verdad.

## 3. Guía de Navegación de Documentación para Agentes

Para optimizar el uso de contexto y mantener la consistencia técnica, los agentes deben
consultar **únicamente el archivo específico** que corresponda a la tarea en curso:

### A. Documentación Técnica (`docs/info/`)
Abrir **solo** el archivo relacionado con el módulo que se va a consultar o modificar:
* **`docs/info/01-vision-requisitos.md`** → Visión de producto, casos de uso, restricciones LoRa/RF y premisas de diseño.
* **`docs/info/02-arquitectura.md`** → Diagramas de contenedores Docker, red `bot-net`, flujo entre servicios y puertos (`8869`, `8870`, `8443`, `5433`).
* **`docs/info/03-decisiones-stack.md`** → Justificación técnica de `llama.cpp`, fastembed, PostgreSQL + pgvector y FastAPI.
* **`docs/info/04-presupuesto-recursos.md`** → Límites de memoria RAM, control de inferencia concurrente (semáforo) y presupuesto térmico.
* **`docs/info/05-contratos-datos.md`** → Esquemas internos de dominio (`Fragmento`, `Categoria`), tablas relacionales (`conversaciones`, `mensajes_conversacion`) y hashes de contenido.
* **`docs/info/06-estado-implementacion.md`** → Matriz de estado de módulos y checklist de tareas completadas.
* **`docs/info/07-hardware-objetivo.md`** → Ficha técnica del hardware (RPi4 / RPi5 8GB), flags de CPU, NPU Hailo-8 y almacenamiento SSD.
* **`docs/info/08-contrato-api.md`** → Contrato formal de integración HTTP REST (`/v1/consulta`, `/v1/conversacion/reset`, `/health`), cabeceras Bearer, formatos JSON y ejemplos cURL/Python/JS.

### B. Especificación de Fuentes de Conocimiento del RAG (`docs/rag/`)
Cuando se trabaje con **datos, ingesta, vectorización o ampliación de conocimiento**,
acudir obligatoriamente a este directorio:
* **`docs/rag/README.md`** → Metodología general, flujo de ingesta manual y registro maestro de fuentes.
* **`docs/rag/PLANTILLA_FUENTE.md`** → Plantilla estándar que debe cumplimentarse antes de incorporar cualquier fuente nueva.
* **`docs/rag/primeros-auxilios.md`** → Protocolos médicos y de supervivencia (Cruz Roja, SEMES, Protección Civil).
* **`docs/rag/flora-fauna.md`** → Plantas tóxicas, setas venenosas, flora comestible y fauna peligrosa de Cádiz (REDIAM).
* **`docs/rag/municipios-geografia.md`** → Los 45 municipios de Cádiz con coordenadas GPS WGS84 oficiales y cumbres (IGN/IECA).
* **`docs/rag/fiestas-tradiciones.md`** → Festividades populares, carnavales, ferias y romerías (Patronato de Turismo).
* **`docs/rag/historia-patrimonio.md`** → Hitos históricos de Cádiz: Gadir, época romana, 1812, Trafalgar (IAPH).
* **`docs/rag/overpass-osm.md`** → Farmacias, centros sanitarios y fuentes de agua potable (OpenStreetMap).
* **`docs/rag/wikidata.md`** → Hospitales, faros y entidades territoriales de Cádiz (Wikidata SPARQL).
* **`docs/rag/gbif.md`** → Presencia biológica georreferenciada en el BBOX provincial (GBIF).

### C. Protocolo de Lectura Just-in-Time
Para optimizar el uso de contexto y no saturar la ventana de conversación:
- **No leer proactivamente archivos completos de documentación** salvo que sea estrictamente necesario para la tarea actual.
- Utilizar `view_file` especificando rangos acotados de líneas (`StartLine` y `EndLine`) o herramientas de búsqueda puntual (`grep_search`, `find_by_name`).
- Si solo necesitas consultar un endpoint, consulta exclusivamente `docs/info/08-contrato-api.md`. Si solo necesitas una fuente, consulta únicamente su archivo en `docs/rag/`.

## 4. Configuración

- La config real vive en **`env.py`** y **`.env`** (NO trackeados). La plantilla es
  **`env.example.py`** (trackeada). Cualquier variable nueva se añade primero a
  `env.example.py` con un valor por defecto y un comentario.
- El código accede a la config **solo** vía `src/common/config.py`. No leer
  `os.environ` ni importar `env.py` directamente desde otros módulos.

## 5. Estructura del repositorio

```
src/
  common/     Config, conexión a BD, logging, modelos de datos compartidos.
  api/        Servicio del bot (FastAPI): endpoints, pipeline RAG, memoria multi-turno, post-proceso.
  api/rag/    Embeddings, recuperación vectorial, construcción de contexto.
  updater/    Servicio actualizador: orquestación, normalización y staging.
  updater/sources/  Módulos conectores por cada fuente de datos.
  web/        Servidor y frontend de pruebas web local (chat interactivo).
docs/info/    Documentación técnica y decisiones de arquitectura (8 archivos).
docs/rag/     Fichas y especificaciones de las fuentes de conocimiento del RAG.
docs/planning/  Planificación activa y archivo histórico (archive/).
deploy/postgres/ Migraciones SQL (`0001_init.sql`, `0002_conversaciones.sql`).
scripts/      Utilidades de operación (`actualizar_fuente.py`, `test_e2e.py`, `exportar_conversaciones.py`...).
tests/        Pruebas automatizadas unitarias y de integración.
CHANGELOG.md  Registro histórico formal de versiones (Keep a Changelog).
Makefile      Comandos rápidos de gestión, despliegue y testing.
```

## 6. Stack acordado (resumen)

- **Inferencia LLM:** `llama.cpp` (`llama-server`) en puerto `8869`, modelo Qwen2.5-3B-Instruct Q4_K_M.
- **Embeddings:** `fastembed` con `paraphrase-multilingual-MiniLM-L12-v2` (384 dimensiones).
- **Base vectorial:** PostgreSQL 17 + **pgvector** en puerto `5433` (interno `5432`).
- **API Backend:** FastAPI + Uvicorn en puerto `8870` (1 worker, semáforo de 1 inferencia pesada concurrente).
- **Web UI:** Servidor FastAPI en puerto `8443` con interfaz de chat para validación previa.
- **Despliegue:** Contenedores Docker orquestados con `docker-compose.yml`.

## 7. Flujo de trabajo para implementar

1. Localiza el módulo en `docs/info/` o en `docs/planning/`.
2. Sigue las **fases en orden**; respeta las dependencias entre módulos.
3. Si tocas el RAG, consulta y actualiza la ficha correspondiente en `docs/rag/`.
4. Si tocas arquitectura, endpoints o configuración, actualiza `docs/info/`.
5. Al completar una tarea o plan, añade pruebas mínimas y mantén los commits descriptivos.
6. **Actualización Obligatoria de Planificación:** Al terminar de implementar un plan, es imperativo actualizar `docs/info/06-estado-implementacion.md` y documentar los cambios en `CHANGELOG.md`.

## 8. Convenciones de código

- Estilo: PEP 8, formateo con `ruff`/`black`, tipos con anotaciones.
- Logging por el helper de `src/common`, nunca `print` en servicios.
- Sin secretos en el repo. Todo secreto va a `.env` / `env.py`.
- Toda llamada de red en el `updater` respeta `UPDATER_USER_AGENT`, rate limits
  y la licencia de la fuente.

## 9. Estado actual
 
**Backend Docker y Memoria Conversacional Operativos.**
- Servicios centrales containerizados (`bot-api`, `bot-llm`, `bot-db`, `bot-web`).
- Memoria conversacional multi-turno persistente en PostgreSQL (ventana de 20 turnos con compactación por IA y TTL de 1 hora de inactividad).
- Prompt calibrado para triaje de emergencias y primeros auxilios sin rechazos prematuros.
- Corpus RAG ampliado con 89 fragmentos locales de Cádiz (médico, flora/fauna, 45 municipios con coordenadas WGS84, fiestas e historia).
- Script de actualización manual bajo demanda: `python3 scripts/actualizar_fuente.py`.

