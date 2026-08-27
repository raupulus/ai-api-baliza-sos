# docs/rag — Registro y Especificación de Fuentes de Conocimiento del RAG

Este directorio contiene la **documentación exhaustiva de las fuentes de conocimiento** utilizadas por el motor RAG del Asistente de Emergencias (Cádiz).

Cada archivo de este directorio describe el origen de los datos, las entidades oficiales responsables, las licencias, los bloques temáticos de información estructurada que debe asimilar el asistente y el procedimiento de actualización manual.

---

## 1. Filosofía y Principios del Conocimiento en el RAG

1. **Operación Offline Estricta:**
   El bot opera en una Raspberry Pi 5 (o Pi 4) sin conexión a Internet. Todo el conocimiento debe estar pre-indexado en la base de datos vectorial local (PostgreSQL + pgvector).
2. **Actualización Manual Bajo Demanda (Sin Tareas Automáticas):**
   No existen trabajos cron automáticos ni scraping desatendido. Las fuentes se actualizan **únicamente cuando un operador lo solicita de forma explícita** mediante el comando:
   ```bash
   python3 scripts/actualizar_fuente.py --fuente <nombre-fuente>
   # O para todas las fuentes ampliadas de Cádiz:
   python3 scripts/actualizar_fuente.py --todas
   ```
3. **Seguridad y Validación Humana Obligatoria:**
   El contenido médico de primeros auxilios y las especies biológicas peligrosas no pueden indexarse a partir de scraping arbitrario. Deben provenir de fuentes oficiales contrastadas (Cruz Roja, SEMES, Protección Civil, REDIAM) y contar con validación humana antes de pasar a producción.
4. **Respeto de Licencias y Atribución:**
   Cada fuente documenta su tipo de licencia (CC-BY, ODbL, dominio público) y garantiza el cumplimiento de sus términos de atribución.

---

## 2. Índice de Fuentes Registradas

| Archivo | Identificador Fuente | Categoría | Entidad / Origen Oficial | Estado |
| :--- | :--- | :--- | :--- | :---: |
| [primeros-auxilios.md](primeros-auxilios.md) | `primeros-auxilios-avanzado` | `primeros_auxilios` / `supervivencia` | Cruz Roja Española, SEMES, Protección Civil | ✅ Activa |
| [flora-fauna.md](flora-fauna.md) | `flora-fauna-cadiz` | `flora` / `fauna` | REDIAM, Herbario Andaluz, Soc. Esp. Herpetología | ✅ Activa |
| [municipios-geografia.md](municipios-geografia.md) | `municipios-cadiz` | `geografia` | IGN (Instituto Geográfico Nacional), IECA | ✅ Activa |
| [fiestas-tradiciones.md](fiestas-tradiciones.md) | `fiestas-cadiz` | `cultura_historia` | Patronato de Turismo de Cádiz, Junta de Andalucía | ✅ Activa |
| [historia-patrimonio.md](historia-patrimonio.md) | `historia-cadiz` | `cultura_historia` | Archivo Histórico Provincial de Cádiz, IAPH | ✅ Activa |
| [overpass-osm.md](overpass-osm.md) | `overpass-osm` | `geografia` / `primeros_auxilios` | OpenStreetMap Foundation (Overpass API) | ✅ Activa |
| [wikidata.md](wikidata.md) | `wikidata` | `geografia` | Fundación Wikimedia (Wikidata SPARQL) | ✅ Activa |
| [gbif.md](gbif.md) | `gbif` | `fauna` / `flora` | Global Biodiversity Information Facility (GBIF) | ✅ Activa |

---

## 3. Cómo Agregar una Nueva Fuente de Conocimiento

Para incorporar un nuevo conjunto de datos al RAG, sigue estos pasos:

1. **Crear la especificación en `docs/rag/<nombre-fuente>.md`:**
   Copia la plantilla estandarizada [PLANTILLA_FUENTE.md](PLANTILLA_FUENTE.md) y completa todas sus secciones:
   - Identificador único (usar formato `kebab-case`).
   - Entidad oficial, URL y licencia.
   - Fecha de creación y validación.
   - Bloques temáticos de información detallados.
2. **Implementar el conector en `src/updater/sources/<nombre_fuente>.py`:**
   Hereda de la clase base `Source` (`updater.sources.base.Source`) e implementa el método `fetch() -> list[Fragmento]`.
3. **Registrar la fuente en `src/updater/sources/__init__.py`:**
   Añádela a `SOURCES` e `IMPLEMENTADAS`.
4. **Ejecutar la ingesta manual:**
   ```bash
   python3 scripts/actualizar_fuente.py --fuente <nombre-fuente>
   ```
5. **Actualizar el índice de este README y registrar en `AGENTS.md`.**

---

## 4. Estructura de un Fragmento de Conocimiento

Cada elemento indexado en PostgreSQL genera una fila en la tabla `fragmentos` con los siguientes campos clave:
* `texto`: Contenido textual sintetizado en español (idealmente entre 150 y 450 caracteres).
* `categoria`: `primeros_auxilios`, `fauna`, `flora`, `geografia`, `supervivencia`, `orientacion`, `clima` o `cultura_historia`.
* `subcategoria`: Etiqueta granular para filtrado semántico (ej. `mordeduras`, `pueblos_blancos`, `carnaval`).
* `nivel_confianza`: `alta` (fuente oficial validada), `media` o `baja`.
* `peligrosa`: Booleano para alertar sobre toxicidad o riesgo físico inminente.
* `embedding`: Vector denso de 384 dimensiones generado por `fastembed` (`multilingual-e5-small` o `paraphrase-multilingual-MiniLM-L12-v2`).
