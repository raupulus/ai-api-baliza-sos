# Inventario de Fuentes Actuales del RAG

> **Fecha:** 2026-08-27  
> **Propósito:** Registro técnico de todas las fuentes de datos implementadas en el proyecto, su procedencia en código, su estado de calidad y los problemas detectados que generan respuestas inútiles ("paja") o efecto loro.

---

## 1. Resumen Global de Fuentes

El sistema cuenta actualmente con **8 conectores de fuentes** (5 locales de Cádiz y 3 conectores externos/API) más el corpus de prueba semilla:

| # | Fuente / Conector | Módulo en Código | Ficha de Especificación | Registros / Fragmentos | Calidad / Problema Detectado |
| :-: | :--- | :--- | :--- | :-: | :--- |
| **1** | **Primeros Auxilios Avanzado** | `src/updater/sources/primeros_auxilios_avanzado.py` | `docs/rag/primeros-auxilios.md` | 13 fragmentos | ⚠️ **Sintético / Escaso:** Textos resumidos manualmente sin pasos de campo para situaciones sin material médico comercial. |
| **2** | **Flora y Fauna Peligrosa/Comestible** | `src/updater/sources/flora_fauna_cadiz.py` | `docs/rag/flora-fauna.md` | 13 fragmentos | ⚠️ **Poco accionable:** Fichas botánicas generales; falta detalle de toxicidad diferencial y qué maniobra exacta hacer en campo. |
| **3** | **45 Municipios y Cumbres de Cádiz** | `src/updater/sources/municipios_cadiz.py` | `docs/rag/municipios-geografia.md` | 46 fragmentos | ⚠️ **Formato rígido:** Coordenadas WGS84 de cabeceras municipales y picos; no incluye triangulación por accidentes visuales (embalses, líneas de costa). |
| **4** | **Fiestas y Tradiciones de Cádiz** | `src/updater/sources/fiestas_cadiz.py` | `docs/rag/fiestas-tradiciones.md` | 11 fragmentos | ℹ️ **Baja prioridad en emergencias:** Útil para cultura general o auxilio en aglomeraciones (carnavales, ferias), pero satura contexto si no se filtra bien. |
| **5** | **Historia y Patrimonio de Cádiz** | `src/updater/sources/historia_cadiz.py` | `docs/rag/historia-patrimonio.md` | 6 fragmentos | ℹ️ **Informativo:** Hitos históricos locales (Trafalgar, 1812, Gadir). Sin impacto en supervivencia. |
| **6** | **OpenStreetMap / Overpass** | `src/updater/sources/overpass.py` | `docs/rag/overpass-osm.md` | Dinámico (POIs BBOX) | ⚠️ **Depende de conexión/descarga:** Extrae farmacias, fuentes potables y centros de salud en coordenadas brutas. Requiere volcado offline en CSV estructurado. |
| **7** | **GBIF (Biodiversidad Cádiz)** | `src/updater/sources/gbif.py` | `docs/rag/gbif.md` | Dinámico (Ocurrencias) | ⚠️ **Ruido taxonómico:** Ocurrencias biológicas masivas. Si no se filtra con lupa, introduce nombres científicos sin valor práctico de supervivencia. |
| **8** | **Wikidata SPARQL** | `src/updater/sources/wikidata.py` | `docs/rag/wikidata.md` | Dinámico (Entidades) | ⚠️ **Inconsistencia de datos:** Hospitales, faros y puertos. Debe fijarse en CSV para no depender de la API de Wikimedia. |
| **0** | **Semilla Inicial (Seed)** | `scripts/seed_corpus.py` | — | 6 fragmentos | ⚠️ **Frases genéricas ("paja"):** Textos de 2 líneas ("en la costa busca un faro") que el LLM repite sin aportar pasos reales. |

---

## 2. Diagnóstico Detallado por Fuente

### 2.1. Primeros Auxilios Avanzado (`primeros_auxilios_avanzado.py`)
* **Datos actuales:** Fichas redactadas para caídas, esguinces de tobillo, hemorragias, quemaduras, hipotermia, golpe de calor y RCP.
* **Causa de respuestas deficientes:**
  * Son resúmenes sintéticos teóricos ("acudir a un centro médico", "llamar al 112").
  * **No contienen medicina de expedición/campamento:** En zonas aisladas no hay ambulancia ni férulas de aluminio. Falta explicar cómo usar ramas rectas y ropa para entablillar, cómo presionar una arteria femoral/braquial, o cómo improvisar un torniquete seguro sólo si hay riesgo vital.
* **Solución requerida en `data/raw/`:**
  * Descargar manuales oficiales de Primeros Auxilios en Montaña de la **Federación Española de Deportes de Montaña y Escalada (FEDME)** y del **GREIM de la Guardia Civil**.
  * Extraer fichas estructuradas al CSV maestro.

### 2.2. Flora, Hongos y Fauna Peligrosa (`flora_fauna_cadiz.py`)
* **Datos actuales:** Víbora hocicuda, escolopendra, carabela portuguesa, pez araña, adelfa, cicuta, amanita phalloides.
* **Causa de respuestas deficientes:**
  * Descripciones breves. No detallan los síntomas temporales (ej. si una picadura de víbora produce edema progresivo a los 30 min) ni qué hacer para mitigar dolor intenso en campo (agua caliente a 45 °C para desnaturalizar toxina del pez araña).
* **Solución requerida en `data/raw/`:**
  * Guías toxicológicas de la **Junta de Andalucía / REDIAM** y protocolos de envenenamiento del **Servicio de Información Toxicológica (SIT / INTCF)**.

### 2.3. Geografía y Municipios (`municipios_cadiz.py`)
* **Datos actuales:** 45 municipios con latitud, longitud, altitud y comarca; picos principales (El Torreón, San Cristóbal, etc.).
* **Causa de respuestas deficientes:**
  * Almacenados como texto plano ("El municipio de Grazalema se ubica a...").
  * Si el usuario dice *"estoy viendo una presa grande a la izquierda y un pueblo blanco a la derecha"*, el RAG no conecta esa descripción visual con los embalses de Cádiz (Zahara-El Gastor, Bornos, Arcos, Barbate, Guadalcacín).
* **Solución requerida en `data/raw/`:**
  * Catálogo de orografía visual de Cádiz del **IGN / IECA**: Embalses principales, sierras dominantes, carreteras comarcales clave y orientaciones visuales típicas.

### 2.4. OpenStreetMap, Wikidata y GBIF (Fuentes Externas)
* **Problema actual:** Se concibieron como conectores online que consultan APIs cuando corre el `updater`. Esto rompe el principio de reproductibilidad y genera datos heterogéneos.
* **Solución:**
  * Descargar los POIs una sola vez en `data/raw/` (OpenStreetMap Export de farmacias, puntos de agua, helisuperficies y centros sanitarios de Cádiz).
  * Parsear y consolidar en `data/csv/puntos_auxilio_cadiz.csv`.

---

## 3. Plan de Limpieza y Próximos Pasos

1. **Purga de "paja":** Eliminar fragmentos que solo digan generalidades vacías ("mantén la calma", "llama al 112", "busca un faro").
2. **Descarga estructurada en `data/raw/`:** Guardar los documentos originales (PDFs y datasets oficiales) con su fuente y fecha.
3. **Generación de `data/csv/`:** Crear los archivos CSV definitivos con columnas estandarizadas (`id`, `categoria`, `subcategoria`, `titulo`, `procedimiento_paso_a_paso`, `advertencias_clave`, `fuente`, `fecha`).
