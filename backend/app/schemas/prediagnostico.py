"""
Schemas para Pre-diagnóstico Inteligente
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID


class SintomaInput(BaseModel):
    """Síntoma ingresado por el usuario"""

    descripcion: str = Field(..., min_length=1)
    intensidad: Optional[str] = None  # leve, moderado, severo
    duracion: Optional[str] = None
    frecuencia: Optional[str] = None


class PreDiagnosticoRequest(BaseModel):
    """Request para generar pre-diagnóstico"""

    paciente_id: UUID
    sintomas: List[SintomaInput] = Field(..., min_items=1)
    antecedentes: Optional[str] = None
    medicamentos_actuales: Optional[List[str]] = []
    alergias: Optional[List[str]] = []

    class Config:
        json_schema_extra = {
            "example": {
                "paciente_id": "123e4567-e89b-12d3-a456-426614174000",
                "sintomas": [
                    {
                        "descripcion": "Dolor de cabeza",
                        "intensidad": "moderado",
                        "duracion": "3 días",
                        "frecuencia": "constante",
                    }
                ],
                "antecedentes": "Hipertensión",
                "medicamentos_actuales": ["Losartán 50mg"],
                "alergias": [],
            }
        }


class DiagnosticoDiferencial(BaseModel):
    """Diagnóstico diferencial sugerido"""

    nombre: str
    codigo_cie10: Optional[str] = None
    probabilidad: float = Field(..., ge=0, le=100)  # 0-100%
    evidencias: List[str]
    sintomas_coincidentes: List[str]
    sintomas_faltantes: Optional[List[str]] = None
    urgencia: str  # bajo, medio, alto, critico
    recomendaciones: List[str]


class PreDiagnosticoResponse(BaseModel):
    """Respuesta con pre-diagnóstico y diferenciales"""

    diagnosticos_diferenciales: List[DiagnosticoDiferencial]
    sintomas_analizados: List[str]
    factores_riesgo: List[str]
    examenes_sugeridos: List[str]
    signos_alarma: List[str]
    recomendaciones_generales: List[str]
    nivel_urgencia: str
    timestamp: str


class AlgoritmoDecisionRequest(BaseModel):
    """Request para algoritmo de decisión clínica"""

    sintomas: List[str]
    signos_vitales: Optional[Dict[str, Any]] = None
    antecedentes: Optional[List[str]] = None
    edad: Optional[int] = None
    sexo: Optional[str] = None


class AlgoritmoDecisionResponse(BaseModel):
    """Respuesta del algoritmo de decisión"""

    decision: str
    nivel_urgencia: str
    acciones_inmediatas: List[str]
    examenes_prioritarios: List[str]
    diagnosticos_probables: List[str]
    justificacion: str
    score_gravedad: float  # 0-10
