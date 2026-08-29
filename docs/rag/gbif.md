# Ficha de fuente/conector: GBIF (biodiversidad global)

[← Volver al índice](README.md)

> **Estado:** `en_validacion` — conector operativo, pero con ruido taxonómico; debe filtrarse y fijarse.
> **Tipo:** conector transversal complementario. **Prioridad:** P2 (apoyo a flora-fauna).
> **Destino:** tablas de presencia; solo las fichas de riesgo se convierten en RAG.

---

## 1. Objetivo y límites

Recuperar ocurrencias biológicas georreferenciadas dentro del `BBOX` provincial para ampliar la cobertura de `flora-fauna.md`.

- **Uso:** detección de candidatos de especies presentes; nunca sustituye la ficha de riesgo validada por biólogo.
- **Límite:** una ocurrencia no demuestra abundancia, peligro, comestibilidad ni identificación individual. GBIF introduce ruido taxonómico (sinónimos, registros duplicados, coordenadas imprecisas). No indexar nombres científicos sin filtro ni afirmaciones de riesgo derivadas solo de presencia.

---

## 2. Registro de fuentes

### `GBIF-OCCURRENCE` — GBIF API (principal)

- **Organismo / autoridad:** Global Biodiversity Information Facility y nodo nacional GBIF.ES (CSIC).
- **URL de catálogo / portal:** https://www.gbif.org
- **URL de descarga / API:** `https://api.gbif.org/v1/occurrence/search`
- **Qué obtener:** registros de presencia con taxón, coordenadas, fecha, dataset y licencia por registro.
- **Formato y adquisición:** `API` (REST JSON, paginado).
- **Fiabilidad:** `variable` (por dataset/registro); no eleva a `alta` por sí sola.
- **Licencia:** CC BY 4.0 / CC0 según dataset; conservar por registro.
- **Cadencia:** dinámica; volcado puntual filtrado.

### `REDIAM-FLORA` — REDIAM (contraste oficial flora)

- **Organismo / autoridad:** Red de Información Ambiental de Andalucía.
- **URL de catálogo:** https://www.juntadeandalucia.es/medioambiente/mapwms/REDIAM_WFS_localizacion_flora_andaluza?
- **Qué obtener:** localizaciones oficiales de flora andaluza filtradas por `BBOX`.
- **Formato y adquisición:** `WFS/GML`.
- **Fiabilidad:** `alta` para presencia oficial.
- **Licencia:** `pendiente de verificar` por metadatos.
- **Cadencia:** trimestral.

### `EIDOS` — Banco de Datos de la Naturaleza (contraste taxonómico)

- **Organismo / autoridad:** MITECO.
- **URL de catálogo:** https://www.miteco.gob.es/es/biodiversidad/servicios/banco-datos-naturaleza/eidos_acceso.html
- **Qué obtener:** nombres científicos/vernáculos y taxonomía oficial para normalizar registros GBIF.
- **Formato y adquisición:** `portal/base de datos`.
- **Fiabilidad:** `alta` para taxonomía nacional.
- **Licencia:** `pendiente de verificar` por recurso.
- **Cadencia:** trimestral.

### `JUNTA-PECES` — Manual de identificación pesquera (contraste marino)

- **Organismo / autoridad:** Consejería de Agricultura, Pesca, Agua y Desarrollo Rural.
- **URL de catálogo:** https://www.juntadeandalucia.es/organismos/agriculturapescaaguaydesarrollorural/areas/pesca-acuicultura/comercializacion/paginas/espinteres-manualident.html
- **Qué obtener:** identificación de especies pesqueras para contrastar registros marinos.
- **Formato y adquisición:** `HTML/PDF`.
- **Fiabilidad:** `alta` para identificación; no determina seguridad de consumo.
- **Licencia:** `pendiente de verificar`.
- **Cadencia:** anual.

### `IUCN-REDLIST` — Lista Roja de Especies Amenazadas

- **Organismo / autoridad:** Unión Internacional para la Conservación de la Naturaleza (UICN).
- **URL de catálogo:** https://www.iucnredlist.org/
- **API:** https://api.iucnredlist.org/ (requiere token).
- **Qué obtener:** categoría de amenaza y estado de conservación para contrastar la relevancia de las especies detectadas.
- **Formato y adquisición:** `API/HTML`.
- **Fiabilidad:** `alta` para conservación.
- **Licencia:** verificar términos de uso de la API.
- **Cadencia:** anual.

---

## 3. Bloques y mapeo

| Bloque destino | Fuente | Salida normalizada | Destino (`data/processed/`) | Validación |
|---|---|---|---|---|
| Presencia taxonómica | GBIF + EIDOS | taxón normalizado, lat/lon, fecha, precisión, dataset | `csv/presencia_biodiversidad.csv` | Automática |
| Flora | GBIF + REDIAM | taxón, coordenadas, fuente | `csv/presencia_biodiversidad.csv` | Humana |
| Fauna | GBIF + EIDOS | taxón, coordenadas, fuente | `csv/presencia_biodiversidad.csv` | Humana |
| Especies marinas | GBIF + Junta | taxón, coordenadas, identificación | `csv/presencia_biodiversidad.csv` | Humana |

Solo las especies priorizadas como peligrosas/tóxicas pasan a `flora-fauna.md` y se convierten en fragmentos RAG con revisión biológica.

---

## 4. Auditoría del conector existente

`src/updater/sources/gbif.py` (`GbifSource`) consulta la API con paginación y filtros de `BBOX`, pero introduce nombres científicos sin filtrar y no conserva licencia por registro ni normaliza taxonomía. Debe permanecer como herramienta de extracción; su salida se consolida y filtra antes de publicar.

---

## 5. Instantáneas y transformación

```text
data/raw/downloads/gbif/<AAAA-MM-DD>/
├── gbif/occurrences_<taxon|grupo>.json
├── rediam/flora.gml
├── eidos/<recurso>
├── junta/peces.<pdf|html>
└── MANIFEST.json
```

Guardar la consulta exacta (filtros, `BBOX`, taxones), el timestamp y la licencia por registro. Normalizar taxonomía contra EIDOS y deduplicar por taxón+coordenadas+dataset.

---

## 6. Calidad, presupuesto y actualización

- Validar coordenadas, taxonomía, precisión, duplicados y licencia por registro.
- Rechazar registros sin dataset, coordenadas fuera de rango o taxones no resolubles.
- Revisión biológica para especies priorizadas; no publicar "comestible/peligroso" desde ocurrencia.
- Presupuesto: tabla compacta de candidatos; no copiar todas las ocurrencias a la Pi.
- Actualización trimestral diferencial con diff.

---

## 7. Historial de versiones

| Fecha | Estado | Autor / Revisor | Cambio |
|---|---|---|---|
| 2026-08-27 | `implementada` | equipo_biodiversidad_gbif | Conector REST con paginación, BBOX y normalización. |
| 2026-08-28 | `en_validacion` | Agente Zed | Modernizada a plantilla; añadidas fuentes de contraste y filtro taxonómico. |
