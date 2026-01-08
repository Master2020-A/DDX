from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Integer, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base


class TipoTratamientoEnum(str, enum.Enum):
    FARMACOLOGICO = "farmacologico"
    FISICO = "fisico"
    PALIATIVO = "paliativo"
    QUIRURGICO = "quirurgico"
    PSICOLOGICO = "psicologico"
    OTRO = "otro"


class EstadoTratamientoEnum(str, enum.Enum):
    ACTIVO = "activo"
    COMPLETADO = "completado"
    SUSPENDIDO = "suspendido"
    MODIFICADO = "modificado"


class Tratamiento(Base):
    __tablename__ = "tratamientos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    consulta_id = Column(UUID(as_uuid=True), ForeignKey("consultas.id", ondelete="CASCADE"), nullable=False, index=True)
    diagnostico_id = Column(UUID(as_uuid=True), ForeignKey("diagnosticos.id"))
    tipo_tratamiento = Column(String(50))
    descripcion = Column(String, nullable=False)
    objetivo = Column(String)
    duracion_dias = Column(Integer)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    estado = Column(String(50), default='activo')
    prescrito_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    notas = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Prescripcion(Base):
    __tablename__ = "prescripciones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tratamiento_id = Column(UUID(as_uuid=True), ForeignKey("tratamientos.id", ondelete="CASCADE"), nullable=False)
    medicamento = Column(String(255), nullable=False)
    principio_activo = Column(String(255))
    dosis = Column(String(100), nullable=False)
    frecuencia = Column(String(100), nullable=False)
    via_administracion = Column(String(50))
    duracion_dias = Column(Integer)
    cantidad_total = Column(String(50))
    instrucciones_especiales = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
