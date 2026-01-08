"""
Schemas Pydantic para Sistema de Interoperabilidad
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator

from app.models.interoperabilidad import (
    TipoIntercambio,
    EstadoIntercambio,
    ProtocoloIntercambio,
    NivelConfianza,
)


# ============================================================================
# INSTITUCIÓN EXTERNA
# ============================================================================


class InstitucionExternaBase(BaseModel):
    codigo_nacional: str = Field(..., description="Código nacional (CLUES, NPI, etc.)")
    nombre: str
    tipo: Optional[str] = None
    estado: Optional[str] = None
    municipio: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    responsable_interoperabilidad: Optional[str] = None
    endpoint_fhir: Optional[str] = None
    endpoint_hl7: Optional[str] = None
    endpoint_custom: Optional[str] = None
    protocolos_soportados: List[str] = Field(default_factory=list)
    nivel_confianza: NivelConfianza = NivelConfianza.PENDIENTE_VERIFICACION
    acepta_solicitudes: bool = True
    puede_solicitar: bool = True
    requiere_autorizacion_paciente: bool = True
    notas: Optional[str] = None


class InstitucionExternaCreate(InstitucionExternaBase):
    pass


class InstitucionExternaUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    responsable_interoperabilidad: Optional[str] = None
    endpoint_fhir: Optional[str] = None
    endpoint_hl7: Optional[str] = None
    endpoint_custom: Optional[str] = None
    protocolos_soportados: Optional[List[str]] = None
    nivel_confianza: Optional[NivelConfianza] = None
    acepta_solicitudes: Optional[bool] = None
    puede_solicitar: Optional[bool] = None
    activa: Optional[bool] = None
    notas: Optional[str] = None


class InstitucionExternaResponse(InstitucionExternaBase):
    id: UUID
    api_key: Optional[str] = None
    activa: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# SOLICITUD DE INTERCAMBIO
# ============================================================================


class SolicitudIntercambioBase(BaseModel):
    institucion_destino_id: UUID
    paciente_id: UUID
    tipo: TipoIntercambio
    protocolo: ProtocoloIntercambio
    descripcion: Optional[str] = None
    recursos_solicitados: Optional[List[str]] = Field(default_factory=list)
    periodo_inicio: Optional[datetime] = None
    periodo_fin: Optional[datetime] = None
    prioridad: str = "normal"


class SolicitudIntercambioCreate(SolicitudIntercambioBase):
    pass


class SolicitudIntercambioUpdate(BaseModel):
    estado: Optional[EstadoIntercambio] = None
    autorizado_por_paciente: Optional[bool] = None
    fecha_autorizacion: Optional[datetime] = None
    documento_autorizacion_url: Optional[str] = None
    datos_intercambiados: Optional[Dict[str, Any]] = None
    url_documento: Optional[str] = None
    mensaje_respuesta: Optional[str] = None


class SolicitudIntercambioResponse(SolicitudIntercambioBase):
    id: UUID
    institucion_origen_id: UUID
    estado: EstadoIntercambio
    requiere_autorizacion: bool
    autorizado_por_paciente: bool
    fecha_autorizacion: Optional[datetime] = None
    fecha_respuesta: Optional[datetime] = None
    solicitante_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SolicitudIntercambioDetalle(SolicitudIntercambioResponse):
    """Respuesta detallada con información de instituciones"""

    institucion_origen: Optional[InstitucionExternaResponse] = None
    institucion_destino: Optional[InstitucionExternaResponse] = None
    datos_intercambiados: Optional[Dict[str, Any]] = None
    url_documento: Optional[str] = None
    mensaje_respuesta: Optional[str] = None


# ============================================================================
# HISTORIA CLÍNICA UNIFICADA
# ============================================================================


class EventoClinico(BaseModel):
    """Evento en el timeline clínico"""

    fecha: datetime
    tipo: str  # consulta, hospitalizacion, cirugia, laboratorio, etc.
    descripcion: str
    institucion: str
    gravedad: Optional[str] = None


class DiagnosticoConsolidado(BaseModel):
    """Diagnóstico consolidado de múltiples fuentes"""

    codigo_cie10: str
    descripcion: str
    fecha_diagnostico: datetime
    institucion: str
    activo: bool = True


class MedicamentoActual(BaseModel):
    """Medicamento actual del paciente"""

    nombre: str
    dosis: str
    frecuencia: str
    via_administracion: str
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    institucion_prescriptora: str


class HistoriaClinicaUnificadaBase(BaseModel):
    paciente_id: UUID
    curp: Optional[str] = None
    nss: Optional[str] = None


class HistoriaClinicaUnificadaResponse(HistoriaClinicaUnificadaBase):
    id: UUID
    consultas_totales: int
    hospitalizaciones_totales: int
    cirugias_totales: int
    diagnosticos_activos: List[Dict[str, Any]]
    alergias_consolidadas: List[Dict[str, Any]]
    medicamentos_actuales: List[Dict[str, Any]]
    vacunas_aplicadas: List[Dict[str, Any]]
    instituciones_contribuyentes: List[str]
    eventos_clinicos: List[Dict[str, Any]]
    ultima_actualizacion_externa: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActualizarHistoriaUnificada(BaseModel):
    """Actualización de historia clínica desde fuente externa"""

    diagnosticos_nuevos: Optional[List[DiagnosticoConsolidado]] = None
    medicamentos_nuevos: Optional[List[MedicamentoActual]] = None
    eventos_nuevos: Optional[List[EventoClinico]] = None
    alergias_nuevas: Optional[List[str]] = None
    vacunas_nuevas: Optional[List[Dict[str, Any]]] = None


# ============================================================================
# CONSENTIMIENTO DE INTERCAMBIO
# ============================================================================


class ConsentimientoIntercambioBase(BaseModel):
    paciente_id: UUID
    tipo_consentimiento: str = "general"
    instituciones_autorizadas: List[str] = Field(default_factory=lambda: ["todas"])
    tipos_datos_autorizados: List[str] = Field(
        default_factory=lambda: ["consultas", "laboratorios", "imagenes", "recetas"]
    )
    fecha_expiracion: Optional[datetime] = None
    puede_compartir_diagnosticos: bool = True
    puede_compartir_laboratorios: bool = True
    puede_compartir_imagenes: bool = True
    puede_compartir_recetas: bool = True
    puede_compartir_notas: bool = False


class ConsentimientoIntercambioCreate(ConsentimientoIntercambioBase):
    pass


class ConsentimientoIntercambioUpdate(BaseModel):
    instituciones_autorizadas: Optional[List[str]] = None
    tipos_datos_autorizados: Optional[List[str]] = None
    fecha_expiracion: Optional[datetime] = None
    puede_compartir_diagnosticos: Optional[bool] = None
    puede_compartir_laboratorios: Optional[bool] = None
    puede_compartir_imagenes: Optional[bool] = None
    puede_compartir_recetas: Optional[bool] = None
    puede_compartir_notas: Optional[bool] = None
    activo: Optional[bool] = None


class ConsentimientoIntercambioResponse(ConsentimientoIntercambioBase):
    id: UUID
    fecha_inicio: datetime
    activo: bool
    revocado: bool
    fecha_revocacion: Optional[datetime] = None
    motivo_revocacion: Optional[str] = None
    documento_firmado_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RevocarConsentimiento(BaseModel):
    """Schema para revocar un consentimiento"""

    motivo: str


# ============================================================================
# MAPEO DE CÓDIGOS
# ============================================================================


class MapeoCodigo(BaseModel):
    sistema_origen: str
    codigo_origen: str
    descripcion_origen: Optional[str] = None
    sistema_destino: str
    codigo_destino: str
    descripcion_destino: Optional[str] = None
    equivalencia: str = "exacta"
    confianza: int = Field(100, ge=0, le=100)
    fuente_mapeo: Optional[str] = None
    version: Optional[str] = None


class MapeoCodigos(BaseModel):
    """Múltiples mapeos de códigos"""

    mapeos: List[MapeoCodigo]


# ============================================================================
# ESTADÍSTICAS Y DASHBOARDS
# ============================================================================


class EstadisticasIntercambio(BaseModel):
    """Estadísticas de intercambio de información"""

    total_solicitudes: int
    solicitudes_pendientes: int
    solicitudes_completadas: int
    solicitudes_rechazadas: int
    solicitudes_error: int
    instituciones_activas: int
    pacientes_con_consentimiento: int
    tiempo_promedio_respuesta_horas: float
    tasa_exito: float


class DashboardInteroperabilidad(BaseModel):
    """Dashboard completo de interoperabilidad"""

    estadisticas: EstadisticasIntercambio
    solicitudes_recientes: List[SolicitudIntercambioResponse]
    instituciones_frecuentes: List[Dict[str, Any]]
    protocolos_mas_usados: Dict[str, int]
    tipos_intercambio_mas_comunes: Dict[str, int]


# ============================================================================
# INTERCAMBIO DE EXPEDIENTE COMPLETO
# ============================================================================


class ExpedienteCompletoFHIR(BaseModel):
    """Expediente completo en formato FHIR Bundle"""

    resourceType: str = "Bundle"
    type: str = "collection"
    timestamp: datetime
    entry: List[Dict[str, Any]]


class SolicitudExpedienteCompleto(BaseModel):
    """Solicitud de expediente completo"""

    paciente_id: UUID
    institucion_destino_id: UUID
    incluir_consultas: bool = True
    incluir_laboratorios: bool = True
    incluir_imagenes: bool = True
    incluir_recetas: bool = True
    incluir_hospitalizaciones: bool = True
    periodo_inicio: Optional[datetime] = None
    periodo_fin: Optional[datetime] = None
    formato: str = "fhir_r4"  # fhir_r4, hl7_v2, pdf
    motivo: str


class RespuestaExpediente(BaseModel):
    """Respuesta con expediente completo"""

    solicitud_id: UUID
    formato: str
    url_descarga: Optional[str] = None
    datos: Optional[Dict[str, Any]] = None
    fecha_generacion: datetime
    valido_hasta: datetime
    checksum: str


# --- Fix: faltaba MapeoCodigosCreate (lo importan los routers) ---
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class MapeoCodigosCreate(BaseModel):
    codigo_origen: str
    sistema_origen: str
    codigo_destino: str
    sistema_destino: str
    descripcion: Optional[str] = None
    activo: bool = True


class MapeoCodigosUpdate(BaseModel):
    codigo_origen: Optional[str] = None
    sistema_origen: Optional[str] = None
    codigo_destino: Optional[str] = None
    sistema_destino: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


class MapeoCodigosResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    codigo_origen: str
    sistema_origen: str
    codigo_destino: str
    sistema_destino: str
    descripcion: Optional[str] = None
    activo: bool = True
    created_at: Optional[datetime] = None
