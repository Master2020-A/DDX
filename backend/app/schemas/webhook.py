"""
Schemas Pydantic para Webhooks de Interoperabilidad
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from uuid import UUID


class WebhookSuscripcionCreate(BaseModel):
    """Schema para crear una suscripción de webhook"""

    nombre: str = Field(..., min_length=1, max_length=200)
    descripcion: Optional[str] = None
    url: str = Field(..., description="URL de destino del webhook")
    eventos: List[str] = Field(
        ..., min_items=1, description="Lista de eventos a suscribirse"
    )
    secret_key: Optional[str] = Field(
        None,
        description="Clave secreta (se genera automáticamente si no se proporciona)",
    )
    headers_adicionales: Optional[Dict[str, str]] = None
    timeout_segundos: int = Field(30, ge=5, le=120)
    reintentos_max: int = Field(3, ge=1, le=10)
    filtros: Optional[Dict[str, Any]] = None
    institucion_id: Optional[UUID] = None


class WebhookSuscripcionUpdate(BaseModel):
    """Schema para actualizar una suscripción de webhook"""

    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion: Optional[str] = None
    url: Optional[str] = None
    eventos: Optional[List[str]] = None
    headers_adicionales: Optional[Dict[str, str]] = None
    timeout_segundos: Optional[int] = Field(None, ge=5, le=120)
    reintentos_max: Optional[int] = Field(None, ge=1, le=10)
    activo: Optional[bool] = None
    estado: Optional[str] = None
    filtros: Optional[Dict[str, Any]] = None


class WebhookSuscripcionResponse(BaseModel):
    """Schema de respuesta para suscripción de webhook"""

    id: UUID
    nombre: str
    descripcion: Optional[str]
    url: str
    eventos: List[str]
    secret_key: str
    headers_adicionales: Optional[Dict[str, str]]
    timeout_segundos: int
    reintentos_max: int
    activo: bool
    estado: str
    filtros: Optional[Dict[str, Any]]
    usuario_id: UUID
    institucion_id: Optional[UUID]
    total_envios: int
    total_exitosos: int
    total_fallidos: int
    ultimo_envio: Optional[datetime]
    ultimo_exito: Optional[datetime]
    ultimo_error: Optional[str]
    ultimo_error_fecha: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class WebhookEntregaResponse(BaseModel):
    """Schema de respuesta para entrega de webhook"""

    id: UUID
    suscripcion_id: UUID
    evento: str
    payload: Dict[str, Any]
    url: str
    metodo: str
    headers: Optional[Dict[str, str]]
    exitoso: bool
    codigo_http: Optional[int]
    respuesta: Optional[str]
    error: Optional[str]
    tiempo_respuesta_ms: Optional[int]
    intento: int
    max_intentos: int
    created_at: datetime
    completado_at: Optional[datetime]

    class Config:
        from_attributes = True


class WebhookEventoTest(BaseModel):
    """Schema para enviar evento de prueba"""

    mensaje: Optional[str] = "Evento de prueba"


class WebhookEstadisticas(BaseModel):
    """Schema para estadísticas de webhooks"""

    total_suscripciones: int
    suscripciones_activas: int
    suscripciones_pausadas: int
    suscripciones_error: int
    total_entregas_24h: int
    entregas_exitosas_24h: int
    entregas_fallidas_24h: int
    tasa_exito_porcentaje: float
    eventos_mas_comunes: List[Dict[str, Any]]
