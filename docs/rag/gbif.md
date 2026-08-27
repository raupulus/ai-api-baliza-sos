# Ficha de Fuente de Conocimiento: GBIF (Biodiversidad Global)

---

## 1. Metadatos de la Fuente

* **Identificador interno:** `gbif`
* **Categoría principal:** `fauna` / `flora`
* **Subcategorías:** `biodiversidad_cadiz`, `avistamientos`, `especies_autoctonas`.
* **Entidad / Organismo emisor:** Global Biodiversity Information Facility (GBIF.org) y Nodo Nacional de Información en Biodiversidad (GBIF.ES / CSIC).
* **URL oficial o referencia documental:** https://api.gbif.org/v1/occurrence/search
* **Licencia de uso:** CC-BY 4.0 / CC0 (según el dataset de cada observación científica).
* **Nivel de confianza asignado:** `alta` (Observaciones científicas georreferenciadas).
* **Requiere validación humana:** Sí para reclasificar taxones peligrosos o de interés médico.
* **Validador responsable:** `equipo_biodiversidad_gbif`
* **Fecha de creación de la ficha:** `2026-08-27`
* **Fecha de última actualización:** `2026-08-27`

---

## 2. Descripción y Alcance

Permite recuperar registros de presencia biológica de especies observadas y validadas por científicos y naturalistas dentro del polígono geográfico (BBOX) de la provincia de Cádiz:
- Pinsapo (*Abies pinsapo*) en la Sierra de Grazalema.
- Buitre leonado y alimoche en los tajos rocosos.
- Camaleón común (*Chamaeleo chamaeleon*) en las dunas de Rota, Chipiona y San Fernando.
- Cetáceos en el Estrecho de Gibraltar (orcas, calderones, delfines).

---

## 3. Bloques Temáticos de Información a Indexar

### Bloque 1: Flora Emblemática y Endemismos
* Registros confirmados con coordenadas de especies protegidas o singulares de Cádiz.

### Bloque 2: Fauna Terrestre y Aviar de las Sierras
* Densidad de presencia de rapaces, mamíferos y reptiles en Grazalema y Alcornocales.

---

## 4. Implementación Técnica Asociada

* **Módulo conector:** `src/updater/sources/gbif.py`
* **Clase conector:** `GbifSource`
* **Método de adquisición:** `api` (REST JSON)
* **Comando manual de actualización:**
  ```bash
  python3 scripts/actualizar_fuente.py --fuente gbif
  ```

---

## 5. Historial de Revisiones

| Versión | Fecha | Autor / Revisor | Descripción del Cambio |
| :---: | :---: | :--- | :--- |
| `1.0.0` | `2026-08-27` | `equipo_biodiversidad_gbif` | Conector REST con paginación, filtros de BBOX y normalización de fragmentos. |
