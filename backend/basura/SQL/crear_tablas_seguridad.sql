-- Script SQL para crear tablas de seguridad manualmente
-- Ejecutar este script si Alembic no funciona

-- Tabla: two_factor_auth
CREATE TABLE IF NOT EXISTS two_factor_auth (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL UNIQUE REFERENCES usuarios(id) ON DELETE CASCADE,
    secret_key VARCHAR(255) NOT NULL,
    backup_codes JSONB,
    enabled BOOLEAN DEFAULT false,
    verified BOOLEAN DEFAULT false,
    method VARCHAR(50) DEFAULT 'totp',
    phone_number VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    last_used_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS ix_two_factor_auth_usuario_id ON two_factor_auth(usuario_id);

-- Tabla: audit_logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    accion VARCHAR(100) NOT NULL,
    recurso VARCHAR(100) NOT NULL,
    recurso_id VARCHAR(255),
    descripcion TEXT,
    datos_anteriores JSONB,
    datos_nuevos JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    metodo_http VARCHAR(10),
    endpoint VARCHAR(255),
    exitoso BOOLEAN DEFAULT true,
    codigo_estado INTEGER,
    mensaje_error TEXT,
    metadata_extra JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_audit_logs_usuario_id ON audit_logs(usuario_id);
CREATE INDEX IF NOT EXISTS ix_audit_logs_accion ON audit_logs(accion);
CREATE INDEX IF NOT EXISTS ix_audit_logs_recurso ON audit_logs(recurso);
CREATE INDEX IF NOT EXISTS ix_audit_logs_recurso_id ON audit_logs(recurso_id);
CREATE INDEX IF NOT EXISTS ix_audit_logs_created_at ON audit_logs(created_at);

-- Tabla: user_sessions
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    refresh_token VARCHAR(255) UNIQUE,
    ip_address VARCHAR(45),
    user_agent TEXT,
    device_info JSONB,
    location VARCHAR(255),
    activa BOOLEAN DEFAULT true,
    revocada BOOLEAN DEFAULT false,
    motivo_revocacion VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS ix_user_sessions_usuario_id ON user_sessions(usuario_id);
CREATE INDEX IF NOT EXISTS ix_user_sessions_session_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS ix_user_sessions_activa ON user_sessions(activa);

-- Tabla: permissions
CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(100) NOT NULL UNIQUE,
    codigo VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    modulo VARCHAR(50) NOT NULL,
    recurso VARCHAR(50) NOT NULL,
    accion VARCHAR(50) NOT NULL,
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_permissions_nombre ON permissions(nombre);
CREATE INDEX IF NOT EXISTS ix_permissions_codigo ON permissions(codigo);
CREATE INDEX IF NOT EXISTS ix_permissions_modulo ON permissions(modulo);

-- Tabla: roles
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(100) NOT NULL UNIQUE,
    codigo VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    nivel INTEGER DEFAULT 0,
    rol_padre_id UUID REFERENCES roles(id),
    activo BOOLEAN DEFAULT true,
    es_sistema BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_roles_nombre ON roles(nombre);
CREATE INDEX IF NOT EXISTS ix_roles_codigo ON roles(codigo);

-- Tabla: role_permissions
CREATE TABLE IF NOT EXISTS role_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    concedido_por_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_role_permissions_role_id ON role_permissions(role_id);
CREATE INDEX IF NOT EXISTS ix_role_permissions_permission_id ON role_permissions(permission_id);

-- Tabla: user_roles
CREATE TABLE IF NOT EXISTS user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    asignado_por_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS ix_user_roles_usuario_id ON user_roles(usuario_id);
CREATE INDEX IF NOT EXISTS ix_user_roles_role_id ON user_roles(role_id);

-- Tabla: sso_providers
CREATE TABLE IF NOT EXISTS sso_providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(100) NOT NULL UNIQUE,
    tipo VARCHAR(50) NOT NULL,
    client_id VARCHAR(255) NOT NULL,
    client_secret VARCHAR(255) NOT NULL,
    authorization_endpoint VARCHAR(500),
    token_endpoint VARCHAR(500),
    userinfo_endpoint VARCHAR(500),
    redirect_uri VARCHAR(500) NOT NULL,
    scopes JSONB,
    metadata_config JSONB,
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);

-- Tabla: sso_connections
CREATE TABLE IF NOT EXISTS sso_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    provider_id UUID NOT NULL REFERENCES sso_providers(id) ON DELETE CASCADE,
    external_id VARCHAR(255) NOT NULL,
    external_email VARCHAR(255),
    external_username VARCHAR(255),
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP WITH TIME ZONE,
    profile_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    last_login_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS ix_sso_connections_usuario_id ON sso_connections(usuario_id);
CREATE INDEX IF NOT EXISTS ix_sso_connections_external_id ON sso_connections(external_id);

-- Tabla: encrypted_data
CREATE TABLE IF NOT EXISTS encrypted_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recurso_tipo VARCHAR(50) NOT NULL,
    recurso_id UUID NOT NULL,
    campo VARCHAR(100) NOT NULL,
    datos_encriptados TEXT NOT NULL,
    algoritmo VARCHAR(50) DEFAULT 'AES-256-GCM',
    iv VARCHAR(255),
    encriptado_por_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_encrypted_data_recurso_tipo ON encrypted_data(recurso_tipo);
CREATE INDEX IF NOT EXISTS ix_encrypted_data_recurso_id ON encrypted_data(recurso_id);

-- Mensaje de confirmación
SELECT 'Tablas de seguridad creadas exitosamente' AS resultado;
