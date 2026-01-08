from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from app.models.prueba import TipoPruebaEnum, UrgenciaEnum, EstadoPruebaEnum


class PruebaMedicaBase(BaseModel):
    nombre_prueba: str = Field(..., min_length=1, max_length=255)
    tipo_prueba: TipoPruebaEnum
    descripcion: Optional[str] = None
    urgencia: Optional[UrgenciaEnum] = UrgenciaEnum.NORMAL


class PruebaMedicaCreate(PruebaMedicaBase):
    consulta_id: UUID
    diagnostico_id: Optional[UUID] = None
    fecha_programada: Optional[datetime] = None
    laboratorio_externo: Optional[str] = None


class PruebaMedicaResponse(PruebaMedicaBase):
    id: UUID
    consulta_id: UUID
    diagnostico_id: Optional[UUID]
    estado: EstadoPruebaEnum
    fecha_solicitud: datetime
    fecha_programada: Optional[datetime]
    fecha_realizada: Optional[datetime]
    solicitado_por: UUID
    laboratorio_externo: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResultadoPruebaCreate(BaseModel):
    prueba_id: UUID
    resultado_texto: Optional[str] = None
    resultado_numerico: Optional[Decimal] = None
    unidad_medida: Optional[str] = None
    valores_referencia: Optional[str] = None
    interpretacion: Optional[str] = None
    anormal: bool = False
    archivo_url: Optional[str] = None
    archivo_tipo: Optional[str] = None
    notas: Optional[str] = None
