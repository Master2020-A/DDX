"""
Schemas Pydantic para el módulo de Integraciones
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# ============================================================================
# Configuración General
# ============================================================================


class ConfiguracionIntegracionBase(BaseModel):
    nombre: str
    tipo_sistema: str  # PACS, LIS, RECETA, FARMACIA, CFDI, ERP
    descripcion: Optional[str] = None
    url_base: Optional[str] = None
    puerto: Optional[int] = None
    protocolo: Optional[str] = None
    tipo_auth: Optional[str] = None
    usuario: Optional[str] = None
    configuracion_adicional: Optional[Dict[str, Any]] = None
    webhook_url: Optional[str] = None
    timeout_segundos: int = 30
    max_reintentos: int = 3
    intervalo_reintento_segundos: int = 60
    activo: bool = True
    log_requests: bool = True
    log_responses: bool = True


class ConfiguracionIntegracionCreate(ConfiguracionIntegracionBase):
    password: Optional[str] = None
    api_key: Optional[str] = None
    token: Optional[str] = None
    webhook_secret: Optional[str] = None


class ConfiguracionIntegracionUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    url_base: Optional[str] = None
    puerto: Optional[int] = None
    protocolo: Optional[str] = None
    tipo_auth: Optional[str] = None
    usuario: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    token: Optional[str] = None
    configuracion_adicional: Optional[Dict[str, Any]] = None
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    timeout_segundos: Optional[int] = None
    max_reintentos: Optional[int] = None
    intervalo_reintento_segundos: Optional[int] = None
    activo: Optional[bool] = None
    log_requests: Optional[bool] = None
    log_responses: Optional[bool] = None


class ConfiguracionIntegracionResponse(ConfiguracionIntegracionBase):
    id: UUID
    fecha_ultima_sincronizacion: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# PACS
# ============================================================================


class ConfiguracionPACSBase(BaseModel):
    nombre: str
    servidor: str
    puerto: int = 11112
    ae_title: str
    ae_title_local: str = "DDX"
    usuario: Optional[str] = None
    timeout_segundos: int = 30
    max_reintentos: int = 3
    compresion: bool = True
    modalidades: Optional[List[str]] = None
    activo: bool = True


class ConfiguracionPACSCreate(ConfiguracionPACSBase):
    configuracion_id: UUID
    password: Optional[str] = None


class ConfiguracionPACSResponse(ConfiguracionPACSBase):
    id: UUID
    configuracion_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EnviarEstudioPACS(BaseModel):
    estudio_id: UUID
    pacs_servidor: str
    pacs_puerto: int = 11112
    ae_title: str
    modalidad: str


# ============================================================================
# LIS
# ============================================================================


class ConfiguracionLISBase(BaseModel):
    nombre: str
    tipo_integracion: str  # HL7, FHIR, API_REST
    hl7_servidor: Optional[str] = None
    hl7_puerto: Optional[int] = None
    api_url: Optional[str] = None
    webhook_url: Optional[str] = None
    usar_loinc: bool = True
    mapeo_pruebas: Optional[Dict[str, str]] = None
    activo: bool = True


class ConfiguracionLISCreate(ConfiguracionLISBase):
    configuracion_id: UUID
    api_key: Optional[str] = None
    webhook_secret: Optional[str] = None


class ConfiguracionLISResponse(ConfiguracionLISBase):
    id: UUID
    configuracion_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrdenLaboratorioLIS(BaseModel):
    paciente_id: UUID
    medico_id: UUID
    pruebas: List[Dict[str, Any]]
    muestra: Dict[str, Any]
    prioridad: str = "ROUTINE"


class ResultadoLaboratorioLIS(BaseModel):
    orden_id: str
    paciente_id: UUID
    fecha_resultado: datetime
    estado: str
    resultados: List[Dict[str, Any]]


# ============================================================================
# Receta Electrónica
# ============================================================================


class MedicamentoReceta(BaseModel):
    nombre_generico: str
    nombre_comercial: Optional[str] = None
    presentacion: str
    dosis: str
    frecuencia: str
    via: str
    duracion_dias: int
    cantidad: int
    indicaciones: Optional[str] = None


class RecetaElectronicaBase(BaseModel):
    paciente_id: UUID
    medico_id: UUID
    consulta_id: Optional[UUID] = None
    diagnostico_cie10: Optional[str] = None
    medicamentos: List[MedicamentoReceta]
    vigencia_dias: int = 30


class RecetaElectronicaCreate(RecetaElectronicaBase):
    pass


class FirmaElectronica(BaseModel):
    certificado: str
    sello: str


class RecetaElectronicaResponse(BaseModel):
    id: UUID
    folio: str
    codigo_verificacion: str
    paciente_id: UUID
    medico_id: UUID
    consulta_id: Optional[UUID] = None
    fecha_emision: datetime
    fecha_vencimiento: Optional[datetime] = None
    diagnostico_cie10: Optional[str] = None
    medicamentos: List[Dict[str, Any]]
    estado: str
    fecha_surtido: Optional[datetime] = None
    farmacia_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ValidarReceta(BaseModel):
    folio_receta: str
    codigo_verificacion: str


class SurtirReceta(BaseModel):
    folio_receta: str
    farmacia_id: UUID
    fecha_surtido: datetime
    medicamentos_surtidos: List[Dict[str, Any]]


# ============================================================================
# Farmacia
# ============================================================================


class MedicamentoSolicitud(BaseModel):
    codigo: str
    nombre: str
    cantidad: int
    urgente: bool = False


class SolicitudFarmaciaBase(BaseModel):
    paciente_id: UUID
    medico_id: Optional[UUID] = None
    receta_id: Optional[UUID] = None
    medicamentos_solicitados: List[MedicamentoSolicitud]
    urgente: bool = False
    destino: str
    ubicacion: Optional[str] = None
    notas: Optional[str] = None


class SolicitudFarmaciaCreate(SolicitudFarmaciaBase):
    pass


class SolicitudFarmaciaResponse(BaseModel):
    id: UUID
    folio: str
    paciente_id: UUID
    medico_id: Optional[UUID] = None
    receta_id: Optional[UUID] = None
    fecha_solicitud: datetime
    urgente: bool
    destino: str
    ubicacion: Optional[str] = None
    medicamentos_solicitados: List[Dict[str, Any]]
    estado: str
    fecha_dispensacion: Optional[datetime] = None
    farmaceutico_id: Optional[UUID] = None
    medicamentos_dispensados: Optional[List[Dict[str, Any]]] = None
    costo_total: Optional[float] = None
    verificado: bool
    notas: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DispensarMedicamentos(BaseModel):
    solicitud_id: UUID
    farmaceutico_id: UUID
    medicamentos_dispensados: List[Dict[str, Any]]
    costo_total: float
    verificado_por: Optional[UUID] = None


class ConsultarDisponibilidad(BaseModel):
    medicamento: str
    cantidad_requerida: int


# ============================================================================
# Facturación Electrónica
# ============================================================================


class ReceptorCFDI(BaseModel):
    rfc: str
    nombre: str
    codigo_postal: str
    regimen_fiscal: str


class ConceptoCFDI(BaseModel):
    clave_prod_serv: str
    cantidad: float
    unidad: str
    descripcion: str
    valor_unitario: float
    importe: float
    objeto_imp: str = "02"


class ImpuestosCFDI(BaseModel):
    traslados: Optional[List[Dict[str, Any]]] = None
    retenciones: Optional[List[Dict[str, Any]]] = None


class FacturaElectronicaBase(BaseModel):
    paciente_id: Optional[UUID] = None
    consulta_id: Optional[UUID] = None
    hospitalizacion_id: Optional[UUID] = None
    tipo_comprobante: str
    uso_cfdi: str
    metodo_pago: str
    forma_pago: Optional[str] = None
    receptor: ReceptorCFDI
    conceptos: List[ConceptoCFDI]
    impuestos: Optional[ImpuestosCFDI] = None
    subtotal: float
    descuento: Optional[float] = None
    total: float


class FacturaElectronicaCreate(FacturaElectronicaBase):
    serie: Optional[str] = None


class FacturaElectronicaResponse(BaseModel):
    id: UUID
    uuid_sat: Optional[str] = None
    serie: Optional[str] = None
    folio: str
    paciente_id: Optional[UUID] = None
    tipo_comprobante: str
    uso_cfdi: str
    metodo_pago: str
    forma_pago: Optional[str] = None
    receptor_rfc: str
    receptor_nombre: str
    receptor_cp: str
    conceptos: List[Dict[str, Any]]
    subtotal: float
    descuento: Optional[float] = None
    total: float
    fecha_emision: datetime
    fecha_timbrado: Optional[datetime] = None
    estado: str
    pac_proveedor: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TimbrarFactura(BaseModel):
    factura_id: UUID
    pac_proveedor: str = "FINKOK"


class CancelarFactura(BaseModel):
    uuid: str
    motivo: str
    folio_sustitucion: Optional[str] = None


# ============================================================================
# ERP
# ============================================================================


class IntegracionERPBase(BaseModel):
    tipo_entidad: str
    entidad_id: UUID
    codigo_erp: Optional[str] = None
    datos_enviados: Optional[Dict[str, Any]] = None


class IntegracionERPCreate(IntegracionERPBase):
    pass


class IntegracionERPResponse(BaseModel):
    id: UUID
    tipo_entidad: str
    entidad_id: UUID
    codigo_erp: Optional[str] = None
    fecha_sincronizacion: Optional[datetime] = None
    estado_sincronizacion: str
    mensaje_error: Optional[str] = None
    intentos: int
    datos_enviados: Optional[Dict[str, Any]] = None
    datos_recibidos: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SincronizarPacienteERP(BaseModel):
    paciente_id: UUID
    accion: str  # CREATE, UPDATE, DELETE
    datos: Dict[str, Any]


class RegistrarServicioERP(BaseModel):
    consulta_id: UUID
    paciente_codigo_erp: str
    servicios: List[Dict[str, Any]]
    fecha_servicio: datetime
    departamento: str


# ============================================================================
# Logs
# ============================================================================


class LogIntegracionBase(BaseModel):
    configuracion_id: Optional[UUID] = None
    operacion: str
    direccion: str
    tipo_sistema: str
    url: Optional[str] = None
    metodo: Optional[str] = None
    headers: Optional[Dict[str, Any]] = None
    request_body: Optional[str] = None
    response_status: Optional[int] = None
    response_body: Optional[str] = None
    duracion_ms: Optional[int] = None
    exitoso: bool
    mensaje_error: Optional[str] = None
    usuario_id: Optional[UUID] = None
    entidad_relacionada_id: Optional[UUID] = None
    entidad_relacionada_tipo: Optional[str] = None


class LogIntegracionCreate(LogIntegracionBase):
    pass


class LogIntegracionResponse(LogIntegracionBase):
    id: UUID
    fecha_hora: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Dashboard
# ============================================================================


class EstadisticasIntegracion(BaseModel):
    activo: bool
    operaciones_hoy: int
    operaciones_exitosas_hoy: int
    operaciones_fallidas_hoy: int
    operaciones_pendientes: int
    ultima_sincronizacion: Optional[datetime] = None
    tasa_exito: float


class DashboardIntegraciones(BaseModel):
    pacs: Optional[EstadisticasIntegracion] = None
    lis: Optional[EstadisticasIntegracion] = None
    receta_electronica: Optional[EstadisticasIntegracion] = None
    farmacia: Optional[EstadisticasIntegracion] = None
    facturacion: Optional[EstadisticasIntegracion] = None
    erp: Optional[EstadisticasIntegracion] = None
