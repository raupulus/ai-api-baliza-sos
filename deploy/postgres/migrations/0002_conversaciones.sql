-- Migración 0002: Persistencia de conversaciones y mensajes por cliente
-- Permite histórico multi-turno, auditoría, trazabilidad y compactación.

CREATE TABLE IF NOT EXISTS conversaciones (
    id VARCHAR(64) PRIMARY KEY,
    cliente_id VARCHAR(64) NOT NULL,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resumen TEXT,
    activa BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_conversaciones_cliente ON conversaciones (cliente_id);
CREATE INDEX IF NOT EXISTS idx_conversaciones_actualizado ON conversaciones (actualizado_en);

CREATE TABLE IF NOT EXISTS mensajes_conversacion (
    id BIGSERIAL PRIMARY KEY,
    conversacion_id VARCHAR(64) NOT NULL REFERENCES conversaciones(id) ON DELETE CASCADE,
    rol VARCHAR(16) NOT NULL, -- 'user', 'assistant', 'system_summary'
    contenido TEXT NOT NULL,
    orden INT NOT NULL,
    metadatos JSONB,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mensajes_conversacion_orden ON mensajes_conversacion (conversacion_id, orden);
