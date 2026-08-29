# Fuentes y planificación del conocimiento offline

Este directorio es la fuente de verdad para decidir **qué conocimiento se adquiere, de dónde procede, cómo se transforma y con qué controles puede publicarse** en `ai-api-baliza-sos`.

Una ficha Markdown no implica que exista un conector, que se haya descargado el contenido ni que esté validado. Del mismo modo, la existencia de código no demuestra licencia, actualidad o revisión humana.

## Documentos de gobierno y datos procesados

- [Catálogo maestro de adquisición](catalogo-adquisicion.md): organización y trazabilidad completa de `data/info/valorar.md`.
- [Plan de adquisición y descarga](plan-adquisicion.md): triaje de fuentes por clase (descarga/API/portal/bloqueo) y orden de ejecución.
- [Análisis del lote descargado](analisis-lote.md): hallazgos y restricciones por fuente tras inspeccionar el contenido.
- [Plantilla de ficha de especificación](PLANTILLA_FUENTE.md): campos obligatorios, ciclo de vida, checklists y registro de fuentes.
- [Checklist de validación humana](checklist-validacion-humana.md): puerta única de aprobación antes de indexar contenido sensible.
- [Auditoría de fuentes](auditoria-fuentes.md): checklist de verificación de URLs y estado de incidencias.
- [Lecciones de adquisición](lecciones-adquisicion.md): restricciones y rate-limits encontrados, para no repetir fallos ni bloqueos de red.
- [Directorio de datos procesados (`data/processed/`)](../../data/processed/README.md): datasets limpios (CSV) y fragmentos narrativos (MD) listos para el RAG.

## Criterio de almacenamiento y separación de contextos

| Contexto / Directorio | Contenido | Destino / Tratamiento |
|---|---|---|
| `docs/rag/*.md` | Fichas de especificación, motivos, fuentes y checklists | Documentación de gobierno y planificación |
| `data/raw/` | Descargas originales (PDF, ZIP, HTML, XML) | Equipo actualizador / No versionado en Git |
| `data/processed/csv/` | Teléfonos, coordenadas, frecuencias, horarios | Tablas estructuradas / Relacionales |
| `data/processed/md/` | Procedimientos, primeros auxilios, guías de campo | Base vectorial RAG (`pgvector`) |
| `data/info/` | Laboratorio de ideas y prompts (`valorar.md`) | Cuaderno de trabajo y evaluación |

El sistema opera offline y con recursos limitados. La Pi recibe solo fragmentos aprobados, metadatos necesarios y tablas compactas desde `data/processed/`; los originales se conservan en `data/raw/` para evidencia y reprocesado.

## Estado actual del corpus (2026-08-28)

**4474 fragmentos validados (0 pendientes)** en `data/staging/aprobados/`, listos para la ingesta en la Raspberry Pi.

| Categoría | Frag. | | Categoría | Frag. |
|---|---:|---|---|---:|
| Geografía | 3216 | | Fauna | 25 |
| Supervivencia | 661 | | Primeros auxilios | 17 |
| Transporte | 449 | | Protección civil | 7 |
| Directorios | 54 | | Flora | 6 |
| Orientación | 28 | | Apoyo psicosocial | 5 |

Además: legislación 2 · toxicología 1 · cultura/historia 1 · clima 1 · agricultura 1.

> La columna «Implementación actual» de la tabla siguiente es **indicativa por ficha**; la fuente de verdad numérica es `data/staging/aprobados/`.

## Fichas temáticas evaluadas

| Ficha | Prioridad | Destino | Estado documental | Implementación actual |
|---|---:|---|---|---|
| [Primeros auxilios](primeros-auxilios.md) | P0 | Híbrido | En validación | ✅ 17 frag. (INGESA/ERC + mordeduras) |
| [Toxicología y sustancias](toxicologia-sustancias.md) | P0 | RAG + contactos | Propuesta | ⚠️ 1 frag. (biotoxinas) |
| [Apoyo psicosocial](apoyo-psicosocial.md) | P1 | RAG | Propuesta | ✅ 5 frag. |
| [Protección civil y autoprotección](proteccion-civil-autoproteccion.md) | P0 | RAG | Propuesta | ✅ 7 frag. (montaña + DGPCE) |
| [Preparación y supervivencia](preparacion-supervivencia.md) | P0/P1 | Híbrido | Propuesta | ⚠️ Hueco de fuente ciudadana |
| [Legislación y derechos](legislacion-derechos.md) | P2 | Híbrido | Propuesta | ✅ 2 frag. (Carta DFUE + CE) |
| [Transporte público](transporte-publico.md) | P1 | Estructurado | Propuesta | ✅ 449 frag. (GTFS 367 + ADIF 52 + Renfe 30) |
| [Flora y fauna](flora-fauna.md) | P0/P1 | Híbrido | En validación | ✅ 31 frag. (GBIF 30 + procesionaria 1) |
| [Territorio y medio natural](territorio-medio-natural.md) | P0/P1 | Geoespacial | Propuesta | ⚠️ 2171 topónimos NGA |
| [Municipios y geografía](municipios-geografia.md) | P1 | Geoespacial | En validación | ✅ 45 municipios (DERA/IECA) |
| [Historia y patrimonio](historia-patrimonio.md) | P3 | Híbrido | En validación | ⛔ Conector bloqueado |
| [Fiestas y tradiciones](fiestas-tradiciones.md) | P2 | Híbrido | En validación | ✅ 1 frag. (festivos 2026) |
| [Directorios de emergencia](directorios-emergencia.md) | P0 | Estructurado | Propuesta | ✅ 54 frag. (GC 52 + 112 1 + 016 1) |
| [Agricultura y ganadería](agricultura-ganaderia.md) | P2 | Híbrido | Propuesta | ⚠️ 1 frag. (sectores) + RAIF (28 548) |
| [Radio y comunicaciones](radio-comunicaciones.md) | P1 | Híbrido | Propuesta | 📦 Descargado (Meshtastic + BOE) |
| [Astronomía, mareas y orientación](astronomia-mareas-orientacion.md) | P1 | Híbrido | Propuesta | 📦 Descargado (IGN atlas) |
| [Clima y meteorología](clima-meteorologia.md) | P0/P1 | RAG + tabla de umbrales | Propuesta | ✅ 1 frag. (calor) |
| `[nueva-ficha].md` | `P0..P3` | `RAG / Estructurado / Híbrido / Geoespacial` | `propuesta` | No implementada |

> La fila `[nueva-ficha].md` es una **plantilla de registro** para futuras fichas: copiar la fila, sustituir identificador/prioridad/destino/estado y mantener el orden por prioridad. Usar [`PLANTILLA_FUENTE.md`](PLANTILLA_FUENTE.md) para el contenido.

## Fichas de conectores externos existentes

Estas fichas describen conectores o servicios transversales ya presentes en el repositorio. Su información puede complementar varios dominios, pero no sustituye la fuente competente para teléfonos, riesgos médicos, comestibilidad o vigencia legal.

| Ficha | Uso | Código detectado |
|---|---|---|
| [Overpass / OpenStreetMap](overpass-osm.md) | Puntos geográficos complementarios | `src/updater/sources/overpass.py` |
| [Wikidata](wikidata.md) | Entidades y metadatos complementarios | `src/updater/sources/wikidata.py` |
| [GBIF](gbif.md) | Ocurrencias de biodiversidad | `src/updater/sources/gbif.py` |

## Flujo para incorporar o actualizar conocimiento

1. Localizar el dominio en el [catálogo maestro](catalogo-adquisicion.md).
2. Crear o actualizar su ficha con la [plantilla](PLANTILLA_FUENTE.md).
3. Verificar autoridad, URL estable, licencia, formato, cadencia y alternativa ante caída.
4. Guardar la instantánea original en `data/raw/downloads/<identificador>/<AAAA-MM-DD>/` junto a `MANIFEST.json`, sin editar el original.
5. Transformar a staging conservando fuente, versión, hash y reglas de mapeo.
6. Ejecutar validaciones automáticas y generar diferencias respecto a la versión aprobada.
7. Completar el checkpoint humano obligatorio para medicina, toxicología, especies peligrosas y otros contenidos definidos por la ficha.
8. Solo entonces implementar o ejecutar el conector y publicar la salida aprobada.

No se registra una fuente como implementada por crear su ficha. Cuando se implemente, deberán actualizarse el registro de `src/updater/sources/`, las pruebas y la documentación técnica correspondiente.

## Reglas comunes de seguridad y licencia

- Una URL pública no equivale a una licencia abierta.
- Usar `pendiente de verificar` cuando no exista evidencia de reutilización.
- No marcar contenido como validado sin identidad/rol del revisor, fecha, versión revisada y resultado persistente.
- Horarios, teléfonos, mareas, fechas y frecuencias no se almacenan como texto semántico aproximado.
- El contenido médico y sobre especies peligrosas no se publica desde scraping sin revisión humana.
- Las alertas offline siempre muestran antigüedad y nunca se presentan como información en tiempo real.
- Toda adquisición futura respetará `UPDATER_USER_AGENT`, límites de uso y licencia de la fuente.
