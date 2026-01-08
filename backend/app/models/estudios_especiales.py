"""
Modelos para estudios especiales: EKG, EEG, Ecografías
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class EstudioEKG(Base):
    """Electrocardiograma - Estudio de actividad eléctrica del corazón"""
    __tablename__ = "estudios_ekg"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id", ondelete="CASCADE"), nullable=False, index=True)
    consulta_id = Column(UUID(as_uuid=True), ForeignKey("consultas.id"), nullable=True, index=True)
    medico_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    
    # Información del estudio
    fecha_estudio = Column(DateTime(timezone=True), nullable=False)
    motivo = Column(Text, nullable=True)
    indicacion_clinica = Column(Text, nullable=True)
    
    # Datos del paciente al momento del estudio
    edad_paciente = Column(Integer, nullable=True)
    peso_kg = Column(Float, nullable=True)
    altura_cm = Column(Float, nullable=True)
    presion_arterial = Column(String(20), nullable=True)  # Ej: "120/80"
    
    # Archivo del EKG (PDF, imagen, o datos digitales)
    archivo_id = Column(UUID(as_uuid=True), ForeignKey("imagenes_medicas.id"), nullable=True)
    ruta_archivo = Column(String(500), nullable=True)
    
    # Parámetros medidos
    frecuencia_cardiaca = Column(Integer, nullable=True)  # latidos por minuto
    intervalo_pr = Column(Integer, nullable=True)  # milisegundos
    duracion_qrs = Column(Integer, nullable=True)  # milisegundos
    intervalo_qt = Column(Integer, nullable=True)  # milisegundos
    intervalo_qtc = Column(Integer, nullable=True)  # QT corregido
    eje_qrs = Column(Integer, nullable=True)  # grados (-180 a +180)
    
    # Ritmo
    ritmo = Column(String(100), nullable=True)  # sinusal, fibrilacion_auricular, etc.
    ritmo_regular = Column(Boolean, nullable=True)
    
    # Ondas y segmentos
    onda_p = Column(String(200), nullable=True)  # descripción
    complejo_qrs = Column(String(200), nullable=True)
    segmento_st = Column(String(200), nullable=True)
    onda_t = Column(String(200), nullable=True)
    onda_u = Column(String(200), nullable=True)
    
    # Hallazgos
    hallazgos = Column(ARRAY(String), nullable=True)
    alteraciones = Column(JSONB, nullable=True)  # Array de alteraciones detectadas
    
    # Interpretación automática
    interpretacion_ia = Column(Text, nullable=True)
    confianza_ia = Column(Float, nullable=True)
    categorias_detectadas = Column(ARRAY(String), nullable=True)  # normal, isquemia, arritmia, etc.
    
    # Interpretación médica
    interpretacion_medica = Column(Text, nullable=True)
    diagnostico = Column(String(500), nullable=True)
    recomendaciones = Column(ARRAY(String), nullable=True)
    
    # Clasificación
    clasificacion = Column(String(50), nullable=True)  # normal, anormal_leve, anormal_moderado, anormal_severo
    requiere_atencion = Column(Boolean, default=False)
    es_critico = Column(Boolean, default=False)
    
    # Estado
    estado = Column(String(20), default='pendiente')  # pendiente, interpretado, revisado, aprobado
    revisado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    fecha_revision = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    paciente = relationship("Paciente", foreign_keys=[paciente_id])
    medico = relationship("Usuario", foreign_keys=[medico_id])


class EstudioEEG(Base):
    """Electroencefalograma - Estudio de actividad eléctrica cerebral"""
    __tablename__ = "estudios_eeg"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id", ondelete="CASCADE"), nullable=False, index=True)
    consulta_id = Column(UUID(as_uuid=True), ForeignKey("consultas.id"), nullable=True, index=True)
    medico_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    
    # Información del estudio
    fecha_estudio = Column(DateTime(timezone=True), nullable=False)
    motivo = Column(Text, nullable=True)
    indicacion_clinica = Column(Text, nullable=True)
    
    # Datos del paciente
    edad_paciente = Column(Integer, nullable=True)
    medicamentos_actuales = Column(Text, nullable=True)
    horas_ayuno = Column(Integer, nullable=True)
    horas_sueno_previo = Column(Integer, nullable=True)
    
    # Tipo de estudio
    tipo_estudio = Column(String(50), nullable=False)  # basal, sueno, vigilia, prolongado
    duracion_minutos = Column(Integer, nullable=True)
    
    # Condiciones del estudio
    estado_conciencia = Column(String(50), nullable=True)  # despierto, somnoliento, dormido
    cooperacion_paciente = Column(String(50), nullable=True)  # buena, regular, mala
    artefactos = Column(ARRAY(String), nullable=True)  # movimiento, parpadeo, muscular, etc.
    
    # Archivo del EEG
    archivo_id = Column(UUID(as_uuid=True), ForeignKey("imagenes_medicas.id"), nullable=True)
    ruta_archivo = Column(String(500), nullable=True)
    
    # Actividad de fondo
    actividad_fondo = Column(String(200), nullable=True)
    frecuencia_dominante = Column(Float, nullable=True)  # Hz
    amplitud_promedio = Column(Float, nullable=True)  # microvolts
    simetria = Column(String(50), nullable=True)  # simetrica, asimetrica
    reactividad = Column(String(50), nullable=True)  # presente, ausente, disminuida
    
    # Ritmos cerebrales
    ritmo_alfa = Column(String(200), nullable=True)  # 8-13 Hz
    ritmo_beta = Column(String(200), nullable=True)  # 13-30 Hz
    ritmo_theta = Column(String(200), nullable=True)  # 4-8 Hz
    ritmo_delta = Column(String(200), nullable=True)  # 0.5-4 Hz
    
    # Hallazgos anormales
    ondas_agudas = Column(Boolean, default=False)
    espigas = Column(Boolean, default=False)
    complejos_punta_onda = Column(Boolean, default=False)
    actividad_paroxistica = Column(Boolean, default=False)
    enlentecimiento = Column(String(100), nullable=True)  # focal, difuso, ausente
    
    # Localización de hallazgos
    localizacion_hallazgos = Column(ARRAY(String), nullable=True)  # frontal, temporal, parietal, occipital
    lateralidad = Column(String(20), nullable=True)  # izquierda, derecha, bilateral
    
    # Pruebas de activación
    fotoestimulacion = Column(String(200), nullable=True)
    hiperventilacion = Column(String(200), nullable=True)
    privacion_sueno = Column(String(200), nullable=True)
    
    # Hallazgos
    hallazgos = Column(ARRAY(String), nullable=True)
    alteraciones = Column(JSONB, nullable=True)
    
    # Interpretación automática
    interpretacion_ia = Column(Text, nullable=True)
    confianza_ia = Column(Float, nullable=True)
    categorias_detectadas = Column(ARRAY(String), nullable=True)  # normal, epileptiforme, focal, etc.
    
    # Interpretación médica
    interpretacion_medica = Column(Text, nullable=True)
    diagnostico = Column(String(500), nullable=True)
    recomendaciones = Column(ARRAY(String), nullable=True)
    
    # Clasificación
    clasificacion = Column(String(50), nullable=True)  # normal, anormal_leve, anormal_moderado, anormal_severo
    requiere_atencion = Column(Boolean, default=False)
    es_critico = Column(Boolean, default=False)
    
    # Estado
    estado = Column(String(20), default='pendiente')
    revisado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    fecha_revision = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    paciente = relationship("Paciente", foreign_keys=[paciente_id])
    medico = relationship("Usuario", foreign_keys=[medico_id])


class Ecografia(Base):
    """Estudios de ecografía/ultrasonido"""
    __tablename__ = "ecografias"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id", ondelete="CASCADE"), nullable=False, index=True)
    consulta_id = Column(UUID(as_uuid=True), ForeignKey("consultas.id"), nullable=True, index=True)
    medico_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    
    # Información del estudio
    fecha_estudio = Column(DateTime(timezone=True), nullable=False)
    motivo = Column(Text, nullable=True)
    indicacion_clinica = Column(Text, nullable=True)
    
    # Tipo de ecografía
    tipo_ecografia = Column(String(100), nullable=False)  # abdominal, pelvica, obstetrica, cardiaca, etc.
    region_anatomica = Column(String(100), nullable=False)
    via_acceso = Column(String(50), nullable=True)  # transabdominal, transvaginal, transrectal
    
    # Datos específicos obstétricos (si aplica)
    es_obstetrica = Column(Boolean, default=False)
    edad_gestacional_semanas = Column(Integer, nullable=True)
    numero_fetos = Column(Integer, nullable=True)
    
    # Equipo y técnica
    equipo_utilizado = Column(String(200), nullable=True)
    transductor = Column(String(100), nullable=True)
    modo = Column(String(50), nullable=True)  # B, M, Doppler, 3D, 4D
    
    # Archivo de imágenes
    archivo_id = Column(UUID(as_uuid=True), ForeignKey("imagenes_medicas.id"), nullable=True)
    ruta_archivo = Column(String(500), nullable=True)
    imagenes_adicionales = Column(ARRAY(String), nullable=True)  # Rutas de imágenes adicionales
    
    # Mediciones generales
    mediciones = Column(JSONB, nullable=True)  # Array de mediciones con nombre, valor, unidad
    
    # Hallazgos por órgano/región
    hallazgos_organos = Column(JSONB, nullable=True)  # {organo: descripcion}
    
    # Hallazgos específicos
    hallazgos = Column(ARRAY(String), nullable=True)
    masas_detectadas = Column(JSONB, nullable=True)  # Array de masas con ubicación, tamaño, características
    liquido_libre = Column(Boolean, default=False)
    cantidad_liquido = Column(String(50), nullable=True)  # escaso, moderado, abundante
    
    # Vascularización (Doppler)
    estudio_doppler = Column(Boolean, default=False)
    flujo_vascular = Column(String(200), nullable=True)
    resistencia_vascular = Column(String(200), nullable=True)
    
    # Interpretación automática
    interpretacion_ia = Column(Text, nullable=True)
    confianza_ia = Column(Float, nullable=True)
    categorias_detectadas = Column(ARRAY(String), nullable=True)
    estructuras_identificadas = Column(ARRAY(String), nullable=True)
    
    # Interpretación médica
    descripcion_tecnica = Column(Text, nullable=True)
    interpretacion_medica = Column(Text, nullable=True)
    impresion_diagnostica = Column(Text, nullable=True)
    diagnostico = Column(String(500), nullable=True)
    recomendaciones = Column(ARRAY(String), nullable=True)
    
    # Clasificación
    clasificacion = Column(String(50), nullable=True)  # normal, hallazgos_benignos, sospechoso, patologico
    birads = Column(String(10), nullable=True)  # Para ecografías mamarias (BI-RADS 0-6)
    requiere_atencion = Column(Boolean, default=False)
    requiere_seguimiento = Column(Boolean, default=False)
    
    # Calidad del estudio
    calidad_estudio = Column(String(50), nullable=True)  # excelente, buena, regular, limitada
    limitaciones = Column(Text, nullable=True)
    
    # Estado
    estado = Column(String(20), default='pendiente')
    revisado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    fecha_revision = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    paciente = relationship("Paciente", foreign_keys=[paciente_id])
    medico = relationship("Usuario", foreign_keys=[medico_id])
