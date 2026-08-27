# docs/info — Documentación Técnica del Asistente

> **Última actualización:** 2026-08-27  
> **Ámbito:** Arquitectura, especificaciones técnicas, infraestructura y contratos de datos.

Este directorio constituye la **fuente única de verdad técnica** para la arquitectura, configuración, puertos y componentes del asistente.

---

## 1. Índice de Documentos Técnicos

| Documento | Descripción y Ámbito Técnico |
| :--- | :--- |
| **[`01-vision-requisitos.md`](01-vision-requisitos.md)** | Visión del asistente offline, casos de uso de emergencia en Cádiz, restricciones de radiofrecuencia (LoRa/Meshtastic) y requisitos no funcionales. |
| **[`02-arquitectura.md`](02-arquitectura.md)** | Arquitectura de contenedores Docker (`bot-api`, `bot-llm`, `bot-db`, `bot-web`), red interna `bot-net`, flujo entre servicios y puertos asignados. |
| **[`03-decisiones-stack.md`](03-decisiones-stack.md)** | Justificación técnica de las decisiones de ingeniería: `llama.cpp`, fastembed ONNX, PostgreSQL 17 + pgvector y FastAPI. |
| **[`04-presupuesto-recursos.md`](04-presupuesto-recursos.md)** | Presupuesto estricto de memoria RAM, semáforo de concurrencia para inferencia y control térmico en Raspberry Pi 4 (4GB) y Pi 5 (8GB). |
| **[`05-contratos-datos.md`](05-contratos-datos.md)** | Modelos de dominio internos (`Fragmento`, `Categoria`), tablas relacionales (`conversaciones`, `mensajes_conversacion`) y hashes de contenido. |
| **[`06-estado-implementacion.md`](06-estado-implementacion.md)** | Estado de ejecución por módulos, matriz de componentes completados y hoja de ruta. |
| **[`07-hardware-objetivo.md`](07-hardware-objetivo.md)** | Ficha técnica del hardware (RPi4 y RPi5 8GB), aceleradora NPU Hailo-8, particionado de almacenamiento en SSD y configuraciones EEPROM. |
| **[`08-contrato-api.md`](08-contrato-api.md)** | Especificación formal del contrato de la API HTTP REST (`/v1/consulta`, `/v1/conversacion/reset`, `/health`), formatos JSON, códigos de estado y ejemplos. |

---

## 2. Enlaces Relacionados

* **Conocimiento del RAG:** Consulta [`../rag/README.md`](../rag/README.md) para ver las fichas detalladas de cada fuente de datos (primeros auxilios, flora/fauna, municipios, fiestas e historia).
* **Guías de Operación y Hardware:** Consulta [`../guias/README.md`](../guias/README.md) para configuraciones específicas de disco SSD.
* **Guía para Agentes de IA:** Consulta [`../../AGENTS.md`](../../AGENTS.md) para conocer las normas de trabajo en el repositorio.
