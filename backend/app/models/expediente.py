from sqlalchemy import Column, String, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class ExpedienteClinico(Base):
    __tablename__ = "expedientes_clinicos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id", ondelete="CASCADE"), nullable=False)
    consulta_id = Column(UUID(as_uuid=True), ForeignKey("consultas.id"))
    antecedentes_personales = Column(String)
    antecedentes_familiares = Column(String)
    padecimientos_cronicos = Column(ARRAY(String))
    cirugias_previas = Column(ARRAY(String))
    medicamentos_actuales = Column(ARRAY(String))
    habitos = Column(String)
    signos_vitales = Column(JSONB)  # {"temperatura": 36.5, "presion_arterial": "120/80", ...}
    exploracion_fisica = Column(String)
    notas = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
