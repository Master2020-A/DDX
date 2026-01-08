-- Migración: Sistema de Workflows y Agentes IA
-- Fecha: 2024-12-22
-- Descripción: Tablas para workflows visuales, agentes IA, ejecuciones e integraciones

-- Tabla de workflows (flujos de trabajo visuales)
CREATE TABLE IF NOT EXISTS workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identificación
    workflow_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    
    -- Estado
    status VARCHAR(20) DEFAULT 'draft' NOT NULL,
    version VARCHAR(20) DEFAULT '1.0.0',
    
    -- Definición visual
    nodes JSONB NOT NULL DEFAULT '[]',
    edges JSONB NOT NULL DEFAULT '[]',
    
    -- Configuración
    config JSONB DEFAULT '{}',
    variables JSONB DEFAULT '{}',
    
    -- Metadata visual
    icon VARCHAR(50),
    color VARCHAR(20),
    tags JSONB DEFAULT '[]',
    
    -- Auditoría
    created_by_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de agentes IA
CREATE TABLE IF NOT EXISTS ai_agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    
    -- Identificación
    agent_id VARCHAR(100) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    
    -- Configuración del modelo
    model VARCHAR(50) NOT NULL,
    temperature INTEGER DEFAULT 70,
    max_tokens INTEGER DEFAULT 2000,
    
    -- Prompts
    system_prompt TEXT NOT NULL,
    user_prompt_template TEXT,
    
    -- Tools/Functions
    tools JSONB DEFAULT '[]',
    
    -- Configuración adicional
    config JSONB DEFAULT '{}',
    
    -- Metadata
    role VARCHAR(100),
    icon VARCHAR(50),
    color VARCHAR(20),
    
    -- Auditoría
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de ejecuciones de workflows
CREATE TABLE IF NOT EXISTS workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    
    -- Estado
    status VARCHAR(20) DEFAULT 'pending' NOT NULL,
    
    -- Datos
    input_data JSONB NOT NULL,
    output_data JSONB,
    
    -- Contexto de ejecución
    context JSONB DEFAULT '{}',
    current_node_id VARCHAR(100),
    
    -- Resultados
    node_results JSONB DEFAULT '{}',
    
    -- Logs
    logs JSONB DEFAULT '[]',
    error TEXT,
    
    -- Metadata
    triggered_by VARCHAR(100),
    triggered_by_user_id UUID REFERENCES usuarios(id),
    
    -- Timestamps
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms INTEGER
);

-- Tabla de integraciones
CREATE TABLE IF NOT EXISTS integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identificación
    integration_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(50) NOT NULL,
    provider VARCHAR(100),
    
    -- Configuración
    config JSONB NOT NULL,
    
    -- Estado
    is_active BOOLEAN DEFAULT TRUE,
    is_system BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    description TEXT,
    icon VARCHAR(50),
    
    -- Auditoría
    created_by_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de templates de workflows
CREATE TABLE IF NOT EXISTS workflow_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identificación
    template_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    
    -- Definición
    nodes JSONB NOT NULL,
    edges JSONB NOT NULL,
    config JSONB DEFAULT '{}',
    
    -- Metadata
    icon VARCHAR(50),
    color VARCHAR(20),
    tags JSONB DEFAULT '[]',
    
    -- Popularidad
    use_count INTEGER DEFAULT 0,
    is_featured BOOLEAN DEFAULT FALSE,
    is_system BOOLEAN DEFAULT TRUE,
    
    -- Auditoría
    created_by_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_workflows_workflow_id ON workflows(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status);
CREATE INDEX IF NOT EXISTS idx_workflows_category ON workflows(category);
CREATE INDEX IF NOT EXISTS idx_workflows_created_by ON workflows(created_by_id);

CREATE INDEX IF NOT EXISTS idx_ai_agents_workflow_id ON ai_agents(workflow_id);
CREATE INDEX IF NOT EXISTS idx_ai_agents_agent_id ON ai_agents(agent_id);
CREATE INDEX IF NOT EXISTS idx_ai_agents_role ON ai_agents(role);

CREATE INDEX IF NOT EXISTS idx_workflow_executions_workflow_id ON workflow_executions(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_status ON workflow_executions(status);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_triggered_by_user ON workflow_executions(triggered_by_user_id);

CREATE INDEX IF NOT EXISTS idx_integrations_integration_id ON integrations(integration_id);
CREATE INDEX IF NOT EXISTS idx_integrations_type ON integrations(type);
CREATE INDEX IF NOT EXISTS idx_integrations_is_active ON integrations(is_active);

CREATE INDEX IF NOT EXISTS idx_workflow_templates_template_id ON workflow_templates(template_id);
CREATE INDEX IF NOT EXISTS idx_workflow_templates_category ON workflow_templates(category);

-- Índices GIN para búsquedas en JSONB
CREATE INDEX IF NOT EXISTS idx_workflows_nodes ON workflows USING GIN (nodes);
CREATE INDEX IF NOT EXISTS idx_workflows_tags ON workflows USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_node_results ON workflow_executions USING GIN (node_results);

-- Trigger para actualizar updated_at
DO $$ BEGIN
    CREATE TRIGGER update_workflows_updated_at
        BEFORE UPDATE ON workflows
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TRIGGER update_ai_agents_updated_at
        BEFORE UPDATE ON ai_agents
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TRIGGER update_integrations_updated_at
        BEFORE UPDATE ON integrations
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TRIGGER update_workflow_templates_updated_at
        BEFORE UPDATE ON workflow_templates
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Insertar integraciones del sistema (LLMs)
INSERT INTO integrations (integration_id, name, type, provider, config, is_system, description, icon) VALUES
('openai-gpt4', 'OpenAI GPT-4', 'llm', 'openai', '{"model": "gpt-4", "api_key_required": true}', TRUE, 'Modelo GPT-4 de OpenAI', 'Brain'),
('openai-gpt4-turbo', 'OpenAI GPT-4 Turbo', 'llm', 'openai', '{"model": "gpt-4-turbo", "api_key_required": true}', TRUE, 'Modelo GPT-4 Turbo de OpenAI', 'Zap'),
('openai-gpt4o', 'OpenAI GPT-4o', 'llm', 'openai', '{"model": "gpt-4o", "api_key_required": true}', TRUE, 'Modelo GPT-4o de OpenAI', 'Sparkles'),
('anthropic-claude-3-opus', 'Claude 3 Opus', 'llm', 'anthropic', '{"model": "claude-3-opus", "api_key_required": true}', TRUE, 'Modelo Claude 3 Opus de Anthropic', 'MessageSquare'),
('anthropic-claude-3-sonnet', 'Claude 3.7 Sonnet', 'llm', 'anthropic', '{"model": "claude-3-sonnet", "api_key_required": true}', TRUE, 'Modelo Claude 3.7 Sonnet de Anthropic', 'MessageCircle'),
('google-gemini-2-flash', 'Gemini 2.0 Flash', 'llm', 'google', '{"model": "gemini-2.0-flash", "api_key_required": true}', TRUE, 'Modelo Gemini 2.0 Flash de Google', 'Flame')
ON CONFLICT (integration_id) DO NOTHING;

-- Insertar templates de workflows médicos predefinidos
INSERT INTO workflow_templates (template_id, name, description, category, nodes, edges, config, icon, color, is_featured, tags) VALUES
(
    'triaje-inteligente',
    'Triaje Inteligente de Pacientes',
    'Clasifica automáticamente la urgencia de pacientes según síntomas usando IA',
    'clinical',
    '[
        {"id": "start", "type": "start", "position": {"x": 100, "y": 100}, "data": {"label": "Inicio"}},
        {"id": "agent-triaje", "type": "agent", "position": {"x": 300, "y": 100}, "data": {"label": "Agente Triaje", "model": "gpt-4", "role": "triaje"}},
        {"id": "condition-urgencia", "type": "condition", "position": {"x": 500, "y": 100}, "data": {"label": "Evaluar Urgencia"}},
        {"id": "action-urgente", "type": "action", "position": {"x": 700, "y": 50}, "data": {"label": "Crear Consulta Urgente"}},
        {"id": "action-normal", "type": "action", "position": {"x": 700, "y": 150}, "data": {"label": "Agendar Consulta"}},
        {"id": "end", "type": "end", "position": {"x": 900, "y": 100}, "data": {"label": "Fin"}}
    ]',
    '[
        {"id": "e1", "source": "start", "target": "agent-triaje"},
        {"id": "e2", "source": "agent-triaje", "target": "condition-urgencia"},
        {"id": "e3", "source": "condition-urgencia", "target": "action-urgente", "label": "Urgente"},
        {"id": "e4", "source": "condition-urgencia", "target": "action-normal", "label": "Normal"},
        {"id": "e5", "source": "action-urgente", "target": "end"},
        {"id": "e6", "source": "action-normal", "target": "end"}
    ]',
    '{"timeout_ms": 30000}',
    'AlertCircle',
    '#ef4444',
    TRUE,
    '["triaje", "urgencias", "ia"]'
),
(
    'diagnostico-asistido',
    'Diagnóstico Asistido Multi-Agente',
    'Sistema de diagnóstico que combina múltiples agentes especializados',
    'clinical',
    '[
        {"id": "start", "type": "start", "position": {"x": 100, "y": 200}, "data": {"label": "Inicio"}},
        {"id": "agent-lab", "type": "agent", "position": {"x": 300, "y": 100}, "data": {"label": "Agente Laboratorio", "model": "gpt-4"}},
        {"id": "agent-imaging", "type": "agent", "position": {"x": 300, "y": 200}, "data": {"label": "Agente Imagenología", "model": "gpt-4o"}},
        {"id": "agent-history", "type": "agent", "position": {"x": 300, "y": 300}, "data": {"label": "Agente Historial", "model": "gpt-4o-mini"}},
        {"id": "agent-diagnosis", "type": "agent", "position": {"x": 500, "y": 200}, "data": {"label": "Agente Diagnóstico", "model": "claude-3-sonnet"}},
        {"id": "end", "type": "end", "position": {"x": 700, "y": 200}, "data": {"label": "Fin"}}
    ]',
    '[
        {"id": "e1", "source": "start", "target": "agent-lab"},
        {"id": "e2", "source": "start", "target": "agent-imaging"},
        {"id": "e3", "source": "start", "target": "agent-history"},
        {"id": "e4", "source": "agent-lab", "target": "agent-diagnosis"},
        {"id": "e5", "source": "agent-imaging", "target": "agent-diagnosis"},
        {"id": "e6", "source": "agent-history", "target": "agent-diagnosis"},
        {"id": "e7", "source": "agent-diagnosis", "target": "end"}
    ]',
    '{"parallel_execution": true}',
    'Stethoscope',
    '#3b82f6',
    TRUE,
    '["diagnostico", "ia", "multi-agente"]'
),
(
    'prescripcion-segura',
    'Verificación de Prescripción Segura',
    'Valida prescripciones médicas verificando alergias, interacciones y dosificación',
    'pharmacy',
    '[
        {"id": "start", "type": "start", "position": {"x": 100, "y": 200}, "data": {"label": "Inicio"}},
        {"id": "agent-allergies", "type": "agent", "position": {"x": 300, "y": 100}, "data": {"label": "Verificar Alergias", "model": "gpt-4o-mini"}},
        {"id": "agent-interactions", "type": "agent", "position": {"x": 300, "y": 200}, "data": {"label": "Verificar Interacciones", "model": "gpt-4"}},
        {"id": "agent-dosage", "type": "agent", "position": {"x": 300, "y": 300}, "data": {"label": "Verificar Dosificación", "model": "gpt-4o-mini"}},
        {"id": "condition-safe", "type": "condition", "position": {"x": 500, "y": 200}, "data": {"label": "¿Es Seguro?"}},
        {"id": "action-approve", "type": "action", "position": {"x": 700, "y": 150}, "data": {"label": "Aprobar Prescripción"}},
        {"id": "action-alert", "type": "action", "position": {"x": 700, "y": 250}, "data": {"label": "Alertar Médico"}},
        {"id": "end", "type": "end", "position": {"x": 900, "y": 200}, "data": {"label": "Fin"}}
    ]',
    '[
        {"id": "e1", "source": "start", "target": "agent-allergies"},
        {"id": "e2", "source": "start", "target": "agent-interactions"},
        {"id": "e3", "source": "start", "target": "agent-dosage"},
        {"id": "e4", "source": "agent-allergies", "target": "condition-safe"},
        {"id": "e5", "source": "agent-interactions", "target": "condition-safe"},
        {"id": "e6", "source": "agent-dosage", "target": "condition-safe"},
        {"id": "e7", "source": "condition-safe", "target": "action-approve", "label": "Seguro"},
        {"id": "e8", "source": "condition-safe", "target": "action-alert", "label": "Riesgo"},
        {"id": "e9", "source": "action-approve", "target": "end"},
        {"id": "e10", "source": "action-alert", "target": "end"}
    ]',
    '{"parallel_execution": true, "require_all_agents": true}',
    'Pill',
    '#8b5cf6',
    TRUE,
    '["farmacia", "seguridad", "prescripcion"]'
)
ON CONFLICT (template_id) DO NOTHING;

-- Comentarios
COMMENT ON TABLE workflows IS 'Workflows visuales - flujos de trabajo no-code';
COMMENT ON TABLE ai_agents IS 'Agentes de IA configurados para workflows';
COMMENT ON TABLE workflow_executions IS 'Historial de ejecuciones de workflows';
COMMENT ON TABLE integrations IS 'Integraciones con servicios externos (LLMs, APIs, etc.)';
COMMENT ON TABLE workflow_templates IS 'Templates predefinidos de workflows';

COMMENT ON COLUMN workflows.nodes IS 'Nodos del workflow en formato JSON (posición, tipo, config)';
COMMENT ON COLUMN workflows.edges IS 'Conexiones entre nodos (source, target, label)';
COMMENT ON COLUMN ai_agents.system_prompt IS 'Prompt del sistema que define el comportamiento del agente';
COMMENT ON COLUMN ai_agents.tools IS 'Herramientas/funciones disponibles para el agente';
COMMENT ON COLUMN workflow_executions.node_results IS 'Resultados de cada nodo durante la ejecución';

-- Mensaje de éxito
DO $$ BEGIN
    RAISE NOTICE '✅ Migración completada: Sistema de Workflows y Agentes IA creado correctamente';
END $$;
