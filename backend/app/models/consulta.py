from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.core.database import Base


class TipoConsultaEnum(str, enum.Enum):
    PRIMERA_VEZ = "primera_vez"
    SEGUIMIENTO = "seguimiento"
    URGENCIA = "urgencia"
    INTERCONSULTA = "interconsulta"


class EstadoConsultaEnum(str, enum.Enum):
    EN_PROCESO = "en_proceso"
    COMPLETADA = "completada"
    HOSPITALIZADO = "hospitalizado"
    ALTA = "alta"


class Consulta(Base):
    __tablename__ = "consultas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(
        UUID(as_uuid=True),
        ForeignKey("pacientes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    medico_id = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True
    )
    fecha_hora = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
    tipo_consulta = Column(String(50))
    motivo_consulta = Column(String, nullable=False)
    sintomas = Column(ARRAY(String), nullable=False)
    estado = Column(String(50), default="en_proceso")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relaciones
    pruebas_laboratorio = relationship(
        "PruebaLaboratorio", back_populates="consulta", lazy="select"
    )
    consentimientos_informados = relationship(
        "ConsentimientoInformado",
        back_populates="consulta",
        cascade="all, delete-orphan",
    )
