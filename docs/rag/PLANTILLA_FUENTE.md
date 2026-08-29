# Ficha de planificación: [NOMBRE DEL DOMINIO]

[← Volver al índice](README.md)

> **Estado:** `propuesta | en_validacion | aprobada | implementada | descartada`
>
> Esta ficha especifica la adquisición, el contraste y la transformación. No implica que exista un conector ni que el contenido esté validado en el RAG.

---

## 1. Objetivo y límites

Explicar de forma directa:

- **Por qué es necesario este conocimiento:** qué emergencia, peligro o necesidad resuelve a una persona incomunicada sin internet ni cobertura móvil en la provincia configurada.
- **Qué consultas tipo responderá:** ejemplos de preguntas de radiofrecuencia (LoRa / Meshtastic).
- **Límites estrictos de seguridad:** qué queda expresamente prohibido o fuera de alcance (ej. no inventar dosis, no recomendar consumo de setas dudosas, no sustituir al 112).

---

## 2. Registro de fuentes

Regla de redundancia: **mínimo 1 fuente primaria oficial** y, cuando la información esté dispersa o no dependa de un único organismo, **hasta 5 fuentes** (primaria + secundarias de contraste). Ordenar por autoridad: administración competente → organismo científico/sociedad profesional → datos abiertos colaborativos → fuentes auxiliares.

### `ID-FUENTE` — Nombre del organismo / fuente

- **Organismo / autoridad:**
- **URL de catálogo / portal:**
- **URL de descarga / API:**
- **Qué obtener:**
- **Formato y adquisición:** `JSON | CSV | PDF | HTML | WFS | API | manual`
- **Fiabilidad:** `alta | media | auxiliar`
- **Licencia:** [comprobada: CC BY, ODbL…] o `pendiente de verificar`
- **Cadencia de publicación del origen:** [mensual | anual | estática | por edición]
- **Rate limit / cortesía de red:** [p. ej. máx 1 req/2 s, sin reintentos agresivos, respetar 429/Retry-After, User-Agent identificado]
- **Notas de estabilidad:** [versionado, URLs fijas, estructura de datos]
- **Restricciones conocidas:** [anti-bot, SPA, codificación, CRS, compresión, licencia] — anotar aquí o en §9.

> Si una fuente tiene restricción de redistribución, anotarlo explícitamente como **bloqueo** y no incluirla en la publicación hasta confirmación.

---

## 3. Bloques y mapeo

Detallar la información atómica que debe existir al final:

| Bloque destino | Fuente | Salida normalizada | Destino (`data/processed/`) | Validación |
|---|---|---|---|---|
| `[nombre_bloque]` | `[ID]` | `[campos/texto]` | `csv/...` o `md/...` | `automática | médica | humana` |

---

## 4. Auditoría del conector existente *(si aplica)*

Documentar qué código heredado existe (`src/updater/sources/*.py`), qué problema de trazabilidad/licencia/validación presenta y si puede reutilizarse como inventario de pruebas o debe reemplazarse. Nunca reindexar contenido no auditado.

---

## 5. Instantáneas y transformación

```text
data/raw/downloads/<identificador>/<AAAA-MM-DD>/
├── <fuente>/<archivo_original>.<ext>
├── capabilities/          # si hay consultas WFS/API
├── LICENSE.txt
└── MANIFEST.json          # hash, fuente, fecha UTC, cabeceras, licencia, versión
```

- No editar los originales; conservar evidencia para reprocesado.
- Normalizar a WGS84 si es geoespacial; conservar el CRS original en metadatos.
- Filtrar por `PROVINCIA`/`BBOX`/códigos territoriales, nunca por texto hardcodeado.

---

## 6. Calidad, presupuesto y actualización

- **Validación:** qué se comprueba automáticamente y qué exige revisión humana (con perfil del revisor).
- **Criterios de rechazo inmediato:** contenido sin fuente contrastada, procedimientos obsoletos/peligrosos, listados sin fecha, datos que no se pueden trazar.
- **Pruebas:** casos de consulta reales a evaluar en inferencia.
- **Presupuesto:** objetivo de fragmentos/registros y tamaño máximo; los originales quedan fuera de la Pi.
- **Cadencia de actualización:** dinámica (mensual) o estática (anual/por edición); conservar la versión anterior para rollback y generar diff.

---

## 7. Pendientes para aprobar

- [ ] Checklist atómico por sección (nunca genérico).
- [ ] Verificar licencias de cada fuente.
- [ ] Asignar revisor(es) con rol/identidad real.
- [ ] Confirmar enlace bidireccional a `data/processed/`.

---

## 8. Historial de versiones

| Fecha | Estado | Autor / Revisor | Cambio |
|---|---|---|---|
| `AAAA-MM-DD` | `propuesta` | `[Rol/Nombre]` | Creación inicial de la ficha. |

---

## 9. Restricciones y lecciones de adquisición

> Anotar aquí **cada problema encontrado al descargar/procesar** (con fecha), para no repetirlo en la próxima actualización y para minimizar bloqueos de red por reintentos. Ejemplos: codificación no UTF-8, ZIP con DEFLATE64, WFS con filtro espacial roto, API con certificado autofirmado, `content_type` no fiable, `agency_id` textual vs numérico, CRS de la geometría, límites de paginación.

- [ ] `AAAA-MM-DD` — [restricción/lección] → [solución aplicada].

[← Volver al índice](README.md)
