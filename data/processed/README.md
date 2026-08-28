# Datasets y Fragmentos Procesados para el RAG (`data/processed/`)

Este directorio contiene los **resultados limpios, estructurados y validados** listos para ser indexados en la base de datos PostgreSQL (`pgvector`) y alimentar el asistente offline.

---

## 1. Estructura del Directorio

```text
data/processed/
├── README.md               # Este índice maestro
├── csv/                    # Datasets tabulares estructurados (entidades, coordenadas, teléfonos)
│   ├── PLANTILLA.csv       # Estándar de formato para datos tabulares
│   └── ...                 # Archivos CSV por dominio temático
└── md/                     # Guías, protocolos y fragmentos narrativos de alta densidad
    ├── PLANTILLA.md        # Estándar de formato con frontmatter YAML
    └── ...                 # Archivos Markdown por protocolo o especie
```

---

## 2. Criterios de Inclusión en `data/processed/`

1. **Procedencia de una Ficha en `docs/rag/`:** Todo archivo procesado debe responder a una ficha de especificación en `docs/rag/`.
2. **Limpieza total:** Sin encabezados de navegación, sin publicidad, sin HTML suelto y sin texto de relleno ("paja").
3. **Validación Humana Obligatoria:** Todo contenido médico, primeros auxilios o de especies peligrosas/tóxicas debe contar con el campo `fecha_validacion_humana` y `revisor` acreditado antes de ser indexado en producción.
4. **Respeto a límites LoRa/Meshtastic:** Las instrucciones deben ser claras, atómicas y directamente accionables en el terreno.

---

## 3. Formatos Estándar

### A. Datos Estructurados (`csv/`)
* **Uso:** Directorios telefónicos de emergencia, coordenadas WGS84 de municipios, frecuencias de radio (REMER/PMR), farmacias y centros de salud.
* **Plantilla:** Ver [`csv/PLANTILLA.csv`](csv/PLANTILLA.csv).
* **Columnas obligatorias:** `id`, `categoria`, `subcategoria`, `titulo`, `contenido`, `fuente`, `fuente_url`, `nivel_confianza`, `provincia`, `municipio`, `lat`, `lon`, `fecha_verificacion`.

### B. Fragmentos Narrativos (`md/`)
* **Uso:** Protocolos de soporte vital, inmovilizaciones, tratamientos de picaduras/mordeduras, identificación de setas tóxicas o plantas venenosas, técnicas de orientación y supervivencia.
* **Plantilla:** Ver [`md/PLANTILLA.md`](md/PLANTILLA.md).
* **Frontmatter YAML obligatorio:** Metadatos completos de auditoría, categoría, nivel de confianza y fuentes oficiales.

---

## 4. Registro Maestro de Archivos Procesados

| Archivo | Dominio / Tema | Ficha de origen (`docs/rag/`) | Formato | Registros / Fragmentos | Estado |
|---|---|---|---|---:|---|
| [`csv/telefonos_emergencia_cadiz_municipios.csv`](csv/telefonos_emergencia_cadiz_municipios.csv) | Directorios de emergencia de Cádiz | [`directorios-emergencia.md`](../../docs/rag/directorios-emergencia.md) | CSV | 45 | En validación |

---

## 5. Ingesta a Base de Datos

Para volcar estos datasets a la base vectorial de PostgreSQL, ejecutar:

```bash
# Ingesta manual desde el entorno del proyecto
python3 scripts/actualizar_fuente.py --input data/processed/csv/mi_archivo.csv
```
