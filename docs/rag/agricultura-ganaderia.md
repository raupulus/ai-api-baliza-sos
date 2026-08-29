# Ficha de planificación: agricultura y ganadería

[← Volver al índice](README.md)

> **Estado:** `propuesta` — sin adquisición ni corpus aprobado.
> **Prioridad:** P2. **Destino:** híbrido: estadísticas/alertas estructuradas + RAG técnico.
> **Origen en `valorar.md`:** líneas 59-61.

## 1. Objetivo y límites

Identificar cultivos y ganado relevantes en la provincia configurada y ofrecer fichas técnicas de manejo básico, calendario orientativo, riesgos y señales para solicitar ayuda agronómica o veterinaria. Las estadísticas sirven para priorizar especies; no son una guía de cultivo.

No se proporcionarán diagnósticos veterinarios, pautas farmacológicas, dosis de fitosanitarios, reproducción asistida ni calendarios rígidos sin considerar variedad, suelo, clima y normativa. El asistente debe derivar a servicios agrarios/veterinarios cuando exista enfermedad, parto complicado o riesgo sanitario.

## 2. Registro de fuentes

### `INE-CENSO-AGRARIO`

- **Organismo:** Instituto Nacional de Estadística.
- **Consulta:** https://www.ine.es/dynt3/inebase/es/index.htm?capsel=8305&padre=8301
- **Qué obtener:** superficies, explotaciones y censos por tipo de cultivo/ganado con la granularidad provincial o municipal disponible.
- **Formato:** tablas INE y descargas CSV/PC-Axis cuando se ofrezcan.
- **Fiabilidad:** alta para priorización estadística; puede tener desfase respecto al año actual.
- **Licencia:** verificar condiciones de reutilización del INE y atribución.
- **Cadencia:** por nueva operación/censo, con comprobación anual.

### `JUNTA-SECTOR-AGRARIO-CADIZ`

- **Organismo:** Consejería de Agricultura, Pesca, Agua y Desarrollo Rural.
- **Documento evaluado:** https://www.juntadeandalucia.es/sites/default/files/inline-files/2024/08/C%C3%A1diz%20Sector%20Agrario_%202023.pdf
- **Qué obtener:** contexto y principales sectores agrícolas/ganaderos de Cádiz para contrastar la selección derivada del INE.
- **Formato:** PDF estadístico.
- **Fiabilidad:** alta, pero edición referida a 2023; no usar como dato actual sin fecha.
- **Licencia:** pendiente de verificar.
- **Cadencia:** descubrir anualmente una edición posterior desde el portal, sin fijar el año en código.

### `RAIF`

- **Organismo:** Red de Alerta e Información Fitosanitaria, Junta de Andalucía.
- **Dataset:** https://www.juntadeandalucia.es/datosabiertos/portal/dataset/raif
- **Qué obtener:** parcelas, muestreos, plagas, enfermedades y tratamientos publicados para cultivos, filtrados por provincia/municipio; informes provinciales como contexto.
- **Formato:** ZIP con XML por cultivo y provincia.
- **Estructura observada (olivar, 2026-08-28):** 2006-2016 va un XML por provincia (`*_Cadiz_*.xml`); 2017-2026 va en XML **nacionales** (todas las provincias) que requieren filtrar por `<PROVINCIA>`. El ZIP usa compresión **DEFLATE64** (no legible por `zipfile` de Python; usar `7z`/`bsdtar`). Extracción Cádiz: `scripts/extraer_raif_cadiz.py` → `raif/cadiz/` (28 548 registros, ~63 MB).
- **Fiabilidad:** alta para observaciones de la red; no extrapolar una parcela a toda la provincia.
- **Licencia:** CC BY 4.0 indicada en el portal; conservar texto y atribución con la instantánea.
- **Frecuencia:** parte de los datos se actualiza semanalmente; confirmar por recurso.
- **Cadencia:** semanal durante campañas para alertas; mensual fuera de campaña.

### `IFAPA-PUBLICACIONES`

- **Organismo:** Instituto de Investigación y Formación Agraria y Pesquera de Andalucía.
- **Área temática:** https://www.juntadeandalucia.es/agriculturaypesca/ifapa/web/index.php/investigacion-y-desarrollo/areas-tematicas/produccion-agricola-y-ganadera
- **Centro local:** https://www.juntadeandalucia.es/agriculturaypesca/ifapa/web/index.php/personas-estructuras-y-servicios/centros-ifapa/centro-ifapa-rancho-de-la-merced
- **Qué obtener:** manuales y publicaciones concretas sobre los cultivos/ganado priorizados; metadatos de autoría, edición y ámbito.
- **Formato:** HTML/PDF; selección manual, no raspado indiscriminado.
- **Fiabilidad:** alta para transferencia técnica; verificar que el documento se dirige al público adecuado.
- **Licencia:** pendiente de verificar por publicación.
- **Cadencia:** trimestral para descubrir publicaciones.

### `JUNTA-GANADERIA` — Manuales oficiales ganaderos

- **Organismo:** Consejería competente en ganadería.
- **Punto de descubrimiento:** portal de publicaciones de la Junta e IFAPA; cada manual tendrá un `source_id` propio.
- **Qué obtener:** bienestar, alojamiento, alimentación general, higiene, bioseguridad, ciclos de atención y criterios de aviso veterinario.
- **Formato:** PDF/HTML.
- **Fiabilidad:** alta si es manual oficial vigente; documentos para veterinarios solo se usan para contraste.
- **Licencia:** pendiente de verificar por documento.
- **Cadencia:** anual.

## 3. Mapeo

| Bloque | Fuente | Salida normalizada | Destino | Validación |
|---|---|---|---|---|
| Relevancia provincial | INE + Junta | especie/cultivo, indicador, año, territorio | Tabla | Consistencia estadística |
| Ficha de cultivo | IFAPA | requisitos, calendario condicionado, manejo, riesgos | RAG | Técnico agrónomo |
| Alerta fitosanitaria | RAIF | cultivo, agente, observación, fecha, municipio/parcela | Tabla | No extrapolar |
| Ficha de ganado | Junta/IFAPA | especie, sistema, cuidados generales, periodos sensibles | RAG | Veterinaria obligatoria |
| Señales de alarma | Fuente técnica | signo, riesgo, acción segura, derivación | RAG | Veterinaria/agronómica |

Cada cifra conservará unidad, año y nivel territorial. Las fechas serán ventanas condicionadas, no órdenes universales.

## 4. Instantáneas y transformación

```text
data/raw/downloads/agricultura-ganaderia/<AAAA-MM-DD>/
├── ine/<tabla>.<csv|px>
├── junta/sector_agrario_cadiz.pdf
├── raif/<cultivo>.zip
├── ifapa/<publicacion>.pdf
├── ganaderia/<manual>.pdf
└── MANIFEST.json
```

Filtrar por códigos territoriales de configuración y no por texto “Cádiz” cuando exista código. Procesar XML/CSV en streaming. Asociar cada ficha técnica solo a especies priorizadas por datos y aprobación humana.

## 5. Calidad, presupuesto y actualización

- Validar unidades, años, códigos de municipio, duplicados y granularidad; no mezclar campañas.
- Rechazar dosis químicas, medicamentos, publicaciones comerciales sin contraste y manuales obsoletos sin advertencia.
- Revisores obligatorios: técnico agrónomo para cultivos y veterinario para ganado.
- Pruebas: dato histórico consultado como actual, plaga en una sola parcela, cultivo fuera de provincia, parto animal y petición de dosis.
- Objetivo inicial: 10-20 cultivos, 5-10 grupos ganaderos, menos de 200 fragmentos y tablas resumidas; históricos RAIF completos permanecen fuera de la Pi.
- Actualización diferencial por campaña y recurso; cambios de recomendaciones requieren revisión antes de publicar.

## 6. Pendientes para aprobar

- [ ] Obtener ranking reproducible de cultivos/ganado desde INE y Junta.
- [ ] Seleccionar manuales IFAPA concretos y comprobar sus licencias.
- [ ] Definir cuánto histórico RAIF necesita la operación offline.
- [ ] Asignar revisores agrónomo y veterinario.
- [ ] Definir caducidad y aviso visible de datos por campaña.
