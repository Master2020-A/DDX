"""
Modelos para sistema Multi-Tenancy
Soporte para múltiples hospitales/instituciones
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Boolean,
    Integer,
    Numeric,
    JSON,
    Enum as SQLEnum,
    ForeignKey,  # ← AGREGADO
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.models.metricas_uso import MetricaUso
from app.core.database import Base


class TipoInstitucion(str, enum.Enum):
    """Tipos de instituciones médicas"""

    HOSPITAL_PUBLICO = "hospital_publico"
    HOSPITAL_PRIVADO = "hospital_privado"
    CLINICA = "clinica"
    CONSULTORIO = "consultorio"
    LABORATORIO = "laboratorio"
    CENTRO_DIAGNOSTICO = "centro_diagnostico"
    OTRO = "otro"


class PlanSuscripcion(str, enum.Enum):
    """Planes de suscripción disponibles"""

    BASICO = "basico"
    PROFESIONAL = "profesional"
    EMPRESARIAL = "empresarial"
    PERSONALIZADO = "personalizado"


class EstadoInstitucion(str, enum.Enum):
    """Estados de la institución"""

    ACTIVA = "activa"
    SUSPENDIDA = "suspendida"
    PRUEBA = "prueba"
    CANCELADA = "cancelada"


class Institucion(Base):
    """
    Modelo principal de Multi-Tenancy
    Representa un hospital, clínica u otra institución médica
    """

    __tablename__ = "instituciones"

    # Identificación
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(
        String(50), unique=True, nullable=False, index=True
    )  # Código único corto
    nombre = Column(String(255), nullable=False)
    nombre_comercial = Column(String(255))
    tipo = Column(
        SQLEnum(TipoInstitucion), nullable=False, default=TipoInstitucion.CLINICA
    )

    # Información legal
    razon_social = Column(String(255))
    rfc = Column(String(13), unique=True)
    registro_sanitario = Column(String(100))

    # Contacto
    telefono = Column(String(20))
    email = Column(String(255), nullable=False)
    sitio_web = Column(String(255))

    # Dirección
    direccion = Column(Text)
    ciudad = Column(String(100))
    estado_geografico = Column(String(100))  # ← RENOMBRADO (antes: estado)
    codigo_postal = Column(String(10))
    pais = Column(String(100), default="México")

    # Configuración de suscripción
    plan = Column(
        SQLEnum(PlanSuscripcion), nullable=False, default=PlanSuscripcion.BASICO
    )
    estado = Column(
        SQLEnum(EstadoInstitucion), nullable=False, default=EstadoInstitucion.PRUEBA
    )
    fecha_inicio_suscripcion = Column(DateTime, default=datetime.utcnow)
    fecha_fin_prueba = Column(DateTime)
    fecha_renovacion = Column(DateTime)

    # Límites y cuotas
    max_usuarios = Column(Integer, default=5)
    max_pacientes = Column(Integer, default=100)
    max_almacenamiento_gb = Column(Integer, default=10)

    # Uso actual (para facturación)
    usuarios_activos = Column(Integer, default=0)
    pacientes_registrados = Column(Integer, default=0)
    almacenamiento_usado_gb = Column(Numeric(10, 2), default=0)

    # Configuración personalizada
    configuracion = Column(JSON, default=dict)  # ← Cambiado de {} a dict

    # Facturación
    metodo_pago = Column(String(50))
    dia_facturacion = Column(Integer, default=1)
    moneda = Column(String(3), default="MXN")

    # Branding
    logo_url = Column(String(500))
    favicon_url = Column(String(500))
    color_primario = Column(String(7), default="#1976d2")
    color_secundario = Column(String(7), default="#dc004e")

    # Seguridad
    ip_permitidas = Column(JSON, default=list)  # ← Cambiado de None a list
    require_2fa = Column(Boolean, default=False)
    sesion_timeout_minutos = Column(Integer, default=60)

    # Metadata
    notas_internas = Column(Text)
    activa = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    usuarios = relationship("Usuario", back_populates="institucion", lazy="dynamic")
    pacientes = relationship("Paciente", back_populates="institucion", lazy="dynamic")
    metricas_uso = relationship(
        "MetricaUso", back_populates="institucion", cascade="all, delete-orphan"
    )
    facturas = relationship(
        "FacturaInstitucion", back_populates="institucion", cascade="all, delete-orphan"
    )
    configuraciones_modulos = relationship(
        "ConfiguracionModulo",
        back_populates="institucion",
        cascade="all, delete-orphan",
    )


class MetricaUso(Base):
    """
    Métricas de uso para facturación
    Registra el uso diario/mensual de recursos por institución
    """

    __abstract__ = True
    # __tablename__ = "metricas_uso"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ✅ CORREGIDO: Agregado ForeignKey
    institucion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("instituciones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Período
    fecha = Column(DateTime, nullable=False, index=True)
    tipo_periodo = Column(String(20), default="diario")

    # Métricas de uso
    usuarios_activos = Column(Integer, default=0)
    pacientes_nuevos = Column(Integer, default=0)
    consultas_realizadas = Column(Integer, default=0)
    estudios_laboratorio = Column(Integer, default=0)
    estudios_imagenes = Column(Integer, default=0)
    almacenamiento_gb = Column(Numeric(10, 2), default=0)

    # Uso de módulos
    uso_telemedicina_minutos = Column(Integer, default=0)
    uso_ia_analisis = Column(Integer, default=0)
    mensajes_enviados = Column(Integer, default=0)
    reportes_generados = Column(Integer, default=0)

    # API calls
    api_calls = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación
    institucion = relationship("Institucion", back_populates="metricas_uso")


class FacturaInstitucion(Base):
    """
    Facturas generadas para cada institución
    """

    __tablename__ = "facturas_instituciones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ✅ CORREGIDO: Agregado ForeignKey
    institucion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("instituciones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Información de factura
    numero_factura = Column(String(50), unique=True, nullable=False)
    fecha_emision = Column(DateTime, nullable=False, default=datetime.utcnow)
    fecha_vencimiento = Column(DateTime, nullable=False)

    # Período facturado
    periodo_inicio = Column(DateTime, nullable=False)
    periodo_fin = Column(DateTime, nullable=False)

    # Montos
    subtotal = Column(Numeric(10, 2), nullable=False)
    impuestos = Column(Numeric(10, 2), default=0)
    descuentos = Column(Numeric(10, 2), default=0)
    total = Column(Numeric(10, 2), nullable=False)
    moneda = Column(String(3), default="MXN")

    # Desglose de conceptos
    conceptos = Column(JSON, default=list)

    # Estado
    estado = Column(String(20), default="pendiente")
    fecha_pago = Column(DateTime)
    metodo_pago = Column(String(50))
    referencia_pago = Column(String(100))

    # Archivos
    pdf_url = Column(String(500))
    xml_url = Column(String(500))

    # Metadata
    notas = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación
    institucion = relationship("Institucion", back_populates="facturas")


class ConfiguracionModulo(Base):
    """
    Configuración específica de módulos por institución
    """

    __tablename__ = "configuraciones_modulos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ✅ CORREGIDO: Agregado ForeignKey
    institucion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("instituciones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Módulo
    modulo = Column(String(50), nullable=False)
    activo = Column(Boolean, default=True)

    # Configuración específica del módulo
    configuracion = Column(JSON, default=dict)

    # Permisos y restricciones
    permisos = Column(JSON, default=dict)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ✅ AGREGADO: Relación inversa
    institucion = relationship("Institucion", back_populates="configuraciones_modulos")
