"""
Modelo de Notificaciones para Interoperabilidad
Sistema de notificaciones push en tiempo real
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class TipoNotificacion(str, enum.Enum):
    """Tipos de notificaciones"""

    SOLICITUD_NUEVA = "solicitud_nueva"
    SOLICITUD_APROBADA = "solicitud_aprobada"
    SOLICITUD_RECHAZADA = "solicitud_rechazada"
    SOLICITUD_COMPLETADA = "solicitud_completada"
    SOLICITUD_ERROR = "solicitud_error"
    CONSENTIMIENTO_EXPIRA = "consentimiento_expira"
    CONSENTIMIENTO_EXPIRADO = "consentimiento_expirado"
    INSTITUCION_NUEVA = "institucion_nueva"
    INSTITUCION_INACTIVA = "institucion_inactiva"
    ALERTA_SISTEMA = "alerta_sistema"


class PrioridadNotificacion(str, enum.Enum):
    """Prioridad de notificaciones"""

    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    URGENTE = "urgente"


class NotificacionInteroperabilidad(Base):
    """
    Notificaciones del sistema de interoperabilidad
    """

    __tablename__ = "notificaciones_interoperabilidad"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Tipo y prioridad
    tipo = Column(SQLEnum(TipoNotificacion), nullable=False, index=True)
    prioridad = Column(
        SQLEnum(PrioridadNotificacion),
        nullable=False,
        default=PrioridadNotificacion.MEDIA,
        index=True,
    )

    # Contenido
    titulo = Column(String(200), nullable=False)
    mensaje = Column(Text, nullable=False)
    datos_adicionales = Column(Text, nullable=True)  # JSON con información extra

    # Destinatario
    usuario_id = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True
    )

    # Referencias
    solicitud_id = Column(
        UUID(as_uuid=True),
        ForeignKey("solicitudes_intercambio.id"),
        nullable=True,
        index=True,
    )
    institucion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("instituciones_externas.id"),
        nullable=True,
        index=True,
    )

    # Estado
    leida = Column(Boolean, default=False, nullable=False, index=True)
    fecha_lectura = Column(DateTime, nullable=True)

    # Acciones
    accion_url = Column(String(500), nullable=True)  # URL para acción relacionada
    accion_texto = Column(String(100), nullable=True)  # Texto del botón de acción

    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    usuario = relationship("Usuario", backref="notificaciones_interoperabilidad")
    solicitud = relationship("SolicitudIntercambio", backref="notificaciones")
    institucion = relationship("InstitucionExterna", backref="notificaciones")

    def __repr__(self):
        return f"<NotificacionInteroperabilidad {self.tipo}: {self.titulo}>"

    def marcar_como_leida(self):
        """Marca la notificación como leída"""
        self.leida = True
        self.fecha_lectura = datetime.utcnow()

    def to_dict(self):
        """Convierte la notificación a diccionario"""
        return {
            "id": str(self.id),
            "tipo": self.tipo.value,
            "prioridad": self.prioridad.value,
            "titulo": self.titulo,
            "mensaje": self.mensaje,
            "datos_adicionales": self.datos_adicionales,
            "usuario_id": str(self.usuario_id),
            "solicitud_id": str(self.solicitud_id) if self.solicitud_id else None,
            "institucion_id": str(self.institucion_id) if self.institucion_id else None,
            "leida": self.leida,
            "fecha_lectura": (
                self.fecha_lectura.isoformat() if self.fecha_lectura else None
            ),
            "accion_url": self.accion_url,
            "accion_texto": self.accion_texto,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
