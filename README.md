# bot-ia-auxiliar

Backend de un **asistente de emergencia y supervivencia offline** para la
provincia de **Cádiz (España)**, ejecutable en una **Raspberry Pi 4 (4 GB)**
sin conexión a internet. Atiende consultas de IA (LLM pequeño local + RAG)
provenientes de clientes externos (bots de **Telegram** y **Meshtastic/LoRa**).

> Estado: **planificación**. Ver [`docs/planning/initial_plan/00_index.md`](docs/planning/initial_plan/00_index.md).

## Qué hace

Una persona perdida o en apuros envía una consulta por Meshtastic/Telegram
(p. ej. *"medusa azul en la playa, dolor fuerte, qué hago"* o *"estoy perdido,
veo un faro y dunas a mi izquierda"*). El backend recupera contexto local
verificado (fauna, geografía, primeros auxilios, orientación) y el LLM redacta
una respuesta **breve en español**: hasta **3 mensajes de 250 caracteres**,
devuelta siempre como **JSON**.

## Arquitectura (dos servicios)

| Servicio | Carpeta | Función |
|----------|---------|---------|
| **API del bot** | `src/api` | Recibe la consulta, hace RAG, llama al LLM, devuelve JSON breve. |
| **Actualizador de contexto** | `src/updater` | Ingesta/scraping de fuentes, normaliza, checkpoint humano, indexa en la base vectorial. |

Ambos se apoyan en `llama-server` (llama.cpp) y en PostgreSQL+pgvector,
desplegados de forma **nativa con systemd**.

## Stack

- **LLM:** llama.cpp (`llama-server`) · modelo por env (def. Qwen2.5-1.5B-Instruct Q4_K_M)
- **Embeddings:** multilingual-e5-small (384 dim) vía fastembed
- **Vector store:** PostgreSQL + pgvector (clúster local en `data/`)
- **API:** FastAPI + Uvicorn
- **SO objetivo:** Raspberry Pi OS / Linux · **sin Docker**

## Estructura

```
src/        Código (common, api, updater)
docs/info/  Documentación técnica y decisiones
docs/planning/initial_plan/  Plan por módulos (fases + checklists)
deploy/     Unidades systemd y scripts de PostgreSQL
scripts/    Utilidades de operación
data/       Directorio de trabajo (no trackeado)
```

## Configuración

```bash
cp env.example.py env.py   # ajusta valores reales (no se trackea)
```

Todo lo geográfico (`PROVINCIA`, `BBOX`...) y el modelo (`LLM_MODEL_PATH`)
se controlan desde `env.py`. Cambiar de provincia o de modelo no requiere tocar
código.

## Documentación

- Visión y requisitos: [`docs/info/01-vision-requisitos.md`](docs/info/01-vision-requisitos.md)
- Arquitectura: [`docs/info/02-arquitectura.md`](docs/info/02-arquitectura.md)
- Decisiones de stack: [`docs/info/03-decisiones-stack.md`](docs/info/03-decisiones-stack.md)
- Presupuesto de recursos (RAM): [`docs/info/04-presupuesto-recursos.md`](docs/info/04-presupuesto-recursos.md)
- Contrato de la API y formato RAG: [`docs/info/05-contratos-datos.md`](docs/info/05-contratos-datos.md)
- Hardware objetivo, modelos y paralelismo: [`docs/info/07-hardware-objetivo.md`](docs/info/07-hardware-objetivo.md)
- Guías de SSD (RPi4 / RPi5): [`docs/guias/`](docs/guias/README.md)
- Guía para agentes de IA: [`AGENTS.md`](AGENTS.md)
