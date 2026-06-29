# Módulo 06 · Fuentes de datos y scraping

## Resumen

Implementa un **conector por fuente** bajo `src/updater/sources/`, siguiendo la
interfaz `Source` del módulo 05. Cada conector sabe adquirir (API o scraping de
PDF), respetar la licencia, acotar a la provincia (`BBOX`/códigos) y producir
fragmentos normalizados. Se prioriza por **riesgo y automatización**: primero lo
seguro y 100% por API (geografía), al final lo sensible (primeros auxilios), que
siempre pasa por checkpoint humano. Las fuentes y su clasificación parten del
análisis preliminar adjunto.

Dependencias: 05. Habilita: Hito C.

## Clasificación de fuentes (del análisis preliminar)

| Categoría | Fuentes | Método | Riesgo | Validación |
|-----------|---------|--------|--------|------------|
| Geografía/playas/accesos | OpenStreetMap/Overpass, IGN, AEMET | API | Bajo | Automatizable |
| Fauna/flora peligrosa | GBIF, MITECO, Wikidata/Wikipedia, fauna marina local | API | Medio | Validar lo tóxico/peligroso |
| Supervivencia | Manuales oficiales con licencia abierta | Mixto/PDF | Medio | Revisar fuente por fuente |
| Primeros auxilios | Cruz Roja, ERC, OMS, 112/Protección Civil, SEMICYUC | PDF/scraping puntual | **Alto** | **Checkpoint humano obligatorio** |

## Fase 1 — Geografía (riesgo bajo, primero)

- **Overpass/OSM**: playas, accesos, caminos, faros, fuentes de agua, refugios,
  hospitales/centros de salud dentro del `BBOX`. Normalizar a fragmentos de
  orientación/geografía.
- **IGN**: cartografía/topónimos oficiales para referencias de orientación.
- **AEMET (API, requiere `AEMET_API_KEY`)**: contexto climático estacional de la
  zona (no predicción en tiempo real; el sistema es offline).
- Empezar aquí permite validar todo el pipeline con datos sin riesgo.

## Fase 2 — Fauna y flora (riesgo medio)

- **GBIF (API)**: biodiversidad geolocalizada filtrada por provincia; fichas de
  especies presentes.
- **MITECO**: inventario de especies, indicadores de peligrosidad.
- **Wikidata/Wikipedia (API)**: descripciones generales; revisar calidad.
- **Fauna marina local** (medusas y especies costeras de Cádiz) si se
  identifican fuentes fiables.
- **Toda especie marcada tóxica/peligrosa → checkpoint humano** antes de indexar.

## Fase 3 — Supervivencia (mixto)

- Manuales de organismos oficiales (protección civil, ejércitos) **con licencia
  abierta** para reutilización. Evitar foros/blogs como fuente primaria.
- Extracción de PDF → fragmentos accionables (agua, refugio, hipotermia, golpe
  de calor, señalización).

## Fase 4 — Primeros auxilios (riesgo alto, último)

- **Cruz Roja, ERC, OMS, 112/Protección Civil, SEMICYUC**: scraping puntual de
  PDF/guías oficiales.
- **No generar contenido médico con el LLM ni indexar scraping no verificado.**
- **Checkpoint humano obligatorio** sobre cada fragmento; `nivel_confianza:alta`
  solo tras validación.
- Asociar siempre el aviso "Info orientativa. Llama al 112." en respuestas.

## Fase 5 — Utilidades comunes de adquisición

- Cliente HTTP con `User-Agent`, rate limiting y reintentos (reutilizable).
- Extractor de PDF a texto (limpieza, segmentación) reutilizable.
- Caché local de descargas para no repetir peticiones.
- Registro de licencia y fecha por fuente (tabla `fuentes`).

## Fase 6 — Catálogo y mantenimiento

- Documentar por fuente: endpoint/URL, licencia, frecuencia de actualización,
  campos usados, política de validación.
- Marcar qué fuentes son por API directa vs. scraping puntual de PDF (pipeline
  pendiente del análisis preliminar).

## Verificación del módulo

- Cada conector produce fragmentos válidos que pasan la normalización.
- Las fuentes sensibles **no se indexan sin validación**.
- Acotamiento por provincia funciona (cambiar `BBOX`/`PROVINCIA` cambia datos).
- Licencias registradas para cada fuente.

## Checklist

> Leyenda de estado (autogenerada en la fase de implementación): [x] = terminado en código y verificado en sandbox · [ ] = pendiente de ejecutar en la Raspberry Pi o con BD/red en vivo (compilar llama.cpp en ARM, descargar modelo, levantar PostgreSQL, pruebas de integración).


- [x] Fase 1: conector Overpass/OSM (geografía/accesos).
- [ ] Fase 1: conector IGN (topónimos/cartografía).
- [ ] Fase 1: conector AEMET (clima estacional).
- [x] Fase 2: conector GBIF (biodiversidad por provincia).
- [ ] Fase 2: conector MITECO (peligrosidad de especies).
- [x] Fase 2: conector Wikidata/Wikipedia (descripciones).
- [ ] Fase 2: fauna marina local evaluada/integrada.
- [x] Fase 2: especies peligrosas enrutadas a checkpoint.
- [ ] Fase 3: manuales de supervivencia con licencia abierta (PDF→fragmentos).
- [ ] Fase 4: fuentes de primeros auxilios con checkpoint obligatorio.
- [ ] Fase 4: aviso médico asociado.
- [x] Fase 5: cliente HTTP común (UA, rate limit, reintentos).
- [ ] Fase 5: extractor de PDF reutilizable y caché de descargas.
- [x] Fase 6: catálogo de fuentes con licencia y frecuencia.
- [ ] Verificación: acotamiento por provincia y bloqueo sin validación.
