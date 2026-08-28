# Ficha de planificación de conocimiento: [NOMBRE DEL DOMINIO]

[← Volver al índice de fuentes RAG](README.md)

> **Estado:** `propuesta | en_validacion | aprobada | implementada | descartada`
>
> Esta ficha especifica la adquisición, contraste y transformación. No implica que exista un conector ni que el contenido esté validado en el RAG.

---

## 1. Identificación y Ciclo de Vida

- **Identificador:** `kebab-case` (ej. `primeros-auxilios`, `flora-fauna`, `directorios-emergencia`)
- **Categorías:** `primeros_auxilios | fauna | flora | geografia | supervivencia | orientacion | clima | cultura_historia | directorios`
- **Ámbito territorial:** Provincia configurada mediante `PROVINCIA` y `BBOX` (Cádiz por defecto).
- **Puntos de origen:** Conceptos derivados de [`data/info/valorar.md`](../../data/info/valorar.md).
- **Prioridad:** `P0 crítica | P1 alta | P2 media | P3 baja`
- **Destino del dato:** `RAG vectorial (MD) | Tabla estructurada (CSV) | Híbrido`
- **Fecha de creación / actualización de ficha:** `AAAA-MM-DD`
- **Periodicidad recomendada de sincronización:** `Estática / Puntual | Anual | Semestral | Trimestral | Mensual`
- **Fecha de última extracción efectiva:** `Sin extracción | AAAA-MM-DD`
- **Fichero(s) procesado(s) resultante(s):** `data/processed/csv/...` o `data/processed/md/...`
- **Responsable / Revisor:** `[Rol / Especialista / Pendiente de asignar]`

---

## 2. Motivo y Justificación de Campo

Explicar de forma directa:
* **Por qué es necesario este conocimiento:** Qué emergencia, peligro o necesidad resuelve a una persona incomunicada sin internet ni cobertura móvil en la provincia.
* **Qué consultas tipo responderá:** Ejemplos de preguntas de radiofrecuencia (LoRa / Meshtastic).
* **Límites estrictos de seguridad:** Qué información queda expresamente prohibida o fuera de alcance (ej. no inventar dosis de medicamentos, no recolectar setas dudosas sin confirmación pericial).

---

## 3. Checklist de Objetivos y Ciclo de Vida

- [ ] **1. Especificación:** Ficha redactada, fuentes identificadas y contrastadas.
- [ ] **2. Descarga a Raw:** Instantánea original almacenada en `data/raw/<identificador>/<AAAA-MM-DD>/` con `MANIFEST.json`.
- [ ] **3. Normalización y Limpieza:** Script/filtro creado para transformar a `data/processed/` (sin ruido, navegación ni paja).
- [ ] **4. Checkpoint Humano:** Validación y firma de contenido crítico (médico, legal, toxicológico) por revisor cualificado.
- [ ] **5. Ingesta al RAG / BD:** Carga completada en base de datos PostgreSQL (`pgvector`) o tablas relacionales.
- [ ] **6. Verificación en Inferencia:** Pruebas de consulta en LLM evaluando respuestas breves ($\le 200$ bytes UTF-8) y sin alucinaciones.

---

## 4. Registro de Fuentes

Listar siempre la **fuente oficial/primaria** y, cuando no sea un organismo con autoridad directa o sea información dispersa, incluir **fuentes secundarias para contrastar datos**.

### Fuente Principal `[ID-OFICIAL]` — [Nombre del Organismo / Fuente]

- **Organismo y autoridad:** [ej. Cruz Roja, IGN, SAS, Instituto Toxicológico, Junta de Andalucía]
- **URL de catálogo / Portal:** [URL estable]
- **URL de descarga / API:** [Endpoint o enlace de descarga directa]
- **Qué se obtiene:** [Campos, protocolos, tablas, capítulos o capas]
- **Formato y adquisición:** `JSON | CSV | PDF | HTML | WFS | manual`
- **Fiabilidad:** `alta (oficial)`
- **Licencia:** [Comprobada: CC BY, datos abiertos, reutilización autorizada]
- **Cadencia de publicación del origen:** [ej. mensual, anual, estática]
- **Notas de estabilidad:** [Versionado, URLs fijas, estructura de datos]

### Fuente Secundaria / Contraste `[ID-SECUNDARIA]` — [Nombre de Referencia]

- **Organismo o autor:** [Entidad de apoyo, manual de referencia o guía técnica]
- **URL / Referencia:** [URL o ISBN]
- **Uso para contraste:** [Qué datos concretos se verifican contra esta fuente para evitar errores]
- **Fiabilidad:** `media | auxiliar`

---

## 5. Bloques Requeridos para el RAG y Mapeo

Detallar la información exacta y atómica que debe existir en el RAG al final:

| Bloque destino | Fuente | Campos de origen | Salida normalizada | Destino (`data/processed/`) | Validación requerida |
|---|---|---|---|---|---|
| `[nombre_bloque]` | `[ID]` | `[origen]` | `[campos/texto]` | `csv/...` o `md/...` | `automática | médica | humana` |

---

## 6. Almacenamiento Raw y Procesado

### A. Instantánea Original (`data/raw/`)
```text
data/raw/<identificador>/<AAAA-MM-DD>/
├── original.<ext>
└── MANIFEST.json
```

### B. Resultado Procesado (`data/processed/`)
* Si es tabular/estructurado: `data/processed/csv/<identificador>.csv` (conforme a [`data/processed/csv/PLANTILLA.csv`](../../data/processed/csv/PLANTILLA.csv)).
* Si es narrativo/guía: `data/processed/md/<identificador>.md` (conforme a [`data/processed/md/PLANTILLA.md`](../../data/processed/md/PLANTILLA.md)).

---

## 7. Controles de Calidad y Criterios de Rechazo

- **Completitud:** Toda entrada debe tener coordenadas válidas o instrucciones de primeros auxilios verificables.
- **Criterios de rechazo inmediato:**
  - Contenido sin fuente contrastada.
  - Procedimientos médicos obsoletos o peligrosos (ej. succionar veneno de serpiente, aplicar torniquetes sin indicación estricta).
  - Listados sin fecha o con teléfonos no institucionales.

---

## 8. Historial de Versiones

| Fecha | Estado | Autor / Revisor | Cambio |
|---|---|---|---|
| `AAAA-MM-DD` | `propuesta` | `[Nombre/Rol]` | Creación inicial de la ficha. |

[← Volver al índice de fuentes RAG](README.md)
