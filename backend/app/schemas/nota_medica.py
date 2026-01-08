from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class NotaMedicaBase(BaseModel):
    paciente_id: UUID
    consulta_id: Optional[UUID] = None
    hospitalizacion_id: Optional[UUID] = None
    tipo_nota: str = Field(..., description="Tipo de nota: evolucion, ingreso, alta, interconsulta, procedimiento, defuncion")
    titulo: str = Field(..., min_length=1, max_length=255)
    contenido: str = Field(..., min_length=1)


class NotaMedicaCreate(NotaMedicaBase):
    pass


class NotaMedicaUpdate(BaseModel):
    tipo_nota: Optional[str] = None
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)
    contenido: Optional[str] = Field(None, min_length=1)
    firmada: Optional[bool] = None


class NotaMedicaResponse(NotaMedicaBase):
    id: UUID
    autor_id: UUID
    fecha_nota: datetime
    firmada: bool
    created_at: datetime

    class Config:
        from_attributes = True
