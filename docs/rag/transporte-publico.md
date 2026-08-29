# Ficha de planificación: transporte público

[← Volver al índice](README.md)

> **Estado:** `en-normalizacion` — GTFS unificado CTAN descargado, filtrado por consorcios de Cádiz y normalizado a CSV; Renfe/ADIF pendientes.
> **Prioridad:** P1. **Destino:** tablas estructuradas; RAG solo para explicaciones estables.
> **Origen en `valorar.md`:** líneas 34 y 35.

## 1. Objetivo y límites

Disponer offline de paradas, estaciones, líneas, recorridos y horarios planificados de tren, autobús y, si está incluido en el consorcio, transporte marítimo de la provincia configurada. Debe responder con coincidencias exactas y mostrar la fecha de validez de la instantánea.

No puede informar incidencias, retrasos, cancelaciones ni disponibilidad en tiempo real sin conexión. Nunca se presentará un horario antiguo como vigente: si la consulta cae fuera del calendario descargado, se indicará la limitación.

## 2. Registro de fuentes

### `RENFE-GTFS-CERCANIAS`

- **Organismo:** Renfe Viajeros.
- **Catálogo:** https://data.renfe.com/es/dataset/horarios-cercanias
- **Qué obtener:** paquete GTFS de Cercanías aplicable al núcleo de Cádiz: agencias, paradas, rutas, viajes, calendarios, excepciones, horarios y formas si están disponibles.
- **Formato:** ZIP con CSV GTFS.
- **Núcleo Cádiz (verificado 2026-08-28):** `route_id` con prefijo `31T` (12 rutas: C-1, C-1a y T-1 Trambahía). Los prefijos `10T` (Madrid) y `30T` (Sevilla) se descartan; `30T` roza el BBOX por Lebrija/Las Cabezas. `stop_times.txt` (~287 MB) se filtra en streaming, sin cargarlo en memoria.
- **Fiabilidad:** alta para planificación publicada por el operador.
- **Licencia:** comprobar la licencia indicada en el catálogo y conservarla con cada instantánea; estado actual `pendiente_de_verificar`.
- **Frecuencia observada:** no asumida; descubrir `Last-Modified`, metadatos y periodo de `calendar_dates.txt`.
- **Cadencia propuesta:** semanal y antes de periodos festivos.
- **Estabilidad:** la URL final del recurso puede cambiar; resolverla desde el catálogo, no hardcodearla.

### `CTAN-GTFS-JSON`

- **Organismo:** Consorcios de Transporte Metropolitano de Andalucía, Junta de Andalucía.
- **API:** https://api.ctan.es/
- **Condiciones:** http://api.ctan.es/avisolegal.html
- **Ámbitos:** Consorcio Bahía de Cádiz (`agency_id = CMTBC`) y Consorcio Campo de Gibraltar (`agency_id = CTMCG`). **Verificado 2026-08-28:** en el GTFS unificado, `agency_id` es **textual** (no numérico); la lista real de consorcios incluye `CTMAS`, `CTMAM`, `CTAG`, `CMTBC`, `CTHU`, `CTJA`, `CTAL`, `CTMCG`, `CTMAC`. Se filtran únicamente `CMTBC` (59 rutas) y `CTMCG` (15 rutas).
- **Qué obtener:** operadores, líneas, paradas, expediciones, horarios y ficheros GTFS/JSON ofrecidos por la API; incluir transporte marítimo solo si aparece oficialmente en esos datos.
- **Formato:** JSON y GTFS generado diariamente.
- **Fiabilidad:** alta para servicios consorciados; servicios municipales o interurbanos externos pueden faltar.
- **Licencia:** aplicar el aviso legal de CTAN; verificar expresamente redistribución offline y atribución.
- **Cadencia propuesta:** diaria durante la actualización, conservando solo versiones necesarias.
- **Estabilidad:** documentar endpoints reales desde la especificación de la API; respetar límites aunque no se publiquen.

### `OPERADORES-LOCALES` — Cobertura residual

- **Organismo:** ayuntamientos y operadores públicos competentes.
- **Punto de descubrimiento:** portales oficiales municipales y catálogo de datos abiertos de Diputación: https://datosabiertos.dipucadiz.es/ (API real = RTOD `https://apirtod.dipucadiz.es/api/collections.json`; ver T6)
- **Qué obtener:** únicamente líneas/paradas no cubiertas por Renfe o CTAN.
- **Formato:** GTFS/CSV/JSON preferente; PDF solo como último recurso y no para horarios automatizados.
- **Fiabilidad:** alta si es publicación del operador; media si requiere transcripción.
- **Licencia:** pendiente de verificar por conjunto.
- **Cadencia:** según el operador.

### `ADIF-ESTACIONES` — Infraestructura ferroviaria

- **Organismo:** ADIF / ADIF Alta Velocidad.
- **Datos espaciales (IDEADIF):** https://ideadif.adif.es/
- **WFS resuelto (2026-08-28):** `https://ideadif.adif.es/services/wfs` → capa `tn-ra:RailwayStationNode` (INSPIRE 3.0). Requiere cabecera **Safari macOS + cortesía** (antes anti-bot). 52 estaciones/instalaciones de Cádiz normalizadas → `estaciones_ferrocarril_cadiz.csv`.
- **Portal viajeros:** https://www.adif.es/viajeros
- **Qué obtener:** catálogo de estaciones, denominación oficial, coordenadas, servicios y accesibilidad para cruzar con las paradas GTFS de Renfe.
- **Formato:** WFS/INSPIRE (XML); coord. EPSG:4258 (≈ WGS84).
- **Fiabilidad:** alta para infraestructura; no incluye horarios de servicio.
- **Licencia:** verificar condiciones de uso de los datos de ADIF.
- **Cadencia:** trimestral.

### `PUERTOS-BAHIA` — Transporte marítimo

- **Organismo:** Autoridad Portuaria de la Bahía de Cádiz / Consorcio de Transportes.
- **Punto de descubrimiento:** portal oficial de la APBC y consorcios metropolitanos.
- **Qué obtener:** líneas marítimas regulares (si existen datos oficiales reutilizables), embarcaderos y paradas.
- **Formato:** HTML/CSV/GTFS si se publica.
- **Fiabilidad:** alta si es publicación oficial; si no hay dataset, se excluye y se documenta la ausencia.
- **Licencia:** pendiente de verificar.
- **Cadencia:** según el operador.

## 3. Modelo y mapeo

| Tabla | GTFS/origen | Campos mínimos | Reglas |
|---|---|---|---|
| `transport_agencies` | `agency.txt` | fuente, agency_id, nombre, URL, zona horaria | Clave compuesta por fuente |
| `transport_stops` | `stops.txt` | stop_id, nombre, lat, lon, tipo, parent | WGS84 y filtro territorial |
| `transport_routes` | `routes.txt` | route_id, agency_id, tipo, nombre | Conservar modo GTFS |
| `transport_trips` | `trips.txt` | trip_id, route_id, service_id, destino | No convertir cada viaje en embedding |
| `transport_stop_times` | `stop_times.txt` | trip_id, secuencia, llegada, salida | Admitir horas GTFS > 24:00 |
| `transport_services` | `calendar*` | service_id, días, inicio/fin, excepciones | Vigencia obligatoria |
| `transport_shapes` | `shapes.txt` | shape_id, secuencia, lat, lon | Simplificar para la Pi si procede |

Un registro conservará `snapshot_id`, proveedor, licencia, fecha de descarga y periodo cubierto. Duplicados entre fuentes no se fusionarán sin una regla explícita de autoridad.

## 4. Instantáneas

```text
data/raw/downloads/transporte-publico/<AAAA-MM-DD>/
├── renfe-cercanias/gtfs.zip
├── ctan-2/gtfs.zip
├── ctan-5/gtfs.zip
├── catalogos/
├── LICENSE.txt
└── MANIFEST.json
```

Validar el ZIP contra las tablas obligatorias de GTFS, codificación, claves externas, coordenadas y rango temporal antes de normalizar. Filtrar por `PROVINCIA`, `BBOX` y relaciones de rutas, no por nombres hardcodeados.

## 5. Calidad, presupuesto y actualización

- Completitud: todas las referencias GTFS deben resolver; detectar servicios sin calendario y paradas fuera del área.
- Actualidad: bloquear consultas fuera de `feed_start_date/feed_end_date` o del rango derivado.
- Pruebas: transbordo, servicio tras medianoche, excepción festiva, estación homónima, parada sin horario y fecha fuera de cobertura.
- Presupuesto: importar solo los dos consorcios y el núcleo pertinente; índices por parada, ruta, fecha y secuencia. No cargar todos los horarios en RAM.
- En cada actualización, comparar periodo, conteos y cambios de IDs; mantener instantánea anterior para rollback.

## 6. Pendientes para aprobar

- [x] Verificar licencias de Renfe y CTAN y posibilidad de copia offline. *(CTAN: pendiente de confirmar redistribución; Renfe: pendiente)*
- [ ] Inventariar servicios municipales no cubiertos.
- [x] Confirmar endpoints y códigos de consorcio desde documentación oficial. *(`agency_id` textual: `CMTBC`/`CTMCG`)*
- [x] Medir tamaño real de tres paquetes GTFS. *(unificado CTAN descargado; Renfe 313 MB todo España — ver T7)*
- [ ] Definir mensaje de caducidad para consultas sin datos vigentes.

> **Geocodificación (2026-08-28):** las paradas de autobús, Cercanías y Trambahía se han asignado a su municipio mediante point-in-polygon contra los polígonos DERA (`g13_01_TerminoMunicipal`, EPSG:25830), con `scripts/geocodificar_transporte.py`. 395/397 paradas con municipio; 2 en `Secadero` quedan fuera (límite con Málaga). El municipio se inyecta en el texto del fragmento para que el RAG lo recupere.
