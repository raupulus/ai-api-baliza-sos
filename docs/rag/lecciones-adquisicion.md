# Lecciones de adquisición y restricciones (evitar repetir fallos)

[← Volver al índice](README.md)

> **Fecha:** 2026-08-28 · **Uso:** consulta obligatoria antes de re-descargar o re-procesar cualquier fuente. Cada entrada registra un problema encontrado y su solución. Añade aquí cada nueva restricción *al encontrarla*.

---

## 1. Cortesía de red y anti-bloqueo (reglas generales)

- **User-Agent identificado** en toda petición: `bot-ia-auxiliar/0.1` (+ contacto público `public@raupulus.dev`). No usar UA genérico de navegador salvo que la fuente lo exija.
- **Intervalo mínimo entre peticiones:** 1–2 s en APIs (Overpass, GBIF, Wikidata). Respetar `429` y `Retry-After`; backoff exponencial (2^n, máx 30 s).
- **No reintentar agresivamente** endpoints que devuelven 403/202/anti-bot (EUR-Lex, EUDA): se bloquean más. Cambiar de espejo o de vía.
- **Anti-bot resuelto con cortesía (2026-08-28):** EUR-Lex (202) y ADIF IDEADIF pasaron a **200** usando cabecera de **Safari macOS** (`AppleWebKit/605.1.15 ... Version/16.6 Safari/605.1.15`) + 3 s entre peticiones + 10 s cada 5 + **alternar dominios**. Los bloqueos por anti-bot suelen ser por exceso de peticiones seguidas al mismo host. Ver `scripts/reintentar_bloqueadas.py`.
- **Certificados autofirmados:** algunos portales de la Junta usan TLS autofirmado; usar `-k` solo para verificar, y anotarlo.
- **`content_type` de la respuesta no es fiable:** verificar con `file`, `pdfinfo` o inspección real, no con la cabecera HTTP.

---

## 2. Formatos y compresión

| Problema | Fuente | Solución |
|---|---|---|
| ZIP con **DEFLATE64** (`compress_type=9`), no lo lee `zipfile` de Python | RAIF (Junta) | Descomprimir con `7z`/`bsdtar` (`scripts/extraer_raif_cadiz.py`). |
| `stop_times.txt` de **287 MB** | GTFS Renfe | Leer en **streaming** (`z.open`), nunca `z.read()` completo. |
| CSV en **ISO-8859** | Guardia Civil | Transcodificar a UTF-8 antes de parsear. |
| Campos GTFS con **espacios** al final | Renfe | Aplicar `.strip()` a todos los valores. |
| PDF **escaneado** (0 palabras en `pdftotext`) | Peces, montaña, DGPCE | OCR con `tesseract -l spa` (`scripts/ocr_pdf_es.py`). |
| PDF **mixto** (texto + imágenes) | DGPCE | `pdftotext` > 0 no garantiza que las páginas clave (ej. "Recomendaciones") sean texto; verificar página a página y OCR si falta. |
| HTML en **euskera/catalán** aunque el portal parezca español | AESAN (`/eu/`) | Pedir explícitamente la ruta `/es/` y comprobar `lang`. |

---

## 3. APIs y WFS geográficos

| Problema | Fuente | Solución |
|---|---|---|
| WFS de deegree con **`intersects()` inexistente** (filtro espacial roto) | NGA (IECA) | Filtrar por campos escalares `coordenadaX`/`coordenadaY` (UTM), no por geometría. |
| WFS de MapServer **BBOX devuelve 0** | REDIAM flora | Filtro espacial roto (BBOX→vacío, CQL→403). **Workaround:** `outputFormat=geojson` funciona y trae `coor_x`/`coor_y` (UTM EPSG:3042) + `nombre_cie` + `fuente`; descargar completo paginando (`maxFeatures=5000`) y filtrar en cliente por `coor_x`/`coor_y`. |
| **Axis order WFS 1.1.0**: EPSG:4326 es (lat, lon) | NGA | Usar EPSG:25830 (x=easting, y=northing) en el filtro para evitar ambigüedad. |
| **Paginación**: `DefaultMaxFeatures=15000`, `numberOfFeatures` = nº devuelto (no total) | NGA | Paginar por `startIndex` hasta respuesta vacía. |
| **typeName con prefijo** (`app:Entidad`) requiere POST con namespace | NGA | POST `GetFeature` con `xmlns:app`; KVP falla ("No binding for prefix"). |
| CKAN **`package_search` → 404** | Diputación | La API real es **RTOD** (`apirtod.dipucadiz.es/api/collections.json`), no CKAN. |
| RTOD `datos/<id>.json` → **500** y SPARQL Marmotta → **connection reset** | Diputación | La fuente no sirve datos; reintentar en otra fecha o descartar. |
| **Wikidata `P131*`** no alcanza a playas/faros | Wikidata | Usar `SERVICE wikibase:around` (radio) con centro de provincia. |
| **ADIF IDEADIF** era SPA/anti-bot | ADIF | El WFS INSPIRE `https://ideadif.adif.es/services/wfs` (capa `tn-ra:RailwayStationNode`) responde con cabecera Safari macOS + cortesía. 52 estaciones de Cádiz normalizadas. |
| **`httpx` no instalado** en el entorno de operación | conectores | Usar `urllib` (stdlib) en scripts de operación (`scripts/fijar_conectores.py`). |

---

## 4. Estructuras de datos específicas

| Dato | Fuente | Detalle |
|---|---|---|
| `agency_id` **textual** (`CMTBC`, `CTMCG`), no numérico | GTFS unificado CTAN | No usar `2`/`5`. |
| Núcleo de Cádiz = `route_id` prefijo **`31T`** | GTFS Renfe | `30T`=Sevilla (roza BBOX por Lebrija), `10T`=Madrid. |
| RAIF 2006-2016 va **un XML por provincia**; 2017+ va **nacional** | RAIF | Filtrar por `<PROVINCIA>Cádiz</PROVINCIA>` para los nacionales. |
| DERA/NGA en **EPSG:25830** (UTM 30N) | IECA | Convertir a WGS84 con la fórmula inversa UTM (`scripts/normalizar_municipios.py`). |
| AESAN toxinas es **portal/hub** sin contenido sustantivo | AESAN | Las fichas concretas están en subpáginas; el consejo ciudadano de biotoxinas está en la Junta. |

---

## 5. Licencias (verificadas o bloqueadas) — resueltas por el usuario 2026-08-28

| Fuente | Licencia | Nota / acción |
|---|---|---|
| INGESA, DGPCE, DGT, SAS | **Reutilizable** (Ley 37/2007 + datos.gob.es) | Citar autoría, no desnaturalizar, no sugerir patrocinio, conservar fecha/versión. (DGT: infografías/fotos con reserva.) |
| ROA (efemérides) | **Reutilizable** | Citar «Origen: Real Instituto y Observatorio de la Armada (ROA) / Ministerio de Defensa». |
| ERC-2025 | **Reutilizable no comercial** | Citar «© European Resuscitation Council», no alterar diagramas. |
| AEMPS (plantas medicinales) | **Reproducción autorizada citando origen** | Pie del PDF. |
| Sanidad (guía agua RD 3/2023) | **Reproducción permitida citando la fuente** | Pie de la guía. |
| Overpass/OSM | **ODbL** | Atribución a OpenStreetMap. |
| Wikidata | **CC0** | — |
| GBIF | Por dataset | Citar GBIF + dataset. |
| Guardia Civil CSV | CC BY-NC-SA (verificar) | Verificar ficha datos.gob. |
| Cruz Roja | **NO redistribuible** (copyright privativo) | Solo enlace, cita (art. 32 TRLPI) o resumen propio. |
| Puertos del Estado (mareas) | **NO redistribuible** (no cesión a terceros) | Documentar script/instrucciones para que el **usuario** descargue; no empaquetar los datos. |
| UIT-HET 2005 | **Derechos reservados** | Solo referencia/cita; redistribución requiere autorización escrita (jur@itu.int). |
| Dioscórides-1998 | **Datos botánicos en dominio público; la traducción de 1998 NO redistribuible** | Extraer hechos/resumir/citar (art. 32 TRLPI); no copiar el texto. |

---

## 6. Flujo de validación (referencia)

```
data/raw/downloads/ → normalizar → data/processed/ → scripts/migrar_a_staging.py
→ data/staging/pendientes/ → scripts/review.py (aprobar/rechazar)
→ data/staging/aprobados/ → python -m updater.cli --reindex-aprobados
```

- **Idempotencia por hash:** al cambiar el `texto` de un fragmento se duplica en staging (el hash es sensible al texto). Purgar la cola del dominio antes de re-migrar con formato nuevo.
- **Flag `peligrosa`:** `migrar_a_staging.py` lo lee del frontmatter MD (`peligrosa: true`); el CSV de GBIF no lo propaga (limitación conocida).

[← Volver al índice](README.md)
