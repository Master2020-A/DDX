from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Text,
    JSON,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class TipoNormativa(str, enum.Enum):
    HIPAA = "HIPAA"
    GDPR = "GDPR"
    NOM_004 = "NOM-004-SSA3-2012"
    OTRA = "OTRA"


class TipoConsentimiento(str, enum.Enum):
    TRATAMIENTO = "TRATAMIENTO"
    CIRUGIA = "CIRUGIA"
    ANESTESIA = "ANESTESIA"
    INVESTIGACION = "INVESTIGACION"
    DATOS_PERSONALES = "DATOS_PERSONALES"
    IMAGEN = "IMAGEN"
    OTRO = "OTRO"


class EstadoConsentimiento(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    ACEPTADO = "ACEPTADO"
    RECHAZADO = "RECHAZADO"
    REVOCADO = "REVOCADO"


class TipoAccesoSensible(str, enum.Enum):
    LECTURA = "LECTURA"
    MODIFICACION = "MODIFICACION"
    ELIMINACION = "ELIMINACION"
    EXPORTACION = "EXPORTACION"
    IMPRESION = "IMPRESION"


class ConfiguracionCumplimiento(Base):
    __tablename__ = "configuracion_cumplimiento"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    normativa = Column(SQLEnum(TipoNormativa), nullable=False, unique=True)
    habilitado = Column(Boolean, default=True, nullable=False)

    # Configuración específica por normativa
    configuracion = Column(JSON, nullable=True)

    # HIPAA
    requiere_autorizacion_acceso = Column(Boolean, default=True)
    requiere_log_acceso = Column(Boolean, default=True)
    dias_retencion_logs = Column(Integer, default=2555)  # 7 años

    # GDPR
    requiere_consentimiento_explicito = Column(Boolean, default=True)
    permite_portabilidad_datos = Column(Boolean, default=True)
    permite_derecho_olvido = Column(Boolean, default=True)
    dias_respuesta_solicitud = Column(Integer, default=30)

    # NOM-004-SSA3-2012
    requiere_firma_electronica = Column(Boolean, default=True)
    requiere_expediente_electronico = Column(Boolean, default=True)
    requiere_respaldo_informacion = Column(Boolean, default=True)

    notas = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FirmaElectronica(Base):
    __tablename__ = "firmas_electronicas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Usuario que firma
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)

    # Documento/Recurso firmado
    recurso_tipo = Column(
        String(100), nullable=False
    )  # nota_medica, consentimiento, receta, etc.
    recurso_id = Column(UUID(as_uuid=True), nullable=False)

    # Datos de la firma
    firma_digital = Column(Text, nullable=False)  # Hash criptográfico
    certificado = Column(Text, nullable=True)  # Certificado digital (opcional)
    algoritmo = Column(String(50), default="SHA-256", nullable=False)

    # Metadatos
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    ubicacion = Column(JSON, nullable=True)  # Geolocalización

    # Validación
    valida = Column(Boolean, default=True, nullable=False)
    fecha_validacion = Column(DateTime, nullable=True)
    motivo_invalidacion = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones
    usuario = relationship("Usuario", back_populates="firmas_electronicas")


class ConsentimientoInformado(Base):
    __tablename__ = "consentimientos_informados"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Paciente
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)

    # Tipo y estado
    tipo = Column(SQLEnum(TipoConsentimiento), nullable=False)
    estado = Column(
        SQLEnum(EstadoConsentimiento),
        default=EstadoConsentimiento.PENDIENTE,
        nullable=False,
    )

    # Contenido
    titulo = Column(String(500), nullable=False)
    descripcion = Column(Text, nullable=False)
    riesgos = Column(JSON, nullable=True)  # Lista de riesgos
    beneficios = Column(JSON, nullable=True)  # Lista de beneficios
    alternativas = Column(JSON, nullable=True)  # Alternativas de tratamiento

    # Documento
    documento_url = Column(String(1000), nullable=True)
    documento_hash = Column(String(256), nullable=True)  # Hash del documento

    # Firma del paciente
    firma_paciente_id = Column(
        UUID(as_uuid=True), ForeignKey("firmas_electronicas.id"), nullable=True
    )
    fecha_firma_paciente = Column(DateTime, nullable=True)

    # Firma del médico
    medico_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    firma_medico_id = Column(
        UUID(as_uuid=True), ForeignKey("firmas_electronicas.id"), nullable=True
    )
    fecha_firma_medico = Column(DateTime, nullable=True)

    # Testigos (opcional)
    testigos = Column(JSON, nullable=True)

    # Revocación
    fecha_revocacion = Column(DateTime, nullable=True)
    motivo_revocacion = Column(Text, nullable=True)

    # Metadatos
    ip_address = Column(String(45), nullable=True)
    dispositivo = Column(String(200), nullable=True)

    # Relación con procedimiento/consulta
    consulta_id = Column(UUID(as_uuid=True), ForeignKey("consultas.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    paciente = relationship("Paciente", back_populates="consentimientos_informados")
    medico = relationship("Usuario", foreign_keys=[medico_id])
    firma_paciente = relationship("FirmaElectronica", foreign_keys=[firma_paciente_id])
    firma_medico = relationship("FirmaElectronica", foreign_keys=[firma_medico_id])
    consulta = relationship("Consulta", back_populates="consentimientos_informados")


class LogAccesoSensible(Base):
    __tablename__ = "logs_acceso_sensible"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Usuario que accede
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)

    # Recurso accedido
    recurso_tipo = Column(
        String(100), nullable=False
    )  # expediente, imagen_medica, laboratorio, etc.
    recurso_id = Column(UUID(as_uuid=True), nullable=False)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=True)

    # Tipo de acceso
    tipo_acceso = Column(SQLEnum(TipoAccesoSensible), nullable=False)

    # Detalles del acceso
    accion = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    datos_accedidos = Column(JSON, nullable=True)  # Campos específicos accedidos

    # Justificación (requerido por HIPAA)
    justificacion = Column(Text, nullable=True)
    autorizado = Column(Boolean, default=True, nullable=False)

    # Metadatos técnicos
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    endpoint = Column(String(500), nullable=True)
    metodo_http = Column(String(10), nullable=True)

    # Cumplimiento
    normativa_aplicable = Column(SQLEnum(TipoNormativa), nullable=True)

    # Auditoría
    auditado = Column(Boolean, default=False, nullable=False)
    fecha_auditoria = Column(DateTime, nullable=True)
    resultado_auditoria = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relaciones
    usuario = relationship("Usuario", back_populates="logs_acceso_sensible")
    paciente = relationship("Paciente", back_populates="logs_acceso_sensible")


class SolicitudDatosPersonales(Base):
    __tablename__ = "solicitudes_datos_personales"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Paciente solicitante
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)

    # Tipo de solicitud (GDPR)
    tipo_solicitud = Column(
        String(100), nullable=False
    )  # acceso, rectificacion, portabilidad, olvido

    # Estado
    estado = Column(
        String(50), default="PENDIENTE", nullable=False
    )  # PENDIENTE, EN_PROCESO, COMPLETADA, RECHAZADA

    # Detalles
    descripcion = Column(Text, nullable=False)
    datos_solicitados = Column(JSON, nullable=True)

    # Respuesta
    fecha_respuesta = Column(DateTime, nullable=True)
    respuesta = Column(Text, nullable=True)
    archivo_respuesta_url = Column(String(1000), nullable=True)

    # Usuario que procesa
    procesado_por_id = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )

    # Plazos (GDPR: 30 días)
    fecha_limite = Column(DateTime, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    paciente = relationship("Paciente", back_populates="solicitudes_datos_personales")
    procesado_por = relationship("Usuario")


class AuditoriaHIPAA(Base):
    __tablename__ = "auditoria_hipaa"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Período de auditoría
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)

    # Auditor
    auditor_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)

    # Resultados
    total_accesos = Column(Integer, default=0)
    accesos_autorizados = Column(Integer, default=0)
    accesos_no_autorizados = Column(Integer, default=0)
    accesos_sospechosos = Column(Integer, default=0)

    # Hallazgos
    hallazgos = Column(JSON, nullable=True)
    recomendaciones = Column(JSON, nullable=True)

    # Cumplimiento
    nivel_cumplimiento = Column(Integer, nullable=True)  # Porcentaje 0-100
    cumple_normativa = Column(Boolean, default=True)

    # Documentación
    reporte_url = Column(String(1000), nullable=True)
    notas = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones
    auditor = relationship("Usuario")
