# Ficha de Fuente de Conocimiento: Municipios y Geografía Oficial de Cádiz

[← Volver al Índice de Fuentes RAG](README.md)

---

## 1. Metadatos de la Fuente

* **Identificador interno:** `municipios-cadiz`
* **Categoría principal:** `geografia`
* **Subcategorías:** `municipio`, `orografia_montana`, `comarcas`, `refugios`.
* **Entidad / Organismo emisor:** Instituto Geográfico Nacional (IGN, Ministerio de Transportes y Movilidad Sostenible) e Instituto de Estadística y Cartografía de Andalucía (IECA, Junta de Andalucía).
* **URL oficial o referencia documental:**
  - Nomenclátor Geográfico de Andalucía (https://www.juntadeandalucia.es/institutodeestadisticaycartografia).
  - Base Topográfica Nacional 1:25.000 (BTN25 - IGN).
  - Federación Andaluza de Montañismo (FAM).
* **Licencia de uso:** CC-BY 4.0 (Información Geográfica Oficial de Libre Reutilización).
* **Nivel de confianza asignado:** `alta`
* **Requiere validación humana:** No (Datos cartográficos oficiales contrastados).
* **Validador responsable:** `equipo_cartografia_ign`
* **Fecha de creación de la ficha:** `2026-08-27`
* **Fecha de última actualización:** `2026-08-27`

---

## 2. Descripción y Alcance

Proporciona la cobertura espacial completa de la provincia de Cádiz con sus **45 municipios oficiales** y sus accidentes orográficos y montañosos más prominentes.
Permite al asistente responder preguntas de geolocalización, coordenadas GPS exactas (WGS84 latitud/longitud), altitudes, comarcas y puntos clave para rescates o triangulación en caso de desorientación.

---

## 3. Bloques Temáticos de Información a Indexar

### Bloque 1: Bahía de Cádiz
* **Municipios:** Cádiz (capital: 36.5298, -6.2924, alt. 11m), Jerez de la Frontera (36.6850, -6.1261, alt. 56m), San Fernando (36.4644, -6.1983, alt. 8m), El Puerto de Santa María (36.5997, -6.2307, alt. 15m), Chiclana de la Frontera (36.4190, -6.1460, alt. 21m), Puerto Real (36.5284, -6.1906, alt. 14m).

### Bloque 2: Costa Noroeste
* **Municipios:** Sanlúcar de Barrameda (36.7781, -6.3515, alt. 30m, desembocadura Guadalquivir), Chipiona (36.7369, -6.4326, alt. 6m), Rota (36.6214, -6.3586, alt. 12m), Trebujena (36.8705, -6.1755, alt. 69m).

### Bloque 3: La Janda
* **Municipios:** Conil de la Frontera (36.2770, -6.0886, alt. 41m), Vejer de la Frontera (36.2541, -5.9620, alt. 201m), Barbate (36.1923, -5.9221, alt. 14m, Cabo de Trafalgar), Medina Sidonia (36.4572, -5.9269, alt. 337m), Benalup-Casas Viejas (36.3427, -5.8118, alt. 112m), Alcalá de los Gazules (36.4613, -5.7225, alt. 165m), Paterna de Rivera (36.5218, -5.8679, alt. 127m).

### Bloque 4: Campo de Gibraltar
* **Municipios:** Algeciras (36.1274, -5.4536, alt. 20m), La Línea de la Concepción (36.1680, -5.3486, alt. 5m), San Roque (36.2104, -5.3842, alt. 108m), Los Barrios (36.1843, -5.4920, alt. 23m), Tarifa (36.0143, -5.6044, alt. 7m - punto más meridional continental), Jimena de la Frontera (36.4336, -5.4542, alt. 203m), Castellar de la Frontera (36.3168, -5.4538, alt. 48m), San Martín del Tesorillo (36.3411, -5.3186, alt. 42m).

### Bloque 5: Sierra de Cádiz (Pueblos Blancos)
* **Municipios:** Arcos de la Frontera (36.7483, -5.8106), Grazalema (36.7588, -5.3688, alt. 812m), Ubrique (36.6787, -5.4468), El Bosque (36.7578, -5.5066), Villamartín (36.8601, -5.6468), Olvera (36.9344, -5.2662), Zahara de la Sierra (36.8400, -5.3900), Algodonales (36.8809, -5.4055), Bornos (36.8206, -5.7444), Prado del Rey (36.7891, -5.5562), Espera (36.8724, -5.8055), Setenil de las Bodegas (36.8639, -5.1812, alt. 640m), Torre Alháquime (36.9158, -5.2346), Alcalá del Valle (36.9048, -5.1724), Benaocaz (36.7003, -5.4216), Villaluenga del Rosario (36.6974, -5.3850, alt. 858m - pueblo más alto), Algar (36.6560, -5.6568), El Gastor (36.8550, -5.3210), Puerto Serrano (36.9224, -5.5456).

### Bloque 6: Cumbres, Puertos y Puntos Orográficos Estratégicos
* **Pico El Torreón:** Máxima altitud de Cádiz (1648 m), Sierra del Pinar en Grazalema (36.7645, -5.4121).
* **Pico El Aljibe:** Máxima cumbre de Los Alcornocales (1092 m, 36.4678, -5.5902).
* **Puerto de las Palomas:** Paso de carretera a 1157 m (36.7663, -5.3789) entre Grazalema y Zahara.
* **Puerto del Boyar:** Divisoria de aguas y mirador panorámico a 1103 m (36.7512, -5.4053).

---

## 4. Implementación Técnica Asociada

* **Módulo conector:** `src/updater/sources/municipios_cadiz.py`
* **Clase conector:** `MunicipiosCadizSource`
* **Método de adquisición:** `nomenclator_oficial`
* **Comando manual de actualización:**
  ```bash
  python3 scripts/actualizar_fuente.py --fuente municipios-cadiz
  ```

---

## 5. Historial de Revisiones

| Versión | Fecha | Autor / Revisor | Descripción del Cambio |
| :---: | :---: | :--- | :--- |
| `1.0.0` | `2026-08-27` | `equipo_cartografia_ign` | Incorporación exhaustiva de los 45 municipios de Cádiz con coordenadas GPS, altitud y 4 puntos orográficos principales (48 fragmentos). |

---

[← Volver al Índice de Fuentes RAG](README.md)

