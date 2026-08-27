# Ficha de Fuente de Conocimiento: Historia y Patrimonio de la Provincia de Cádiz

---

## 1. Metadatos de la Fuente

* **Identificador interno:** `historia-cadiz`
* **Categoría principal:** `cultura_historia`
* **Subcategorías:** `antiguedad_fenicia`, `antiguedad_romana`, `edad_media_reconquista`, `carrera_indias`, `batalla_trafalgar`, `constitucion_1812`.
* **Entidad / Organismo emisor:** Archivo Histórico Provincial de Cádiz, Instituto Andaluz del Patrimonio Histórico (IAPH, Junta de Andalucía) y Museo de Cádiz.
* **URL oficial o referencia documental:**
  - Guía del Patrimonio Histórico de la Provincia de Cádiz (IAPH).
  - Archivo Histórico Provincial de Cádiz (Junta de Andalucía).
  - Centro de Interpretación de la Constitución de 1812 y Yacimiento Arqueológico Gadir.
* **Licencia de uso:** CC-BY 4.0 (Patrimonio Histórico y Documental).
* **Nivel de confianza asignado:** `alta`
* **Requiere validación humana:** No (Fuentes historiográficas contrastadas).
* **Validador responsable:** `equipo_historia_archivo`
* **Fecha de creación de la ficha:** `2026-08-27`
* **Fecha de última actualización:** `2026-08-27`

---

## 2. Descripción y Alcance

Cubre los grandes hitos históricos y patrimoniales que han modelado la geografía, arquitectura y cultura de la provincia de Cádiz: desde su fundación en la antigüedad hasta la época contemporánea. Permite responder consultas sobre orígenes de topónimos, batallas navales, fortalezas defensivas, murallas y efemérides constitucionales.

---

## 3. Bloques Temáticos de Información a Indexar

### Bloque 1: Fundación Fenicia de Gadir (c. 1100 a.C.)
* **Hitos:** Considerada la ciudad viva más antigua de Occidente, fundada hacia 1104 a.C. por fenicios de Tiro. Santuario del dios Melqart (Hércules gaditano) en el islote de Sancti Petri, yacimiento arqueológico Gadir y sarcófagos antropoides en el Museo de Cádiz.

### Bloque 2: Gades Romano y Baelo Claudia
* **Hitos:** Prosperidad bajo la familia de los Balbos. Teatro romano de Cádiz, acueducto de Tempul y factorías de salazón de pescado y salsa garum. Ciudad hispanorromana de Baelo Claudia (playa de Bolonia, Tarifa) con basílica, foro, termas y templos a la tríada capitolina.

### Bloque 3: Al-Ándalus y la Reconquista ("de la Frontera")
* **Hitos:** Presencia musulmana desde 711. En el siglo XIII, tras la conquista de Alfonso X el Sabio, el territorio fijó la frontera militar con el reino nazarí de Granada, originando el sobrenombre histórico "de la Frontera" en Arcos, Chiclana, Conil, Vejer y Jerez.

### Bloque 4: La Carrera de Indias y Siglo de Oro Gaditano (Siglo XVIII)
* **Hitos:** En 1717 se traslada la Casa de la Contratación y el Consulado de Indias de Sevilla a Cádiz, consolidando el monopolio del comercio con América. Época de mayor esplendor económico y cosmopolita: construcción de baluartes, murallas y más de un centenar de torres mirador (Torre Tavira).

### Bloque 5: Batalla de Trafalgar (21 de octubre de 1805)
* **Hitos:** Combate naval entre la flota combinada hispano-francesa y la armada británica de Horatio Nelson frente al Cabo de Trafalgar (Barbate / Caños de Meca), que consolidó la hegemonía marítima británica.

### Bloque 6: Las Cortes de Cádiz y la Constitución de 1812 ("La Pepa")
* **Hitos:** Asedio de las tropas napoleónicas (1810-1812) resistido por Cádiz y San Fernando (Real Isla de León). Promulgación el 19 de marzo de 1812 en el Oratorio de San Felipe Neri de la primera constitución liberal española, que consagró la soberanía nacional, división de poderes y libertad de imprenta.

---

## 4. Implementación Técnica Asociada

* **Módulo conector:** `src/updater/sources/historia_cadiz.py`
* **Clase conector:** `HistoriaCadizSource`
* **Método de adquisición:** `manual_validado`
* **Comando manual de actualización:**
  ```bash
  python3 scripts/actualizar_fuente.py --fuente historia-cadiz
  ```

---

## 5. Historial de Revisiones

| Versión | Fecha | Autor / Revisor | Descripción del Cambio |
| :---: | :---: | :--- | :--- |
| `1.0.0` | `2026-08-27` | `equipo_historia_archivo` | 6 fragmentos estructurados con la cronología histórica principal de Cádiz. |
