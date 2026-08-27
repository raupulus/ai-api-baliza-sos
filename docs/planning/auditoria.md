# Auditoría de Calidad, Comportamiento y Datos del Asistente

> **Fecha:** 2026-08-27  
> **Estado:** Documento de análisis y registro de fallos.  
> **Objetivo:** Identificar las causas raíz del bajo rendimiento del asistente en pruebas reales y evaluar la arquitectura necesaria para que sea certero, fiable y verdaderamente útil en situaciones de emergencia offline.

---

## 1. Registro de Incidentes y Fallos Observados en Pruebas Reales

En las pruebas directas sobre la interfaz web (`http://172.18.1.121:8443`) simulando una caída en montaña en la Sierra de Cádiz, se han manifestado fallos graves de coherencia, utilidad clínica y calidad lingüística:

### A. Alucinaciones Sintácticas y Médicas Incoherentes
* **Español roto / Construcciones gramaticales inexistentes:**
  > *"No muevaste, por favor."*
  Un modelo de lenguaje bien ajustado no debería conjugar de forma errónea una orden básica en español (*"No te muevas"*).
* **Invención de conceptos médicos y terminología disparatada:**
  > *"Aplica un yes pos (presión arterial) en la pierna si es posible."*
  Peligro crítico: el modelo mezcla fragmentos de inglés, traduce erróneamente términos o inventa maniobras médicas inexistentes ("yes pos") que en una situación de emergencia real causarían confusión letal o daños graves a la víctima.

### B. Respuestas Burocráticas, Inútiles y Efecto "Loro RAG"
* **Escupir fragmentos del RAG sin resolver el problema:** El sistema toma el fragmento recuperado (ej. *"Evalúa tu consciencia..."*) y lo vomita con ligeras variaciones, sin atender a la consulta concreta que el usuario acaba de formular.
* **Obsesión con la muletilla del 112:**
  En una red LoRa/Meshtastic o en áreas aisladas de la Sierra de Grazalema donde **no hay cobertura móvil ni internet**, el usuario consulta a este bot precisamente porque **NO PUEDE llamar al 112**.
  Responder en cada mensaje: *"Llama al 112 con tu ubicación"* no aporta ningún valor y deja al usuario desamparado ante hipotermia, fracturas o deshidratación. El bot debe enseñar **qué hacer mientras no hay auxilio** (inmovilizar con ramas/ropa, buscar abrigo, potabilizar agua) y, en todo caso, indicar qué datos emitir por radiofrecuencia.
* **Incapacidad para interpretar referencias geográficas reales:**
  Cuando el usuario dice: *"veo a la derecha una ciudad y a la izquierda un lago muy grande"*, el bot debería ser capaz de relacionar ese escenario con la orografía de Cádiz (ej. Sierra de Líjar/Grazalema con vistas al embalse de Zahara-El Gastor y el pueblo de Algodonales o Zahara). En lugar de eso, el bot ignoró la referencia o la repitió textualmente sin aportar orientación alguna.

---

## 2. Diagnóstico Técnico de Causas Raíz

### 2.1. Limitaciones Cognitivas del Modelo Pequeño (Qwen2.5-3B)
* **Presupuesto paramétrico:** Un modelo de 3.000 millones de parámetros cuantizado a 4 bits (`Q4_K_M`) tiene una ventana de razonamiento y precisión léxica muy limitada en español comparado con modelos mayores.
* **Sobrecarga de instrucciones negativas y restricciones:** El prompt actual satura la capacidad atencional del modelo pequeño (triage activo, no inventar, máx 3 frases, máx caracteres, formato JSON, aviso 112). Cuando un modelo 3B se satura, degenera en incoherencias ("yes pos") o repeticiones atractoras.
* **Ausencia de Few-Shot:** Los modelos pequeños aprenden por imitación directa de ejemplos, no por abstracción de reglas complejas. Sin 3 o 4 ejemplos exactos de cómo responder paso a paso en español impecable, el modelo improvisa con resultados deficientes.
* **Oportunidad de Hardware (RPi5 8 GB):** La máquina de despliegue actual cuenta con **8 GB de RAM**. Qwen2.5-3B ocupa apenas ~2.0 GB. Existe margen sobrado en RAM para evaluar modelos de **7B u 8B parámetros** (como `Qwen2.5-7B-Instruct-Q4_K_M` ~4.5 GB RAM, o `Llama-3.1-8B-Instruct-Q4_K_M`), cuya solidez lingüística en español, comprensión médica y razonamiento contextual están a un nivel infinitamente superior.

### 2.2. Deficiencias en el Corpus RAG Actual
* **Textos sintéticos y dispersos:** Los fragmentos indexados actualmente provienen de resúmenes semi-manuales en scripts de Python, sin un estándar riguroso de extracción a partir de manuales oficiales íntegros.
* **Falta de granularidad accionable:** Muchos fragmentos contienen generalidades en lugar de guías de campo directas y claras (ej. protocolos paso a paso de inmovilización sin férula comercial, puntos de agua de manantial fiables, triangulación por embalses de la provincia).
* **Ausencia de pipeline de datos formal:** No existe un proceso reproducible que tome documentos oficiales en bruto (PDFs de Cruz Roja, Protección Civil, manuales de rescate en montaña de la Guardia Civil / GREIM, IGN), los limpie, los corte en chunks atómicos y los almacene en un archivo auditable (CSV/JSONL) en el repositorio antes de vectorizarlos.

---

## 3. Plan de Acción y Evaluación de Soluciones

Para transformar este prototipo en un asistente verdaderamente certero y útil en emergencias offline, se plantean tres líneas de trabajo coordinadas:

### Línea 1: Reestructuración Integral del Corpus RAG (Datos Limpios y Verificados)
1. **Directorio temporal de trabajo (`data/raw/` o staging temporal):**
   * Descargar exclusivamente documentación técnica y médica oficial:
     * Manuales de primeros auxilios en montaña y zonas aisladas (Cruz Roja, SEMES, GREIM).
     * Cartografía y orografía de Cádiz (cumbres, valles, embalses, orientaciones típicas).
     * Protocolos de supervivencia (potabilización, refugio, señales de socorro).
2. **Pipeline de Procesamiento y Chunking:**
   * Script estructurado que limpie paja, elimine lenguaje redundante y genere fragmentos de alta densidad de información (formato acción-reacción).
3. **Repositorio Maestro en CSV/JSONL:**
   * Archivo versionado en Git (`data/corpus_cadiz_validado.csv` o similar) con columnas claras:
     * `id`: identificador único.
     * `categoria` / `subcategoria`.
     * `titulo_fuente` / `url_oficial` / `fecha_extraccion`.
     * `texto`: fragmento limpio, conciso y atómico.
     * `validado_por` / `fecha_validacion`.
   * Este archivo será la única fuente de verdad para poblar PostgreSQL + pgvector mediante un script determinista e idempotente.

### Línea 2: Optimización del Motor LLM en Raspberry Pi 5
1. **Prueba de Modelos Superiores (7B/8B):**
   * Evaluar en la RPi5 con 8 GB el rendimiento y latencia de:
     * `Qwen2.5-7B-Instruct-Q4_K_M` (~4.5 GB RAM).
     * `Llama-3.1-8B-Instruct-Q4_K_M` (~4.9 GB RAM).
   * Determinar si la latencia (15–25 s) es admisible a cambio de erradicar al 100% las alucinaciones léxicas ("yes pos", "No muevaste") y ganar comprensión situacional real.
2. **Few-Shot Prompting:**
   * Sustituir explicaciones abstractas por 3 ejemplos canónicos en el prompt:
     * *Ejemplo 1:* Accidente traumático en montaña sin cobertura (inmovilización con ropa, posición anti-shock, abrigo, referencias).
     * *Ejemplo 2:* Picadura o envenenamiento en costa/campo (actuación inmediata, qué NO hacer).
     * *Ejemplo 3:* Desorientación geográfica (triangulación por hitos visuales de Cádiz).

### Línea 3: Reenfoque del Comportamiento de Emergencia (Asumir "Sin Cobertura")
* **Premisa de diseño:** El bot debe asumir por defecto que el usuario **no tiene teléfono móvil disponible** (por eso usa LoRa o un nodo offline).
* Las respuestas deben centrarse en:
  1. **Autoprotección y supervivencia inmediata** (primeros auxilios de campo sin material médico profesional).
  2. **Estabilización de la víctima** (evitar empeoramiento, shock o hipotermia).
  3. **Preparación para rescate** (cómo señalizar la posición, qué referencias recopilar para cuando haya enlace de radio o avistamiento).
