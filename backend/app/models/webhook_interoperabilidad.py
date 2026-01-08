"""
Modelo de Webhooks para Interoperabilidad
Sistema de suscripciones a eventos y notificaciones automáticas
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Text,
    Integer,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class EventoWebhook(str, enum.Enum):
    """Eventos disponibles para suscripción"""

    SOLICITUD_CREADA = "solicitud.creada"
    SOLICITUD_APROBADA = "solicitud.aprobada"
    SOLICITUD_RECHAZADA = "solicitud.rechazada"
    SOLICITUD_COMPLETADA = "solicitud.completada"
    SOLICITUD_ERROR = "solicitud.error"
    INSTITUCION_CREADA = "institucion.creada"
    INSTITUCION_ACTUALIZADA = "institucion.actualizada"
    INSTITUCION_DESACTIVADA = "institucion.desactivada"
    CONSENTIMIENTO_CREADO = "consentimiento.creado"
    CONSENTIMIENTO_REVOCADO = "consentimiento.revocado"
    CONSENTIMIENTO_EXPIRANDO = "consentimiento.expirando"
    BUNDLE_FHIR_GENERADO = "bundle.generado"
    HISTORIA_UNIFICADA_CREADA = "historia.creada"


class EstadoWebhook(str, enum.Enum):
    """Estado de la suscripción webhook"""

    ACTIVO = "activo"
    PAUSADO = "pausado"
    DESACTIVADO = "desactivado"
    ERROR = "error"


class WebhookSuscripcion(Base):
    """
    Suscripciones de webhooks para eventos de interoperabilidad
    """

    __tablename__ = "webhook_suscripciones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Información básica
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)

    # URL de destino
    url = Column(String(500), nullable=False)

    # Eventos suscritos (array de EventoWebhook)
    eventos = Column(
        JSONB, nullable=False
    )  # ["solicitud.creada", "solicitud.aprobada"]

    # Autenticación
    secret_key = Column(String(100), nullable=False)  # Para firmar payloads (HMAC)
    headers_adicionales = Column(JSONB, nullable=True)  # Headers HTTP personalizados

    # Configuración
    timeout_segundos = Column(Integer, default=30, nullable=False)
    reintentos_max = Column(Integer, default=3, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    estado = Column(
        SQLEnum(EstadoWebhook), default=EstadoWebhook.ACTIVO, nullable=False
    )

    # Filtros opcionales
    filtros = Column(JSONB, nullable=True)  # {"prioridad": ["alta", "urgente"]}

    # Propietario
    usuario_id = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True
    )
    institucion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("instituciones_externas.id"),
        nullable=True,
        index=True,
    )

    # Estadísticas
    total_envios = Column(Integer, default=0, nullable=False)
    total_exitosos = Column(Integer, default=0, nullable=False)
    total_fallidos = Column(Integer, default=0, nullable=False)
    ultimo_envio = Column(DateTime, nullable=True)
    ultimo_exito = Column(DateTime, nullable=True)
    ultimo_error = Column(Text, nullable=True)
    ultimo_error_fecha = Column(DateTime, nullable=True)

    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    usuario = relationship("Usuario", backref="webhooks_interoperabilidad")
    institucion = relationship("InstitucionExterna", backref="webhooks")
    entregas = relationship(
        "WebhookEntrega", back_populates="suscripcion", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<WebhookSuscripcion {self.nombre}: {len(self.eventos)} eventos>"

    def incrementar_estadisticas(self, exitoso: bool):
        """Incrementa las estadísticas de envío"""
        self.total_envios += 1
        self.ultimo_envio = datetime.utcnow()

        if exitoso:
            self.total_exitosos += 1
            self.ultimo_exito = datetime.utcnow()
            if self.estado == EstadoWebhook.ERROR:
                self.estado = EstadoWebhook.ACTIVO
        else:
            self.total_fallidos += 1

    def registrar_error(self, error: str):
        """Registra un error en el webhook"""
        self.ultimo_error = error
        self.ultimo_error_fecha = datetime.utcnow()

        # Si hay muchos errores consecutivos, marcar como error
        if self.total_fallidos > 10 and self.total_exitosos == 0:
            self.estado = EstadoWebhook.ERROR


class WebhookEntrega(Base):
    """
    Registro de entregas de webhooks
    """

    __tablename__ = "webhook_entregas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Suscripción
    suscripcion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("webhook_suscripciones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Evento
    evento = Column(String(100), nullable=False, index=True)
    payload = Column(JSONB, nullable=False)

    # Entrega
    url = Column(String(500), nullable=False)
    metodo = Column(String(10), default="POST", nullable=False)
    headers = Column(JSONB, nullable=True)

    # Resultado
    exitoso = Column(Boolean, nullable=False, index=True)
    codigo_http = Column(Integer, nullable=True)
    respuesta = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    tiempo_respuesta_ms = Column(Integer, nullable=True)

    # Reintentos
    intento = Column(Integer, default=1, nullable=False)
    max_intentos = Column(Integer, default=3, nullable=False)

    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completado_at = Column(DateTime, nullable=True)

    # Relaciones
    suscripcion = relationship("WebhookSuscripcion", back_populates="entregas")

    def __repr__(self):
        return f"<WebhookEntrega {self.evento}: {'✓' if self.exitoso else '✗'}>"

    def to_dict(self):
        """Convierte la entrega a diccionario"""
        return {
            "id": str(self.id),
            "suscripcion_id": str(self.suscripcion_id),
            "evento": self.evento,
            "payload": self.payload,
            "url": self.url,
            "exitoso": self.exitoso,
            "codigo_http": self.codigo_http,
            "respuesta": self.respuesta,
            "error": self.error,
            "tiempo_respuesta_ms": self.tiempo_respuesta_ms,
            "intento": self.intento,
            "max_intentos": self.max_intentos,
            "created_at": self.created_at.isoformat(),
            "completado_at": (
                self.completado_at.isoformat() if self.completado_at else None
            ),
        }
