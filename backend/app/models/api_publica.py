"""
Modelos para API Pública y Marketplace
"""

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Integer,
    Text,
    JSON,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class TipoEvento(str, enum.Enum):
    """Tipos de eventos para webhooks"""

    PACIENTE_CREADO = "paciente.creado"
    PACIENTE_ACTUALIZADO = "paciente.actualizado"
    CONSULTA_CREADA = "consulta.creada"
    CONSULTA_FINALIZADA = "consulta.finalizada"
    LABORATORIO_CREADO = "laboratorio.creado"
    LABORATORIO_COMPLETADO = "laboratorio.completado"
    IMAGEN_SUBIDA = "imagen.subida"
    IMAGEN_ANALIZADA = "imagen.analizada"
    FACTURA_GENERADA = "factura.generada"
    FACTURA_TIMBRADA = "factura.timbrada"
    RECETA_GENERADA = "receta.generada"
    RECETA_SURTIDA = "receta.surtida"


class EstadoPlugin(str, enum.Enum):
    """Estados de plugins en marketplace"""

    PENDIENTE = "pendiente"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    SUSPENDIDO = "suspendido"


class APIKey(Base):
    """API Keys para acceso a la API pública"""

    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text)

    # Key y secret
    key = Column(String(64), unique=True, nullable=False, index=True)
    secret_hash = Column(String(255), nullable=False)  # Hash del secret

    # Permisos
    permisos = Column(
        ARRAY(String), default=list
    )  # ["pacientes:read", "consultas:write", etc.]
    scopes = Column(ARRAY(String), default=list)  # ["read", "write", "admin"]

    # Límites de uso
    rate_limit_por_minuto = Column(Integer, default=60)
    rate_limit_por_dia = Column(Integer, default=10000)

    # Webhooks asociados
    webhook_url = Column(String(500))
    webhook_secret = Column(String(255))
    eventos_suscritos = Column(ARRAY(String), default=list)

    # Estado
    activa = Column(Boolean, default=True)
    expira_en = Column(DateTime, nullable=True)

    # Metadata
    ip_whitelist = Column(ARRAY(String), default=list)
    entorno = Column(
        String(50), default="produccion"
    )  # desarrollo, staging, produccion

    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ultimo_uso = Column(DateTime, nullable=True)
    total_requests = Column(Integer, default=0)

    # Relaciones
    logs = relationship(
        "LogAPIPublica", back_populates="api_key", cascade="all, delete-orphan"
    )


class LogAPIPublica(Base):
    """Logs de uso de la API pública"""

    __tablename__ = "logs_api_publica"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    api_key_id = Column(UUID(as_uuid=True), ForeignKey("api_keys.id"), nullable=False)

    # Request
    metodo = Column(String(10), nullable=False)  # GET, POST, PUT, DELETE
    endpoint = Column(String(500), nullable=False)
    ip_origen = Column(String(45))
    user_agent = Column(Text)

    # Response
    status_code = Column(Integer)
    tiempo_respuesta_ms = Column(Integer)

    # Datos
    request_body = Column(JSON)
    response_body = Column(JSON)
    error = Column(Text)

    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relaciones
    api_key = relationship("APIKey", back_populates="logs")


class Webhook(Base):
    """Webhooks configurados"""

    __tablename__ = "webhooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    api_key_id = Column(UUID(as_uuid=True), ForeignKey("api_keys.id"), nullable=False)

    # Configuración
    nombre = Column(String(200), nullable=False)
    url = Column(String(500), nullable=False)
    secret = Column(String(255), nullable=False)

    # Eventos
    eventos = Column(
        ARRAY(String), nullable=False
    )  # ["paciente.creado", "consulta.creada"]

    # Configuración de reintentos
    max_reintentos = Column(Integer, default=3)
    timeout_segundos = Column(Integer, default=30)

    # Estado
    activo = Column(Boolean, default=True)

    # Metadata
    headers_personalizados = Column(JSON)

    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ultimo_envio = Column(DateTime, nullable=True)
    total_envios = Column(Integer, default=0)
    total_errores = Column(Integer, default=0)

    # Relaciones
    entregas = relationship(
        "EntregaWebhook", back_populates="webhook", cascade="all, delete-orphan"
    )


class EntregaWebhook(Base):
    """Registro de entregas de webhooks"""

    __tablename__ = "entregas_webhook"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    webhook_id = Column(UUID(as_uuid=True), ForeignKey("webhooks.id"), nullable=False)

    # Evento
    evento = Column(String(100), nullable=False)
    payload = Column(JSON, nullable=False)

    # Entrega
    intento = Column(Integer, default=1)
    status_code = Column(Integer)
    tiempo_respuesta_ms = Column(Integer)

    # Resultado
    exitoso = Column(Boolean, default=False)
    error = Column(Text)
    response_body = Column(Text)

    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    proximo_reintento = Column(DateTime, nullable=True)

    # Relaciones
    webhook = relationship("Webhook", back_populates="entregas")


class Plugin(Base):
    """Plugins del marketplace"""

    __tablename__ = "plugins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Información básica
    nombre = Column(String(200), nullable=False, unique=True)
    slug = Column(String(200), nullable=False, unique=True, index=True)
    descripcion = Column(Text, nullable=False)
    descripcion_larga = Column(Text)

    # Autor
    autor = Column(String(200), nullable=False)
    email_autor = Column(String(255))
    url_autor = Column(String(500))

    # Versión
    version = Column(String(50), nullable=False)
    version_minima_ddx = Column(String(50))

    # Categoría
    categoria = Column(String(100))  # integracion, analisis, reportes, etc.
    tags = Column(ARRAY(String), default=list)

    # URLs
    url_repositorio = Column(String(500))
    url_documentacion = Column(String(500))
    url_demo = Column(String(500))
    url_icono = Column(String(500))
    screenshots = Column(ARRAY(String), default=list)

    # Instalación
    url_descarga = Column(String(500))
    hash_archivo = Column(String(255))
    tamano_bytes = Column(Integer)

    # Configuración
    requiere_api_key = Column(Boolean, default=False)
    permisos_requeridos = Column(ARRAY(String), default=list)
    configuracion_schema = Column(JSON)

    # Estado
    estado = Column(String(50), default="pendiente")
    verificado = Column(Boolean, default=False)

    # Estadísticas
    descargas = Column(Integer, default=0)
    instalaciones_activas = Column(Integer, default=0)
    calificacion_promedio = Column(Integer, default=0)  # 0-5
    total_calificaciones = Column(Integer, default=0)

    # Precio
    es_gratuito = Column(Boolean, default=True)
    precio_usd = Column(Integer, default=0)

    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fecha_aprobacion = Column(DateTime, nullable=True)

    # Relaciones
    instalaciones = relationship(
        "InstalacionPlugin", back_populates="plugin", cascade="all, delete-orphan"
    )
    resenas = relationship(
        "ResenaPlugin", back_populates="plugin", cascade="all, delete-orphan"
    )


class InstalacionPlugin(Base):
    """Instalaciones de plugins"""

    __tablename__ = "instalaciones_plugin"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plugin_id = Column(UUID(as_uuid=True), ForeignKey("plugins.id"), nullable=False)

    # Configuración
    configuracion = Column(JSON)
    api_key_id = Column(UUID(as_uuid=True), ForeignKey("api_keys.id"), nullable=True)

    # Estado
    activo = Column(Boolean, default=True)
    version_instalada = Column(String(50))

    # Auditoría
    fecha_instalacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, nullable=True)
    ultimo_uso = Column(DateTime, nullable=True)

    # Relaciones
    plugin = relationship("Plugin", back_populates="instalaciones")


class ResenaPlugin(Base):
    """Reseñas de plugins"""

    __tablename__ = "resenas_plugin"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plugin_id = Column(UUID(as_uuid=True), ForeignKey("plugins.id"), nullable=False)

    # Reseña
    calificacion = Column(Integer, nullable=False)  # 1-5
    titulo = Column(String(200))
    comentario = Column(Text)

    # Autor
    autor_nombre = Column(String(200))
    autor_email = Column(String(255))

    # Metadata
    version_plugin = Column(String(50))
    verificado = Column(Boolean, default=False)

    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    plugin = relationship("Plugin", back_populates="resenas")
