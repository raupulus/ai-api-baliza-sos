# Dudas y pendientes no resueltos — RAG

> **Fecha:** 2026-08-29 · **Propósito:** solo lo **sin resolver**. Todo lo resuelto vive ya en su ficha de `docs/rag/` (no aquí).

---

## Bloqueos externos (fuera de mi control)

| # | Fuente | URL | Estado | Posible vía |
|---|---|---|---|---|
| T22 | Diputación de Cádiz (RTOD) | https://apirtod.dipucadiz.es/api/collections.json | ⚠️ **En mantenimiento** (listado OK, datos devuelven 500) | Reintentar en horas/días; si sigue, cubrir con Overpass (ya hecho). |
| T3b | REDIAM — flora andaluza (WFS) | https://www.juntadeandalucia.es/medioambiente/mapwms/REDIAM_WFS_localizacion_flora_andaluza?service=WFS&version=2.0.0&request=GetCapabilities | GetCapabilities 200, pero **BBOX → vacío** y **CQL → 403**. `outputFormat=geojson` **SÍ funciona** (trae `nombre_cie`, `coor_x`/`coor_y` UTM EPSG:3042) | Descargar completo paginando (`maxFeatures=5000`) y filtrar en cliente por `coor_x`/`coor_y`. Ojo: 403 si se martillea → espaciar peticiones. |
| B3 | EUDA (antes EMCDDA) | https://www.euda.europa.eu/publications_en | Home → 403, pero `/publications_en` accesible | Usar la URL de publicaciones; descartar si no aporta nada nuevo sobre PNSD (ya cubierto). |

---

> El resto de tareas y dudas de la planificación quedaron resueltas y documentadas en su ficha correspondiente de `docs/rag/`: licencias en `lecciones-adquisicion.md` §5, procesionaria en `flora-fauna.md`, 061/091/016 en `directorios-emergencia.md`, ADIF en `transporte-publico.md`, etc.
