"""
Modelos avanzados para Workflows: Versionado y A/B Testing
"""

import enum
import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    Integer,
    ForeignKey,
    Float,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class WorkflowVersion(Base):
    """Versionado de workflows"""

    __tablename__ = "workflow_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Información de versión
    version_number = Column(String(20), nullable=False)  # "1.0.0", "1.1.0", "2.0.0"
    version_name = Column(String(200))  # "Versión Inicial", "Mejora de Triaje"
    is_current = Column(Boolean, default=False)  # Solo una versión puede ser current
    is_published = Column(Boolean, default=False)

    # Snapshot del workflow en esta versión
    nodes = Column(JSONB, nullable=False)
    edges = Column(JSONB, nullable=False)
    config = Column(JSONB, default=dict)
    variables = Column(JSONB, default=dict)

    # Changelog
    changes_description = Column(Text)  # Descripción de cambios
    breaking_changes = Column(Boolean, default=False)  # ¿Rompe compatibilidad?

    # Métricas de esta versión
    execution_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)  # 0.0 - 1.0
    avg_duration_ms = Column(Integer, default=0)
    error_count = Column(Integer, default=0)

    # Auditoría
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime)
    deprecated_at = Column(DateTime)

    # Relaciones
    workflow = relationship("Workflow", back_populates="versions")


class ABTestStatus(str, enum.Enum):
    """Estados de un test A/B"""

    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ABTest(Base):
    """Tests A/B para workflows"""

    __tablename__ = "ab_tests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Información del test
    test_name = Column(String(200), nullable=False)
    description = Column(Text)
    hypothesis = Column(Text)  # "La versión B reducirá el tiempo de triaje en 20%"

    # Estado
    status = Column(String(20), default=ABTestStatus.DRAFT.value)

    # Variantes (versiones a comparar)
    variant_a_version_id = Column(
        UUID(as_uuid=True), ForeignKey("workflow_versions.id"), nullable=False
    )
    variant_b_version_id = Column(
        UUID(as_uuid=True), ForeignKey("workflow_versions.id"), nullable=False
    )

    # Configuración de distribución
    traffic_split = Column(Float, default=0.5)  # 0.5 = 50/50, 0.7 = 70/30
    sample_size = Column(Integer)  # Número de ejecuciones objetivo
    confidence_level = Column(Float, default=0.95)  # 95% de confianza

    # Métricas objetivo
    primary_metric = Column(
        String(100)
    )  # "duration", "success_rate", "user_satisfaction"
    secondary_metrics = Column(JSONB, default=list)

    # Resultados
    variant_a_executions = Column(Integer, default=0)
    variant_b_executions = Column(Integer, default=0)
    variant_a_metrics = Column(JSONB, default=dict)
    variant_b_metrics = Column(JSONB, default=dict)
    winner = Column(String(1))  # "A" o "B"
    statistical_significance = Column(Float)  # p-value

    # Fechas
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_days = Column(Integer)

    # Auditoría
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    workflow = relationship("Workflow", back_populates="ab_tests")
    variant_a = relationship(
        "WorkflowVersion", foreign_keys=[variant_a_version_id], backref="ab_tests_as_a"
    )
    variant_b = relationship(
        "WorkflowVersion", foreign_keys=[variant_b_version_id], backref="ab_tests_as_b"
    )


class ABTestExecution(Base):
    """Registro de ejecuciones en tests A/B"""

    __tablename__ = "ab_test_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ab_test_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ab_tests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    execution_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflow_executions.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Variante asignada
    variant = Column(String(1), nullable=False)  # "A" o "B"
    version_id = Column(UUID(as_uuid=True), ForeignKey("workflow_versions.id"))

    # Métricas capturadas
    duration_ms = Column(Integer)
    success = Column(Boolean)
    error_occurred = Column(Boolean, default=False)
    custom_metrics = Column(JSONB, default=dict)

    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    ab_test = relationship("ABTest", backref="executions")
    execution = relationship("WorkflowExecution", backref="ab_test_execution")
    version = relationship("WorkflowVersion")
