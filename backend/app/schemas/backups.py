"""
Schemas de Pydantic para el módulo de Backups y Recuperación
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.models.backups import (
    TipoBackup,
    EstadoBackup,
    TipoRestauracion,
    EstadoRestauracion,
    NivelSeveridad,
)


# ==================== BACKUP SCHEMAS ====================


class BackupCreate(BaseModel):
    tipo: TipoBackup = TipoBackup.COMPLETO
    nombre: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = None


class BackupResponse(BaseModel):
    id: UUID
    tipo: TipoBackup
    estado: EstadoBackup
    nombre: str
    descripcion: Optional[str]
    ruta_archivo: str
    tamano_bytes: Optional[int]
    base_datos: str
    version_postgresql: Optional[str]
    checksum_md5: Optional[str]
    checksum_sha256: Optional[str]
    comprimido: bool
    algoritmo_compresion: Optional[str]
    encriptado: bool
    fecha_inicio: datetime
    fecha_fin: Optional[datetime]
    duracion_segundos: Optional[int]
    fecha_expiracion: Optional[datetime]
    retencion_dias: int
    automatico: bool
    mensaje_error: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ==================== PROGRAMACIÓN SCHEMAS ====================


class ProgramacionBackupCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = None
    tipo_backup: TipoBackup = TipoBackup.COMPLETO
    cron_expresion: str = Field(..., description="Expresión cron para programación")
    zona_horaria: str = "UTC"
    retencion_dias: int = Field(30, ge=1, le=365)
    max_backups_mantener: int = Field(10, ge=1, le=100)
    compresion: bool = True
    encriptacion: bool = False
    notificar_exito: bool = False
    notificar_fallo: bool = True
    emails_notificacion: Optional[List[str]] = None


class ProgramacionBackupUpdate(BaseModel):
    activo: Optional[bool] = None
    cron_expresion: Optional[str] = None
    retencion_dias: Optional[int] = Field(None, ge=1, le=365)
    notificar_exito: Optional[bool] = None
    notificar_fallo: Optional[bool] = None
    emails_notificacion: Optional[List[str]] = None


class ProgramacionBackupResponse(BaseModel):
    id: UUID
    nombre: str
    descripcion: Optional[str]
    activo: bool
    tipo_backup: TipoBackup
    cron_expresion: str
    zona_horaria: str
    retencion_dias: int
    max_backups_mantener: int
    base_datos: str
    ruta_destino: str
    compresion: bool
    encriptacion: bool
    notificar_exito: bool
    notificar_fallo: bool
    emails_notificacion: Optional[List[str]]
    ultima_ejecucion: Optional[datetime]
    proximo_ejecucion: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ==================== RESTAURACIÓN SCHEMAS ====================


class RestauracionCreate(BaseModel):
    backup_id: UUID
    tipo: TipoRestauracion = TipoRestauracion.COMPLETA
    nombre: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = None
    motivo: str = Field(..., min_length=1, description="Razón de la restauración")
    punto_tiempo: Optional[datetime] = None
    tablas_restaurar: Optional[List[str]] = None
    sobrescribir: bool = False


class RestauracionResponse(BaseModel):
    id: UUID
    backup_id: UUID
    tipo: TipoRestauracion
    estado: EstadoRestauracion
    nombre: str
    descripcion: Optional[str]
    motivo: str
    punto_tiempo: Optional[datetime]
    tablas_restaurar: Optional[List[str]]
    base_datos_destino: str
    sobrescribir: bool
    fecha_inicio: datetime
    fecha_fin: Optional[datetime]
    duracion_segundos: Optional[int]
    mensaje_error: Optional[str]
    validacion_exitosa: Optional[bool]
    resultado_validacion: Optional[Dict[str, Any]]
    usuario_id: UUID
    aprobado_por: Optional[UUID]
    fecha_aprobacion: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ==================== REPLICACIÓN SCHEMAS ====================


class ReplicacionBDCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = None
    tipo_replicacion: str = Field(..., description="streaming, logical, etc.")
    servidor_primario: str
    servidor_replica: str
    puerto: int = 5432
    umbral_lag_bytes: int = 10485760  # 10MB
    umbral_lag_segundos: int = 60


class ReplicacionBDResponse(BaseModel):
    id: UUID
    nombre: str
    descripcion: Optional[str]
    activo: bool
    tipo_replicacion: str
    servidor_primario: str
    servidor_replica: str
    puerto: int
    estado_conexion: Optional[str]
    lag_replicacion_bytes: Optional[int]
    lag_replicacion_segundos: Optional[int]
    ultima_verificacion: Optional[datetime]
    ultima_sincronizacion: Optional[datetime]
    umbral_lag_bytes: int
    umbral_lag_segundos: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ==================== MONITOREO SCHEMAS ====================


class MonitoreoSaludResponse(BaseModel):
    id: UUID
    timestamp: datetime
    conexiones_activas: Optional[int]
    conexiones_maximas: Optional[int]
    tamano_bd_bytes: Optional[int]
    transacciones_por_segundo: Optional[int]
    uso_cpu_porcentaje: Optional[int]
    uso_memoria_porcentaje: Optional[int]
    uso_disco_porcentaje: Optional[int]
    espacio_disco_libre_gb: Optional[int]
    tiempo_respuesta_promedio_ms: Optional[int]
    requests_por_minuto: Optional[int]
    errores_por_minuto: Optional[int]
    estado_sistema: Optional[str]
    disponibilidad_porcentaje: Optional[int]
    alertas_activas: int

    class Config:
        from_attributes = True


# ==================== ALERTA SCHEMAS ====================


class AlertaBackupResponse(BaseModel):
    id: UUID
    severidad: NivelSeveridad
    tipo: str
    titulo: str
    mensaje: str
    backup_id: Optional[UUID]
    restauracion_id: Optional[UUID]
    replicacion_id: Optional[UUID]
    activa: bool
    fecha_resolucion: Optional[datetime]
    resuelto_por: Optional[UUID]
    notas_resolucion: Optional[str]
    notificado: bool
    fecha_notificacion: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AlertaResolverRequest(BaseModel):
    notas: str = Field(..., min_length=1, description="Notas sobre la resolución")


# ==================== PLAN RECUPERACIÓN SCHEMAS ====================


class PlanRecuperacionCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = None
    rto_minutos: int = Field(
        ..., ge=1, description="Recovery Time Objective en minutos"
    )
    rpo_minutos: int = Field(
        ..., ge=1, description="Recovery Point Objective en minutos"
    )
    procedimientos: List[Dict[str, Any]] = Field(
        ..., description="Lista de pasos a seguir"
    )
    contactos_emergencia: Optional[List[Dict[str, str]]] = None
    recursos_requeridos: Optional[List[str]] = None
    frecuencia_prueba_dias: int = Field(90, ge=1, le=365)


class PlanRecuperacionResponse(BaseModel):
    id: UUID
    nombre: str
    descripcion: Optional[str]
    activo: bool
    rto_minutos: int
    rpo_minutos: int
    procedimientos: List[Dict[str, Any]]
    contactos_emergencia: Optional[List[Dict[str, str]]]
    recursos_requeridos: Optional[List[str]]
    ultima_prueba: Optional[datetime]
    proxima_prueba: Optional[datetime]
    frecuencia_prueba_dias: int
    resultado_ultima_prueba: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ==================== ESTADÍSTICAS SCHEMAS ====================


class EstadisticasBackupsResponse(BaseModel):
    total_backups: int
    backups_completados: int
    backups_fallidos: int
    ultimo_backup: Dict[str, Any]
    tamano_total_gb: float
    programaciones_activas: int


class EstadoSistemaResponse(BaseModel):
    estado: str  # healthy, degraded, critical
    disponibilidad_porcentaje: float
    uptime_dias: int
    ultimo_backup_exitoso: Optional[datetime]
    alertas_activas: int
    replicacion_activa: bool
    espacio_disco_libre_gb: int
