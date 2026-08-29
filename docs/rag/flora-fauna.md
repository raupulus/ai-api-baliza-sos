# Ficha de planificación: flora, fauna y riesgos biológicos

[← Volver al índice](README.md)

> **Estado:** `en_validacion` — existe un conector heredado, pero no acredita fuentes, licencias ni revisión biológica.
> **Prioridad:** P0 para toxicidad/peligro; P1 para inventario y peces. **Destino:** híbrido geoespacial + RAG.
> **Origen en `valorar.md`:** líneas 36-37, 53-54 y 62.

## 1. Objetivo y límites

Mantener presencia geográfica y fichas seguras de flora, fauna, setas y peces relevantes para la provincia configurada, con especial atención a toxicidad, picaduras/mordeduras, toxinas marinas y contaminación.

La presencia de una especie no demuestra identificación individual, abundancia, peligro ni comestibilidad. El asistente no autorizará comer plantas, setas o peces silvestres a partir de una descripción. Los remedios del Dioscórides son material histórico y **no** se indexarán como consejo médico.

## 2. Registro de fuentes

### `REDIAM-FLORA`

- **Organismo:** Red de Información Ambiental de Andalucía.
- **WFS:** https://www.juntadeandalucia.es/medioambiente/mapwms/REDIAM_WFS_localizacion_flora_andaluza?
- **Qué obtener:** registros/localizaciones, taxón, categoría o metadatos disponibles, filtrados por `BBOX`.
- **Formato:** WFS/GML; descubrir capas mediante `GetCapabilities`.
- **Fiabilidad:** alta como información ambiental oficial; revisar fecha y precisión por registro.
- **Licencia:** pendiente de verificar en metadatos del servicio.
- **Cadencia:** trimestral.

### `EIDOS`

- **Organismo:** Ministerio para la Transición Ecológica y el Reto Demográfico.
- **Portal:** https://www.miteco.gob.es/es/biodiversidad/servicios/banco-datos-naturaleza/eidos_acceso.html
- **Qué obtener:** nombres científicos/vernáculos, taxonomía y fichas oficiales de especies; conservación cuando corresponda.
- **Formato:** portal/base de datos y descargas disponibles.
- **Fiabilidad:** alta para taxonomía nacional.
- **Licencia:** pendiente de verificar por recurso.
- **Cadencia:** trimestral.

### `GBIF` — Presencia complementaria

- **Ficha específica:** [gbif.md](gbif.md).
- **Qué obtener:** ocurrencias georreferenciadas para detectar candidatos y ampliar cobertura.
- **Fiabilidad:** variable por dataset/registro; nunca eleva por sí sola una afirmación a confianza alta.
- **Licencia:** por registro/dataset, conservada individualmente.
- **Cadencia:** según la ficha de GBIF.

### `JUNTA-PECES`

- **Organismo:** Consejería de Agricultura, Pesca, Agua y Desarrollo Rural.
- **Manual de identificación:** https://www.juntadeandalucia.es/organismos/agriculturapescaaguaydesarrollorural/areas/pesca-acuicultura/comercializacion/paginas/espinteres-manualident.html
- **Qué obtener:** identificación de especies pesqueras de interés y nombres comerciales/oficiales.
- **Formato:** HTML/PDF enlazado.
- **OCR (2026-08-28):** tomo I (126 pág.) y tomo II (210 pág.) escaneados; OCR español (`tesseract spa`) completado → `.ocr.txt` junto al PDF. Inventario estructurado de especies pendiente (T23).
- **Fiabilidad:** alta para identificación pesquera; no determina por sí solo seguridad de consumo.
- **Licencia:** pendiente de verificar por publicación.
- **Cadencia:** anual.

### `AESAN-TOXINAS`

- **Organismo:** Agencia Española de Seguridad Alimentaria y Nutrición.
- **Portal:** https://www.aesan.gob.es/eu/seguridad-alimentaria/contaminantes-quimicos/toxinas
- **Qué obtener:** riesgos por biotoxinas/contaminantes, prevención, alertas o documentos aplicables a productos marinos y vegetales.
- **Formato:** HTML/PDF.
- **Fiabilidad:** alta para seguridad alimentaria.
- **Licencia:** pendiente de verificar por recurso.
- **Cadencia:** mensual para alertas y anual para fichas estables.

### `AEMPS-PLANTAS` y `DIOSCORIDES-1998`

- **AEMPS:** https://www.aemps.gob.es/informa/notasInformativas/medicamentosUsoHumano/medPlantas/2011/docs/NI-MUH_06-2011_plantasMed.pdf
- **Original histórico local:** `data/raw/Dioscórides_Plantas_y_remedios_medicinales_Libros_I_III_ocr_G_1998.pdf`.
- **Qué obtener:** AEMPS se usa para riesgos/regulación de plantas medicinales. El Dioscórides solo podrá alimentar metadatos históricos o terminología tras revisar derechos de la traducción.
- **Fiabilidad:** AEMPS alta para seguridad regulatoria; Dioscórides auxiliar/histórica, no clínica.
- **Licencia:** AEMPS: **reproducción autorizada citando el origen** (aviso al pie del PDF). La traducción del Dioscórides-1998 sigue pendiente y presumiblemente protegida.
- **Cadencia:** AEMPS anual; documento histórico sin actualización.

## 3. Bloques y mapeo

| Bloque | Fuentes | Salida | Destino | Validación |
|---|---|---|---|---|
| Taxonomía | EIDOS + fuente oficial | taxon_id, nombre, sinónimos, rango | Tabla | Taxonómica |
| Presencia | REDIAM/GBIF | taxón, lat/lon o área, fecha, precisión, dataset | Geoespacial | Calidad por registro |
| Riesgo biológico | AESAN/AEMPS/guía oficial específica | exposición, síntomas orientativos, no hacer, derivación | RAG | Biología + sanitaria |
| Peces | Junta + AESAN | identificación, hábitat, comercialización, riesgo documentado | Híbrido | Pesquera/sanitaria |
| Contaminación | AESAN/autoridad ambiental | contaminante, matriz, área, vigencia, restricción | Tabla + RAG | No extrapolar |
| Vectores y zoonosis | SAS + ECDC | mosquito (Nilo Occidental), garrapata, flebotomo; síntomas, prevención, alarma | RAG | Sanitaria obligatoria |
| Uso histórico | Dioscórides | título/taxón/contexto histórico | No indexar inicialmente | Derechos + experto |

Toda ficha de especie conservará qué afirmación procede de qué fuente. “Comestible” nunca se derivará de ausencia de toxicidad ni de conocimiento popular.

## 4. Auditoría del conector existente

`src/updater/sources/flora_fauna_cadiz.py` contiene fichas manuales con licencia genérica, confianza alta y supuesto revisor no identificable. Además, mezcla presencia, identificación, toxicidad, tratamiento y comestibilidad sin citas por fragmento y fecha la validación en cada ejecución.

Debe permanecer bloqueado para nuevas ingestas hasta rastrear cada afirmación y sustituir etiquetas no demostradas. Esta auditoría documental no certifica ni corrige clínicamente las especies actuales.

## 5. Instantáneas

```text
data/raw/downloads/flora-fauna/<AAAA-MM-DD>/
├── rediam/flora.<gml|gpkg>
├── eidos/<recurso>
├── gbif/occurrences.<csv|json>
├── junta/peces.<pdf|html>
├── aesan/<ficha>.html
├── aemps/plantas.pdf
└── MANIFEST.json
```

El Dioscórides ya descargado no se duplica: se registrará hash, tamaño, procedencia y derechos en un manifiesto de inventario.

## 6. Calidad, presupuesto y actualización

- Validar taxonomía, coordenadas, fecha, licencia por registro, duplicados y precisión espacial.
- Revisión humana obligatoria por biólogo; toxicidad/comestibilidad añade profesional sanitario o de seguridad alimentaria.
- Rechazar identificación por una sola característica, tratamientos no sanitarios, ubicaciones sensibles que deban protegerse y alertas vencidas.
- Pruebas: taxón sinónimo, registro dudoso, pez parecido, seta solicitada como comida, contaminación histórica y remedio medicinal.
- Objetivo: tablas compactas y 100-250 fichas de riesgo; no copiar todas las ocurrencias ni PDFs a la Pi.
- Actualización diferencial; los cambios de taxonomía y seguridad requieren revisión antes de publicar.

## 7. Pendientes para aprobar

- [ ] Inventariar capas/campos REDIAM y licencias exactas.
- [ ] Resolver subpáginas **en español** de AESAN (biotoxinas marinas, ciguatera, histamina, micotoxinas) para extraer riesgo accionable.
- [ ] Definir especies prioritarias y fuente de riesgo para cada una (procesionaria, medusas, víbora hocicuda, setas tóxicas, adelfa/ricino).
  - **Progreso 2026-08-28:** mordeduras/picaduras de animales (víbora, medusas, pez araña/rascacio, escorpión/araña, abeja/avispa) normalizadas desde INGESA → `primeros_auxilios_*` (3 fragmentos). Pendiente específico: procesionaria del pino (contacto) e identificación de setas tóxicas.
- [ ] Extraer inventario de especies del OCR de peces (T23).
- [ ] Resolver derechos y decisión final sobre el Dioscórides.
- [ ] Asignar revisores de biología, toxicología y seguridad alimentaria.
- [ ] Diseñar sustitución del conector heredado con trazabilidad por afirmación.
