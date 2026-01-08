from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Boolean, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base


class TipoPruebaEnum(str, enum.Enum):
    LABORATORIO = "laboratorio"
    IMAGEN = "imagen"
    BIOPSIA = "biopsia"
    ELECTROCARDIOGRAMA = "electrocardiograma"
    OTRO = "otro"


class UrgenciaEnum(str, enum.Enum):
    NORMAL = "normal"
    URGENTE = "urgente"
    EMERGENCIA = "emergencia"


class EstadoPruebaEnum(str, enum.Enum):
    SOLICITADA = "solicitada"
    EN_PROCESO = "en_proceso"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"


class PruebaMedica(Base):
    __tablename__ = "pruebas_medicas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    consulta_id = Column(UUID(as_uuid=True), ForeignKey("consultas.id", ondelete="CASCADE"), nullable=False, index=True)
    diagnostico_id = Column(UUID(as_uuid=True), ForeignKey("diagnosticos.id"))
    tipo_prueba = Column(String(50))
    nombre_prueba = Column(String(255), nullable=False)
    descripcion = Column(String)
    urgencia = Column(String(20))
    estado = Column(String(50), default='solicitada')
    fecha_solicitud = Column(DateTime(timezone=True), server_default=func.now())
    fecha_programada = Column(DateTime(timezone=True))
    fecha_realizada = Column(DateTime(timezone=True))
    solicitado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    laboratorio_externo = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ResultadoPrueba(Base):
    __tablename__ = "resultados_pruebas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prueba_id = Column(UUID(as_uuid=True), ForeignKey("pruebas_medicas.id", ondelete="CASCADE"), nullable=False, index=True)
    resultado_texto = Column(String)
    resultado_numerico = Column(Numeric)
    unidad_medida = Column(String(50))
    valores_referencia = Column(String(255))
    interpretacion = Column(String)
    anormal = Column(Boolean, default=False)
    archivo_url = Column(String)
    archivo_tipo = Column(String(50))
    notas = Column(String)
    registrado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    fecha_resultado = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
