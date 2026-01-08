from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base


class TipoDiagnosticoEnum(str, enum.Enum):
    PRE_DIAGNOSTICO = "pre_diagnostico"
    DIAGNOSTICO_PRESUNTIVO = "diagnostico_presuntivo"
    DIAGNOSTICO_CONFIRMADO = "diagnostico_confirmado"
    DIAGNOSTICO_DIFERENCIAL = "diagnostico_diferencial"


class NivelConfianzaEnum(str, enum.Enum):
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"
    CONFIRMADO = "confirmado"


class EstadoDiagnosticoEnum(str, enum.Enum):
    ACTIVO = "activo"
    DESCARTADO = "descartado"
    CONFIRMADO = "confirmado"


class Diagnostico(Base):
    __tablename__ = "diagnosticos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    consulta_id = Column(UUID(as_uuid=True), ForeignKey("consultas.id", ondelete="CASCADE"), nullable=False, index=True)
    medico_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    tipo = Column(String(50))
    codigo_cie10 = Column(String(10))
    descripcion = Column(String, nullable=False)
    confianza_nivel = Column(String(20))
    justificacion = Column(String)
    evidencias = Column(ARRAY(String))
    estado = Column(String(50), default='activo')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
