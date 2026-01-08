from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base


class UrgenciaEnum(str, enum.Enum):
    NORMAL = "normal"
    URGENTE = "urgente"
    EMERGENCIA = "emergencia"


class EstadoInterconsultaEnum(str, enum.Enum):
    SOLICITADA = "solicitada"
    ACEPTADA = "aceptada"
    EN_PROCESO = "en_proceso"
    COMPLETADA = "completada"
    RECHAZADA = "rechazada"
    CANCELADA = "cancelada"


class TipoNotificacionEnum(str, enum.Enum):
    NUEVA_SOLICITUD = "nueva_solicitud"
    ACEPTADA = "aceptada"
    RECHAZADA = "rechazada"
    RESPUESTA_DISPONIBLE = "respuesta_disponible"
    MENSAJE_NUEVO = "mensaje_nuevo"
    RECORDATORIO = "recordatorio"


class NotificacionInterconsulta(Base):
    """Notificaciones para especialistas sobre interconsultas"""
    __tablename__ = "notificaciones_interconsulta"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interconsulta_id = Column(UUID(as_uuid=True), ForeignKey("interconsultas.id", ondelete="CASCADE"), nullable=False, index=True)
    medico_destinatario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    
    tipo = Column(String(50), nullable=False)
    titulo = Column(String(200), nullable=False)
    mensaje = Column(Text, nullable=False)
    leida = Column(Boolean, default=False, nullable=False)
    fecha_lectura = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relaciones
    interconsulta = relationship("Interconsulta", back_populates="notificaciones")


class MensajeInterconsulta(Base):
    """Chat entre médicos sobre una interconsulta"""
    __tablename__ = "mensajes_interconsulta"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interconsulta_id = Column(UUID(as_uuid=True), ForeignKey("interconsultas.id", ondelete="CASCADE"), nullable=False, index=True)
    medico_emisor_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    
    mensaje = Column(Text, nullable=False)
    archivos_adjuntos = Column(ARRAY(String), nullable=True)  # URLs o IDs de archivos
    leido = Column(Boolean, default=False, nullable=False)
    fecha_lectura = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relaciones
    interconsulta = relationship("Interconsulta", back_populates="mensajes")


class SeguimientoInterconsulta(Base):
    """Seguimiento interdisciplinario de interconsultas"""
    __tablename__ = "seguimientos_interconsulta"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interconsulta_id = Column(UUID(as_uuid=True), ForeignKey("interconsultas.id", ondelete="CASCADE"), nullable=False, index=True)
    medico_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    
    tipo_seguimiento = Column(String(50), nullable=False)  # evolucion, control, revision
    observaciones = Column(Text, nullable=False)
    estado_paciente = Column(String(100), nullable=True)
    cambios_tratamiento = Column(Text, nullable=True)
    proxima_revision = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class Interconsulta(Base):
    __tablename__ = "interconsultas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id", ondelete="CASCADE"), nullable=False, index=True)
    consulta_id = Column(UUID(as_uuid=True), ForeignKey("consultas.id", ondelete="SET NULL"), nullable=True, index=True)
    hospitalizacion_id = Column(UUID(as_uuid=True), ForeignKey("hospitalizaciones.id", ondelete="SET NULL"), nullable=True)
    
    # Médicos involucrados
    medico_solicitante_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    especialista_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    
    # Información de la solicitud
    especialidad_requerida = Column(String(100), nullable=False)
    motivo_solicitud = Column(Text, nullable=False)
    antecedentes_relevantes = Column(Text, nullable=True)
    estudios_adjuntos = Column(ARRAY(String), nullable=True)  # IDs de estudios
    urgencia = Column(String(20), nullable=False, default='normal')
    estado = Column(String(50), nullable=False, default='solicitada')
    
    # Fechas
    fecha_solicitud = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fecha_aceptacion = Column(DateTime(timezone=True), nullable=True)
    fecha_programada = Column(DateTime(timezone=True), nullable=True)
    fecha_realizada = Column(DateTime(timezone=True), nullable=True)
    fecha_completada = Column(DateTime(timezone=True), nullable=True)
    
    # Respuesta del especialista
    diagnostico_especialista = Column(Text, nullable=True)
    hallazgos = Column(Text, nullable=True)
    recomendaciones = Column(Text, nullable=True)
    plan_tratamiento = Column(Text, nullable=True)
    requiere_seguimiento = Column(Boolean, default=False)
    fecha_seguimiento = Column(DateTime(timezone=True), nullable=True)
    
    # Motivo de rechazo (si aplica)
    motivo_rechazo = Column(Text, nullable=True)
    
    # Metadata
    prioridad_clinica = Column(Integer, default=1)  # 1-5
    notas_internas = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relaciones
    notificaciones = relationship("NotificacionInterconsulta", back_populates="interconsulta", cascade="all, delete-orphan")
    mensajes = relationship("MensajeInterconsulta", back_populates="interconsulta", cascade="all, delete-orphan")
