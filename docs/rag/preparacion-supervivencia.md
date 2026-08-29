# Ficha de planificación: preparación y supervivencia segura

[← Volver al índice](README.md)

> **Estado:** `propuesta` — sin implementación ni validación.
> **Prioridad:** P0 para agua y reservas; P1 para kits y orientación práctica; P3 para fabricación no esencial.
> **Destino:** RAG vectorial con listas estructuradas. **Origen:** líneas 42-43, 47-48, 55-57, 78-79 y 84-146 de `valorar.md`.

## 1. Objetivo y límites

Documentar preparación doméstica y de viaje para cortes de suministro, aislamiento, evacuación o extravío: agua, alimentos, kits de hogar/montaña/coche, personas vulnerables, mascotas, higiene y conservación. Las cantidades deben incluir unidad, escenario, duración y fuente.

Se excluyen fabricación de pólvora o explosivos, armas, trampas, destilación de alcohol, técnicas médicas y prácticas de supervivencia de alto riesgo. Jabón solo se valorará como higiene segura si una fuente pública documenta el procedimiento. Cerveza, ginebra, whisky e hidromiel no son conocimiento prioritario; la destilación queda expresamente descartada.

## 2. Registro de fuentes

### `DGPCE-AUTOPROTECCION` — Autoprotección ciudadana

- **Organismo:** Dirección General de Protección Civil y Emergencias.
- **Portal:** https://www.proteccioncivil.es/coordinacion/gestion-de-riesgos/autoproteccion
- **PDF:** https://www.proteccioncivil.es/documents/20121/0/07-Autoproteccion_accesible.pdf/4344b9ea-05ef-6415-0223-10ab4257effd
- **Qué obtener:** plan familiar, documentación, suministros, comunicación, confinamiento y evacuación.
- **Formato:** HTML/PDF, publicación con NIPO.
- **Fiabilidad:** alta.
- **Licencia:** pendiente de verificar; no inferir licencia por el carácter público.
- **Cadencia:** semestral.

### `SANIDAD-AGUA` — Agua de consumo e incidencias

- **Organismo:** Ministerio de Sanidad.
- **Guía RD 3/2023:** https://www.sanidad.gob.es/areas/sanidadAmbiental/calidadAguas/aguasConsumoHumano/publicaciones/docs/2023_GUIA_RD_3_2023.pdf
- **FAQ sanitaria ante inundaciones:** https://www.sanidad.gob.es/areas/alertasEmergenciasSanitarias/alertasActuales/infoDana/faq/home.htm
- **Qué obtener:** prioridad de avisos municipales, usos seguros/no seguros del agua, actuación ante incidencias y prevención de contaminación.
- **Formato:** PDF/HTML.
- **Fiabilidad:** alta; la guía general no es por sí sola un manual de potabilización improvisada.
- **Condiciones:** la guía declara **reproducción permitida citando la fuente** ("La totalidad o parte de esta publicación puede reproducirse sin permiso adicional, siempre que se mencione la fuente"). Nota 2026-08-28: es una guía regulatoria de 235 páginas orientada a operadores/municipios, con **poco contenido accionable para ciudadanos**; la potabilización ciudadana debe venir de la FAQ sanitaria ante inundaciones o DGPCE.
- **Cadencia:** anual y ante cambios normativos.

### `DGT-V16` — Equipamiento reglamentario del vehículo

- **Organismo:** Dirección General de Tráfico.
- **URL:** https://www.dgt.es/muevete-con-seguridad/tecnologia-e-innovacion-en-carretera/Dispositivos-de-presenalizacion-V16/
- **Qué obtener:** vigencia, requisitos y uso de dispositivos V16; nunca mantener una fecha legal sin su versión.
- **Formato:** HTML y listado enlazado de dispositivos certificados.
- **Fiabilidad:** alta para normativa vial.
- **Licencia:** pendiente de verificar.
- **Cadencia:** mensual por posible cambio reglamentario o de listado.

### `GC-MONTANA` — Preparación para montaña

- **Organismo:** Guardia Civil.
- **URL:** https://web.guardiacivil.es/es/colaboracion/consejos/montana/
- **Qué obtener:** planificación, material, meteorología previa, comunicación del itinerario y actuación ante extravío.
- **Formato:** HTML.
- **Fiabilidad:** alta para prevención.
- **Licencia:** pendiente de verificar.
- **Cadencia:** semestral.

### `AESAN-RESERVAS` — Seguridad alimentaria

- **Organismo:** Agencia Española de Seguridad Alimentaria y Nutrición.
- **Portal ciudadano:** https://www.aesan.gob.es/para-la-ciudadania
- **Manipulación/higiene de alimentos:** https://www.aesan.gob.es/seguridad-alimentaria/higiene-alimentos/manipuladores-alimentos
- **Qué obtener:** conservación, integridad de envases, cadena de frío, fechas, higiene y riesgos por contaminación. La lista concreta de reservas deberá contrastarse con DGPCE u otra guía pública específica.
- **Formato:** HTML/PDF.
- **Fiabilidad:** alta para seguridad alimentaria.
- **Licencia:** pendiente de verificar por recurso.
- **Cadencia:** anual.

## 3. Bloques y mapeo

| Bloque | Fuentes | Salida normalizada | Destino | Revisión |
|---|---|---|---|---|
| Plan familiar | DGPCE | escenario, contactos, reunión, evacuación | RAG | Protección Civil |
| Kit básico | DGPCE | artículo, finalidad, cantidad, duración, colectivo | Tabla + RAG | Fuente por elemento |
| Coche | DGT + DGPCE | obligatorio/recomendado, vigencia, uso | Tabla | Legal y seguridad vial |
| Montaña | GC | material, condición, estación, riesgo | Tabla + RAG | Rescate/montaña |
| Mascotas | DGPCE o fuente pública por localizar | identificación, agua, alimento, transporte, medicación | Tabla | Veterinaria |
| Alimentos | AESAN + DGPCE | tipo, conservación, rotación, descarte | RAG | Seguridad alimentaria |
| Agua | SANIDAD | origen, riesgo, tratamiento autorizado, limitación | RAG | Sanitaria obligatoria |
| Señalización de socorro | GC/DGPCE | silbato (6/min), espejo, fuego con humo, código suelo-aire, luz | RAG | Rescate/montaña |
| Higiene | SANIDAD | limpieza, desinfección, mezclas prohibidas | RAG | Sanitaria obligatoria |

No trasladar automáticamente las cantidades del borrador de `valorar.md`: son requisitos a verificar, no una fuente. Cada cifra debe conservar unidad, población, duración y cita.

## 4. Instantáneas y transformación

```text
data/raw/downloads/preparacion-supervivencia/<AAAA-MM-DD>/
├── dgpce_autoproteccion.pdf
├── sanidad_guia_agua.pdf
├── sanidad_emergencia_agua.html
├── dgt_v16.html
├── guardia_civil_montana.html
├── aesan_seguridad_alimentaria/
└── MANIFEST.json
```

Separar hechos estables de requisitos con vigencia. Normalizar cantidades a unidades SI sin perder el original. Las listas se deduplicarán por `escenario + articulo + colectivo`; la salida conservará si es obligación legal, recomendación oficial o complemento pendiente.

## 5. Seguridad, presupuesto y actualización

- Revisión sanitaria obligatoria para agua, alimentos, higiene y personas con necesidades médicas.
- Revisión veterinaria para mascotas si se incorporan cantidades o cuidados clínicos.
- Rechazar recetas químicas ambiguas, dosis sin concentración del producto, consumo de flora silvestre, pólvora, destilación y contenido basado solo en blogs.
- Pruebas futuras: corte de agua, inundación, evacuación con menor/persona dependiente, coche inmovilizado y extravío en montaña.
- Objetivo: 40-80 registros de kit y 40-80 fragmentos; menos de 500 KiB normalizados. Los PDF quedan fuera de la Pi.
- Actualización por hash; requisitos legales se comparan mensualmente y recomendaciones semestralmente. No publicar cambios críticos sin informe de diferencias y revisión.

## 6. Pendientes para aprobar

- [ ] Localizar una fuente oficial española específica para kit de mascotas.
- [ ] Confirmar fuente oficial de cantidades mínimas de agua/alimentos por persona y duración.
- [ ] Verificar condiciones de reutilización.
- [ ] Asignar revisores sanitario, de Protección Civil y veterinario.
- [ ] Decidir si jabón se descarta o se documenta solo como higiene no industrial.
