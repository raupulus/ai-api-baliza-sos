# Ficha de Fuente de Conocimiento: [NOMBRE DE LA FUENTE]

[← Volver al Índice de Fuentes RAG](README.md)

> **Plantilla estándar para registrar y mantener fuentes de conocimiento en el RAG.**
> Toda fuente debe disponer de esta ficha antes de ser indexada en producción.

---

## 1. Metadatos de la Fuente

* **Identificador interno:** `nombre-de-la-fuente` *(formato kebab-case usado en el CLI y en el código)*
* **Categoría principal:** `[primeros_auxilios | fauna | flora | geografia | supervivencia | orientacion | clima | cultura_historia]`
* **Subcategorías:** `[subcategoria_1, subcategoria_2, ...]`
* **Entidad / Organismo emisor:** `[Nombre oficial del organismo, institución o colectivo]`
* **URL oficial o referencia documental:** `[https://... o referencia bibliográfica]`
* **Licencia de uso:** `[Ej. CC-BY 4.0, ODbL, Dominio Público, etc.]`
* **Nivel de confianza asignado:** `[alta | media | baja]` *(las fuentes médicas oficiales siempre llevan 'alta')*
* **Requiere validación humana:** `[Sí | No]` *(obligatorio 'Sí' para medicina y especies venenosas)*
* **Validador responsable:** `[Nombre del equipo, revisor o identificador]`
* **Fecha de creación de la ficha:** `AAAA-MM-DD`
* **Fecha de última actualización:** `AAAA-MM-DD`

---

## 2. Descripción y Alcance

Describe brevemente qué información cubre esta fuente, por qué es relevante para el Asistente de Emergencias y Supervivencia de Cádiz y en qué situaciones de auxilio o consulta se activará en el RAG.

---

## 3. Bloques Temáticos de Información a Indexar

Detalla cada uno de los temas o bloques de datos que el conector debe extraer y convertir en fragmentos vectoriales:

### Bloque 1: [Título del Bloque 1]
* **Objetivo:** Qué debe aprender el bot de este bloque.
* **Contenido clave:**
  - Puntos esenciales a cubrir.
  - Terminología o palabras clave para la búsqueda semántica.
* **Ejemplo de fragmento normalizado:**
  > *"Texto breve (150-450 caracteres), accionable, claro y en español..."*

### Bloque 2: [Título del Bloque 2]
* **Objetivo:** ...
* **Contenido clave:** ...
* **Ejemplo de fragmento normalizado:**
  > *...*

---

## 4. Implementación Técnica Asociada

* **Módulo conector:** `src/updater/sources/<nombre_modulo>.py`
* **Clase conector:** `<NombreClaseSource>`
* **Método de adquisición:** `[manual_validado | api | scraping_pdf | open_data]`
* **Comando manual de actualización:**
  ```bash
  python3 scripts/actualizar_fuente.py --fuente <identificador-interno>
  ```

---

## 5. Historial de Revisiones

| Versión | Fecha | Autor / Revisor | Descripción del Cambio |
| :---: | :---: | :--- | :--- |
| `1.0.0` | `AAAA-MM-DD` | `[Nombre]` | Creación inicial de la fuente e indexación del corpus base. |

---

[← Volver al Índice de Fuentes RAG](README.md)

