"""
Modelos para Procesamiento de Lenguaje Natural (PLN)
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
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class TranscripcionVoz(Base):
    """Transcripciones de audio a texto"""

    __tablename__ = "transcripciones_voz"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=True)
    medico_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    consulta_id = Column(UUID(as_uuid=True), ForeignKey("consultas.id"), nullable=True)

    # Datos del audio
    archivo_audio = Column(String(500))  # Ruta o URL del archivo
    duracion_segundos = Column(Float)
    formato_audio = Column(String(50))  # mp3, wav, m4a, etc.

    # Transcripción
    texto_transcrito = Column(Text, nullable=False)
    idioma_detectado = Column(String(10))  # es, en, etc.
    confianza = Column(Float)  # 0-1

    # Metadatos
    modelo_utilizado = Column(String(100))  # whisper-1, etc.
    tiempo_procesamiento = Column(Float)  # segundos

    # Información extraída (opcional)
    informacion_extraida = Column(JSON)  # Entidades, síntomas, medicamentos, etc.

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    paciente = relationship("Paciente")
    medico = relationship("Usuario")


class ExtraccionInformacion(Base):
    """Extracción estructurada de información de notas médicas"""

    __tablename__ = "extracciones_informacion"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=True)
    medico_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    consulta_id = Column(UUID(as_uuid=True), ForeignKey("consultas.id"), nullable=True)
    transcripcion_id = Column(
        UUID(as_uuid=True), ForeignKey("transcripciones_voz.id"), nullable=True
    )

    # Texto fuente
    texto_original = Column(Text, nullable=False)
    tipo_documento = Column(
        String(100)
    )  # nota_evolucion, historia_clinica, receta, etc.

    # Información extraída
    sintomas = Column(JSON)  # Lista de síntomas identificados
    diagnosticos = Column(JSON)  # Diagnósticos mencionados
    medicamentos = Column(JSON)  # Medicamentos y dosis
    procedimientos = Column(JSON)  # Procedimientos realizados o sugeridos
    signos_vitales = Column(JSON)  # Presión, temperatura, etc.
    antecedentes = Column(JSON)  # Antecedentes mencionados
    alergias = Column(JSON)  # Alergias identificadas

    # Entidades nombradas
    entidades_medicas = Column(JSON)  # Todas las entidades médicas detectadas

    # Metadatos
    modelo_utilizado = Column(String(100))
    confianza_promedio = Column(Float)
    tiempo_procesamiento = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    paciente = relationship("Paciente")
    medico = relationship("Usuario")
    transcripcion = relationship("TranscripcionVoz")


class ResumenClinico(Base):
    """Resúmenes automáticos de historias clínicas"""

    __tablename__ = "resumenes_clinicos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    medico_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)

    # Configuración del resumen
    tipo_resumen = Column(String(100))  # completo, ejecutivo, por_sistema, cronologico
    periodo_inicio = Column(DateTime)
    periodo_fin = Column(DateTime)

    # Fuentes incluidas
    incluye_consultas = Column(Boolean, default=True)
    incluye_laboratorios = Column(Boolean, default=True)
    incluye_imagenes = Column(Boolean, default=True)
    incluye_medicamentos = Column(Boolean, default=True)

    # Resumen generado
    resumen_texto = Column(Text, nullable=False)
    resumen_estructurado = Column(JSON)  # Resumen en formato estructurado

    # Secciones del resumen
    datos_demograficos = Column(JSON)
    motivo_consulta_principal = Column(Text)
    antecedentes_relevantes = Column(JSON)
    evolucion_clinica = Column(Text)
    diagnosticos_actuales = Column(JSON)
    tratamiento_actual = Column(JSON)
    estudios_pendientes = Column(JSON)
    plan_seguimiento = Column(Text)

    # Metadatos
    numero_documentos_analizados = Column(Integer)
    modelo_utilizado = Column(String(100))
    tiempo_procesamiento = Column(Float)

    # Control de versiones
    version = Column(Integer, default=1)
    es_version_actual = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    paciente = relationship("Paciente")
    medico = relationship("Usuario")


class TraduccionMedica(Base):
    """Traducciones de terminología médica"""

    __tablename__ = "traducciones_medicas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    medico_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)

    # Texto original
    texto_original = Column(Text, nullable=False)
    idioma_origen = Column(String(10), nullable=False)  # es, en, fr, etc.

    # Traducción
    texto_traducido = Column(Text, nullable=False)
    idioma_destino = Column(String(10), nullable=False)

    # Tipo de traducción
    tipo_contenido = Column(
        String(100)
    )  # termino_medico, diagnostico, procedimiento, medicamento, texto_libre
    especialidad = Column(String(100))  # cardiologia, neurologia, etc.

    # Terminología médica identificada
    terminos_medicos_origen = Column(JSON)  # Términos en idioma original
    terminos_medicos_destino = Column(JSON)  # Términos traducidos

    # Alternativas y sinónimos
    traducciones_alternativas = Column(JSON)
    sinonimos = Column(JSON)

    # Contexto adicional
    definicion = Column(Text)  # Definición del término si aplica
    notas_clinicas = Column(Text)  # Notas adicionales sobre el uso

    # Metadatos
    modelo_utilizado = Column(String(100))
    confianza = Column(Float)
    tiempo_procesamiento = Column(Float)

    # Validación
    validado_por_medico = Column(Boolean, default=False)
    fecha_validacion = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    medico = relationship("Usuario")


class DiccionarioMedico(Base):
    """Diccionario de términos médicos multiidioma"""

    __tablename__ = "diccionario_medico"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Término principal
    termino_es = Column(String(500))  # Español
    termino_en = Column(String(500))  # Inglés
    termino_la = Column(String(500))  # Latín

    # Clasificación
    categoria = Column(
        String(100)
    )  # anatomia, patologia, farmacologia, procedimiento, etc.
    especialidad = Column(String(100))

    # Definiciones
    definicion_es = Column(Text)
    definicion_en = Column(Text)

    # Sinónimos
    sinonimos_es = Column(JSON)
    sinonimos_en = Column(JSON)

    # Abreviaturas
    abreviaturas = Column(JSON)

    # Códigos estándar
    codigo_cie10 = Column(String(20))
    codigo_snomed = Column(String(50))
    codigo_loinc = Column(String(50))

    # Uso clínico
    frecuencia_uso = Column(Integer, default=0)

    # Metadatos
    fuente = Column(String(200))  # OMS, RAE, etc.
    verificado = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
