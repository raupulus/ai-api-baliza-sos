# Ficha de Fuente de Conocimiento: Wikidata (Grafo de Conocimiento)

[← Volver al Índice de Fuentes RAG](README.md)

---

## 1. Metadatos de la Fuente

* **Identificador interno:** `wikidata`
* **Categoría principal:** `geografia`
* **Subcategorías:** `municipios`, `hospitales`, `faros`, `accidentes_geograficos`.
* **Entidad / Organismo emisor:** Fundación Wikimedia y comunidad global de Wikidata.
* **URL oficial o referencia documental:** https://query.wikidata.org (Endpoint SPARQL).
* **Licencia de uso:** CC0 1.0 Universal (Dominio Público).
* **Nivel de confianza asignado:** `media`
* **Requiere validación humana:** No.
* **Validador responsable:** `equipo_datos_enlazados`
* **Fecha de creación de la ficha:** `2026-08-27`
* **Fecha de última actualización:** `2026-08-27`

---

## 2. Descripción y Alcance

Permite recuperar mediante consultas SPARQL estructuradas datos enciclopédicos y relacionales de entidades situadas en la provincia de Cádiz:
- Hospitales comarcales y de especialidades con identificadores Q.
- Faros marítimos emblemáticos (Chipiona, Trafalgar, Rota, Tarifa, San Jerónimo).
- Alturas de cumbres y municipios limítrofes.

---

## 3. Bloques Temáticos de Información a Indexar

### Bloque 1: Faros de Navegación del Litoral Gaditano
* Entidades Wikidata con `P31 = Q39715` (faro) e `is in administrative entity = Cádiz (Q81977)`.
* Altura focal, alcance luminoso en millas náuticas y coordenadas GPS.

### Bloque 2: Infraestructuras Sanitarias Mayores
* Entidades con `P31 = Q16917` (hospital).
* Nombre oficial, número de camas, helipuerto y ubicación.

---

## 4. Implementación Técnica Asociada

* **Módulo conector:** `src/updater/sources/wikidata.py`
* **Clase conector:** `WikidataSource`
* **Método de adquisición:** `api` (SPARQL JSON)
* **Comando manual de actualización:**
  ```bash
  python3 scripts/actualizar_fuente.py --fuente wikidata
  ```

---

## 5. Historial de Revisiones

| Versión | Fecha | Autor / Revisor | Descripción del Cambio |
| :---: | :---: | :--- | :--- |
| `1.0.0` | `2026-08-27` | `equipo_datos_enlazados` | Conector SPARQL funcional para entidades de Cádiz. |

---

[← Volver al Índice de Fuentes RAG](README.md)

