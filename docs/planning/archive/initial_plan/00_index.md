# Plan inicial — Índice

Planificación de la implementación del backend, dividida en **módulos**. Cada
módulo tiene su propio archivo con un **resumen** al inicio, **fases ordenadas**
y un **checklist** al final que debe marcarse a medida que se implementa.

> Esta planificación es **provisional** y se irá adaptando módulo a módulo
> durante la implementación.

## Cómo usar este plan

1. Implementa los módulos en el orden indicado (respetan dependencias).
2. Dentro de cada módulo, sigue las fases en orden.
3. Marca cada casilla del checklist al completar la tarea correspondiente.
4. Si una decisión cambia, actualiza el doc del módulo y, si aplica,
   `docs/info/`.

## Orden de implementación y dependencias

| # | Módulo | Depende de | Objetivo |
|---|--------|-----------|----------|
| 01 | [Infraestructura base](01_infraestructura_base.md) | — | Repo, config, PostgreSQL+pgvector, esqueleto systemd, logging. |
| 02 | [Servicio LLM (llama.cpp)](02_servicio_llm.md) | 01 | Compilar llama.cpp, gestión de modelos, `llama-server`. |
| 03 | [Motor RAG](03_motor_rag.md) | 01, 02 | Embeddings, esquema vectorial, recuperación. |
| 04 | [API del bot](04_api_bot.md) | 01, 02, 03 | Endpoint, pipeline, prompt, post-proceso 250×3, JSON. |
| 05 | [Actualizador de contexto](05_servicio_actualizador.md) | 01, 03 | Orquestación de ingesta, normalización, checkpoint, indexado. |
| 06 | [Fuentes de datos y scraping](06_fuentes_datos_scraping.md) | 05 | Conectores por fuente (GBIF, Overpass, AEMET, IGN, PDFs...). |
| 07 | [Calidad, seguridad y observabilidad](07_calidad_seguridad.md) | 04, 05 | Validación humana, avisos, pruebas, métricas, backups. |
| 08 | [Despliegue y operación](08_despliegue_operacion.md) | todos | Unidades systemd, tuning RPi, runbook, cambio de modelo. |

## Hitos sugeridos

- **Hito A — "Habla":** 01 + 02 + un endpoint mínimo → la Pi responde con el LLM
  (aún sin RAG).
- **Hito B — "Sabe":** 03 + 04 → respuestas con RAG sobre un corpus semilla
  cargado a mano.
- **Hito C — "Aprende":** 05 + 06 → el actualizador llena la base desde fuentes
  reales con checkpoint humano.
- **Hito D — "Producción":** 07 + 08 → endurecido, monitorizado y desplegado con
  systemd, arrancando solo tras reinicio.

## Referencias de contexto

- Visión y requisitos: `../../info/01-vision-requisitos.md`
- Arquitectura: `../../info/02-arquitectura.md`
- Decisiones de stack: `../../info/03-decisiones-stack.md`
- Presupuesto de recursos: `../../info/04-presupuesto-recursos.md`
- Contratos de datos: `../../info/05-contratos-datos.md`
