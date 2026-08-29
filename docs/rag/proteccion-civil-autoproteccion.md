# Ficha de planificación: protección civil y autoprotección

[← Volver al índice](README.md)

> **Estado:** `propuesta` — sin conector ni contenido aprobado.
> **Prioridad:** P0. **Destino:** RAG vectorial; avisos vigentes fuera de alcance offline.
> **Origen en `valorar.md`:** líneas 39, 46, 51 y 52.

## 1. Objetivo y límites

Preparar instrucciones oficiales, breves y accionables para prevenir riesgos y actuar durante inundaciones, incendios forestales, terremotos, evacuaciones, confinamientos y accidentes en montaña. El corpus debe distinguir **antes, durante y después**, priorizar siempre órdenes de 112 y autoridades, y no presentar información precargada como si fuera una alerta en tiempo real.

No se indexarán técnicas policiales, enfrentamiento con agresores, acceso a zonas cerradas, rescate técnico ni instrucciones contrarias a una orden oficial.

## 2. Registro de fuentes

### `DGPCE-RIESGOS` — Guías de información al ciudadano

- **Organismo:** Dirección General de Protección Civil y Emergencias, Ministerio del Interior.
- **Catálogo:** https://www.proteccioncivil.es/coordinacion/gestion-de-riesgos
- **Descargas evaluadas:**
  - Inundaciones: https://www.proteccioncivil.es/documents/20121/0/08-Inundaciones_accesible.pdf/9b11b38f-447a-5eea-38bd-088def20096f
  - Incendios forestales: https://www.proteccioncivil.es/documents/20121/1069714/02-Incendios_Forestales_accesible.pdf/ba63caa6-901f-31c0-a4f3-5f0b7c87d927
  - Riesgo sísmico: https://www.proteccioncivil.es/documents/20121/0/01-Riesgos_Sismico_accesible.pdf/4a195b9a-680e-6232-c471-8520f79af96e
  - Autoprotección: https://www.proteccioncivil.es/documents/20121/0/07-Autoproteccion_accesible.pdf/4344b9ea-05ef-6415-0223-10ab4257effd
- **Qué obtener:** prevención, conducta durante el suceso, evacuación/confinamiento, retorno seguro y preguntas frecuentes.
- **Formato:** PDF accesible con NIPO; descarga manual versionada.
- **Fiabilidad:** alta, por autoridad estatal competente.
- **Licencia:** pendiente de verificar para cada publicación; NIPO y acceso público no equivalen a licencia abierta.
- **Cadencia:** comprobar semestralmente el catálogo y tras cambios normativos o grandes emergencias.

### `ANDALUCIA-112` — Emergencias 112 Andalucía

- **Organismo:** Agencia de Emergencias de Andalucía, Junta de Andalucía.
- **URL:** https://www.juntadeandalucia.es/organismos/ema/areas/emergencias-112.html
- **Qué obtener:** funcionamiento del 112, datos que debe comunicar quien llama, accesibilidad y recomendaciones autonómicas enlazadas.
- **Formato:** HTML y publicaciones vinculadas.
- **Fiabilidad:** alta para Andalucía.
- **Licencia:** pendiente de verificar en el aviso legal y por recurso.
- **Cadencia:** trimestral.

### `GC-MONTANA` — Consejos de la Guardia Civil

- **Organismo:** Guardia Civil, Ministerio del Interior.
- **URL:** https://web.guardiacivil.es/es/colaboracion/consejos/montana/
- **Qué obtener:** planificación de salida, prevención de extravíos, aviso de itinerario y conducta ante accidente en montaña.
- **Formato:** HTML.
- **Fiabilidad:** alta para prevención y solicitud de auxilio; no sustituye guías sanitarias.
- **Licencia:** pendiente de verificar.
- **Cadencia:** semestral.

### `POLICIA-CONSEJOS` — Consejos de seguridad de Policía Nacional

- **Organismo:** Policía Nacional, Ministerio del Interior.
- **Catálogo institucional verificado:** https://www.policia.es/_es/colabora_participacion_colectivosciudadanos.php
- **Qué obtener:** únicamente recomendaciones ciudadanas relacionadas con emergencias, desapariciones, evacuaciones y seguridad personal.
- **Formato:** HTML/PDF; selección manual por tema.
- **Fiabilidad:** alta dentro de su competencia.
- **Licencia:** pendiente de verificar.
- **Cadencia:** semestral.

### `DGT-METEOROLOGIA-VIAL` — Seguridad vial ante meteorología adversa

- **Organismo:** Dirección General de Tráfico.
- **Portal:** https://www.dgt.es/
- **Qué obtener:** recomendaciones de conducción ante inundaciones, niebla, viento y hielo; equipamiento V16 y conducta en vía durante una emergencia.
- **Formato:** HTML/PDF.
- **Fiabilidad:** alta para seguridad vial.
- **Licencia:** pendiente de verificar.
- **Cadencia:** semestral.

## 3. Bloques y mapeo

| Bloque destino | Fuente | Salida normalizada | Subcategoría | Validación |
|---|---|---|---|---|
| Inundación | DGPCE | `fase`, `situacion`, `hacer`, `evitar`, `escalada` | `inundaciones` | Comparar secciones y versión |
| Incendio forestal | DGPCE | conducta en vivienda, carretera, campo y evacuación | `incendios` | Revisión Protección Civil |
| Terremoto | DGPCE | interior, exterior, vehículo y réplicas | `sismos` | Revisión Protección Civil |
| Tsunami/maremoto | DGPCE + IGN | retirada del mar, alejamiento de costa, zonas altas, señales de alerta | `tsunamis` | Revisión Protección Civil |
| Autoprotección | DGPCE | plan familiar, confinamiento, evacuación | `autoproteccion` | Revisión humana |
| Aviso al 112 | ANDALUCIA-112 | `que_ocurre`, `donde`, `afectados`, `riesgos` | `llamada_112` | Teléfono exacto y vigente |
| Montaña | GC-MONTANA | preparación, extravío y auxilio | `montana` | Contraste con DGPCE |
| Seguridad | POLICIA-CONSEJOS | prevención y derivación | `seguridad_ciudadana` | Excluir tácticas operativas |

Cada fragmento conservará `source_id`, URL, título, NIPO o versión, fecha de consulta y hash. Las instrucciones incompatibles por versión se bloquean hasta revisión.

## 4. Instantáneas y transformación

```text
data/raw/downloads/proteccion-civil-autoproteccion/<AAAA-MM-DD>/
├── dgpce_inundaciones.pdf
├── dgpce_incendios_forestales.pdf
├── dgpce_riesgo_sismico.pdf
├── dgpce_autoproteccion.pdf
├── andalucia_112.html
├── consejos_gc_montana.html
└── MANIFEST.json
```

Extraer por encabezados; eliminar navegación y normativa no operativa; convertir cada recomendación en una unidad con riesgo, fase y contexto. No combinar instrucciones de riesgos distintos. Las referencias geográficas dependerán de `PROVINCIA`/`BBOX`, aunque las guías sean nacionales.

## 5. Calidad, presupuesto y actualización

- Revisión obligatoria por personal de Protección Civil o emergencias antes de publicar.
- Rechazar consejos sin procedencia exacta, versiones antiguas contradictorias y contenido que implique rescate técnico.
- Casos de prueba: riada en coche, incendio con orden de confinamiento, humo durante evacuación, terremoto en interior, extravío en sierra y llamada con cobertura limitada.
- Objetivo: 60-120 fragmentos, menos de 250 KiB de texto normalizado; PDFs solo en el equipo actualizador.
- Descargar condicionalmente, comparar hashes y generar diferencias por bloque. Un cambio en “hacer/no hacer” exige nueva aprobación; mantener en la Pi la última versión aprobada hasta entonces.

## 6. Pendientes para aprobar

- [ ] Verificar licencia/condiciones de cada recurso.
- [ ] Confirmar estabilidad del catálogo de consejos de Policía Nacional.
- [ ] Asignar revisor de Protección Civil.
- [ ] Definir tratamiento de instrucciones autonómicas que prevalezcan sobre guías generales.
- [ ] Preparar pruebas de respuestas de hasta tres mensajes y 230 bytes por mensaje.
