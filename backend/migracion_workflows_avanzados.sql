-- ============================================================
-- MIGRACION DE WORKFLOWS AVANZADOS
-- Agrega soporte para Loops, Subworkflows, Versionado y A/B Testing
-- ============================================================

-- 1. Actualizar ENUM nodetype para agregar loop y subworkflow
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'loop' AND enumtypid = 'nodetype'::regtype) THEN
        ALTER TYPE nodetype ADD VALUE 'loop';
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'subworkflow' AND enumtypid = 'nodetype'::regtype) THEN
        ALTER TYPE nodetype ADD VALUE 'subworkflow';
    END IF;
END $$;

-- 2. Crear tabla workflow_versions
CREATE TABLE IF NOT EXISTS workflow_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    
    -- Informacion de version
    version_number VARCHAR(20) NOT NULL,
    version_name VARCHAR(200),
    is_current BOOLEAN DEFAULT FALSE,
    is_published BOOLEAN DEFAULT FALSE,
    
    -- Snapshot del workflow
    nodes JSONB NOT NULL,
    edges JSONB NOT NULL,
    config JSONB DEFAULT '{}'::jsonb,
    variables JSONB DEFAULT '{}'::jsonb,
    
    -- Changelog
    changes_description TEXT,
    breaking_changes BOOLEAN DEFAULT FALSE,
    
    -- Metricas
    execution_count INTEGER DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0,
    avg_duration_ms INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    
    -- Auditoria
    created_by_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    published_at TIMESTAMP WITHOUT TIME ZONE,
    deprecated_at TIMESTAMP WITHOUT TIME ZONE,
    
    CONSTRAINT unique_workflow_version UNIQUE (workflow_id, version_number)
);

CREATE INDEX IF NOT EXISTS idx_workflow_versions_workflow ON workflow_versions(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_versions_current ON workflow_versions(workflow_id, is_current) WHERE is_current = TRUE;
CREATE INDEX IF NOT EXISTS idx_workflow_versions_published ON workflow_versions(is_published) WHERE is_published = TRUE;

-- 3. Crear ENUM abtestatus
DO $$ BEGIN
    CREATE TYPE abtestatus AS ENUM (
        'draft',
        'running',
        'paused',
        'completed',
        'cancelled'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 4. Crear tabla ab_tests
CREATE TABLE IF NOT EXISTS ab_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    
    -- Informacion del test
    test_name VARCHAR(200) NOT NULL,
    description TEXT,
    hypothesis TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    
    -- Variantes
    variant_a_version_id UUID NOT NULL REFERENCES workflow_versions(id),
    variant_b_version_id UUID NOT NULL REFERENCES workflow_versions(id),
    
    -- Configuracion
    traffic_split FLOAT DEFAULT 0.5,
    sample_size INTEGER,
    confidence_level FLOAT DEFAULT 0.95,
    
    -- Metricas
    primary_metric VARCHAR(100),
    secondary_metrics JSONB DEFAULT '[]'::jsonb,
    
    -- Resultados
    variant_a_executions INTEGER DEFAULT 0,
    variant_b_executions INTEGER DEFAULT 0,
    variant_a_metrics JSONB DEFAULT '{}'::jsonb,
    variant_b_metrics JSONB DEFAULT '{}'::jsonb,
    winner VARCHAR(1),
    statistical_significance FLOAT,
    
    -- Fechas
    started_at TIMESTAMP WITHOUT TIME ZONE,
    completed_at TIMESTAMP WITHOUT TIME ZONE,
    duration_days INTEGER,
    
    -- Auditoria
    created_by_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ab_tests_workflow ON ab_tests(workflow_id);
CREATE INDEX IF NOT EXISTS idx_ab_tests_status ON ab_tests(status);
CREATE INDEX IF NOT EXISTS idx_ab_tests_running ON ab_tests(workflow_id, status) WHERE status = 'running';

-- 5. Crear tabla ab_test_executions
CREATE TABLE IF NOT EXISTS ab_test_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ab_test_id UUID NOT NULL REFERENCES ab_tests(id) ON DELETE CASCADE,
    execution_id UUID NOT NULL REFERENCES workflow_executions(id) ON DELETE CASCADE,
    
    -- Variante asignada
    variant VARCHAR(1) NOT NULL,
    version_id UUID REFERENCES workflow_versions(id),
    
    -- Metricas capturadas
    duration_ms INTEGER,
    success BOOLEAN,
    error_occurred BOOLEAN DEFAULT FALSE,
    custom_metrics JSONB DEFAULT '{}'::jsonb,
    
    -- Auditoria
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ab_test_executions_test ON ab_test_executions(ab_test_id);
CREATE INDEX IF NOT EXISTS idx_ab_test_executions_execution ON ab_test_executions(execution_id);
CREATE INDEX IF NOT EXISTS idx_ab_test_executions_variant ON ab_test_executions(ab_test_id, variant);

-- 6. Agregar columna parent_workflow_id a workflows
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'workflows' 
        AND column_name = 'parent_workflow_id'
    ) THEN
        ALTER TABLE workflows ADD COLUMN parent_workflow_id UUID REFERENCES workflows(id);
    END IF;
END $$;

-- 7. Crear funcion para actualizar metricas de versiones
CREATE OR REPLACE FUNCTION update_version_metrics()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'completed' OR NEW.status = 'failed' THEN
        UPDATE workflow_versions
        SET 
            execution_count = execution_count + 1,
            success_rate = (
                SELECT COUNT(*)::FLOAT / NULLIF(COUNT(*), 0)
                FROM workflow_executions we
                WHERE we.workflow_id = NEW.workflow_id
                AND we.status = 'completed'
            ),
            avg_duration_ms = (
                SELECT AVG(duration_ms)::INTEGER
                FROM workflow_executions we
                WHERE we.workflow_id = NEW.workflow_id
                AND we.duration_ms IS NOT NULL
            ),
            error_count = (
                SELECT COUNT(*)
                FROM workflow_executions we
                WHERE we.workflow_id = NEW.workflow_id
                AND we.status = 'failed'
            )
        WHERE workflow_id = NEW.workflow_id
        AND is_current = TRUE;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 8. Crear trigger para actualizar metricas
DROP TRIGGER IF EXISTS trigger_update_version_metrics ON workflow_executions;

CREATE TRIGGER trigger_update_version_metrics
AFTER UPDATE ON workflow_executions
FOR EACH ROW
WHEN (OLD.status IS DISTINCT FROM NEW.status)
EXECUTE FUNCTION update_version_metrics();

-- 9. Crear versiones iniciales para workflows existentes
INSERT INTO workflow_versions (
    workflow_id, version_number, version_name,
    is_current, is_published,
    nodes, edges, config, variables,
    created_by_id, published_at
)
SELECT 
    id,
    '1.0.0',
    'Version Inicial',
    TRUE,
    TRUE,
    nodes,
    edges,
    COALESCE(config, '{}'::jsonb),
    COALESCE(variables, '{}'::jsonb),
    created_by_id,
    NOW()
FROM workflows
WHERE status = 'active'
AND id NOT IN (SELECT workflow_id FROM workflow_versions);

-- ============================================================
-- MIGRACION COMPLETADA
-- ============================================================
-- Tablas creadas:
-- - workflow_versions (versionado de workflows)
-- - ab_tests (pruebas A/B)
-- - ab_test_executions (ejecuciones de pruebas A/B)
--
-- ENUMs actualizados:
-- - nodetype: agregados 'loop' y 'subworkflow'
-- - abtestatus: creado nuevo enum
--
-- Triggers:
-- - trigger_update_version_metrics: actualiza metricas automaticamente
-- ============================================================
