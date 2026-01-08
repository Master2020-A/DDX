"""
Modelos de base de datos para el módulo de Integraciones
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base


class ConfiguracionIntegracion(Base):
    """
    Configuración general de integraciones con sistemas externos
    """
    __tablename__ = "configuraciones_integracion"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100), unique=True, nullable=False, index=True)
    tipo_sistema = Column(String(50), nullable=False)  # PACS, LIS, RECETA, FARMACIA, CFDI, ERP
    descripcion = Column(Text)
    
    # Conexión
    url_base = Column(String(500))
    puerto = Column(Integer)
    protocolo = Column(String(20))  # HTTP, HTTPS, HL7, DICOM
    
    # Autenticación
    tipo_auth = Column(String(20))  # BASIC, BEARER, OAUTH2, API_KEY
    usuario = Column(String(100))
    password_encrypted = Column(Text)
    api_key_encrypted = Column(Text)
    token_encrypted = Column(Text)
    
    # Configuración específica (JSON)
    configuracion_adicional = Column(JSON)
    
    # Webhooks
    webhook_url = Column(String(500))
    webhook_secret = Column(Text)
    
    # Reintentos y timeouts
    timeout_segundos = Column(Integer, default=30)
    max_reintentos = Column(Integer, default=3)
    intervalo_reintento_segundos = Column(Integer, default=60)
    
    # Estado
    activo = Column(Boolean, default=True)
    fecha_ultima_sincronizacion = Column(DateTime)
    
    # Logs
    log_requests = Column(Boolean, default=True)
    log_responses = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConfiguracionPACS(Base):
    """
    Configuración específica para servidores PACS (DICOM)
    """
    __tablename__ = "configuracion_pacs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    configuracion_id = Column(UUID(as_uuid=True), ForeignKey("configuraciones_integracion.id"))
    
    nombre = Column(String(100), nullable=False)
    servidor = Column(String(255), nullable=False)  # IP o hostname
    puerto = Column(Integer, default=11112)
    ae_title = Column(String(16), nullable=False)  # Application Entity Title
    ae_title_local = Column(String(16), default="DDX")
    
    # Credenciales
    usuario = Column(String(100))
    password_encrypted = Column(Text)
    
    # Configuración de transferencia
    timeout_segundos = Column(Integer, default=30)
    max_reintentos = Column(Integer, default=3)
    compresion = Column(Boolean, default=True)
    
    # Modalidades soportadas
    modalidades = Column(JSON)  # ["CT", "MRI", "XR", "US", "CR", "DX"]
    
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConfiguracionLIS(Base):
    """
    Configuración para Laboratory Information System
    """
    __tablename__ = "configuracion_lis"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    configuracion_id = Column(UUID(as_uuid=True), ForeignKey("configuraciones_integracion.id"))
    
    nombre = Column(String(100), nullable=False)
    tipo_integracion = Column(String(20), nullable=False)  # HL7, FHIR, API_REST
    
    # Conexión HL7
    hl7_servidor = Column(String(255))
    hl7_puerto = Column(Integer)
    
    # API REST
    api_url = Column(String(500))
    api_key_encrypted = Column(Text)
    
    # Webhook para resultados
    webhook_url = Column(String(500))
    webhook_secret = Column(Text)
    
    # Mapeo de códigos
    usar_loinc = Column(Boolean, default=True)
    mapeo_pruebas = Column(JSON)  # Mapeo local → LOINC
    
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RecetaElectronica(Base):
    """
    Recetas electrónicas con firma digital
    """
    __tablename__ = "recetas_electronicas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    folio = Column(String(50), unique=True, nullable=False, index=True)
    codigo_verificacion = Column(String(20), nullable=False)
    
    # Referencias
    paciente_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    medico_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    consulta_id = Column(UUID(as_uuid=True))
    
    # Datos de la receta
    fecha_emision = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_vencimiento = Column(DateTime)
    diagnostico_cie10 = Column(String(10))
    
    # Medicamentos (JSON)
    medicamentos = Column(JSON, nullable=False)
    
    # Firma electrónica
    certificado_medico = Column(Text)
    sello_digital = Column(Text)
    cadena_original = Column(Text)
    
    # Estado
    estado = Column(String(20), default="ACTIVA")  # ACTIVA, SURTIDA, PARCIAL, VENCIDA, CANCELADA
    fecha_surtido = Column(DateTime)
    farmacia_id = Column(UUID(as_uuid=True))
    
    # Trazabilidad
    intentos_validacion = Column(Integer, default=0)
    ultima_validacion = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SolicitudFarmacia(Base):
    """
    Solicitudes de medicamentos a farmacia
    """
    __tablename__ = "solicitudes_farmacia"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    folio = Column(String(50), unique=True, nullable=False, index=True)
    
    # Referencias
    receta_id = Column(UUID(as_uuid=True), ForeignKey("recetas_electronicas.id"))
    paciente_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    medico_id = Column(UUID(as_uuid=True))
    
    # Solicitud
    fecha_solicitud = Column(DateTime, default=datetime.utcnow, nullable=False)
    urgente = Column(Boolean, default=False)
    destino = Column(String(50))  # HOSPITALIZACION, URGENCIAS, AMBULATORIO
    ubicacion = Column(String(100))  # Cama, consultorio, etc.
    
    # Medicamentos (JSON)
    medicamentos_solicitados = Column(JSON, nullable=False)
    
    # Dispensación
    estado = Column(String(20), default="PENDIENTE")  # PENDIENTE, PROCESANDO, DISPENSADO, CANCELADO
    fecha_dispensacion = Column(DateTime)
    farmaceutico_id = Column(UUID(as_uuid=True))
    medicamentos_dispensados = Column(JSON)
    
    # Costos
    costo_total = Column(Numeric(10, 2))
    
    # Verificación
    verificado = Column(Boolean, default=False)
    verificado_por = Column(UUID(as_uuid=True))
    fecha_verificacion = Column(DateTime)
    
    # Notas
    notas = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FacturaElectronica(Base):
    """
    Facturas electrónicas CFDI 4.0
    """
    __tablename__ = "facturas_electronicas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    uuid_sat = Column(String(36), unique=True, index=True)
    serie = Column(String(25))
    folio = Column(String(40), nullable=False, index=True)
    
    # Referencias
    paciente_id = Column(UUID(as_uuid=True), index=True)
    consulta_id = Column(UUID(as_uuid=True))
    hospitalizacion_id = Column(UUID(as_uuid=True))
    
    # Datos fiscales
    tipo_comprobante = Column(String(1), nullable=False)  # I, E, P
    uso_cfdi = Column(String(3), nullable=False)
    metodo_pago = Column(String(3), nullable=False)
    forma_pago = Column(String(2))
    
    # Receptor
    receptor_rfc = Column(String(13), nullable=False)
    receptor_nombre = Column(String(254), nullable=False)
    receptor_cp = Column(String(5), nullable=False)
    receptor_regimen = Column(String(3))
    
    # Conceptos (JSON)
    conceptos = Column(JSON, nullable=False)
    
    # Importes
    subtotal = Column(Numeric(18, 6), nullable=False)
    descuento = Column(Numeric(18, 6))
    total = Column(Numeric(18, 6), nullable=False)
    
    # Timbrado
    fecha_emision = Column(DateTime, nullable=False)
    fecha_timbrado = Column(DateTime)
    sello_sat = Column(Text)
    sello_cfdi = Column(Text)
    cadena_original = Column(Text)
    
    # Archivos
    xml_content = Column(Text)
    pdf_content = Column(Text)  # Base64
    codigo_qr = Column(Text)
    
    # Estado
    estado = Column(String(20), default="PENDIENTE")  # PENDIENTE, TIMBRADA, CANCELADA
    fecha_cancelacion = Column(DateTime)
    motivo_cancelacion = Column(String(2))
    folio_sustitucion = Column(String(36))
    
    # PAC
    pac_proveedor = Column(String(50))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class IntegracionERP(Base):
    """
    Sincronización con ERP hospitalario
    """
    __tablename__ = "integraciones_erp"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tipo_entidad = Column(String(50), nullable=False, index=True)  # PACIENTE, SERVICIO, PAGO, INVENTARIO
    entidad_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # ID en DDX
    codigo_erp = Column(String(100), index=True)  # ID en ERP
    
    # Sincronización
    fecha_sincronizacion = Column(DateTime)
    estado_sincronizacion = Column(String(20), default="PENDIENTE")  # PENDIENTE, SINCRONIZADO, ERROR
    mensaje_error = Column(Text)
    intentos = Column(Integer, default=0)
    
    # Datos enviados/recibidos
    datos_enviados = Column(JSON)
    datos_recibidos = Column(JSON)
    
    # Trazabilidad
    sincronizado_por = Column(UUID(as_uuid=True))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LogIntegracion(Base):
    """
    Logs de todas las operaciones de integración
    """
    __tablename__ = "logs_integracion"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    configuracion_id = Column(UUID(as_uuid=True), ForeignKey("configuraciones_integracion.id"), index=True)
    
    # Operación
    operacion = Column(String(100), nullable=False, index=True)
    direccion = Column(String(10), nullable=False)  # SALIDA, ENTRADA
    tipo_sistema = Column(String(50), index=True)  # PACS, LIS, etc.
    
    # Request/Response
    url = Column(String(500))
    metodo = Column(String(10))  # GET, POST, PUT, DELETE
    headers = Column(JSON)
    request_body = Column(Text)
    response_status = Column(Integer)
    response_body = Column(Text)
    
    # Timing
    fecha_hora = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    duracion_ms = Column(Integer)
    
    # Estado
    exitoso = Column(Boolean, nullable=False, index=True)
    mensaje_error = Column(Text)
    
    # Contexto
    usuario_id = Column(UUID(as_uuid=True))
    entidad_relacionada_id = Column(UUID(as_uuid=True))
    entidad_relacionada_tipo = Column(String(50))
    
    created_at = Column(DateTime, default=datetime.utcnow)
