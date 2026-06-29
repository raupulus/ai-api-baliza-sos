# Módulo 03 · Motor RAG

## Resumen

El cerebro de recuperación: convierte texto en embeddings con
**multilingual-e5-small** (384 dim) vía fastembed/ONNX, almacena y consulta los
vectores en **pgvector**, y entrega los fragmentos más relevantes para construir
el contexto del prompt. Define el chunking, los prefijos `query:`/`passage:`, el
filtrado por umbral/categoría/zona y la construcción del bloque de contexto
acotado. Lo usan tanto la API (embedding de la consulta + recuperación) como el
actualizador (embedding de los fragmentos al indexar).

Dependencias: 01, 02. Habilita: 04, 05.

## Fase 1 — Servicio de embeddings (`src/api/rag/embeddings.py`)

- Wrapper sobre fastembed con el modelo de `EMBEDDING_MODEL`, cargado una sola
  vez (singleton) para no duplicar RAM.
- Aplicar prefijos e5 (`EMBEDDING_QUERY_PREFIX` / `EMBEDDING_PASSAGE_PREFIX`).
- API interna: `embed_query(texto) -> vector`, `embed_passages(textos) -> vectores`.
- Verificar que la dimensión coincide con `EMBEDDING_DIM` (fallar si no).

## Fase 2 — Estrategia de chunking

- Reglas de troceado por tipo de fuente: fragmentos **autocontenidos y cortos**
  (un primer auxilio = un fragmento accionable; una especie = una ficha).
- Tamaño objetivo por fragmento alineado con `RAG_MAX_CONTEXT_CHARS` y el
  contexto del LLM. Evitar fragmentos largos que llenen el KV-cache.
- Metadatos obligatorios por fragmento (categoría, fuente, confianza).

## Fase 3 — Almacenamiento e indexado vectorial

- Funciones de upsert en `fragmentos` con `embedding` y `hash_contenido`
  (idempotencia).
- Índice IVFFlat/exacto (de módulo 01); parámetros de búsqueda documentados.
- Operación de reindexado completo (si cambia el modelo de embeddings).

## Fase 4 — Recuperación (`src/api/rag/retrieval.py`)

- Búsqueda por similitud coseno top-`RAG_TOP_K`, con `RAG_MIN_SCORE` como
  umbral.
- Filtros opcionales: por `categoria_sugerida`, por provincia/zona (si hay
  `ubicacion`), por `nivel_confianza`.
- Devolver fragmentos + puntuación + metadatos de fuente.

## Fase 5 — Construcción de contexto (`src/api/rag/context.py`)

- Ensamblar el bloque `[CONTEXTO]` del prompt respetando
  `RAG_MAX_CONTEXT_CHARS`: priorizar por score y confianza, truncar con criterio.
- Adjuntar la procedencia (para poblar `fuentes` en la respuesta).
- Caso "sin contexto suficiente": señal explícita para que la API responda con
  cautela y no se invente.

## Fase 6 — Evaluación del RAG

- Conjunto pequeño de consultas de prueba por categoría con la respuesta/fuente
  esperada.
- Métricas simples: ¿se recupera el fragmento correcto en el top-k?
- Script para ejecutar la evaluación y detectar regresiones al cambiar
  modelo/umbral.

## Verificación del módulo

- Indexar un corpus semilla pequeño y comprobar recuperaciones coherentes.
- Validar que cambiar `RAG_TOP_K`/`RAG_MIN_SCORE` surte efecto.
- Confirmar coincidencia de dimensiones embeddings ↔ esquema.

## Checklist

- [ ] Fase 1: wrapper de embeddings (fastembed) singleton.
- [ ] Fase 1: prefijos e5 aplicados; validación de dimensión.
- [ ] Fase 2: reglas de chunking por tipo de fuente documentadas.
- [ ] Fase 3: upsert idempotente con `hash_contenido`.
- [ ] Fase 3: índice vectorial y parámetros de búsqueda definidos.
- [ ] Fase 3: operación de reindexado completo.
- [ ] Fase 4: recuperación top-k con umbral.
- [ ] Fase 4: filtros por categoría/zona/confianza.
- [ ] Fase 5: construcción de contexto acotada por caracteres.
- [ ] Fase 5: manejo de "sin contexto suficiente".
- [ ] Fase 6: set de evaluación y script de métricas.
- [ ] Verificación: corpus semilla indexado y recuperaciones coherentes.
