from pydantic import BaseModel, Field, validator
from typing import Optional, List, Union, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class ObservationStatusEnum(str, Enum):
    REGISTERED = "registered"
    PRELIMINARY = "preliminary"
    FINAL = "final"
    AMENDED = "amended"
    CORRECTED = "corrected"
    CANCELLED = "cancelled"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"


class ObservationCategoryEnum(str, Enum):
    VITAL_SIGNS = "vital-signs"
    LABORATORY = "laboratory"
    IMAGING = "imaging"
    PROCEDURE = "procedure"
    SURVEY = "survey"
    EXAM = "exam"
    THERAPY = "therapy"
    ACTIVITY = "activity"


# Tipos FHIR básicos
class Coding(BaseModel):
    system: Optional[str] = None
    version: Optional[str] = None
    code: Optional[str] = None
    display: Optional[str] = None
    userSelected: Optional[bool] = None


class CodeableConcept(BaseModel):
    coding: Optional[List[Coding]] = None
    text: Optional[str] = None


class Identifier(BaseModel):
    use: Optional[str] = None
    type: Optional[CodeableConcept] = None
    system: Optional[str] = None
    value: Optional[str] = None
    period: Optional[dict] = None
    assigner: Optional[dict] = None


class Reference(BaseModel):
    reference: Optional[str] = None
    type: Optional[str] = None
    identifier: Optional[Identifier] = None
    display: Optional[str] = None


class Quantity(BaseModel):
    value: Optional[float] = None
    comparator: Optional[str] = None
    unit: Optional[str] = None
    system: Optional[str] = None
    code: Optional[str] = None


class Range(BaseModel):
    low: Optional[Quantity] = None
    high: Optional[Quantity] = None


class Ratio(BaseModel):
    numerator: Optional[Quantity] = None
    denominator: Optional[Quantity] = None


class Period(BaseModel):
    start: Optional[datetime] = None
    end: Optional[datetime] = None


class Annotation(BaseModel):
    authorReference: Optional[Reference] = None
    authorString: Optional[str] = None
    time: Optional[datetime] = None
    text: str


class ReferenceRange(BaseModel):
    low: Optional[Quantity] = None
    high: Optional[Quantity] = None
    type: Optional[CodeableConcept] = None
    appliesTo: Optional[List[CodeableConcept]] = None
    age: Optional[Range] = None
    text: Optional[str] = None


class ObservationComponent(BaseModel):
    code: CodeableConcept
    valueQuantity: Optional[Quantity] = None
    valueCodeableConcept: Optional[CodeableConcept] = None
    valueString: Optional[str] = None
    valueBoolean: Optional[bool] = None
    valueInteger: Optional[int] = None
    valueRange: Optional[Range] = None
    valueRatio: Optional[Ratio] = None
    valueTime: Optional[str] = None
    valueDateTime: Optional[datetime] = None
    valuePeriod: Optional[Period] = None
    dataAbsentReason: Optional[CodeableConcept] = None
    interpretation: Optional[List[CodeableConcept]] = None
    referenceRange: Optional[List[ReferenceRange]] = None


# Schemas principales
class ObservationCreate(BaseModel):
    """Schema para crear una nueva Observation"""

    identifier: Optional[List[Identifier]] = None
    status: ObservationStatusEnum = ObservationStatusEnum.FINAL
    category: Optional[List[str]] = None
    code: CodeableConcept
    subject_type: str = "Patient"
    subject_id: UUID
    encounter_id: Optional[UUID] = None
    effective_datetime: Optional[datetime] = None
    effective_period_start: Optional[datetime] = None
    effective_period_end: Optional[datetime] = None
    issued: Optional[datetime] = None
    performer: Optional[List[Reference]] = None

    # Valores (solo uno debe estar presente)
    value_quantity: Optional[Quantity] = None
    value_codeable_concept: Optional[CodeableConcept] = None
    value_string: Optional[str] = None
    value_boolean: Optional[bool] = None
    value_integer: Optional[int] = None
    value_range: Optional[Range] = None
    value_ratio: Optional[Ratio] = None
    value_time: Optional[str] = None
    value_datetime: Optional[datetime] = None
    value_period: Optional[Period] = None

    interpretation: Optional[List[CodeableConcept]] = None
    note: Optional[List[Annotation]] = None
    method: Optional[CodeableConcept] = None
    body_site: Optional[CodeableConcept] = None
    reference_range: Optional[List[ReferenceRange]] = None
    component: Optional[List[ObservationComponent]] = None
    derived_from: Optional[List[Reference]] = None

    # Metadatos de origen
    source_type: Optional[str] = None
    source_id: Optional[UUID] = None

    class Config:
        use_enum_values = True


class ObservationUpdate(BaseModel):
    """Schema para actualizar una Observation"""

    status: Optional[ObservationStatusEnum] = None
    category: Optional[List[str]] = None
    code: Optional[CodeableConcept] = None
    effective_datetime: Optional[datetime] = None
    effective_period_start: Optional[datetime] = None
    effective_period_end: Optional[datetime] = None
    issued: Optional[datetime] = None
    performer: Optional[List[Reference]] = None

    value_quantity: Optional[Quantity] = None
    value_codeable_concept: Optional[CodeableConcept] = None
    value_string: Optional[str] = None
    value_boolean: Optional[bool] = None
    value_integer: Optional[int] = None
    value_range: Optional[Range] = None
    value_ratio: Optional[Ratio] = None
    value_time: Optional[str] = None
    value_datetime: Optional[datetime] = None
    value_period: Optional[Period] = None

    interpretation: Optional[List[CodeableConcept]] = None
    note: Optional[List[Annotation]] = None
    method: Optional[CodeableConcept] = None
    body_site: Optional[CodeableConcept] = None
    reference_range: Optional[List[ReferenceRange]] = None
    component: Optional[List[ObservationComponent]] = None

    class Config:
        use_enum_values = True


class ObservationResponse(BaseModel):
    """Schema de respuesta para Observation"""

    id: UUID
    identifier: Optional[List[dict]] = None
    status: str
    category: Optional[List[str]] = None
    code: dict
    subject_type: str
    subject_id: UUID
    encounter_id: Optional[UUID] = None
    effective_datetime: Optional[datetime] = None
    effective_period_start: Optional[datetime] = None
    effective_period_end: Optional[datetime] = None
    issued: Optional[datetime] = None
    performer: Optional[List[dict]] = None

    value_quantity: Optional[dict] = None
    value_codeable_concept: Optional[dict] = None
    value_string: Optional[str] = None
    value_boolean: Optional[bool] = None
    value_integer: Optional[int] = None
    value_range: Optional[dict] = None
    value_ratio: Optional[dict] = None
    value_time: Optional[str] = None
    value_datetime: Optional[datetime] = None
    value_period: Optional[dict] = None

    interpretation: Optional[List[dict]] = None
    note: Optional[List[dict]] = None
    method: Optional[dict] = None
    body_site: Optional[dict] = None
    reference_range: Optional[List[dict]] = None
    component: Optional[List[dict]] = None
    derived_from: Optional[List[dict]] = None

    source_type: Optional[str] = None
    source_id: Optional[UUID] = None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ObservationFHIR(BaseModel):
    """Schema FHIR R4 completo para Observation"""

    resourceType: str = "Observation"
    id: str
    meta: Optional[dict] = None
    identifier: Optional[List[dict]] = None
    status: str
    category: Optional[List[dict]] = None
    code: dict
    subject: dict
    encounter: Optional[dict] = None
    effectiveDateTime: Optional[str] = None
    effectivePeriod: Optional[dict] = None
    issued: Optional[str] = None
    performer: Optional[List[dict]] = None
    valueQuantity: Optional[dict] = None
    valueCodeableConcept: Optional[dict] = None
    valueString: Optional[str] = None
    valueBoolean: Optional[bool] = None
    valueInteger: Optional[int] = None
    valueRange: Optional[dict] = None
    valueRatio: Optional[dict] = None
    valueTime: Optional[str] = None
    valueDateTime: Optional[str] = None
    valuePeriod: Optional[dict] = None
    interpretation: Optional[List[dict]] = None
    note: Optional[List[dict]] = None
    method: Optional[dict] = None
    bodySite: Optional[dict] = None
    referenceRange: Optional[List[dict]] = None
    component: Optional[List[dict]] = None
    derivedFrom: Optional[List[dict]] = None


class ObservationBundle(BaseModel):
    """Bundle de Observations FHIR"""

    resourceType: str = "Bundle"
    type: str = "searchset"
    total: int
    entry: List[dict]
