-- Migración: DDX Studio - Sistema de módulos personalizados no-code
-- Fecha: 2024-12-21
-- Descripción: Tablas para almacenar metadata de módulos personalizados creados visualmente

-- Tabla principal de módulos personalizados
CREATE TABLE IF NOT EXISTS custom_modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identificación
    module_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    version VARCHAR(20) DEFAULT '1.0.0',
    
    -- Estado
    status VARCHAR(20) DEFAULT 'draft',
    is_system BOOLEAN DEFAULT FALSE,
    
    -- Metadata visual
    icon VARCHAR(50),
    color VARCHAR(20),
    category VARCHAR(100),
    
    -- Definición completa del módulo en JSON
    definition JSONB NOT NULL,
    
    -- Código generado (cache)
    generated_code JSONB,
    
    -- Autor
    created_by_id UUID REFERENCES usuarios(id),
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deployed_at TIMESTAMP
);

-- Tabla de modelos de datos personalizados
CREATE TABLE IF NOT EXISTS custom_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module_id UUID NOT NULL REFERENCES custom_modules(id) ON DELETE CASCADE,
    
    -- Identificación
    name VARCHAR(100) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Definición de campos
    fields JSONB NOT NULL,
    
    -- Relaciones
    relationships JSONB,
    
    -- Índices personalizados
    indexes JSONB,
    
    -- Validaciones
    validations JSONB,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de endpoints API personalizados
CREATE TABLE IF NOT EXISTS custom_endpoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module_id UUID NOT NULL REFERENCES custom_modules(id) ON DELETE CASCADE,
    
    -- Identificación
    name VARCHAR(100) NOT NULL,
    path VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL,
    description TEXT,
    
    -- Configuración
    auth_required BOOLEAN DEFAULT TRUE,
    permissions JSONB,
    
    -- Parámetros
    path_params JSONB,
    query_params JSONB,
    body_schema JSONB,
    
    -- Lógica
    handler_type VARCHAR(50),
    handler_config JSONB,
    
    -- Respuesta
    response_schema JSONB,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de formularios personalizados
CREATE TABLE IF NOT EXISTS custom_forms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module_id UUID NOT NULL REFERENCES custom_modules(id) ON DELETE CASCADE,
    
    -- Identificación
    name VARCHAR(100) NOT NULL,
    title VARCHAR(200),
    description TEXT,
    
    -- Configuración
    fields JSONB NOT NULL,
    layout JSONB,
    validations JSONB,
    
    -- Acciones
    submit_endpoint VARCHAR(200),
    on_success JSONB,
    on_error JSONB,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de historial de despliegues
CREATE TABLE IF NOT EXISTS module_deployments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module_id UUID NOT NULL REFERENCES custom_modules(id) ON DELETE CASCADE,
    
    -- Información del despliegue
    version VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    
    -- Detalles
    deployed_by_id UUID REFERENCES usuarios(id),
    
    -- Logs
    deployment_log TEXT,
    error_log TEXT,
    
    -- Timestamps
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_custom_modules_module_id ON custom_modules(module_id);
CREATE INDEX IF NOT EXISTS idx_custom_modules_status ON custom_modules(status);
CREATE INDEX IF NOT EXISTS idx_custom_modules_category ON custom_modules(category);
CREATE INDEX IF NOT EXISTS idx_custom_modules_created_by ON custom_modules(created_by_id);

CREATE INDEX IF NOT EXISTS idx_custom_models_module_id ON custom_models(module_id);
CREATE INDEX IF NOT EXISTS idx_custom_models_table_name ON custom_models(table_name);

CREATE INDEX IF NOT EXISTS idx_custom_endpoints_module_id ON custom_endpoints(module_id);
CREATE INDEX IF NOT EXISTS idx_custom_endpoints_path ON custom_endpoints(path);

CREATE INDEX IF NOT EXISTS idx_custom_forms_module_id ON custom_forms(module_id);

CREATE INDEX IF NOT EXISTS idx_module_deployments_module_id ON module_deployments(module_id);
CREATE INDEX IF NOT EXISTS idx_module_deployments_status ON module_deployments(status);

-- Índices GIN para búsquedas en JSONB
CREATE INDEX IF NOT EXISTS idx_custom_modules_definition ON custom_modules USING GIN (definition);
CREATE INDEX IF NOT EXISTS idx_custom_models_fields ON custom_models USING GIN (fields);

-- Trigger para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DO $$ BEGIN
    CREATE TRIGGER update_custom_modules_updated_at
        BEFORE UPDATE ON custom_modules
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TRIGGER update_custom_models_updated_at
        BEFORE UPDATE ON custom_models
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TRIGGER update_custom_endpoints_updated_at
        BEFORE UPDATE ON custom_endpoints
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TRIGGER update_custom_forms_updated_at
        BEFORE UPDATE ON custom_forms
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Comentarios
COMMENT ON TABLE custom_modules IS 'Módulos personalizados creados con DDX Studio';
COMMENT ON TABLE custom_models IS 'Modelos de datos personalizados (tablas)';
COMMENT ON TABLE custom_endpoints IS 'Endpoints API personalizados';
COMMENT ON TABLE custom_forms IS 'Formularios personalizados';
COMMENT ON TABLE module_deployments IS 'Historial de despliegues de módulos';

COMMENT ON COLUMN custom_modules.module_id IS 'Identificador único del módulo (slug)';
COMMENT ON COLUMN custom_modules.definition IS 'Definición completa del módulo en JSON';
COMMENT ON COLUMN custom_modules.generated_code IS 'Código generado (cache)';
COMMENT ON COLUMN custom_modules.status IS 'Estado: draft, active, inactive, deprecated';

-- Mensaje de éxito
DO $$ BEGIN
    RAISE NOTICE '✅ Migración completada: Tablas de DDX Studio creadas correctamente';
END $$;
