from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# ============================================================================
# SIGNOS VITALES
# ============================================================================

class SignosVitalesBase(BaseModel):
    temperatura: Optional[float] = Field(None, description="Temperatura en °C")
    presion_arterial_sistolica: Optional[int] = Field(None, description="Presión arterial sistólica en mmHg")
    presion_arterial_diastolica: Optional[int] = Field(None, description="Presión arterial diastólica en mmHg")
    frecuencia_cardiaca: Optional[int] = Field(None, description="Frecuencia cardíaca en lpm")
    frecuencia_respiratoria: Optional[int] = Field(None, description="Frecuencia respiratoria en rpm")
    saturacion_oxigeno: Optional[float] = Field(None, description="Saturación de oxígeno en %")
    peso: Optional[float] = Field(None, description="Peso en kg")
    talla: Optional[float] = Field(None, description="Talla en cm")
    imc: Optional[float] = Field(None, description="Índice de masa corporal")
    perimetro_abdominal: Optional[float] = Field(None, description="Perímetro abdominal en cm")
    glucosa: Optional[float] = Field(None, description="Glucosa en mg/dL")


# ============================================================================
# EXPEDIENTE CLÍNICO
# ============================================================================

class ExpedienteClinicoBase(BaseModel):
    paciente_id: UUID
    consulta_id: Optional[UUID] = None
    antecedentes_personales: Optional[str] = None
    antecedentes_familiares: Optional[str] = None
    padecimientos_cronicos: Optional[List[str]] = []
    cirugias_previas: Optional[List[str]] = []
    medicamentos_actuales: Optional[List[str]] = []
    habitos: Optional[str] = None
    signos_vitales: Optional[Dict[str, Any]] = None
    exploracion_fisica: Optional[str] = None
    notas: Optional[str] = None


class ExpedienteClinicoCreate(ExpedienteClinicoBase):
    pass


class ExpedienteClinicoUpdate(BaseModel):
    antecedentes_personales: Optional[str] = None
    antecedentes_familiares: Optional[str] = None
    padecimientos_cronicos: Optional[List[str]] = None
    cirugias_previas: Optional[List[str]] = None
    medicamentos_actuales: Optional[List[str]] = None
    habitos: Optional[str] = None
    signos_vitales: Optional[Dict[str, Any]] = None
    exploracion_fisica: Optional[str] = None
    notas: Optional[str] = None


class ExpedienteClinicoResponse(ExpedienteClinicoBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# PADECIMIENTO CRÓNICO
# ============================================================================

class PadecimientoCronicoBase(BaseModel):
    nombre: str = Field(..., description="Nombre del padecimiento")
    fecha_diagnostico: Optional[str] = Field(None, description="Fecha de diagnóstico")
    tratamiento_actual: Optional[str] = Field(None, description="Tratamiento actual")
    observaciones: Optional[str] = None


# ============================================================================
# CIRUGÍA PREVIA
# ============================================================================

class CirugiaPreviaBase(BaseModel):
    nombre: str = Field(..., description="Nombre de la cirugía")
    fecha: Optional[str] = Field(None, description="Fecha de la cirugía")
    hospital: Optional[str] = Field(None, description="Hospital donde se realizó")
    observaciones: Optional[str] = None


# ============================================================================
# MEDICAMENTO ACTUAL
# ============================================================================

class MedicamentoActualBase(BaseModel):
    nombre: str = Field(..., description="Nombre del medicamento")
    dosis: Optional[str] = Field(None, description="Dosis")
    frecuencia: Optional[str] = Field(None, description="Frecuencia de administración")
    via_administracion: Optional[str] = Field(None, description="Vía de administración")
    fecha_inicio: Optional[str] = Field(None, description="Fecha de inicio")
    observaciones: Optional[str] = None
