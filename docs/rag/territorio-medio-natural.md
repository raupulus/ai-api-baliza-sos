# Ficha de planificación: territorio y medio natural

[← Volver al índice](README.md)

> **Estado:** `propuesta` — sin importador geoespacial.
> **Prioridad:** P0 para agua/costa; P1 para espacios y senderos.
> **Destino:** tablas geoespaciales; RAG para descripciones y normas estables. **Origen:** líneas 38, 81 y 82 de `valorar.md`.

## 1. Objetivo y límites

Representar playas, costa, mar, ríos, afluentes, embalses, espacios naturales, senderos y equipamientos públicos de la provincia configurada. Permitirá búsquedas por nombre, municipio y proximidad cuando se disponga de coordenadas.

Una geometría no demuestra potabilidad, accesibilidad, apertura ni seguridad actual. No se inferirán rutas transitables, caudales, banderas de playa, incendios, cierres o nivel de embalses a partir de una instantánea sin datos en tiempo real.

## 2. Registro de fuentes

### `DERA` — Datos Espaciales de Referencia de Andalucía

- **Organismo:** Instituto de Estadística y Cartografía de Andalucía (IECA).
- **Descargas:** https://www.juntadeandalucia.es/institutodeestadisticaycartografia/dega/datos-espaciales-de-referencia-de-andalucia-dera/descarga-de-informacion
- **Servicios WFS:** familia `https://www.ideandalucia.es/services/DERA_g<grupo>_<tema>/wfs?`, desde relieve hasta límites administrativos; las capas concretas se descubrirán mediante `GetCapabilities`.
- **Qué obtener:** hidrografía, relieve, litoral, topónimos, infraestructuras y límites necesarios para filtrar el área.
- **Formato:** GPKG/servicios OGC según publicación.
- **Fiabilidad:** alta como cartografía autonómica de referencia.
- **Licencia:** verificar metadatos y condiciones del conjunto descargado; no generalizar una licencia a todas las capas.
- **Cadencia:** trimestral para catálogo y por edición para paquetes.

### `REDIAM-SENDEROS`

- **Organismo:** Red de Información Ambiental de Andalucía, Junta de Andalucía.
- **Servicio:** https://www.juntadeandalucia.es/medioambiente/mapwms/REDIAM_Equipamientos_Uso_Publico_Andalucia?
- **Qué obtener:** senderos señalizados, carriles cicloturistas, trazado, nombre, dificultad publicada y equipamientos como miradores, centros de visitantes, áreas recreativas o refugios.
- **Formato:** WFS para datos; WMS solo para inspección visual.
- **Fiabilidad:** alta para inventario publicado; no garantiza apertura o estado físico actual.
- **Licencia:** pendiente de verificar en metadatos/aviso de REDIAM.
- **Cadencia:** mensual; el catálogo ha publicado ediciones fechadas.

### `REDIAM-EENNPP`

- **Organismo:** REDIAM.
- **Servicio:** https://www.juntadeandalucia.es/medioambiente/mapwms/REDIAM_Espacios_Naturales_Protegidos?
- **Qué obtener:** límites y figura de parques, parajes, reservas, monumentos y otras protecciones.
- **Formato:** WFS/WMS.
- **Fiabilidad:** alta para delimitación oficial publicada.
- **Licencia:** pendiente de verificar.
- **Cadencia:** trimestral y tras cambios normativos.

### `DIPUCADIZ-DATOS` — Conjuntos provinciales complementarios

- **Organismo:** Diputación de Cádiz y entidades publicadoras de su catálogo.
- **Catálogo CKAN:** https://datosabiertos.dipucadiz.es/ (portal de datos abiertos). **Endpoint resuelto 2026-08-28:** API real = RTOD `https://apirtod.dipucadiz.es/api/collections.json`; CKAN `api/3` → 404 y `datos/<id>.json` → 500 hoy (ver T6).
- **API RTOD (plantilla):** https://apirtod.dipucadiz.es/api/datos/<id>.json (sustituir `<id>` por el identificador real)
- **Qué obtener:** playas, equipamientos u otros elementos solo cuando el conjunto indique entidad responsable, actualización y licencia.
- **Formato:** JSON/CSV/geográfico según conjunto.
- **Fiabilidad:** alta si el publicador es la administración competente; documentar por dataset.
- **Licencia:** la indicada por cada dataset, nunca heredada del catálogo.
- **Cadencia:** mensual para descubrir cambios.

### `JUNTA-SAIH` — Sistema Automático de Información Hidrológica (Andalucía)

- **Organismo:** Consejería competente en Agua, Junta de Andalucía.
- **Portal SAIH:** https://www.juntadeandalucia.es/medioambiente/portal/landing-page/-/asset_publisher/V4ouVkw30tT0/content/saih
- **Qué obtener:** red hidrográfica oficial, embalses y datos de nivel publicados de las cuencas andaluzas (Guadalete-Barbate, Mediterránea) como contraste del DERA.
- **Formato:** HTML/CSV; descubrir recursos reutilizables y fechas de lectura.
- **Fiabilidad:** alta para hidrografía y niveles publicados de Andalucía.
- **Licencia:** verificar por recurso; los datos de nivel requieren fecha de lectura y no se presentan como tiempo real.
- **Cadencia:** trimestral; niveles según publicación oficial.

## 3. Mapeo geoespacial

| Capa destino | Fuente preferente | Campos mínimos | Geometría | Uso |
|---|---|---|---|---|
| `watercourses` | DERA | id, nombre, tipo, jerarquía, vigencia | línea | Nombre/proximidad |
| `water_bodies` | DERA | id, nombre, tipo, estado descriptivo si existe | polígono | Embalses/lagunas |
| `coast_beaches` | DERA/Diputación | id, nombre, municipio, fuente | línea/polígono/punto | Costa/playas |
| `protected_areas` | REDIAM | id oficial, nombre, figura, norma, fecha | polígono | Ámbito protegido |
| `trails` | REDIAM | id, nombre, longitud publicada, dificultad, estado no inferido | línea | Ruta offline |
| `public_facilities` | REDIAM | id, tipo, nombre, coordenadas | punto | Equipamiento cercano |

Normalizar a WGS84 para intercambio y conservar CRS original. Validar geometrías, cortar por el límite provincial configurado y conservar elementos limítrofes relevantes con marca `interseca_bbox`.

## 4. Instantáneas

```text
data/raw/downloads/territorio-medio-natural/<AAAA-MM-DD>/
├── dera/<paquete_o_capa>.<gpkg|gml>
├── rediam/senderos_equipamientos.gml
├── rediam/espacios_naturales.gml
├── dipucadiz/<dataset>.<json|csv>
├── capabilities/
└── MANIFEST.json
```

Guardar `GetCapabilities`, consulta exacta, CRS y filtros junto al resultado. Simplificar geometrías solo en la salida derivada, con tolerancia documentada; nunca alterar el original.

## 5. Calidad, presupuesto y actualización

- Validar CRS, geometrías vacías/inválidas, coordenadas fuera de rango, duplicados por ID y topónimos sin municipio.
- Contrastar límites con IECA; diferencias importantes bloquean publicación.
- Revisión humana para etiquetas de potabilidad, peligrosidad, dificultad o comestibilidad; no se deducen de la capa.
- Pruebas: punto cerca de río, playa homónima, sendero que cruza provincia, espacio superpuesto y geometría sin nombre.
- Presupuesto: originales GPKG/GML quedan en el actualizador; la Pi recibe geometrías simplificadas e índices. Medir antes de decidir PostGIS frente a columnas compactas.
- Comparar IDs y geometrías por versión; cierres o avisos temporales requieren otra fuente y fecha de expiración.

## 6. Pendientes para aprobar

- [ ] Inventariar capas DERA exactas mediante `GetCapabilities`.
- [ ] Verificar licencias de DERA, REDIAM y cada dataset provincial.
- [ ] Definir tolerancias de simplificación y precisión mínima.
- [ ] Decidir motor espacial compatible con el presupuesto de la Pi.
- [ ] Asignar revisión de cartografía y uso público.
