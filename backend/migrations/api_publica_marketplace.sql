-- Migración para API Pública y Marketplace
-- Ejecutar con: psql -U postgres -d ddx -f migrations/api_publica_marketplace.sql

-- Tabla de API Keys
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    key VARCHAR(64) UNIQUE NOT NULL,
    secret_hash VARCHAR(255) NOT NULL,
    permisos TEXT[] DEFAULT '{}',
    scopes TEXT[] DEFAULT '{}',
    rate_limit_por_minuto INTEGER DEFAULT 60,
    rate_limit_por_dia INTEGER DEFAULT 10000,
    webhook_url VARCHAR(500),
    webhook_secret VARCHAR(255),
    eventos_suscritos TEXT[] DEFAULT '{}',
    activa BOOLEAN DEFAULT TRUE,
    expira_en TIMESTAMP,
    ip_whitelist TEXT[] DEFAULT '{}',
    entorno VARCHAR(50) DEFAULT 'produccion',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_uso TIMESTAMP,
    total_requests INTEGER DEFAULT 0
);

CREATE INDEX idx_api_keys_key ON api_keys(key);
CREATE INDEX idx_api_keys_activa ON api_keys(activa);

-- Tabla de Logs de API Pública
CREATE TABLE IF NOT EXISTS logs_api_publica (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_key_id UUID NOT NULL REFERENCES api_keys(id) ON DELETE CASCADE,
    metodo VARCHAR(10) NOT NULL,
    endpoint VARCHAR(500) NOT NULL,
    ip_origen VARCHAR(45),
    user_agent TEXT,
    status_code INTEGER,
    tiempo_respuesta_ms INTEGER,
    request_body JSONB,
    response_body JSONB,
    error TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_api_key ON logs_api_publica(api_key_id);
CREATE INDEX idx_logs_timestamp ON logs_api_publica(timestamp);

-- Tabla de Webhooks
CREATE TABLE IF NOT EXISTS webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_key_id UUID NOT NULL REFERENCES api_keys(id) ON DELETE CASCADE,
    nombre VARCHAR(200) NOT NULL,
    url VARCHAR(500) NOT NULL,
    secret VARCHAR(255) NOT NULL,
    eventos TEXT[] NOT NULL,
    max_reintentos INTEGER DEFAULT 3,
    timeout_segundos INTEGER DEFAULT 30,
    activo BOOLEAN DEFAULT TRUE,
    headers_personalizados JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_envio TIMESTAMP,
    total_envios INTEGER DEFAULT 0,
    total_errores INTEGER DEFAULT 0
);

CREATE INDEX idx_webhooks_api_key ON webhooks(api_key_id);
CREATE INDEX idx_webhooks_activo ON webhooks(activo);

-- Tabla de Entregas de Webhooks
CREATE TABLE IF NOT EXISTS entregas_webhook (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_id UUID NOT NULL REFERENCES webhooks(id) ON DELETE CASCADE,
    evento VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    intento INTEGER DEFAULT 1,
    status_code INTEGER,
    tiempo_respuesta_ms INTEGER,
    exitoso BOOLEAN DEFAULT FALSE,
    error TEXT,
    response_body TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    proximo_reintento TIMESTAMP
);

CREATE INDEX idx_entregas_webhook ON entregas_webhook(webhook_id);
CREATE INDEX idx_entregas_timestamp ON entregas_webhook(timestamp);

-- Tabla de Plugins
CREATE TABLE IF NOT EXISTS plugins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(200) NOT NULL UNIQUE,
    slug VARCHAR(200) NOT NULL UNIQUE,
    descripcion TEXT NOT NULL,
    descripcion_larga TEXT,
    autor VARCHAR(200) NOT NULL,
    email_autor VARCHAR(255),
    url_autor VARCHAR(500),
    version VARCHAR(50) NOT NULL,
    version_minima_ddx VARCHAR(50),
    categoria VARCHAR(100),
    tags TEXT[] DEFAULT '{}',
    url_repositorio VARCHAR(500),
    url_documentacion VARCHAR(500),
    url_demo VARCHAR(500),
    url_icono VARCHAR(500),
    screenshots TEXT[] DEFAULT '{}',
    url_descarga VARCHAR(500),
    hash_archivo VARCHAR(255),
    tamano_bytes INTEGER,
    requiere_api_key BOOLEAN DEFAULT FALSE,
    permisos_requeridos TEXT[] DEFAULT '{}',
    configuracion_schema JSONB,
    estado VARCHAR(50) DEFAULT 'pendiente',
    verificado BOOLEAN DEFAULT FALSE,
    descargas INTEGER DEFAULT 0,
    instalaciones_activas INTEGER DEFAULT 0,
    calificacion_promedio INTEGER DEFAULT 0,
    total_calificaciones INTEGER DEFAULT 0,
    es_gratuito BOOLEAN DEFAULT TRUE,
    precio_usd INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_aprobacion TIMESTAMP
);

CREATE INDEX idx_plugins_slug ON plugins(slug);
CREATE INDEX idx_plugins_estado ON plugins(estado);
CREATE INDEX idx_plugins_categoria ON plugins(categoria);
CREATE INDEX idx_plugins_verificado ON plugins(verificado);

-- Tabla de Instalaciones de Plugins
CREATE TABLE IF NOT EXISTS instalaciones_plugin (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plugin_id UUID NOT NULL REFERENCES plugins(id) ON DELETE CASCADE,
    configuracion JSONB,
    api_key_id UUID REFERENCES api_keys(id) ON DELETE SET NULL,
    activo BOOLEAN DEFAULT TRUE,
    version_instalada VARCHAR(50),
    fecha_instalacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP,
    ultimo_uso TIMESTAMP
);

CREATE INDEX idx_instalaciones_plugin ON instalaciones_plugin(plugin_id);
CREATE INDEX idx_instalaciones_activo ON instalaciones_plugin(activo);

-- Tabla de Reseñas de Plugins
CREATE TABLE IF NOT EXISTS resenas_plugin (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plugin_id UUID NOT NULL REFERENCES plugins(id) ON DELETE CASCADE,
    calificacion INTEGER NOT NULL CHECK (calificacion >= 1 AND calificacion <= 5),
    titulo VARCHAR(200),
    comentario TEXT,
    autor_nombre VARCHAR(200),
    autor_email VARCHAR(255),
    version_plugin VARCHAR(50),
    verificado BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_resenas_plugin ON resenas_plugin(plugin_id);
CREATE INDEX idx_resenas_calificacion ON resenas_plugin(calificacion);

-- Función para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para updated_at
CREATE TRIGGER update_api_keys_updated_at BEFORE UPDATE ON api_keys
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_webhooks_updated_at BEFORE UPDATE ON webhooks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_plugins_updated_at BEFORE UPDATE ON plugins
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_resenas_updated_at BEFORE UPDATE ON resenas_plugin
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comentarios
COMMENT ON TABLE api_keys IS 'API Keys para acceso a la API pública de DDX';
COMMENT ON TABLE logs_api_publica IS 'Logs de uso de la API pública';
COMMENT ON TABLE webhooks IS 'Webhooks configurados para eventos del sistema';
COMMENT ON TABLE entregas_webhook IS 'Registro de entregas de webhooks';
COMMENT ON TABLE plugins IS 'Plugins disponibles en el marketplace';
COMMENT ON TABLE instalaciones_plugin IS 'Instalaciones de plugins por usuarios';
COMMENT ON TABLE resenas_plugin IS 'Reseñas y calificaciones de plugins';
