# app/models/telemedicina.py

import uuid
import secrets
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Enum,
    Integer,
    JSON,
    Date,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class EstadoConsulta(str, enum.Enum):
    PROGRAMADA = "programada"
    EN_ESPERA = "en_espera"
    EN_CURSO = "en_curso"
    FINALIZADA = "finalizada"
    CANCELADA = "cancelada"
    NO_REALIZADA = "no_realizada"


class TipoConsulta(str, enum.Enum):
    VIDEOLLAMADA = "videollamada"
    AUDIO = "audio"
    CHAT = "chat"


class TipoMensaje(str, enum.Enum):
    TEXTO = "texto"
    IMAGEN = "imagen"
    ARCHIVO = "archivo"
    SISTEMA = "sistema"


class EmisorTipo(str, enum.Enum):
    MEDICO = "medico"
    PACIENTE = "paciente"
    SISTEMA = "sistema"


class TipoSeguimiento(str, enum.Enum):
    CITA_CONTROL = "cita_control"
    RECORDATORIO_MEDICAMENTO = "recordatorio_medicamento"
    VERIFICACION_SINTOMAS = "verificacion_sintomas"
    ENVIO_RESULTADOS = "envio_resultados"
    OTRO = "otro"


class ConsultaRemota(Base):
    """Modelo para consultas de telemedicina"""

    __tablename__ = "consultas_remotas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Relaciones
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    medico_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)

    # Información de la sala
    sala_id = Column(String(50), unique=True, nullable=False)
    token_sala = Column("token_acceso", String(255), nullable=False)

    # Tipo y estado
    # Usar STRING en lugar de Enum nativo
    tipo = Column(String(50), nullable=False, default=TipoConsulta.VIDEOLLAMADA.value)
    estado = Column(String(50), nullable=False, default=EstadoConsulta.PROGRAMADA.value)

    # Fechas
    fecha_programada = Column(DateTime, nullable=False)
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)
    duracion_minutos = Column(Integer, nullable=True)

    # Información médica
    motivo_consulta = Column(Text, nullable=True)
    notas_medico = Column(Text, nullable=True)
    diagnostico_preliminar = Column(Text, nullable=True)
    plan_tratamiento = Column(Text, nullable=True)

    # Control
    requiere_seguimiento = Column(Boolean, default=False)
    # recordatorio_enviado = Column(Boolean, default=False)

    # URLs de acceso
    url_sala_medico = Column(String(500), nullable=True)
    url_sala_paciente = Column(String(500), nullable=True)

    # Metadatos
    # metadata_conexion = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    paciente = relationship("Paciente", back_populates="consultas_remotas")
    medico = relationship("Usuario", back_populates="consultas_remotas")
    mensajes = relationship(
        "MensajeChat", back_populates="consulta", cascade="all, delete-orphan"
    )
    prescripciones = relationship(
        "PrescripcionElectronica", back_populates="consulta_remota"
    )
    seguimientos = relationship(
        "SeguimientoPostConsulta", back_populates="consulta_remota"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.sala_id:
            self.sala_id = self._generar_sala_id()
        if not self.token_sala:
            self.token_sala = self._generar_token()
        self._generar_urls()

    def _generar_sala_id(self) -> str:
        """Genera un ID único para la sala"""
        return secrets.token_urlsafe(15)

    def _generar_token(self) -> str:
        """Genera un token seguro para acceso"""
        return secrets.token_urlsafe(32)

    def _generar_urls(self):
        """Genera las URLs de acceso a la sala"""
        base_url = "https://telemedicina.ddx.local/sala"
        self.url_sala_medico = (
            f"{base_url}/{self.sala_id}?token={self.token_sala}&role=medico"
        )
        self.url_sala_paciente = (
            f"{base_url}/{self.sala_id}?token={self.token_sala}&role=paciente"
        )


class MensajeChat(Base):
    """Mensajes del chat de telemedicina"""

    __tablename__ = "mensajes_chat"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    consulta_remota_id = Column(
        UUID(as_uuid=True), ForeignKey("consultas_remotas.id"), nullable=False
    )

    # Emisor
    emisor_id = Column(UUID(as_uuid=True), nullable=False)
    # Guardar como texto en BD (no ENUM nativo)
    emisor_tipo = Column(
        String(20), nullable=False
    )  # valores: "MEDICO", "PACIENTE", etc.

    # Contenido
    contenido = Column(Text, nullable=False)
    # También como texto
    tipo_mensaje = Column(String(20), nullable=False, default=TipoMensaje.TEXTO.value)

    # Archivos adjuntos
    archivo_url = Column(String(500), nullable=True)
    archivo_nombre = Column(String(255), nullable=True)
    archivo_tipo = Column(String(100), nullable=True)

    # Estado
    leido = Column(Boolean, default=False)
    # ESTA COLUMNA NO EXISTE EN LA TABLA → QUITARLA
    # fecha_leido = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    consulta = relationship("ConsultaRemota", back_populates="mensajes")


class PrescripcionElectronica(Base):
    """Recetas electrónicas generadas en teleconsultas"""

    __tablename__ = "prescripciones_electronicas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Relaciones
    consulta_remota_id = Column(
        UUID(as_uuid=True), ForeignKey("consultas_remotas.id"), nullable=True
    )
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    medico_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)

    # Número único de receta
    numero_receta = Column(String(50), unique=True, nullable=False)

    # Información médica
    diagnostico = Column(Text, nullable=False)
    codigo_cie10 = Column(String(20), nullable=True)

    # Medicamentos (JSON array)
    medicamentos = Column(JSON, nullable=False)

    # Indicaciones
    indicaciones_generales = Column(Text, nullable=True)

    # Validez
    fecha_emision = Column(DateTime, default=datetime.utcnow)
    fecha_vigencia = Column(DateTime, nullable=False)

    # Estado
    # activa = Column(Boolean, default=True)

    # Firma digital (simplificada)
    firma_medico = Column(Text, nullable=True)
    codigo_verificacion = Column(String(20), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    consulta_remota = relationship("ConsultaRemota", back_populates="prescripciones")
    paciente = relationship("Paciente", back_populates="prescripciones_electronicas")
    medico = relationship("Usuario", back_populates="prescripciones_emitidas")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.numero_receta:
            self.numero_receta = self._generar_numero_receta()
        if not self.codigo_verificacion:
            self.codigo_verificacion = self._generar_codigo_verificacion()

    def _generar_numero_receta(self) -> str:
        """Genera número único de receta"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        aleatorio = secrets.token_hex(3).upper()
        return f"RX-{timestamp}-{aleatorio}"

    def _generar_codigo_verificacion(self) -> str:
        """Genera código de verificación"""
        return secrets.token_hex(4).upper()


from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Enum,
    Integer,
    JSON,
    Date,
)


class SeguimientoPostConsulta(Base):
    __tablename__ = "seguimientos_post_consulta"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    consulta_remota_id = Column(
        UUID(as_uuid=True), ForeignKey("consultas_remotas.id"), nullable=True
    )
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    medico_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)

    # Tipo y contenido
    # Guardar como texto en BD, no como ENUM nativo
    tipo = Column(
        String(50), nullable=False
    )  # valores como "RECORDATORIO_MEDICAMENTO", etc.
    titulo = Column(String(200), nullable=False)
    mensaje = Column(Text, nullable=False)

    fecha_programada = Column(DateTime, nullable=False)
    metodo_notificacion = Column(String(50), default="email")

    enviado = Column(Boolean, default=False)
    fecha_enviado = Column(DateTime, nullable=True)
    respuesta_paciente = Column(Text, nullable=True)
    fecha_respuesta = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    consulta_remota = relationship("ConsultaRemota", back_populates="seguimientos")
    paciente = relationship("Paciente", back_populates="seguimientos")
    medico = relationship("Usuario")
