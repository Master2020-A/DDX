# app/schemas/telemedicina.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from enum import Enum


# ============================================================
# ENUMS
# ============================================================


class EstadoConsultaEnum(str, Enum):
    PROGRAMADA = "programada"
    EN_ESPERA = "en_espera"
    EN_CURSO = "en_curso"
    FINALIZADA = "finalizada"
    CANCELADA = "cancelada"
    NO_REALIZADA = "no_realizada"


class TipoConsultaEnum(str, Enum):
    VIDEOLLAMADA = "videollamada"
    AUDIO = "audio"
    CHAT = "chat"


class TipoMensajeEnum(str, Enum):
    TEXTO = "texto"
    IMAGEN = "imagen"
    ARCHIVO = "archivo"
    SISTEMA = "sistema"


class EmisorTipoEnum(str, Enum):
    MEDICO = "medico"
    PACIENTE = "paciente"
    SISTEMA = "sistema"


class TipoSeguimientoEnum(str, Enum):
    CITA_CONTROL = "cita_control"
    RECORDATORIO_MEDICAMENTO = "recordatorio_medicamento"
    VERIFICACION_SINTOMAS = "verificacion_sintomas"
    ENVIO_RESULTADOS = "envio_resultados"
    OTRO = "otro"


# ============================================================
# CONSULTA REMOTA
# ============================================================


class ConsultaRemotaBase(BaseModel):
    paciente_id: UUID
    fecha_programada: datetime
    motivo_consulta: Optional[str] = None
    tipo: TipoConsultaEnum = TipoConsultaEnum.VIDEOLLAMADA


class ConsultaRemotaCreate(ConsultaRemotaBase):
    medico_id: Optional[UUID] = None  # Si no se envía, usa el usuario actual


class ConsultaRemotaUpdate(BaseModel):
    fecha_programada: Optional[datetime] = None
    motivo_consulta: Optional[str] = None
    tipo: Optional[TipoConsultaEnum] = None
    estado: Optional[EstadoConsultaEnum] = None


class ConsultaRemotaResponse(BaseModel):
    id: UUID
    paciente_id: UUID
    medico_id: UUID
    sala_id: str
    tipo: TipoConsultaEnum
    estado: EstadoConsultaEnum
    fecha_programada: datetime
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    duracion_minutos: Optional[int] = None
    motivo_consulta: Optional[str] = None
    notas_medico: Optional[str] = None
    diagnostico_preliminar: Optional[str] = None
    plan_tratamiento: Optional[str] = None
    requiere_seguimiento: bool = False
    url_sala_medico: Optional[str] = None
    url_sala_paciente: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Datos relacionados opcionales
    paciente_nombre: Optional[str] = None
    medico_nombre: Optional[str] = None

    class Config:
        from_attributes = True


class ConsultaRemotaDetalle(ConsultaRemotaResponse):
    """Respuesta con detalles completos incluyendo relaciones"""

    mensajes_count: int = 0
    tiene_prescripcion: bool = False
    tiene_seguimiento: bool = False


class IniciarConsultaResponse(BaseModel):
    id: UUID
    estado: EstadoConsultaEnum
    fecha_inicio: datetime
    sala_id: str
    url_sala_medico: str
    url_sala_paciente: str


class FinalizarConsultaRequest(BaseModel):
    notas_medico: Optional[str] = None
    diagnostico_preliminar: Optional[str] = None
    plan_tratamiento: Optional[str] = None
    requiere_seguimiento: bool = False


class FinalizarConsultaResponse(BaseModel):
    id: UUID
    estado: EstadoConsultaEnum
    fecha_fin: datetime
    duracion_minutos: int
    notas_medico: Optional[str] = None
    diagnostico_preliminar: Optional[str] = None


# ============================================================
# MENSAJES CHAT
# ============================================================


class MensajeChatBase(BaseModel):
    contenido: str
    tipo_mensaje: TipoMensajeEnum = TipoMensajeEnum.TEXTO


class MensajeChatCreate(MensajeChatBase):
    consulta_remota_id: UUID
    archivo_url: Optional[str] = None
    archivo_nombre: Optional[str] = None


class MensajeChatResponse(BaseModel):
    id: UUID
    consulta_remota_id: UUID
    emisor_id: UUID
    emisor_tipo: EmisorTipoEnum
    contenido: str
    tipo_mensaje: TipoMensajeEnum
    archivo_url: Optional[str] = None
    archivo_nombre: Optional[str] = None
    leido: bool
    fecha_leido: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# PRESCRIPCIÓN ELECTRÓNICA
# ============================================================


class MedicamentoSchema(BaseModel):
    nombre: str
    dosis: str
    frecuencia: str
    duracion: str
    via_administracion: str = "oral"
    indicaciones: Optional[str] = None


class PrescripcionCreate(BaseModel):
    consulta_remota_id: Optional[UUID] = None
    paciente_id: UUID
    diagnostico: str
    codigo_cie10: Optional[str] = None
    medicamentos: List[MedicamentoSchema]
    indicaciones_generales: Optional[str] = None
    dias_vigencia: int = Field(default=30, ge=1, le=365)


class PrescripcionResponse(BaseModel):
    id: UUID
    numero_receta: str
    consulta_remota_id: Optional[UUID] = None
    paciente_id: UUID
    medico_id: UUID
    diagnostico: str
    codigo_cie10: Optional[str] = None
    medicamentos: List[dict]
    indicaciones_generales: Optional[str] = None
    fecha_emision: datetime
    fecha_vigencia: datetime
    activa: bool
    codigo_verificacion: str
    created_at: datetime

    # Datos relacionados
    paciente_nombre: Optional[str] = None
    medico_nombre: Optional[str] = None
    medico_cedula: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================
# SEGUIMIENTO POST-CONSULTA
# ============================================================


class SeguimientoCreate(BaseModel):
    consulta_remota_id: Optional[UUID] = None
    paciente_id: UUID
    tipo: TipoSeguimientoEnum
    titulo: str
    mensaje: str
    fecha_programada: datetime
    metodo_notificacion: str = "email"


class SeguimientoResponse(BaseModel):
    id: UUID
    consulta_remota_id: Optional[UUID] = None
    paciente_id: UUID
    medico_id: UUID
    tipo: TipoSeguimientoEnum
    titulo: str
    mensaje: str
    fecha_programada: datetime
    metodo_notificacion: str
    enviado: bool
    fecha_enviado: Optional[datetime] = None
    respuesta_paciente: Optional[str] = None
    fecha_respuesta: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SeguimientoUpdate(BaseModel):
    titulo: Optional[str] = None
    mensaje: Optional[str] = None
    fecha_programada: Optional[datetime] = None
    metodo_notificacion: Optional[str] = None


# ============================================================
# ESTADÍSTICAS
# ============================================================


class EstadisticasTelemedicina(BaseModel):
    total_consultas: int
    consultas_programadas: int
    consultas_realizadas: int
    consultas_canceladas: int
    duracion_promedio_minutos: float
    prescripciones_emitidas: int
    seguimientos_programados: int
