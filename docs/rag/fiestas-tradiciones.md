# Ficha de planificación: festivos, fiestas y tradiciones

[← Volver al índice](README.md)

> **Estado:** `en_validacion` — existe un conector de eventos tradicionales; faltan fuentes exactas y calendario oficial anual.
> **Prioridad:** P2. **Destino:** fechas estructuradas + RAG cultural.
> **Origen en `valorar.md`:** línea 45.

## 1. Objetivo y límites

Mantener por separado: (1) festivos oficiales vigentes de ámbito estatal, autonómico y local; y (2) fiestas/tradiciones con fechas variables o aproximadas. Las respuestas indicarán municipio, fecha o regla de cálculo, año, fuente y estado de confirmación.

Una fecha habitual no equivale a convocatoria oficial. No se inferirán cortes de tráfico, horarios, mareas, aforo ni celebración efectiva sin publicación anual del organizador.

## 2. Registro de fuentes

### `JUNTA-FESTIVOS`

- **Organismo:** Consejería de Empleo, Empresa y Trabajo Autónomo, Junta de Andalucía.
- **Portal anual:** https://www.juntadeandalucia.es/organismos/empleoempresaytrabajoautonomo/areas/relaciones-laborales/calendario-fiestas.html
- **Ejemplo BOJA 2026:** https://www.juntadeandalucia.es/boja/2025/197/28
- **Qué obtener:** festivos autonómicos/oficiales del calendario laboral, disposición, año y correcciones posteriores.
- **Formato:** HTML/BOJA/PDF.
- **Fiabilidad:** alta para calendario andaluz.
- **Licencia:** verificar aviso legal/condiciones del BOJA; conservar cita oficial.
- **Cadencia:** anual desde su publicación y revisión mensual de correcciones hasta cerrar el año.

### `BOP-FESTIVOS-LOCALES`

- **Organismo:** boletines y autoridades laborales competentes; publicación provincial/local oficial.
- **Portal:** https://www.bopcadiz.es/
- **Qué obtener:** dos fiestas locales por municipio o la resolución/listado oficial que corresponda, incluyendo correcciones.
- **Formato:** PDF/HTML; buscar una resolución anual consolidada antes de automatizar.
- **Fiabilidad:** alta para fechas publicadas.
- **Licencia:** pendiente de verificar.
- **Cadencia:** anual y tras correcciones.

### `CADIZ-TURISMO`

- **Organismo:** Patronato Provincial de Turismo, Diputación de Cádiz.
- **Portal:** https://www.cadizturismo.com/
- **Qué obtener:** descripción, localidad, temporada, relevancia y enlaces del organizador para fiestas tradicionales.
- **Formato:** HTML/publicaciones.
- **Fiabilidad:** alta como fuente institucional turística, pero una descripción no confirma fecha anual.
- **Licencia:** pendiente de verificar por página/recurso.
- **Cadencia:** trimestral y antes de cada temporada.

### `AYUNTAMIENTOS-ORGANIZADORES`

- **Organismo:** ayuntamiento, entidad organizadora o autoridad competente de cada evento.
- **Descubrimiento:** sedes y agendas oficiales; cada evento tendrá URL específica.
- **Qué obtener:** fecha confirmada, ubicación, edición, cambios o cancelación.
- **Formato:** HTML/PDF/dataset.
- **Fiabilidad:** alta para la edición concreta.
- **Licencia:** pendiente de verificar por origen.
- **Cadencia:** por edición; solo conservar como vigente el año indicado.

### `IAPH-ETNOLOGIA`

- **Organismo:** Instituto Andaluz del Patrimonio Histórico.
- **Guía Digital:** https://www.juntadeandalucia.es/organismos/iaph/areas/documentacion-patrimonio/guia-digital.html
- **Qué obtener:** valor etnológico, denominaciones y contexto patrimonial cuando exista registro.
- **Formato:** API/HTML.
- **Fiabilidad:** alta para documentación patrimonial.
- **Licencia:** verificar condiciones de metadatos/textos.
- **Cadencia:** anual.

## 3. Modelo y mapeo

| Bloque | Fuente | Campos | Destino | Vigencia |
|---|---|---|---|---|
| Festivo oficial | Junta/BOJA/BOP | fecha, año, ámbito, municipio, norma, corrección | Tabla | Solo año publicado |
| Evento confirmado | organizador | evento_id, edición, inicio/fin, lugar, URL | Tabla | Edición concreta |
| Regla variable | fuente institucional | regla, calendario asociado, precisión | Tabla + RAG | No sustituye confirmación |
| Tradición | Turismo/IAPH | nombre, municipio, descripción, estacionalidad | RAG | Estable, revisar |
| Declaración de interés | resolución oficial | categoría, autoridad, fecha, expediente | Tabla | Hasta cambio oficial |

Claves: `municipality_code + event_id + edition_year`. Una fecha aproximada se almacena como intervalo/estación, no como día inventado.

## 4. Auditoría del conector existente

`src/updater/sources/fiestas_cadiz.py` contiene diez descripciones manuales y fechas habituales. No enlaza la fuente de cada evento, declara licencia/confianza/validación no demostradas y usa la fecha de ejecución como validación. También mezcla hechos culturales con fechas anuales y afirmaciones sobre reconocimiento turístico.

Debe auditarse evento a evento. Puede servir como lista inicial de candidatos, pero sus fechas no deben responder consultas del año actual hasta comprobar la edición oficial.

## 5. Instantáneas

```text
data/raw/downloads/fiestas-tradiciones/<AAAA-MM-DD>/
├── junta/calendario_laboral_<AAAA>.<html|pdf>
├── boja/disposicion_y_correcciones/
├── bop/festivos_locales_<AAAA>.pdf
├── turismo/<evento>.html
├── ayuntamientos/<municipio>/<evento>.<html|pdf>
└── MANIFEST.json
```

Relacionar cada corrección con la disposición inicial y conservar ambos documentos. No sobrescribir años anteriores.

## 6. Calidad, presupuesto y actualización

- Comprobar que cada municipio tenga el número esperado de festivos locales cuando la resolución anual lo permita.
- Detectar duplicados, cambios de nombre, fechas imposibles, ediciones canceladas y fuentes de años anteriores.
- Revisión humana para eventos; festivos se validan contra norma y correcciones.
- Pruebas: fecha móvil, evento según marea, festivo trasladado, corrección BOJA/BOP, cancelación y consulta sin año.
- Presupuesto: cientos de filas/año y 50-150 fragmentos culturales; tamaño mínimo, sin PDF en la Pi.
- Actualización anual de calendarios y por edición de eventos, conservando última versión aprobada y diff.

## 7. Pendientes para aprobar

- [ ] Localizar la resolución oficial anual de festivos locales para los 45 municipios.
- [ ] Verificar licencias de BOJA, BOP, Turismo e IAPH.
- [ ] Asignar URL oficial y regla de fecha a cada evento heredado.
- [ ] Definir cuántos años futuros/pasados conservar en la Pi.
- [ ] Planificar migración del conector a tablas con vigencia.
