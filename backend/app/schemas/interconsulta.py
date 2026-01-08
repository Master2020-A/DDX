"""
Schemas de Pydantic para Interconsultas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ==================== INTERCONSULTA ====================

class InterconsultaBase(BaseModel):
    especialidad_requerida: str
    motivo_solicitud: str
    antecedentes_relevantes: Optional[str] = None
    estudios_adjuntos: Optional[List[str]] = None
    urgencia: str = "normal"
    fecha_programada: Optional[datetime] = None
    prioridad_clinica: int = 1


class InterconsultaCreate(InterconsultaBase):
    paciente_id: UUID
    consulta_id: Optional[UUID] = None
    hospitalizacion_id: Optional[UUID] = None
    especialista_id: Optional[UUID] = None


class InterconsultaUpdate(BaseModel):
    especialista_id: Optional[UUID] = None
    estado: Optional[str] = None
    fecha_programada: Optional[datetime] = None
    fecha_realizada: Optional[datetime] = None
    diagnostico_especialista: Optional[str] = None
    hallazgos: Optional[str] = None
    recomendaciones: Optional[str] = None
    plan_tratamiento: Optional[str] = None
    requiere_seguimiento: Optional[bool] = None
    fecha_seguimiento: Optional[datetime] = None
    motivo_rechazo: Optional[str] = None
    notas_internas: Optional[str] = None


class InterconsultaResponse(InterconsultaBase):
    id: UUID
    paciente_id: UUID
    consulta_id: Optional[UUID]
    hospitalizacion_id: Optional[UUID]
    medico_solicitante_id: UUID
    especialista_id: Optional[UUID]
    estado: str
    fecha_solicitud: datetime
    fecha_aceptacion: Optional[datetime]
    fecha_realizada: Optional[datetime]
    fecha_completada: Optional[datetime]
    diagnostico_especialista: Optional[str]
    hallazgos: Optional[str]
    recomendaciones: Optional[str]
    plan_tratamiento: Optional[str]
    requiere_seguimiento: bool
    fecha_seguimiento: Optional[datetime]
    motivo_rechazo: Optional[str]
    prioridad_clinica: int
    notas_internas: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== NOTIFICACIÓN ====================

class NotificacionInterconsultaBase(BaseModel):
    tipo: str
    titulo: str
    mensaje: str


class NotificacionInterconsultaCreate(NotificacionInterconsultaBase):
    interconsulta_id: UUID
    medico_destinatario_id: UUID


class NotificacionInterconsultaResponse(NotificacionInterconsultaBase):
    id: UUID
    interconsulta_id: UUID
    medico_destinatario_id: UUID
    leida: bool
    fecha_lectura: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== MENSAJE (CHAT) ====================

class MensajeInterconsultaBase(BaseModel):
    mensaje: str
    archivos_adjuntos: Optional[List[str]] = None


class MensajeInterconsultaCreate(MensajeInterconsultaBase):
    interconsulta_id: UUID


class MensajeInterconsultaResponse(MensajeInterconsultaBase):
    id: UUID
    interconsulta_id: UUID
    medico_emisor_id: UUID
    leido: bool
    fecha_lectura: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== SEGUIMIENTO ====================

class SeguimientoInterconsultaBase(BaseModel):
    tipo_seguimiento: str
    observaciones: str
    estado_paciente: Optional[str] = None
    cambios_tratamiento: Optional[str] = None
    proxima_revision: Optional[datetime] = None


class SeguimientoInterconsultaCreate(SeguimientoInterconsultaBase):
    interconsulta_id: UUID


class SeguimientoInterconsultaResponse(SeguimientoInterconsultaBase):
    id: UUID
    interconsulta_id: UUID
    medico_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== RESPUESTAS ESPECIALES ====================

class AceptarInterconsultaRequest(BaseModel):
    fecha_programada: Optional[datetime] = None
    notas: Optional[str] = None


class RechazarInterconsultaRequest(BaseModel):
    motivo_rechazo: str


class ResponderInterconsultaRequest(BaseModel):
    diagnostico_especialista: str
    hallazgos: Optional[str] = None
    recomendaciones: Optional[str] = None
    plan_tratamiento: Optional[str] = None
    requiere_seguimiento: bool = False
    fecha_seguimiento: Optional[datetime] = None


class EstadisticasInterconsultasResponse(BaseModel):
    total_solicitadas: int
    pendientes: int
    aceptadas: int
    completadas: int
    rechazadas: int
    por_especialidad: dict
    por_urgencia: dict
    tiempo_promedio_respuesta: Optional[float] = None  # en horas
