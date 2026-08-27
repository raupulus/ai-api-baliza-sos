# 07 · Hardware objetivo, modelos y paralelismo

> **Última actualización:** 2026-08-27  
> **Ámbito:** Especificaciones de hardware (RPi4 / RPi5), NPU Hailo-8 y almacenamiento SSD.

[← Volver al Índice de Documentación Técnica](README.md)

---

Completa la información de hardware del proyecto: placas soportadas, modelo
recomendado para cada una y cuántas consultas (inferencias) puede atender cada
configuración. Complementa el presupuesto de RAM de
`04-presupuesto-recursos.md` y las decisiones de `03-decisiones-stack.md`.

## 1. Placas soportadas

- **Mínimo soportado: Raspberry Pi 4 (4 GB).** Es el objetivo de diseño: si algo
  funciona aquí, funciona en todo lo superior.
- **Recomendado / preferible: Raspberry Pi 5 (8 GB o 16 GB).** CPU ~3× más
  rápida y más RAM permiten modelos mejores y/o atender más consultas.

Todo es **dinámico por `env.py`**: cambiar de placa = ajustar `LLM_MODEL_PATH`,
`LLM_THREADS`, `LLM_CONTEXT_SIZE` y, si procede, `API_MAX_CONCURRENT_INFERENCES`.
No se toca código.

### Comparativa de CPU

| Placa | SoC | CPU | Núcleos | Almacenamiento rápido |
|-------|-----|-----|---------|-----------------------|
| RPi 4 | BCM2711 | Cortex‑A72 @ 1.5–1.8 GHz | 4 | SSD por **USB 3.0** (no hay PCIe) |
| RPi 5 | BCM2712 | Cortex‑A76 @ 2.4 GHz (~3×) | 4 | **NVMe por PCIe** (M.2 HAT+) o USB 3.0 |

Guías de almacenamiento: `../guias/ssd-raspberry-pi-4.md` y
`../guias/ssd-raspberry-pi-5.md`. Un SSD es muy recomendable en ambas (PostgreSQL
y modelos sufren con microSD).

## 2. Modelo recomendado por placa

Todos en **GGUF Q4_K_M** (equilibrio tamaño/calidad para CPU). La familia base
es **Qwen2.5‑Instruct** por su buen español; alternativas válidas: Gemma 2,
Llama 3.2.

| Placa · RAM | Modelo recomendado | Pesos aprox. | Alternativa |
|-------------|--------------------|-------------:|-------------|
| RPi 4 · 4 GB | **Qwen2.5‑1.5B‑Instruct** | ~1.1 GB | Qwen2.5‑0.5B (más rápido, menos calidad) |
| RPi 5 · 4 GB | Qwen2.5‑1.5B‑Instruct | ~1.1 GB | Qwen2.5‑3B (va justo) |
| RPi 5 · 8 GB | **Qwen2.5‑3B‑Instruct** | ~2.0 GB | Qwen2.5‑1.5B (si priorizas latencia) |
| RPi 5 · 16 GB | Qwen2.5‑7B‑Instruct | ~4.5 GB | Qwen2.5‑3B (si priorizas concurrencia) |

> Recordatorio del presupuesto de RAM: además del modelo conviven el SO,
> PostgreSQL, los embeddings y el servidor. En 4 GB, un 3B queda al límite; por
> eso el **defecto en RPi4 es 1.5B**.

## 3. Cuántas inferencias en paralelo

Puntos clave que limitan el paralelismo en estas placas:

- **CPU**: ambas tienen **4 núcleos**. Una inferencia bien configurada usa los 4
  (`LLM_THREADS=4`). Atender **N inferencias a la vez** obliga a repartir núcleos
  (`LLM_THREADS≈4/N`), así que **cada respuesta se vuelve más lenta**: el
  paralelismo aumenta el caudal total, no la rapidez individual.
- **RAM**: con `llama-server` y **batching continuo** (`--parallel N`) los
  **pesos del modelo se comparten** entre slots; solo crece el KV‑cache por slot.
  Es la forma eficiente de permitir concurrencia sin duplicar el modelo en RAM.
- **Arquitectura del proyecto**: por defecto `API_MAX_CONCURRENT_INFERENCES=1`
  (semáforo) para proteger la RAM en RPi4. Las peticiones extra **esperan en
  cola** hasta el límite de tiempo del cliente (5 min).

### Recomendación práctica por placa

| Placa · RAM | Modelo | `LLM_THREADS` | Inferencias en paralelo | Cómo activarlo |
|-------------|--------|:-------------:|:-----------------------:|----------------|
| RPi 4 · 4 GB | 1.5B | 4 | **1** (resto en cola) | Valor por defecto |
| RPi 5 · 4 GB | 1.5B | 4 | 1 | Por defecto (CPU ~3× más rápida) |
| RPi 5 · 8 GB | 3B | 4 | **1** (o 2 con 1.5B) | `--parallel 2`, `LLM_THREADS=2`, `API_MAX_CONCURRENT_INFERENCES=2` |
| RPi 5 · 16 GB | 7B | 4 | 1 · (2 con 3B · 2–3 con 1.5B) | `--parallel N`, `LLM_THREADS=4/N`, `API_MAX_CONCURRENT_INFERENCES=N` |

Cómo subir la concurrencia (solo RPi5 con RAM holgada):

1. Arranca `llama-server` con `--parallel N` (N slots, batching continuo).
2. Pon `LLM_THREADS ≈ 4/N` para no sobre‑suscribir la CPU.
3. Sube `API_MAX_CONCURRENT_INFERENCES=N` en `env.py`.

> Para un asistente de **emergencia**, normalmente importa más la **latencia de
> una respuesta rápida** que el caudal. Salvo que esperes ráfagas reales de
> consultas simultáneas (varios nodos Meshtastic a la vez), mantener **N=1 con un
> modelo ágil** suele ser la mejor opción. Sube la concurrencia solo si la
> monitorización muestra cola y hay RAM de sobra.

### Y el actualizador de contexto

El servicio actualizador (ingesta/scraping/embeddings) es intensivo y **no debe
coincidir con los picos** de la API: corre por `systemd timer` de madrugada. En
RPi5 16 GB sí hay margen para solapar actualizador y API ocasionalmente; en
RPi4 4 GB conviene no solaparlos.

## 4. Resumen de elección

- **Tienes RPi4 4 GB**: funciona, con 1.5B y 1 inferencia a la vez. Pon **SSD**.
- **Vas a comprar / preferible**: **RPi5 8 GB** con **NVMe** → 3B con buena
  latencia, margen para todo. Es el punto dulce calidad/precio para el proyecto.
- **Quieres el mejor modelo o concurrencia real**: **RPi5 16 GB** → 7B, o varios
  slots con 1.5B/3B.

## Fuentes

- [Raspberry Pi 5 (producto y variantes de RAM)](https://www.raspberrypi.com/products/raspberry-pi-5/)
- [Tom's Hardware — Raspberry Pi 5 16GB review](https://www.tomshardware.com/raspberry-pi/raspberry-pi-5-16gb-review)
- [llama.cpp server — parallel / continuous batching](https://github.com/ggml-org/llama.cpp/tree/master/tools/server)

---

[← Volver al Índice de Documentación Técnica](README.md)

