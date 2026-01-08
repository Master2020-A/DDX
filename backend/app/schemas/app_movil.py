"""
Schemas de Pydantic para el módulo de Aplicación Móvil
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.models.app_movil import (
    PlataformaMovil,
    EstadoDispositivo,
    TipoNotificacion,
    EstadoNotificacion,
    TipoDocumento,
    EstadoSincronizacion,
)


# ==================== DISPOSITIVO MÓVIL ====================


class DispositivoMovilCreate(BaseModel):
    plataforma: PlataformaMovil
    modelo: Optional[str] = None
    version_os: Optional[str] = None
    version_app: Optional[str] = None
    device_id: str
    push_token: Optional[str] = None
    ip_registro: Optional[str] = None
    user_agent: Optional[str] = None


class DispositivoMovilUpdate(BaseModel):
    push_token: Optional[str] = None
    version_app: Optional[str] = None
    notificaciones_habilitadas: Optional[bool] = None
    biometria_habilitada: Optional[bool] = None
    sincronizacion_automatica: Optional[bool] = None


class DispositivoMovilResponse(BaseModel):
    id: UUID
    usuario_id: UUID
    plataforma: PlataformaMovil
    modelo: Optional[str]
    version_os: Optional[str]
    version_app: Optional[str]
    device_id: str
    estado: EstadoDispositivo
    notificaciones_habilitadas: bool
    biometria_habilitada: bool
    sincronizacion_automatica: bool
    ultimo_acceso: Optional[datetime]
    fecha_registro: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== NOTIFICACIÓN PUSH ====================


class NotificacionPushCreate(BaseModel):
    dispositivo_id: Optional[UUID] = None
    usuario_id: UUID
    tipo: TipoNotificacion
    titulo: str = Field(..., max_length=200)
    mensaje: str
    datos: Optional[Dict[str, Any]] = None
    accion_url: Optional[str] = None
    prioridad: Optional[str] = "normal"
    programada_para: Optional[datetime] = None


class NotificacionPushResponse(BaseModel):
    id: UUID
    dispositivo_id: Optional[UUID]
    usuario_id: UUID
    tipo: TipoNotificacion
    titulo: str
    mensaje: str
    datos: Optional[Dict[str, Any]]
    accion_url: Optional[str]
    estado: EstadoNotificacion
    prioridad: str
    programada_para: Optional[datetime]
    fecha_envio: Optional[datetime]
    fecha_entrega: Optional[datetime]
    fecha_lectura: Optional[datetime]
    mensaje_error: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class NotificacionPushEnviar(BaseModel):
    titulo: str = Field(..., max_length=200)
    mensaje: str
    tipo: TipoNotificacion = TipoNotificacion.SISTEMA
    usuarios_ids: Optional[List[UUID]] = None
    dispositivos_ids: Optional[List[UUID]] = None
    datos: Optional[Dict[str, Any]] = None
    accion_url: Optional[str] = None
    prioridad: Optional[str] = "normal"


# ==================== DOCUMENTO ESCANEADO ====================


class DocumentoEscaneadoCreate(BaseModel):
    tipo: TipoDocumento
    nombre: str = Field(..., max_length=255)
    descripcion: Optional[str] = None
    paciente_id: Optional[UUID] = None
    latitud: Optional[str] = None
    longitud: Optional[str] = None
    fecha_captura: Optional[datetime] = None


class DocumentoEscaneadoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    texto_extraido: Optional[str] = None
    ocr_procesado: Optional[bool] = None
    confianza_ocr: Optional[int] = None


class DocumentoEscaneadoResponse(BaseModel):
    id: UUID
    dispositivo_id: UUID
    usuario_id: UUID
    paciente_id: Optional[UUID]
    tipo: TipoDocumento
    nombre: str
    descripcion: Optional[str]
    ruta_archivo: str
    ruta_thumbnail: Optional[str]
    tamano_bytes: Optional[int]
    mime_type: Optional[str]
    texto_extraido: Optional[str]
    ocr_procesado: bool
    confianza_ocr: Optional[int]
    firmado: bool
    fecha_firma: Optional[datetime]
    sincronizado: bool
    fecha_sincronizacion: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class FirmarDocumentoRequest(BaseModel):
    firma_biometrica: Dict[str, Any]


# ==================== SINCRONIZACIÓN OFFLINE ====================


class SincronizacionOfflineCreate(BaseModel):
    entidad: str = Field(..., max_length=100)
    operacion: str = Field(..., max_length=20)
    entidad_id: Optional[UUID] = None
    datos: Dict[str, Any]
    datos_anteriores: Optional[Dict[str, Any]] = None
    prioridad: Optional[int] = 5
    fecha_creacion_local: datetime


class SincronizacionOfflineResponse(BaseModel):
    id: UUID
    dispositivo_id: UUID
    usuario_id: UUID
    entidad: str
    operacion: str
    entidad_id: Optional[UUID]
    datos: Dict[str, Any]
    estado: EstadoSincronizacion
    prioridad: int
    intentos: int
    max_intentos: int
    fecha_creacion_local: datetime
    fecha_procesamiento: Optional[datetime]
    fecha_completado: Optional[datetime]
    mensaje_error: Optional[str]
    conflicto: bool
    datos_servidor: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class SincronizarRequest(BaseModel):
    operaciones: List[SincronizacionOfflineCreate]


class SincronizarResponse(BaseModel):
    total: int
    exitosas: int
    fallidas: int
    conflictos: int
    resultados: List[SincronizacionOfflineResponse]


# ==================== CITA MÓVIL ====================


class CitaMovilCreate(BaseModel):
    paciente_id: UUID
    medico_id: UUID
    fecha_hora: datetime
    duracion_minutos: Optional[int] = 30
    motivo: Optional[str] = None
    notas: Optional[str] = None
    es_telemedicina: Optional[bool] = False


class CitaMovilUpdate(BaseModel):
    fecha_hora: Optional[datetime] = None
    duracion_minutos: Optional[int] = None
    motivo: Optional[str] = None
    notas: Optional[str] = None
    confirmada: Optional[bool] = None
    cancelada: Optional[bool] = None
    motivo_cancelacion: Optional[str] = None


class CitaMovilResponse(BaseModel):
    id: UUID
    paciente_id: UUID
    medico_id: UUID
    dispositivo_id: Optional[UUID]
    fecha_hora: datetime
    duracion_minutos: int
    motivo: Optional[str]
    notas: Optional[str]
    confirmada: bool
    fecha_confirmacion: Optional[datetime]
    cancelada: bool
    fecha_cancelacion: Optional[datetime]
    motivo_cancelacion: Optional[str]
    recordatorio_enviado: bool
    fecha_recordatorio: Optional[datetime]
    es_telemedicina: bool
    url_videollamada: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== CONFIGURACIÓN APP MÓVIL ====================


class ConfiguracionAppMovilUpdate(BaseModel):
    notificaciones_citas: Optional[bool] = None
    notificaciones_resultados: Optional[bool] = None
    notificaciones_mensajes: Optional[bool] = None
    notificaciones_recordatorios: Optional[bool] = None
    recordatorio_citas_minutos: Optional[int] = None
    sincronizar_solo_wifi: Optional[bool] = None
    sincronizar_automaticamente: Optional[bool] = None
    intervalo_sincronizacion_minutos: Optional[int] = None
    requerir_biometria: Optional[bool] = None
    timeout_sesion_minutos: Optional[int] = None
    tema: Optional[str] = None
    idioma: Optional[str] = None
    limpiar_cache_automaticamente: Optional[bool] = None
    dias_retener_datos_offline: Optional[int] = None


class ConfiguracionAppMovilResponse(BaseModel):
    id: UUID
    usuario_id: UUID
    notificaciones_citas: bool
    notificaciones_resultados: bool
    notificaciones_mensajes: bool
    notificaciones_recordatorios: bool
    recordatorio_citas_minutos: int
    sincronizar_solo_wifi: bool
    sincronizar_automaticamente: bool
    intervalo_sincronizacion_minutos: int
    requerir_biometria: bool
    timeout_sesion_minutos: int
    tema: str
    idioma: str
    limpiar_cache_automaticamente: bool
    dias_retener_datos_offline: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== SESIÓN MÓVIL ====================


class SesionMovilCreate(BaseModel):
    device_id: str
    push_token: Optional[str] = None


class SesionMovilResponse(BaseModel):
    id: UUID
    dispositivo_id: UUID
    usuario_id: UUID
    token_sesion: str
    refresh_token: Optional[str]
    activa: bool
    fecha_inicio: datetime
    fecha_expiracion: datetime
    fecha_ultimo_uso: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ==================== ESTADÍSTICAS ====================


class EstadisticasAppMovilResponse(BaseModel):
    total_dispositivos: int
    dispositivos_activos: int
    dispositivos_ios: int
    dispositivos_android: int
    notificaciones_enviadas_hoy: int
    notificaciones_pendientes: int
    documentos_escaneados_mes: int
    citas_programadas: int
    sincronizaciones_pendientes: int


class EstadoSincronizacionResponse(BaseModel):
    ultima_sincronizacion: Optional[datetime]
    operaciones_pendientes: int
    operaciones_en_progreso: int
    operaciones_fallidas: int
    conflictos_sin_resolver: int
