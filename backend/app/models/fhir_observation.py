from sqlalchemy import (
    Column,
    String,
    DateTime,
    Text,
    Integer,
    ForeignKey,
    Enum as SQLEnum,
    ARRAY,
    Boolean,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class ObservationStatus(str, enum.Enum):
    REGISTERED = "registered"
    PRELIMINARY = "preliminary"
    FINAL = "final"
    AMENDED = "amended"
    CORRECTED = "corrected"
    CANCELLED = "cancelled"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"


class ObservationCategory(str, enum.Enum):
    VITAL_SIGNS = "vital-signs"
    LABORATORY = "laboratory"
    IMAGING = "imaging"
    PROCEDURE = "procedure"
    SURVEY = "survey"
    EXAM = "exam"
    THERAPY = "therapy"
    ACTIVITY = "activity"


class FHIRObservation(Base):
    """
    Modelo para almacenar Observaciones FHIR R4
    Representa mediciones y observaciones clínicas
    """

    __tablename__ = "fhir_observations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificadores
    identifier = Column(JSONB, nullable=True)  # Array de identificadores

    # Estado y categoría
    status = Column(
        SQLEnum(ObservationStatus), nullable=False, default=ObservationStatus.FINAL
    )
    category = Column(
        ARRAY(String), nullable=True
    )  # Categorías (vital-signs, laboratory, etc)

    # Código de la observación (LOINC, SNOMED, etc)
    code = Column(JSONB, nullable=False)  # CodeableConcept

    # Referencias
    subject_type = Column(
        String, nullable=False, default="Patient"
    )  # Patient, Group, Device, Location
    subject_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    encounter_id = Column(UUID(as_uuid=True), ForeignKey("consultas.id"), nullable=True)

    # Tiempo
    effective_datetime = Column(DateTime, nullable=True)
    effective_period_start = Column(DateTime, nullable=True)
    effective_period_end = Column(DateTime, nullable=True)
    issued = Column(DateTime, nullable=True)

    # Performer (quien realizó la observación)
    performer = Column(JSONB, nullable=True)  # Array de referencias

    # Valor de la observación
    value_quantity = Column(JSONB, nullable=True)  # {value, unit, system, code}
    value_codeable_concept = Column(JSONB, nullable=True)
    value_string = Column(Text, nullable=True)
    value_boolean = Column(Boolean, nullable=True)
    value_integer = Column(Integer, nullable=True)
    value_range = Column(JSONB, nullable=True)
    value_ratio = Column(JSONB, nullable=True)
    value_sampled_data = Column(JSONB, nullable=True)
    value_time = Column(String, nullable=True)
    value_datetime = Column(DateTime, nullable=True)
    value_period = Column(JSONB, nullable=True)

    # Interpretación
    interpretation = Column(JSONB, nullable=True)  # Array de CodeableConcept

    # Notas
    note = Column(JSONB, nullable=True)  # Array de Annotation

    # Método
    method = Column(JSONB, nullable=True)  # CodeableConcept

    # Sitio corporal
    body_site = Column(JSONB, nullable=True)  # CodeableConcept

    # Rango de referencia
    reference_range = Column(JSONB, nullable=True)  # Array de ReferenceRange

    # Componentes (para observaciones multi-componente)
    component = Column(JSONB, nullable=True)  # Array de ObservationComponent

    # Datos derivados
    derived_from = Column(JSONB, nullable=True)  # Referencias a otros recursos

    # Metadatos
    meta = Column(JSONB, nullable=True)  # Meta (versionId, lastUpdated, profile, etc)

    # Datos originales (para trazabilidad)
    source_type = Column(
        String, nullable=True
    )  # laboratorio, signo_vital, estudio_especial
    source_id = Column(UUID(as_uuid=True), nullable=True)  # ID del recurso original

    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    created_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)

    # Relaciones
    subject = relationship(
        "Paciente", foreign_keys=[subject_id], backref="fhir_observations"
    )
    encounter = relationship(
        "Consulta", foreign_keys=[encounter_id], backref="fhir_observations"
    )
    creator = relationship("Usuario", foreign_keys=[created_by])

    def to_fhir_dict(self) -> dict:
        """
        Convierte el modelo a un diccionario FHIR R4 completo
        """
        observation = {
            "resourceType": "Observation",
            "id": str(self.id),
            "status": self.status.value,
            "code": self.code,
            "subject": {
                "reference": f"{self.subject_type}/{self.subject_id}",
                "type": self.subject_type,
            },
        }

        # Meta
        if self.meta:
            observation["meta"] = self.meta
        else:
            observation["meta"] = {
                "versionId": "1",
                "lastUpdated": self.updated_at.isoformat() if self.updated_at else None,
            }

        # Identificadores
        if self.identifier:
            observation["identifier"] = self.identifier

        # Categoría
        if self.category:
            observation["category"] = [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": cat,
                            "display": cat.replace("-", " ").title(),
                        }
                    ]
                }
                for cat in self.category
            ]

        # Encounter
        if self.encounter_id:
            observation["encounter"] = {"reference": f"Encounter/{self.encounter_id}"}

        # Tiempo efectivo
        if self.effective_datetime:
            observation["effectiveDateTime"] = self.effective_datetime.isoformat()
        elif self.effective_period_start or self.effective_period_end:
            observation["effectivePeriod"] = {}
            if self.effective_period_start:
                observation["effectivePeriod"][
                    "start"
                ] = self.effective_period_start.isoformat()
            if self.effective_period_end:
                observation["effectivePeriod"][
                    "end"
                ] = self.effective_period_end.isoformat()

        # Issued
        if self.issued:
            observation["issued"] = self.issued.isoformat()

        # Performer
        if self.performer:
            observation["performer"] = self.performer

        # Valor (solo uno de los tipos)
        if self.value_quantity:
            observation["valueQuantity"] = self.value_quantity
        elif self.value_codeable_concept:
            observation["valueCodeableConcept"] = self.value_codeable_concept
        elif self.value_string:
            observation["valueString"] = self.value_string
        elif self.value_boolean is not None:
            observation["valueBoolean"] = self.value_boolean
        elif self.value_integer is not None:
            observation["valueInteger"] = self.value_integer
        elif self.value_range:
            observation["valueRange"] = self.value_range
        elif self.value_ratio:
            observation["valueRatio"] = self.value_ratio
        elif self.value_sampled_data:
            observation["valueSampledData"] = self.value_sampled_data
        elif self.value_time:
            observation["valueTime"] = self.value_time
        elif self.value_datetime:
            observation["valueDateTime"] = self.value_datetime.isoformat()
        elif self.value_period:
            observation["valuePeriod"] = self.value_period

        # Interpretación
        if self.interpretation:
            observation["interpretation"] = self.interpretation

        # Notas
        if self.note:
            observation["note"] = self.note

        # Método
        if self.method:
            observation["method"] = self.method

        # Sitio corporal
        if self.body_site:
            observation["bodySite"] = self.body_site

        # Rango de referencia
        if self.reference_range:
            observation["referenceRange"] = self.reference_range

        # Componentes
        if self.component:
            observation["component"] = self.component

        # Derivado de
        if self.derived_from:
            observation["derivedFrom"] = self.derived_from

        return observation
