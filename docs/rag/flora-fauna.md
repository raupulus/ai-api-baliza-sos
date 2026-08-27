# Ficha de Fuente de Conocimiento: Flora y Fauna de Cádiz

[← Volver al Índice de Fuentes RAG](README.md)

---

## 1. Metadatos de la Fuente

* **Identificador interno:** `flora-fauna-cadiz`
* **Categoría principal:** `flora` / `fauna`
* **Subcategorías:** `plantas_toxicas`, `setas_toxicas`, `plantas_comestibles`, `reptiles_peligrosos`, `artropodos`, `fauna_marina`.
* **Entidad / Organismo emisor:** Red de Información Ambiental de Andalucía (REDIAM), Herbario Andaluz (Junta de Andalucía), Sociedad Española de Herpetología (AHE), Asociación Micológica Sierra de Grazalema y Parque Natural Los Alcornocales.
* **URL oficial o referencia documental:**
  - Catálogo de Flora Silvestre Amenazada y de Interés de Andalucía (REDIAM).
  - Guía Micológica de la Sierra de Grazalema y Los Alcornocales.
  - Inventario de Especies de la Costa Atlántica Gaditana.
* **Licencia de uso:** CC-BY 4.0 (Biodiversidad y Seguridad Ambiental).
* **Nivel de confianza asignado:** `alta`
* **Requiere validación humana:** Sí (Validado por biólogos).
* **Validador responsable:** `equipo_botanica_zoologia`
* **Fecha de creación de la ficha:** `2026-08-27`
* **Fecha de última actualización:** `2026-08-27`

---

## 2. Descripción y Alcance

Esta fuente recopila las especies vegetales, micológicas y animales más relevantes de la provincia de Cádiz con especial foco en:
1. **Seguridad y toxicidad:** Especies venenosas cuya ingestión, mordedura o contacto directo entrañan riesgo de muerte o intoxicación severa en excursiones o playas.
2. **Supervivencia y alimentación:** Plantas silvestres autóctonas seguras y comestibles (fuente de agua y nutrientes en extravío).

---

## 3. Bloques Temáticos de Información a Indexar

### Bloque 1: Flora Tóxica Silvestre de Cádiz
* **Especies clave:**
  - **Adelfa (*Nerium oleander*):** Contiene oleandrina (cardiotóxica letal). Toda la planta es venenosa, incluido el humo al quemarse.
  - **Estramonio (*Datura stramonium*):** Alcaloides tropánicos (escopolamina, atropina). Produce alucinaciones graves, parálisis y coma.
  - **Cicuta mayor (*Conium maculatum*):** Cicutina neurotóxica. Tallo con motas púrpuras y olor fétido a orina de ratón. Mortal en minutos por asfixia.

### Bloque 2: Micología Tóxica de Grazalema y Alcornocales
* **Especies clave:**
  - **Cicuta verde / Oronja verde (*Amanita phalloides*):** Causa el 90% de intoxicaciones fúngicas mortales. Muy común bajo encinas, alcornoques y castaños en otoño. Sombrero oliváceo, láminas blancas, anillo y volva en saco. Síntomas tardíos (6-24 h) seguidos de fallo hepático agudo.

### Bloque 3: Plantas Silvestres Comestibles de Supervivencia
* **Especies clave:**
  - **Tagarnina (*Scolymus hispanicus*):** Cardo silvestre muy extendido. Pencas comestibles ricas en inulina y potasio.
  - **Palmito (*Chamaerops humilis*):** Única palmera autóctona europea. El cogollo tierno basal ("espadiña") es comestible crudo o asado.
  - **Espárrago triguero (*Asparagus acutifolius*):** Brotes tiernos comestibles ricos en nutrientes y agua.

### Bloque 4: Fauna Terrestre Peligrosa
* **Especies clave:**
  - **Víbora hocicuda (*Vipera latastei*):** Cabeza triangular con apéndice nasal elevado y zigzag dorsal. Habita en pedregales y matorrales soleados. Mordedura grave que requiere suero hospitalario.
  - **Escolopendra (*Scolopendra cingulata*):** Ciempiés gigante de hasta 17 cm. Picadura muy dolorosa con edema intenso.
  - **Araña reclusa o violinista (*Loxosceles rufescens*):** Mancha en violín sobre cefalotórax. Picadura con riesgo de necrosis cutánea local.

### Bloque 5: Fauna Marina Peligrosa
* **Especies clave:**
  - **Pez araña (*Trachinus draco*):** Enterrado en la arena de la orilla. Espinas dorsales venenosas con toxina termolábil.
  - **Carabela portuguesa (*Physalia physalis*):** Flotador gasoso azulado y largos tentáculos urticantes que provocan quemaduras químicas severas.

---

## 4. Implementación Técnica Asociada

* **Módulo conector:** `src/updater/sources/flora_fauna_cadiz.py`
* **Clase conector:** `FloraFaunaCadizSource`
* **Método de adquisición:** `manual_validado`
* **Comando manual de actualización:**
  ```bash
  python3 scripts/actualizar_fuente.py --fuente flora-fauna-cadiz
  ```

---

## 5. Historial de Revisiones

| Versión | Fecha | Autor / Revisor | Descripción del Cambio |
| :---: | :---: | :--- | :--- |
| `1.0.0` | `2026-08-27` | `equipo_botanica_zoologia` | Ficha inicial con 12 especies críticas de Cádiz (plantas tóxicas, setas, comestibles y fauna venenosa). |

---

[← Volver al Índice de Fuentes RAG](README.md)

