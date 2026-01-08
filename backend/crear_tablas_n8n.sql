-- Script para crear las tablas de N8N

-- Tabla de configuración de N8N
CREATE TABLE IF NOT EXISTS n8n_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_key VARCHAR(255) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL DEFAULT 'N8N Integration',
    descripcion TEXT,
    n8n_webhook_url VARCHAR(500) NOT NULL,
    n8n_api_url VARCHAR(500),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    webhooks_habilitados BOOLEAN NOT NULL DEFAULT TRUE,
    timeout_segundos INTEGER NOT NULL DEFAULT 5,
    eventos_habilitados JSONB,
    total_eventos_enviados INTEGER NOT NULL DEFAULT 0,
    total_eventos_exitosos INTEGER NOT NULL DEFAULT 0,
    total_eventos_fallidos INTEGER NOT NULL DEFAULT 0,
    ultimo_evento_enviado TIMESTAMP,
    created_by UUID NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices para n8n_config
CREATE INDEX IF NOT EXISTS idx_n8n_config_api_key ON n8n_config(api_key);
CREATE INDEX IF NOT EXISTS idx_n8n_config_activo ON n8n_config(activo);

-- Tabla de log de eventos de N8N
CREATE TABLE IF NOT EXISTS n8n_event_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evento_tipo VARCHAR(100) NOT NULL,
    evento_data JSONB NOT NULL,
    prioridad VARCHAR(20) NOT NULL DEFAULT 'normal',
    webhook_url VARCHAR(500) NOT NULL,
    exitoso BOOLEAN NOT NULL,
    codigo_http INTEGER,
    tiempo_respuesta_ms INTEGER,
    error TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Índices para n8n_event_log
CREATE INDEX IF NOT EXISTS idx_n8n_event_log_evento_tipo ON n8n_event_log(evento_tipo);
CREATE INDEX IF NOT EXISTS idx_n8n_event_log_created_at ON n8n_event_log(created_at);
CREATE INDEX IF NOT EXISTS idx_n8n_event_log_exitoso ON n8n_event_log(exitoso);

-- Comentarios
COMMENT ON TABLE n8n_config IS 'Configuración de integración con N8N';
COMMENT ON TABLE n8n_event_log IS 'Log de eventos enviados a N8N';

-- Mensaje de confirmación
DO $$
BEGIN
    RAISE NOTICE 'Tablas de N8N creadas exitosamente';
END $$;
