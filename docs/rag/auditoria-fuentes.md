# Auditoría de fuentes — checklist y verificación de URLs

[← Volver al índice](README.md)

> **Fecha de última verificación:** 2026-08-28
> **Alcance:** las 103 URLs únicas citadas en las fichas de `docs/rag/`.
> **Herramienta:** `scripts/auditar_urls.py` (extrae, desduplica y comprueba el estado HTTP).

---

## 1. Resumen ejecutivo

| Métrica | Valor |
|---|---:|
| URLs únicas comprobadas | 103 |
| OK (HTTP < 400) | 87 (85 %) |
| Fallos reales corregidos | 5 |
| Endpoints en revisión | 1 (CKAN de Diputación) |
| Falsos positivos | 10 |

**Clasificación de los 16 resultados no-OK:**

| Categoría | Casos | Conclusión |
|---|---|---|
| Fallo real (404 / DNS) | 5 | Corregido con URL alternativa oficial |
| Endpoint CKAN sin responder | 1 | Marcado "en revisión"; portal raíz operativo |
| URL plantilla con placeholder (`<id>`, `...`) | 4 | No es fallo; requiere parámetro real |
| Endpoint que exige POST (Overpass) | 1 | No es fallo; GET devuelve 406 |
| Certificado SSL de cadena incompleta (sandbox) | 3 | Operativo en navegador; `curl -k` devuelve 200 |
| Bloqueo anti-bot (403) | 2 | La API o portal alternativo sí responde |

---

## 2. Fallos reales corregidos

| Ficha | URL rota | Causa | Corrección aplicada |
|---|---|---|---|
| `toxicologia-sustancias.md` | SIT (mjusticia) | 404 | Nueva URL institucional + teléfono 24 h (91 562 04 20) |
| `clima-meteorologia.md` | Sanidad plan calor | 404 | Ruta nueva `calorExtremo/home.htm` |
| `preparacion-supervivencia.md` | AESAN manipulación alimentos | 404 | Ruta nueva `seguridad-alimentaria/higiene-alimentos/…` |
| `transporte-publico.md` | `data.adif.es` | DNS roto | Sustituida por `ideadif.adif.es` + `adif.es/viajeros` |
| `territorio-medio-natural.md` | `chguadaletebarbate.es` | DNS roto | Sustituida por SAIH Junta de Andalucía (cuencas Guadalete-Barbate) |

---

## 3. Endpoints en revisión

| Endpoint | Estado | Fichas afectadas | Acción pendiente |
|---|---|---|---|
| `apidatosabiertos.dipucadiz.es/api/3/action/package_search` | 404 recurrente | `directorios-emergencia`, `historia-patrimonio`, `overpass-osm`, `territorio-medio-natural`, `transporte-publico` | Verificar ruta CKAN correcta o usar portal `datosabiertos.dipucadiz.es/` |

---

## 4. Checklist por ficha

> Leyenda: ✅ verificado OK · 🔧 con incidencias corregidas · ⏳ pendiente de re-verificación.

| Ficha | Fuentes | Estado | Incidencias |
|---|---:|---|---|
| `primeros-auxilios.md` | 5 | ✅ | — |
| `toxicologia-sustancias.md` | 5 | 🔧 | SIT corregida |
| `apoyo-psicosocial.md` | 5 | ✅ | — |
| `proteccion-civil-autoproteccion.md` | 5 | ✅ | — |
| `preparacion-supervivencia.md` | 5 | 🔧 | AESAN corregida |
| `legislacion-derechos.md` | 5 | ✅ | — |
| `transporte-publico.md` | 5 | 🔧 | ADIF corregida |
| `flora-fauna.md` | 6 | ✅ | — |
| `territorio-medio-natural.md` | 5 | 🔧 | Hidrografía corregida |
| `municipios-geografia.md` | 5 | ✅ | — |
| `historia-patrimonio.md` | 5 | 🔧 | CKAN Diputación en revisión |
| `fiestas-tradiciones.md` | 5 | ✅ | — |
| `directorios-emergencia.md` | 5 | 🔧 | CKAN Diputación en revisión |
| `agricultura-ganaderia.md` | 5 | ✅ | — |
| `radio-comunicaciones.md` | 7 | ✅ | — |
| `astronomia-mareas-orientacion.md` | 5 | ✅ | — |
| `clima-meteorologia.md` | 5 | 🔧 | Sanidad calor corregida |
| `overpass-osm.md` | 5 | 🔧 | CKAN Diputación en revisión |
| `wikidata.md` | 5 | ✅ | — |
| `gbif.md` | 5 | ✅ | — |

---

## 5. Falsos positivos documentados (no requieren acción)

- **URLs plantilla** con `<id>` o `...` (AEMET API, `apirtod.dipucadiz.es`, Wikidata SPARQL): son plantillas, no enlaces finales.
- **Overpass `/api/interpreter`**: devuelve 406 a GET porque exige POST con la consulta QL.
- **Certificados SSL** (`bopcadiz.es`, `cultura.gob.es`, `dipucadiz.es`): cadena incompleta en el sandbox; operativos en navegador.
- **Bloqueo anti-bot 403** (`gbif.org`, `adif.es`): la API `api.gbif.org` y el portal `ideadif.adif.es` responden correctamente.

---

## 6. Cómo re-ejecutar la verificación

```bash
python3 scripts/auditar_urls.py
```

El script imprime estado por URL y un resumen de fallos con la referencia `ficha:línea`. Añadir el resultado a la tabla §4 y actualizar la fecha del encabezado.

---

[← Volver al índice](README.md)
