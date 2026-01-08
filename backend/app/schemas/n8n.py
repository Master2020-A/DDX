"""
Schemas para N8N Integration
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# ========== N8N Config Schemas ==========


class N8NConfigBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    descripcion: Optional[str] = None
    n8n_webhook_url: str = Field(..., max_length=500)
    n8n_api_url: Optional[str] = Field(None, max_length=500)
    activo: bool = True
    webhooks_habilitados: bool = True
    timeout_segundos: int = Field(5, ge=1, le=60)
    eventos_habilitados: Optional[List[str]] = None


class N8NConfigCreate(N8NConfigBase):
    pass


class N8NConfigUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = None
    n8n_webhook_url: Optional[str] = Field(None, max_length=500)
    n8n_api_url: Optional[str] = Field(None, max_length=500)
    activo: Optional[bool] = None
    webhooks_habilitados: Optional[bool] = None
    timeout_segundos: Optional[int] = Field(None, ge=1, le=60)
    eventos_habilitados: Optional[List[str]] = None


class N8NConfigResponse(N8NConfigBase):
    id: UUID
    api_key: str
    total_eventos_enviados: int
    total_eventos_exitosos: int
    total_eventos_fallidos: int
    ultimo_evento_enviado: Optional[datetime]
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class N8NConfigStats(BaseModel):
    """Estadísticas de N8N"""

    total_eventos_enviados: int
    total_eventos_exitosos: int
    total_eventos_fallidos: int
    tasa_exito: float
    ultimo_evento_enviado: Optional[datetime]


# ========== N8N Event Log Schemas ==========


class N8NEventLogResponse(BaseModel):
    id: UUID
    evento_tipo: str
    evento_data: Dict[str, Any]
    prioridad: str
    webhook_url: str
    exitoso: bool
    codigo_http: Optional[int]
    tiempo_respuesta_ms: Optional[int]
    error: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ========== N8N Webhook Schemas ==========


class WebhookEventBase(BaseModel):
    """Base para eventos de webhook"""

    event: str
    data: Dict[str, Any]
    priority: str = "normal"


class WebhookTestRequest(BaseModel):
    """Request para probar webhook"""

    url: str = Field(..., max_length=500)
    event_type: str = Field(..., max_length=100)
    test_data: Optional[Dict[str, Any]] = None


class WebhookTestResponse(BaseModel):
    """Response de prueba de webhook"""

    exitoso: bool
    mensaje: str
    codigo_http: Optional[int]
    tiempo_respuesta_ms: Optional[int]
    error: Optional[str]


# ========== N8N Workflow Schemas ==========


class N8NWorkflowInfo(BaseModel):
    """Información de un workflow de N8N"""

    id: str
    name: str
    active: bool
    createdAt: Optional[datetime]
    updatedAt: Optional[datetime]


class N8NWorkflowExecution(BaseModel):
    """Ejecución de un workflow de N8N"""

    id: str
    workflowId: str
    finished: bool
    mode: str
    startedAt: datetime
    stoppedAt: Optional[datetime]
    status: str


class N8NWorkflowsStatus(BaseModel):
    """Estado de workflows de N8N"""

    total: int
    active: int
    inactive: int
    workflows: List[N8NWorkflowInfo]


class N8NExecutionsStatus(BaseModel):
    """Estado de ejecuciones de N8N"""

    total: int
    success: int
    failed: int
    running: int
    executions: List[N8NWorkflowExecution]


# ========== Eventos Específicos ==========


class EventoPacienteCreado(BaseModel):
    paciente_id: str
    nombre_completo: str
    edad: Optional[int]
    genero: Optional[str]


class EventoLaboratorioCritico(BaseModel):
    resultado_id: str
    paciente_id: str
    paciente_nombre: str
    parametro: str
    valor: float
    rango_normal: str
    nivel: str


class EventoCitaAgendada(BaseModel):
    cita_id: str
    paciente_id: str
    paciente_nombre: str
    paciente_email: Optional[str]
    paciente_telefono: Optional[str]
    medico_id: str
    medico_nombre: str
    fecha: str
    hora: str
    tipo: str


class EventoEstudioCompletado(BaseModel):
    estudio_id: str
    paciente_id: str
    tipo_estudio: str
    categoria: str


class EventoRecetaEmitida(BaseModel):
    receta_id: str
    paciente_id: str
    paciente_nombre: str
    medico_id: str
    medicamentos: List[Dict[str, Any]]
    farmacia_preferida: Optional[str]


# ========== API Key Management ==========


class N8NAPIKeyGenerate(BaseModel):
    """Request para generar API key"""

    nombre: str = Field(..., max_length=100)
    descripcion: Optional[str] = None


class N8NAPIKeyResponse(BaseModel):
    """Response con API key generada"""

    api_key: str
    mensaje: str
    expires_at: Optional[datetime]
    usage: str


# ========== Eventos Disponibles ==========


class EventoDisponible(BaseModel):
    """Información de un evento disponible"""

    nombre: str
    descripcion: str
    categoria: str
    prioridad_default: str
    ejemplo_payload: Dict[str, Any]


class EventosDisponiblesResponse(BaseModel):
    """Lista de eventos disponibles"""

    total: int
    categorias: List[str]
    eventos: List[EventoDisponible]
