"""
Modelos para Sistema de Interoperabilidad
Intercambio de expedientes, Red Nacional de Salud, Historia Clínica Unificada
"""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class TipoIntercambio(str, enum.Enum):
    """Tipos de intercambio de información"""

    EXPEDIENTE_COMPLETO = "expediente_completo"
    CONSULTA_ESPECIFICA = "consulta_especifica"
    LABORATORIO = "laboratorio"
    IMAGENES = "imagenes"
    RECETA = "receta"
    REFERENCIA = "referencia"
    CONTRA_REFERENCIA = "contra_referencia"


class EstadoIntercambio(str, enum.Enum):
    """Estados del intercambio"""

    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    COMPLETADO = "completado"
    RECHAZADO = "rechazado"
    ERROR = "error"


class ProtocoloIntercambio(str, enum.Enum):
    """Protocolos de intercambio soportados"""

    FHIR_R4 = "fhir_r4"
    HL7_V2 = "hl7_v2"
    HL7_V3 = "hl7_v3"
    DICOM = "dicom"
    CDA = "cda"  # Clinical Document Architecture
    CUSTOM = "custom"


class NivelConfianza(str, enum.Enum):
    """Nivel de confianza de la institución"""

    VERIFICADA = "verificada"
    CONFIABLE = "confiable"
    PENDIENTE_VERIFICACION = "pendiente_verificacion"
    NO_VERIFICADA = "no_verificada"


class InstitucionExterna(Base):
    """
    Registro de instituciones externas para intercambio
    """

    __tablename__ = "instituciones_externas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificación
    codigo_nacional = Column(String(50), unique=True, index=True)  # CLUES, NPI, etc.
    nombre = Column(String(255), nullable=False)
    tipo = Column(String(100))  # Hospital, Clínica, Laboratorio, etc.

    # Ubicación
    estado = Column(String(100))
    municipio = Column(String(100))
    direccion = Column(Text)

    # Contacto
    telefono = Column(String(20))
    email = Column(String(255))
    responsable_interoperabilidad = Column(String(255))

    # Configuración técnica
    endpoint_fhir = Column(String(500))
    endpoint_hl7 = Column(String(500))
    endpoint_custom = Column(String(500))
    protocolos_soportados = Column(JSON, default=list)  # ["fhir_r4", "hl7_v2"]

    # Seguridad
    api_key = Column(String(255))
    certificado_digital = Column(Text)  # Certificado X.509
    nivel_confianza = Column(
        SQLEnum(NivelConfianza), default=NivelConfianza.PENDIENTE_VERIFICACION
    )

    # Configuración
    acepta_solicitudes = Column(Boolean, default=True)
    puede_solicitar = Column(Boolean, default=True)
    requiere_autorizacion_paciente = Column(Boolean, default=True)

    # Metadata
    activa = Column(Boolean, default=True)
    notas = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    solicitudes_enviadas = relationship(
        "SolicitudIntercambio",
        foreign_keys="SolicitudIntercambio.institucion_destino_id",
        back_populates="institucion_destino",
    )
    solicitudes_recibidas = relationship(
        "SolicitudIntercambio",
        foreign_keys="SolicitudIntercambio.institucion_origen_id",
        back_populates="institucion_origen",
    )


class SolicitudIntercambio(Base):
    """
    Solicitudes de intercambio de información entre instituciones
    """

    __tablename__ = "solicitudes_intercambio"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Instituciones involucradas
    institucion_origen_id = Column(
        UUID(as_uuid=True),
        ForeignKey("instituciones_externas.id"),
        nullable=False,
        index=True,
    )
    institucion_destino_id = Column(
        UUID(as_uuid=True),
        ForeignKey("instituciones_externas.id"),
        nullable=False,
        index=True,
    )

    # Paciente
    paciente_id = Column(
        UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False, index=True
    )

    # Tipo de intercambio
    tipo = Column(SQLEnum(TipoIntercambio), nullable=False)
    protocolo = Column(SQLEnum(ProtocoloIntercambio), nullable=False)

    # Información solicitada
    descripcion = Column(Text)
    recursos_solicitados = Column(JSON)  # Lista de recursos FHIR o tipos de datos
    periodo_inicio = Column(DateTime)  # Período de información solicitada
    periodo_fin = Column(DateTime)

    # Estado
    estado = Column(SQLEnum(EstadoIntercambio), default=EstadoIntercambio.PENDIENTE)
    prioridad = Column(String(20), default="normal")  # urgente, alta, normal, baja

    # Autorización
    requiere_autorizacion = Column(Boolean, default=True)
    autorizado_por_paciente = Column(Boolean, default=False)
    fecha_autorizacion = Column(DateTime)
    documento_autorizacion_url = Column(String(500))

    # Respuesta
    fecha_respuesta = Column(DateTime)
    datos_intercambiados = Column(JSON)  # Datos en formato acordado
    url_documento = Column(String(500))  # URL del documento intercambiado
    mensaje_respuesta = Column(Text)

    # Auditoría
    solicitante_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    respondido_por = Column(String(255))

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    institucion_origen = relationship(
        "InstitucionExterna",
        foreign_keys=[institucion_origen_id],
        back_populates="solicitudes_enviadas",
    )
    institucion_destino = relationship(
        "InstitucionExterna",
        foreign_keys=[institucion_destino_id],
        back_populates="solicitudes_recibidas",
    )
    paciente = relationship("Paciente")
    solicitante = relationship("Usuario")


class HistoriaClinicaUnificada(Base):
    """
    Historia clínica unificada que consolida información de múltiples fuentes
    """

    __tablename__ = "historia_clinica_unificada"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Paciente
    paciente_id = Column(
        UUID(as_uuid=True),
        ForeignKey("pacientes.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Identificadores nacionales
    curp = Column(String(18), index=True)
    nss = Column(String(11), index=True)  # Número de Seguridad Social

    # Consolidación de datos
    consultas_totales = Column(Integer, default=0)
    hospitalizaciones_totales = Column(Integer, default=0)
    cirugias_totales = Column(Integer, default=0)

    # Resumen clínico consolidado
    diagnosticos_activos = Column(JSON, default=list)
    alergias_consolidadas = Column(JSON, default=list)
    medicamentos_actuales = Column(JSON, default=list)
    vacunas_aplicadas = Column(JSON, default=list)

    # Fuentes de información
    instituciones_contribuyentes = Column(JSON, default=list)  # Lista de instituciones
    ultima_actualizacion_externa = Column(DateTime)

    # Timeline unificado
    eventos_clinicos = Column(JSON, default=list)  # Timeline de eventos importantes

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación
    paciente = relationship("Paciente", back_populates="historia_unificada")


class LogIntercambio(Base):
    """
    Log de auditoría de todos los intercambios de información
    """

    __tablename__ = "logs_intercambio"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Referencia
    solicitud_id = Column(
        UUID(as_uuid=True), ForeignKey("solicitudes_intercambio.id"), index=True
    )

    # Detalles del intercambio
    accion = Column(String(100), nullable=False)  # solicitud, respuesta, error, etc.
    protocolo = Column(String(50))
    direccion = Column(String(20))  # entrante, saliente

    # Datos técnicos
    endpoint = Column(String(500))
    metodo_http = Column(String(10))
    codigo_respuesta = Column(Integer)
    tiempo_respuesta_ms = Column(Integer)

    # Contenido (opcional, para debugging)
    request_headers = Column(JSON)
    request_body = Column(Text)
    response_headers = Column(JSON)
    response_body = Column(Text)

    # Errores
    error = Column(Text)
    stack_trace = Column(Text)

    # Seguridad
    ip_origen = Column(String(45))
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))

    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relaciones
    solicitud = relationship("SolicitudIntercambio")
    usuario = relationship("Usuario")


class ConsentimientoIntercambio(Base):
    """
    Consentimientos de pacientes para intercambio de información
    """

    __tablename__ = "consentimientos_intercambio"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Paciente
    paciente_id = Column(
        UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False, index=True
    )

    # Alcance del consentimiento
    tipo_consentimiento = Column(String(50), nullable=False)  # general, especifico
    instituciones_autorizadas = Column(JSON, default=list)  # Lista de IDs o "todas"
    tipos_datos_autorizados = Column(
        JSON, default=list
    )  # consultas, labs, imagenes, etc.

    # Vigencia
    fecha_inicio = Column(DateTime, default=datetime.utcnow)
    fecha_expiracion = Column(DateTime)
    activo = Column(Boolean, default=True)

    # Restricciones
    puede_compartir_diagnosticos = Column(Boolean, default=True)
    puede_compartir_laboratorios = Column(Boolean, default=True)
    puede_compartir_imagenes = Column(Boolean, default=True)
    puede_compartir_recetas = Column(Boolean, default=True)
    puede_compartir_notas = Column(Boolean, default=False)

    # Documentación
    documento_firmado_url = Column(String(500))
    firma_digital = Column(Text)

    # Revocación
    revocado = Column(Boolean, default=False)
    fecha_revocacion = Column(DateTime)
    motivo_revocacion = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación
    paciente = relationship("Paciente")


class MapeoCodigos(Base):
    """
    Mapeo entre diferentes sistemas de codificación (ICD-10, SNOMED, LOINC, etc.)
    """

    __tablename__ = "mapeo_codigos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Sistema origen
    sistema_origen = Column(
        String(50), nullable=False, index=True
    )  # ICD-10, SNOMED, etc.
    codigo_origen = Column(String(50), nullable=False, index=True)
    descripcion_origen = Column(String(500))

    # Sistema destino
    sistema_destino = Column(String(50), nullable=False, index=True)
    codigo_destino = Column(String(50), nullable=False, index=True)
    descripcion_destino = Column(String(500))

    # Calidad del mapeo
    equivalencia = Column(String(20))  # exacta, aproximada, parcial
    confianza = Column(Integer)  # 0-100

    # Metadata
    fuente_mapeo = Column(String(100))  # WHO, SNOMED International, manual, etc.
    version = Column(String(20))
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
