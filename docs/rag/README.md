# Fuentes y planificación del conocimiento offline

Este directorio es la fuente de verdad para decidir **qué conocimiento se adquiere, de dónde procede, cómo se transforma y con qué controles puede publicarse** en `ai-api-baliza-sos`.

Una ficha Markdown no implica que exista un conector, que se haya descargado el contenido ni que esté validado. Del mismo modo, la existencia de código no demuestra licencia, actualidad o revisión humana.

## Documentos de gobierno y datos procesados

- [Catálogo maestro de adquisición](catalogo-adquisicion.md): organización y trazabilidad completa de `data/info/valorar.md`.
- [Plantilla de ficha de especificación](PLANTILLA_FUENTE.md): campos obligatorios, ciclo de vida, checklists y registro de fuentes.
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

## Fichas temáticas evaluadas

| Ficha | Prioridad | Destino | Estado documental | Implementación actual |
|---|---:|---|---|---|
| [Primeros auxilios](primeros-auxilios.md) | P0 | Híbrido | En validación | Conector heredado; bloqueado hasta auditoría de contenido |
| [Toxicología y sustancias](toxicologia-sustancias.md) | P0 | RAG + contactos | Propuesta | No implementada |
| [Apoyo psicosocial](apoyo-psicosocial.md) | P1 | RAG | Propuesta | No implementada |
| [Protección civil y autoprotección](proteccion-civil-autoproteccion.md) | P0 | RAG | Propuesta | No implementada |
| [Preparación y supervivencia](preparacion-supervivencia.md) | P0/P1 | Híbrido | Propuesta | No implementada |
| [Legislación y derechos](legislacion-derechos.md) | P2 | Híbrido | Propuesta | No implementada |
| [Transporte público](transporte-publico.md) | P1 | Estructurado | Propuesta | No implementada |
| [Flora y fauna](flora-fauna.md) | P0/P1 | Híbrido | En validación | Conector heredado; bloqueado hasta auditoría de contenido |
| [Territorio y medio natural](territorio-medio-natural.md) | P0/P1 | Geoespacial | Propuesta | No implementada |
| [Municipios y geografía](municipios-geografia.md) | P1 | Geoespacial | En validación | Conector heredado; ampliar a núcleos y contrastar |
| [Historia y patrimonio](historia-patrimonio.md) | P3 | Híbrido | En validación | Conector heredado; falta trazabilidad por afirmación |
| [Fiestas y tradiciones](fiestas-tradiciones.md) | P2 | Híbrido | En validación | Conector heredado; fechas sin vigencia estructurada |
| [Directorios de emergencia](directorios-emergencia.md) | P0 | Estructurado | Propuesta | No implementada |
| [Agricultura y ganadería](agricultura-ganaderia.md) | P2 | Híbrido | Propuesta | No implementada |
| [Radio y comunicaciones](radio-comunicaciones.md) | P1 | Híbrido | Propuesta | No implementada |
| [Astronomía, mareas y orientación](astronomia-mareas-orientacion.md) | P1 | Híbrido | Propuesta | No implementada |

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
4. Guardar la instantánea original en `data/raw/<identificador>/<AAAA-MM-DD>/` junto a `MANIFEST.json`, sin editar el original.
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
