from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base


class TipoNotaEnum(str, enum.Enum):
    EVOLUCION = "evolucion"
    INGRESO = "ingreso"
    ALTA = "alta"
    INTERCONSULTA = "interconsulta"
    PROCEDIMIENTO = "procedimiento"
    DEFUNCION = "defuncion"


class NotaMedica(Base):
    __tablename__ = "notas_medicas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id", ondelete="CASCADE"), nullable=False, index=True)
    consulta_id = Column(UUID(as_uuid=True), ForeignKey("consultas.id"))
    hospitalizacion_id = Column(UUID(as_uuid=True), ForeignKey("hospitalizaciones.id"))
    autor_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    tipo_nota = Column(String(50))
    titulo = Column(String(255), nullable=False)
    contenido = Column(String, nullable=False)
    fecha_nota = Column(DateTime(timezone=True), server_default=func.now())
    firmada = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
