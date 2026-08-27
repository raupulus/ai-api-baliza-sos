"""
Configuración de ejemplo del proyecto (plantilla TRACKEADA en git).

Copia este archivo a `env.py` y ajusta los valores:

    cp env.example.py env.py

`env.py` NO se trackea (ver .gitignore). Contiene la configuración real de
cada despliegue. Todos los valores admiten sobreescritura por variable de
entorno real (útil con `EnvironmentFile=` de systemd), de modo que puedes
cambiar el modelo o la provincia sin tocar el código.

Convención: una sola fuente de verdad. El código sólo importa `env.py` a
través de `src/common/config.py`; nunca lee `os.environ` directamente.
"""

import os

# ---------------------------------------------------------------------------
# 1. CONTEXTO GEOGRÁFICO (provincia objetivo, parametrizable)
# ---------------------------------------------------------------------------
# Cambiando estas variables se adapta el sistema a otra provincia sin tocar
# código: condiciona el filtrado de fuentes (GBIF, Overpass, AEMET, IGN...).
PROVINCIA = os.environ.get("PROVINCIA", "Cádiz")
PROVINCIA_SLUG = os.environ.get("PROVINCIA_SLUG", "cadiz")
PAIS = os.environ.get("PAIS", "España")
PAIS_CODIGO_ISO = os.environ.get("PAIS_CODIGO_ISO", "ES")
# Bounding box aprox. de la provincia (min_lon, min_lat, max_lon, max_lat).
# Se usa para acotar consultas geográficas (Overpass, GBIF occurrences).
BBOX = os.environ.get("BBOX", "-6.50,35.95,-5.10,37.05")
# Código GADM / NUTS / código de provincia INE (para filtrar fuentes oficiales).
PROVINCIA_CODIGO_INE = os.environ.get("PROVINCIA_CODIGO_INE", "11")
IDIOMA = os.environ.get("IDIOMA", "es")  # Respuestas del bot: solo español.

# ---------------------------------------------------------------------------
# 2. SERVICIO LLM (llama.cpp / llama-server)
# ---------------------------------------------------------------------------
# El modelo es DINÁMICO: se elige por ruta al fichero GGUF. Cambiar de modelo
# (p. ej. al pasar de RPi4 4GB a RPi5 8GB) = cambiar LLM_MODEL_PATH y reiniciar
# el servicio. Por defecto: Qwen2.5-1.5B-Instruct (seguro en 4GB).
LLM_SERVER_HOST = os.environ.get("LLM_SERVER_HOST", "127.0.0.1")
LLM_SERVER_PORT = int(os.environ.get("LLM_SERVER_PORT", "8869"))
LLM_MODEL_PATH = os.environ.get(
    "LLM_MODEL_PATH",
    "./models/qwen2.5-1.5b-instruct-q4_k_m.gguf",
)
# Nº de hilos = nº de núcleos de la RPi (4 en RPi4). Ajustar en RPi5.
LLM_THREADS = int(os.environ.get("LLM_THREADS", "4"))
# Tamaño de contexto. Pequeño para ahorrar RAM; suficiente para RAG breve.
LLM_CONTEXT_SIZE = int(os.environ.get("LLM_CONTEXT_SIZE", "2048"))
# Tope de tokens a generar (respuesta breve: ~3 mensajes de 250 caracteres).
LLM_MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", "320"))
LLM_TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.3"))
# Tiempo máximo de generación (s) antes de cortar. El cliente espera hasta 300.
LLM_TIMEOUT_SECONDS = int(os.environ.get("LLM_TIMEOUT_SECONDS", "280"))

# ---------------------------------------------------------------------------
# 3. EMBEDDINGS (motor RAG)
# ---------------------------------------------------------------------------
# Modelo de embeddings ligero para CPU/ARM. Por defecto multilingual-e5-small
# (384 dimensiones): excelente en español, índice pequeño, rápido.
# IMPORTANTE: si cambias de modelo cambia también EMBEDDING_DIM y hay que
# reindexar toda la base vectorial.
EMBEDDING_MODEL = os.environ.get(
    "EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
EMBEDDING_DIM = int(os.environ.get("EMBEDDING_DIM", "384"))
# Prefijos para el modelo (vacíos para MiniLM, "query: "/"passage: " para e5).
EMBEDDING_QUERY_PREFIX = os.environ.get("EMBEDDING_QUERY_PREFIX", "")
EMBEDDING_PASSAGE_PREFIX = os.environ.get("EMBEDDING_PASSAGE_PREFIX", "")

# ---------------------------------------------------------------------------
# 4. RECUPERACIÓN RAG
# ---------------------------------------------------------------------------
RAG_TOP_K = int(os.environ.get("RAG_TOP_K", "4"))
# Umbral mínimo de similitud coseno para considerar útil un fragmento.
# Fragmentos por debajo se descartan. 0.42 es un valor equilibrado para MiniLM en lenguaje natural.
RAG_MIN_SCORE = float(os.environ.get("RAG_MIN_SCORE", "0.42"))  # umbral similitud
RAG_MAX_CONTEXT_CHARS = int(os.environ.get("RAG_MAX_CONTEXT_CHARS", "1800"))

# ---------------------------------------------------------------------------
# 5. BASE DE DATOS (PostgreSQL + pgvector, en el directorio de trabajo)
# ---------------------------------------------------------------------------
DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_PORT = int(os.environ.get("DB_PORT", "5432"))
DB_NAME = os.environ.get("DB_NAME", "bot_emergencias")
DB_USER = os.environ.get("DB_USER", "bot")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "CAMBIA_ESTA_CLAVE")
# Directorio de datos del clúster PostgreSQL local (autocontenido en el proyecto).
DB_DATA_DIR = os.environ.get("DB_DATA_DIR", "./data/postgres")

# ---------------------------------------------------------------------------
# 6. API DEL BOT (servicio que atienden los clientes Telegram/Meshtastic)
# ---------------------------------------------------------------------------
API_HOST = os.environ.get("API_HOST", "0.0.0.0")
API_PORT = int(os.environ.get("API_PORT", "8870"))
WEB_HOST = os.environ.get("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.environ.get("WEB_PORT", "8443"))
# Token simple de autenticación de clientes (cabecera Authorization: Bearer ...).
API_AUTH_TOKEN = os.environ.get("API_AUTH_TOKEN", "CAMBIA_ESTE_TOKEN")
# Sólo una inferencia LLM simultánea (protege la RAM de la RPi).
API_MAX_CONCURRENT_INFERENCES = int(os.environ.get("API_MAX_CONCURRENT_INFERENCES", "1"))
# Seguridad: si el token sigue siendo el de por defecto, la API se NIEGA a
# atender peticiones. Pon esto a "true" solo en desarrollo local consciente.
API_ALLOW_INSECURE_TOKEN = os.environ.get("API_ALLOW_INSECURE_TOKEN", "false").lower() in (
    "1", "true", "yes",
)

# ---------------------------------------------------------------------------
# 7. FORMATO DE RESPUESTA (límites para Meshtastic/LoRa)
# ---------------------------------------------------------------------------
# Máximo de bytes UTF-8 por mensaje. Meshtastic tiene un límite LoRa útil de
# ~237 bytes de texto. 230 bytes garantiza que entren de sobra tildes, ñ y signos.
RESP_MAX_BYTES_PER_MSG = int(os.environ.get("RESP_MAX_BYTES_PER_MSG", "230"))
RESP_MAX_CHARS_PER_MSG = RESP_MAX_BYTES_PER_MSG  # compatibilidad
RESP_MAX_MESSAGES = int(os.environ.get("RESP_MAX_MESSAGES", "3"))
# Aviso legal breve que se añade en respuestas médicas/de riesgo vital.
RESP_DISCLAIMER_MEDICO = os.environ.get(
    "RESP_DISCLAIMER_MEDICO",
    "Info orientativa. Llama al 112.",
)

# ---------------------------------------------------------------------------
# 8. SERVICIO ACTUALIZADOR DE CONTEXTO (ingesta + scraping)
# ---------------------------------------------------------------------------
# Carpeta donde se dejan documentos pendientes de revisión humana antes de
# indexar (checkpoint obligatorio para primeros auxilios y especies peligrosas).
UPDATER_STAGING_DIR = os.environ.get("UPDATER_STAGING_DIR", "./data/staging")
UPDATER_USER_AGENT = os.environ.get(
    "UPDATER_USER_AGENT",
    "bot-ia-auxiliar/0.1 (+contacto: raul@fryntiz.dev)",
)
# Claves de APIs externas (las que las requieran). Vacío = fuente desactivada.
AEMET_API_KEY = os.environ.get("AEMET_API_KEY", "")

# ---------------------------------------------------------------------------
# 9. MEMORIA CONVERSACIONAL Y MULTI-TURNO
# ---------------------------------------------------------------------------
# Cantidad máxima de turnos completos (pregunta + respuesta) retenidos por cliente
CONV_MAX_TURNOS = int(os.environ.get("CONV_MAX_TURNOS", 20))
# Turnos íntegros a conservar al compactar el historial antiguo con IA
CONV_TURNOS_COMPACTAR = int(os.environ.get("CONV_TURNOS_COMPACTAR", 10))
# Tiempo de expiración de memoria por inactividad (en segundos, 3600 = 1 hora)
CONV_TTL_SEGUNDOS = int(os.environ.get("CONV_TTL_SEGUNDOS", 3600))

# ---------------------------------------------------------------------------
# 10. LOGGING
# ---------------------------------------------------------------------------
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_DIR = os.environ.get("LOG_DIR", "./logs")
