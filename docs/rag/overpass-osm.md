# Ficha de fuente/conector: OpenStreetMap (Overpass API)

[← Volver al índice](README.md)

> **Estado:** `en_validacion` — conector operativo, pero depende de conexión y debe fijarse en CSV offline.
> **Tipo:** conector transversal complementario. **Prioridad:** P1 (apoyo a directorios y territorio).
> **Destino:** tablas geoespaciales (POIs); nunca embeddings de coordenadas brutas.

---

## 1. Objetivo y límites

Obtener puntos de interés (POIs) de auxilio y supervivencia dentro del `BBOX` provincial mediante Overpass QL: farmacias, centros sanitarios, fuentes de agua potable, puestos de socorro, comisarías, bomberos, desfibriladores y helisuperficies.

- **Uso:** complemento de `directorios-emergencia.md`, `territorio-medio-natural.md` y `municipios-geografia.md`.
- **Límite:** OSM es cartografía colaborativa. Un POI no acredita apertura, teléfono vigente ni servicio real. Para contactos y urgencias prevalece la fuente oficial competente. No indexar coordenadas como datos de urgencia sin contraste.

---

## 2. Registro de fuentes

### `OSM-OVERPASS` — OpenStreetMap / Overpass API (principal)

- **Organismo / autoridad:** OpenStreetMap Foundation y comunidad global.
- **URL de catálogo / portal:** https://overpass-api.de
- **URL de descarga / API:** `https://overpass-api.de/api/interpreter` (Overpass QL).
- **Qué obtener:** nodos/vías con `amenity`, `emergency` y etiquetas asociadas dentro del `BBOX`.
- **Formato y adquisición:** `API` (XML/JSON Overpass).
- **Fiabilidad:** `media` (colaborativa; revisada por comunidad).
- **Licencia:** ODbL 1.0 — requiere atribución "© Colaboradores de OpenStreetMap".
- **Cadencia:** dinámica; volcado puntual a CSV para operación offline.
- **Notas de estabilidad:** respetar rate limits, cabeceras y `UPDATER_USER_AGENT`.

### `DIPUCADIZ-DATOS` — Datos abiertos de Diputación de Cádiz (contraste oficial)

- **Organismo / autoridad:** Diputación Provincial de Cádiz y entidades publicadoras.
- **URL de catálogo:** https://datosabiertos.dipucadiz.es/ (portal de datos abiertos; endpoint CKAN en revisión)
- **API de recursos (plantilla):** https://apirtod.dipucadiz.es/api/datos/<id>.json (sustituir `<id>` por el identificador real)
- **Qué obtener:** equipamientos públicos (policía local, protección civil, sedes) con mantenimiento identificable.
- **Formato y adquisición:** `JSON/CSV` (CKAN).
- **Fiabilidad:** `alta` si el publicador es la administración competente.
- **Licencia:** por dataset (registrar por recurso).
- **Cadencia:** mensual.

### `SAS-CENTROS` — Servicio Andaluz de Salud (contraste sanitario)

- **Organismo / autoridad:** Servicio Andaluz de Salud.
- **URL de catálogo:** https://www.sspa.juntadeandalucia.es/servicioandaluzdesalud/el-sas/servicios-y-centros/informacion-por-centros
- **Qué obtener:** hospitales, centros de salud y consultorios oficiales para contrastar los POIs sanitarios de OSM.
- **Formato y adquisición:** `HTML` (identificar recurso reutilizable antes de implementar).
- **Fiabilidad:** `alta` para centros SAS.
- **Licencia:** `pendiente de verificar`.
- **Cadencia:** mensual.

### `DERA` — Datos Espaciales de Referencia de Andalucía (contraste cartográfico)

- **Organismo / autoridad:** IECA.
- **URL de catálogo:** https://www.juntadeandalucia.es/institutodeestadisticaycartografia/dega/datos-espaciales-de-referencia-de-andalucia-dera/descarga-de-informacion
- **Qué obtener:** infraestructuras y equipamientos de referencia para validar geometría y localización.
- **Formato y adquisición:** `WFS/GPKG`.
- **Fiabilidad:** `alta`.
- **Licencia:** verificar por conjunto.
- **Cadencia:** trimestral.

### `IGN-CNIG` — Cartografía nacional de referencia

- **Organismo / autoridad:** Instituto Geográfico Nacional / CNIG.
- **URL de catálogo:** https://centrodedescargas.cnig.es/CentroDescargas/index.jsp
- **Qué obtener:** equipamientos y toponimia oficial de contraste para validar coordenadas y denominaciones.
- **Formato y adquisición:** `CSV/SHP/GPKG`.
- **Fiabilidad:** `alta`.
- **Licencia:** verificar por producto.
- **Cadencia:** anual.

---

## 3. Bloques y mapeo

| Bloque destino | Fuente | Salida normalizada | Destino (`data/processed/`) | Validación |
|---|---|---|---|---|
| Farmacias | OSM + SAS | nombre, municipio, lat/lon, teléfono si consta | `csv/puntos_auxilio_cadiz.csv` | Humana |
| Centros sanitarios | OSM + SAS | tipo, nombre, coordenadas, fuente | `csv/puntos_auxilio_cadiz.csv` | Humana |
| Agua potable | OSM + DERA | nombre, coordenadas, estado | `csv/puntos_agua_cadiz.csv` | Humana |
| Seguridad/rescate | OSM + DIPUCADIZ | tipo, nombre, coordenadas | `csv/puntos_auxilio_cadiz.csv` | Humana |
| Desfibriladores | OSM | coordenadas, acceso | `csv/desfibriladores_cadiz.csv` | Humana |
| Helisuperficies | OSM + DERA | coordenadas, uso | `csv/helisuperficies_cadiz.csv` | Humana |

---

## 4. Auditoría del conector existente

`src/updater/sources/overpass.py` (`OverpassSource`) consulta la API en cada ejecución. Es válido como **herramienta de extracción**, pero su salida no debe indexarse directamente: hay que fijarla en CSV estructurado con `snapshot_id`, fecha y fuente de contraste. No conserva atribución ODbL explícita por fila; debe añadirse.

---

## 5. Instantáneas y transformación

```text
data/raw/downloads/overpass-osm/<AAAA-MM-DD>/
├── overpass/consulta_<tema>.json
├── sas/centros.<html|json>
├── diputacion/<dataset>.<json|csv>
├── dera/<capa>.<gpkg>
├── LICENSE.txt
└── MANIFEST.json
```

Guardar la consulta Overpass exacta, el `BBOX`, el timestamp y las cabeceras de licencia. Normalizar a WGS84 y conservar CRS original.

---

## 6. Calidad, presupuesto y actualización

- Validar coordenadas dentro de provincia, duplicados por proximidad+nombre, y que ningún contacto se publique solo desde OSM.
- Rechazar POIs sin fuente de contraste para urgencias y teléfonos no institucionales.
- Revisión humana para centros sanitarios, helisuperficies y puntos de agua.
- Presupuesto: cientos de filas; no requiere embeddings.
- Actualización trimestral con diff; mantener CSV offline como única fuente en operación.

---

## 7. Historial de versiones

| Fecha | Estado | Autor / Revisor | Cambio |
|---|---|---|---|
| 2026-08-27 | `implementada` | equipo_cartografia_osm | Conector Overpass con BBOX y rate limiting. |
| 2026-08-28 | `en_validacion` | Agente Zed | Modernizada a plantilla; añadidas fuentes de contraste y política de volcado offline. |
