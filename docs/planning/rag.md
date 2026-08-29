# Plan Maestro RAG — Sistema de Conocimiento Offline para Emergencias en Cádiz

> **Fecha de creación:** 2026-08-28
> **Última actualización:** 2026-08-28
> **Estado:** Activo — reconciliado con las fuentes de verdad del repositorio.
> **Ámbito:** Especificación completa para la generación, validación y mantenimiento del corpus RAG en `docs/rag/` y `data/processed/`.

> [!IMPORTANT]
> Este documento es **planificación de gobierno**. No genera conectores, no ingiere contenido ni declara validación médica/biológica por sí mismo. Las fichas reales viven en `docs/rag/`; los datos limpios, en `data/processed/`.

---

## 1. Objetivos del Plan

Este documento define **el qué, cómo, cuándo y quién** para:

1. **Estructurar** las fichas de especificación en `docs/rag/` con separación atómica y trazabilidad total.
2. **Reconciliar** la planificación con el estado real del repositorio (fichas existentes, conectores heredados, datos procesados).
3. **Garantizar calidad** con checklists atómicos por sección y *checkpoints* humanos obligatorios.
4. **Minimizar el consumo de tokens** del LLM local con datos atómicos, sin redundancia y pre-procesados.
5. **Detectar huecos críticos** para una situación de emergencia/supervivencia y proponer su cobertura.
6. **Facilitar actualizaciones futuras** sabiendo exactamente qué se extrajo, de dónde, cuándo y con qué problemas.

---

## 2. Fuentes de Verdad y Estado Actual (reconciliación)

La planificación **no puede contradecir** el estado real. Estas son las fuentes de verdad:

| Fuente de verdad | Qué define | Estado |
|---|---|---|
| `docs/rag/README.md` | Metodología y **registro maestro** de fichas. | Vigente |
| `docs/rag/catalogo-adquisicion.md` | Trazabilidad completa de `data/info/valorar.md` → fichas. | Vigente |
| `docs/rag/PLANTILLA_FUENTE.md` | Estructura obligatoria de cada ficha. | Vigente |
| `docs/info/05-contratos-datos.md` | Formato de fragmento RAG y esquema relacional. | Vigente |
| `docs/info/01-vision-requisitos.md` | Límites duros (230 bytes × 3, hardware mínimo). | Vigente |
| `data/info/fuentes_actuales.md` | Diagnóstico de conectores heredados. | Vigente |
| `data/info/valorar.md` | Cuaderno de trabajo del usuario (entrada, no autoridad). | Protegido |

### 2.1. Estado real de `docs/rag/`

El listado de `data/info/estado.md` (25 ítems) fue **consolidado** por `catalogo-adquisicion.md` en **17 fichas temáticas + 3 fichas de conector + documentos de gobierno** (ver `docs/rag/README.md`). **No** existe una ficha por URL ni por cada ítem suelto del cuaderno.

**Fichas temáticas existentes (17):**

| Ficha | Prioridad | Destino | Estado de implementación (2026-08-28) |
|---|---:|---|---|
| `primeros-auxilios.md` | P0 | Híbrido | ✅ Normalizado: 17 fragmentos (INGESA/ERC + mordeduras/picaduras) |
| `toxicologia-sustancias.md` | P0 | RAG + contactos | ⚠️ Parcial: 1 fragmento (biotoxinas marinas). PNSD descartado (prevención, no aguda) |
| `apoyo-psicosocial.md` | P1 | RAG | ✅ Normalizado: 5 fragmentos |
| `proteccion-civil-autoproteccion.md` | P0 | RAG | ✅ Normalizado: 7 fragmentos (montaña + DGPCE) |
| `preparacion-supervivencia.md` | P0/P1 | Híbrido | ⚠️ Hueco: guía de agua regulatoria (licencia aclarada); falta fuente ciudadana de potabilización/kits |
| `legislacion-derechos.md` | P2 | Híbrido | ✅ Normalizado: 2 fragmentos (Carta DFUE + Constitución) |
| `transporte-publico.md` | P1 | Estructurado | ✅ Normalizado: 449 fragmentos (GTFS 367 + ADIF 52 + Renfe 30), geocodificado |
| `flora-fauna.md` | P0/P1 | Híbrido | ✅ Normalizado: 31 fragmentos (GBIF 30 + procesionaria 1); peces 136 en CSV de referencia |
| `territorio-medio-natural.md` | P0/P1 | Geoespacial | ⚠️ Parcial: 2171 topónimos NGA; senderos/EENNPP pendientes |
| `municipios-geografia.md` | P1 | Geoespacial | ✅ Normalizado: 45 municipios + NGA |
| `historia-patrimonio.md` | P3 | Híbrido | ⛔ Conector heredado bloqueado (sin trazabilidad) |
| `fiestas-tradiciones.md` | P2 | Híbrido | ✅ Normalizado: 1 fragmento (festivos 2026, BOJA) |
| `directorios-emergencia.md` | P0 | Estructurado | ✅ Normalizado: 54 (GC 52 + 112 1 + 016 1); política de vigencia definida |
| `agricultura-ganaderia.md` | P2 | Híbrido | ✅ Normalizado: 1 fragmento (sector agrario 2023); RAIF 28 548 en CSV de referencia |
| `radio-comunicaciones.md` | P1 | Híbrido | 📦 Descargado (Meshtastic + BOE CNAF/reglamento), no normalizado (técnico/inglés) |
| `astronomia-mareas-orientacion.md` | P1 | Híbrido | 📦 Descargado (IGN atlas), no normalizado (material de referencia) |
| `clima-meteorologia.md` | P0/P1 | RAG + tabla de umbrales | ✅ Normalizado: 1 fragmento (calor); umbrales AEMET pendientes |

**Fichas de conector (3, transversales):**

| Ficha | Uso | Código detectado |
|---|---|---|
| `overpass-osm.md` | POIs geográficos complementarios | `src/updater/sources/overpass.py` |
| `wikidata.md` | Entidades y metadatos complementarios | `src/updater/sources/wikidata.py` |
| `gbif.md` | Ocurrencias de biodiversidad | `src/updater/sources/gbif.py` |

### 2.2. Estado real de `data/processed/` y `data/staging/` (2026-08-28)

**Corpus en staging: 4474 fragmentos validados y aprobados (0 pendientes)** (desglose por fuente en `docs/rag/README.md`):

| Dominio | Fragmentos | Origen |
|---|---:|---|
| Geografía | 3216 | 45 municipios DERA + 1505 Overpass + 200 Wikidata + 2171 NGA (curado) |
| Supervivencia | 661 | Overpass (agua potable/refugios) |
| Transporte | 449 | GTFS CTAN (367) + ADIF (52) + Renfe (30) |
| Directorios | 54 | Guardia Civil (52) + 112 (1) + 016 (1) |
| Orientación | 28 | Overpass (faros) |
| Fauna | 25 | GBIF (24) + procesionaria (1) |
| Primeros auxilios | 17 | INGESA/ERC (14) + mordeduras/picaduras (3) |
| Protección civil | 7 | Guardia Civil montaña (3) + DGPCE (4) |
| Flora | 6 | GBIF |
| Apoyo psicosocial | 5 | OMS/Sanidad |
| Legislación | 2 | Carta DFUE (1) + Constitución CE (1) |
| Agricultura | 1 | Junta de Andalucía (sector agrario 2023) |
| Cultura/historia | 1 | BOJA festivos 2026 |
| Clima | 1 | Sanidad (calor) |
| Toxicología | 1 | Junta de Andalucía (biotoxinas) |

**Referencias estructuradas (no se migran a RAG):** `nga_toponimos_cadiz_referencia.csv` (14 855), `peces_especies_cadiz.csv` (136), `lineas_autobus_cadiz.csv` (71), `lineas_cercanias_cadiz.csv` (12), RAIF Cádiz (`raif/cadiz/`, 28 548 registros), OCR de peces/DGPCE en `data/raw/`.

**Flujo vigente:** `data/raw/downloads/` → normalizar → `data/processed/` → `scripts/migrar_a_staging.py` → `data/staging/pendientes/` → `scripts/review.py` (aprobar) → `python -m updater.cli --reindex-aprobados`.

> ⚠️ El antiguo `telefonos_emergencia_cadiz_municipios.csv` (generado por IA) fue **purgado** (T15); sustituido por el directorio oficial de Guardia Civil + fragmento 112.

### 2.3. Conectores heredados y su estado de bloqueo

| Conector | Contenido | Bloqueo |
|---|---|---|
| `primeros_auxilios_avanzado.py` | 13 fragmentos sintéticos | Licencia genérica, revisor no identificado, mezcla dominios |
| `flora_fauna_cadiz.py` | 13 fichas botánicas/fauna | Sin citas por fragmento, fecha de validación falsa |
| `municipios_cadiz.py` | 46 fragmentos de 45 municipios | Formato rígido, sin triangulación visual |
| `fiestas_cadiz.py` | 11 fragmentos | Fechas sin vigencia estructurada |
| `historia_cadiz.py` | 6 fragmentos | Sin trazabilidad por afirmación |
| `overpass.py`, `gbif.py`, `wikidata.py` | Dinámicos (API online) | ✅ Fijados a CSV offline (2026-08-28): Overpass 1505 POIs, Wikidata 200 lugares, GBIF 30 especies → `data/processed/csv/`. |
| `seed_corpus.py` | 6 fragmentos genéricos ("paja") | Debe purgarse |

**Regla de gobierno:** ningún conector heredado se reejecuta para **nuevas ingestas** hasta auditar su trazabilidad y sustituir las etiquetas no demostradas.

---

## 3. Requisitos Obligatorios para `docs/rag/`

Toda ficha debe cumplir (extraído de `data/info/estado.md`, refinado):

- [ ] **Separación atómica de datos** por sección (1 concepto = 1 sección).
- [ ] **Checklist al final** con **cada sección** (nunca genérico).
- [ ] **Metadatos de fechas:**
  - Creación de la ficha.
  - Última actualización de la ficha.
  - Última extracción de datos desde fuentes.
  - Última generación de `data/processed/`.
  - Próxima actualización recomendada.
- [ ] **Descripciones detalladas** del bloque y de cada sección (justo debajo de su título).
- [ ] **Anotación de problemas** encontrados (con fecha).
- [ ] **Mapeo de datos** (campos de origen → campos normalizados) para no re-mapear en el futuro.
- [ ] **Enlace bidireccional** al archivo generado en `data/processed/`.
- [ ] **Licencia** verificada, o `pendiente de verificar` explícito.
- [ ] **Ciclo de vida:** `propuesta | en_validacion | aprobada | implementada | descartada`.
- [ ] **Puntos de origen** en `data/info/valorar.md` (líneas concretas).

---

## 4. Taxonomía del Corpus (estructura consolidada y trazable)

Se agrupa en **categorías lógicas de mantenimiento**, pero cada ficha conserva su identidad y trazabilidad individual. La nomenclatura es **exactamente** la de los archivos reales de `docs/rag/`.

### 🏥 **Categoría 1 — SALUD Y EMERGENCIAS MÉDICAS** *(P0)*

> Validación obligatoria: profesional sanitario (medicina/enfermería). Toxicología añade perfil específico.

| Ficha | Secciones clave | Fuentes primarias | Destino |
|---|---|---|---|
| `primeros-auxilios.md` | Evaluación inicial, RCP/DEA, atragantamiento, hemorragias/traumatismos, parto inminente, traqueostomía existente, autocuidados comunes | ERC-2025, INGESA, Cruz Roja, SAS | `md/primeros-auxilios/` + CSV de protocolos |
| `toxicologia-sustancias.md` | Sustancias y cuadros agudos, primera respuesta, exposición accidental, contactos (SIT/INTCF) | SIT/INTCF, PNSD, INGESA | `md/toxicologia/` + CSV de sustancias |
| `apoyo-psicosocial.md` | Crisis de ansiedad, duelo, estrés post-emergencia, comunicación con víctimas | Cruz Roja, SAMU, SAS | `md/apoyo-psicosocial/` |

### 🌿 **Categoría 2 — RIESGOS BIOLÓGICOS Y MEDIO NATURAL** *(P0/P1)*

> Validación obligatoria: biólogo; toxicidad/comestibilidad añade sanitario o de seguridad alimentaria.

| Ficha | Secciones clave | Fuentes primarias | Destino |
|---|---|---|---|
| `flora-fauna.md` | Taxonomía, presencia, riesgo biológico (picaduras/mordeduras/toxinas), peces, contaminación, uso histórico | REDIAM, EIDOS, Junta, AESAN, AEMPS | Híbrido (tabla + RAG) |
| `territorio-medio-natural.md` | Playas, ríos, embalses, afluentes, parques naturales, senderos | IGN, REDIAM, Junta de Andalucía | Geoespacial + `md/` |

### 🗺️ **Categoría 3 — GEOGRAFÍA Y LOCALIZACIÓN** *(P0/P1)*

> Validación: IGN/IECA u organismo competente.

| Ficha | Secciones clave | Fuentes primarias | Destino |
|---|---|---|---|
| `municipios-geografia.md` | 45 municipios, núcleos, pedanías, topónimos, cumbres, altitud | IGN, IECA, Diputación de Cádiz | `csv/municipios_cadiz.csv` |
| `directorios-emergencia.md` | GC, Policía Nacional/local, Protección Civil, Cruz Roja, SAS, 112, sedes | Guardia Civil, Policía, SAS, Diputación | `csv/directorios_emergencia.csv` |

### 🛡️ **Categoría 4 — PROTECCIÓN CIVIL Y AUTOPROTECCIÓN** *(P0)*

> Validación obligatoria: Protección Civil, Guardia Civil, DGT.

| Ficha | Secciones clave | Fuentes primarias | Destino |
|---|---|---|---|
| `proteccion-civil-autoproteccion.md` | Inundaciones, incendios forestales, terremotos, evacuación, autoprotección | DGPCE, Guardia Civil, Policía | `md/proteccion_civil/` |
| `preparacion-supervivencia.md` | Kits (hogar/montaña/coche/mascotas), reservas de alimentos, potabilización, refugio, señales de socorro | DGPCE, Cruz Roja, manuales de montaña | `md/preparacion/` |

### 📡 **Categoría 5 — COMUNICACIONES** *(P1)*

> Validación: URE, normativa española de radiofrecuencia, documentación oficial de Meshtastic.

| Ficha | Secciones clave | Fuentes primarias | Destino |
|---|---|---|---|
| `radio-comunicaciones.md` | Meshtastic/LoRa (868 MHz), límite 230 bytes × 3, protocolos de emergencia (SOS/MÉDICO/INCENDIO), Winlink/VARA/APRS, frecuencias, REMER | URE, ITU, Meshtastic, REMER | `md/comunicaciones/` + `csv/frecuencias_emergencia.csv` |

### 🧭 **Categoría 6 — ORIENTACIÓN, ASTRONOMÍA Y MAREAS** *(P1)*

> Validación: ROA, IGN, Puertos del Estado (con licencia confirmada).

| Ficha | Secciones clave | Fuentes primarias | Destino |
|---|---|---|---|
| `astronomia-mareas-orientacion.md` | Sol/Luna (orto/ocaso/fases), almanaque, orientación por estrellas, mareas | ROA, IGN, Puertos del Estado | Tablas precalculadas + `md/orientacion/` |

### 🚌 **Categoría 7 — TRANSPORTE** *(P1/P2)*

> Validación: Consorcio de Transporte de Cádiz, Renfe, empresas.

| Ficha | Secciones clave | Fuentes primarias | Destino |
|---|---|---|---|
| `transporte-publico.md` | Líneas de autobús (Bahía de Cádiz, Campo de Gibraltar), tren, paradas críticas | CTAN/Consorcio, Renfe (GTFS) | `csv/transporte_publico.csv` |

### 🌾 **Categoría 8 — SECTOR PRIMARIO** *(P2)*

> Validación: Junta de Andalucía, Ministerio de Agricultura.

| Ficha | Secciones clave | Fuentes primarias | Destino |
|---|---|---|---|
| `agricultura-ganaderia.md` | Cultivos típicos, sanidad vegetal, ganado, riesgos zoonóticos, puntos de agua | Junta de Andalucía, MAPA, SEIASA | `csv/agricultura_ganaderia.csv` |

### 🎭 **Categoría 9 — CULTURA Y SOCIEDAD** *(P2/P3)*

> Validación: Patronato de Turismo, ayuntamientos, IAPH.

| Ficha | Secciones clave | Fuentes primarias | Destino |
|---|---|---|---|
| `fiestas-tradiciones.md` | Festivos oficiales, carnavales, ferias, romerías (con vigencia) | BOJA, Patronato, ayuntamientos | `csv/fiestas_cadiz.csv` |
| `historia-patrimonio.md` | Hitos históricos (Gadir, 1812, Trafalgar), patrimonio por municipio | IAPH, Junta de Andalucía | `md/historia_patrimonio/` |

### ⚖️ **Categoría 10 — LEGAL** *(P2)*

> Validación: BOE, Junta de Andalucía.

| Ficha | Secciones clave | Fuentes primarias | Destino |
|---|---|---|---|
| `legislacion-derechos.md` | Normativa de emergencias, derechos en catástrofes, corpus legal acotado | BOE, EUR-Lex, Junta de Andalucía | `md/legislacion/` |

### 🔌 **Fichas de conector (transversales)**

No sustituyen a la fuente competente para teléfonos, riesgos médicos, comestibilidad o vigencia legal. Sirven para **complementar y detectar faltantes**, y deben **fijarse en CSV offline** para no depender de API en operación.

| Ficha | Complemento | Precaución |
|---|---|---|
| `overpass-osm.md` | Farmacias, fuentes potables, centros sanitarios (POIs) | Coordenadas brutas; volcar offline |
| `wikidata.md` | Hospitales, faros, entidades territoriales | Inconsistencia; fijar en CSV |
| `gbif.md` | Ocurrencias de biodiversidad | Ruido taxonómico; filtrar con lupa |

---

## 5. Huecos Críticos Identificados para Emergencias/Supervivencia

El corpus actual no cubre todo lo necesario ante una catástrofe. Se proponen las siguientes ampliaciones, ordenadas por impacto.

### 5.1. 🔴 **NUEVA FICHA — `clima-meteorologia.md`** *(P0/P1)*

**No existe** una ficha de meteorología/clima, pese a que el enum de categorías (`docs/info/05-contratos-datos.md`) ya contempla `clima`. Es un hueco grave para Cádiz.

- **Necesidad:** olas de calor, DANAs, levante/terral, tormentas, nieblas costeras, riesgo de incendio por viento. Una persona aislada necesita interpretar el cielo y conocer los umbrales de peligro.
- **Alcance offline (no predicción en tiempo real):** climatología estacional por comarca, señales de mal tiempo (nubes, viento, presión), umbrales de riesgo, autoprotección meteorológica.
- **Fuentes:** AEMET (OpenData), DGPCE, Puertos del Estado (meteorología marina), Protección Civil de Andalucía.
- **Destino:** `md/clima/` + tabla de umbrales por comarca.

### 5.2. 🟠 **Ampliación — `directorios-emergencia.md`: helisuperficies y puntos de evacuación** *(P0)*

Falta estructurar los **puntos de aterrizaje de helicópteros (helisuperficies), helipuertos y zonas de evacuación/reunión** por municipio. Son críticos para rescate y deben tener coordenadas exactas.

### 5.3. 🟠 **Ampliación — `proteccion-civil-autoproteccion.md`: riesgo sísmico y tsunami** *(P0/P1)*

El Golfo de Cádiz es zona de riesgo sísmico y de tsunami. Debe incluirse una sección específica de **terremotos y maremotos** (protocolo de alejamiento de costa, señales de retirada del mar, zonas altas).

### 5.4. 🟡 **Ampliación — `flora-fauna.md`: enfermedades transmitidas por vectores** *(P1)*

Añadir **mosquitos (virus del Nilo Occidental), garrapatas, flebotomos** y otros vectores con presencia en Cádiz, síntomas orientativos y prevención. Fuente: SAS, ECDC, Junta de Andalucía.

### 5.5. 🟡 **Ampliación — `primeros-auxilios.md`: colectivos vulnerables** *(P0/P1)*

Reforzar secciones para **niños/lactantes, personas mayores, embarazadas y personas con discapacidad** (diferencias en RCP, dosis de seguridad, evacuación accesible). Ya se anota la falta de protocolo neonatal.

### 5.6. 🟢 **Consolidación — señalización visual/acústica de socorro** *(P1)*

Garantizar en `preparacion-supervivencia.md` la **señalización de socorro** completa: silbato (seis señales/min), espejo, fuego con humo, código suelo-aire, luz intermitente. Es la interfaz real entre víctima y rescate.

### 5.7. 🟢 **Consolidación — infraestructura crítica de agua** *(P0/P1)*

En `territorio-medio-natural.md`: **manantiales, fuentes públicas, depósitos y puntos de agua potable** fiables, con coordenadas y estado. Es de máxima prioridad en supervivencia (ya detectado en `fuentes_actuales.md`).

> **Criterio de decisión ficha nueva vs. sección:** crear ficha nueva solo si el dominio tiene **autoridad distinta + cadencia distinta + destino distinto**. `clima-meteorologia.md` cumple los tres; el resto se resuelve como sección dentro de una ficha existente.

---

## 6. Registro Maestro de Fuentes y Validación

### 6.1. Política de preferencia

1. Administración competente y texto/dataset oficial vigente.
2. Organismo científico o sociedad profesional responsable.
3. Datos abiertos colaborativos (OSM/Wikidata/GBIF) como **complemento**, nunca sustituto silencioso.
4. Fuentes comerciales o de usuarios solo si no hay alternativa, con confianza explícitamente inferior.

### 6.2. Matriz de fuentes validadas y bloqueos

| ID | Organismo | Dominio | Fiabilidad | Licencia | Cadencia | Bloqueo |
|---|---|---:|---|---|---|---|
| ERC-2025 | European Resuscitation Council | RCP/DEA | Alta (sociedad científica) | Pendiente | Por edición | Licencia por documento |
| INGESA | Ministerio de Sanidad | Primeros auxilios/urgencias | Alta | Pendiente | Semestral | Antigüedad |
| Cruz Roja | Cruz Roja Española | PA, kits, psicosocial | Alta | Pendiente | Trimestral | Por página |
| SAS | Servicio Andaluz de Salud | Autocuidados, centros | Alta | Pendiente | Mensual/Trimestral | Por ficha |
| SIT/INTCF | Instituto Toxicología | Toxicología | Alta | Pendiente | Semestral | — |
| PNSD | Plan Nacional sobre Drogas | Sustancias | Alta | Pendiente | Semestral | — |
| REDIAM | Junta de Andalucía | Flora/territorio | Alta | Pendiente (WFS) | Trimestral | Metadatos por capa |
| EIDOS | MITECO | Taxonomía | Alta | Pendiente | Trimestral | Por recurso |
| AESAN | Seguridad Alimentaria | Toxinas/contaminantes | Alta | Pendiente | Mensual/Anual | Por recurso |
| AEMPS | Medicamentos | Plantas medicinales | Alta | Pendiente | Anual | Por documento |
| GC | Guardia Civil | Dependencias, montaña | Alta | CC BY-NC-SA (verificar) | Mensual | Verificar ficha datos.gob |
| Policía | Policía Nacional | Comisarías, seguridad | Alta | CC BY (verificar) | Mensual | Por conjunto |
| DIPUCADIZ | Diputación de Cádiz | Entidades locales | Alta (por publicador) | Por dataset | Mensual | Por dataset |
| DGPCE | Protección Civil | Guías/autoprotección | Alta | Pendiente | Anual/Semestral | Por documento |
| DGT | Tráfico | Equipamiento V16, vial | Alta | Pendiente | Anual | Por documento |
| IGN/IECA | Geografía nacional/andaluz | Municipios, cartografía | Alta | Verificar CNIG | Anual/Puntual | Por descarga |
| ROA | Real Observatorio Armada | Efemérides/almanaque | Alta | Pendiente | Anual | **Publicación posiblemente comercial** |
| Puertos del Estado | Estado | Mareas | Alta | **Bloqueada redistribución** | Anual | **Confirmar por escrito** |
| BOE/EUR-Lex | Estado/UE | Legislación | Alta | Abierta (verificar) | Puntual | Versiones consolidadas |
| URE/ITU | Radio | Frecuencias/normativa | Alta | Pendiente | Puntual | ITU-2005 derechos reservados |
| Meshtastic | Comunidad oficial | Guía Meshtastic | Alta (oficial) | Verificar repo | Por versión | Versionar |
| REMER 2017 | Estado | Vademécum | Media (histórica) | Pendiente | Puntual | **Nunca autoridad única** |
| GBIF | Red biodiversidad | Ocurrencias | Variable | Por dataset | Según ficha | Ruido taxonómico |
| OSM/Overpass | Comunidad | POIs | Media | ODbL | Puntual | Complemento |
| Wikidata | Wikimedia | Entidades | Media | CC0 | Puntual | Inconsistencia |
| AEMET | Agencia Meteorología | Clima (nueva ficha) | Alta | Verificar OpenData | Anual/Diario | Por dataset |
| ECDC | Salud UE | Vectores | Alta | Verificar | Anual | Por recurso |

### 6.3. Bloqueos legales que paralizan la publicación

1. **Puertos del Estado** prohíbe transferir los datos descargados a terceros → la ficha de mareas queda **bloqueada** hasta confirmación escrita.
2. **ROA** puede tener publicación comercial → verificar antes de redistribuir almanaque/efemérides.
3. **ERC-2025, INGESA, Cruz Roja, SAS, DGPCE, DGT** tienen licencias *pendientes de verificar* por documento → no publicar hasta acreditarlas.
4. **Dioscórides 1998** tiene traducción presumiblemente protegida → solo metadatos históricos, nunca consejo médico.
5. **ITU HET 2005** derechos reservados → reutilización pendiente.

> **Regla de oro:** una URL pública **no equivale** a licencia abierta. Todo lo que no conste se marca `pendiente de verificar` y queda fuera de publicación.

---

## 7. Flujo de Trabajo por Ficha

### Fase 1 — Especificación (`docs/rag/`)
1. Crear/actualizar ficha con `PLANTILLA_FUENTE.md`.
2. Definir bloques atómicos, fuentes oficiales (URL estable), subsecciones y checklist por sección.
3. Asignar revisor (ej. médico para `primeros-auxilios.md`).

### Fase 2 — Descarga (`data/raw/`)
```
data/raw/<identificador>/<AAAA-MM-DD>/
├── <archivo_original>.<ext>
└── MANIFEST.json   # hash SHA-256, fuente, fecha UTC, cabeceras, licencia, versión
```
- **No editar** los originales. Conservar evidencia para reprocesado.

### Fase 3 — Procesamiento (`data/staging/`)
1. Limpiar ruido (navegación, publicidad), normalizar UTF-8, dividir en chunks atómicos.
2. **Checkpoint humano obligatorio** para: médico, toxicología, especies peligrosas, legal.
3. Generar **diff** respecto a la versión aprobada anterior.

### Fase 4 — Generación (`data/processed/`)
1. Producir:
   - **RAG vectorial:** `data/processed/md/<grupo>/<fragmentos>.md` (conforme a `md/PLANTILLA.md`).
   - **Estructurado:** `data/processed/csv/<grupo>.csv` (conforme a `csv/PLANTILLA.csv`).
   - **README.md** por directorio (descripción + condiciones de uso).
2. **Enlace bidireccional** ficha ↔ `data/processed/`.

### Fase 5 — Ingesta (PostgreSQL + pgvector)
1. Ejecutar `python3 scripts/actualizar_fuente.py --input <archivo>`.
2. Validar: fragmentos cargados, metadatos preservados, sin duplicados (hash `hash_contenido`).

---

## 8. Checklist Maestro por Ficha

- [ ] **Metadatos:** creación, última actualización, última extracción, próxima actualización.
- [ ] **Contenido:** separación atómica, descripciones por bloque/sección, fuentes oficiales, licencias, mapeo de campos.
- [ ] **Calidad:** checklist por sección, anotación de problemas, validación humana (si crítico).
- [ ] **Trazabilidad:** enlace a `data/processed/`, referencia a `data/raw/`, puntos de origen en `valorar.md`.

---

## 9. Priorización y Plazos

### 🔴 P0 — Críticos (supervivencia inmediata)

| Ficha / Acción | Razón | Estado |
|---|---|---|
| `primeros-auxilios.md` | Protocolo médico esencial | Auditar conector + asignar revisor |
| `toxicologia-sustancias.md` | Intoxicaciones y actuación | Crear contenido validado |
| `directorios-emergencia.md` | Ubicaciones y teléfonos de auxilio | Contrastar CSV IA + estructurar |
| `proteccion-civil-autoproteccion.md` | Guías oficiales de desastres | Descargar + validar |
| `preparacion-supervivencia.md` | Kits, agua, refugio, señales | Descargar + validar |
| `flora-fauna.md` | Riesgos biológicos y toxicidad | Auditar conector + asignar revisor |
| `territorio-medio-natural.md` | Puntos de agua y riesgos naturales | Crear capa geoespacial |
| **Nueva** `clima-meteorologia.md` | Umbrales de riesgo meteorológico | Crear ficha + fuentes AEMET |

### 🟡 P1 — Importantes (segunda fase)

| Ficha / Acción | Razón |
|---|---|
| `radio-comunicaciones.md` | Base del proyecto (Meshtastic/LoRa) |
| `municipios-geografia.md` | Contexto geográfico + triangulación visual |
| `astronomia-mareas-orientacion.md` | Orientación offline |
| `apoyo-psicosocial.md` | Crisis post-emergencia |
| `transporte-publico.md` | Movilidad |

### 🟢 P2 — Complementarios (tercera fase)

`agricultura-ganaderia.md`, `legislacion-derechos.md`, `fiestas-tradiciones.md`.

### 🔵 P3 — Informativos (cuarta fase)

`historia-patrimonio.md`.

> Los plazos calendario se fijan **solo cuando haya revisor asignado**; antes, las fichas permanecen en `propuesta`/`en_validacion`.

---

## 10. Presupuesto de Recursos (restricción RPi)

- **Hardware mínimo:** Raspberry Pi 4, 4 GB (no negociable). **Despliegue actual:** RPi 5, 8 GB (margen para modelos mayores).
- **Límite de respuesta duro:** **≤ 230 bytes UTF-8 × 3 mensajes** (no 250 caracteres). Objetivo: 1 mensaje.
- **Modelo:** configurable por `LLM_MODEL_PATH`. Actual `Qwen2.5-3B-Instruct Q4_K_M`. Evaluar `Qwen2.5-7B-Instruct Q4_K_M` (~4.5 GB) en la RPi5/8 GB.
- **Fragmentos objetivo:**
  - Primeros auxilios: 80–160 fragmentos (< 500 KiB).
  - Flora/fauna: 100–250 fichas de riesgo (tablas compactas, no copiar todas las ocurrencias).
  - Directorios: cientos/pocos miles de filas (< 10 MiB), sin embeddings.
  - Astronomía/mareas: tablas anuales de pocos MiB.
- **Principio:** los PDFs/datasets originales **quedan en el actualizador**; a la Pi solo llegan fragmentos aprobados, metadatos y tablas compactas.

---

## 11. Reglas de Oro del RAG

1. **✅ Válido:** solo fuentes oficiales/científicas, con validación humana para crítico, coordenadas WGS84 verificables.
2. **❌ Prohibido:** procedimientos médicos no validados, comestibilidad sin experto, contactos no verificados, información caducada, y "paja" genérica sin acción concreta.
3. **📏 Técnico:** respetar 230 bytes × 3, formato JSON, modelo por env, RAM ≤ presupuesto.
4. **🔄 Actualización:** dinámicas (directorios) mensual; estáticas (manuales) anual o por nueva edición; conservar versión anterior en `data/processed/archive/`.
5. **🔒 Licencia:** sin licencia acreditada → `pendiente de verificar` → fuera de publicación.

---

## 12. Herramientas y Scripts Reales

| Script | Propósito | Ubicación |
|---|---|---|
| `actualizar_fuente.py` | Descarga/procesamiento/ingesta de fuentes. | `scripts/` |
| `seed_corpus.py` | Carga del corpus semilla (a purgar de "paja"). | `scripts/` |
| `eval_rag.py` | Evaluación de recuperación RAG. | `scripts/` |
| `test_e2e.py` | Pruebas de inferencia con el LLM. | `scripts/` |
| `review.py` | Checkpoint humano de contenido sensible. | `scripts/` |
| `migrate.py` | Migraciones SQL idempotentes. | `scripts/` |
| `exportar_conversaciones.py` | Exportación de conversaciones. | `scripts/` |
| `backup.sh` / `healthcheck.sh` | Respaldo y salud operativa. | `scripts/` |

> ⚠️ Los scripts `validar_rag.py` y `cargar_rag.py` mencionados en versiones previas de este plan **no existen**. La validación automática debe integrarse en `actualizar_fuente.py` o crearse explícitamente.

---

## 13. Ejemplo de Ficha (alineado con la plantilla real)

```markdown
# Ficha de planificación: primeros auxilios y problemas de salud comunes

[← Volver al índice](README.md)

> **Estado:** `en_validacion`
> **Prioridad:** P0
> **Destino:** RAG vectorial + contactos estructurados
> **Origen en `valorar.md`:** líneas 30-32, 40 y 80

## 1. Objetivo y límites
... [alcance + prohibiciones explícitas] ...

## 2. Registro de fuentes
### `ERC-2025` — Guías europeas de resucitación
- **Organismo / URL / Qué obtener / Formato / Fiabilidad / Licencia / Cadencia**

## 3. Bloques y mapeo
| Bloque | Fuente preferente | Salida normalizada | Subcategoría | Revisión |

## 4. Auditoría del conector existente
... [bloqueos de trazabilidad] ...

## 5. Instantáneas
... [estructura data/raw/...] ...

## 6. Calidad, presupuesto y actualización
... [validaciones, pruebas, objetivo de fragmentos] ...

## 7. Pendientes para aprobar
- [ ] Checklist por sección (atómico, no genérico)
```

---

## 14. Métricas de Éxito (Definition of Done)

Una ficha se considera **completa y publicable** cuando:

- [ ] Tiene revisor real identificado (nombre/rol) y evidencia de revisión con fecha y versión.
- [ ] Cada fragmento/fila conserva `fuente_url`, `fecha_extraccion`, `nivel_confianza`, `licencia` y `hash_contenido`.
- [ ] El contenido crítico pasa el *checkpoint humano* (no se publica desde scraping sin revisión).
- [ ] Las respuestas del LLM caben en ≤ 230 bytes UTF-8 × 3 y **no** contienen alucinaciones ni "paja".
- [ ] No queda ningún conector heredado reindexando contenido sin auditar.

---

## 15. Referencias

- [`AGENTS.md`](../AGENTS.md) — guía general del proyecto.
- [`docs/rag/README.md`](../rag/README.md) — metodología y registro maestro de fichas.
- [`docs/rag/catalogo-adquisicion.md`](../rag/catalogo-adquisicion.md) — trazabilidad de `valorar.md`.
- [`docs/rag/PLANTILLA_FUENTE.md`](../rag/PLANTILLA_FUENTE.md) — plantilla obligatoria de ficha.
- [`docs/info/05-contratos-datos.md`](../info/05-contratos-datos.md) — formato de fragmento y esquema relacional.
- [`docs/info/01-vision-requisitos.md`](../info/01-vision-requisitos.md) — límites duros y requisitos.
- [`data/info/fuentes_actuales.md`](../../data/info/fuentes_actuales.md) — diagnóstico de conectores heredados.
- [`data/info/valorar.md`](../../data/info/valorar.md) — cuaderno de trabajo del usuario (entrada).
- [`docs/planning/auditoria.md`](./auditoria.md) — análisis de fallos del asistente.

---

## 16. Historial de Versiones

| Fecha | Autor | Cambio |
|---|---|---|
| 2026-08-28 | Mistral Vibe | Creación inicial basada en `estado.md` + AGENTS.md. |
| 2026-08-28 | Agente Zed | **Reconciliación integral** con el estado real: nomenclatura real de 16+3 fichas, corrección de límites (230 bytes × 3), hardware (RPi4 min / RPi5 actual), modelo configurable, scripts reales; añadida la categoría de riesgos biológicos (`flora-fauna`), ficha `directorios-emergencia`, nueva ficha `clima-meteorologia.md`, matriz de fuentes con bloqueos legales y huecos críticos de supervivencia. |
| 2026-08-28 | Agente Zed | **Lote de adquisición/normalización**: T16 (CTAN 367 paradas), T7 (Renfe 30 paradas), T15 (purga CSV IA), T8 (RAIF Cádiz 28 548 registros), T4 (conectores→CSV), T18 (geocodificación transporte), OCR español (montaña + DGPCE + peces), protección civil (7 fragmentos). Staging: **2240 pendientes**. |
