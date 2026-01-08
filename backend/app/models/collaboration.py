"""
Modelos para Colaboración en Tiempo Real
"""

from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class WorkflowCollaborator(Base):
    """Colaborador de un workflow"""

    __tablename__ = "workflow_collaborators"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)

    # Rol y permisos
    role = Column(String(20), default="viewer")  # owner, editor, viewer
    permissions = Column(ARRAY(String), default=["read"])  # read, write, delete, share

    # Estado
    is_active = Column(Boolean, default=True)
    last_seen_at = Column(String)

    # Configuración personal
    color = Column(String(20))  # Color del cursor
    nickname = Column(String(100))

    # Metadatos
    invited_by_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    invited_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    accepted_at = Column(String)

    # Relaciones
    workflow = relationship("Workflow")
    user = relationship("Usuario", foreign_keys=[user_id])
    invited_by = relationship("Usuario", foreign_keys=[invited_by_id])


class CollaborationSession(Base):
    """Sesión de colaboración activa"""

    __tablename__ = "collaboration_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)

    # Información de sesión
    connection_id = Column(String(100), unique=True)
    user_name = Column(String(200))
    user_color = Column(String(20))

    # Estado
    is_active = Column(Boolean, default=True)
    cursor_x = Column(Integer, default=0)
    cursor_y = Column(Integer, default=0)

    # Actividad
    last_activity_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    connected_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    disconnected_at = Column(String)

    # Metadatos
    user_agent = Column(String(500))
    ip_address = Column(String(50))

    # Relaciones
    workflow = relationship("Workflow")
    user = relationship("Usuario")


class WorkflowChange(Base):
    """Historial de cambios en un workflow"""

    __tablename__ = "workflow_changes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)

    # Tipo de cambio
    change_type = Column(
        String(50)
    )  # node_added, node_updated, node_deleted, edge_added, etc.
    entity_type = Column(String(20))  # node, edge, config
    entity_id = Column(String(100))

    # Datos del cambio
    before_data = Column(JSONB)
    after_data = Column(JSONB)
    diff = Column(JSONB)

    # Contexto
    session_id = Column(UUID(as_uuid=True), ForeignKey("collaboration_sessions.id"))
    user_name = Column(String(200))

    # Metadatos
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())

    # Relaciones
    workflow = relationship("Workflow")
    user = relationship("Usuario")
    session = relationship("CollaborationSession")


class ChatMessage(Base):
    """Mensajes de chat en colaboración"""

    __tablename__ = "collaboration_chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)

    # Mensaje
    message = Column(Text, nullable=False)
    message_type = Column(String(20), default="text")  # text, system, mention

    # Referencias
    reply_to_id = Column(
        UUID(as_uuid=True), ForeignKey("collaboration_chat_messages.id")
    )
    mentioned_user_ids = Column(ARRAY(UUID(as_uuid=True)), default=[])

    # Estado
    is_edited = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)

    # Metadatos
    user_name = Column(String(200))
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    edited_at = Column(String)

    # Relaciones
    workflow = relationship("Workflow")
    user = relationship("Usuario")
    reply_to = relationship("ChatMessage", remote_side=[id])


class WorkflowLock(Base):
    """Bloqueos para edición exclusiva de elementos"""

    __tablename__ = "workflow_locks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)

    # Elemento bloqueado
    entity_type = Column(String(20))  # node, edge, workflow
    entity_id = Column(String(100))

    # Estado
    is_active = Column(Boolean, default=True)

    # Metadatos
    user_name = Column(String(200))
    locked_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    expires_at = Column(String)

    # Relaciones
    workflow = relationship("Workflow")
    user = relationship("Usuario")
