"""
Modelos para Inteligencia Artificial Médica
"""

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer,
    Text,
    Boolean,
    Float,
    JSON,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class AnalisisIA(Base):
    """Análisis generales realizados por IA"""

    __tablename__ = "analisis_ia"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    medico_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)

    tipo_analisis = Column(
        String(100), nullable=False
    )  # diagnostico, riesgo, tratamiento, interacciones, anomalias
    contexto = Column(JSON)  # Datos de entrada para el análisis
    resultado = Column(JSON)  # Resultado estructurado del análisis
    confianza = Column(Float)  # Nivel de confianza (0-1)

    modelo_ia = Column(String(100))  # gpt-4, claude, etc.
    version_modelo = Column(String(50))
    tokens_utilizados = Column(Integer)
    tiempo_procesamiento = Column(Float)  # segundos

    validado_por_medico = Column(Boolean, default=False)
    fecha_validacion = Column(DateTime, nullable=True)
    notas_medico = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    paciente = relationship("Paciente", back_populates="analisis_ia")
    medico = relationship("Usuario")


class PrediccionRiesgo(Base):
    """Predicciones de riesgo para diferentes condiciones"""

    __tablename__ = "predicciones_riesgo"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    medico_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)

    tipo_riesgo = Column(
        String(100), nullable=False
    )  # cardiovascular, diabetes, cancer, etc.
    nivel_riesgo = Column(String(50))  # bajo, moderado, alto, muy_alto
    porcentaje_riesgo = Column(Float)  # 0-100

    factores_riesgo = Column(ARRAY(String))
    factores_protectores = Column(ARRAY(String))

    recomendaciones = Column(ARRAY(String))
    estudios_sugeridos = Column(ARRAY(String))

    datos_utilizados = Column(JSON)  # Datos del paciente utilizados
    algoritmo = Column(String(100))  # Framingham, SCORE, etc.

    valido_hasta = Column(DateTime)  # Fecha de revalidación

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    paciente = relationship("Paciente", back_populates="predicciones_riesgo")
    medico = relationship("Usuario")


class RecomendacionTratamiento(Base):
    """Recomendaciones de tratamiento generadas por IA"""

    __tablename__ = "recomendaciones_tratamiento"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    medico_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    diagnostico_id = Column(UUID(as_uuid=True), nullable=True)

    diagnostico_principal = Column(String(200))
    codigo_cie10 = Column(String(10))

    medicamentos_sugeridos = Column(
        JSON
    )  # [{nombre, dosis, frecuencia, duracion, razon}]
    terapias_no_farmacologicas = Column(ARRAY(String))
    cambios_estilo_vida = Column(ARRAY(String))

    contraindicaciones = Column(ARRAY(String))
    precauciones = Column(ARRAY(String))

    evidencia_cientifica = Column(JSON)  # Referencias y nivel de evidencia
    guias_clinicas = Column(ARRAY(String))

    prioridad = Column(String(50))  # inmediata, alta, media, baja

    aplicado = Column(Boolean, default=False)
    fecha_aplicacion = Column(DateTime, nullable=True)
    resultado_aplicacion = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    paciente = relationship("Paciente", back_populates="recomendaciones_tratamiento")
    medico = relationship("Usuario")


class InteraccionMedicamentosa(Base):
    """Análisis de interacciones entre medicamentos"""

    __tablename__ = "interacciones_medicamentosas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    medico_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)

    medicamentos_analizados = Column(ARRAY(String))

    interacciones_encontradas = Column(
        JSON
    )  # [{medicamento1, medicamento2, severidad, descripcion, manejo}]
    severidad_maxima = Column(String(50))  # leve, moderada, severa, contraindicada

    alertas_criticas = Column(ARRAY(String))
    recomendaciones_ajuste = Column(ARRAY(String))

    alergias_consideradas = Column(ARRAY(String))
    condiciones_consideradas = Column(ARRAY(String))

    fuente_datos = Column(String(100))  # DrugBank, FDA, etc.

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    paciente = relationship("Paciente", back_populates="interacciones_medicamentosas")
    medico = relationship("Usuario")


class AnomaliaDetectada(Base):
    """Anomalías detectadas en estudios por IA"""

    __tablename__ = "anomalias_detectadas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)

    tipo_estudio = Column(String(100))  # laboratorio, imagen, ekg, eeg, etc.
    estudio_id = Column(UUID(as_uuid=True))  # ID del estudio específico

    tipo_anomalia = Column(
        String(100)
    )  # valor_critico, patron_anormal, hallazgo_incidental
    severidad = Column(String(50))  # leve, moderada, severa, critica

    descripcion = Column(Text)
    localizacion = Column(String(200))  # Para imágenes

    valores_anormales = Column(JSON)  # Valores específicos fuera de rango
    patron_detectado = Column(String(200))

    confianza_deteccion = Column(Float)  # 0-1
    requiere_atencion_inmediata = Column(Boolean, default=False)

    recomendaciones = Column(ARRAY(String))
    estudios_adicionales = Column(ARRAY(String))

    revisado_por_medico = Column(Boolean, default=False)
    medico_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    fecha_revision = Column(DateTime, nullable=True)
    notas_revision = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    paciente = relationship("Paciente", back_populates="anomalias_detectadas")
    medico = relationship("Usuario")


class AsistenteIA(Base):
    """Conversaciones con el asistente de IA"""

    __tablename__ = "asistente_ia"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    medico_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=True)

    sesion_id = Column(UUID(as_uuid=True), default=uuid.uuid4)

    pregunta = Column(Text, nullable=False)
    respuesta = Column(Text, nullable=False)

    contexto = Column(JSON)  # Datos del paciente, estudios, etc.
    tipo_consulta = Column(
        String(100)
    )  # diagnostico, tratamiento, interpretacion, etc.

    util = Column(Boolean, nullable=True)  # Feedback del médico

    modelo_ia = Column(String(100))
    tokens_utilizados = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    medico = relationship("Usuario")
    paciente = relationship("Paciente", back_populates="consultas_asistente_ia")
