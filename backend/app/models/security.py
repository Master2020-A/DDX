"""
Modelos de seguridad avanzada
"""

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Text,
    Integer,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base


class TwoFactorAuth(Base):
    """Modelo para autenticación de dos factores"""

    __tablename__ = "two_factor_auth"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # TOTP
    secret_key = Column(String(255), nullable=False)
    backup_codes = Column(JSONB, nullable=True)

    # Estado
    enabled = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)

    # Metadata
    method = Column(String(50), default="totp")
    phone_number = Column(String(20), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    # Relaciones
    usuario = relationship("Usuario", back_populates="two_factor_auth")


class AuditLog(Base):
    """Modelo para registro de auditoría"""

    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Usuario y acción
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    accion = Column(String(100), nullable=False, index=True)
    recurso = Column(String(100), nullable=False, index=True)
    recurso_id = Column(String(255), nullable=True, index=True)

    # Detalles
    descripcion = Column(Text, nullable=True)
    datos_anteriores = Column(JSONB, nullable=True)
    datos_nuevos = Column(JSONB, nullable=True)

    # Contexto
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    metodo_http = Column(String(10), nullable=True)
    endpoint = Column(String(255), nullable=True)

    # Resultado
    exitoso = Column(Boolean, default=True)
    codigo_estado = Column(Integer, nullable=True)
    mensaje_error = Column(Text, nullable=True)

    # Metadata adicional
    metadata_extra = Column(JSONB, nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relaciones
    usuario = relationship("Usuario", foreign_keys=[usuario_id])


class UserSession(Base):
    """Modelo para gestión de sesiones de usuario"""

    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Token y sesión
    session_token = Column(String(255), nullable=False, unique=True, index=True)
    refresh_token = Column(String(255), nullable=True, unique=True)

    # Información de la sesión
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    device_info = Column(JSONB, nullable=True)
    location = Column(String(255), nullable=True)

    # Estado
    activa = Column(Boolean, default=True, index=True)
    revocada = Column(Boolean, default=False)
    motivo_revocacion = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    # Relaciones
    usuario = relationship("Usuario", back_populates="sessions")


class Permission(Base):
    """Modelo para permisos granulares"""

    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificación
    nombre = Column(String(100), nullable=False, unique=True, index=True)
    codigo = Column(String(100), nullable=False, unique=True, index=True)
    descripcion = Column(Text, nullable=True)

    # Categorización
    modulo = Column(String(50), nullable=False, index=True)
    recurso = Column(String(50), nullable=False)
    accion = Column(String(50), nullable=False)

    # Metadata
    activo = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relaciones
    roles = relationship("RolePermission", back_populates="permission")


class Role(Base):
    """Modelo para roles con permisos granulares"""

    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificación
    nombre = Column(String(100), nullable=False, unique=True, index=True)
    codigo = Column(String(100), nullable=False, unique=True, index=True)
    descripcion = Column(Text, nullable=True)

    # Jerarquía
    nivel = Column(Integer, default=0)
    rol_padre_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=True)

    # Estado
    activo = Column(Boolean, default=True)
    es_sistema = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relaciones
    permisos = relationship(
        "RolePermission", back_populates="role", cascade="all, delete-orphan"
    )
    usuarios = relationship("UserRole", back_populates="role")
    rol_padre = relationship("Role", remote_side=[id], backref="roles_hijos")


class RolePermission(Base):
    """Tabla de asociación entre roles y permisos"""

    __tablename__ = "role_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    permission_id = Column(
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Metadata
    concedido_por_id = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    role = relationship("Role", back_populates="permisos")
    permission = relationship("Permission", back_populates="roles")
    concedido_por = relationship("Usuario", foreign_keys=[concedido_por_id])


class UserRole(Base):
    """Tabla de asociación entre usuarios y roles"""

    __tablename__ = "user_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Metadata
    asignado_por_id = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Relaciones
    usuario = relationship("Usuario", foreign_keys=[usuario_id], back_populates="roles")
    role = relationship("Role", back_populates="usuarios")
    asignado_por = relationship("Usuario", foreign_keys=[asignado_por_id])


class SSOProvider(Base):
    """Modelo para proveedores de SSO"""

    __tablename__ = "sso_providers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificación
    nombre = Column(String(100), nullable=False, unique=True)
    tipo = Column(String(50), nullable=False)

    # Configuración
    client_id = Column(String(255), nullable=False)
    client_secret = Column(String(255), nullable=False)
    authorization_endpoint = Column(String(500), nullable=True)
    token_endpoint = Column(String(500), nullable=True)
    userinfo_endpoint = Column(String(500), nullable=True)
    redirect_uri = Column(String(500), nullable=False)

    # Configuración adicional
    scopes = Column(JSONB, nullable=True)
    metadata_config = Column(JSONB, nullable=True)

    # Estado
    activo = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SSOConnection(Base):
    """Modelo para conexiones SSO de usuarios"""

    __tablename__ = "sso_connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sso_providers.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Identificación externa
    external_id = Column(String(255), nullable=False, index=True)
    external_email = Column(String(255), nullable=True)
    external_username = Column(String(255), nullable=True)

    # Tokens
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    profile_data = Column(JSONB, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relaciones
    usuario = relationship("Usuario", foreign_keys=[usuario_id])
    provider = relationship("SSOProvider", foreign_keys=[provider_id])


class EncryptedData(Base):
    """Modelo para datos encriptados end-to-end"""

    __tablename__ = "encrypted_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Referencia
    recurso_tipo = Column(String(50), nullable=False, index=True)
    recurso_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    campo = Column(String(100), nullable=False)

    # Datos encriptados
    datos_encriptados = Column(Text, nullable=False)
    algoritmo = Column(String(50), default="AES-256-GCM")
    iv = Column(String(255), nullable=True)

    # Metadata
    encriptado_por_id = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relaciones
    encriptado_por = relationship("Usuario", foreign_keys=[encriptado_por_id])
