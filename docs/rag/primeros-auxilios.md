# Ficha de planificación: primeros auxilios y problemas de salud comunes

[← Volver al índice](README.md)

> **Estado:** `en_validacion` — existe el conector heredado `primeros-auxilios-avanzado`, pero su procedencia, licencia y validación deben auditarse antes de reutilizarlo.
> **Prioridad:** P0. **Destino:** RAG vectorial + contactos estructurados.
> **Origen en `valorar.md`:** líneas 30-32, 40 y 80.

## 1. Objetivo y límites

Proporcionar instrucciones breves para población general ante primeros auxilios básicos, urgencias graves, parto inminente, atragantamiento, caídas, esguinces/fracturas y síntomas comunes, con señales de alarma y escalada al 112. No diagnostica ni sustituye asistencia sanitaria.

La traqueostomía se limita a cuidados de seguridad para una persona que **ya tiene** cánula/estoma y a pedir ayuda; nunca explicará cómo crear una vía aérea, cambiar dispositivos sin formación o practicar procedimientos invasivos. Los tratamientos farmacológicos, dosis, torniquetes, picaduras y potabilización solo se incorporarán desde una guía exacta y tras validación profesional.

## 2. Registro de fuentes

### `ERC-2025` — Guías europeas de resucitación

- **Organismo:** European Resuscitation Council.
- **Portal:** https://www.erc.edu/science-research/guidelines/guidelines-2025/
- **Resumen oficial en castellano:** https://www.erc.edu/media/vatl54cg/01_gl2025_exec-summary_es_v10.pdf?dl=0
- **Qué obtener:** soporte vital básico ciudadano, reconocimiento de parada, uso de DEA, atragantamiento y diferencias por grupo cuando estén en el material público seleccionado.
- **Formato:** HTML/PDF, edición 2025.
- **Fiabilidad:** alta por sociedad científica responsable de las guías europeas.
- **Licencia:** pendiente de verificar por documento y traducción; no asumir reutilización integral.
- **Cadencia:** por nueva edición, corrección o actualización intermedia.

### `INGESA-PA` — Guía de primeros auxilios

- **Organismo:** Instituto Nacional de Gestión Sanitaria, Ministerio de Sanidad.
- **Documento:** https://ingesa.sanidad.gob.es/dam/jcr:bf2bfc8d-e181-4629-9650-ca8b2985393b/Guia_centros_educativos.pdf
- **Qué obtener:** evaluación inicial, activación de emergencias y actuaciones ciudadanas aplicables; revisar público objetivo y fecha editorial.
- **Formato:** PDF.
- **Fiabilidad:** alta como publicación sanitaria oficial; puede requerir contraste por antigüedad.
- **Licencia:** pendiente de verificar en el documento/aviso legal.
- **Cadencia:** semestral para descubrir sustitución.

### `INGESA-URG` — Guía de urgencias extrahospitalarias

- **Organismo:** INGESA.
- **Documento:** https://ingesa.sanidad.gob.es/dam/jcr:a8b93f7a-e8dd-49d1-b643-b068f9508e18/Guia_urgencias_extrahosp.pdf
- **Qué obtener:** señales de gravedad y contraste clínico para parto, traumatismos y urgencias; no trasladar técnicas o dosis profesionales.
- **Formato:** PDF, documento de 2014.
- **Fiabilidad:** alta como referencia profesional histórica, no como única guía vigente para ciudadanía.
- **Licencia:** pendiente de verificar.
- **Cadencia:** buscar sustitución semestralmente.

### `CRUZROJA-PA`

- **Organismo:** Cruz Roja Española.
- **Ejemplo evaluado, atragantamiento:** https://www2.cruzroja.es/es/web/ahora/-/qu-c3-a9-hacer-ante-un-atragantamiento
- **Qué obtener:** recomendaciones públicas concretas de primeros auxilios, una página/documento por protocolo.
- **Formato:** HTML/PDF.
- **Fiabilidad:** alta como organización de referencia; cada protocolo debe contrastarse con ERC/Sanidad.
- **Licencia:** pendiente de verificar por página; enlazar no implica permiso para copiar.
- **Cadencia:** trimestral.

### `SAS-CIUDADANIA` — Autocuidados y derivación

- **Organismo:** Servicio Andaluz de Salud.
- **Ejemplo verificado, resfriado:** https://www.sspa.juntadeandalucia.es/servicioandaluzdesalud/ciudadania/farmacia-y-prestaciones/informacion-la-ciudadania-sobre-el-uso-de-medicamentos/medicamentos-para-el-resfriado-preguntas-frecuentes
- **Qué obtener:** fichas oficiales para fiebre, tos, resfriado, cefalea, ampollas y señales de alarma; cada tema necesita URL y fecha propias.
- **Formato:** HTML/PDF.
- **Fiabilidad:** alta para ciudadanía andaluza.
- **Licencia:** pendiente de verificar por ficha.
- **Cadencia:** trimestral.

## 3. Bloques y mapeo

| Bloque | Fuente preferente | Salida normalizada | Subcategoría | Revisión |
|---|---|---|---|---|
| Evaluación inicial | ERC/INGESA | seguridad, respuesta, respiración, llamada | `evaluacion_inicial` | Sanitaria |
| RCP/DEA | ERC | grupo, secuencia, ritmo, DEA, cese | `soporte_vital` | Sanitaria obligatoria |
| Atragantamiento | ERC + Cruz Roja | gravedad, tos, maniobras por grupo, pérdida de conciencia | `atragantamiento` | Sanitaria obligatoria |
| Hemorragias/trauma | INGESA + guía vigente por seleccionar | hacer, no hacer, inmovilización, alarma | `traumatismos` | Sanitaria obligatoria |
| Parto inminente | INGESA-URG + fuente ciudadana por seleccionar | reconocer, llamar, acompañar, seguridad | `parto` | Obstetricia |
| Traqueostomía existente | fuente clínica ciudadana por localizar | alarma, posición, ayuda, límites | `traqueostomia_cuidados` | Especialista; no invasivo |
| Salud común | SAS | autocuidado no farmacológico, alarma, derivación | `autocuidados` | Medicina/enfermería |
| Riesgos locales | fuentes sanitarias específicas | exposición, primeros pasos, alarma | `picaduras_mordeduras` | Sanitaria + biología |
| Colectivos vulnerables | ERC/SAS + guía pediátrica | niño/lactante, persona mayor, embarazada, discapacidad; diferencias RCP y evacuación | `vulnerables` | Sanitaria obligatoria |

Cada fragmento tendrá escenario, población, acciones ordenadas, prohibiciones, señales de alarma, fuente exacta, edición y aprobación. Los contactos se enlazan desde `directorios-emergencia.md`.

## 4. Auditoría del conector existente

Existe `src/updater/sources/primeros_auxilios_avanzado.py`, con contenido escrito manualmente. Antes de ejecutarlo de nuevo deben corregirse en una fase de implementación separada estos bloqueos:

- atribuye una licencia genérica `CC-BY-NC-SA 4.0` sin vincularla a documentos;
- marca `manual_validado`, confianza alta y un equipo revisor no identificado;
- usa la fecha de ejecución como fecha de validación;
- mezcla medicina, especies peligrosas, montaña y potabilización;
- contiene cifras e instrucciones sin referencia por fragmento.

Esta ficha no valida ni invalida clínicamente cada frase: exige reemplazarla o rastrearla contra las fuentes anteriores y guardar revisor real, fecha, versión y resultado.

## 5. Instantáneas

```text
data/raw/downloads/primeros-auxilios/<AAAA-MM-DD>/
├── erc-2025/<documento>.pdf
├── ingesa/guia_primeros_auxilios.pdf
├── ingesa/guia_urgencias_extrahospitalarias.pdf
├── cruz-roja/<protocolo>.html
├── sas/<autocuidado>.html
└── MANIFEST.json
```

Extraer encabezados y listas sin resumir automáticamente dosis o secuencias críticas. Generar una tabla de trazabilidad `fragmento → páginas/secciones → revisor` antes de publicar.

## 6. Calidad, presupuesto y actualización

- Revisión obligatoria por profesional sanitario competente; obstetricia y traqueostomía requieren perfil específico.
- Rechazar contenido sin versión, dirigido solo a profesionales si no puede adaptarse con seguridad, o que contradiga una guía más reciente.
- Pruebas: adulto/niño, persona inconsciente, embarazo, anticoagulantes, fiebre con alarma, cánula existente y ausencia de cobertura.
- Las respuestas deben caber en hasta tres mensajes de 230 bytes sin omitir llamada al 112 ni prohibiciones críticas.
- Objetivo: 80-160 fragmentos, menos de 500 KiB; PDF originales fuera de la Pi.
- Actualizar por versión; todo cambio en secuencia, cifra o “no hacer” bloquea publicación hasta nueva revisión.

## 7. Pendientes para aprobar

- [ ] Asignar profesionales sanitarios reales y registrar evidencia de revisión.
- [ ] Localizar fuentes ciudadanas vigentes para parto y traqueostomía existente.
- [ ] Verificar licencias de ERC, INGESA, Cruz Roja y SAS.
- [ ] Diseñar migración segura del conector heredado sin publicar contenido no auditado.
- [ ] Definir casos de prueba clínicos y revisión de los límites LoRa.
