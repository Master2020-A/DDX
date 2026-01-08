from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base


class TipoSeguimientoEnum(str, enum.Enum):
    MEDICO = "medico"
    ENFERMERIA = "enfermeria"
    FISIOTERAPIA = "fisioterapia"
    NUTRICION = "nutricion"
    PSICOLOGIA = "psicologia"
    TRABAJO_SOCIAL = "trabajo_social"


class Seguimiento(Base):
    __tablename__ = "seguimientos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id", ondelete="CASCADE"), nullable=False, index=True)
    consulta_id = Column(UUID(as_uuid=True), ForeignKey("consultas.id"))
    responsable_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    tipo_seguimiento = Column(String(50))
    fecha_seguimiento = Column(DateTime(timezone=True), nullable=False)
    evolucion = Column(String, nullable=False)
    plan_accion = Column(String)
    proxima_cita = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
