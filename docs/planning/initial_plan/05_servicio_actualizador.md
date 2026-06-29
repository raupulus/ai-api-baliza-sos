# Módulo 05 · Servicio actualizador de contexto

## Resumen

Servicio independiente que **construye y mantiene la base de conocimiento**.
Orquesta la adquisición desde fuentes (módulo 06), normaliza todo al formato de
fragmento común, deja el contenido sensible en **staging para validación
humana**, y solo tras la aprobación genera embeddings e indexa en pgvector con
idempotencia. No comparte proceso con la API y se ejecuta bajo demanda o por
**systemd timer**. Aquí vive la garantía de calidad/seguridad de los datos.

Dependencias: 01, 03. Habilita: 06, Hito C.

## Fase 1 — Arquitectura del actualizador (`src/updater`)

- `pipeline.py`: orquestador con etapas adquirir → normalizar → stage →
  (checkpoint) → embeber → indexar.
- Interfaz común `Source` que cada conector de `sources/` implementa
  (`fetch()`, `normalize()` → fragmentos).
- Registro de fuentes activas según `env.py` (una fuente sin clave/condición se
  desactiva).

## Fase 2 — Normalización al formato de fragmento

- Convertir cualquier salida de fuente al esquema de
  `docs/info/05-contratos-datos.md` (`texto`, `fuente`, `fecha`, `categoria`,
  `nivel_confianza`, `licencia`, `hash_contenido`...).
- Asignar `nivel_confianza` por política: oficial+validado = `alta`; scraping no
  verificado ≤ `media`.
- Calcular `hash_contenido` para idempotencia.

## Fase 3 — Staging y checkpoint humano

- Volcar a `data/staging` los fragmentos que **requieren validación**
  (primeros auxilios, fauna peligrosa/tóxica) en un formato revisable
  (JSON/markdown legible).
- Herramienta/CLI mínima para que el operador **apruebe, edite o rechace**
  (`scripts/review.py` o comando del updater).
- Solo lo aprobado pasa a indexado; registrar `validado_por`/`validado_fecha`.

## Fase 4 — Embedding e indexado

- Generar embeddings de los fragmentos aprobados (módulo 03, prefijo `passage:`).
- Upsert idempotente en `fragmentos` (por `hash_contenido`).
- Registrar la ejecución en la tabla `ingestas` (qué fuente, cuántos, errores).

## Fase 5 — Orquestación y programación

- CLI del actualizador: `--source X`, `--all`, `--dry-run`, `--reindex`.
- Unidad `context-updater.service` + `context-updater.timer` (p. ej. nocturno).
- Garantizar que **no coincide con picos** de la API (presupuesto de RAM).
- Idempotencia y reanudación: una ejecución repetida no duplica datos.

## Fase 6 — Robustez

- Rate limiting y reintentos con backoff por fuente; respetar `User-Agent`.
- Manejo de fuente caída/parcial sin abortar todo el pipeline.
- Trazabilidad: logs por fuente y resumen final de la ejecución.

## Verificación del módulo

- Ejecutar el pipeline con una fuente de bajo riesgo (p. ej. geografía) de
  principio a fin e indexar.
- Forzar el camino de checkpoint con una fuente sensible y comprobar que **sin
  aprobación no se indexa**.
- Re-ejecutar y confirmar idempotencia (no duplica).

## Checklist

- [ ] Fase 1: orquestador `pipeline.py` con etapas definidas.
- [ ] Fase 1: interfaz común `Source` y registro de fuentes por env.
- [ ] Fase 2: normalización al formato de fragmento.
- [ ] Fase 2: política de `nivel_confianza` aplicada.
- [ ] Fase 2: `hash_contenido` para idempotencia.
- [ ] Fase 3: staging de contenido sensible en `data/staging`.
- [ ] Fase 3: herramienta de revisión (aprobar/editar/rechazar).
- [ ] Fase 3: registro de `validado_por`/`validado_fecha`.
- [ ] Fase 4: embedding e indexado de fragmentos aprobados.
- [ ] Fase 4: upsert idempotente y registro en `ingestas`.
- [ ] Fase 5: CLI con `--source/--all/--dry-run/--reindex`.
- [ ] Fase 5: unidad + timer systemd, sin coincidir con picos.
- [ ] Fase 6: rate limiting, reintentos y tolerancia a fallos por fuente.
- [ ] Verificación: checkpoint impide indexar sin aprobación; idempotencia OK.
