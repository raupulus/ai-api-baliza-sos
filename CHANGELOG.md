# Changelog

Todas las modificaciones notables de este proyecto se documentan en este archivo.
El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y se adhiere al versionado semántico.

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
- **Triaje de Emergencias Activo:** Reformulado el prompt para evaluar de inmediato el estado físico de la víctima, aportar pautas de inmovilización/abrigo y referenciar puntos de auxilio para el 112, eliminando el rechazo prematuro.
- **Contrato de API (`docs/info/08-contrato-api.md`):** Actualizado como documento 100% autónomo y exportable con soporte para `id_conversacion` y `reset_conversacion`.

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
