# Ficha de planificación: apoyo psicosocial en emergencias

[← Volver al índice](README.md)

> **Estado:** `propuesta` — sin implementación.
> **Prioridad:** P1. **Destino:** RAG vectorial.
> **Origen en `valorar.md`:** línea 63.

## 1. Objetivo y límites

Ofrecer pautas breves de primer apoyo a personas que acaban de sufrir una catástrofe, accidente, pérdida o mala noticia: seguridad, escucha, necesidades básicas, conexión con apoyos y detección de riesgo. No realizará diagnóstico, psicoterapia, interrogatorio del trauma ni promesas falsas.

## 2. Fuentes

### `SANIDAD-CATASTROFES-2024`

- **Organismo:** Comisionado de Salud Mental, Ministerio de Sanidad.
- **Documento:** https://www.sanidad.gob.es/areas/alertasEmergenciasSanitarias/alertasActuales/infoDana/riesgoParaLaSalud/docs/2024_11_08_Marco_de_intervencion_psicosocial_en_situaciones_de_catastrofes.pdf
- **Qué obtener:** principios de derechos/equidad, participación, “no dañar”, niveles de apoyo, coordinación y derivación.
- **Formato:** PDF.
- **Fiabilidad:** alta; marco oficial reciente.
- **Licencia:** pendiente de verificar en el documento/aviso legal.
- **Cadencia:** anual y tras emergencias con nuevas recomendaciones.

### `SANIDAD-AUTOAYUDA`

- **Portal:** https://www.sanidad.gob.es/ciudadanos/saludMental/autoayuda.htm
- **Qué obtener:** reacciones esperables, autocuidado, apoyo a niños y criterios temporales para pedir ayuda.
- **Formato:** HTML.
- **Fiabilidad:** alta; revisar actualidad editorial.
- **Licencia:** pendiente de verificar.

### `DGPCE-PSICOSOCIAL`

- **Organismo:** Dirección General de Protección Civil y Emergencias.
- **Guía:** https://www.proteccioncivil.es/catalogo/guiastecnicas/Planificacion_Intervencion_Psicosocial_Emergencias/index.html
- **Qué obtener:** necesidades psicosociales, coordinación y límites entre ayuda básica y atención profesional.
- **Formato:** HTML/PDF.
- **Fiabilidad:** alta, pero parte del material puede ser antiguo.
- **Licencia:** pendiente de verificar.

### `CRUZROJA-PSICOSOCIAL` — Cruz Roja Española

- **Organismo:** Cruz Roja Española.
- **Portal:** https://www2.cruzroja.es/
- **Qué obtener:** materiales públicos de apoyo psicosocial en emergencias, autocuidado y acompañamiento a personas afectadas.
- **Formato:** HTML/PDF.
- **Fiabilidad:** alta como organización de referencia; cada documento debe verificarse.
- **Licencia:** pendiente de verificar por documento.
- **Cadencia:** trimestral.

### `OMS-PFA` — Primera Ayuda Psicológica (OPS/OMS)

- **Autoridad:** Organización Mundial de la Salud / Organización Panamericana de la Salud.
- **Guía PFA:** https://www.who.int/publications/i/item/9789241548205
- **Qué obtener:** principios de primera ayuda psicológica (PFA), escucha, necesidades básicas, grupos vulnerables y límites del apoyo no profesional.
- **Formato:** PDF (traducción oficial en español disponible).
- **Fiabilidad:** alta como estándar internacional; adaptar al marco español.
- **Licencia:** verificar condiciones de la OMS/OPS; la guía suele permitir uso con atribución.
- **Cadencia:** estable; comprobar ediciones.

## 3. Bloques y mapeo

| Bloque | Contenido normalizado | Subcategoría | Seguridad |
|---|---|---|---|
| Primer contacto | presentarse, seguridad, permiso, tono y privacidad | `primer_apoyo` | No forzar relato |
| Escucha | preguntas abiertas mínimas, validar sin diagnosticar | `escucha` | No prometer confidencialidad absoluta |
| Necesidades | agua, abrigo, medicación, reunificación, información | `necesidades_basicas` | Priorizar peligro físico |
| Grupos vulnerables | infancia, mayores, discapacidad, duelo | `vulnerabilidad` | Lenguaje adaptado |
| Riesgo agudo | desorientación grave, violencia, autolesión/suicidio | `derivacion_urgente` | 112 y supervisión segura |
| Intervinientes | pausas, relevo, apoyo entre pares y derivación | `intervinientes` | No sustituye salud laboral |

## 4. `data/raw/` y transformación

```text
data/raw/downloads/apoyo-psicosocial/<fecha>/
├── marco_intervencion_psicosocial.pdf
├── sanidad_autoayuda.html
├── proteccion_civil_psicosocial/
└── MANIFEST.json
```

Extraer únicamente recomendaciones para ciudadanía/primer interviniente. Los formularios con datos personales y las técnicas reservadas a psicólogos no se indexan.

## 5. Validación y aceptación

- Revisión obligatoria por profesional de psicología de emergencias o salud mental.
- Incluir pruebas para duelo, menor separado, persona en shock, ataque de pánico, posible suicidio y primer interviniente saturado.
- Toda indicación de riesgo suicida o violencia debe priorizar seguridad y contacto con emergencias.
- Corpus estimado: 20-40 fragmentos; impacto mínimo en la Pi.
