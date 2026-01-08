"""
Schemas para API Pública y Marketplace
"""

from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# ============================================================================
# API Keys
# ============================================================================


class APIKeyCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    descripcion: Optional[str] = None
    permisos: List[str] = Field(default_factory=list)
    scopes: List[str] = Field(default_factory=list)
    rate_limit_por_minuto: int = Field(default=60, ge=1, le=1000)
    rate_limit_por_dia: int = Field(default=10000, ge=1, le=1000000)
    webhook_url: Optional[str] = None
    eventos_suscritos: List[str] = Field(default_factory=list)
    expira_en: Optional[datetime] = None
    ip_whitelist: List[str] = Field(default_factory=list)
    entorno: str = Field(default="produccion")


class APIKeyResponse(BaseModel):
    id: UUID
    nombre: str
    descripcion: Optional[str]
    key: str
    secret: Optional[str] = None  # Solo se muestra al crear
    permisos: List[str]
    scopes: List[str]
    rate_limit_por_minuto: int
    rate_limit_por_dia: int
    webhook_url: Optional[str]
    eventos_suscritos: List[str]
    activa: bool
    expira_en: Optional[datetime]
    entorno: str
    created_at: datetime
    ultimo_uso: Optional[datetime]
    total_requests: int

    class Config:
        from_attributes = True


class APIKeyUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    permisos: Optional[List[str]] = None
    scopes: Optional[List[str]] = None
    rate_limit_por_minuto: Optional[int] = None
    rate_limit_por_dia: Optional[int] = None
    webhook_url: Optional[str] = None
    eventos_suscritos: Optional[List[str]] = None
    activa: Optional[bool] = None


# ============================================================================
# Webhooks
# ============================================================================


class WebhookCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    url: str = Field(..., min_length=1, max_length=500)
    eventos: List[str] = Field(..., min_items=1)
    max_reintentos: int = Field(default=3, ge=0, le=10)
    timeout_segundos: int = Field(default=30, ge=5, le=300)
    headers_personalizados: Optional[Dict[str, str]] = None


class WebhookResponse(BaseModel):
    id: UUID
    nombre: str
    url: str
    secret: str
    eventos: List[str]
    max_reintentos: int
    timeout_segundos: int
    activo: bool
    headers_personalizados: Optional[Dict[str, str]]
    created_at: datetime
    ultimo_envio: Optional[datetime]
    total_envios: int
    total_errores: int

    class Config:
        from_attributes = True


class WebhookUpdate(BaseModel):
    nombre: Optional[str] = None
    url: Optional[str] = None
    eventos: Optional[List[str]] = None
    max_reintentos: Optional[int] = None
    timeout_segundos: Optional[int] = None
    activo: Optional[bool] = None
    headers_personalizados: Optional[Dict[str, str]] = None


class EntregaWebhookResponse(BaseModel):
    id: UUID
    webhook_id: UUID
    evento: str
    payload: Dict[str, Any]
    intento: int
    status_code: Optional[int]
    tiempo_respuesta_ms: Optional[int]
    exitoso: bool
    error: Optional[str]
    timestamp: datetime
    proximo_reintento: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================================
# Plugins
# ============================================================================


class PluginCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    descripcion: str = Field(..., min_length=10)
    descripcion_larga: Optional[str] = None
    autor: str = Field(..., min_length=1, max_length=200)
    email_autor: Optional[str] = None
    url_autor: Optional[str] = None
    version: str = Field(..., min_length=1, max_length=50)
    version_minima_ddx: Optional[str] = None
    categoria: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    url_repositorio: Optional[str] = None
    url_documentacion: Optional[str] = None
    url_demo: Optional[str] = None
    url_icono: Optional[str] = None
    screenshots: List[str] = Field(default_factory=list)
    url_descarga: Optional[str] = None
    requiere_api_key: bool = Field(default=False)
    permisos_requeridos: List[str] = Field(default_factory=list)
    configuracion_schema: Optional[Dict[str, Any]] = None
    es_gratuito: bool = Field(default=True)
    precio_usd: int = Field(default=0, ge=0)

    @validator("slug")
    def validar_slug(cls, v):
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                "El slug solo puede contener letras, números, guiones y guiones bajos"
            )
        return v.lower()


class PluginResponse(BaseModel):
    id: UUID
    nombre: str
    slug: str
    descripcion: str
    descripcion_larga: Optional[str]
    autor: str
    email_autor: Optional[str]
    url_autor: Optional[str]
    version: str
    version_minima_ddx: Optional[str]
    categoria: Optional[str]
    tags: List[str]
    url_repositorio: Optional[str]
    url_documentacion: Optional[str]
    url_demo: Optional[str]
    url_icono: Optional[str]
    screenshots: List[str]
    url_descarga: Optional[str]
    requiere_api_key: bool
    permisos_requeridos: List[str]
    configuracion_schema: Optional[Dict[str, Any]]
    estado: str
    verificado: bool
    descargas: int
    instalaciones_activas: int
    calificacion_promedio: int
    total_calificaciones: int
    es_gratuito: bool
    precio_usd: int
    created_at: datetime
    updated_at: datetime
    fecha_aprobacion: Optional[datetime]

    class Config:
        from_attributes = True


class PluginUpdate(BaseModel):
    descripcion: Optional[str] = None
    descripcion_larga: Optional[str] = None
    version: Optional[str] = None
    categoria: Optional[str] = None
    tags: Optional[List[str]] = None
    url_repositorio: Optional[str] = None
    url_documentacion: Optional[str] = None
    url_demo: Optional[str] = None
    url_icono: Optional[str] = None
    screenshots: Optional[List[str]] = None
    url_descarga: Optional[str] = None
    precio_usd: Optional[int] = None


class InstalacionPluginCreate(BaseModel):
    plugin_id: UUID
    configuracion: Optional[Dict[str, Any]] = None
    api_key_id: Optional[UUID] = None


class InstalacionPluginResponse(BaseModel):
    id: UUID
    plugin_id: UUID
    configuracion: Optional[Dict[str, Any]]
    activo: bool
    version_instalada: str
    fecha_instalacion: datetime
    fecha_actualizacion: Optional[datetime]
    ultimo_uso: Optional[datetime]

    class Config:
        from_attributes = True


class ResenaPluginCreate(BaseModel):
    plugin_id: UUID
    calificacion: int = Field(..., ge=1, le=5)
    titulo: Optional[str] = Field(None, max_length=200)
    comentario: Optional[str] = None
    autor_nombre: str = Field(..., min_length=1, max_length=200)
    autor_email: Optional[str] = None
    version_plugin: str


class ResenaPluginResponse(BaseModel):
    id: UUID
    plugin_id: UUID
    calificacion: int
    titulo: Optional[str]
    comentario: Optional[str]
    autor_nombre: str
    version_plugin: str
    verificado: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Logs
# ============================================================================


class LogAPIPublicaResponse(BaseModel):
    id: UUID
    metodo: str
    endpoint: str
    ip_origen: Optional[str]
    status_code: Optional[int]
    tiempo_respuesta_ms: Optional[int]
    error: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Estadísticas
# ============================================================================


class EstadisticasAPI(BaseModel):
    total_requests: int
    requests_exitosos: int
    requests_fallidos: int
    tiempo_respuesta_promedio_ms: float
    endpoints_mas_usados: List[Dict[str, Any]]
    errores_comunes: List[Dict[str, Any]]
    uso_por_dia: List[Dict[str, Any]]


class EstadisticasMarketplace(BaseModel):
    total_plugins: int
    plugins_activos: int
    plugins_verificados: int
    total_descargas: int
    total_instalaciones: int
    plugins_populares: List[PluginResponse]
    categorias: List[Dict[str, int]]


# ============================================================================
# Documentación
# ============================================================================


class EndpointDoc(BaseModel):
    metodo: str
    ruta: str
    descripcion: str
    parametros: List[Dict[str, Any]]
    respuesta_ejemplo: Dict[str, Any]
    permisos_requeridos: List[str]
    rate_limit: str


class DocumentacionAPI(BaseModel):
    version: str
    base_url: str
    autenticacion: Dict[str, str]
    endpoints: List[EndpointDoc]
    ejemplos: List[Dict[str, Any]]
    errores_comunes: List[Dict[str, str]]
