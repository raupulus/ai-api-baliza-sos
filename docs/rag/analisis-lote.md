# Análisis del lote descargado — hallazgos y restricciones por fuente

[← Volver al índice](README.md)

> **Fecha de análisis:** 2026-08-28
> **Alcance:** lote P0 descargado a `data/raw/` (22 archivos + 2 tomos de peces + 1 rescate montaña).
> **Compañero de:** [`auditoria-fuentes.md`](auditoria-fuentes.md) y [`plan-adquisicion.md`](plan-adquisicion.md).

---

## 1. Resumen del lote

| Ficha | Fuente | Archivo | Tipo | Estado para RAG |
|---|---|---|---|---|
| primeros-auxilios | ERC-2025 | `erc_2025_resumen_es.pdf` (204 pp) | PDF cifrado (restricciones) | ✅ Texto extraíble; contenido válido |
| primeros-auxilios | INGESA | `ingesa_guia_primeros_auxilios.pdf` (52 pp) | PDF | ✅ Índice claro; orientado a docentes |
| primeros-auxilios | INGESA | `ingesa_guia_urgencias_extrahospitalarias.pdf` (170 pp) | PDF | ✅ Profesional; solo para contraste |
| proteccion-civil | DGPCE | 4 PDFs (inundaciones/incendios/sismo/autoprotección) | PDF | ✅ Ciudadano, accionable |
| proteccion-civil | Guardia Civil | `guardia_civil_rescate_montana.pdf` (2 pp) | PDF | ✅ Breve y accionable |
| proteccion-civil | Guardia Civil | `guardia_civil_consejos_montana.html` | HTML | ⚠️ Portada; contenido en PDF enlazado |
| proteccion-civil | 112 Andalucía | `andalucia_112.html` | HTML | ⚠️ Navegación dinámica |
| preparacion-supervivencia | Sanidad | `sanidad_guia_agua_rd3_2023.pdf` (236 pp) | PDF | ⚠️ Normativa técnica; no guía de campo |
| apoyo-psicosocial | Sanidad | `sanidad_marco_intervencion_psicosocial.pdf` (5 pp) | PDF | ✅ Marco breve |
| apoyo-psicosocial | Sanidad | `sanidad_autoayuda.html` | HTML | ✅ Contenido accionable |
| apoyo-psicosocial | OMS | `oms_pfa_guia.html` | HTML | ⚠️ Ficha; PDF requiere enlace directo |
| toxicologia | PNSD | `pnsd_informacion_ciudadanos.html` | HTML | ⚠️ Índice; cada sustancia es una URL |
| flora-fauna | AEMPS | `aemps_plantas_medicinales.pdf` (3 pp) | PDF | ✅ Nota breve |
| flora-fauna | AESAN | `aesan_toxinas.html` | HTML | ⚠️ Portal; fichas por toxina |
| flora-fauna | Junta | `junta_manual_peces_tomo_i.pdf` (126 pp) | PDF | ✅ Identificación de especies |
| flora-fauna | Junta | `junta_manual_peces_tomo_ii_baja.pdf` (210 pp) | PDF | ✅ Identificación de especies |
| clima | Sanidad | `sanidad_plan_calor.html` | HTML | ✅ Contenido accionable |
| clima | DGPCE | `dgpce_gestion_riesgos.html` | HTML | ⚠️ Navegación dinámica, sin enlaces PDF |
| directorios | Guardia Civil | `guardia_civil_dependencias.csv` (2.446 líneas) | CSV | ✅ Estructurado; filtrable por Cádiz |

---

## 2. Restricciones y lecciones por fuente (para no repetir en próximos análisis)

### `ERC-2025` (primeros auxilios)
- **PDF cifrado** con `copy:no`. El contenido **sí** se extrae con `pdftotext` (cifrado de permisos, no de datos), pero **no** debe redistribuirse tal cual. Licencia pendiente de verificar.
- 28 MB / 204 páginas. Para la Pi solo fragmentos, no el PDF.

### `INGESA` (primeros auxilios)
- **Guía de centros educativos**: orientada a accidentes en colegios (infancia). Útil, pero hay que filtrar el enfoque escolar y extraer lo generalizable a adultos.
- **Guía de urgencias extrahospitalarias**: documento **de 2014 dirigido a profesionales**; usar solo como contraste, nunca como protocolo ciudadano directo.

### `DGPCE` (protección civil / clima)
- Los 4 PDFs de guías ciudadanas son **directamente accionables** (antes/durante/después). Buen material base.
- La página `gestion-de-riesgos` es **navegación dinámica**: no expone enlaces PDF estáticos en el HTML descargado. Los PDFs concretos ya los teníamos por URL directa. **Restricción:** no automatizar scraping de ese catálogo; usar las URLs directas ya conocidas.

### `Guardia Civil` (protección civil / directorios)
- La página de consejos de montaña es una **portada**; el contenido real está en `rescate_en_montana.pdf` (2 páginas) descubierto vía enlace interno.
- El CSV de dependencias es **nacional** (2.446 filas), **ISO-8859**, delimitador `;`. **Restricción:** transcodificar a UTF-8 y filtrar `PROVINCIA == "CÁDIZ"` antes de indexar.

### `112 Andalucía` (protección civil)
- HTML con **contenido dinámico** (frames/navegación). La información accionable es mínima en el HTML plano. Priorizar otras fuentes para protocolos; usar esta solo para datos de contacto del 112.

### `Sanidad` (preparación / clima / psicosocial)
- **Guía RD 3/2023 (agua)**: 236 páginas de **normativa técnica de implementación**, no una guía práctica de potabilización en campo. **Restricción:** extraer solo los apartados de actuación ante incidencias y usos seguros; no intentar convertir el decreto entero en RAG.
- **Plan calor** (`calorExtremo/home.htm`): contenido accionable (niveles de riesgo, golpe de calor). Válido.
- **Autoayuda psicosocial**: HTML con contenido accionable ("reacciones frecuentes", "qué hacer"). Válido.
- **Marco intervención psicosocial**: PDF de 5 páginas, marco breve. Válido.

### `OMS` (apoyo psicosocial)
- La URL descargada es la **ficha de la publicación**, no el PDF. **Restricción:** localizar el enlace directo del PDF (o usar la versión OPS en español) antes de indexar.

### `PNSD` (toxicología)
- La página descargada es el **índice de sustancias**; cada sustancia (`alcohol`, `cannabis`, `cocaína`, `anfetamina`, etc.) tiene su **propia URL**. **Restricción:** para tener contenido hay que descargar página por sustancia, no el índice.

### `EUDA` (toxicología, contraste)
- **403 anti-bot** a descarga automática. **Restricción:** no automatizar; usar URLs de perfil de sustancia específicas o consultar manualmente.

### `AEMPS` (flora-fauna)
- Nota de 3 páginas (2011) sobre regulación de plantas medicinales. **Antigua**; usar como contexto regulatorio, no como guía actual.

### `AESAN` (flora-fauna)
- La página de toxinas es un **portal**; el detalle está en subpáginas (`micotoxinas`, `biotoxinas marinas`, etc.). **Restricción:** descargar por subpágina, no el índice.

### `Junta — peces` (flora-fauna)
- La URL original era una **portada**; los PDFs reales (Tomos I y II, 126 y 210 pp) están enlazados internamente. **Restricción:** el nombre de archivo usa "x" en lugar de "ó/á" (p. ej. `Identificacixn`), reflejo de codificación; descargar con el nombre canónico.

### `content_type` no fiable (transversal)
- Varios servidores sirven CSV/PDF como `text/html`. **Restricción:** verificar el contenido con `file`/`pdfinfo`/inspección, no confiar en la cabecera HTTP.

---

## 3. Prioridad de normalización tras este análisis

1. **DGPCE (4 guías)** — material ciudadano más accionable y listo para fragmentar.
2. **INGESA guía centros educativos** — extraer protocolos generalizables (RCP, atragantamiento, hemorragias, quemaduras).
3. **ERC-2025** — fuente canónica de RCP/DEA; extraer secuencias por grupo.
4. **Guardia Civil rescate montaña** — fragmento corto y útil.
5. **CSV Guardia Civil** — transcodificar + filtrar Cádiz → tabla de directorios.
6. **Sanidad plan calor / autoayuda** — HTML accionable.
7. **Peces Tomos I/II** — extraer fichas de especies relevantes.
8. **Resto** — requiere resolver subpáginas/PDFs antes de procesar.

---

## 4. Restricciones de normalización (PDFs DGPCE)

**Hallazgo crítico:** las 4 guías DGPCE almacenan la sección **"Recomendaciones"** (el contenido accionable: ANTES/DURANTE/DESPUÉS) como **imágenes/infografías** (11-20 imágenes por PDF), no como texto. Solo las "Preguntas frecuentes" son texto extraíble.

- **`pdftotext`** extrae las preguntas frecuentes pero deja vacía la sección de recomendaciones.
- **OCR** no es viable de forma segura en este entorno: `tesseract` solo tiene el modelo `eng` (no `spa`), y aplicar OCR de baja calidad a contenido de protección civil violaría la regla de "no publicar desde scraping no verificado".
- **Decisión:** no normalizar las recomendaciones de DGPCE desde imagen. Requieren una de estas vías:
  1. Localizar una **fuente alternativa en texto** con el mismo contenido (p. ej. la versión EPUB de las guías, que el propio NIPO declara, o las guías autonómicas 112 Andalucía en HTML).
  2. Instalar el modelo OCR español (`spa`) y **validar manualmente** cada fragmento extraído.
  3. Incorporar las recomendaciones desde fuentes HTML accionables ya identificadas (112 Andalucía, Guardia Civil).

- **Las "Preguntas frecuentes"** de las guías DGPCE sí son normalizables, pero su valor para el RAG de emergencias es **medio-bajo** (mucho contenido es informativo, no accionable). Se priorizan después de las fuentes accionables.

## 5. Capacidad de extracción de texto por PDF (normalización)

| PDF | Texto extraíble | Veredicto para normalización |
|---|---|---|
| ERC-2025 | 332 k chars | ✅ Canónico para RCP/DEA |
| INGESA urgencias extrahospitalarias | 298 k chars | ✅ Contraste profesional |
| INGESA guía centros educativos | sí (índice limpio) | ✅ Protocolos generalizables |
| Sanidad agua RD 3/2023 | 366 k chars | ⚠️ Normativa, no guía de campo |
| Sanidad marco psicosocial | 7 k chars | ✅ Breve y accionable |
| AEMPS plantas medicinales | 5 k chars | ✅ Nota regulatoria |
| DGPCE (4 guías) | parcial (solo FAQ) | ⚠️ Recomendaciones en imagen |
| Guardia Civil rescate montaña | texto duplicado/desordenado | ❌ Escaneado/diseño, no extraíble |
| Junta peces Tomo I | 0 chars | ❌ Escaneado (imagen) |
| Junta peces Tomo II | — | ❌ Presumible escaneado |

**Restricción transversal:** varios PDFs de Protección Civil/Guardia Civil/Junta son **escaneados o infografías** sin capa de texto fiable. La normalización debe verificar `pdftotext` > 0 antes de procesar y **nunca** forzar la extracción de PDFs de imagen sin OCR español validado.

## 6. Restricciones de fuentes HTML (normalización)

- **Sanidad plan calor (`calorExtremo/home.htm`)**: la página descargada es una **portada/introducción**; las recomendaciones accionables viven en subpáginas enlazadas (`Recomendaciones generales de protección`, `Niveles de riesgo`, etc.). **Restricción:** no fragmentar la portada; descargar las subpáginas concretas antes de normalizar.
- **Sanidad autoayuda (`autoayuda.htm`)**: contenido accionable sí extraíble, pero la sección "Dónde obtener ayuda" referencia la **Comunidad de Madrid** (no aplica a Cádiz). **Restricción:** al extraer, omitir o generalizar referencias territoriales ajenas a `PROVINCIA`.

[← Volver al índice](README.md)
