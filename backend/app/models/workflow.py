"""
Modelos de datos para Workflows y Agentes IA
Sistema de orquestación visual no-code
"""

from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    Integer,
    ForeignKey,
    JSON,
    Enum as SQLEnum,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class WorkflowStatus(str, enum.Enum):
    """Estados de un workflow"""

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ExecutionStatus(str, enum.Enum):
    """Estados de ejecución"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NodeType(str, enum.Enum):
    """Tipos de nodos en el workflow"""

    START = "start"
    END = "end"
    AGENT = "agent"
    CONDITION = "condition"
    ACTION = "action"
    FORM = "form"
    API_CALL = "api_call"
    DATABASE = "database"
    NOTIFICATION = "notification"
    DELAY = "delay"
    LOOP = "loop"
    SUBWORKFLOW = "subworkflow"


class AgentModel(str, enum.Enum):
    """Modelos de IA disponibles"""

    # OpenAI
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"

    # Anthropic
    CLAUDE_3_OPUS = "claude-3-opus"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    CLAUDE_3_HAIKU = "claude-3-haiku"

    # Google
    GEMINI_2_FLASH = "gemini-2.0-flash"
    GEMINI_PRO = "gemini-pro"


class Workflow(Base):
    """Workflow visual - flujo de trabajo completo"""

    __tablename__ = "workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))

    # Estado
    status = Column(
        SQLEnum(WorkflowStatus, values_callable=lambda x: [e.value for e in x]),
        default=WorkflowStatus.DRAFT,
        nullable=False,
    )
    version = Column(String(20), default="1.0.0")

    # Definición visual del workflow
    nodes = Column(JSONB, nullable=False, default=list)  # Lista de nodos
    edges = Column(JSONB, nullable=False, default=list)  # Conexiones entre nodos

    # Configuración
    config = Column(JSONB, default=dict)  # Configuración general
    variables = Column(JSONB, default=dict)  # Variables globales del workflow

    # Metadata visual
    icon = Column(String(50))
    color = Column(String(20))
    tags = Column(JSONB, default=list)

    # Auditoría
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    executions = relationship(
        "WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan"
    )
    agents = relationship(
        "AIAgent", back_populates="workflow", cascade="all, delete-orphan"
    )
    versions = relationship(
        "WorkflowVersion", back_populates="workflow", cascade="all, delete-orphan"
    )
    ab_tests = relationship(
        "ABTest", back_populates="workflow", cascade="all, delete-orphan"
    )


class AIAgent(Base):
    """Agente de IA configurado"""

    __tablename__ = "ai_agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(
        UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE")
    )

    # Identificación
    agent_id = Column(String(100), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)

    # Configuración del modelo
    model = Column(
        SQLEnum(AgentModel, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    temperature = Column(Integer, default=70)  # 0-100 (se divide por 100)
    max_tokens = Column(Integer, default=2000)

    # Prompts
    system_prompt = Column(Text, nullable=False)
    user_prompt_template = Column(Text)

    # Tools/Functions disponibles
    tools = Column(JSONB, default=list)

    # Configuración adicional
    config = Column(JSONB, default=dict)

    # Metadata
    role = Column(String(100))  # ej: "triaje", "diagnostico", "farmaceutico"
    icon = Column(String(50))
    color = Column(String(20))

    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    workflow = relationship("Workflow", back_populates="agents")


class WorkflowExecution(Base):
    """Ejecución de un workflow"""

    __tablename__ = "workflow_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Estado de ejecución
    status = Column(
        SQLEnum(ExecutionStatus, values_callable=lambda x: [e.value for e in x]),
        default=ExecutionStatus.PENDING,
        nullable=False,
    )

    # Datos de entrada y salida
    input_data = Column(JSONB, nullable=False)
    output_data = Column(JSONB)

    # Contexto de ejecución
    context = Column(JSONB, default=dict)  # Variables y estado durante la ejecución
    current_node_id = Column(String(100))  # Nodo actual en ejecución

    # Resultados de cada nodo
    node_results = Column(JSONB, default=dict)

    # Logs y errores
    logs = Column(JSONB, default=list)
    error = Column(Text)

    # Metadata
    triggered_by = Column(String(100))  # "manual", "api", "schedule", "event"
    triggered_by_user_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration_ms = Column(Integer)  # Duración en milisegundos

    # Relaciones
    workflow = relationship("Workflow", back_populates="executions")


class Integration(Base):
    """Integraciones con servicios externos"""

    __tablename__ = "integrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificación
    integration_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    type = Column(String(50), nullable=False)  # "llm", "api", "database", "messaging"
    provider = Column(String(100))  # "openai", "anthropic", "google", etc.

    # Configuración
    config = Column(JSONB, nullable=False)  # API keys, endpoints, etc.

    # Estado
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # Integraciones del sistema vs. usuario

    # Metadata
    description = Column(Text)
    icon = Column(String(50))

    # Auditoría
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WorkflowTemplate(Base):
    """Templates predefinidos de workflows"""

    __tablename__ = "workflow_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificación
    template_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))

    # Definición del template
    nodes = Column(JSONB, nullable=False)
    edges = Column(JSONB, nullable=False)
    config = Column(JSONB, default=dict)

    # Metadata
    icon = Column(String(50))
    color = Column(String(20))
    tags = Column(JSONB, default=list)

    # Popularidad
    use_count = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    is_system = Column(Boolean, default=True)

    # Auditoría
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
