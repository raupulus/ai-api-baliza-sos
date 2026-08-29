# Ficha de planificación: directorios de emergencia

[← Volver al índice](README.md)

> **Estado:** `propuesta` — sin importación ni datos validados.
> **Prioridad:** P0. **Destino:** tablas estructuradas; nunca embeddings para teléfonos/direcciones.
> **Origen en `valorar.md`:** líneas 58 y 71.

## 1. Objetivo y límites

Mantener un directorio offline verificable de números generales y dependencias de Guardia Civil, Policía Nacional, policías locales, Protección Civil, Cruz Roja, centros de salud y hospitales de toda la provincia configurada. Cada dato debe indicar autoridad, ámbito, fecha de comprobación y posible caducidad.

El fichero `data/csv/telefonos_emergencia_cadiz_municipios.csv`, generado previamente con IA, solo puede usarse como lista de candidatos para contrastar; nunca como fuente ni publicarse sin verificación individual. No almacenar contactos personales.

## 2. Registro de fuentes

### `GC-DEPENDENCIAS`

- **Organismo:** Guardia Civil, Ministerio del Interior.
- **CSV:** https://web.guardiacivil.es/.galleries/Documentos/listado-dependenciasde-atencion-ciudadania-Guardia-Civil.csv
- **Qué obtener:** denominación de dependencia, dirección, localidad, provincia, teléfonos, servicios y coordenadas si constan.
- **Formato:** CSV.
- **Fiabilidad:** alta; dataset oficial de dependencias de atención ciudadana.
- **Licencia:** datos.gob.es lo cataloga como CC BY-NC-SA 4.0; verificar esa ficha y conservar evidencia antes de reutilizar.
- **Cadencia:** mensual.

### `POLICIA-DATOS`

- **Organismo:** Policía Nacional, Ministerio del Interior.
- **Catálogo:** https://www.policia.es/_es/catalogo_de_datos.php
- **Qué obtener:** dependencias/comisarías y datos de contacto de los conjuntos oficiales aplicables.
- **Formato:** el publicado en cada conjunto.
- **Fiabilidad:** alta.
- **Licencia:** datos.gob.es indica CC BY 4.0 para determinados conjuntos; verificar licencia específica del recurso descargado.
- **Cadencia:** mensual.

### `SAS-CENTROS`

- **Organismo:** Servicio Andaluz de Salud.
- **Buscador oficial:** https://www.sspa.juntadeandalucia.es/servicioandaluzdesalud/el-sas/servicios-y-centros/informacion-por-centros
- **Qué obtener:** hospitales, centros de salud, consultorios, dirección, municipio, teléfonos y servicios publicados.
- **Formato:** HTML/datos internos del buscador; identificar un recurso reutilizable antes de implementar.
- **Fiabilidad:** alta para centros SAS.
- **Licencia:** pendiente de verificar.
- **Cadencia:** mensual; teléfonos y servicios son datos volátiles.

### `DIPUCADIZ-ENTIDADES`

- **Organismo:** Diputación de Cádiz y ayuntamientos publicadores.
- **Catálogo:** https://datosabiertos.dipucadiz.es/ (portal de datos abiertos). **Endpoint resuelto 2026-08-28:** la API real es RTOD — `https://apirtod.dipucadiz.es/api/collections.json` (32 colecciones). El CKAN (`apidatosabiertos.dipucadiz.es/api/3/action/*`) devuelve 404 y los `datos/<id>.json` devuelven 500 hoy; alternativas SPARQL `/sparql/` y catálogo web `/data`.
- **API de recursos (plantilla):** https://apirtod.dipucadiz.es/api/datos/<id>.json (sustituir `<id>` por el identificador real)
- **Qué obtener:** policías locales, Protección Civil municipal, servicios públicos y sedes cuando exista dataset oficial con mantenimiento identificable.
- **Formato:** CKAN JSON y recurso JSON/CSV.
- **Fiabilidad:** alta si el publicador es competente; registrar entidad por fila.
- **Licencia:** por dataset.
- **Cadencia:** mensual.

### `ORGANISMOS-DIRECTOS` — Cruz Roja, 112 y ayuntamientos

- **Puntos de descubrimiento:** https://www2.cruzroja.es/ y https://www.juntadeandalucia.es/organismos/ema/areas/emergencias-112.html, más sedes electrónicas municipales.
- **Qué obtener:** números generales y asambleas/sedes solo de páginas oficiales; priorizar 112 cuando corresponda.
- **Formato:** HTML o dataset público.
- **Fiabilidad:** alta si la página identifica organismo y sede.
- **Licencia:** pendiente de verificar por origen.
- **Cadencia:** mensual y verificación humana periódica.

## 3. Modelo y reglas de autoridad

| Campo | Regla |
|---|---|
| `service_id` | ID de origen; si no existe, hash estable de organismo + tipo + sede |
| `organization` / `service_type` | vocabulario controlado, sin inferir competencias |
| `name`, `address`, `postal_code`, `municipality` | conservar valor oficial y forma normalizada |
| `phone` | E.164 cuando sea posible; conservar extensión y original |
| `latitude`, `longitude` | WGS84, con `coordinate_source` y precisión |
| `coverage` | general, provincial, municipal o sede; no deducir por prefijo |
| `opening_hours` | estructura explícita y texto original; fecha de vigencia |
| `helisuperficie` | helipuertos, helisuperficies y zonas de aterrizaje/evacuación con coordenadas, operador y uso |
| `verified_at`, `source_url`, `snapshot_id` | obligatorios para publicar |
| `active` / `valid_until` | evitar borrar silenciosamente; mantener historial |

Prioridad ante conflicto: número nacional/autonómico publicado por la autoridad competente; después dataset del organismo; después portal municipal. OSM/Wikidata pueden detectar faltantes, pero no prevalecen sobre un contacto oficial.

## 4. Instantáneas y contraste

```text
data/raw/downloads/directorios-emergencia/<AAAA-MM-DD>/
├── guardia-civil/dependencias.csv
├── policia-nacional/<recurso>
├── sas/centros.<html|json>
├── diputacion/<dataset>.<json|csv>
├── organismos-directos/
└── MANIFEST.json
```

Normalizar sin sobrescribir el original. Comparar el CSV generado por IA contra las fuentes y producir un informe `confirmado/corregido/no_encontrado`; los dos últimos estados no pasan a producción.

## 5. Calidad, presupuesto y actualización

- Validar sintaxis telefónica, duplicados, municipio oficial, coordenadas y URL de evidencia.
- Verificación humana por muestreo y obligatoria para altas/cambios de teléfonos generales.
- Todo registro sin revisión dentro de la cadencia definida se marca `posiblemente_desactualizado` en vez de ocultar la antigüedad.
- Pruebas: 112, municipio pequeño, sede sin teléfono, horario partido, número sustituido y dos organismos en la misma dirección.
- Presupuesto: previsiblemente cientos o pocos miles de filas, muy inferior a 10 MiB con índices; no requiere embeddings.
- Actualización mensual con diff por campo y rollback de la última instantánea aprobada.

## 6. Política de vigencia (T12)

| Tipo de dato | Caducidad desde `verified_at` | Estado al superar |
|---|---|---:|---|
| Teléfonos/direcciones de organismos (GC, Policía, SAS, Protección Civil, Cruz Roja) | 6 meses | `posiblemente_desactualizado` |
| Horarios (transporte, farmacias de guardia) | 1 mes o `feed_end_date` del GTFS | `vencido` (no se presenta como vigente) |
| Coordenadas de infraestructura (helisuperficies, sedes, estaciones) | 12 meses | `posiblemente_desactualizado` |
| Números nacionales/autonómicos (112/061/062/091) | 12 meses | revisión manual |

Regla general: **sin `verified_at` no se publica**; la caducidad nunca oculta la antigüedad, solo la marca. El dato vencido se conserva con `active=false` y no se borra silenciosamente.

## 7. Pendientes para aprobar

- [ ] Identificar recursos descargables concretos de Policía Nacional y SAS.
- [ ] Inventariar los 45 portales municipales y priorizar APIs/datasets comunes.
- [ ] Verificar licencias y atribuciones por recurso.
- [x] Definir antigüedad máxima por tipo de contacto. *(política en §6)*
- [ ] Asignar responsable de comprobación humana.
