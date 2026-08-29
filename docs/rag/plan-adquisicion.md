# Plan de adquisición y descarga de fuentes

[← Volver al índice](README.md)

> **Fecha:** 2026-08-28
> **Estado:** operativo — fase de descarga priorizada por dominio P0.
> **Compañero de:** [`auditoria-fuentes.md`](auditoria-fuentes.md) (verificación de URLs) y [`catalogo-adquisicion.md`](catalogo-adquisicion.md) (trazabilidad de `valorar.md`).

---

## 1. Decisión de método

La descarga **no** se hace "todo a granel de una vez". Se aplica un pipeline por fuente, porque cada fuente tiene un modo de obtención y un estado legal distinto:

| Clase | Significado | Tratamiento |
|---|---|---|
| **D (descarga directa)** | PDF/CSV/archivo accesible con GET | Descargar a `data/raw/downloads/<id>/<AAAA-MM-DD>/` + `MANIFEST.json` |
| **A (API con consulta)** | Requiere construir una query (SPARQL, WFS, REST, GTFS) | Documentar la consulta exacta y guardar la respuesta como snapshot |
| **P (portal de descubrimiento)** | URL de catálogo; el recurso real hay que localizarlo | Resolver el recurso concreto antes de descargar |
| **B (bloqueada por licencia)** | Prohibida la redistribución/indexación o publicación comercial | **No descargar para indexar**; registrar el bloqueo y buscar alternativa |

**Regla de oro:** una URL pública no equivale a licencia abierta. Lo marcado `pendiente de verificar` se descarga solo a `data/raw/` como evidencia de trabajo, pero **no se procesa ni se indexa** hasta confirmar licencia y, si es contenido crítico, validación humana.

---

## 2. Orden de ejecución (por prioridad)

1. **P0** — primeros auxilios, toxicología, protección civil, agua, directorios, clima, flora/fauna peligrosa.
2. **P1** — territorio, transporte, radio, astronomía/mareas, apoyo psicosocial.
3. **P2** — legislación acotada, agricultura/ganadería, festivos.
4. **P3** — historia, patrimonio.

Dentro de cada prioridad, primero las **descargas directas (D)** y luego las **APIs (A)**, dejando los **portales (P)** y **bloqueos (B)** para resolver al final.

---

## 3. Triaje por ficha (clase de cada fuente)

> Clave: **D**=descarga directa · **A**=API · **P**=portal · **B**=bloqueada · **T**=plantilla (URL con placeholder).

### P0 — SALUD Y EMERGENCIAS

| Ficha | Fuente | Clase | Nota de obtención |
|---|---|---|---|
| primeros-auxilios | ERC-2025 (resumen ES) | D | PDF directo |
| primeros-auxilios | INGESA-PA | D | PDF directo |
| primeros-auxilios | INGESA-URG | D | PDF directo |
| primeros-auxilios | Cruz Roja (atragantamiento) | D | HTML/PDF por página |
| primeros-auxilios | SAS-CIUDADANIA | P | Buscar ficha por tema |
| toxicologia | SIT (mjusticia) | D | HTML; fijar teléfono |
| toxicologia | PNSD | D | HTML + dosieres PDF |
| toxicologia | INGESA-URG | D | PDF directo |
| toxicologia | AEMPS | P | Buscar prospecto/ficha |
| toxicologia | EMCDDA/EUDA | D | HTML/PDF |
| apoyo-psicosocial | SANIDAD-CATASTROFES | D | PDF directo |
| apoyo-psicosocial | SANIDAD-AUTOAYUDA | D | HTML |
| apoyo-psicosocial | DGPCE-PSICOSOCIAL | D | HTML/PDF |
| apoyo-psicosocial | Cruz Roja | P | Buscar material |
| apoyo-psicosocial | OMS-PFA | D | PDF guía |

### P0 — PROTECCIÓN CIVIL Y AGUA

| Ficha | Fuente | Clase | Nota de obtención |
|---|---|---|---|
| proteccion-civil | DGPCE (inundaciones/incendios/sismo/autoprotección) | D | 4 PDFs directos |
| proteccion-civil | ANDALUCIA-112 | D | HTML |
| proteccion-civil | GC-MONTANA | D | HTML |
| proteccion-civil | POLICIA-CONSEJOS | P | Catálogo; elegir página |
| proteccion-civil | DGT-METEO | P | Buscar sección |
| preparacion-supervivencia | DGPCE-AUTOPROTECCION | D | PDF directo |
| preparacion-supervivencia | SANIDAD-AGUA (RD 3/2023) | D | PDF directo |
| preparacion-supervivencia | SANIDAD-AGUA (FAQ inundaciones) | D | HTML |
| preparacion-supervivencia | DGT-V16 | D | HTML |
| preparacion-supervivencia | GC-MONTANA | D | HTML |
| preparacion-supervivencia | AESAN-RESERVAS | D | HTML/PDF |

### P0/P1 — RIESGOS BIOLÓGICOS Y CLIMA

| Ficha | Fuente | Clase | Nota de obtención |
|---|---|---|---|
| flora-fauna | REDIAM-FLORA | A | WFS `GetCapabilities` → capa |
| flora-fauna | EIDOS | P | Portal/base de datos |
| flora-fauna | GBIF | A | API REST con BBOX |
| flora-fauna | JUNTA-PECES | D | HTML/PDF |
| flora-fauna | AESAN-TOXINAS | D | HTML |
| flora-fauna | AEMPS-PLANTAS | D | PDF directo |
| flora-fauna | Dioscórides-1998 | B | Traducción protegida; solo metadatos |
| clima | AEMET-OPENDATA | A | API con `api_key` (T) |
| clima | DGPCE-METEO | D | PDF/HTML |
| clima | ANDALUCIA-112 | D | HTML |
| clima | SANIDAD-CALOR | D | HTML/PDF |
| clima | DGT-METEO | P | Buscar sección |

### P0 — DIRECTORIOS

| Ficha | Fuente | Clase | Nota de obtención |
|---|---|---|---|
| directorios-emergencia | GC-DEPENDENCIAS | D | CSV directo |
| directorios-emergencia | POLICIA-DATOS | P | Catálogo; elegir conjunto |
| directorios-emergencia | SAS-CENTROS | P | Buscador; identificar recurso |
| directorios-emergencia | DIPUCADIZ-ENTIDADES | P | CKAN en revisión |
| directorios-emergencia | ORGANISMOS-DIRECTOS | P | Sedes municipales |

### P1 — RESTO DE DOMINIOS

| Ficha | Fuente | Clase | Nota de obtención |
|---|---|---|---|
| municipios-geografia | IECA-NOMENCLATOR | P | Resolver descarga |
| municipios-geografia | NGA-WFS | A | WFS `GetCapabilities` |
| municipios-geografia | DERA-LIMITES | A | WFS/GPKG |
| municipios-geografia | IGN-CNIG | P | Centro de descargas |
| municipios-geografia | INE-POBLACION | D | Tablas CSV |
| territorio | DERA | A | WFS/GPKG |
| territorio | REDIAM-SENDEROS | A | WFS |
| territorio | REDIAM-EENNPP | A | WFS |
| territorio | DIPUCADIZ-DATOS | P | CKAN en revisión |
| territorio | JUNTA-SAIH | D | HTML |
| transporte | RENFE-GTFS | D | ZIP GTFS |
| transporte | CTAN-GTFS | A | API/GTFS |
| transporte | OPERADORES-LOCALES | P | Catálogo |
| transporte | ADIF-ESTACIONES | A | IDEADIF (WFS/IDE) |
| transporte | PUERTOS-BAHIA | P | Portal APBC |
| radio | MESHTASTIC-OFFICIAL | D | Markdown versionado |
| radio | WINLINK | D | HTML/manual |
| radio | VARAC-VARA | D | HTML/PDF |
| radio | PINPOINT-APRS | D | HTML/PDF |
| radio | BOE-RADIO | D | HTML/XML |
| radio | REMER-VADEMECUM | B | Ya descargado; inventariar capítulos |
| radio | UIT-HET | B | Derechos reservados |
| astronomia | ROA-EFEMERIDES | P | Formulario/HTML |
| astronomia | IGN-ASTRONOMIA | D | PDF/publicación |
| astronomia | ROA-ALMANAQUE | B | Posible publicación comercial |
| astronomia | PDE-MAREAS | B | Prohibida redistribución |
| astronomia | IHM | P | Publicaciones/cartas |

### P2/P3 — COMPLEMENTARIOS

| Ficha | Fuente | Clase | Nota de obtención |
|---|---|---|---|
| legislacion | BOE (API consolidada) | A | API XML |
| legislacion | BOE-CONSTITUCION | D | XML/PDF |
| legislacion | BOE-CODIGO-CIVIL | P | Índice → normas |
| legislacion | EURLEX-CARTA | D | HTML/XML |
| legislacion | BOP-CADIZ | P | Disposiciones concretas |
| agricultura | INE-CENSO-AGRARIO | D | Tablas |
| agricultura | JUNTA-SECTOR-AGRARIO | D | PDF |
| agricultura | RAIF | D | ZIP XML |
| agricultura | IFAPA | P | Selección manual |
| agricultura | JUNTA-GANADERIA | P | Portal |
| fiestas | JUNTA-FESTIVOS | D | HTML/BOJA |
| fiestas | BOP-FESTIVOS-LOCALES | P | Resolución anual |
| fiestas | CADIZ-TURISMO | D | HTML |
| fiestas | AYUNTAMIENTOS | P | Agendas |
| fiestas | IAPH-ETNOLOGIA | A | API |
| historia | IAPH-OPEN-DATA | A | API |
| historia | JUNTA-PATRIMONIO | P | Portal |
| historia | ARCHIVO-MUSEOS | P | Portal |
| historia | AYUNTAMIENTOS-DIPUTACION | P | CKAN en revisión |
| historia | MCU-BIC | P | Registro BIC |

### Conectores transversales

| Ficha | Fuente | Clase | Nota de obtención |
|---|---|---|---|
| overpass-osm | Overpass API | A | POST con consulta QL |
| overpass-osm | DIPUCADIZ / SAS / DERA / IGN | P/A | contraste |
| wikidata | Wikidata SPARQL | A | query JSON |
| wikidata | IGN / IAPH / Puertos / SAS | P/A | contraste |
| gbif | GBIF API | A | REST con BBOX |
| gbif | REDIAM / EIDOS / JUNTA / IUCN | A/P | contraste |

---

## 4. Estructura de descarga en `data/raw/downloads/`

```
data/raw/downloads/<identificador>/<AAAA-MM-DD>/
├── <fuente>/<archivo_original>.<ext>
├── LICENSE.txt          # si hay condiciones de licencia
└── MANIFEST.json        # hash SHA-256, fuente, fecha UTC, cabeceras, licencia, versión
```

Los archivos originales **no se editan**. El `MANIFEST.json` registra, por archivo: `url`, `fecha_descarga` (UTC), `sha256`, `licencia`, `content_type`, `size_bytes` y `notas`.

---

## 5. Progreso de descarga

| Fase | Estado |
|---|---|
| Descarga P0 (salud, protección civil, agua, directorios, clima, flora) | ✅ Completada |
| Descarga P1/P2 (descargas directas) | ✅ Completada — 12 descargas adicionales |
| Descarga P3 (historia) | ⏳ Pendiente (solo API IAPH, no descarga directa) |
| Resolución de portales (P), APIs (A) y bloqueos (B) | ⏳ Pendiente — documentado en §7 |

## 6. Hallazgos de adquisición

- **`guardia_civil_dependencias.csv`**: 2.446 líneas de **ámbito nacional**, codificación **ISO-8859** y delimitador `;`. Al procesar: transcodificar a UTF-8 y filtrar por `PROVINCIA == "CÁDIZ"`.
- **`content_type` poco fiable**: algunos servidores públicos sirven CSV/PDF como `text/html`; el `file` y la inspección del contenido prevalecen sobre la cabecera.
- **`euda.europa.eu` (EUDA)**: devuelve 403 a descarga automática (anti-bot). Es fuente de contraste; resolver por navegador o usar perfiles por sustancia vía URL específica.
- **`eur-lex.europa.eu` (EUR-Lex)**: devuelve **HTTP 202 con 0 bytes** (anti-bot). **Restricción:** usar espejo oficial en BOE (`DOUE-Z-2012-70018`) para la Carta de Derechos Fundamentales, o descarga manual.
- **Navegación dinámica (DGPCE gestión de riesgos, 112 Andalucía)**: no exponen enlaces PDF estáticos en el HTML plano. Usar URLs directas ya conocidas, no hacer scraping del catálogo.
- **Portales que requieren subpáginas (PNSD, AESAN)**: la página descargada es el índice; el contenido real está en una URL por sustancia/toxina.
- **PDFs enlazados desde portadas (Junta peces, Guardia Civil montaña)**: la URL de la ficha era una portada; el PDF real se descubre por enlace interno.
- **GTFS Renfe**: ZIP de **313 MB descomprimido**, `stop_times.txt` de 287 MB, **todo España** (no solo Cádiz). Al procesar filtrar por núcleo de Cádiz y **no descomprimir en la Pi**.
- **RAIF**: ZIP con un XML por provincia (2.2 GB descomprimido). Solo interesa `*_Cadiz_*.xml`. **No descomprimir todo**; extraer selectivamente.
- **IECA nomenclátor**: la página no expone enlaces de descarga estáticos (descarga dinámica). Resolver recurso concreto o usar el WFS DERA/NGA.
- **REDIAM WFS**: capas confirmadas `senderos` y `equipamientos_uso_publico` vía `GetCapabilities`.

> El detalle completo por fuente está en [`analisis-lote.md`](analisis-lote.md).

---

## 7. Fuentes restantes por clase (no descarga directa)

### A — API con consulta (requieren conector/query, no un simple GET)

| Ficha | Fuente | Estado actual |
|---|---|---|
| municipios-geografia | DERA-LIMITES (WFS) | ✅ Resuelto: capa `g13_01_TerminoMunicipal`, filtro `provincia='Cádiz'` → 45 municipios |
| municipios-geografia | NGA-WFS | ✅ Resuelto: capa `Entidad` (topónimos) |
| territorio | DERA (WFS/GPKG) | ✅ Resuelto: capas de límites identificadas |
| flora-fauna | REDIAM-FLORA (WFS) | ✅ Resuelto: capa `ms:localizacion_flora`, campos `nombre_cie`, `coor_x/y`, `fuente` |
| flora-fauna | GBIF (REST) | Conector existente `gbif.py`; fijar snapshot CSV |
| transporte | CTAN-GTFS (API) | ✅ Resuelto: endpoint `https://api.ctan.es/v1/datos/UNIFICADO/gtfs.zip` (GTFS unificado, 9 consorcios). Interesan CMTBC (Bahía de Cádiz) y CTMCG (Campo de Gibraltar). |
| transporte | ADIF-ESTACIONES (IDEADIF) | ⚠️ Bloqueado: SPA con datos por JS + anti-bot 403. Requiere ejecutar el JS o usar fuente alternativa. |
| legislacion | BOE API consolidada (XML) | API documentada; construir consulta por norma |
| fiestas | IAPH-ETNOLOGIA (API) | API Guía Digital |
| historia | IAPH-OPEN-DATA (API) | API Guía Digital |
| overpass-osm | Overpass API (POST QL) | Conector existente `overpass.py`; fijar CSV |
| wikidata | SPARQL | Conector existente `wikidata.py`; fijar CSV |
| gbif | GBIF REST | Conector existente `gbif.py`; fijar CSV |

### Consultas WFS reutilizables (DERA y REDIAM)

```bash
# GetCapabilities (descubrir capas)
curl -sL "https://www.ideandalucia.es/services/DERA_g13_limites_administrativos/wfs?service=WFS&version=2.0.0&request=GetCapabilities"

# Términos municipales de Cádiz (45 registros)
curl -sL "https://www.ideandalucia.es/services/DERA_g13_limites_administrativos/wfs?service=WFS&version=2.0.0&request=GetFeature&typeNames=DERA_g13_limites_administrativos:g13_01_TerminoMunicipal&cql_filter=provincia='C%C3%A1diz'&count=50"

# Nomenclátor geográfico (topónimos) — capa Entidad
curl -sL "https://www.ideandalucia.es/wfs-nga/services?service=WFS&version=1.1.0&request=GetCapabilities"

# Flora andaluza (REDIAM)
curl -sL "https://www.juntadeandalucia.es/medioambiente/mapwms/REDIAM_WFS_localizacion_flora_andaluza?service=WFS&version=2.0.0&request=GetCapabilities"
```

Campos útiles DERA: `id_dera`, `cod_mun`, `nombre`, `provincia`, `geom`. REDIAM flora: `nombre_cie`, `coor_x`, `coor_y`, `fuente`.

### B — Bloqueadas por licencia (no indexar sin confirmación)

| Ficha | Fuente | Motivo |
|---|---|---|
| flora-fauna | Dioscórides-1998 | Traducción protegida; solo metadatos |
| radio | UIT-HET 2005 | Derechos reservados |
| radio | REMER-Vademécum 2017 | Ya descargado; inventariar capítulos antes de usar |
| astronomia | ROA-Almanaque | Posible publicación comercial |
| astronomia | PDE-MAREAS (Puertos del Estado) | Prohibida redistribución (manual 2021) |

### P — Portales de descubrimiento (resolver recurso concreto)

| Ficha | Fuente | Nota |
|---|---|---|
| primeros-auxilios | SAS-CIUDADANIA | Ficha por tema (resfriado, fiebre…) |
| toxicologia | AEMPS / EMCDDA | Perfil por sustancia |
| proteccion-civil | POLICIA-CONSEJOS / DGT | Elegir página concreta |
| directorios | POLICIA / SAS-CENTROS / DIPUCADIZ / ORGANISMOS | Catálogos; recurso concreto |
| municipios | IECA-NOMENCLATOR / IGN-CNIG | Descarga dinámica |
| historia | ARCHIVO-MUSEOS / MCU-BIC / AYUNTAMIENTOS | Portal |
| agricultura | IFAPA / JUNTA-GANADERIA | Selección manual |
| fiestas | BOP-LOCALES / AYUNTAMIENTOS | Resolución anual |

[← Volver al índice](README.md)

[← Volver al índice](README.md)
