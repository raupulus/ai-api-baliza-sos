# Contrato de la API HTTP — Asistente de Emergencias (Cádiz)

Este documento define la **especificación técnica formal y contrato de integración** de la API HTTP del Asistente de Emergencias y Supervivencia.

Está diseñado para que cualquier cliente externo (**pasarelas Meshtastic/LoRa**, **bots de Telegram**, interfaces web, scripts o clientes móviles) pueda interactuar con el backend de manera predecible, segura y estandarizada.

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
  "categoria_sugerida": "fauna"
}
```

#### Parámetros de Entrada
| Parámetro | Tipo | Requerido | Descripción |
| :--- | :--- | :---: | :--- |
| `consulta` | `string` | **Sí** | Pregunta o situación en lenguaje natural (mín. 3 caracteres, máx. 500 caracteres). |
| `ubicacion` | `string` | No | Ubicación aproximada o municipio de la provincia de Cádiz (ej. `"Tarifa"`, `"Grazalema"`). |
| `cliente` | `string` | No | Identificador del cliente para trazabilidad y métricas (ej. `"telegram:123456"`, `"meshtastic:!abcd1234"`). |
| `categoria_sugerida`| `string` | No | Filtro temático opcional (`"primeros_auxilios"`, `"fauna"`, `"geografia"`, `"supervivencia"`). |

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
| `mensajes` | `list[string]` | **Lista de 1 a 3 mensajes**. Cada mensaje mide estrictamente **$\le 250$ caracteres** para ajustarse a los paquetes LoRa / Meshtastic. |
| `categoria` | `string \| null` | Categoría temática dominante identificada por el RAG (`"fauna"`, `"primeros_auxilios"`, `"supervivencia"`, `"orientacion"`, etc.). `null` si no hubo match. |
| `confianza` | `float` | Puntuación de similitud coseno máxima obtenida en la base vectorial (rango `0.0` a `1.0`). Si no supera el umbral, vale `0.0`. |
| `fuentes` | `list[object]` | Lista de fuentes curadas utilizadas como contexto (`titulo`, `fecha`, `url`). |
| `modelo` | `string` | Nombre del modelo LLM que generó la respuesta (ej. `"qwen2.5-3b-instruct-q4_k_m"`). |
| `tiempo_ms` | `integer` | Latencia total de inferencia en el servidor en milisegundos. |
| `truncado` | `boolean` | `true` si la respuesta del LLM tuvo que ser recortada para respetar el límite de 3 mensajes de 250 caracteres. |

---

## 4. Reglas de Negocio y Garantías de Seguridad

1. **Restricción de Tamaño para Radiofrecuencia (LoRa / Meshtastic):**
   * Longitud máxima por elemento de `mensajes`: **250 caracteres**.
   * Cantidad máxima de elementos: **3 mensajes**.
   * Los clientes de radio pueden transmitir cada elemento como un paquete individual secuencial (`[1/2]`, `[2/2]`).
2. **Garantía Anti-Alucinación:**
   * Si la consulta no coincide con el corpus validado de Cádiz con una similitud coseno $\ge 0.55$, el sistema **no inventa información**.
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

### 6.4. Pasarela Meshtastic (Pseudo-código / Python)
```python
# Cuando un nodo Meshtastic envía un mensaje directo al bot:
def on_meshtastic_packet(packet, interface):
    texto_recibido = packet['decoded']['text']
    sender_id = packet['fromId']

    # Consultar la API del bot
    res = httpx.post(
        "http://172.18.1.121:8870/v1/consulta",
        headers={"Authorization": "Bearer MI_TOKEN"},
        json={"consulta": texto_recibido, "cliente": f"meshtastic:{sender_id}"},
        timeout=120.0
    ).json()

    # Cada elemento de data['mensajes'] mide <= 250 caracteres
    for msg in res["mensajes"]:
        interface.sendText(text=msg, destinationId=sender_id)
```
