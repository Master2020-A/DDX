from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base


class TipoArchivoEnum(str, enum.Enum):
    IMAGEN = "imagen"
    DOCUMENTO = "documento"
    LABORATORIO = "laboratorio"
    RADIOGRAFIA = "radiografia"
    ECOGRAFIA = "ecografia"
    TOMOGRAFIA = "tomografia"
    RESONANCIA = "resonancia"


class ArchivoMedico(Base):
    __tablename__ = "archivos_medicos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id", ondelete="CASCADE"), nullable=False, index=True)
    consulta_id = Column(UUID(as_uuid=True), ForeignKey("consultas.id"))
    prueba_id = Column(UUID(as_uuid=True), ForeignKey("pruebas_medicas.id"))
    tipo_archivo = Column(String(50))
    nombre_archivo = Column(String(255), nullable=False)
    url_archivo = Column(String, nullable=False)
    tamano_bytes = Column(BigInteger)
    mime_type = Column(String(100))
    descripcion = Column(String)
    subido_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
