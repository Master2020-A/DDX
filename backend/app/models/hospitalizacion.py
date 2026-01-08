from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Integer, Text, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base


class EstadoHospitalizacionEnum(str, enum.Enum):
    ACTIVO = "activo"
    ALTA_MEDICA = "alta_medica"
    ALTA_VOLUNTARIA = "alta_voluntaria"
    DEFUNCION = "defuncion"
    TRASLADO = "traslado"


class EstadoCamaEnum(str, enum.Enum):
    DISPONIBLE = "disponible"
    OCUPADA = "ocupada"
    MANTENIMIENTO = "mantenimiento"
    LIMPIEZA = "limpieza"


class TipoNotaEnum(str, enum.Enum):
    INGRESO = "ingreso"
    EVOLUCION = "evolucion"
    INTERCONSULTA = "interconsulta"
    PROCEDIMIENTO = "procedimiento"
    ALTA = "alta"


class Hospitalizacion(Base):
    __tablename__ = "hospitalizaciones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id", ondelete="CASCADE"), nullable=False, index=True)
    consulta_id = Column(UUID(as_uuid=True), ForeignKey("consultas.id"), nullable=True)
    medico_responsable_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    
    # Fechas
    fecha_ingreso = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    fecha_alta = Column(DateTime(timezone=True), nullable=True)
    
    # Información de ingreso
    motivo_ingreso = Column(Text, nullable=False)
    diagnostico_ingreso = Column(Text, nullable=False)
    diagnostico_egreso = Column(Text, nullable=True)
    # resumen_clinico = Column(Text, nullable=True)  # Comentado temporalmente
    
    # Ubicación
    area_hospitalizacion = Column(String(100), nullable=True)  # Medicina Interna, Cirugía, UCI, etc.
    numero_cama = Column(String(20), nullable=True)
    # piso = Column(String(20), nullable=True)  # Comentado - no existe en BD
    
    # Estado y clasificación
    estado = Column(String(50), default='activo', index=True)
    prioridad = Column(String(20), default='normal')  # urgente, alta, normal, baja
    tipo_ingreso = Column(String(50), nullable=True)  # programado, urgencia, emergencia
    
    # Información adicional
    alergias_conocidas = Column(ARRAY(String), nullable=True)
    antecedentes_relevantes = Column(Text, nullable=True)
    tratamiento_actual = Column(Text, nullable=True)
    
    # Seguros y administrativo
    tipo_seguro = Column(String(100), nullable=True)
    numero_poliza = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    paciente = relationship("Paciente", foreign_keys=[paciente_id])
    medico_responsable = relationship("Usuario", foreign_keys=[medico_responsable_id])
    notas_evolucion = relationship("NotaEvolucion", back_populates="hospitalizacion", cascade="all, delete-orphan")
    indicaciones = relationship("IndicacionMedica", back_populates="hospitalizacion", cascade="all, delete-orphan")


class Cama(Base):
    __tablename__ = "camas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero_cama = Column(String(20), nullable=False, unique=True, index=True)
    area = Column(String(100), nullable=False)  # UCI, Medicina Interna, Cirugía, etc.
    piso = Column(String(20), nullable=True)
    habitacion = Column(String(20), nullable=True)
    
    # Estado
    estado = Column(String(50), default='disponible', index=True)
    
    # Características
    tipo_cama = Column(String(50), nullable=True)  # estándar, eléctrica, UCI, pediátrica
    tiene_oxigeno = Column(Boolean, default=False)
    tiene_monitor = Column(Boolean, default=False)
    tiene_ventilador = Column(Boolean, default=False)
    capacidad_peso = Column(Float, nullable=True)  # kg
    
    # Ocupación actual
    hospitalizacion_actual_id = Column(UUID(as_uuid=True), ForeignKey("hospitalizaciones.id"), nullable=True)
    fecha_ultima_limpieza = Column(DateTime(timezone=True), nullable=True)
    fecha_ultimo_mantenimiento = Column(DateTime(timezone=True), nullable=True)
    
    # Notas
    observaciones = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    hospitalizacion_actual = relationship("Hospitalizacion", foreign_keys=[hospitalizacion_actual_id])


class NotaEvolucion(Base):
    __tablename__ = "notas_evolucion"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hospitalizacion_id = Column(UUID(as_uuid=True), ForeignKey("hospitalizaciones.id", ondelete="CASCADE"), nullable=False, index=True)
    medico_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    
    # Información de la nota
    fecha_nota = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    tipo_nota = Column(String(50), default='evolucion')  # evolucion, ingreso, interconsulta, procedimiento, alta
    turno = Column(String(20), nullable=True)  # matutino, vespertino, nocturno
    
    # Contenido clínico
    subjetivo = Column(Text, nullable=True)  # Síntomas reportados por el paciente
    objetivo = Column(Text, nullable=True)  # Hallazgos del examen físico
    
    # Signos vitales
    temperatura = Column(Float, nullable=True)
    presion_arterial_sistolica = Column(Integer, nullable=True)
    presion_arterial_diastolica = Column(Integer, nullable=True)
    frecuencia_cardiaca = Column(Integer, nullable=True)
    frecuencia_respiratoria = Column(Integer, nullable=True)
    saturacion_oxigeno = Column(Float, nullable=True)
    
    # Evaluación y plan
    evaluacion = Column(Text, nullable=True)  # Análisis e interpretación
    plan = Column(Text, nullable=True)  # Plan de tratamiento
    
    # Estudios y procedimientos
    estudios_solicitados = Column(ARRAY(String), nullable=True)
    procedimientos_realizados = Column(ARRAY(String), nullable=True)
    
    # Estado del paciente
    estado_general = Column(String(50), nullable=True)  # estable, crítico, mejoría, deterioro
    nivel_conciencia = Column(String(50), nullable=True)  # alerta, somnoliento, estuporoso, coma
    
    # Notas adicionales
    observaciones = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    hospitalizacion = relationship("Hospitalizacion", back_populates="notas_evolucion")
    medico = relationship("Usuario", foreign_keys=[medico_id])


class IndicacionMedica(Base):
    __tablename__ = "indicaciones_medicas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hospitalizacion_id = Column(UUID(as_uuid=True), ForeignKey("hospitalizaciones.id", ondelete="CASCADE"), nullable=False, index=True)
    medico_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    
    # Información de la indicación
    fecha_indicacion = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    tipo_indicacion = Column(String(50), nullable=False)  # medicamento, dieta, cuidados, estudios, procedimiento
    
    # Detalles de la indicación
    descripcion = Column(Text, nullable=False)
    dosis = Column(String(200), nullable=True)  # Para medicamentos
    via_administracion = Column(String(50), nullable=True)  # oral, IV, IM, SC, etc.
    frecuencia = Column(String(100), nullable=True)  # cada 8 horas, 3 veces al día, etc.
    duracion = Column(String(100), nullable=True)  # 7 días, hasta nueva orden, etc.
    
    # Prioridad y estado
    prioridad = Column(String(20), default='normal')  # urgente, alta, normal
    estado = Column(String(50), default='activa')  # activa, suspendida, completada, cancelada
    
    # Fechas de vigencia
    fecha_inicio = Column(DateTime(timezone=True), nullable=True)
    fecha_fin = Column(DateTime(timezone=True), nullable=True)
    fecha_suspension = Column(DateTime(timezone=True), nullable=True)
    motivo_suspension = Column(Text, nullable=True)
    
    # Observaciones
    observaciones = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    hospitalizacion = relationship("Hospitalizacion", back_populates="indicaciones")
    medico = relationship("Usuario", foreign_keys=[medico_id])


class NotaAlta(Base):
    __tablename__ = "notas_alta"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hospitalizacion_id = Column(UUID(as_uuid=True), ForeignKey("hospitalizaciones.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    medico_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    
    # Información del alta
    fecha_alta = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    tipo_alta = Column(String(50), nullable=False)  # medica, voluntaria, defuncion, traslado
    
    # Resumen clínico
    motivo_ingreso = Column(Text, nullable=False)
    resumen_evolucion = Column(Text, nullable=False)
    diagnostico_egreso = Column(Text, nullable=False)
    procedimientos_realizados = Column(Text, nullable=True)
    complicaciones = Column(Text, nullable=True)
    
    # Condición al egreso
    condicion_egreso = Column(String(50), nullable=True)  # mejorado, curado, igual, agravado
    estado_funcional = Column(Text, nullable=True)
    
    # Indicaciones al alta
    medicamentos_egreso = Column(Text, nullable=True)
    dieta_recomendada = Column(Text, nullable=True)
    cuidados_domiciliarios = Column(Text, nullable=True)
    restricciones = Column(Text, nullable=True)
    
    # Seguimiento
    fecha_control = Column(DateTime(timezone=True), nullable=True)
    especialidad_control = Column(String(100), nullable=True)
    estudios_pendientes = Column(ARRAY(String), nullable=True)
    
    # Pronóstico
    pronostico = Column(Text, nullable=True)
    
    # Información adicional
    observaciones = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    hospitalizacion = relationship("Hospitalizacion", foreign_keys=[hospitalizacion_id])
    medico = relationship("Usuario", foreign_keys=[medico_id])
