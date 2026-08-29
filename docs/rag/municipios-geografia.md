# Ficha de planificación: municipios, núcleos y topónimos

[← Volver al índice](README.md)

> **Estado:** `en_validacion` — existe un conector de 45 municipios, pendiente de contrastar y ampliar.
> **Prioridad:** P1. **Destino:** tablas geoespaciales; RAG solo para descripciones con fuente.
> **Origen en `valorar.md`:** líneas 3 y 44.

## 1. Objetivo y límites

Cubrir toda la provincia configurada con municipios, entidades de población, núcleos, diseminados/pedanías y topónimos oficiales, incluyendo códigos estables y coordenadas representativas. Esta base relacionará consultas, directorios, transporte y patrimonio con el territorio correcto.

Una coordenada de núcleo no representa todo el término municipal ni es un punto de rescate. Las comarcas o descripciones turísticas no se presentarán como divisiones administrativas oficiales si la fuente no lo indica.

## 2. Registro de fuentes

### `IECA-NOMENCLATOR`

- **Organismo:** Instituto de Estadística y Cartografía de Andalucía.
- **Portal:** https://www.juntadeandalucia.es/institutodeestadisticaycartografia/dega/nomenclator-de-entidades-y-nucleos-de-poblacion-de-andalucia
- **Qué obtener:** municipios, entidades colectivas/singulares, núcleos y diseminados, códigos, nombres y población/edición si están publicados.
- **Formato:** descarga o consulta oficial; determinar recurso concreto durante implementación.
- **Fiabilidad:** alta para entidades y núcleos andaluces.
- **Licencia:** pendiente de verificar en metadatos del conjunto.
- **Cadencia:** anual o por nueva edición.

### `NGA-WFS` — Nomenclátor Geográfico de Andalucía

- **Organismo:** IECA/Infraestructura de Datos Espaciales de Andalucía.
- **WFS:** https://www.ideandalucia.es/wfs-nga/services?
- **Qué obtener:** topónimos, clasificación, coordenadas/geometría y códigos disponibles; descubrir capas con `GetCapabilities`.
- **Formato:** WFS/GML.
- **Fiabilidad:** alta como nomenclátor geográfico oficial.
- **Licencia:** pendiente de verificar.
- **Cadencia:** trimestral.

### `DERA-LIMITES`

- **Organismo:** IECA.
- **Descargas:** https://www.juntadeandalucia.es/institutodeestadisticaycartografia/dega/datos-espaciales-de-referencia-de-andalucia-dera/descarga-de-informacion
- **WFS de límites:** https://www.ideandalucia.es/services/DERA_g13_limites_administrativos/wfs?
- **Qué obtener:** límites provincial y municipal, códigos y edición.
- **Formato:** GPKG/WFS.
- **Fiabilidad:** alta.
- **Licencia:** verificar por conjunto.
- **Cadencia:** por edición, comprobación trimestral.

### `IGN-CNIG` — Contraste nacional

- **Organismo:** Instituto Geográfico Nacional / Centro Nacional de Información Geográfica.
- **Centro de descargas:** https://centrodedescargas.cnig.es/CentroDescargas/index.jsp
- **Qué obtener:** nomenclátor y cartografía nacional solo para contraste de nombres, altitud o elementos fronterizos.
- **Formato:** CSV/SHP/GPKG según producto.
- **Fiabilidad:** alta.
- **Licencia:** verificar condiciones de uso del producto concreto.
- **Cadencia:** anual.

### `INE-POBLACION` — Población oficial por municipio

- **Organismo:** Instituto Nacional de Estadística.
- **Consulta:** https://www.ine.es/dynt3/inebase/es/index.htm?padre=525
- **Qué obtener:** cifras oficiales de población por municipio/núcleo y año, para enriquecer `municipalities`/`population_entities` con dato demográfico trazable.
- **Formato:** tablas y descargas CSV/PC-Axis.
- **Fiabilidad:** alta para estadística oficial.
- **Licencia:** verificar condiciones de reutilización del INE y atribución.
- **Cadencia:** anual (padrón continuo).

## 3. Modelo y mapeo

| Tabla | Campos mínimos | Fuente preferente | Regla |
|---|---|---|---|
| `municipalities` | código INE/IECA, nombre, provincia, geometría, edición | IECA/DERA | Deben ser 45 solo cuando `PROVINCIA=Cádiz` |
| `population_entities` | código jerárquico, nombre, tipo, municipio, población/año | IECA | Conservar jerarquía |
| `place_names` | id, nombre, variantes, tipo, lat/lon/geometría, fuente | NGA | No deduplicar solo por texto |
| `administrative_boundaries` | id, nivel, geometría, CRS, vigencia | DERA | Validar topología |
| `elevation_points` | id, nombre, altitud, referencia vertical, geometría | IGN/IECA | No mezclar altitud media y puntual |

Las coordenadas se almacenan en WGS84 para consulta y con CRS original en metadatos. Los alias se mantienen separados del nombre oficial.

## 4. Auditoría del conector existente

`src/updater/sources/municipios_cadiz.py` contiene 45 municipios y cuatro puntos escritos a mano. No conserva códigos oficiales ni procedencia por coordenada, fija Cádiz en los datos y mezcla geografía con descripciones narrativas. También asigna licencia y validación no demostradas y usa la fecha de ejecución como validación.

El conector puede servir como inventario de pruebas, pero no como fuente de verdad. Su contenido deberá compararse registro a registro y migrarse a datos estructurados parametrizados.

## 5. Instantáneas

```text
data/raw/downloads/municipios-geografia/<AAAA-MM-DD>/
├── ieca/nomenclator.<csv|xlsx|json>
├── nga/toponimos.gml
├── dera/limites.<gpkg|gml>
├── ign/<producto_contraste>
└── MANIFEST.json
```

Filtrar por código provincial o intersección espacial, nunca por una lista hardcodeada. Guardar consulta WFS, CRS, edición y hash.

## 6. Calidad, presupuesto y actualización

- Validar códigos únicos, relaciones padre-hijo, 45 municipios para Cádiz, geometrías, rangos y nombres vacíos.
- Revisar manualmente altas/bajas/cambios de entidad y discrepancias IECA/IGN.
- Pruebas: entidad homónima, pedanía/diseminado, topónimo fronterizo, punto fuera del término y cambio de nombre.
- Presupuesto: miles de topónimos y geometrías simplificadas, previsiblemente pocos MiB; originales fuera de la Pi.
- Actualización anual con diff por código; cambios de límites requieren revisión y rollback.

## 7. Pendientes para aprobar

- [ ] Identificar descargas y capas exactas del nomenclátor IECA/NGA.
- [ ] Verificar licencias por producto.
- [ ] Definir vocabulario de tipos de entidad y relación con municipios.
- [ ] Medir precisión/tamaño y tolerancia de simplificación.
- [ ] Planificar migración del conector heredado sin perder pruebas existentes.
