"""
Modelos de base de datos para el módulo de Backups y Recuperación
"""

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer,
    Boolean,
    Text,
    Enum as SQLEnum,
    BigInteger,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

from app.core.database import Base


class TipoBackup(str, enum.Enum):
    """Tipos de backup"""

    COMPLETO = "completo"
    INCREMENTAL = "incremental"
    DIFERENCIAL = "diferencial"
    TRANSACCIONAL = "transaccional"


class EstadoBackup(str, enum.Enum):
    """Estados de un backup"""

    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    COMPLETADO = "completado"
    FALLIDO = "fallido"
    CANCELADO = "cancelado"


class TipoRestauracion(str, enum.Enum):
    """Tipos de restauración"""

    COMPLETA = "completa"
    POINT_IN_TIME = "point_in_time"
    TABLA_ESPECIFICA = "tabla_especifica"
    DATOS_ESPECIFICOS = "datos_especificos"


class EstadoRestauracion(str, enum.Enum):
    """Estados de una restauración"""

    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    COMPLETADO = "completado"
    FALLIDO = "fallido"
    CANCELADO = "cancelado"


class NivelSeveridad(str, enum.Enum):
    """Niveles de severidad para alertas"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Backup(Base):
    """
    Modelo para registrar backups de la base de datos
    """

    __tablename__ = "backups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tipo = Column(SQLEnum(TipoBackup), nullable=False, default=TipoBackup.COMPLETO)
    estado = Column(
        SQLEnum(EstadoBackup), nullable=False, default=EstadoBackup.PENDIENTE
    )

    # Información del backup
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text)
    ruta_archivo = Column(String(500), nullable=False)
    tamano_bytes = Column(BigInteger)  # Tamaño en bytes

    # Metadata del backup
    base_datos = Column(String(100), nullable=False)
    version_postgresql = Column(String(50))
    metodo_backup = Column(String(100))  # pg_dump, pg_basebackup, etc.

    # Checksums para verificar integridad
    checksum_md5 = Column(String(32))
    checksum_sha256 = Column(String(64))

    # Información de compresión
    comprimido = Column(Boolean, default=True)
    algoritmo_compresion = Column(String(50))  # gzip, bzip2, etc.

    # Información de encriptación
    encriptado = Column(Boolean, default=False)
    algoritmo_encriptacion = Column(String(50))  # AES-256, etc.

    # Tiempos
    fecha_inicio = Column(DateTime, nullable=False, default=datetime.utcnow)
    fecha_fin = Column(DateTime)
    duracion_segundos = Column(Integer)

    # Información de retención
    fecha_expiracion = Column(DateTime)
    retencion_dias = Column(Integer, default=30)

    # Backup automático o manual
    automatico = Column(Boolean, default=False)
    programacion_id = Column(
        UUID(as_uuid=True)
    )  # ID de la programación si es automático

    # Información de error (si falló)
    mensaje_error = Column(Text)

    # Metadata adicional
    metadata_json = Column(JSON)  # Información adicional en JSON

    # Auditoría
    usuario_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProgramacionBackup(Base):
    """
    Modelo para programar backups automáticos
    """

    __tablename__ = "programacion_backups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text)
    activo = Column(Boolean, default=True)

    # Tipo de backup
    tipo_backup = Column(
        SQLEnum(TipoBackup), nullable=False, default=TipoBackup.COMPLETO
    )

    # Programación (cron expression)
    cron_expresion = Column(
        String(100), nullable=False
    )  # Ej: "0 2 * * *" (diario a las 2am)
    zona_horaria = Column(String(50), default="UTC")

    # Configuración de retención
    retencion_dias = Column(Integer, default=30)
    max_backups_mantener = Column(Integer, default=10)

    # Configuración de backup
    base_datos = Column(String(100), nullable=False)
    ruta_destino = Column(String(500), nullable=False)
    compresion = Column(Boolean, default=True)
    encriptacion = Column(Boolean, default=False)

    # Notificaciones
    notificar_exito = Column(Boolean, default=False)
    notificar_fallo = Column(Boolean, default=True)
    emails_notificacion = Column(JSON)  # Lista de emails

    # Última ejecución
    ultima_ejecucion = Column(DateTime)
    proximo_ejecucion = Column(DateTime)

    # Auditoría
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))


class Restauracion(Base):
    """
    Modelo para registrar restauraciones de backups
    """

    __tablename__ = "restauraciones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    backup_id = Column(UUID(as_uuid=True), nullable=False)
    tipo = Column(
        SQLEnum(TipoRestauracion), nullable=False, default=TipoRestauracion.COMPLETA
    )
    estado = Column(
        SQLEnum(EstadoRestauracion),
        nullable=False,
        default=EstadoRestauracion.PENDIENTE,
    )

    # Información de la restauración
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text)
    motivo = Column(Text)  # Razón de la restauración

    # Point-in-time recovery
    punto_tiempo = Column(DateTime)  # Para restauración point-in-time

    # Restauración selectiva
    tablas_restaurar = Column(JSON)  # Lista de tablas a restaurar
    datos_especificos = Column(JSON)  # Filtros para datos específicos

    # Base de datos destino
    base_datos_destino = Column(String(100), nullable=False)
    sobrescribir = Column(Boolean, default=False)

    # Tiempos
    fecha_inicio = Column(DateTime, nullable=False, default=datetime.utcnow)
    fecha_fin = Column(DateTime)
    duracion_segundos = Column(Integer)

    # Información de error (si falló)
    mensaje_error = Column(Text)

    # Validación post-restauración
    validacion_exitosa = Column(Boolean)
    resultado_validacion = Column(JSON)

    # Metadata adicional
    metadata_json = Column(JSON)

    # Auditoría
    usuario_id = Column(UUID(as_uuid=True), nullable=False)
    aprobado_por = Column(UUID(as_uuid=True))  # Requiere aprobación
    fecha_aprobacion = Column(DateTime)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ReplicacionBD(Base):
    """
    Modelo para configurar y monitorear replicación de base de datos
    """

    __tablename__ = "replicacion_bd"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text)
    activo = Column(Boolean, default=True)

    # Configuración de replicación
    tipo_replicacion = Column(String(50), nullable=False)  # streaming, logical, etc.
    servidor_primario = Column(String(255), nullable=False)
    servidor_replica = Column(String(255), nullable=False)
    puerto = Column(Integer, default=5432)

    # Estado de replicación
    estado_conexion = Column(String(50))  # conectado, desconectado, error
    lag_replicacion_bytes = Column(BigInteger)  # Retraso en bytes
    lag_replicacion_segundos = Column(Integer)  # Retraso en segundos

    # Monitoreo
    ultima_verificacion = Column(DateTime)
    ultima_sincronizacion = Column(DateTime)

    # Alertas
    umbral_lag_bytes = Column(BigInteger, default=10485760)  # 10MB
    umbral_lag_segundos = Column(Integer, default=60)  # 60 segundos

    # Metadata
    metadata_json = Column(JSON)

    # Auditoría
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MonitoreoSalud(Base):
    """
    Modelo para monitorear la salud del sistema
    """

    __tablename__ = "monitoreo_salud"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Métricas de base de datos
    conexiones_activas = Column(Integer)
    conexiones_maximas = Column(Integer)
    tamano_bd_bytes = Column(BigInteger)
    transacciones_por_segundo = Column(Integer)

    # Métricas de sistema
    uso_cpu_porcentaje = Column(Integer)
    uso_memoria_porcentaje = Column(Integer)
    uso_disco_porcentaje = Column(Integer)
    espacio_disco_libre_gb = Column(Integer)

    # Métricas de aplicación
    tiempo_respuesta_promedio_ms = Column(Integer)
    requests_por_minuto = Column(Integer)
    errores_por_minuto = Column(Integer)

    # Estado general
    estado_sistema = Column(String(50))  # healthy, degraded, critical
    disponibilidad_porcentaje = Column(Integer)  # Para calcular uptime

    # Alertas generadas
    alertas_activas = Column(Integer, default=0)

    # Metadata
    metadata_json = Column(JSON)


class AlertaBackup(Base):
    """
    Modelo para registrar alertas del sistema de backups
    """

    __tablename__ = "alertas_backup"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    severidad = Column(
        SQLEnum(NivelSeveridad), nullable=False, default=NivelSeveridad.INFO
    )
    tipo = Column(
        String(100), nullable=False
    )  # backup_fallido, espacio_disco, replicacion, etc.

    # Información de la alerta
    titulo = Column(String(255), nullable=False)
    mensaje = Column(Text, nullable=False)

    # Relacionado con
    backup_id = Column(UUID(as_uuid=True))
    restauracion_id = Column(UUID(as_uuid=True))
    replicacion_id = Column(UUID(as_uuid=True))

    # Estado
    activa = Column(Boolean, default=True)
    fecha_resolucion = Column(DateTime)
    resuelto_por = Column(UUID(as_uuid=True))
    notas_resolucion = Column(Text)

    # Notificaciones
    notificado = Column(Boolean, default=False)
    fecha_notificacion = Column(DateTime)

    # Metadata
    metadata_json = Column(JSON)

    # Auditoría
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PlanRecuperacion(Base):
    """
    Modelo para definir planes de recuperación ante desastres
    """

    __tablename__ = "planes_recuperacion"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text)
    activo = Column(Boolean, default=True)

    # Objetivos
    rto_minutos = Column(Integer, nullable=False)  # Recovery Time Objective
    rpo_minutos = Column(Integer, nullable=False)  # Recovery Point Objective

    # Procedimientos
    procedimientos = Column(JSON, nullable=False)  # Lista de pasos a seguir

    # Contactos de emergencia
    contactos_emergencia = Column(JSON)  # Lista de contactos

    # Recursos necesarios
    recursos_requeridos = Column(JSON)

    # Pruebas del plan
    ultima_prueba = Column(DateTime)
    proxima_prueba = Column(DateTime)
    frecuencia_prueba_dias = Column(Integer, default=90)
    resultado_ultima_prueba = Column(Text)

    # Metadata
    metadata_json = Column(JSON)

    # Auditoría
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))
