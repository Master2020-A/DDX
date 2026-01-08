from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.consulta import TipoConsultaEnum, EstadoConsultaEnum


class ConsultaBase(BaseModel):
    motivo_consulta: str = Field(..., min_length=1)
    sintomas: List[str] = Field(..., min_items=1)
    tipo_consulta: Optional[TipoConsultaEnum] = TipoConsultaEnum.PRIMERA_VEZ


class ConsultaCreate(ConsultaBase):
    paciente_id: UUID


class ConsultaUpdate(BaseModel):
    motivo_consulta: Optional[str] = None
    sintomas: Optional[List[str]] = None
    estado: Optional[EstadoConsultaEnum] = None


class ConsultaResponse(ConsultaBase):
    id: UUID
    paciente_id: UUID
    medico_id: UUID
    fecha_hora: datetime
    estado: EstadoConsultaEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
