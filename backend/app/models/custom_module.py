"""
Modelos para DDX Studio - Sistema de módulos personalizados no-code
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class ModuleStatus(str, enum.Enum):
    """Estado del módulo personalizado"""

    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"


class CustomModule(Base):
    """
    Módulo personalizado creado con DDX Studio
    Almacena la metadata completa del módulo
    """

    __tablename__ = "custom_modules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificación
    module_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    version = Column(String(20), default="1.0.0")

    # Estado
    status = Column(String(20), default=ModuleStatus.DRAFT.value)
    is_system = Column(Boolean, default=False)

    # Metadata del módulo
    icon = Column(String(50))
    color = Column(String(20))
    category = Column(String(100))

    # Definición completa del módulo en JSON
    definition = Column(JSONB, nullable=False)

    # Código generado (opcional, para cache)
    generated_code = Column(JSONB)

    # Autor y permisos
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    created_by = relationship("Usuario", foreign_keys=[created_by_id])

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    deployed_at = Column(DateTime)

    # Relaciones
    models = relationship(
        "CustomModel", back_populates="module", cascade="all, delete-orphan"
    )
    endpoints = relationship(
        "CustomEndpoint", back_populates="module", cascade="all, delete-orphan"
    )
    forms = relationship(
        "CustomForm", back_populates="module", cascade="all, delete-orphan"
    )


class CustomModel(Base):
    """
    Modelo de datos personalizado (tabla)
    """

    __tablename__ = "custom_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_id = Column(
        UUID(as_uuid=True), ForeignKey("custom_modules.id", ondelete="CASCADE")
    )

    # Identificación
    name = Column(String(100), nullable=False)
    table_name = Column(String(100), nullable=False)
    description = Column(Text)

    # Definición de campos
    fields = Column(JSONB, nullable=False)

    # Relaciones con otros modelos
    relationships = Column(JSONB)

    # Índices personalizados
    indexes = Column(JSONB)

    # Validaciones
    validations = Column(JSONB)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relación
    module = relationship("CustomModule", back_populates="models")


class CustomEndpoint(Base):
    """
    Endpoint API personalizado
    """

    __tablename__ = "custom_endpoints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_id = Column(
        UUID(as_uuid=True), ForeignKey("custom_modules.id", ondelete="CASCADE")
    )

    # Identificación
    name = Column(String(100), nullable=False)
    path = Column(String(200), nullable=False)
    method = Column(String(10), nullable=False)
    description = Column(Text)

    # Configuración
    auth_required = Column(Boolean, default=True)
    permissions = Column(JSONB)

    # Parámetros
    path_params = Column(JSONB)
    query_params = Column(JSONB)
    body_schema = Column(JSONB)

    # Lógica del endpoint
    handler_type = Column(String(50))
    handler_config = Column(JSONB)

    # Respuesta
    response_schema = Column(JSONB)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relación
    module = relationship("CustomModule", back_populates="endpoints")


class CustomForm(Base):
    """
    Formulario personalizado
    """

    __tablename__ = "custom_forms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_id = Column(
        UUID(as_uuid=True), ForeignKey("custom_modules.id", ondelete="CASCADE")
    )

    # Identificación
    name = Column(String(100), nullable=False)
    title = Column(String(200))
    description = Column(Text)

    # Configuración del formulario
    fields = Column(JSONB, nullable=False)
    layout = Column(JSONB)
    validations = Column(JSONB)

    # Acciones
    submit_endpoint = Column(String(200))
    on_success = Column(JSONB)
    on_error = Column(JSONB)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relación
    module = relationship("CustomModule", back_populates="forms")


class ModuleDeployment(Base):
    """
    Historial de despliegues de módulos
    """

    __tablename__ = "module_deployments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_id = Column(
        UUID(as_uuid=True), ForeignKey("custom_modules.id", ondelete="CASCADE")
    )

    # Información del despliegue
    version = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)

    # Detalles
    deployed_by_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    deployed_by = relationship("Usuario")

    # Logs
    deployment_log = Column(Text)
    error_log = Column(Text)

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)
