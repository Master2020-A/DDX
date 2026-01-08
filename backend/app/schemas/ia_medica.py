"""
Schemas para Inteligencia Artificial Médica
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# ==================== ASISTENTE DE DIAGNÓSTICO ====================


class AsistenteConsultaRequest(BaseModel):
    """Request para consultar al asistente de IA"""

    pregunta: str = Field(..., description="Pregunta o consulta al asistente")
    paciente_id: Optional[UUID] = Field(None, description="ID del paciente (opcional)")
    incluir_historial: bool = Field(True, description="Incluir historial del paciente")
    incluir_estudios: bool = Field(True, description="Incluir estudios recientes")
    tipo_consulta: Optional[str] = Field(None, description="Tipo de consulta")


class AsistenteConsultaResponse(BaseModel):
    """Response del asistente de IA"""

    id: UUID
    pregunta: str
    respuesta: str
    contexto_utilizado: Dict[str, Any]
    tipo_consulta: str
    referencias: List[str] = []
    created_at: datetime


# ==================== PREDICCIÓN DE RIESGOS ====================


class PrediccionRiesgoRequest(BaseModel):
    """Request para predicción de riesgos"""

    paciente_id: UUID
    tipo_riesgo: str = Field(
        ..., description="cardiovascular, diabetes, cancer_pulmon, etc."
    )
    incluir_recomendaciones: bool = True


class FactorRiesgo(BaseModel):
    """Factor de riesgo individual"""

    nombre: str
    valor: Any
    impacto: str  # alto, medio, bajo
    modificable: bool


class PrediccionRiesgoResponse(BaseModel):
    """Response de predicción de riesgos"""

    id: UUID
    paciente_id: UUID
    tipo_riesgo: str
    nivel_riesgo: str
    porcentaje_riesgo: float

    factores_riesgo: List[FactorRiesgo]
    factores_protectores: List[str]

    recomendaciones: List[str]
    estudios_sugeridos: List[str]

    algoritmo: str
    valido_hasta: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== RECOMENDACIONES DE TRATAMIENTO ====================


class RecomendacionTratamientoRequest(BaseModel):
    """Request para recomendaciones de tratamiento"""

    paciente_id: UUID
    diagnostico_principal: str
    codigo_cie10: Optional[str] = None
    sintomas: List[str] = []
    comorbilidades: List[str] = []


class MedicamentoSugerido(BaseModel):
    """Medicamento sugerido con detalles"""

    nombre: str
    dosis: str
    frecuencia: str
    duracion: str
    via_administracion: str
    razon: str
    nivel_evidencia: str


class RecomendacionTratamientoResponse(BaseModel):
    """Response de recomendaciones de tratamiento"""

    id: UUID
    paciente_id: UUID
    diagnostico_principal: str
    codigo_cie10: Optional[str]

    medicamentos_sugeridos: List[MedicamentoSugerido]
    terapias_no_farmacologicas: List[str]
    cambios_estilo_vida: List[str]

    contraindicaciones: List[str]
    precauciones: List[str]

    guias_clinicas: List[str]
    prioridad: str

    created_at: datetime

    class Config:
        from_attributes = True


# ==================== INTERACCIONES MEDICAMENTOSAS ====================


class InteraccionMedicamentosaRequest(BaseModel):
    """Request para análisis de interacciones"""

    paciente_id: UUID
    medicamentos: List[str] = Field(
        ..., min_length=2, description="Lista de medicamentos a analizar"
    )
    incluir_alergias: bool = True
    incluir_condiciones: bool = True


class Interaccion(BaseModel):
    """Interacción entre medicamentos"""

    medicamento1: str
    medicamento2: str
    severidad: str  # leve, moderada, severa, contraindicada
    descripcion: str
    mecanismo: str
    efectos: List[str]
    manejo: str


class InteraccionMedicamentosaResponse(BaseModel):
    """Response de análisis de interacciones"""

    id: UUID
    paciente_id: UUID
    medicamentos_analizados: List[str]

    interacciones_encontradas: List[Interaccion]
    severidad_maxima: str

    alertas_criticas: List[str]
    recomendaciones_ajuste: List[str]

    alergias_consideradas: List[str]
    condiciones_consideradas: List[str]

    created_at: datetime

    class Config:
        from_attributes = True


# ==================== DETECCIÓN DE ANOMALÍAS ====================


class DeteccionAnomaliasRequest(BaseModel):
    """Request para detección de anomalías"""

    paciente_id: UUID
    tipo_estudio: str  # laboratorio, imagen, ekg, eeg
    estudio_id: Optional[UUID] = None
    datos_estudio: Optional[Dict[str, Any]] = None


class AnomaliaDetectadaResponse(BaseModel):
    """Response de anomalía detectada"""

    id: UUID
    paciente_id: UUID
    tipo_estudio: str
    estudio_id: Optional[UUID]

    tipo_anomalia: str
    severidad: str
    descripcion: str
    localizacion: Optional[str]

    valores_anormales: Dict[str, Any]
    patron_detectado: Optional[str]

    confianza_deteccion: float
    requiere_atencion_inmediata: bool

    recomendaciones: List[str]
    estudios_adicionales: List[str]

    created_at: datetime

    class Config:
        from_attributes = True


# ==================== RECONOCIMIENTO DE IMÁGENES ====================


class ReconocimientoImagenRequest(BaseModel):
    """Request para reconocimiento de imágenes médicas"""

    imagen_id: UUID
    tipo_analisis: str = Field(
        ..., description="clasificacion, segmentacion, deteccion"
    )
    modelo: Optional[str] = Field("gpt-4-vision", description="Modelo de IA a utilizar")


class HallazgoImagen(BaseModel):
    """Hallazgo en imagen médica"""

    tipo: str
    descripcion: str
    localizacion: str
    severidad: str
    confianza: float
    coordenadas: Optional[Dict[str, Any]] = None


class ReconocimientoImagenResponse(BaseModel):
    """Response de reconocimiento de imagen"""

    imagen_id: UUID
    tipo_analisis: str

    hallazgos: List[HallazgoImagen]
    impresion_diagnostica: str
    recomendaciones: List[str]

    confianza_general: float
    requiere_revision: bool

    modelo_utilizado: str
    tiempo_procesamiento: float

    created_at: datetime


# ==================== DASHBOARD DE IA ====================


class EstadisticasIA(BaseModel):
    """Estadísticas generales de uso de IA"""

    total_analisis: int
    analisis_por_tipo: Dict[str, int]

    predicciones_riesgo_activas: int
    anomalias_pendientes_revision: int
    interacciones_criticas: int

    tiempo_promedio_respuesta: float
    tasa_validacion_medico: float

    consultas_asistente_hoy: int
    consultas_asistente_mes: int


class AnalisisReciente(BaseModel):
    """Análisis reciente resumido"""

    id: UUID
    tipo: str
    paciente_nombre: str
    resultado_resumen: str
    severidad: Optional[str]
    created_at: datetime


class DashboardIAResponse(BaseModel):
    """Response del dashboard de IA"""

    estadisticas: EstadisticasIA
    analisis_recientes: List[AnalisisReciente]
    alertas_criticas: List[Dict[str, Any]]
    recomendaciones_pendientes: int
