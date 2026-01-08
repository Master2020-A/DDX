from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class ConditionClinicalStatus(str, enum.Enum):
    """Estado clínico de la condición"""

    ACTIVE = "active"
    RECURRENCE = "recurrence"
    RELAPSE = "relapse"
    INACTIVE = "inactive"
    REMISSION = "remission"
    RESOLVED = "resolved"


class ConditionVerificationStatus(str, enum.Enum):
    """Estado de verificación de la condición"""

    UNCONFIRMED = "unconfirmed"
    PROVISIONAL = "provisional"
    DIFFERENTIAL = "differential"
    CONFIRMED = "confirmed"
    REFUTED = "refuted"
    ENTERED_IN_ERROR = "entered-in-error"


class ConditionCategory(str, enum.Enum):
    """Categoría de la condición"""

    PROBLEM_LIST_ITEM = "problem-list-item"
    ENCOUNTER_DIAGNOSIS = "encounter-diagnosis"


class FHIRCondition(Base):
    """
    Modelo para almacenar recursos Condition HL7 FHIR R4
    Representa diagnósticos, problemas de salud y condiciones clínicas
    """

    __tablename__ = "fhir_conditions"

    # Identificador primario
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificadores externos (FHIR)
    identifier = Column(JSONB, comment="Identificadores externos del recurso FHIR")
    fhir_id = Column(
        String(255), index=True, comment="ID del recurso en el servidor FHIR externo"
    )
    fhir_server_url = Column(String(500), comment="URL del servidor FHIR de origen")

    # Estado clínico y verificación
    clinical_status = Column(
        SQLEnum(ConditionClinicalStatus),
        nullable=False,
        default=ConditionClinicalStatus.ACTIVE,
        comment="Estado clínico de la condición",
    )
    verification_status = Column(
        SQLEnum(ConditionVerificationStatus),
        nullable=False,
        default=ConditionVerificationStatus.CONFIRMED,
        comment="Estado de verificación",
    )

    # Categoría
    category = Column(
        JSONB,
        comment="Categoría de la condición (problem-list-item, encounter-diagnosis)",
    )

    # Severidad
    severity = Column(
        JSONB, comment="Severidad de la condición (mild, moderate, severe)"
    )

    # Código de la condición (ICD-10, SNOMED CT, etc.)
    code = Column(
        JSONB, nullable=False, comment="Código de la condición (CodeableConcept)"
    )

    # Sitio corporal afectado
    body_site = Column(JSONB, comment="Sitio corporal afectado")

    # Paciente
    subject_id = Column(
        UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False, index=True
    )
    subject = relationship("Paciente", backref="fhir_conditions")

    # Encuentro/Consulta relacionada
    encounter_id = Column(
        UUID(as_uuid=True), ForeignKey("consultas.id"), nullable=True, index=True
    )
    encounter = relationship("Consulta", backref="fhir_conditions")

    # Fechas
    onset_datetime = Column(DateTime, comment="Fecha de inicio de la condición")
    onset_age = Column(JSONB, comment="Edad de inicio")
    onset_period = Column(JSONB, comment="Período de inicio")
    onset_range = Column(JSONB, comment="Rango de inicio")
    onset_string = Column(String(500), comment="Descripción textual del inicio")

    abatement_datetime = Column(DateTime, comment="Fecha de resolución")
    abatement_age = Column(JSONB, comment="Edad de resolución")
    abatement_period = Column(JSONB, comment="Período de resolución")
    abatement_range = Column(JSONB, comment="Rango de resolución")
    abatement_string = Column(
        String(500), comment="Descripción textual de la resolución"
    )

    recorded_date = Column(DateTime, comment="Fecha de registro")

    # Quién registró
    recorder_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    recorder = relationship(
        "Usuario", foreign_keys=[recorder_id], backref="recorded_conditions"
    )

    # Quién afirmó
    asserter_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    asserter = relationship(
        "Usuario", foreign_keys=[asserter_id], backref="asserted_conditions"
    )

    # Etapa de la condición
    stage = Column(JSONB, comment="Etapa de la condición")

    # Evidencia
    evidence = Column(JSONB, comment="Evidencia que soporta la condición")

    # Notas
    note = Column(JSONB, comment="Notas adicionales (Annotation)")

    # Metadatos de origen
    source_system = Column(
        String(255), comment="Sistema de origen (interno, FHIR externo, HL7 v2)"
    )
    source_record_id = Column(
        String(255), comment="ID del registro en el sistema de origen"
    )

    # Recurso FHIR completo
    fhir_resource = Column(JSONB, comment="Recurso FHIR completo en formato JSON")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self):
        return f"<FHIRCondition(id={self.id}, code={self.code}, subject_id={self.subject_id})>"
