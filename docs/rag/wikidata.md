# Ficha de fuente/conector: Wikidata (grafo de conocimiento)

[← Volver al índice](README.md)

> **Estado:** `en_validacion` — conector operativo, pero debe fijarse en CSV y contrastarse.
> **Tipo:** conector transversal complementario. **Prioridad:** P2 (apoyo a geografía y patrimonio).
> **Destino:** tablas estructuradas; metadatos, no narrativa.

---

## 1. Objetivo y límites

Recuperar entidades y metadatos estructurados de la provincia mediante consultas SPARQL: hospitales, faros, municipios, cumbres y accidentes geográficos con identificadores Q y propiedades.

- **Uso:** complemento de `municipios-geografia.md`, `directorios-emergencia.md`, `historia-patrimonio.md` y `astronomia-mareas-orientacion.md`.
- **Límite:** Wikidata es un grafo colaborativo con inconsistencias. Nunca prevalece sobre una fuente oficial para teléfonos, riesgo médico o vigencia legal. No indexar afirmaciones sin referencia (`sources`) ni extraer narrativa histórica.

---

## 2. Registro de fuentes

### `WIKIDATA-SPARQL` — Wikidata SPARQL (principal)

- **Organismo / autoridad:** Fundación Wikimedia y comunidad Wikidata.
- **URL de catálogo / portal:** https://query.wikidata.org
- **URL de descarga / API:** `https://query.wikidata.org/sparql?query=...&format=json`
- **Qué obtener:** entidades (hospitales, faros, municipios, cumbres) con identificadores Q y propiedades seleccionadas.
- **Formato y adquisición:** `API` (SPARQL JSON).
- **Fiabilidad:** `media`.
- **Licencia:** CC0 1.0 (dominio público) para los datos estructurados.
- **Cadencia:** dinámica; volcado puntual.
- **Notas de estabilidad:** respetar `User-Agent` y límites del endpoint.

### `IGN-CNIG` — Instituto Geográfico Nacional (contraste oficial)

- **Organismo / autoridad:** IGN / CNIG.
- **URL de catálogo:** https://centrodedescargas.cnig.es/CentroDescargas/index.jsp
- **Qué obtener:** nomenclátor, altitudes y topónimos oficiales para contrastar entidades de Wikidata.
- **Formato y adquisición:** `CSV/SHP/GPKG`.
- **Fiabilidad:** `alta`.
- **Licencia:** verificar por producto.
- **Cadencia:** anual.

### `IAPH-OPEN-DATA` — Instituto Andaluz del Patrimonio Histórico (contraste patrimonial)

- **Organismo / autoridad:** IAPH.
- **URL de catálogo:** https://www.juntadeandalucia.es/organismos/iaph/areas/documentacion-patrimonio/guia-digital.html
- **API:** https://guiadigital.iaph.es/store/apis/info?name=open-data-iaph&provider=guiadigital&version=1.0
- **Qué obtener:** entidades patrimoniales oficiales para contrastar faros/hitos culturales.
- **Formato y adquisición:** `API`.
- **Fiabilidad:** `alta` para inventario andaluz.
- **Licencia:** verificar por separado metadatos e imágenes.
- **Cadencia:** trimestral.

### `PUERTOS-ESTADO` — Autoridad portuaria (contraste de faros)

- **Organismo / autoridad:** Puertos del Estado.
- **URL de catálogo:** https://portuscopia.puertos.es/
- **Qué obtener:** faros y señales marítimas oficiales para contrastar alcances/alturas.
- **Formato y adquisición:** `HTML` (verificar reutilización).
- **Fiabilidad:** `alta`; ver condiciones de reutilización.
- **Licencia:** `pendiente de verificar`; posible restricción.
- **Cadencia:** anual.

### `SAS-CENTROS` — Servicio Andaluz de Salud (contraste sanitario)

- **Organismo / autoridad:** Servicio Andaluz de Salud.
- **URL de catálogo:** https://www.sspa.juntadeandalucia.es/servicioandaluzdesalud/el-sas/servicios-y-centros/informacion-por-centros
- **Qué obtener:** hospitales y centros sanitarios oficiales para contrastar las entidades sanitarias de Wikidata.
- **Formato y adquisición:** `HTML` (identificar recurso reutilizable).
- **Fiabilidad:** `alta`.
- **Licencia:** `pendiente de verificar`.
- **Cadencia:** mensual.

---

## 3. Bloques y mapeo

| Bloque destino | Fuente | Salida normalizada | Destino (`data/processed/`) | Validación |
|---|---|---|---|---|
| Hospitales | Wikidata + SAS | Q-ID, nombre, coordenadas, camas | `csv/hospitales_cadiz.csv` | Humana |
| Faros | Wikidata + Puertos | nombre, coordenadas, alcance, altura | `csv/faros_cadiz.csv` | Humana |
| Municipios | Wikidata + IGN | Q-ID, nombre, coordenadas | `csv/municipios_cadiz.csv` | Automática |
| Cumbres | Wikidata + IGN | nombre, altitud, coordenadas | `csv/cumbres_cadiz.csv` | Humana |

---

## 4. Auditoría del conector existente

`src/updater/sources/wikidata.py` (`WikidataSource`) consulta SPARQL en vivo. Su salida es heterogénea y carece de `snapshot_id`, fecha de consulta y referencia por afirmación. Debe fijarse en CSV y contrastarse antes de publicar.

---

## 5. Instantáneas y transformación

```text
data/raw/downloads/wikidata/<AAAA-MM-DD>/
├── sparql/consulta_<tema>.json
├── ign/<producto_contraste>
├── iaph/records.<json|xml>
├── puertos/<faro>.<html>
└── MANIFEST.json
```

Guardar la consulta SPARQL exacta, el timestamp y la versión del resultado. Normalizar a WGS84; conservar el Q-ID como clave de trazabilidad.

---

## 6. Calidad, presupuesto y actualización

- Validar coordenadas, IDs únicos, y que toda entidad crítica tenga fuente de contraste oficial.
- Rechazar entidades sin referencia o con datos contradictorios sin resolver.
- Revisión humana para hospitales, faros y cumbres.
- Presupuesto: pocos cientos de filas; no requiere embeddings.
- Actualización trimestral con diff y fijación en CSV.

---

## 7. Historial de versiones

| Fecha | Estado | Autor / Revisor | Cambio |
|---|---|---|---|
| 2026-08-27 | `implementada` | equipo_datos_enlazados | Conector SPARQL para entidades de Cádiz. |
| 2026-08-28 | `en_validacion` | Agente Zed | Modernizada a plantilla; añadidas fuentes de contraste y política de fijado en CSV. |
