# Ficha de planificación: toxicología e intoxicaciones por sustancias

[← Volver al índice](README.md)

> **Estado:** `propuesta` — no implementada ni validada.
> **Prioridad:** P0. **Destino:** RAG vectorial con tablas de sinónimos.
> **Origen en `valorar.md`:** líneas 41 y 80.

## 1. Objetivo y límites

Permitir reconocer una posible intoxicación accidental o sobredosis, identificar señales de alarma y dar primeros pasos seguros mientras se contacta con 112 o con el Servicio de Información Toxicológica (SIT). No contendrá instrucciones de síntesis, preparación, dosificación, combinación o consumo de drogas, ni sustituirá la valoración del SIT.

## 2. Fuentes

### `SIT` — Instituto Nacional de Toxicología y Ciencias Forenses

- **Autoridad:** Ministerio de Justicia; servicio toxicológico oficial.
- **Portal:** https://www.mjusticia.gob.es/es/institucional/organismos/instituto-nacional/servicios/servicio-informacion/servicio-informacion1
- **Teléfono 24 h:** 91 562 04 20 (SIT).
- **Qué obtener:** teléfono vigente, pautas generales ante exposición, datos que debe recopilar quien llama y publicaciones divulgativas disponibles.
- **Formato:** HTML/PDF; adquisición manual versionada.
- **Fiabilidad:** alta para actuación toxicológica.
- **Licencia:** pendiente de verificar por publicación.
- **Actualización propuesta:** trimestral para contacto y anual para documentos.

### `PNSD` — Plan Nacional sobre Drogas

- **Autoridad:** Delegación del Gobierno para el Plan Nacional sobre Drogas, Ministerio de Sanidad.
- **Portal:** https://pnsd.sanidad.gob.es/ciudadanos/informacion/home.htm
- **Qué obtener:** nombres y sinónimos, efectos agudos, riesgos, situaciones de especial gravedad y vías de ayuda para alcohol, cannabis, cocaína, opioides, anfetaminas, metanfetamina, MDMA, alucinógenos, hipnosedantes, inhalables y nuevas sustancias.
- **Formato:** HTML y dosieres PDF. Algunas publicaciones indican expresamente reproducción permitida citando la fuente; comprobar cada documento.
- **Fiabilidad:** alta para descripción y prevención; no usar como protocolo clínico de tratamiento.
- **Actualización propuesta:** trimestral, con prioridad para nuevas sustancias y alertas.

### `INGESA-URG` — Urgencias extrahospitalarias

- **Documento:** https://ingesa.sanidad.gob.es/dam/jcr:a8b93f7a-e8dd-49d1-b643-b068f9508e18/Guia_urgencias_extrahosp.pdf
- **Qué obtener:** criterios profesionales de gravedad y contexto clínico solo para revisión del corpus ciudadano.
- **Fiabilidad:** alta, pero documento de 2014 y dirigido a profesionales.
- **Licencia:** pendiente de confirmar en el propio documento.
- **Uso:** fuente de contraste; no trasladar dosis ni intervenciones profesionales al asistente ciudadano.

### `AEMPS` — Agencia Española de Medicamentos y Productos Sanitarios

- **Autoridad:** Ministerio de Sanidad; regulador de medicamentos.
- **Portal:** https://www.aemps.gob.es/
- **Qué obtener:** fichas técnicas, prospectos y notas de seguridad sobre intoxicaciones por medicamentos, interacciones y principios activos; útil para intoxicaciones accidentales domésticas.
- **Formato:** HTML/PDF (CIMA: https://cima.aemps.es).
- **Fiabilidad:** alta para medicamentos; no sustituye al SIT en intoxicación aguda.
- **Licencia:** pendiente de verificar por documento.
- **Cadencia:** semestral.

### `EMCDDA` — Observatorio Europeo de las Drogas y las Toxicomanías

- **Autoridad:** agencia de la Unión Europea.
- **Portal:** https://www.euda.europa.eu/ (antes EMCDDA; EUDA)
- **Qué obtener:** perfiles de sustancias, prevalencia, riesgos agudos y nuevas sustancias psicoactivas; contraste internacional de cuadros y alertas.
- **Formato:** HTML/PDF.
- **Fiabilidad:** alta como referencia europea; no es protocolo clínico nacional.
- **Licencia:** pendiente de verificar; comprobar aviso de reutilización de la UE.
- **Cadencia:** trimestral para alertas de nuevas sustancias.

## 3. Bloques y mapeo

| Bloque | Origen | Salida normalizada | Subcategoría | Revisión |
|---|---|---|---|---|
| Identificación | PNSD | `sustancia`, `familia`, `alias` | `sustancias` | Farmacia/toxicología |
| Cuadro agudo | PNSD + SIT | `signos_frecuentes`, `signos_alarma`, `inicio_orientativo` | `intoxicacion_aguda` | Obligatoria |
| Primera respuesta | SIT | `proteger`, `no_hacer`, `llamar`, `datos_para_sit` | `actuacion_inicial` | Obligatoria |
| Exposición no intencional | SIT | `via`, `producto`, `descontaminacion_autorizada` | `exposicion_accidental` | Obligatoria |
| Ayuda | SIT/PNSD | `telefono`, `servicio`, `vigencia` | Tabla de contactos | Doble comprobación |

Cada fragmento debe separar síntomas orientativos de señales de alarma y terminar con la escalada adecuada. No se inferirá la sustancia únicamente por síntomas.

## 4. `data/raw/`

```text
data/raw/downloads/toxicologia-sustancias/<fecha>/
├── pnsd_<sustancia>.<html|pdf>
├── sit_informacion.html
└── MANIFEST.json
```

## 5. Calidad y seguridad

- Validación humana obligatoria por profesional sanitario con competencia en toxicología.
- Rechazar contenidos que indiquen dosis recreativas, neutralizaciones caseras no autorizadas, inducción del vómito o mezclas.
- Los nombres callejeros tienen confianza media y fecha; pueden cambiar rápidamente.
- La respuesta debe recomendar conservar envase/muestra solo cuando hacerlo sea seguro.
- Pruebas futuras: adulto inconsciente, niño expuesto, inhalación, contacto ocular, sustancia desconocida y mezcla de sustancias.

## 6. Presupuesto y actualización

Corpus objetivo: 25-60 fichas compactas, normalmente menos de 100 fragmentos. Descargar solo páginas/dosieres seleccionados. Comparar hash y fecha; cualquier cambio de actuación obliga a nueva revisión humana antes de publicar.

## 7. Pendientes para aprobar

- [ ] Confirmar URL y teléfono vigente del SIT durante la implementación.
- [ ] Revisar condiciones de reutilización de cada documento.
- [ ] Asignar validador sanitario.
- [ ] Definir vocabulario de sinónimos sin convertirlo en guía de consumo.
