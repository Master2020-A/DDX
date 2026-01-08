from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.diagnostico import TipoDiagnosticoEnum, NivelConfianzaEnum, EstadoDiagnosticoEnum


class DiagnosticoBase(BaseModel):
    tipo: TipoDiagnosticoEnum
    descripcion: str = Field(..., min_length=1)
    codigo_cie10: Optional[str] = None
    confianza_nivel: Optional[NivelConfianzaEnum] = None
    justificacion: Optional[str] = None
    evidencias: Optional[List[str]] = []


class DiagnosticoCreate(DiagnosticoBase):
    consulta_id: UUID


class DiagnosticoResponse(DiagnosticoBase):
    id: UUID
    consulta_id: UUID
    medico_id: UUID
    estado: EstadoDiagnosticoEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
