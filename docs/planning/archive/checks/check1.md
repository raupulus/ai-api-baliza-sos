# Informe de Auditoría: Backend Asistente Emergencia Offline

Tras realizar un análisis profundo del código implementado en `src/`, la configuración `env.py` y los scripts de despliegue en `deploy/`, he detectado varios problemas críticos que podrían comprometer la estabilidad y seguridad del sistema, especialmente considerando las restricciones de hardware (Raspberry Pi 4 de 4 GB).

Aquí tienes la lista detallada de vulnerabilidades, cuellos de botella y puntos de fallo encontrados:

## 1. Arquitectura y Concurrencia (Crítico)

**Bloqueo del *Event Loop* en FastAPI**
En `src/api/pipeline.py`, el método principal `responder` está definido como `async def`. Sin embargo, en su interior ejecuta llamadas totalmente **síncronas** y bloqueantes:
- `retrieval.buscar(...)` llama internamente a `get_embedder().embed_query()`.
- La librería `fastembed` usa ONNX Runtime de forma local para calcular vectores. Este es un proceso fuertemente acoplado a la CPU que tarda cientos de milisegundos y **bloquea completamente el hilo de ejecución principal** de Python.
- **Consecuencia:** Mientras se calcula el embedding de una solicitud, el servidor queda totalmente congelado, incapaz de atender otras solicitudes, responder al endpoint `/health` o gestionar tareas en segundo plano.

**Bloqueo Síncrono de Base de Datos**
La función `retrieval.buscar()` utiliza un context manager síncrono (`with cursor() as cur:`) basado en `psycopg` regular. Al igual que con los embeddings, esto agrava el bloqueo del bucle de eventos asíncronos de FastAPI.

**Recomendación:** Mover todo el procesamiento RAG (Embedding + Base de datos) y la generación del prompt a funciones bloqueantes clásicas (`def`) y delegar su ejecución a un `ThreadPool` de FastAPI (`run_in_threadpool`), o reescribir la interacción de la BD usando `psycopg.AsyncConnectionPool` y ejecutar la carga de embeddings bajo `asyncio.to_thread()`.

## 2. Memoria y Recursos (Riesgo de OOM)

**Protección de Concurrencia Incompleta**
En `src/api/concurrency.py`, hay un semáforo (`inference_semaphore`) para limitar a `1` la concurrencia del LLM (`llm.generate_async`). Sin embargo, ¡el cálculo del *embedding* ocurre **antes** y no está protegido por este semáforo!
- **Consecuencia:** Si entran ráfagas de consultas (ej. desde Meshtastic), el sistema cargará o ejecutará instancias de evaluación ONNX (`fastembed`) en paralelo consumiendo toda la RAM libre. Peor aún, mientras una petición espera al `llama-server`, FastAPI seguirá ejecutando los embeddings de las otras peticiones en paralelo con el LLM, forzando la memoria al límite de los 4GB y provocando un fallo por **Out Of Memory (OOM)**.

**Recomendación:** El semáforo debe abarcar *toda* la sección de procesamiento local pesado. El cálculo del embedding (`get_embedder().embed_query(...)`) y la generación posterior con LLM deben ocurrir estrictamente dentro del mismo bloque del semáforo.

## 3. Manejo de Errores y Resiliencia

**Falta de Reintentos en el LLM (`llama-server`)**
En `src/api/llm_client.py` el cliente HTTP configurado para interactuar con `llama-server` ejecuta un único intento. Si falla o da timeout, no reintenta. En un entorno ajustado, una pausa temporal del servidor (ej. Garbage Collection) puede rechazar la conexión. Se deben implementar reintentos con *backoff*, tal como se hace en el componente `updater`.

**Healthcheck Frágil**
El endpoint `/health` utiliza importación perezosa de librerías y hace uso del pool de base de datos síncrono. En arranques fríos o cuando la CPU está saturada, un simple timeout en la BD daría como fallido el estado general del bot de forma prematura.

**Inicialización Inestable de PostgreSQL**
En el servicio SystemD (`deploy/systemd/postgresql-local.service`), si el directorio definido en `DB_DATA_DIR` no ha sido inicializado por primera vez con `init_cluster.sh`, `pg_ctl` fallará en un bucle infinito intentando iniciar la base de datos local.

## 4. Seguridad y Vulnerabilidades

**Vulnerabilidad de *Timing Attack* en el Token de API**
En `src/api/app.py`, la autenticación se evalúa con una comparación de cadenas simple: `if authorization != esperado:`. Un atacante podría realizar ataques de tiempo (timing attacks) para adivinar el token Bearer analizando el tiempo que tarda la API en responder.
- **Recomendación:** Usar la función de tiempo constante `secrets.compare_digest(authorization, esperado)` de la biblioteca estándar de Python.

**Tolerancia a Configuración Insegura por Defecto**
Actualmente, si el token de API (`API_AUTH_TOKEN`) mantiene su valor por defecto `"CAMBIA_ESTE_TOKEN"`, el sistema simplemente emite un warning (`_log.warning(...)`) en `src/api/app.py` y permite que el servidor arranque. Si alguien se olvida de configurarlo, el sistema quedará expuesto al público con una clave conocida.
- **Recomendación:** El bot debe abortar su inicio (`sys.exit` o lanzar una excepción fatal) si detecta que la clave de producción es la que viene por defecto.

## 5. Conclusión y Desviaciones de `AGENTS.md`

En términos generales, el proyecto respeta los lineamientos documentados (uso de entorno, modelo dinámico, y el RAG con Postgres). Sin embargo, se incumple indirectamente la regla fundamental de **"Hardware mínimo: RPi4 4 GB"**, ya que el manejo actual de la concurrencia (problemas 1 y 2) saturará irremediablemente el dispositivo y el sistema colapsará ante múltiples solicitudes concurrentes.

El backend es funcional en pruebas secuenciales de un solo hilo, pero requiere refactorización asíncrona urgente antes de su uso real.

---

## Evaluación de la auditoría (revisión)

Tras revisar el código, **la mayoría de los hallazgos son reales y se han
corregido**. Matices por punto:

- **1 (event loop) y 2 (semáforo/embedding): reales.** Correctos y relacionados:
  el embedding (ONNX) y la BD síncrona corrían en el bucle, y el semáforo no
  cubría el embedding. Corregido de una vez.
- **3a (reintentos LLM): válido con matiz.** Se reintenta **solo ante errores de
  conexión**, nunca ante timeouts (un timeout reintentado excedería el
  presupuesto de 5 min del cliente).
- **3b (healthcheck frágil): menor/subjetivo.** No es un bug; aun así se mejora
  sacando la comprobación del event loop. Que un timeout de BD marque "no sano"
  es el comportamiento esperado de un healthcheck.
- **3c (bucle de fallo de PostgreSQL): real.** Corregido.
- **4a (timing attack) y 4b (token por defecto): reales.** Corregidos.
- La conclusión de "colapso ante concurrencia" estaba algo dramatizada para el
  escenario real ("pocos clientes" + semáforo ya existente), pero el fondo
  técnico era correcto y se ha reforzado.

Veredicto: **no había hallazgos equivocados**; uno (3b) estaba sobredimensionado.

## Checklist de correcciones aplicadas

- [x] **1 · Event loop**: `pipeline.responder` ejecuta el trabajo pesado con
  `run_in_threadpool`; el bucle de FastAPI queda libre (`src/api/pipeline.py`).
- [x] **2 · Semáforo completo**: el semáforo de inferencia ahora envuelve
  embedding + BD + generación (serialización estricta, protege la RAM).
- [x] **3a · Reintentos LLM**: `LLMClient` reintenta con backoff solo
  `ConnectError`; los timeouts no se reintentan (`src/api/llm_client.py`).
- [x] **3b · Healthcheck**: `/health` pasa a `async` y delega BD/LLM a
  threadpool para no bloquear el bucle (`src/api/app.py`).
- [x] **3c · PostgreSQL systemd**: `ExecStartPre` inicializa el clúster si falta
  `PG_VERSION`, evitando el bucle de fallo
  (`deploy/systemd/postgresql-local.service`).
- [x] **4a · Timing attack**: autenticación con `secrets.compare_digest`
  (`src/api/app.py`).
- [x] **4b · Token inseguro**: si `API_AUTH_TOKEN` es el de por defecto, la API
  responde 503 salvo `API_ALLOW_INSECURE_TOKEN=true` (dev); aviso CRÍTICO al
  arrancar. Nueva variable en `env.example.py`/`env.py` y `config.py`.
- [x] **Pruebas**: `tests/test_llm_client.py` (reintentos) y comprobación de
  token inseguro en `tests/test_config.py`. Verificado en sandbox (sintaxis +
  lógica de reintentos con stub de httpx).

### Pendiente (mejoras menores, no bloqueantes)

- [ ] Migrar la BD a `psycopg.AsyncConnectionPool` si en el futuro se quiere
  solapar E/S (hoy innecesario: el threadpool + semáforo ya resuelven el bloqueo
  para "pocos clientes").
- [ ] Métricas ligeras de latencia/uso de RAM (módulo 07, fase 4).
