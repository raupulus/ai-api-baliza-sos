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
| [`csv/guardia_civil_dependencias_cadiz.csv`](csv/guardia_civil_dependencias_cadiz.csv) | Dependencias Guardia Civil de Cádiz | [`directorios-emergencia.md`](../../docs/rag/directorios-emergencia.md) | CSV | 52 | En staging (pendiente) |
| [`csv/municipios_cadiz.csv`](csv/municipios_cadiz.csv) | 45 municipios de Cádiz (WGS84) | [`municipios-geografia.md`](../../docs/rag/municipios-geografia.md) | CSV | 45 | En staging (pendiente) |
| [`csv/transporte_publico_cadiz.csv`](csv/transporte_publico_cadiz.csv) | Paradas de autobús (CMTBC + CTMCG, GTFS unificado CTAN) | [`transporte-publico.md`](../../docs/rag/transporte-publico.md) | CSV | 367 | En staging (pendiente) |
| [`csv/transporte_publico_renfe_cadiz.csv`](csv/transporte_publico_renfe_cadiz.csv) | Estaciones Cercanías (C-1/C-1a) + paradas Tranvía de la Bahía (T-1), núcleo Cádiz del GTFS Renfe | [`transporte-publico.md`](../../docs/rag/transporte-publico.md) | CSV | 30 | En staging (pendiente) |
| [`csv/estaciones_ferrocarril_cadiz.csv`](csv/estaciones_ferrocarril_cadiz.csv) | Estaciones/instalaciones ferroviarias de Cádiz (WFS INSPIRE ADIF) | [`transporte-publico.md`](../../docs/rag/transporte-publico.md) | CSV | 52 | En staging (pendiente) |
| [`csv/lineas_autobus_cadiz.csv`](csv/lineas_autobus_cadiz.csv) | Líneas de autobús (referencia, no se migra a staging) | [`transporte-publico.md`](../../docs/rag/transporte-publico.md) | CSV | 71 | Referencia |
| [`csv/lineas_cercanias_cadiz.csv`](csv/lineas_cercanias_cadiz.csv) | Líneas Cercanías/Trambahía Cádiz (referencia, no se migra) | [`transporte-publico.md`](../../docs/rag/transporte-publico.md) | CSV | 12 | Referencia |
| [`csv/peces_especies_cadiz.csv`](csv/peces_especies_cadiz.csv) | Inventario de especies pesqueras (código FAO + nombre científico) | [`flora-fauna.md`](../../docs/rag/flora-fauna.md) | CSV | 136 | Referencia (no se migra) |
| [`csv/overpass_pois_cadiz.csv`](csv/overpass_pois_cadiz.csv) | POIs de OSM (playas, faros, agua, hospitales, farmacias, refugios) | [`overpass-osm.md`](../../docs/rag/overpass-osm.md) | CSV | 1505 | En staging (pendiente) |
| [`csv/wikidata_lugares_cadiz.csv`](csv/wikidata_lugares_cadiz.csv) | Lugares naturales de Cádiz (playas, faros, parques, cabos, ríos) | [`wikidata.md`](../../docs/rag/wikidata.md) | CSV | 200 | En staging (pendiente) |
| [`csv/gbif_especies_cadiz.csv`](csv/gbif_especies_cadiz.csv) | Especies con presencia en el BBOX (flora/fauna) | [`gbif.md`](../../docs/rag/gbif.md) | CSV | 30 | En staging (pendiente) |
| [`csv/nga_toponimos_cadiz.csv`](csv/nga_toponimos_cadiz.csv) | Topónimos críticos NGA (agua, equipamientos, litoral, cuevas) | [`territorio-medio-natural.md`](../../docs/rag/territorio-medio-natural.md) | CSV | 2171 | En staging (pendiente) |
| [`md/apoyo_psicosocial_principios.md`](md/apoyo_psicosocial_principios.md) | Principios de intervención psicosocial | [`apoyo-psicosocial.md`](../../docs/rag/apoyo-psicosocial.md) | MD | 1 | En staging (pendiente) |
| [`md/apoyo_psicosocial_niveles.md`](md/apoyo_psicosocial_niveles.md) | Niveles escalonados de apoyo psicosocial | [`apoyo-psicosocial.md`](../../docs/rag/apoyo-psicosocial.md) | MD | 1 | En staging (pendiente) |
| [`md/apoyo_psicosocial_autocuidado.md`](md/apoyo_psicosocial_autocuidado.md) | Autocuidado tras un desastre | [`apoyo-psicosocial.md`](../../docs/rag/apoyo-psicosocial.md) | MD | 1 | En staging (pendiente) |
| [`md/apoyo_psicosocial_infancia.md`](md/apoyo_psicosocial_infancia.md) | Apoyo a niños tras un desastre | [`apoyo-psicosocial.md`](../../docs/rag/apoyo-psicosocial.md) | MD | 1 | En staging (pendiente) |
| [`md/apoyo_psicosocial_alarma.md`](md/apoyo_psicosocial_alarma.md) | Cuándo buscar ayuda profesional | [`apoyo-psicosocial.md`](../../docs/rag/apoyo-psicosocial.md) | MD | 1 | En staging (pendiente) |
| [`md/primeros_auxilios_rcp.md`](md/primeros_auxilios_rcp.md) | RCP básica | [`primeros-auxilios.md`](../../docs/rag/primeros-auxilios.md) | MD | 1 | En staging (pendiente) |
| [`md/primeros_auxilios_atragantamiento.md`](md/primeros_auxilios_atragantamiento.md) | Atragantamiento | [`primeros-auxilios.md`](../../docs/rag/primeros-auxilios.md) | MD | 1 | En staging (pendiente) |
| [`md/primeros_auxilios_hemorragias.md`](md/primeros_auxilios_hemorragias.md) | Heridas y hemorragias | [`primeros-auxilios.md`](../../docs/rag/primeros-auxilios.md) | MD | 1 | En staging (pendiente) |
| [`md/primeros_auxilios_quemaduras.md`](md/primeros_auxilios_quemaduras.md) | Quemaduras | [`primeros-auxilios.md`](../../docs/rag/primeros-auxilios.md) | MD | 1 | En staging (pendiente) |
| [`md/primeros_auxilios_traumatismos.md`](md/primeros_auxilios_traumatismos.md) | Contusiones/esguinces/fracturas | [`primeros-auxilios.md`](../../docs/rag/primeros-auxilios.md) | MD | 1 | En staging (pendiente) |
| [`md/primeros_auxilios_sincope.md`](md/primeros_auxilios_sincope.md) | Pérdida de conocimiento | [`primeros-auxilios.md`](../../docs/rag/primeros-auxilios.md) | MD | 1 | En staging (pendiente) |
| [`md/primeros_auxilios_intoxicaciones.md`](md/primeros_auxilios_intoxicaciones.md) | Intoxicaciones | [`primeros-auxilios.md`](../../docs/rag/primeros-auxilios.md) | MD | 1 | En staging (pendiente) |
| [`md/primeros_auxilios_mordedura_serpiente.md`](md/primeros_auxilios_mordedura_serpiente.md) | Mordedura de serpiente (víbora) | [`primeros-auxilios.md`](../../docs/rag/primeros-auxilios.md) | MD | 1 | En staging (pendiente) |
| [`md/primeros_auxilios_picaduras_marinas.md`](md/primeros_auxilios_picaduras_marinas.md) | Picaduras marinas (medusas y pez araña) | [`primeros-auxilios.md`](../../docs/rag/primeros-auxilios.md) | MD | 1 | En staging (pendiente) |
| [`md/primeros_auxilios_picaduras_insectos_aracnidos.md`](md/primeros_auxilios_picaduras_insectos_aracnidos.md) | Picaduras de insectos y arácnidos | [`primeros-auxilios.md`](../../docs/rag/primeros-auxilios.md) | MD | 1 | En staging (pendiente) |
| [`md/primeros_auxilios_erc_svb_adulto.md`](md/primeros_auxilios_erc_svb_adulto.md) | SVB adulto (ERC 2025) | [`primeros-auxilios.md`](../../docs/rag/primeros-auxilios.md) | MD | 1 | En staging (pendiente) |
| [`md/primeros_auxilios_erc_dea_adulto.md`](md/primeros_auxilios_erc_dea_adulto.md) | DEA adulto (ERC 2025) | [`primeros-auxilios.md`](../../docs/rag/primeros-auxilios.md) | MD | 1 | En staging (pendiente) |
| [`md/primeros_auxilios_erc_svbp.md`](md/primeros_auxilios_erc_svbp.md) | SVB pediátrico (ERC 2025) | [`primeros-auxilios.md`](../../docs/rag/primeros-auxilios.md) | MD | 1 | En staging (pendiente) |
| [`md/primeros_auxilios_erc_ovace.md`](md/primeros_auxilios_erc_ovace.md) | Obstrucción vía aérea pediátrica (ERC 2025) | [`primeros-auxilios.md`](../../docs/rag/primeros-auxilios.md) | MD | 1 | En staging (pendiente) |
| [`md/primeros_auxilios_erc_ovace_adulto.md`](md/primeros_auxilios_erc_ovace_adulto.md) | Atragantamiento adulto (ERC 2025) | [`primeros-auxilios.md`](../../docs/rag/primeros-auxilios.md) | MD | 1 | En staging (pendiente) |
| [`md/primeros_auxilios_erc_dolor_toracico.md`](md/primeros_auxilios_erc_dolor_toracico.md) | Dolor torácico (ERC 2025) | [`primeros-auxilios.md`](../../docs/rag/primeros-auxilios.md) | MD | 1 | En staging (pendiente) |
| `md/proteccion_civil_*.md` (7) | Autoprotección: montaña, señales helicóptero, inundaciones, incendios, sismo, evacuación | [`proteccion-civil-autoproteccion.md`](../../docs/rag/proteccion-civil-autoproteccion.md) | MD | 7 | En staging (pendiente) |
| [`md/directorios_emergencias_112.md`](md/directorios_emergencias_112.md) | Teléfono único de emergencias 112 (RD 903/1997) | [`directorios-emergencia.md`](../../docs/rag/directorios-emergencia.md) | MD | 1 | En staging (pendiente) |
| [`md/directorios_emergencias_numeros.md`](md/directorios_emergencias_numeros.md) | Números 061, 091 y 016 (SAS, Policía, Igualdad) | [`directorios-emergencia.md`](../../docs/rag/directorios-emergencia.md) | MD | 1 | En staging (pendiente) |
| [`md/fauna_procesionaria.md`](md/fauna_procesionaria.md) | Procesionaria del pino: riesgo por contacto (`peligrosa`) | [`flora-fauna.md`](../../docs/rag/flora-fauna.md) | MD | 1 | En staging (pendiente) |
| [`md/toxicologia_biotoxinas_marinas.md`](md/toxicologia_biotoxinas_marinas.md) | Moluscos bivalvos y biotoxinas (marea roja) | [`toxicologia-sustancias.md`](../../docs/rag/toxicologia-sustancias.md) | MD | 1 | En staging (pendiente) |
| [`md/legislacion_derechos_constitucion.md`](md/legislacion_derechos_constitucion.md) | Derechos y deberes en emergencias (CE art. 15 y 30.4) | [`legislacion-derechos.md`](../../docs/rag/legislacion-derechos.md) | MD | 1 | En staging (pendiente) |
| [`md/agricultura_sectores_cadiz.md`](md/agricultura_sectores_cadiz.md) | Principales sectores agrarios de Cádiz | [`agricultura-ganaderia.md`](../../docs/rag/agricultura-ganaderia.md) | MD | 1 | En staging (pendiente) |
| [`md/fiestas_festivos_2026.md`](md/fiestas_festivos_2026.md) | Fiestas laborales Andalucía 2026 | [`fiestas-tradiciones.md`](../../docs/rag/fiestas-tradiciones.md) | MD | 1 | En staging (pendiente) |
| [`md/primeros_auxilios_erc_hipoglucemia.md`](md/primeros_auxilios_erc_hipoglucemia.md) | Hipoglucemia (ERC 2025) | [`primeros-auxilios.md`](../../docs/rag/primeros-auxilios.md) | MD | 1 | En staging (pendiente) |

---

## 5. Ingesta a Base de Datos

Para volcar estos datasets a la base vectorial de PostgreSQL, ejecutar:

```bash
# Ingesta manual desde el entorno del proyecto
python3 scripts/actualizar_fuente.py --input data/processed/csv/mi_archivo.csv
```
