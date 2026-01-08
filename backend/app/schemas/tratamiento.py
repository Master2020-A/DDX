from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime, date
from app.models.tratamiento import TipoTratamientoEnum, EstadoTratamientoEnum


class TratamientoBase(BaseModel):
    descripcion: str = Field(..., min_length=1)
    tipo_tratamiento: TipoTratamientoEnum
    objetivo: Optional[str] = None
    duracion_dias: Optional[int] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    notas: Optional[str] = None


class TratamientoCreate(TratamientoBase):
    consulta_id: UUID
    diagnostico_id: Optional[UUID] = None


class TratamientoResponse(TratamientoBase):
    id: UUID
    consulta_id: UUID
    diagnostico_id: Optional[UUID]
    estado: EstadoTratamientoEnum
    prescrito_por: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PrescripcionCreate(BaseModel):
    tratamiento_id: UUID
    medicamento: str = Field(..., min_length=1, max_length=255)
    principio_activo: Optional[str] = None
    dosis: str = Field(..., min_length=1, max_length=100)
    frecuencia: str = Field(..., min_length=1, max_length=100)
    via_administracion: Optional[str] = None
    duracion_dias: Optional[int] = None
    cantidad_total: Optional[str] = None
    instrucciones_especiales: Optional[str] = None
