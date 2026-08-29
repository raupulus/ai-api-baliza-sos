# Ficha de planificación: clima y meteorología offline

[← Volver al índice](README.md)

> **Estado:** `propuesta` — sin conector ni contenido aprobado.
> **Prioridad:** P0 para umbrales de riesgo y autoprotección; P1 para climatología y orientación meteorológica.
> **Destino:** RAG vectorial + tabla de umbrales/estaciones. **Origen:** hueco detectado en `docs/planning/rag.md` §5.1 (el enum `categoria` ya contempla `clima`).

---

## 1. Objetivo y límites

Cubrir el conocimiento meteorológico que una persona aislada puede usar **sin predicción en tiempo real**: climatología estacional por comarca, señales de mal tiempo observables (nubes, viento, presión, mar), umbrales de riesgo (olas de calor, lluvias intensas/DANA, viento de levante/terral, niebla costera) y autoprotección asociada.

- **Por qué es necesario:** Cádiz concentra riesgos muy distintos — olas de calor en la campiña, levante en el Estrecho y la bahía, DANAs con inundaciones, nieblas costeras en la costa atlántica y riesgo de incendio por viento seco. Saber interpretar el entorno evita exponerse o permite anticipar refugio.
- **Consultas tipo:** "el cielo se ha puesto muy oscuro y huele a tierra, ¿qué viene?", "¿cuánto viento es peligroso para caminar?", "hace mucho calor y no sudo, ¿es golpe de calor?", "¿la niebla de la costa dura todo el día?".
- **Límites estrictos:** no se presenta como predicción ni alerta en tiempo real (sin conexión). Nunca se emite un aviso oficial; solo se describe el fenómeno, el umbral orientativo y la autoprotección. El dato meteorológico marino de Puertos del Estado queda **bloqueado** por condiciones de redistribución hasta confirmación.

---

## 2. Registro de fuentes

### `AEMET-OPENDATA` — Agencia Estatal de Meteorología (principal)

- **Organismo / autoridad:** AEMET, Ministerio para la Transición Ecológica y el Reto Demográfico.
- **URL de catálogo:** https://opendata.aemet.es/centrodedescargas/inicio
- **API:** https://opendata.aemet.es/opendata/ (requiere `api_key`)
- **Qué obtener:** climatologías normales por estación/comarca, valores normales de temperatura y precipitación, fenómenos adversos publicados y umbrales oficiales de aviso por provincia.
- **Formato y adquisición:** `JSON/CSV` vía API.
- **Fiabilidad:** `alta` (organismo meteorológico oficial).
- **Licencia:** AEMET OpenData permite reutilización con atribución; verificar las condiciones exactas y la nota legal del endpoint antes de redistribuir.
- **Cadencia:** climatologías anuales; avisos por campaña.
- **Notas de estabilidad:** documentar `api_key`, endpoint, estación y fecha de extracción; la estructura de avisos cambia por boletín.

### `DGPCE-METEO` — Riesgos meteorológicos y autoprotección

- **Organismo / autoridad:** Dirección General de Protección Civil y Emergencias.
- **URL de catálogo:** https://www.proteccioncivil.es/coordinacion/gestion-de-riesgos
- **Qué obtener:** guías ciudadanas ante olas de calor, lluvias intensas, tormentas, vientos fuertes y nevadas; conducta antes/durante/después.
- **Formato y adquisición:** `PDF/HTML` con NIPO.
- **Fiabilidad:** `alta`.
- **Licencia:** `pendiente de verificar` por publicación.
- **Cadencia:** semestral y tras grandes emergencias.

### `ANDALUCIA-112` — Emergencias 112 Andalucía / Agencia de Emergencias

- **Organismo / autoridad:** Agencia de Emergencias de Andalucía (EMA), Junta de Andalucía.
- **URL:** https://www.juntadeandalucia.es/organismos/ema/areas/emergencias-112.html
- **Qué obtener:** consejos autonómicos de autoprotección meteorológica y funcionamiento de los avisos por nivel (amarillo/naranja/rojo) en Andalucía.
- **Formato y adquisición:** `HTML/PDF`.
- **Fiabilidad:** `alta` para Andalucía.
- **Licencia:** `pendiente de verificar` en aviso legal y por recurso.
- **Cadencia:** trimestral y por campaña.

### `SANIDAD-CALOR` — Plan nacional de altas temperaturas y salud

- **Organismo / autoridad:** Ministerio de Sanidad.
- **URL:** https://www.sanidad.gob.es/areas/sanidadAmbiental/riesgosAmbientales/calorExtremo/home.htm
- **Qué obtener:** umbrales de temperatura por zona (meteosalud), niveles de riesgo, recomendaciones para personas vulnerables y señales de golpe de calor.
- **Formato y adquisición:** `HTML/PDF`.
- **Fiabilidad:** `alta` para riesgo sanitario por calor.
- **Licencia:** `pendiente de verificar`.
- **Cadencia:** anual, antes del verano.

### `DGT-METEO` — Conducción ante meteorología adversa

- **Organismo / autoridad:** Dirección General de Tráfico.
- **URL:** https://www.dgt.es/
- **Qué obtener:** recomendaciones de conducción ante niebla, viento, lluvia y calor extremo, y equipamiento asociado.
- **Formato y adquisición:** `HTML`.
- **Fiabilidad:** `alta` para seguridad vial.
- **Licencia:** `pendiente de verificar`.
- **Cadencia:** semestral.

> **Contraste adicional (no activo por defecto):** `Puertos del Estado` (meteorología marina/oleaje) es la autoridad para mar, pero su manual prohíbe transferir datos a terceros; queda **bloqueado** y solo se usará si se confirma por escrito compatibilidad con el uso offline.

---

## 3. Bloques y mapeo

| Bloque destino | Fuente | Salida normalizada | Destino (`data/processed/`) | Validación |
|---|---|---|---|---|
| Climatología por comarca | AEMET | comarca, mes, temp/pp normal, extremos, fuente | `csv/clima_cadiz.csv` + `md/clima/` | Meteorológica |
| Umbrales de aviso | AEMET + DGPCE | fenómeno, nivel, umbral, conducta | `csv/umbrales_meteo.csv` | Meteorológica |
| Olas de calor y salud | SANIDAD-CALOR | umbral por zona, riesgo, población vulnerable | `md/clima/` + tabla | Sanitaria |
| Viento (levante/terral) | AEMET + DGPCE | dirección, intensidad, efecto local, riesgo | `md/clima/` | Meteorológica |
| Lluvia/DANA/inundación | DGPCE + AEMET | señal observable, conducta, evacuación | `md/clima/` | Protección Civil |
| Niebla costera | AEMET + DGT | formación, persistencia, conducción | `md/clima/` + tabla | Meteorológica/vial |
| Señales observables de campo | AEMET + manuales | cielo, viento, presión, humedad → interpretación | `md/clima/` | Meteorológica |
| Autoprotección general | DGPCE + ANDALUCIA-112 | fase, hacer/no hacer, escalada | `md/clima/` | Protección Civil |

Cada fragmento conservará `source_id`, URL, edición/boletín, fecha de consulta y hash. Los umbrales llevan `provincia`, `zona` y `vigencia`, nunca se presentan como alerta en tiempo real.

---

## 4. Instantáneas y transformación

```text
data/raw/downloads/clima-meteorologia/<AAAA-MM-DD>/
├── aemet/normales_<comarca>.<json|csv>
├── aemet/umbrales_avisos.json
├── dgpce/<riesgo>.pdf
├── andalucia_112/<recomendacion>.html
├── sanidad/plan_calor.pdf
├── dgt/<meteo>.html
└── MANIFEST.json
```

Extraer por encabezado/boletín; eliminar navegación; convertir cada recomendación en una unidad con fenómeno, umbral, fase y contexto. No mezclar riesgos distintos. Las referencias geográficas dependen de `PROVINCIA`/`BBOX`.

---

## 5. Calidad, presupuesto y actualización

- Validar zona/estación, rango de fechas, unidades, umbrales coherentes con AEMET y duplicados.
- Rechazar consejos sin procedencia, "predicciones" caseras, umbrales sin fuente y contenido de foros.
- Revisión obligatoria por meteorólogo o técnico de Protección Civil; las recomendaciones sanitarias por calor, por perfil sanitario.
- Pruebas: golpe de calor, DANA con subida de nivel, viento de levante que impide avanzar, niebla en carretera y consulta que pide una predicción futura.
- Objetivo: 40-80 fragmentos y pocos cientos de filas de umbrales; tamaño mínimo, PDFs solo en el actualizador.
- Actualización anual de climatologías y umbrales; avisos por campaña con diff y rollback. Un cambio de umbral bloquea la tabla hasta revisión.

---

## 6. Pendientes para aprobar

- [ ] Obtener y documentar `api_key`/endpoints de AEMET OpenData y sus condiciones exactas.
- [ ] Seleccionar las estaciones/comarcas representativas de Cádiz para las normales.
- [ ] Verificar licencias de DGPCE, Junta, Sanidad y DGT.
- [ ] Resolver por escrito el bloqueo de Puertos del Estado para meteorología marina.
- [ ] Asignar revisor meteorológico/protección civil y sanitario para calor.

---

## 7. Historial de versiones

| Fecha | Estado | Autor / Revisor | Cambio |
|---|---|---|---|
| 2026-08-28 | `propuesta` | Agente Zed | Creación de la ficha a partir del hueco `clima` del plan maestro. |
