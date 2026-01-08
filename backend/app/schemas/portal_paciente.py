# app/schemas/portal_paciente.py

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from uuid import UUID


# ============================================================================
# CITAS
# ============================================================================


class CitaPacienteCreate(BaseModel):
    paciente_id: UUID
    medico_id: Optional[UUID] = None
    tipo_cita: str = "primera_vez"
    especialidad_solicitada: Optional[str] = None
    motivo_consulta: str
    fecha_solicitada: date
    hora_solicitada: Optional[time] = None
    notas_paciente: Optional[str] = None


class CitaPacienteUpdate(BaseModel):
    medico_id: Optional[UUID] = None
    fecha_confirmada: Optional[datetime] = None
    estado: Optional[str] = None
    notas_medico: Optional[str] = None
    motivo_cancelacion: Optional[str] = None


class CitaPacienteResponse(BaseModel):
    id: UUID
    paciente_id: UUID
    medico_id: Optional[UUID]
    tipo_cita: str
    especialidad_solicitada: Optional[str]
    motivo_consulta: str
    fecha_solicitada: date
    hora_solicitada: Optional[time]
    fecha_confirmada: Optional[datetime]
    duracion_minutos: int
    estado: str
    notas_paciente: Optional[str]
    notas_medico: Optional[str]
    recordatorio_enviado: bool
    fecha_cancelacion: Optional[datetime]
    motivo_cancelacion: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# SOLICITUDES DE ESTUDIOS
# ============================================================================


class SolicitudEstudioCreate(BaseModel):
    paciente_id: UUID
    medico_solicitante_id: Optional[UUID] = None
    tipo_estudio: str = "laboratorio"
    nombre_estudio: str
    descripcion: Optional[str] = None
    indicaciones_especiales: Optional[str] = None
    prioridad: str = "normal"
    notas_paciente: Optional[str] = None


class SolicitudEstudioUpdate(BaseModel):
    estado: Optional[str] = None
    medico_autorizador_id: Optional[UUID] = None
    fecha_programada: Optional[datetime] = None
    fecha_realizacion: Optional[datetime] = None
    resultado_disponible: Optional[bool] = None
    url_resultado: Optional[str] = None
    notas_autorizacion: Optional[str] = None
    motivo_rechazo: Optional[str] = None


class SolicitudEstudioResponse(BaseModel):
    id: UUID
    paciente_id: UUID
    medico_solicitante_id: Optional[UUID]
    medico_autorizador_id: Optional[UUID]
    tipo_estudio: str
    nombre_estudio: str
    descripcion: Optional[str]
    indicaciones_especiales: Optional[str]
    estado: str
    prioridad: str
    fecha_solicitud: datetime
    fecha_autorizacion: Optional[datetime]
    fecha_programada: Optional[datetime]
    fecha_realizacion: Optional[datetime]
    resultado_disponible: bool
    url_resultado: Optional[str]
    notas_paciente: Optional[str]
    notas_autorizacion: Optional[str]
    motivo_rechazo: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# PAGOS
# ============================================================================


class PagoServicioCreate(BaseModel):
    paciente_id: UUID
    cita_id: Optional[UUID] = None
    solicitud_estudio_id: Optional[UUID] = None
    concepto: str
    descripcion: Optional[str] = None
    monto: float = Field(..., gt=0)
    moneda: str = "MXN"
    metodo_pago: str = "tarjeta_credito"


class PagoServicioUpdate(BaseModel):
    estado: Optional[str] = None
    referencia_pago: Optional[str] = None
    fecha_procesado: Optional[datetime] = None
    fecha_completado: Optional[datetime] = None
    datos_transaccion: Optional[Dict[str, Any]] = None
    comprobante_url: Optional[str] = None


class PagoServicioResponse(BaseModel):
    id: UUID
    paciente_id: UUID
    cita_id: Optional[UUID]
    solicitud_estudio_id: Optional[UUID]
    concepto: str
    descripcion: Optional[str]
    monto: float
    moneda: str
    metodo_pago: str
    referencia_pago: Optional[str]
    estado: str
    fecha_pago: datetime
    fecha_procesado: Optional[datetime]
    fecha_completado: Optional[datetime]
    comprobante_url: Optional[str]
    reembolsado: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# MENSAJERÍA
# ============================================================================


class MensajePacienteMedicoCreate(BaseModel):
    paciente_id: UUID
    medico_id: UUID
    remitente_tipo: str  # 'paciente' o 'medico'
    asunto: Optional[str] = None
    mensaje: str
    archivos_adjuntos: Optional[List[str]] = None
    mensaje_padre_id: Optional[UUID] = None


class MensajePacienteMedicoUpdate(BaseModel):
    leido: Optional[bool] = None
    fecha_lectura: Optional[datetime] = None


class MensajePacienteMedicoResponse(BaseModel):
    id: UUID
    paciente_id: UUID
    medico_id: UUID
    remitente_tipo: str
    asunto: Optional[str]
    mensaje: str
    archivos_adjuntos: Optional[List[str]]
    estado: str
    leido: bool
    fecha_lectura: Optional[datetime]
    mensaje_padre_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# RECORDATORIOS DE MEDICAMENTOS
# ============================================================================


class RecordatorioMedicamentoCreate(BaseModel):
    paciente_id: UUID
    receta_id: Optional[UUID] = None
    nombre_medicamento: str
    dosis: str
    via_administracion: Optional[str] = None
    indicaciones: Optional[str] = None
    frecuencia: str = "diario"
    horarios: List[str]  # ["08:00", "20:00"]
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    duracion_dias: Optional[int] = None
    notificar_email: bool = True
    notificar_sms: bool = False
    notificar_push: bool = True


class RecordatorioMedicamentoUpdate(BaseModel):
    activo: Optional[bool] = None
    pausado: Optional[bool] = None
    horarios: Optional[List[str]] = None
    fecha_fin: Optional[date] = None
    notificar_email: Optional[bool] = None
    notificar_sms: Optional[bool] = None
    notificar_push: Optional[bool] = None


class RecordatorioMedicamentoResponse(BaseModel):
    id: UUID
    paciente_id: UUID
    receta_id: Optional[UUID]
    nombre_medicamento: str
    dosis: str
    via_administracion: Optional[str]
    indicaciones: Optional[str]
    frecuencia: str
    horarios: List[str]
    fecha_inicio: date
    fecha_fin: Optional[date]
    duracion_dias: Optional[int]
    activo: bool
    pausado: bool
    notificar_email: bool
    notificar_sms: bool
    notificar_push: bool
    ultima_toma_registrada: Optional[datetime]
    tomas_registradas: int
    tomas_omitidas: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# REGISTRO DE TOMA DE MEDICAMENTOS
# ============================================================================


class RegistroTomaMedicamentoCreate(BaseModel):
    recordatorio_id: UUID
    fecha_programada: datetime
    fecha_real: Optional[datetime] = None
    tomado: bool = False
    omitido: bool = False
    motivo_omision: Optional[str] = None
    notas: Optional[str] = None
    efectos_secundarios: Optional[str] = None


class RegistroTomaMedicamentoResponse(BaseModel):
    id: UUID
    recordatorio_id: UUID
    fecha_programada: datetime
    fecha_real: Optional[datetime]
    tomado: bool
    omitido: bool
    motivo_omision: Optional[str]
    notas: Optional[str]
    efectos_secundarios: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# CONFIGURACIÓN DEL PORTAL
# ============================================================================


class ConfiguracionPortalCreate(BaseModel):
    paciente_id: UUID
    notificaciones_email: bool = True
    notificaciones_sms: bool = False
    notificaciones_push: bool = True
    compartir_datos_investigacion: bool = False
    mostrar_perfil_publico: bool = False
    idioma: str = "es"
    tema: str = "light"
    zona_horaria: str = "America/Mexico_City"
    recordatorios_citas: bool = True
    recordatorios_medicamentos: bool = True
    recordatorios_estudios: bool = True


class ConfiguracionPortalUpdate(BaseModel):
    notificaciones_email: Optional[bool] = None
    notificaciones_sms: Optional[bool] = None
    notificaciones_push: Optional[bool] = None
    compartir_datos_investigacion: Optional[bool] = None
    mostrar_perfil_publico: Optional[bool] = None
    idioma: Optional[str] = None
    tema: Optional[str] = None
    zona_horaria: Optional[str] = None
    recordatorios_citas: Optional[bool] = None
    recordatorios_medicamentos: Optional[bool] = None
    recordatorios_estudios: Optional[bool] = None


class ConfiguracionPortalResponse(BaseModel):
    id: UUID
    paciente_id: UUID
    notificaciones_email: bool
    notificaciones_sms: bool
    notificaciones_push: bool
    compartir_datos_investigacion: bool
    mostrar_perfil_publico: bool
    idioma: str
    tema: str
    zona_horaria: str
    recordatorios_citas: bool
    recordatorios_medicamentos: bool
    recordatorios_estudios: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# ACCESO A EXPEDIENTE
# ============================================================================


class AccesoExpedienteResponse(BaseModel):
    id: UUID
    paciente_id: UUID
    usuario_id: Optional[UUID]
    tipo_acceso: str
    seccion_accedida: Optional[str]
    recurso_id: Optional[UUID]
    ip_address: Optional[str]
    user_agent: Optional[str]
    duracion_segundos: Optional[int]
    fecha_acceso: datetime

    class Config:
        from_attributes = True


# ============================================================================
# DASHBOARD DEL PORTAL
# ============================================================================


class DashboardPortalResponse(BaseModel):
    """Dashboard completo del portal del paciente"""

    # Estadísticas generales
    total_citas: int
    citas_pendientes: int
    proxima_cita: Optional[CitaPacienteResponse]

    # Estudios
    total_estudios: int
    estudios_pendientes: int
    resultados_disponibles: int

    # Medicamentos
    medicamentos_activos: int
    proxima_toma: Optional[datetime]

    # Mensajes
    mensajes_no_leidos: int

    # Pagos
    pagos_pendientes: int
    total_pagado_mes: float

    class Config:
        from_attributes = True


# ============================================================================
# EXPEDIENTE COMPLETO
# ============================================================================


class ExpedienteCompletoResponse(BaseModel):
    """Expediente médico completo del paciente"""

    # Información básica
    paciente_id: UUID
    numero_expediente: str
    nombre_completo: str
    fecha_nacimiento: date
    edad: int
    genero: Optional[str]
    tipo_sangre: Optional[str]
    alergias: Optional[List[str]]

    # Resumen de actividad
    total_consultas: int
    ultima_consulta: Optional[datetime]
    total_estudios: int
    total_medicamentos: int

    # Datos disponibles
    tiene_laboratorios: bool
    tiene_imagenes: bool
    tiene_recetas: bool
    tiene_hospitalizaciones: bool

    class Config:
        from_attributes = True
