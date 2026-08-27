# Ficha de Fuente de Conocimiento: OpenStreetMap (Overpass API)

[← Volver al Índice de Fuentes RAG](README.md)

---

## 1. Metadatos de la Fuente

* **Identificador interno:** `overpass-osm`
* **Categoría principal:** `geografia` (y `primeros_auxilios` para puntos sanitarios)
* **Subcategorías:** `farmacias`, `centros_salud`, `fuentes_agua`, `policia_rescate`, `helisuperficies`.
* **Entidad / Organismo emisor:** OpenStreetMap Foundation y comunidad global de cartografía abierta colaborativa.
* **URL oficial o referencia documental:** https://overpass-api.de
* **Licencia de uso:** ODbL (Open Database License) 1.0 (Requiere atribución: "© Colaboradores de OpenStreetMap").
* **Nivel de confianza asignado:** `media` (Cartografía colaborativa revisada).
* **Requiere validación humana:** No para geografía general; sí para centros de urgencias críticos.
* **Validador responsable:** `equipo_cartografia_osm`
* **Fecha de creación de la ficha:** `2026-08-27`
* **Fecha de última actualización:** `2026-08-27`

---

## 2. Descripción y Alcance

Consulta mediante el API Overpass elementos geoespaciales y puntos de interés (POIs) de auxilio y supervivencia en el BBOX de la provincia de Cádiz:
- Farmacias y botiquines en zonas aisladas.
- Centros de salud, ambulatorios y puntos de atención continuada.
- Fuentes de agua potable pública (`amenity=drinking_water`).
- Puestos de socorro costero, comisarías y parques de bomberos.

---

## 3. Bloques Temáticos de Información a Indexar

### Bloque 1: Farmacias y Urgencias Sanitarias
* Filtros Overpass: `node["amenity"="pharmacy"]`, `node["amenity"="hospital"]`, `node["amenity"="clinic"]`.
* Atributos extraídos: Nombre, calle, municipio, teléfono y coordenadas GPS.

### Bloque 2: Puntos de Agua Potable y Supervivencia
* Filtros Overpass: `node["amenity"="drinking_water"]`.
* Atributos extraídos: Ubicación, estado del manantial/fuente y coordenadas.

### Bloque 3: Seguridad y Rescate
* Filtros Overpass: `node["amenity"="police"]`, `node["amenity"="fire_station"]`, `node["emergency"="defibrillator"]`.

---

## 4. Implementación Técnica Asociada

* **Módulo conector:** `src/updater/sources/overpass.py`
* **Clase conector:** `OverpassSource`
* **Método de adquisición:** `api` (HTTP Overpass QL)
* **Comando manual de actualización:**
  ```bash
  python3 scripts/actualizar_fuente.py --fuente overpass-osm
  ```

---

## 5. Historial de Revisiones

| Versión | Fecha | Autor / Revisor | Descripción del Cambio |
| :---: | :---: | :--- | :--- |
| `1.0.0` | `2026-08-27` | `equipo_cartografia_osm` | Conector inicial con soporte de BBOX gaditano y rate limiting. |

---

[← Volver al Índice de Fuentes RAG](README.md)

