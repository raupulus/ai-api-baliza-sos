# Ficha de Fuente de Conocimiento: Primeros Auxilios y Supervivencia Avanzada

---

## 1. Metadatos de la Fuente

* **Identificador interno:** `primeros-auxilios-avanzado`
* **Categoría principal:** `primeros_auxilios` (con bloques complementarios en `supervivencia`)
* **Subcategorías:** `traumatismos_montana`, `inmovilizacion_tobillo`, `hemorragias`, `rcp_soporte_vital`, `atragantamiento`, `golpe_de_calor`, `hipotermia`, `pez_arana`, `carabela_portuguesa`, `vibora_hocicuda`, `desorientacion_stop`, `senales_socorro`, `potabilizacion_agua`.
* **Entidad / Organismo emisor:** Cruz Roja Española, Sociedad Española de Medicina de Urgencias y Emergencias (SEMES), Dirección General de Protección Civil y Emergencias (Ministerio del Interior), y GREIM (Grupos de Rescate Especial de Intervención en Montaña de la Guardia Civil).
* **URL oficial o referencia documental:**
  - Guías Oficiales de Primeros Auxilios de Cruz Roja Española (https://www.cruzroja.es).
  - Protocolos de Soporte Vital Básico y Triaje de SEMES (https://www.semes.org).
  - Manual de Autoprotección y Emergencias de Protección Civil Andalucía.
* **Licencia de uso:** CC-BY-NC-SA 4.0 (Guías Sanitarias Oficiales y Material Docente Público).
* **Nivel de confianza asignado:** `alta`
* **Requiere validación humana:** Sí (Validado médicamente).
* **Validador responsable:** `equipo_sanitario_emergencias`
* **Fecha de creación de la ficha:** `2026-08-27`
* **Fecha de última actualización:** `2026-08-27`

---

## 2. Descripción y Alcance

Esta fuente proporciona el núcleo de conocimiento médico y de supervivencia para situaciones críticas en la provincia de Cádiz:
- **Entorno de montaña (Sierra de Grazalema, Los Alcornocales):** Traumatismos por caídas, esguinces, desorientación en senderos escarpados y shock térmico (hipotermia por humedad o calor extremo).
- **Entorno costero y litoral (Bahía de Cádiz, Costa de la Luz, Estrecho de Tarifa):** Picaduras de peces venenosos (pez araña), celentéreos (carabela portuguesa, medusas) y deshidratación o golpe de calor agravado por viento de Levante.
- **Soporte vital inmediato:** Maniobras esenciales que cualquier persona sin formación médica puede ejecutar paso a paso (RCP, desatragantamiento de Heimlich, hemostasia y torniquetes) mientras se coordinan los servicios de emergencia del 112.

---

## 3. Bloques Temáticos de Información a Indexar

### Bloque 1: Traumatología y Caídas en Montaña
* **Objetivo:** Pautas de rescate sin agravar posibles lesiones vertebrales o articulares.
* **Contenido clave:**
  - No mover a víctimas con sospecha de daño en columna o cuello salvo peligro inminente.
  - Inmovilización de tobillos y rodillas con férulas improvisadas sin retirar la bota en marcha.
  - Aislamiento térmico del suelo para evitar el enfriamiento rápido del accidentado.

### Bloque 2: Hemorragias Masivas y Torniquetes
* **Objetivo:** Detención de sangrado severo antes de que ocurra shock hipovolémico.
* **Contenido clave:**
  - Presión directa mantenida con apósito durante mínimo 5-10 minutos.
  - Criterio de uso de torniquete: sangrado arterial pulsátil en extremidades incontrolable por compresión.
  - Colocación 5-7 cm por encima de la herida y anotación indeleble de la hora de aplicación.

### Bloque 3: Soporte Vital Básico (RCP y Atragantamiento)
* **Objetivo:** Mantener la oxigenación cerebral en parada cardiorrespiratoria o asfixia.
* **Contenido clave:**
  - Secuencia RCP: 30 compresiones torácicas a 100-120 cpm (profundidad 5-6 cm) seguidas de 2 ventilaciones (o solo compresiones continuas).
  - Atragantamiento: 5 golpes interescapulares firmes con el talón de la mano alternados con 5 compresiones abdominales hacia dentro y hacia arriba (Heimlich).

### Bloque 4: Termorregulación y Climatología Extrema en Cádiz
* **Objetivo:** Actuación ante golpes de calor por viento de Levante o frío en la sierra.
* **Contenido clave:**
  - Golpe de calor: sombra inmediata, compresas frescas en cuello, axilas e ingles, hidratación solo si está consciente.
  - Hipotermia: manta térmica con la cara plateada hacia dentro, ropa seca y bebidas calientes azucaradas (nunca alcohol).

### Bloque 5: Toxicología por Picaduras y Mordeduras
* **Objetivo:** Tratamiento específico según la naturaleza bioquímica de cada toxina.
* **Contenido clave:**
  - Pez araña: inmersión inmediata en agua caliente (40-45 °C durante 30-60 min) por ser toxina termolábil.
  - Carabela portuguesa / Medusas: lavado exclusivo con agua marina o vinagre; no usar agua dulce ni frotar.
  - Víbora hocicuda: inmovilización por debajo del corazón; jamás sajar, succionar ni torniquetear.

### Bloque 6: Supervivencia, Desorientación y Señales de Socorro
* **Objetivo:** Guiar al usuario desorientado para sobrevivir y facilitar su rescate.
* **Contenido clave:**
  - Protocolo S.T.O.P. (Stop, Think, Observe, Plan).
  - Señal internacional de socorro: 6 señales acústicas/luminosas por minuto con 1 minuto de pausa.
  - Señalización hacia helicópteros de salvamento (cuerpo en 'Y' para YES/Auxilio).
  - Potabilización de emergencia: ebullición o 2 gotas de lejía apta para consumo por litro.

---

## 4. Implementación Técnica Asociada

* **Módulo conector:** `src/updater/sources/primeros_auxilios_avanzado.py`
* **Clase conector:** `PrimerosAuxiliosAvanzadoSource`
* **Método de adquisición:** `manual_validado`
* **Comando manual de actualización:**
  ```bash
  python3 scripts/actualizar_fuente.py --fuente primeros-auxilios-avanzado
  ```

---

## 5. Historial de Revisiones

| Versión | Fecha | Autor / Revisor | Descripción del Cambio |
| :---: | :---: | :--- | :--- |
| `1.0.0` | `2026-08-27` | `equipo_sanitario_emergencias` | Corpus inicial validado: 13 fragmentos de soporte vital, traumatología, picaduras y protocolo STOP. |
