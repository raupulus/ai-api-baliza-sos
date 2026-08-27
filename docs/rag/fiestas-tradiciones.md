# Ficha de Fuente de Conocimiento: Fiestas y Tradiciones de la Provincia de Cádiz

[← Volver al Índice de Fuentes RAG](README.md)

---

## 1. Metadatos de la Fuente

* **Identificador interno:** `fiestas-cadiz`
* **Categoría principal:** `cultura_historia`
* **Subcategorías:** `carnaval`, `feria`, `carreras_caballos`, `semana_santa`, `romeria`, `festividad_popular`, `fiesta_marinera`, `corpus_christi`.
* **Entidad / Organismo emisor:** Patronato Provincial de Turismo de la Diputación de Cádiz y Consejería de Turismo, Cultura y Deporte de la Junta de Andalucía.
* **URL oficial o referencia documental:**
  - Guía Oficial de Fiestas de la Provincia de Cádiz (https://www.cadizturismo.com).
  - Catálogo General del Patrimonio Histórico Andaluz (Actividades de Interés Etnológico).
* **Licencia de uso:** CC-BY 4.0 (Patrimonio Cultural Inmaterial y Turismo).
* **Nivel de confianza asignado:** `alta`
* **Requiere validación humana:** No (Fuentes oficiales institucionales y etnográficas).
* **Validador responsable:** `equipo_cultura_turismo`
* **Fecha de creación de la ficha:** `2026-08-27`
* **Fecha de última actualización:** `2026-08-27`

---

## 2. Descripción y Alcance

Cubre el calendario festivo tradicional, ferias, carnavales, romerías y celebraciones populares de la provincia de Cádiz. Permite al asistente responder a preguntas de contexto cultural, afluencia masiva, gastronomía típica ligada a eventos, fechas aproximadas y localidades donde se celebran.

---

## 3. Bloques Temáticos de Información a Indexar

### Bloque 1: Carnaval de Cádiz (Cádiz Capital)
* **Fecha:** Febrero o principios de marzo.
* **Relevancia:** Fiesta de Interés Turístico Internacional.
* **Aspectos clave:** Concurso Oficial de Agrupaciones Carnavalescas (COAC) en el Gran Teatro Falla, chirigotas ilegales y callejeras por el barrio de La Viña, plaza de las Flores y el Palillero. Erizadas, ostionadas y pestiñadas gastronómicas.

### Bloque 2: Feria del Caballo de Jerez de la Frontera
* **Fecha:** Mayo.
* **Relevancia:** Fiesta de Interés Turístico Internacional.
* **Aspectos clave:** Parque González Hontoria, paseo de jinetes y enganches ecuestres, casetas de acceso público libre, flamenco, sevillanas y degustación de vino fino y rebujito con tapas locales.

### Bloque 3: Carreras de Caballos en las Playas de Sanlúcar de Barrameda
* **Fecha:** Agosto (dos ciclos según las mareas vivas de bajamar).
* **Relevancia:** Fiesta de Interés Turístico Internacional desde 1845.
* **Aspectos clave:** Purasangres compitiendo sobre la arena húmeda de la playa de Bajo de Guía con Doñana al fondo. Apuestas infantiles y consumo de Manzanilla de Sanlúcar y langostinos.

### Bloque 4: Semana Santa de la Provincia de Cádiz
* **Fecha:** Marzo o abril (según calendario lunar).
* **Localidades destacadas:** Cádiz capital (recorridos estrechos y empinados), Jerez de la Frontera (alta imaginería) y Arcos de la Frontera. Cantes por saetas al paso de los misterios y palios.

### Bloque 5: Ferias Locales y del Vino
* **Feria de la Manzanilla (Sanlúcar):** Finales de mayo / primeros de junio en la Calzada de la Duquesa.
* **Feria de Primavera y Fiesta del Vino Fino (El Puerto de Santa María):** Mayo en el recinto de Las Banderas.

### Bloque 6: Romerías y Festividades Marineras
* **Romería del Rocío:** Salida de hermandades gaditanas en mayo/junio embarcando en Bajo de Guía para cruzar Doñana.
* **Noche de San Juan (23-24 de junio):** Quema de los tradicionales "Juanillos" (muñecos satíricos) y hogueras en las playas (La Caleta, Victoria, Conil, Barbate).
* **Fiestas de la Virgen del Carmen (16 de julio):** Procesiones marineras en barcos engalanados en Barbate, Conil, Rota y Algeciras bendiciendo las aguas.
* **Corpus Christi de Zahara de la Sierra:** Junio, Fiesta de Interés Turístico Nacional con calles cubiertas por un dosel de juncia y quejigo aromático.

---

## 4. Implementación Técnica Asociada

* **Módulo conector:** `src/updater/sources/fiestas_cadiz.py`
* **Clase conector:** `FiestasCadizSource`
* **Método de adquisición:** `manual_validado`
* **Comando manual de actualización:**
  ```bash
  python3 scripts/actualizar_fuente.py --fuente fiestas-cadiz
  ```

---

## 5. Historial de Revisiones

| Versión | Fecha | Autor / Revisor | Descripción del Cambio |
| :---: | :---: | :--- | :--- |
| `1.0.0` | `2026-08-27` | `equipo_cultura_turismo` | 10 fragmentos indexados con las festividades mayores de la provincia de Cádiz. |

---

[← Volver al Índice de Fuentes RAG](README.md)

