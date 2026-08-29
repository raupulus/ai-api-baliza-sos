# Catálogo maestro de adquisición del conocimiento

[← Volver al índice de fuentes RAG](README.md)

> **Estado:** planificación, sin implementación asociada.
> **Fecha de evaluación:** 2026-08-27.
> **Entrada analizada:** [`data/info/valorar.md`](../../data/info/valorar.md).

## 1. Decisión de organización

El listado se divide por **dominio de información y ciclo de actualización**, no por cada URL. Una ficha puede reunir varias fuentes complementarias del mismo dominio. Se evita crear un archivo por enlace y también mezclar datos con distinta validación o cadencia.

No todo debe almacenarse como embeddings:

| Tipo | Destino propuesto | Motivo |
|---|---|---|
| Procedimientos, advertencias y explicaciones | RAG vectorial | Consulta semántica y respuesta breve. |
| Teléfonos, direcciones, horarios y fechas | PostgreSQL estructurado | Coincidencia exacta, vigencia y filtros. |
| Coordenadas, rutas, hidrografía y senderos | PostgreSQL/PostGIS o tablas compactas | Proximidad y geometría; el vector RAG no calcula distancias. |
| Mareas, ortos, ocasos y fases lunares | Tablas precalculadas por año/estación | Resultados deterministas y pequeños. |
| PDFs, GPKG y datasets originales | `data/raw/` en el equipo actualizador | Evidencia y reprocesado; no se copian íntegros a la Pi. |

## 2. Fichas propuestas

| Ficha | Cobertura | Prioridad | Destino | Estado |
|---|---|---:|---|---|
| [primeros-auxilios.md](primeros-auxilios.md) | Primeros auxilios, urgencias y dolencias comunes | P0 | Híbrido | Ficha auditada; conector heredado bloqueado |
| [toxicologia-sustancias.md](toxicologia-sustancias.md) | Drogas, intoxicaciones y toxicología | P0 | RAG | Ficha creada; sin implementación |
| [apoyo-psicosocial.md](apoyo-psicosocial.md) | Primer apoyo tras catástrofes o malas noticias | P1 | RAG | Ficha creada; sin implementación |
| [proteccion-civil-autoproteccion.md](proteccion-civil-autoproteccion.md) | Riesgos naturales, seguridad y autoprotección | P0 | RAG | Ficha creada; sin implementación |
| [preparacion-supervivencia.md](preparacion-supervivencia.md) | Kits, reservas, agua y supervivencia segura | P0/P1 | RAG | Ficha creada; sin implementación |
| [legislacion-derechos.md](legislacion-derechos.md) | Constitución, derechos y corpus legal acotado | P2 | Híbrido | Ficha creada; sin implementación |
| [transporte-publico.md](transporte-publico.md) | Tren, autobús y transporte marítimo | P1 | Estructurado | Ficha creada; sin implementación |
| [flora-fauna.md](flora-fauna.md) | Flora, fauna, peces, toxicidad y contaminación | P0/P1 | Híbrido | Ficha auditada; conector heredado bloqueado |
| [territorio-medio-natural.md](territorio-medio-natural.md) | Agua, costa, parques y senderos | P0/P1 | Geoespacial | Ficha creada; sin implementación |
| [municipios-geografia.md](municipios-geografia.md) | Municipios, núcleos, pedanías y topónimos | P1 | Geoespacial | Ficha auditada; ampliar a núcleos |
| [historia-patrimonio.md](historia-patrimonio.md) | Historia y lugares patrimoniales | P3 | Híbrido | Ficha auditada; ampliar desde IAPH |
| [fiestas-tradiciones.md](fiestas-tradiciones.md) | Festivos oficiales y eventos tradicionales | P2 | Híbrido | Ficha auditada; separar vigencia |
| [directorios-emergencia.md](directorios-emergencia.md) | Servicios, centros, direcciones y teléfonos | P0 | Estructurado | Ficha creada; sin implementación |
| [agricultura-ganaderia.md](agricultura-ganaderia.md) | Cultivos, sanidad vegetal y ganado | P2 | Híbrido | Ficha creada; sin implementación |
| [radio-comunicaciones.md](radio-comunicaciones.md) | Meshtastic, REMER, Winlink y normativa RF | P1 | RAG/estructurado | Ficha creada; sin implementación |
| [astronomia-mareas-orientacion.md](astronomia-mareas-orientacion.md) | Sol, Luna, almanaque, mareas y estrellas | P1 | Híbrido | Ficha creada; sin implementación |
| [clima-meteorologia.md](clima-meteorologia.md) | Clima, umbrales de riesgo y autoprotección meteorológica | P0/P1 | RAG + tabla | Ficha creada; sin implementación |

## 3. Trazabilidad completa de `valorar.md`

| Líneas | Elementos solicitados | Ficha de destino | Decisión |
|---:|---|---|---|
| 30-32 | Primeros auxilios básicos, graves y urgencias | `primeros-auxilios.md` | Incluir solo maniobras para población general; traqueostomía se limita al cuidado seguro de una persona con estoma existente, nunca a crear una vía aérea. |
| 33 | Leyes españolas | `legislacion-derechos.md` | No descargar todo el ordenamiento; corpus curado y versionado. |
| 34 | Rutas de tren | `transporte-publico.md` | GTFS de Renfe; tablas, no embeddings de horarios. |
| 35 | Rutas de autobús | `transporte-publico.md` | API/GTFS CTAN para Bahía de Cádiz y Campo de Gibraltar. |
| 36-37 | Flora y fauna | `flora-fauna.md` | Presencia oficial + fichas de riesgo validadas. |
| 38 | Playas, ríos, mar, afluentes y embalses | `territorio-medio-natural.md` | DERA/IGN/Diputación; geometrías filtradas por provincia. |
| 39, 46 | Guías y actuación ante desastres | `proteccion-civil-autoproteccion.md` | Guías oficiales por riesgo. |
| 40 | Guías de Cruz Roja | `primeros-auxilios.md` | Fuente complementaria; verificar licencia por documento. |
| 41 | Sustancias estupefacientes | `toxicologia-sustancias.md` | Síntomas, riesgo y primera respuesta; excluir preparación, dosis y optimización de consumo. |
| 42-43 | Supervivencia básica/avanzada | `preparacion-supervivencia.md` | Solo prácticas legales, contrastadas y de bajo riesgo. |
| 44 | Ciudades, historia y lugares relevantes | `municipios-geografia.md` + `historia-patrimonio.md` | Separar identidad territorial de narrativa histórica. |
| 45 | Festivos del año | `fiestas-tradiciones.md` | BOJA anual y correcciones; tabla con vigencia. |
| 47-48 | Alimentos de reserva y potabilización | `preparacion-supervivencia.md` | Seguridad alimentaria y agua; validación sanitaria. |
| 49, 64 | Guía oficial de Meshtastic | `radio-comunicaciones.md` | Un único bloque; documentación versionada desde repositorio oficial. |
| 50 | Vademécum REMER 2017 | `radio-comunicaciones.md` y fichas temáticas pertinentes | Fuente oficial histórica, nunca autoridad única para protocolos actuales. |
| 51-52 | Seguridad Guardia Civil y Policía | `proteccion-civil-autoproteccion.md` | Consejos oficiales y fecha de vigencia. |
| 53-54 | Peces, comestibilidad, toxinas y contaminación | `flora-fauna.md` | Identificación no basta para autorizar consumo; combinar Junta/AESAN/CSIC. |
| 55-57, 84-145 | Kits hogar, montaña, coche y mascotas | `preparacion-supervivencia.md` | Listas por escenario, normativa V16 y necesidades vulnerables/animales. |
| 58, 71 | Direcciones y teléfonos de emergencia | `directorios-emergencia.md` | Fuentes oficiales, coordenadas y control de antigüedad. El CSV generado por IA queda como borrador no confiable. |
| 59-61 | Cultivos y ganado | `agricultura-ganaderia.md` | Estadística para priorizar especies + guías técnicas/alertas. |
| 62 | Dioscórides y plantas medicinales | `flora-fauna.md` | Documento de 1998 con traducción protegida y conocimiento histórico: no indexar como recomendación médica. |
| 63 | Atención psicológica | `apoyo-psicosocial.md` | Primer apoyo y derivación, no diagnóstico ni terapia automática. |
| 65-66 | Winlink, VARA, VarAC, PinPoint y frecuencias | `radio-comunicaciones.md` | Manuales separados por producto; frecuencias siempre ligadas a país, licencia y fecha. |
| 67-69 | Derechos humanos, Código Civil y Constitución | `legislacion-derechos.md` | EUR-Lex/BOE, artículos y versiones consolidadas. |
| 70 | Manual UIT | `radio-comunicaciones.md` | Referencia profesional de 2005; derechos reservados, reutilización pendiente. |
| 72-77 | Astronomía, almanaque, mareas, Luna, Sol y estrellas | `astronomia-mareas-orientacion.md` | Sol/Luna/almanaque agrupados por ROA; mareas separadas por Puertos del Estado. |
| 78 | Pólvora y jabón | `preparacion-supervivencia.md` | Excluir fabricación de explosivos; jabón solo higiene de bajo riesgo con fuente autorizada. |
| 79 | Cerveza, whisky, ginebra e hidromiel | `preparacion-supervivencia.md` | Sin prioridad de emergencia. Excluir destilación y procedimientos peligrosos; valorar solo conservación/fermentación segura si existe necesidad futura. |
| 80 | Problemas de salud comunes | `primeros-auxilios.md` | Autocuidados, señales de alarma y derivación; no diagnóstico. |
| 81-82 | Parques naturales y senderos | `territorio-medio-natural.md` | REDIAM WFS y normativa/avisos del espacio protegido. |

## 4. Política común de fuentes

Orden de preferencia:

1. Administración competente y texto/dataset oficial vigente.
2. Organismo científico o sociedad profesional responsable.
3. Datos abiertos colaborativos como complemento, nunca sustituto silencioso.
4. Fuentes comerciales o de usuarios solo si no existe alternativa y con confianza explícitamente inferior.

Cada instantánea guardará URL, fecha UTC, hash SHA-256, cabeceras HTTP disponibles, licencia y versión. Una URL accesible no demuestra permiso de reutilización: si las condiciones no constan, la ficha queda bloqueada en `pendiente_de_verificar`.

## 5. Prioridad de ejecución futura

1. **P0:** primeros auxilios, toxicología, protección civil, clima/riesgo meteorológico, agua, directorios y riesgos biológicos.
2. **P1:** territorio, transporte, radio, astronomía/mareas y apoyo psicosocial.
3. **P2:** legislación acotada, agricultura/ganadería y festivos.
4. **P3:** historia, patrimonio y fabricación alimentaria no esencial.

## 6. Restricciones para la fase actual

Esta evaluación no crea conectores, no ingiere contenido, no modifica el esquema de base de datos y no declara ninguna validación médica o biológica. Las rutas de `data/raw/` descritas en las fichas son propuestas de almacenamiento para futuras instantáneas.
