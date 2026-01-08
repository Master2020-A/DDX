"""
Modelos para el módulo de Aplicación Móvil
"""

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Text,
    Integer,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum


from app.core.database import Base


# ==================== ENUMS ====================


class PlataformaMovil(str, enum.Enum):
    """Plataforma del dispositivo móvil"""

    IOS = "ios"
    ANDROID = "android"


class EstadoDispositivo(str, enum.Enum):
    """Estado del dispositivo móvil"""

    ACTIVO = "activo"
    INACTIVO = "inactivo"
    BLOQUEADO = "bloqueado"
    REVOCADO = "revocado"


class TipoNotificacion(str, enum.Enum):
    """Tipo de notificación push"""

    CITA = "cita"
    RECORDATORIO = "recordatorio"
    RESULTADO = "resultado"
    MENSAJE = "mensaje"
    ALERTA = "alerta"
    SISTEMA = "sistema"


class EstadoNotificacion(str, enum.Enum):
    """Estado de la notificación"""

    PENDIENTE = "pendiente"
    ENVIADA = "enviada"
    ENTREGADA = "entregada"
    LEIDA = "leida"
    FALLIDA = "fallida"


class TipoDocumento(str, enum.Enum):
    """Tipo de documento escaneado"""

    IDENTIFICACION = "identificacion"
    RECETA = "receta"
    LABORATORIO = "laboratorio"
    ESTUDIO = "estudio"
    CONSENTIMIENTO = "consentimiento"
    OTRO = "otro"


class EstadoSincronizacion(str, enum.Enum):
    """Estado de sincronización"""

    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"
    FALLIDA = "fallida"


# ==================== MODELOS ====================


class DispositivoMovil(Base):
    """
    Dispositivos móviles registrados
    """

    __tablename__ = "dispositivos_moviles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Información del dispositivo
    plataforma = Column(SQLEnum(PlataformaMovil), nullable=False)
    modelo = Column(String(100))
    version_os = Column(String(50))
    version_app = Column(String(50))
    device_id = Column(String(255), unique=True, nullable=False, index=True)

    # Token para notificaciones push
    push_token = Column(String(500))
    push_token_actualizado = Column(DateTime)

    # Estado y configuración
    estado = Column(
        SQLEnum(EstadoDispositivo), default=EstadoDispositivo.ACTIVO, nullable=False
    )
    notificaciones_habilitadas = Column(Boolean, default=True)
    biometria_habilitada = Column(Boolean, default=False)
    sincronizacion_automatica = Column(Boolean, default=True)

    # Información de red
    ip_registro = Column(String(45))
    user_agent = Column(Text)

    # Fechas
    ultimo_acceso = Column(DateTime)
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_revocacion = Column(DateTime)

    # Metadata
    metadata_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NotificacionPush(Base):
    """
    Notificaciones push enviadas a dispositivos móviles
    """

    __tablename__ = "notificaciones_push"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dispositivo_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    usuario_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Contenido de la notificación
    tipo = Column(SQLEnum(TipoNotificacion), nullable=False)
    titulo = Column(String(200), nullable=False)
    mensaje = Column(Text, nullable=False)

    # Datos adicionales (deep linking, etc.)
    datos = Column(JSON)
    accion_url = Column(String(500))

    # Estado
    estado = Column(
        SQLEnum(EstadoNotificacion),
        default=EstadoNotificacion.PENDIENTE,
        nullable=False,
    )

    # Prioridad (alta, normal, baja)
    prioridad = Column(String(20), default="normal")

    # Programación
    programada_para = Column(DateTime)

    # Fechas de eventos
    fecha_envio = Column(DateTime)
    fecha_entrega = Column(DateTime)
    fecha_lectura = Column(DateTime)

    # Error (si falló)
    mensaje_error = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DocumentoEscaneado(Base):
    """
    Documentos escaneados desde la app móvil
    """

    __tablename__ = "documentos_escaneados"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dispositivo_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    usuario_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    paciente_id = Column(UUID(as_uuid=True), index=True)

    # Información del documento
    tipo = Column(SQLEnum(TipoDocumento), nullable=False)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text)

    # Archivo
    ruta_archivo = Column(String(500), nullable=False)
    ruta_thumbnail = Column(String(500))
    tamano_bytes = Column(Integer)
    mime_type = Column(String(100))

    # OCR y procesamiento
    texto_extraido = Column(Text)
    ocr_procesado = Column(Boolean, default=False)
    confianza_ocr = Column(Integer)  # 0-100

    # Metadata de captura
    latitud = Column(String(50))
    longitud = Column(String(50))
    fecha_captura = Column(DateTime)

    # Firma digital (si aplica)
    firmado = Column(Boolean, default=False)
    firma_biometrica = Column(JSON)  # Datos de la firma biométrica
    fecha_firma = Column(DateTime)

    # Sincronización
    sincronizado = Column(Boolean, default=False)
    fecha_sincronizacion = Column(DateTime)

    # Metadata
    metadata_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SincronizacionOffline(Base):
    """
    Cola de sincronización para datos offline
    """

    __tablename__ = "sincronizacion_offline"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dispositivo_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    usuario_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Información de la operación
    entidad = Column(String(100), nullable=False)  # consulta, paciente, nota, etc.
    operacion = Column(String(20), nullable=False)  # create, update, delete
    entidad_id = Column(UUID(as_uuid=True))

    # Datos
    datos = Column(JSON, nullable=False)
    datos_anteriores = Column(JSON)  # Para rollback

    # Estado
    estado = Column(
        SQLEnum(EstadoSincronizacion),
        default=EstadoSincronizacion.PENDIENTE,
        nullable=False,
    )

    # Prioridad (1-10, 10 más alta)
    prioridad = Column(Integer, default=5)

    # Intentos
    intentos = Column(Integer, default=0)
    max_intentos = Column(Integer, default=3)

    # Fechas
    fecha_creacion_local = Column(DateTime, nullable=False)
    fecha_procesamiento = Column(DateTime)
    fecha_completado = Column(DateTime)

    # Error
    mensaje_error = Column(Text)

    # Conflicto (si hay versión más reciente en servidor)
    conflicto = Column(Boolean, default=False)
    datos_servidor = Column(JSON)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CitaMovil(Base):
    """
    Citas agendadas desde la app móvil
    """

    __tablename__ = "citas_moviles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    medico_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    dispositivo_id = Column(UUID(as_uuid=True), index=True)

    # Información de la cita
    fecha_hora = Column(DateTime, nullable=False, index=True)
    duracion_minutos = Column(Integer, default=30)
    motivo = Column(Text)
    notas = Column(Text)

    # Estado
    confirmada = Column(Boolean, default=False)
    fecha_confirmacion = Column(DateTime)

    cancelada = Column(Boolean, default=False)
    fecha_cancelacion = Column(DateTime)
    motivo_cancelacion = Column(Text)

    # Recordatorios
    recordatorio_enviado = Column(Boolean, default=False)
    fecha_recordatorio = Column(DateTime)

    # Ubicación (si es telemedicina)
    es_telemedicina = Column(Boolean, default=False)
    url_videollamada = Column(String(500))

    # Metadata
    metadata_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConfiguracionAppMovil(Base):
    """
    Configuración de la aplicación móvil por usuario
    """

    __tablename__ = "configuracion_app_movil"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)

    # Notificaciones
    notificaciones_citas = Column(Boolean, default=True)
    notificaciones_resultados = Column(Boolean, default=True)
    notificaciones_mensajes = Column(Boolean, default=True)
    notificaciones_recordatorios = Column(Boolean, default=True)

    # Tiempo de anticipación para recordatorios (minutos)
    recordatorio_citas_minutos = Column(Integer, default=60)

    # Sincronización
    sincronizar_solo_wifi = Column(Boolean, default=False)
    sincronizar_automaticamente = Column(Boolean, default=True)
    intervalo_sincronizacion_minutos = Column(Integer, default=15)

    # Seguridad
    requerir_biometria = Column(Boolean, default=False)
    timeout_sesion_minutos = Column(Integer, default=30)

    # Preferencias de UI
    tema = Column(String(20), default="auto")  # light, dark, auto
    idioma = Column(String(10), default="es")

    # Almacenamiento
    limpiar_cache_automaticamente = Column(Boolean, default=True)
    dias_retener_datos_offline = Column(Integer, default=30)

    # Metadata
    metadata_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SesionMovil(Base):
    """
    Sesiones activas de la app móvil
    """

    __tablename__ = "sesiones_moviles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dispositivo_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    usuario_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Token de sesión
    token_sesion = Column(String(500), unique=True, nullable=False, index=True)
    refresh_token = Column(String(500), unique=True)

    # Estado
    activa = Column(Boolean, default=True)

    # Fechas
    fecha_inicio = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_expiracion = Column(DateTime, nullable=False)
    fecha_ultimo_uso = Column(DateTime)
    fecha_cierre = Column(DateTime)

    # Información de conexión
    ip_address = Column(String(45))
    user_agent = Column(Text)

    # Metadata
    metadata_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
