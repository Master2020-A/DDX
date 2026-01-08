-- ============================================================
-- MIGRACION DE COLABORACION EN TIEMPO REAL
-- ============================================================

-- 1. Crear tabla workflow_collaborators
CREATE TABLE IF NOT EXISTS workflow_collaborators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES usuarios(id),
    
    -- Rol y permisos
    role VARCHAR(20) DEFAULT 'viewer',
    permissions TEXT[],
    
    -- Estado
    is_active BOOLEAN DEFAULT TRUE,
    last_seen_at VARCHAR(50),
    
    -- Configuracion personal
    color VARCHAR(20),
    nickname VARCHAR(100),
    
    -- Metadatos
    invited_by_id UUID REFERENCES usuarios(id),
    invited_at VARCHAR(50) DEFAULT NOW()::TEXT,
    accepted_at VARCHAR(50),
    
    CONSTRAINT unique_workflow_user UNIQUE (workflow_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_collaborators_workflow ON workflow_collaborators(workflow_id);
CREATE INDEX IF NOT EXISTS idx_collaborators_user ON workflow_collaborators(user_id);

-- 2. Crear tabla collaboration_sessions
CREATE TABLE IF NOT EXISTS collaboration_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES usuarios(id),
    
    -- Informacion de sesion
    connection_id VARCHAR(100) UNIQUE,
    user_name VARCHAR(200),
    user_color VARCHAR(20),
    
    -- Estado
    is_active BOOLEAN DEFAULT TRUE,
    cursor_x INTEGER DEFAULT 0,
    cursor_y INTEGER DEFAULT 0,
    
    -- Actividad
    last_activity_at VARCHAR(50) DEFAULT NOW()::TEXT,
    connected_at VARCHAR(50) DEFAULT NOW()::TEXT,
    disconnected_at VARCHAR(50),
    
    -- Metadatos
    user_agent VARCHAR(500),
    ip_address VARCHAR(50)
);

CREATE INDEX IF NOT EXISTS idx_sessions_workflow ON collaboration_sessions(workflow_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON collaboration_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_connection ON collaboration_sessions(connection_id);
CREATE INDEX IF NOT EXISTS idx_sessions_active ON collaboration_sessions(workflow_id, is_active) WHERE is_active = TRUE;

-- 3. Crear tabla workflow_changes
CREATE TABLE IF NOT EXISTS workflow_changes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES usuarios(id),
    
    -- Tipo de cambio
    change_type VARCHAR(50),
    entity_type VARCHAR(20),
    entity_id VARCHAR(100),
    
    -- Datos del cambio
    before_data JSONB,
    after_data JSONB,
    diff JSONB,
    
    -- Contexto
    session_id UUID REFERENCES collaboration_sessions(id),
    user_name VARCHAR(200),
    
    -- Metadatos
    created_at VARCHAR(50) DEFAULT NOW()::TEXT
);

CREATE INDEX IF NOT EXISTS idx_changes_workflow ON workflow_changes(workflow_id);
CREATE INDEX IF NOT EXISTS idx_changes_user ON workflow_changes(user_id);
CREATE INDEX IF NOT EXISTS idx_changes_session ON workflow_changes(session_id);
CREATE INDEX IF NOT EXISTS idx_changes_created ON workflow_changes(created_at);

-- 4. Crear tabla collaboration_chat_messages
CREATE TABLE IF NOT EXISTS collaboration_chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES usuarios(id),
    
    -- Mensaje
    message TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text',
    
    -- Referencias
    reply_to_id UUID REFERENCES collaboration_chat_messages(id),
    mentioned_user_ids UUID[],
    
    -- Estado
    is_edited BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    
    -- Metadatos
    user_name VARCHAR(200),
    created_at VARCHAR(50) DEFAULT NOW()::TEXT,
    edited_at VARCHAR(50)
);

CREATE INDEX IF NOT EXISTS idx_chat_workflow ON collaboration_chat_messages(workflow_id);
CREATE INDEX IF NOT EXISTS idx_chat_user ON collaboration_chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_created ON collaboration_chat_messages(created_at);

-- 5. Crear tabla workflow_locks
CREATE TABLE IF NOT EXISTS workflow_locks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES usuarios(id),
    
    -- Elemento bloqueado
    entity_type VARCHAR(20),
    entity_id VARCHAR(100),
    
    -- Estado
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadatos
    user_name VARCHAR(200),
    locked_at VARCHAR(50) DEFAULT NOW()::TEXT,
    expires_at VARCHAR(50)
);

CREATE INDEX IF NOT EXISTS idx_locks_workflow ON workflow_locks(workflow_id);
CREATE INDEX IF NOT EXISTS idx_locks_entity ON workflow_locks(workflow_id, entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_locks_active ON workflow_locks(is_active) WHERE is_active = TRUE;

-- ============================================================
-- MIGRACION COMPLETADA
-- ============================================================
