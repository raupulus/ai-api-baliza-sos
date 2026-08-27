-- Migración 0001 · Esquema inicial
-- Requiere la extensión pgvector. La dimensión del vector debe coincidir con
-- EMBEDDING_DIM (por defecto 384, multilingual-e5-small). Si cambias de modelo
-- de embeddings, ajusta la dimensión y reindexa.

CREATE EXTENSION IF NOT EXISTS vector;

-- Catálogo de fuentes de datos.
CREATE TABLE IF NOT EXISTS fuentes (
    id          SERIAL PRIMARY KEY,
    nombre      TEXT NOT NULL UNIQUE,
    url         TEXT,
    licencia    TEXT,
    metodo      TEXT NOT NULL DEFAULT 'api',     -- 'api' | 'scraping_pdf'
    frecuencia  TEXT,
    activa      BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Fragmentos de conocimiento + embeddings.
CREATE TABLE IF NOT EXISTS fragmentos (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    texto           TEXT NOT NULL,
    fuente          TEXT NOT NULL,
    fuente_url      TEXT,
    fecha           DATE,
    categoria       TEXT NOT NULL,
    subcategoria    TEXT,
    provincia       TEXT,
    nivel_confianza TEXT NOT NULL DEFAULT 'media', -- 'alta' | 'media' | 'baja'
    licencia        TEXT,
    peligrosa       BOOLEAN NOT NULL DEFAULT FALSE,
    validado_por    TEXT,
    validado_fecha  DATE,
    hash_contenido  TEXT NOT NULL UNIQUE,          -- idempotencia (upsert)
    embedding       vector(384) NOT NULL,
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT now(),
    actualizado_en  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_fragmentos_categoria   ON fragmentos (categoria);
CREATE INDEX IF NOT EXISTS idx_fragmentos_provincia   ON fragmentos (provincia);
CREATE INDEX IF NOT EXISTS idx_fragmentos_confianza   ON fragmentos (nivel_confianza);

-- Índice vectorial. Con un corpus pequeño basta la búsqueda exacta (sin índice
-- ANN) o IVFFlat. Se deja IVFFlat preparado; descomenta HNSW si el corpus crece
-- mucho. NOTA: IVFFlat requiere datos para construirse con buen reparto; se
-- puede crear/recrear tras la primera carga masiva.
--
-- Índice vectorial HNSW (coseno): permite inserciones dinámicas desde 0 filas,
-- excelente recall y construcción incremental sin requerir reentrenar centroides.
CREATE INDEX IF NOT EXISTS idx_fragmentos_embedding_hnsw
    ON fragmentos USING hnsw (embedding vector_cosine_ops);

-- Auditoría de ejecuciones del actualizador.
CREATE TABLE IF NOT EXISTS ingestas (
    id              SERIAL PRIMARY KEY,
    fuente          TEXT NOT NULL,
    iniciado_en     TIMESTAMPTZ NOT NULL DEFAULT now(),
    finalizado_en   TIMESTAMPTZ,
    fragmentos_nuevos      INTEGER NOT NULL DEFAULT 0,
    fragmentos_actualizados INTEGER NOT NULL DEFAULT 0,
    fragmentos_en_staging  INTEGER NOT NULL DEFAULT 0,
    errores         INTEGER NOT NULL DEFAULT 0,
    detalle         TEXT
);

-- Log anónimo de consultas (opcional, para evaluar el RAG).
CREATE TABLE IF NOT EXISTS consultas (
    id              BIGSERIAL PRIMARY KEY,
    consulta        TEXT NOT NULL,
    categoria       TEXT,
    confianza       REAL,
    n_fragmentos    INTEGER,
    sin_contexto    BOOLEAN NOT NULL DEFAULT FALSE,
    modelo          TEXT,
    tiempo_ms       INTEGER,
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Trigger para mantener actualizado_en.
CREATE OR REPLACE FUNCTION touch_actualizado_en() RETURNS trigger AS $$
BEGIN
    NEW.actualizado_en = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_fragmentos_touch ON fragmentos;
CREATE TRIGGER trg_fragmentos_touch
    BEFORE UPDATE ON fragmentos
    FOR EACH ROW EXECUTE FUNCTION touch_actualizado_en();
