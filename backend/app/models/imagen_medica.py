from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class ImagenMedica(Base):
    __tablename__ = "imagenes_medicas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id", ondelete="CASCADE"), nullable=False, index=True)
    consulta_id = Column(UUID(as_uuid=True), ForeignKey("consultas.id"), nullable=True, index=True)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    
    # Información del archivo
    nombre_archivo = Column(String(255), nullable=False)
    ruta_archivo = Column(String(500), nullable=False)  # Path relativo en el servidor
    url_archivo = Column(String(500), nullable=True)  # URL pública si aplica
    tipo_archivo = Column(String(50), nullable=False)  # image/jpeg, image/png, application/dicom
    tamanio_bytes = Column(Integer, nullable=False)
    
    # Metadatos de la imagen
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    tipo_imagen = Column(String(50), nullable=False)  # rayos_x, tomografia, resonancia, fotografia, ecografia, etc.
    modalidad = Column(String(50), nullable=True)  # CR, CT, MR, US, XA, etc. (DICOM modality)
    region_anatomica = Column(String(100), nullable=True)  # torax, abdomen, craneo, etc.
    lateralidad = Column(String(20), nullable=True)  # izquierda, derecha, bilateral
    
    # Dimensiones
    ancho = Column(Integer, nullable=True)
    alto = Column(Integer, nullable=True)
    
    # Metadatos DICOM (si aplica)
    dicom_metadata = Column(JSONB, nullable=True)
    
    # Análisis con IA
    analisis_ia_completado = Column(Boolean, default=False)
    resultados_ia = Column(JSONB, nullable=True)  # Resultados de CheXNet, MONAI, etc.
    confianza_ia = Column(Float, nullable=True)  # Confianza del análisis
    hallazgos = Column(ARRAY(String), nullable=True)  # Lista de hallazgos detectados
    
    # Anotaciones
    anotaciones = Column(JSONB, nullable=True)  # Array de anotaciones con coordenadas
    
    # Estado y visibilidad
    es_dicom = Column(Boolean, default=False)
    requiere_revision = Column(Boolean, default=False)
    aprobada = Column(Boolean, default=False)
    
    # Timestamps
    fecha_adquisicion = Column(DateTime(timezone=True), nullable=True)  # Fecha real de la imagen
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
