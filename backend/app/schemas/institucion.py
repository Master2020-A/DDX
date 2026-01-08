"""
Schemas Pydantic para Multi-Tenancy
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.models.institucion import (
    TipoInstitucion,
    PlanSuscripcion,
    EstadoInstitucion,
)


# ============================================================================
# INSTITUCIÓN
# ============================================================================


class InstitucionBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=255)
    nombre_comercial: Optional[str] = None
    tipo: TipoInstitucion
    razon_social: Optional[str] = None
    rfc: Optional[str] = Field(None, max_length=13)
    registro_sanitario: Optional[str] = None
    telefono: Optional[str] = None
    email: EmailStr
    sitio_web: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    estado: Optional[str] = None
    codigo_postal: Optional[str] = None
    pais: str = "México"


class InstitucionCreate(InstitucionBase):
    codigo: str = Field(..., min_length=2, max_length=50)
    plan: PlanSuscripcion = PlanSuscripcion.BASICO
    max_usuarios: int = 5
    max_pacientes: int = 100
    max_almacenamiento_gb: int = 10
    configuracion: Optional[Dict[str, Any]] = {}

    @validator("codigo")
    def codigo_valido(cls, v):
        # Solo letras, números y guiones
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                "Código debe contener solo letras, números, guiones y guiones bajos"
            )
        return v.lower()


class InstitucionUpdate(BaseModel):
    nombre: Optional[str] = None
    nombre_comercial: Optional[str] = None
    tipo: Optional[TipoInstitucion] = None
    razon_social: Optional[str] = None
    rfc: Optional[str] = None
    registro_sanitario: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    sitio_web: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    estado: Optional[str] = None
    codigo_postal: Optional[str] = None
    pais: Optional[str] = None
    plan: Optional[PlanSuscripcion] = None
    estado_institucion: Optional[EstadoInstitucion] = None
    max_usuarios: Optional[int] = None
    max_pacientes: Optional[int] = None
    max_almacenamiento_gb: Optional[int] = None
    configuracion: Optional[Dict[str, Any]] = None
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    color_primario: Optional[str] = None
    color_secundario: Optional[str] = None
    require_2fa: Optional[bool] = None
    sesion_timeout_minutos: Optional[int] = None
    activa: Optional[bool] = None


class InstitucionResponse(InstitucionBase):
    id: UUID
    codigo: str
    plan: PlanSuscripcion
    estado: EstadoInstitucion
    fecha_inicio_suscripcion: datetime
    fecha_fin_prueba: Optional[datetime]
    fecha_renovacion: Optional[datetime]
    max_usuarios: int
    max_pacientes: int
    max_almacenamiento_gb: int
    usuarios_activos: int
    pacientes_registrados: int
    almacenamiento_usado_gb: float
    configuracion: Dict[str, Any]
    logo_url: Optional[str]
    color_primario: str
    color_secundario: str
    require_2fa: bool
    activa: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InstitucionResumen(BaseModel):
    """Resumen de institución para listados"""

    id: UUID
    codigo: str
    nombre: str
    tipo: TipoInstitucion
    plan: PlanSuscripcion
    estado: EstadoInstitucion
    usuarios_activos: int
    pacientes_registrados: int
    activa: bool

    class Config:
        from_attributes = True


# ============================================================================
# MÉTRICAS DE USO
# ============================================================================


class MetricaUsoCreate(BaseModel):
    institucion_id: UUID
    fecha: datetime
    tipo_periodo: str = "diario"
    usuarios_activos: int = 0
    pacientes_nuevos: int = 0
    consultas_realizadas: int = 0
    estudios_laboratorio: int = 0
    estudios_imagenes: int = 0
    almacenamiento_gb: float = 0
    uso_telemedicina_minutos: int = 0
    uso_ia_analisis: int = 0
    mensajes_enviados: int = 0
    reportes_generados: int = 0
    api_calls: int = 0


class MetricaUsoResponse(BaseModel):
    id: UUID
    institucion_id: UUID
    fecha: datetime
    tipo_periodo: str
    usuarios_activos: int
    pacientes_nuevos: int
    consultas_realizadas: int
    estudios_laboratorio: int
    estudios_imagenes: int
    almacenamiento_gb: float
    uso_telemedicina_minutos: int
    uso_ia_analisis: int
    mensajes_enviados: int
    reportes_generados: int
    api_calls: int
    created_at: datetime

    class Config:
        from_attributes = True


class ResumenUso(BaseModel):
    """Resumen de uso para dashboard"""

    periodo_inicio: datetime
    periodo_fin: datetime
    total_usuarios: int
    total_pacientes: int
    total_consultas: int
    total_estudios: int
    almacenamiento_total_gb: float
    tendencia_usuarios: float  # % cambio vs período anterior
    tendencia_pacientes: float
    tendencia_consultas: float


# ============================================================================
# FACTURACIÓN
# ============================================================================


class ConceptoFactura(BaseModel):
    concepto: str
    cantidad: int
    precio_unitario: float
    total: float


class FacturaCreate(BaseModel):
    institucion_id: UUID
    periodo_inicio: datetime
    periodo_fin: datetime
    conceptos: List[ConceptoFactura]
    subtotal: float
    impuestos: float = 0
    descuentos: float = 0
    total: float
    fecha_vencimiento: datetime
    notas: Optional[str] = None


class FacturaUpdate(BaseModel):
    estado: Optional[str] = None
    fecha_pago: Optional[datetime] = None
    metodo_pago: Optional[str] = None
    referencia_pago: Optional[str] = None
    pdf_url: Optional[str] = None
    xml_url: Optional[str] = None


class FacturaResponse(BaseModel):
    id: UUID
    institucion_id: UUID
    numero_factura: str
    fecha_emision: datetime
    fecha_vencimiento: datetime
    periodo_inicio: datetime
    periodo_fin: datetime
    subtotal: float
    impuestos: float
    descuentos: float
    total: float
    moneda: str
    conceptos: List[Dict[str, Any]]
    estado: str
    fecha_pago: Optional[datetime]
    metodo_pago: Optional[str]
    referencia_pago: Optional[str]
    pdf_url: Optional[str]
    xml_url: Optional[str]
    notas: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ResumenFacturacion(BaseModel):
    """Resumen de facturación para dashboard"""

    total_facturado: float
    total_cobrado: float
    total_pendiente: float
    facturas_vencidas: int
    proxima_facturacion: Optional[datetime]
    mrr: float  # Monthly Recurring Revenue


# ============================================================================
# CONFIGURACIÓN DE MÓDULOS
# ============================================================================


class ConfiguracionModuloCreate(BaseModel):
    institucion_id: UUID
    modulo: str
    activo: bool = True
    configuracion: Dict[str, Any] = {}
    permisos: Dict[str, Any] = {}


class ConfiguracionModuloUpdate(BaseModel):
    activo: Optional[bool] = None
    configuracion: Optional[Dict[str, Any]] = None
    permisos: Optional[Dict[str, Any]] = None


class ConfiguracionModuloResponse(BaseModel):
    id: UUID
    institucion_id: UUID
    modulo: str
    activo: bool
    configuracion: Dict[str, Any]
    permisos: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# DASHBOARD MULTI-TENANT
# ============================================================================


class EstadisticasInstitucion(BaseModel):
    """Estadísticas generales de una institución"""

    institucion_id: UUID
    nombre_institucion: str
    plan: PlanSuscripcion
    estado: EstadoInstitucion

    # Uso actual
    usuarios_activos: int
    pacientes_registrados: int
    almacenamiento_usado_gb: float

    # Límites
    max_usuarios: int
    max_pacientes: int
    max_almacenamiento_gb: int

    # Porcentajes de uso
    uso_usuarios_pct: float
    uso_pacientes_pct: float
    uso_almacenamiento_pct: float

    # Actividad reciente (últimos 30 días)
    consultas_mes: int
    estudios_mes: int
    ingresos_mes: float

    # Estado de cuenta
    facturas_pendientes: int
    monto_pendiente: float
    dias_hasta_renovacion: Optional[int]


class DashboardMultiTenant(BaseModel):
    """Dashboard completo para administración multi-tenant"""

    total_instituciones: int
    instituciones_activas: int
    instituciones_prueba: int
    instituciones_suspendidas: int

    # Métricas globales
    total_usuarios: int
    total_pacientes: int
    total_almacenamiento_gb: float

    # Ingresos
    mrr_total: float  # Monthly Recurring Revenue
    arr_total: float  # Annual Recurring Revenue
    ingresos_mes_actual: float
    ingresos_mes_anterior: float
    crecimiento_ingresos_pct: float

    # Top instituciones
    top_instituciones_por_uso: List[EstadisticasInstitucion]
    top_instituciones_por_ingresos: List[EstadisticasInstitucion]

    # Alertas
    instituciones_limite_usuarios: List[UUID]
    instituciones_limite_almacenamiento: List[UUID]
    facturas_vencidas: int
    renovaciones_proximas: int
