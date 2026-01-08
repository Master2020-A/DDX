from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# ============================================================================
# ANOTACIÓN EN IMAGEN
# ============================================================================

class AnotacionImagen(BaseModel):
    tipo: str = Field(..., description="Tipo de anotación: rectangulo, circulo, flecha, texto")
    coordenadas: Dict[str, float] = Field(..., description="Coordenadas de la anotación")
    color: Optional[str] = Field("#FF0000", description="Color en formato hex")
    texto: Optional[str] = Field(None, description="Texto de la anotación")
    grosor: Optional[int] = Field(2, description="Grosor de la línea")
    autor: Optional[str] = Field(None, description="Autor de la anotación")
    fecha: Optional[datetime] = Field(None, description="Fecha de la anotación")


# ============================================================================
# RESULTADO DE ANÁLISIS IA
# ============================================================================

class ResultadoAnalisisIA(BaseModel):
    modelo: str = Field(..., description="Nombre del modelo: CheXNet, MONAI, etc.")
    version: Optional[str] = Field(None, description="Versión del modelo")
    predicciones: Dict[str, float] = Field(..., description="Predicciones con sus probabilidades")
    hallazgos: List[str] = Field(default_factory=list, description="Hallazgos detectados")
    confianza_global: float = Field(..., description="Confianza global del análisis")
    tiempo_procesamiento: Optional[float] = Field(None, description="Tiempo en segundos")
    fecha_analisis: datetime = Field(default_factory=datetime.now)


# ============================================================================
# IMAGEN MÉDICA
# ============================================================================

class ImagenMedicaBase(BaseModel):
    paciente_id: UUID
    consulta_id: Optional[UUID] = None
    titulo: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = None
    tipo_imagen: str = Field(..., description="rayos_x, tomografia, resonancia, fotografia, etc.")
    modalidad: Optional[str] = Field(None, description="CR, CT, MR, US, XA, etc.")
    region_anatomica: Optional[str] = None
    lateralidad: Optional[str] = None
    fecha_adquisicion: Optional[datetime] = None


class ImagenMedicaCreate(ImagenMedicaBase):
    nombre_archivo: str
    ruta_archivo: str
    tipo_archivo: str
    tamanio_bytes: int
    ancho: Optional[int] = None
    alto: Optional[int] = None
    es_dicom: bool = False
    dicom_metadata: Optional[Dict[str, Any]] = None


class ImagenMedicaUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)
    descripcion: Optional[str] = None
    tipo_imagen: Optional[str] = None
    region_anatomica: Optional[str] = None
    lateralidad: Optional[str] = None
    anotaciones: Optional[List[Dict[str, Any]]] = None
    requiere_revision: Optional[bool] = None
    aprobada: Optional[bool] = None


class ImagenMedicaResponse(ImagenMedicaBase):
    id: UUID
    usuario_id: UUID
    nombre_archivo: str
    ruta_archivo: str
    url_archivo: Optional[str]
    tipo_archivo: str
    tamanio_bytes: int
    ancho: Optional[int]
    alto: Optional[int]
    es_dicom: bool
    dicom_metadata: Optional[Dict[str, Any]]
    analisis_ia_completado: bool
    resultados_ia: Optional[Dict[str, Any]]
    confianza_ia: Optional[float]
    hallazgos: Optional[List[str]]
    anotaciones: Optional[List[Dict[str, Any]]]
    requiere_revision: bool
    aprobada: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# SOLICITUD DE ANÁLISIS IA
# ============================================================================

class SolicitudAnalisisIA(BaseModel):
    imagen_id: UUID
    modelo: str = Field(..., description="CheXNet, MONAI, etc.")
    opciones: Optional[Dict[str, Any]] = Field(default_factory=dict)


# ============================================================================
# COMPARACIÓN DE IMÁGENES
# ============================================================================

class ComparacionImagenes(BaseModel):
    imagen_id_1: UUID
    imagen_id_2: UUID
    notas_comparacion: Optional[str] = None


# ============================================================================
# GALERÍA (para respuesta con múltiples imágenes)
# ============================================================================

class GaleriaResponse(BaseModel):
    total: int
    imagenes: List[ImagenMedicaResponse]
    por_tipo: Dict[str, int] = Field(default_factory=dict)
    por_region: Dict[str, int] = Field(default_factory=dict)
