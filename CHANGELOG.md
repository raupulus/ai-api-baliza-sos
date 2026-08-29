# Changelog

Todas las modificaciones notables de este proyecto se documentan en este archivo.
El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y se adhiere al versionado semántico.

---

## [0.6.0] - 2026-08-29

### Añadido
- **Telemetría de hardware en tiempo real vía WebSockets:** Endpoint `/ws/telemetry` en `src/web/server.py` y barra inferior fluida en `index.html` con CPU %, temperatura (°C), RAM % y Disco %.
- **Banco jerárquico de pruebas RAG en 3 niveles:** Selector en cascada en la Web UI (Categoría ➔ Subcategoría / Tipo ➔ Caso concreto) para depuración y verificación exhaustiva de los 4.567 fragmentos.
- **Metadatos conversacionales en `ConsultaResponse` (retrocompatibles):** Inclusión de `turnos_memoria`, `compactado` y `fragmentos_rag` en la respuesta JSON.
- **Corpus RAG vectorizado e indexado en PostgreSQL:** 4.567 fragmentos activos en pgvector en la Raspberry Pi 5.

### Corregido
- **Calibración de límites en la Web UI:** Reemplazados los textos y contadores de 250 caracteres por medición estricta de **$\le 200$ bytes UTF-8** por mensaje mediante `TextEncoder`.

---

## [0.5.0] - 2026-08-28

### Añadido
- **Corpus RAG ampliado a 4474 fragmentos validados (0 pendientes)** en `data/staging/aprobados/`, organizados en 15 categorías: geografía 3216, supervivencia 661, transporte 449, directorios 54, orientación 28, fauna 25, primeros auxilios 17, protección civil 7, flora 6, apoyo psicosocial 5, legislación 2, toxicología 1, cultura/historia 1, clima 1 y agricultura 1. **Pendiente de ingesta/vectorización en la Raspberry Pi.**
- **Gobierno documental del RAG (`docs/rag/`):** 17 fichas temáticas + `PLANTILLA_FUENTE.md` + catálogo maestro, plan de adquisición, análisis del lote, auditoría de fuentes, checklist de validación humana y lecciones de adquisición.
- **Auditoría de fuentes (`scripts/auditar_urls.py`):** verificación de 103 URLs únicas, 5 fallos reales corregidos y checklist por ficha.
- **Política de validación:** auto-aprobación de fuentes oficiales (estado/UE) y sociedades científicas; revisión humana solo para contenido sensible de fuente externa.

### Modificado
- **`docs/info/06-estado-implementacion.md`:** añadido el estado del corpus en staging (4474 fragmentos preparados).
- **`docs/planning/dudas/rag.md`:** reducido a las dudas sin resolver (T22 Diputación, T3b REDIAM flora, B3 EUDA).
- **`docs/rag/README.md`:** añadido el resumen global del corpus y reconciliadas las cifras por ficha.

---

## [0.4.0] - 2026-08-27

### Añadido
- **Ampliación del Corpus RAG de Cádiz:**
  - 89 nuevos fragmentos validados organizados en 5 fuentes (`primeros-auxilios-avanzado`, `flora-fauna-cadiz`, `municipios-cadiz`, `fiestas-cadiz`, `historia-cadiz`).
  - Cobertura de los 45 municipios con coordenadas GPS oficiales WGS84, altitud y picos orográficos.
- **Herramienta de actualización manual (`scripts/actualizar_fuente.py`):** CLI para listar y actualizar fuentes bajo demanda sin automatizaciones en segundo plano.
- **Registro y especificación documental en `docs/rag/`:** Directorio con fichas técnicas individuales por fuente (`primeros-auxilios.md`, `flora-fauna.md`, `municipios-geografia.md`, `fiestas-tradiciones.md`, `historia-patrimonio.md`, `overpass-osm.md`, `wikidata.md`, `gbif.md`) y plantilla estándar `PLANTILLA_FUENTE.md`.
- **Suite de pruebas de integración E2E (`scripts/test_e2e.py`):** Comprobación en vivo de autenticación 401, formato de paquetes LoRa ($\le 250$ chars), memoria multi-turno y reseteo.
- **Script de exportación de historial (`scripts/exportar_conversaciones.py`):** Exportación de conversaciones a JSONL y CSV con filtros por cliente y fecha.
- **`Makefile` de operaciones:** Atajos para sincronización con Raspberry Pi, control Docker, tests y linters.
- **Tests unitarios:** `tests/test_memory.py` y `tests/test_sources_cadiz.py`.

### Modificado
- **Control Estricto de 230 Bytes UTF-8 para Meshtastic:** Adaptado el empaquetador de respuestas (`src/api/postprocess.py`) para medir longitudes en bytes UTF-8 en lugar de caracteres simples. Se fija el límite en $\le 230$ bytes UTF-8 para encajar sin riesgo en el buffer LoRa de Meshtastic (`Constants.DATA_PAYLOAD_LEN = 237 bytes`) con soporte para tildes y signos en español sin cortes de caracteres multibyte.
- **Triaje de Emergencias Activo:** Reformulado el prompt para evaluar de inmediato el estado físico de la víctima, aportar pautas de inmovilización/abrigo y referenciar puntos de auxilio para el 112, eliminando el rechazo prematuro.
- **Corrección de Bucle Conversacional y Progresión de Triaje:** Corregido el bucle atractor en el que el asistente repetía la misma pregunta de evaluación. Se introdujo una regla de progresión conversacional estricta en el prompt que prohíbe repetir preguntas ya contestadas y avanza de inmediato a primeros auxilios/inmovilización. Además, se configuraron `repeat_penalty: 1.15` y `presence_penalty: 0.4` en las peticiones al LLM.
- **Calibración de Umbral RAG (`RAG_MIN_SCORE = 0.42`):** Calibrado el umbral de similitud coseno de 0.55 a 0.42, adaptado a consultas en lenguaje natural con el modelo MiniLM-L12 para recuperar documentos médicos ante accidentes en montaña.
- **Contrato de API (`docs/info/08-contrato-api.md`):** Actualizado como documento 100% autónomo y exportable con soporte para `id_conversacion`, `reset_conversacion` y límites en bytes UTF-8.

---

## [0.3.0] - 2026-08-27

### Añadido
- **Memoria Conversacional Persistente:**
  - Migración SQL `0002_conversaciones.sql` con tablas `conversaciones` y `mensajes_conversacion`.
  - Ventana deslizante de hasta 20 turnos completos (40 mensajes) aislada por cliente.
  - Compactación inteligente con el LLM de turnos antiguos al superar el umbral.
  - Expiración automática por inactividad tras 1 hora (TTL 3600 s).
  - Endpoint de reseteo dedicado `POST /v1/conversacion/reset` y parámetro `reset_conversacion: true` en `POST /v1/consulta`.
- **Selector de ID y botón "Nueva Conversación" en Web UI (`:8443`).**

### Modificado
- `src/api/memory.py`: Parámetros de retención configurables desde `Settings` (`CONV_MAX_TURNOS`, `CONV_TTL_SEGUNDOS`).

---

## [0.2.0] - 2026-08-27

### Añadido
- **Containerización Docker completa (`docker-compose.yml`):**
  - Servicio `bot-llm` con `llama.cpp` nativo ARM en puerto `8869` (Qwen 2.5-3B-Instruct Q4_K_M).
  - Servicio `bot-api` con FastAPI en puerto `8870` (FastEmbed MiniLM 384d y semáforo concurrente de inferencia).
  - Servicio `bot-db` con PostgreSQL 17 + pgvector en puerto `5433` (interno `5432`).
  - Servicio `bot-web` en puerto `8443` con interfaz de chat interactiva y proxy seguro.
- Despliegue en producción sobre Raspberry Pi 5 (`172.18.1.121`).
- Protección de tokens por defecto con visibilidad conmutable en la interfaz web.

---

## [0.1.0] - 2026-08-26

### Añadido
- Arquitectura inicial del backend para Raspberry Pi 4 / Pi 5.
- Esquema base de datos `0001_init.sql` con soporte de pgvector.
- Conector de embeddings FastEmbed (`paraphrase-multilingual-MiniLM-L12-v2`).
- Pipeline RAG básico con límite duro de 3 mensajes de $\le 250$ caracteres para radiofrecuencia (Meshtastic/LoRa).
- Conectores iniciales de scraping y datos abiertos (Overpass/OSM, GBIF, Wikidata).
- Documentación técnica base en `docs/info/`.
