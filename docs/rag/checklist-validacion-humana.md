# Checklist de validación humana del contenido RAG

[← Volver al índice](README.md)

> **Fecha:** 2026-08-28
> **Estado:** operativo — define la puerta única de validación antes de indexar.
> **Herramienta asociada:** `scripts/review.py` · **Módulo:** `src/updater/staging.py`.

---

## 1. Propósito y principio rector

El contenido de emergencia **puede causar daño** si es incorrecto, está obsoleto o se inventa. Por eso, **ningún fragmento sensible se indexa sin aprobación humana explícita**. Este checklist define *qué* requiere validación, *quién* la hace y *con qué criterios* se aprueba o rechaza.

**Regla de oro:** ante la duda, el fragmento **no se aprueba**. Es preferible no tener un dato a tener un dato peligroso.

---

## 2. Flujo operativo (ya implementado)

```
data/raw/downloads/            → evidencia original (no se toca)
        │ normalización
        ▼
data/staging/pendientes/       → fragmentos sensibles, JSON por hash
        │ scripts/review.py
        ├── aprobar  → data/staging/aprobados/  (con operador + fecha)
        └── rechazar → data/staging/rechazados/
        │
        ▼
python -m updater.cli --reindex-aprobados   → indexa en PostgreSQL + pgvector
```

Comandos:
```bash
python3 scripts/review.py --status      # recuento de pendientes/aprobados
python3 scripts/review.py               # revisión interactiva (a/r/s/q)
python -m updater.cli --reindex-aprobados
```

---

## 3. Matriz de sensibilidad por dominio

> **Discrepancia detectada:** el código (`src/common/models.py`) solo marca `primeros_auxilios` como sensible por categoría, más el flag `peligrosa` para especies tóxicas. Sin embargo, las fichas de `docs/rag/` declaran **más dominios** que requieren revisión humana. Esta tabla es la **autoridad**; el código debe alinearse antes de indexar en producción.

| Dominio | Requiere validación humana | Revisor competente | Flag en código (hoy) |
|---|---:|---|---|
| Primeros auxilios | ✅ Obligatoria | Médico / enfermería | ✅ sensible |
| Toxicología / sustancias | ✅ Obligatoria | Toxicólogo / farmacéutico | ⚠️ no cubierto |
| Flora/fauna peligrosa o tóxica | ✅ Obligatoria | Biólogo + sanitario | ✅ `peligrosa=True` |
| Flora/fauna no peligrosa | Recomendable | Biólogo | ⚠️ no cubierto |
| Protección civil / autoprotección | ✅ Obligatoria | Protección Civil / emergencias | ⚠️ no cubierto |
| Preparación / supervivencia (agua, kits) | ✅ Obligatoria para agua/higiene | Sanitario | ⚠️ no cubierto |
| Apoyo psicosocial | ✅ Obligatoria | Psicólogo de emergencias | ⚠️ no cubierto |
| Legislación / derechos | ✅ Obligatoria | Jurista | ⚠️ no cubierto |
| Clima / meteorología | Recomendable | Meteorólogo / Protección Civil | ⚠️ no cubierto |
| Directorios (teléfonos/direcciones) | ✅ Obligatoria (muestreo + altas) | Operador verificado | ⚠️ no cubierto |
| Geografía / municipios | Recomendable | Cartógrafo | ⚠️ no cubierto |
| Transporte (horarios) | Automática (vigencia) | — | ⚠️ no cubierto |
| Radio / comunicaciones | ✅ Obligatoria | Radioaficionado licenciado | ⚠️ no cubierto |
| Agricultura / ganadería | ✅ Obligatoria | Agrónomo / veterinario | ⚠️ no cubierto |
| Fiestas / historia | Recomendable | Documentalista | ⚠️ no cubierto |

> **Acción pendiente (código):** ampliar `CATEGORIAS_SENSIBLES` o introducir un campo `requiere_validacion` explícito en cada ficha, para que `staging.py` no dependa solo de la categoría y del flag `peligrosa`.

> **Decisiones de validación (2026-08-28, delegadas por el usuario):**
> - **D1** — `supervivencia`: el contenido actual son POIs geográficos (no sensibles). Si se añade contenido narrativo de potabilización/higiene, se marcará sensible por subcategoría (`requiere_validacion`).
> - **D2** — `directorios`: validación **1 a 1** con `review.py` (53 fragmentos, P0, manejable).

---

## 4. Checklist de aceptación (a marcar antes de aprobar)

### 4.1. Transversal (todo fragmento)

- [ ] **Fuente identificada:** `fuente` y `fuente_url` presentes y correctas.
- [ ] **Licencia verificada:** no es `pendiente_de_verificar` si el contenido va a indexarse.
- [ ] **Fecha de extracción** registrada y coherente con la descarga.
- [ ] **No es "paja":** el texto contiene una acción o dato concreto, no una generalidad vacía ("mantén la calma", "llama al 112" sin contexto).
- [ ] **Fiel a la fuente:** no parafrasea ni introduce cifras/maniobras que no estén en el documento original.
- [ ] **Ámbito correcto:** si es específico de Cádiz, tiene `provincia` y, si aplica, `municipio`.
- [ ] **Hash estable** (`hash_contenido`) presente para idempotencia.

### 4.2. Primeros auxilios y toxicología

- [ ] Secuencias (RCP, atragantamiento, hemorragias) contrastadas contra la guía vigente (ERC-2025 / INGESA / SIT).
- [ ] Sin dosis de medicamentos inventadas ni maniobras invasivas sin indicación.
- [ ] "No hacer" explícito cuando la fuente lo indica (ej. no inducir vómito, no recolocar fracturas).
- [ ] Señales de alarma y derivación al 112 presentes.
- [ ] Revisor sanitario real identificado (`validado_por` + `validado_fecha`).

### 4.3. Flora, fauna y toxicidad

- [ ] Identificación no se basa en una única característica ambigua.
- [ ] "Comestible" nunca se afirma por ausencia de toxicidad o conocimiento popular.
- [ ] Especies tóxicas/peligrosas marcadas con `peligrosa=True`.
- [ ] Tratamiento/picaduras contrastado con fuente sanitaria, no con blogs.

### 4.4. Protección civil y supervivencia

- [ ] Instrucciones distinguen **antes / durante / después**.
- [ ] Agua/higiene: métodos de potabilización con fuente sanitaria oficial (no recetas caseras).
- [ ] No incluye fabricación de explosivos, armas, destilación ni prácticas de alto riesgo.
- [ ] No presenta información precargada como alerta en tiempo real.

### 4.5. Directorios y datos estructurados

- [ ] Teléfono/dirección verificado contra fuente oficial (no heredado de CSV generado por IA).
- [ ] Coordenadas WGS84 válidas y con `coordinate_source`.
- [ ] Fecha de verificación presente; sin fecha no se publica.

---

## 5. Criterios de rechazo inmediato

- [ ] Contenido sin fuente contrastada o con URL rota.
- [ ] Procedimientos médicos obsoletos o peligrosos.
- [ ] Listados sin fecha o con teléfonos no institucionales.
- [ ] Afirmaciones de comestibilidad sin confirmación de experto.
- [ ] Texto generado/parafraseado que no es fiel a la fuente original.
- [ ] Licencia `pendiente_de_verificar` en contenido que se va a indexar.

---

## 6. Evidencia de validación (campos obligatorios)

Al aprobar con `scripts/review.py`, el sistema registra automáticamente:

- `validado_por` → nombre/rol del revisor (pasado con `--operador`).
- `validado_fecha` → fecha de aprobación.

**Recomendación adicional** (no automatizada aún): registrar también la **versión de la fuente revisada** (ej. "ERC-2025, resumen ES") y el **resultado** (aprobado/rechazado con motivo) en un log. El motivo de rechazo hoy no se persiste; conviene anotarlo en la propia ficha de `docs/rag/` correspondiente.

---

## 7. Estado actual de validación

**Política de validación (decisión del usuario 2026-08-28):** el contenido de **fuentes oficiales** (estado/UE/autonómicas: `*.gob.es`, BOE, `*.europa.eu`, Junta de Andalucía, Guardia Civil, Policía, DGT, ADIF, Renfe, CTAN, Cruz Roja, Protección Civil…) y **sociedades científicas de referencia** (ERC) ya está **revisado por la propia institución**, así que se marca `validado_por = "Fuente oficial (estado/UE)"` y se aprueba automáticamente con `scripts/autoaprobar_oficiales.py`. Solo se revisa manualmente el contenido de **fuentes externas/comunitarias** (OpenStreetMap, Wikidata, GBIF, Wikipedia) o de origen no confirmado.

| Estado | Fragmentos |
|---|---:|
| ✅ Aprobados (4474, todos) | 4474 |
| ⏳ Pendientes | 0 |
| **Total** | **4474** |

> La **procesionaria del pino** (única de fuente externa sensible) fue aprobada por **Biólogo Francisco Ramón Gutierrez**. Todos los fragmentos quedan aprobados y listos para indexar.

Comprobar con `python3 scripts/review.py --status`.

---

## 8. Estado de alineación del código

✅ **Completado:** `src/common/models.py` amplió el enum `Categoria` (8 → 15 valores) y `CATEGORIAS_SENSIBLES` (1 → 8 dominios) conforme a la matriz §3. La columna `categoria` de la BD es `TEXT` sin restricción, por lo que **no requiere migración SQL**.

- Nuevas categorías: `toxicologia`, `apoyo_psicosocial`, `proteccion_civil`, `legislacion`, `directorios`, `transporte`, `radio`, `agricultura`.
- Sensibles ahora: primeros auxilios, toxicología, apoyo psicosocial, protección civil, legislación, directorios, radio, agricultura (además del flag `peligrosa` para flora/fauna).
- `requiere_validacion` sigue derivándose de `categoria ∈ CATEGORIAS_SENSIBLES or peligrosa`.

---

## 9. Próximos pasos

1. Revisar los 4474 fragmentos con `scripts/review.py` y aprobar/rechazar.
2. Asignar revisores reales (médico, biólogo, jurista…) con identidad registrada en `validado_por`.
3. Tras aprobar, indexar con `python -m updater.cli --reindex-aprobados`.
4. Continuar la normalización de ERC-2025 e INGESA siguiendo este flujo.

[← Volver al índice](README.md)
