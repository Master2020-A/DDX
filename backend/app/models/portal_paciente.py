# app/models/portal_paciente.py

import uuid
from datetime import datetime, date, time
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Enum,
    Integer,
    Numeric,
    Date,
    Time,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.models.configuracion_portal import ConfiguracionPortal  # re-export
from app.core.database import Base


# ============================================================================
# ENUMS
# ============================================================================


class EstadoCita(str, enum.Enum):
    SOLICITADA = "solicitada"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    COMPLETADA = "completada"
    NO_ASISTIO = "no_asistio"


class TipoCita(str, enum.Enum):
    PRIMERA_VEZ = "primera_vez"
    SEGUIMIENTO = "seguimiento"
    URGENCIA = "urgencia"
    TELEMEDICINA = "telemedicina"


class EstadoSolicitudEstudio(str, enum.Enum):
    PENDIENTE = "pendiente"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"
    EN_PROCESO = "en_proceso"
    COMPLETADA = "completada"


class TipoEstudio(str, enum.Enum):
    LABORATORIO = "laboratorio"
    IMAGEN = "imagen"
    ESPECIALIZADO = "especializado"


class EstadoPago(str, enum.Enum):
    PENDIENTE = "pendiente"
    PROCESANDO = "procesando"
    COMPLETADO = "completado"
    FALLIDO = "fallido"
    REEMBOLSADO = "reembolsado"


class MetodoPago(str, enum.Enum):
    TARJETA_CREDITO = "tarjeta_credito"
    TARJETA_DEBITO = "tarjeta_debito"
    TRANSFERENCIA = "transferencia"
    EFECTIVO = "efectivo"
    PAYPAL = "paypal"
    STRIPE = "stripe"


class EstadoMensaje(str, enum.Enum):
    ENVIADO = "enviado"
    ENTREGADO = "entregado"
    LEIDO = "leido"


class FrecuenciaRecordatorio(str, enum.Enum):
    UNA_VEZ = "una_vez"
    DIARIO = "diario"
    CADA_12_HORAS = "cada_12_horas"
    CADA_8_HORAS = "cada_8_horas"
    CADA_6_HORAS = "cada_6_horas"
    SEMANAL = "semanal"
    MENSUAL = "mensual"


# ============================================================================
# MODELOS
# ============================================================================


class CitaPaciente(Base):
    """Citas agendadas por pacientes"""

    __tablename__ = "citas_pacientes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Relaciones
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    medico_id = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )  # Puede ser null si es solicitud inicial

    # Información de la cita
    tipo_cita = Column(String(50), nullable=False, default=TipoCita.PRIMERA_VEZ.value)
    especialidad_solicitada = Column(String(100), nullable=True)
    motivo_consulta = Column(Text, nullable=False)

    # Fecha y hora
    fecha_solicitada = Column(Date, nullable=False)
    hora_solicitada = Column(Time, nullable=True)
    fecha_confirmada = Column(DateTime, nullable=True)
    duracion_minutos = Column(Integer, default=30)

    # Estado
    estado = Column(String(50), nullable=False, default=EstadoCita.SOLICITADA.value)
    notas_paciente = Column(Text, nullable=True)
    notas_medico = Column(Text, nullable=True)

    # Recordatorios
    recordatorio_enviado = Column(Boolean, default=False)
    fecha_recordatorio = Column(DateTime, nullable=True)

    # Cancelación
    fecha_cancelacion = Column(DateTime, nullable=True)
    motivo_cancelacion = Column(Text, nullable=True)
    cancelado_por = Column(String(50), nullable=True)  # 'paciente', 'medico', 'sistema'

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    paciente = relationship("Paciente", back_populates="citas_portal")
    medico = relationship("Usuario", foreign_keys=[medico_id])


class SolicitudEstudio(Base):
    """Solicitudes de estudios por pacientes"""

    __tablename__ = "solicitudes_estudios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Relaciones
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    medico_solicitante_id = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )
    medico_autorizador_id = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )

    # Información del estudio
    tipo_estudio = Column(
        String(50), nullable=False, default=TipoEstudio.LABORATORIO.value
    )
    nombre_estudio = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    indicaciones_especiales = Column(Text, nullable=True)

    # Estado
    estado = Column(
        String(50), nullable=False, default=EstadoSolicitudEstudio.PENDIENTE.value
    )
    prioridad = Column(String(50), default="normal")  # normal, urgente, emergencia

    # Fechas
    fecha_solicitud = Column(DateTime, default=datetime.utcnow)
    fecha_autorizacion = Column(DateTime, nullable=True)
    fecha_programada = Column(DateTime, nullable=True)
    fecha_realizacion = Column(DateTime, nullable=True)

    # Resultados
    resultado_disponible = Column(Boolean, default=False)
    resultado_id = Column(
        UUID(as_uuid=True), nullable=True
    )  # Referencia a tabla de resultados
    url_resultado = Column(String(500), nullable=True)

    # Notas
    notas_paciente = Column(Text, nullable=True)
    notas_autorizacion = Column(Text, nullable=True)
    motivo_rechazo = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    paciente = relationship("Paciente", back_populates="solicitudes_estudios")
    medico_solicitante = relationship("Usuario", foreign_keys=[medico_solicitante_id])
    medico_autorizador = relationship("Usuario", foreign_keys=[medico_autorizador_id])


class PagoServicio(Base):
    """Pagos de servicios médicos"""

    __tablename__ = "pagos_servicios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Relaciones
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    cita_id = Column(
        UUID(as_uuid=True), ForeignKey("citas_pacientes.id"), nullable=True
    )
    solicitud_estudio_id = Column(
        UUID(as_uuid=True), ForeignKey("solicitudes_estudios.id"), nullable=True
    )

    # Información del pago
    concepto = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    monto = Column(Numeric(10, 2), nullable=False)
    moneda = Column(String(3), default="MXN")

    # Método de pago
    metodo_pago = Column(
        String(50), nullable=False, default=MetodoPago.TARJETA_CREDITO.value
    )
    referencia_pago = Column(String(255), nullable=True)  # ID de transacción externa

    # Estado
    estado = Column(String(50), nullable=False, default=EstadoPago.PENDIENTE.value)

    # Fechas
    fecha_pago = Column(DateTime, default=datetime.utcnow)
    fecha_procesado = Column(DateTime, nullable=True)
    fecha_completado = Column(DateTime, nullable=True)

    # Información de la transacción
    datos_transaccion = Column(JSON, nullable=True)  # Datos del procesador de pagos
    comprobante_url = Column(String(500), nullable=True)
    factura_id = Column(
        UUID(as_uuid=True), nullable=True
    )  # Referencia a factura electrónica

    # Reembolso
    reembolsado = Column(Boolean, default=False)
    fecha_reembolso = Column(DateTime, nullable=True)
    motivo_reembolso = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    paciente = relationship("Paciente", back_populates="pagos")
    cita = relationship("CitaPaciente")
    solicitud_estudio = relationship("SolicitudEstudio")


class MensajePacienteMedico(Base):
    """Mensajería entre pacientes y médicos"""

    __tablename__ = "mensajes_paciente_medico"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Relaciones
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    medico_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)

    # Información del mensaje
    remitente_tipo = Column(String(50), nullable=False)  # 'paciente' o 'medico'
    asunto = Column(String(255), nullable=True)
    mensaje = Column(Text, nullable=False)

    # Archivos adjuntos
    archivos_adjuntos = Column(JSON, nullable=True)  # Lista de URLs de archivos

    # Estado
    estado = Column(String(50), nullable=False, default=EstadoMensaje.ENVIADO.value)
    leido = Column(Boolean, default=False)
    fecha_lectura = Column(DateTime, nullable=True)

    # Respuesta
    mensaje_padre_id = Column(
        UUID(as_uuid=True), ForeignKey("mensajes_paciente_medico.id"), nullable=True
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    paciente = relationship("Paciente", back_populates="mensajes")
    medico = relationship("Usuario")
    respuestas = relationship(
        "MensajePacienteMedico",
        backref="mensaje_padre",
        remote_side=[id],
        cascade="all, delete",
    )


class RecordatorioMedicamento(Base):
    """Recordatorios de medicamentos para pacientes"""

    __tablename__ = "recordatorios_medicamentos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Relaciones
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    receta_id = Column(
        UUID(as_uuid=True), nullable=True
    )  # Referencia a receta electrónica

    # Información del medicamento
    nombre_medicamento = Column(String(255), nullable=False)
    dosis = Column(String(100), nullable=False)
    via_administracion = Column(String(50), nullable=True)
    indicaciones = Column(Text, nullable=True)

    # Frecuencia
    frecuencia = Column(
        String(50), nullable=False, default=FrecuenciaRecordatorio.DIARIO.value
    )
    horarios = Column(JSON, nullable=False)  # Lista de horarios ["08:00", "20:00"]

    # Duración del tratamiento
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=True)
    duracion_dias = Column(Integer, nullable=True)

    # Estado
    activo = Column(Boolean, default=True)
    pausado = Column(Boolean, default=False)

    # Notificaciones
    notificar_email = Column(Boolean, default=True)
    notificar_sms = Column(Boolean, default=False)
    notificar_push = Column(Boolean, default=True)

    # Seguimiento
    ultima_toma_registrada = Column(DateTime, nullable=True)
    tomas_registradas = Column(Integer, default=0)
    tomas_omitidas = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    paciente = relationship("Paciente", back_populates="recordatorios_medicamentos")
    registros_toma = relationship(
        "RegistroTomaMedicamento",
        back_populates="recordatorio",
        cascade="all, delete-orphan",
    )


class RegistroTomaMedicamento(Base):
    """Registro de tomas de medicamentos"""

    __tablename__ = "registros_toma_medicamento"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Relaciones
    recordatorio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("recordatorios_medicamentos.id"),
        nullable=False,
    )

    # Información de la toma
    fecha_programada = Column(DateTime, nullable=False)
    fecha_real = Column(DateTime, nullable=True)
    tomado = Column(Boolean, default=False)
    omitido = Column(Boolean, default=False)
    motivo_omision = Column(Text, nullable=True)

    # Notas
    notas = Column(Text, nullable=True)
    efectos_secundarios = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    recordatorio = relationship(
        "RecordatorioMedicamento", back_populates="registros_toma"
    )


class AccesoExpediente(Base):
    """Control de acceso al expediente del paciente"""

    __tablename__ = "accesos_expediente"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Relaciones
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    usuario_id = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )  # Puede ser null si es el paciente

    # Información del acceso
    tipo_acceso = Column(String(50), nullable=False)  # 'lectura', 'descarga', 'edicion'
    seccion_accedida = Column(
        String(100), nullable=True
    )  # 'consultas', 'laboratorios', 'imagenes', etc.
    recurso_id = Column(UUID(as_uuid=True), nullable=True)  # ID del recurso específico

    # Detalles
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    duracion_segundos = Column(Integer, nullable=True)

    # Timestamp
    fecha_acceso = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    paciente = relationship("Paciente")
    usuario = relationship("Usuario")


# ConfiguracionPortal se importa desde app.models.configuracion_portal
# No redefinir aquí para evitar conflictos
