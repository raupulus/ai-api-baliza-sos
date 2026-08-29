# Contrato de la API HTTP — Asistente de Emergencias (Cádiz)

> **Versión del Contrato:** 1.2.0  
> **Última actualización:** 2026-08-27  
> **Ámbito:** Especificación técnica formal de integración HTTP REST.  
> **Documento Autónomo y Exportable:** Este archivo puede copiarse directamente a repositorios de clientes externos (bots de Telegram, pasarelas Meshtastic/LoRa, frontends o microservicios) como especificación técnica completa y definitiva de la API.

---

[← Volver al Índice de Documentación Técnica](README.md)

---

## 1. Información General y Puertos

| Servicio | Puerto Host / URL por defecto | Descripción |
| :--- | :--- | :--- |
| **API Backend** | `http://<IP>:8870` | Endpoints REST de consulta e inferencia RAG. |
| **Interfaz Web** | `http://<IP>:8443` | Chat interactivo de pruebas en navegador. |
| **LLM Server** | `http://<IP>:8869` | `llama-server` nativo (`llama.cpp`), uso interno. |
| **Base de Datos**| `localhost:5433` | PostgreSQL 17 + pgvector (interno en Docker `5432`). |

* Formato de intercambio de datos: **JSON (`application/json`)**
* Codificación: **UTF-8**
* Idioma de respuesta: **Español (`es`)**

---

## 2. Autenticación

Todas las peticiones a endpoints protegidos requieren una cabecera HTTP `Authorization` con un Bearer token precompartido:

```http
Authorization: Bearer <API_AUTH_TOKEN>
```

* El token se define en la variable de entorno `API_AUTH_TOKEN` (archivo `.env`).
* Si el token es inválido o no se proporciona, la API devuelve código de estado **`401 Unauthorized`**.
* El endpoint de diagnóstico `/health` es público y **no requiere autenticación**.

---

## 3. Endpoints

### 3.1. Diagnóstico del Sistema (`GET /health`)

Comprueba el estado de los cuatro subsistemas críticos del backend (base de datos relacional, motor vectorial, servidor LLM y motor de embeddings ONNX).

* **Método:** `GET`
* **Ruta:** `/health`
* **Autenticación:** No requerida.

#### Respuesta Exitosa (`200 OK`)
```json
{
  "ok": true,
  "db": true,
  "llm": true,
  "embeddings": true
}
```

#### Campos de Respuesta
| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `ok` | `boolean` | `true` si todos los subsistemas esenciales (`db` y `llm`) están operativos. |
| `db` | `boolean` | `true` si la conexión con PostgreSQL y pgvector responde. |
| `llm` | `boolean` | `true` si el servidor llama.cpp (`:8869`) está listo para inferencias. |
| `embeddings` | `boolean` | `true` si el motor de embeddings FastEmbed/ONNX está inicializado. |

---

### 3.2. Consulta de Emergencia / RAG (`POST /v1/consulta`)

Procesa una pregunta o situación de emergencia en lenguaje natural, recupera el contexto local verificado mediante búsqueda vectorial semántica y genera una respuesta concisa optimizada para enlaces de baja velocidad (RF/Meshtastic).

* **Método:** `POST`
* **Ruta:** `/v1/consulta`
* **Autenticación:** Requerida (`Authorization: Bearer <TOKEN>`).
* **Content-Type:** `application/json`

#### Estructura de Petición (`ConsultaRequest`)
```json
{
  "consulta": "Me ha picado una medusa en la playa de Zahara, ¿qué hago?",
  "ubicacion": "Zahara de los Atunes",
  "cliente": "meshtastic-node-!2a4b6c8d",
  "id_conversacion": "meshtastic-node-!2a4b6c8d",
  "reset_conversacion": false,
  "categoria_sugerida": "fauna"
}
```

#### Parámetros de Entrada
| Parámetro | Tipo | Requerido | Descripción |
| :--- | :--- | :---: | :--- |
| `consulta` | `string` | **Sí** | Pregunta o situación en lenguaje natural (mín. 1 carácter, máx. 2000 caracteres). |
| `id_conversacion` | `string` | No | Identificador único de la conversación para mantener memoria multi-turno (hasta 20 turnos con compactación por IA). Se elimina tras 1 hora de inactividad. |
| `reset_conversacion` | `boolean` | No | Si es `true`, archiva y limpia el contexto previo de este `id_conversacion` antes de responder. |
| `cliente` | `string` | No | Identificador del nodo o usuario emisor (ej. `"telegram:123456"`, `"meshtastic:!2a4b6c8d"`). Sirve de fallback para `id_conversacion` si este no se envía. |
| `ubicacion` | `object` o `string` | No | Ubicación aproximada, coordenadas GPS o municipio de la provincia de Cádiz. |
| `categoria_sugerida`| `string` | No | Filtro temático opcional (`"primeros_auxilios"`, `"fauna"`, `"flora"`, `"geografia"`, `"supervivencia"`, `"cultura_historia"`). |

---

#### Estructura de Respuesta Exitosa (`200 OK`)
```json
{
  "ok": true,
  "mensajes": [
    "Sal del agua, no frotes ni uses agua dulce, retira restos con una tarjeta y aplica agua de mar caliente. Info orientativa. Llama al 112."
  ],
  "categoria": "fauna",
  "confianza": 0.744,
  "fuentes": [
    {
      "titulo": "Cruz Roja (semilla, validado)",
      "fecha": "2026-08-27",
      "url": null
    }
  ],
  "modelo": "qwen2.5-3b-instruct-q4_k_m",
  "tiempo_ms": 8699,
  "truncado": false
}
```

#### Campos de Respuesta (`ConsultaResponse`)
| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `ok` | `boolean` | Indica si la consulta se procesó correctamente. |
| `mensajes` | `list[string]` | **Lista de 1 a 3 mensajes**. Cada mensaje mide estrictamente **$\le 200$ bytes UTF-8** para ajustarse limpiamente al buffer útil de radio en clientes LoRa / Meshtastic. Limpio de metadatos o citas de fuentes. |
| `categoria` | `string \| null` | Categoría temática dominante identificada por el RAG (`"fauna"`, `"primeros_auxilios"`, `"supervivencia"`, `"orientacion"`, etc.). `null` si no hubo match. |
| `confianza` | `float` | Puntuación de similitud coseno máxima obtenida en la base vectorial (rango `0.0` a `1.0`). Si no supera el umbral, vale `0.0`. |
| `fuentes` | `list[object]` | Lista de fuentes curadas utilizadas como contexto (`titulo`, `fecha`, `url`). |
| `aviso` | `string \| null` | Descargo legal o aviso de emergencia (ej. *"Info orientativa. Llama al 112."*). Se devuelve como metadato independiente fuera de `mensajes` para no consumir ancho de banda en LoRa. |
| `modelo` | `string` | Nombre del modelo LLM que generó la respuesta (ej. `"qwen2.5-3b-instruct-q4_k_m"`). |
| `tiempo_ms` | `integer` | Latencia total de inferencia en el servidor en milisegundos. |
| `truncado` | `boolean` | `true` si la respuesta del LLM tuvo que ser recortada para respetar el límite de 3 mensajes de 200 bytes UTF-8. |
| `turnos_memoria` | `integer \| null` | Número de turnos conversacionales activos conservados en la memoria para este cliente. |
| `compactado` | `boolean \| null` | `true` si en este turno se ejecutó una compactación / resumen con IA del historial previo. |
| `fragmentos_rag` | `integer \| null` | Número de fragmentos documentales relevantes recuperados de la base vectorial `pgvector`. |

---

### 3.3. Reseteo de Conversación (`POST /v1/conversacion/reset`)

Limpia la memoria y el contexto de un identificador de conversación o cliente para iniciar un nuevo diálogo limpio sin mezclar temas previos.

* **Método:** `POST`
* **Ruta:** `/v1/conversacion/reset`
* **Autenticación:** Requerida (`Authorization: Bearer <TOKEN>`).
* **Content-Type:** `application/json`

#### Estructura de Petición (`ResetConversacionRequest`)
```json
{
  "id_conversacion": "meshtastic-node-!2a4b6c8d"
}
```

#### Estructura de Respuesta Exitosa (`200 OK`)
```json
{
  "ok": true,
  "mensaje": "Conversación reseteada correctamente.",
  "id_conversacion": "meshtastic-node-!2a4b6c8d"
}
```

---

## 4. Reglas de Negocio y Garantías de Seguridad

1. **Memoria Conversacional y Aislamiento de Clientes:**
   * La API mantiene conversaciones aisladas por cada `id_conversacion` o `cliente`.
   * **Ventana de 20 turnos:** Se guardan hasta 20 preguntas y 20 respuestas completas.
   * **Compactación con IA:** Al superar este umbral, el sistema compacta con el LLM los turnos más antiguos en un resumen sintético y conserva íntegros los últimos 10 turnos.
   * **Expiración a la hora (TTL = 3600 s):** La memoria se borra automáticamente si transcurren 60 minutos sin recibir ningún mensaje con ese identificador.
   * **Persistencia en Base de Datos:** Todas las conversaciones y mensajes quedan archivados en las tablas `conversaciones` y `mensajes_conversacion` de PostgreSQL para auditoría y trazabilidad.

1. **Restricción de Tamaño para Radiofrecuencia (LoRa / Meshtastic):**
   * Longitud máxima por elemento de `mensajes`: **200 bytes UTF-8**. Se calibra para el espacio útil estricto disponible en transmisiones LoRa con Meshtastic, evitando desbordamientos de buffer por tildes, signos o caracteres multibyte.
   * **Metadatos fuera de los mensajes:** Todo descargo legal (`aviso`), fuentes y categorización viajan en campos JSON separados. `mensajes` contiene exclusivamente el texto limpio de ayuda para radiofrecuencia.
   * Cantidad máxima de elementos: **3 mensajes**.
   * Los clientes de radio pueden transmitir cada elemento como un paquete individual secuencial (`[1/2]`, `[2/2]`).
2. **Garantía Anti-Alucinación:**
   * Si la consulta no coincide con el corpus validado de Cádiz con una similitud coseno $\ge 0.42$, el sistema **no inventa información**.
   * Devuelve `confianza: 0.0`, `fuentes: []` y un mensaje estándar:
     `"No dispongo de información fiable. Recomiendo llamar al 112 si es urgente."`
3. **Aviso Médico Obligatorio:**
   * Toda respuesta clasificada como primeros auxilios o especie peligrosa incluye obligatoriamente el descargo de responsabilidad:
     `"Info orientativa. Llama al 112."`
4. **Semáforo de Inferencia:**
   * La Raspberry Pi 5 procesa **1 inferencia pesada a la vez** para garantizar estabilidad de RAM y dejar CPU disponible para otras tareas. Si entran peticiones concurrentes, esperan ordenadamente en cola (timeout de espera de 280 s).

---

## 5. Códigos de Estado y Errores

En caso de error, el cuerpo de respuesta sigue el esquema estándar:
```json
{
  "detail": "Descripción detallada del error"
}
```

| Código HTTP | Motivo | Ejemplo |
| :--- | :--- | :--- |
| `200 OK` | Consulta procesada con éxito. | Ver ejemplo en sección 3.2. |
| `400 Bad Request` | Petición mal formada o payload no válido. | `{"detail": "La consulta no puede estar vacía"}` |
| `401 Unauthorized` | Token Bearer ausente, incorrecto o inseguro. | `{"detail": "Token inválido o no suministrado"}` |
| `422 Unprocessable` | Error de validación de tipos Pydantic. | Campo requerido ausente. |
| `502 Bad Gateway` | Fallo de comunicación entre la API y el LLM o PostgreSQL. | `{"detail": "El servidor LLM no responde"}` |
| `503 Service Unavail`| Sistema ocupado o timeout de inferencia agotado. | `{"detail": "Cola de inferencia llena"}` |

---

## 6. Ejemplos Prácticos de Integración

### 6.1. cURL (Bash)
```bash
TOKEN="TU_API_AUTH_TOKEN"
API_URL="http://172.18.1.121:8870/v1/consulta"

curl -s -X POST "$API_URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "consulta": "Que hacer ante un golpe de calor?",
    "cliente": "curl-test"
  }'
```

### 6.2. Python (`httpx`)
```python
import httpx

API_URL = "http://172.18.1.121:8870/v1/consulta"
TOKEN = "TU_API_AUTH_TOKEN"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "consulta": "Picadura de medusa que hago",
    "cliente": "python-client"
}

with httpx.Client(timeout=60.0) as client:
    response = client.post(API_URL, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()

    print(f"Modelo: {data['modelo']} (Tiempo: {data['tiempo_ms']} ms)")
    for i, mensaje in enumerate(data["mensajes"], 1):
        print(f"[{i}/{len(data['mensajes'])}] ({len(mensaje)} chars): {mensaje}")
```

### 6.3. JavaScript (`fetch` para Navegador o NodeJS)
```javascript
const res = await fetch('http://172.18.1.121:8870/v1/consulta', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer TU_API_AUTH_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    consulta: 'Como conseguir agua potable en una playa?'
  })
});

const data = await res.json();
console.log('Mensajes recibidos:', data.mensajes);
```

### 6.4. Pasarela Meshtastic (Python con Memoria y Comando Reset)
```python
import httpx

API_URL = "http://172.18.1.121:8870"
TOKEN = "MI_API_AUTH_TOKEN"

def on_meshtastic_packet(packet, interface):
    texto = packet.get("decoded", {}).get("text", "").strip()
    sender_id = packet.get("fromId")  # Ej. '!2a4b6c8d'

    if not texto or not sender_id:
        return

    # Comando para resetear contexto conversacional
    if texto.lower() in ("/reset", "!reset", "nueva"):
        httpx.post(
            f"{API_URL}/v1/conversacion/reset",
            headers={"Authorization": f"Bearer {TOKEN}"},
            json={"id_conversacion": f"meshtastic:{sender_id}"},
            timeout=10.0
        )
        interface.sendText("Conversación reiniciada.", destinationId=sender_id)
        return

    # Consulta habitual: la API asocia automáticamente el historial por id_conversacion
    res = httpx.post(
        f"{API_URL}/v1/consulta",
        headers={"Authorization": f"Bearer {TOKEN}"},
        json={
            "consulta": texto,
            "id_conversacion": f"meshtastic:{sender_id}",
            "cliente": f"meshtastic:{sender_id}"
        },
        timeout=180.0
    ).json()

    # Cada elemento de mensajes mide obligatoriamente <= 200 bytes UTF-8 (entra limpio en LoRa MTU)
    for msg in res.get("mensajes", []):
        interface.sendText(text=msg, destinationId=sender_id)
```

---

[← Volver al Índice de Documentación Técnica](README.md)

