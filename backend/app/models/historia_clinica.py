from sqlalchemy import Column, String, Date, DateTime, Integer, Float, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class HistoriaClinicaPediatrica(Base):
    """
    Historia Clínica Pediátrica basada en formato IMSS
    """
    __tablename__ = "historias_clinicas"

    # Identificadores
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    fecha = Column(Date, nullable=False, server_default=func.now())
    numero_afiliacion = Column(String(50))
    
    # Servicio de atención médica (IMSS, ISSSTE, Particular, etc.)
    servicio_atencion_medica = Column(String(200))  # Referencia a instituciones_salud
    
    # Datos básicos del paciente (además de los ya en Paciente)
    informante_parentesco = Column(String(100))
    informante_edad = Column(Integer)
    escolaridad_paciente = Column(String(100))
    
    # PADECIMIENTO ACTUAL
    padecimiento_actual = Column(Text)  # Descripción cronológica de síntomas
    diagnosticos_previos = Column(Text)
    examenes_previos = Column(Text)  # Descripción textual
    examenes_previos_realizados = Column(JSONB)  # Checkboxes: {"biometria_hematica": true, "quimica_sanguinea": true, ...}
    terapeutica_previa = Column(Text)
    
    # ANTECEDENTES FAMILIARES - Madre
    madre_vive = Column(Boolean, default=True)
    madre_edad = Column(Integer)
    madre_escolaridad = Column(String(100))
    madre_ocupacion = Column(String(100))
    madre_gesta = Column(Integer)
    madre_parto = Column(Integer)
    madre_abortos = Column(Integer)
    madre_cesareas = Column(Integer)
    madre_toxicomanias = Column(String(200))
    madre_toxicomanias_especifique = Column(Text)
    
    # ANTECEDENTES FAMILIARES - Padre
    padre_vive = Column(Boolean, default=True)
    padre_edad = Column(Integer)
    padre_escolaridad = Column(String(100))
    padre_ocupacion = Column(String(100))
    padre_toxicomanias = Column(String(200))
    padre_toxicomanias_especifique = Column(Text)
    
    # ANTECEDENTES FAMILIARES - Hermanos
    hermanos_numero = Column(Integer)
    hermanos_vivos = Column(Integer)
    hermanos_muertos = Column(Integer)
    hermanos_muertos_causa = Column(Text)
    hermanos_edades = Column(String(200))
    
    # Padecimientos Heredofamiliares
    heredofam_diabeticos = Column(String(100))
    heredofam_hipertension = Column(String(100))
    heredofam_neurologicos = Column(String(100))
    heredofam_cardiopatas = Column(String(100))
    heredofam_hematologicos = Column(String(100))
    heredofam_nefropatias = Column(String(100))
    heredofam_oncologicos = Column(String(100))
    heredofam_malformaciones = Column(String(100))
    heredofam_alergicos = Column(String(100))
    heredofam_especificar = Column(Text)
    
    # Contacto con enfermedades infecciosas
    contacto_enfermedades_infecciosas = Column(Text)
    
    # ANTECEDENTES PERSONALES PERINATALES
    embarazo_numero = Column(Integer)
    embarazo_curso_normal = Column(Boolean)
    embarazo_causa = Column(Text)
    gestacion_semanas = Column(Integer)
    sitio_atencion_parto = Column(String(200))
    parto_eutocico = Column(Boolean)
    parto_causa = Column(Text)
    
    # Medidas al nacer
    peso_nacimiento = Column(Float)
    talla_nacimiento = Column(Float)
    ruptura_membranas_horas = Column(Float)
    
    # Complicaciones perinatales
    anestesia = Column(String(100))
    anestesia_cual = Column(Text)
    apnea_neonatal = Column(Boolean, default=False)
    convulsiones_neonatales = Column(Boolean, default=False)
    hemorragias_neonatales = Column(Boolean, default=False)
    ictericia_neonatal = Column(Boolean, default=False)
    cianosis_neonatal = Column(Boolean, default=False)
    otros_perinatales = Column(Text)
    informacion_adicional_perinatal = Column(Text)
    
    # VIVIENDA
    num_cuartos_casa = Column(Integer)
    num_personas_duermen_casa = Column(Integer)
    tiene_refrigerador = Column(Boolean, default=False)
    tiene_telefono = Column(Boolean, default=False)
    tiene_automovil = Column(Boolean, default=False)
    
    # Exposición a sustancias tóxicas
    exposicion_sustancias_toxicas = Column(Text)  # Descripción textual
    sustancias_toxicas_checkboxes = Column(JSONB)  # Checkboxes: {"tabaco": true, "cannabis": true, ...}
    
    # PERSONALES PATOLÓGICOS
    personales_patologicos = Column(Text)  # Lista de todas las enfermedades
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    paciente = relationship("Paciente", backref="historias_clinicas")
    exploracion_fisica = relationship("ExploracionFisica", back_populates="historia_clinica", uselist=False)
    antecedentes_no_patologicos = relationship("AntecedentesNoPatologicos", back_populates="historia_clinica", uselist=False)


class ExploracionFisica(Base):
    """
    Exploración Física detallada
    """
    __tablename__ = "exploracion_fisica"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    historia_clinica_id = Column(UUID(as_uuid=True), ForeignKey("historias_clinicas.id"), nullable=False)
    
    # Signos vitales y medidas
    peso = Column(Float)
    talla = Column(Float)
    perimetro_cefalico = Column(Float)
    perimetro_braquial = Column(Float)
    perimetro_pierna = Column(Float)
    segmento_superior = Column(Float)
    segmento_inferior = Column(Float)
    frecuencia_cardiaca = Column(Integer)
    frecuencia_respiratoria = Column(Integer)
    temperatura = Column(Float)
    tension_arterial = Column(String(20))
    
    # Aspecto General
    piel_faneras = Column(Text)
    cabeza = Column(Text)
    ojos = Column(Text)
    oidos = Column(Text)
    boca_faringe = Column(Text)
    cuello = Column(Text)
    torax_ap_respiratorio = Column(Text)
    torax_ap_cardiovascular = Column(Text)
    tanner_mamario = Column(String(10))
    abdomen = Column(Text)
    extremidades = Column(Text)
    genitales = Column(Text)
    tanner_genital = Column(String(10))
    ano_recto = Column(Text)
    tanner_pubico = Column(String(10))
    vasos_perifericos = Column(Text)
    neurologico = Column(Text)
    columna_vertebral = Column(Text)
    
    # Médicos
    medico_realizo_nombre = Column(String(255))
    medico_realizo_firma = Column(String(255))
    medico_reviso_nombre = Column(String(255))
    medico_reviso_firma = Column(String(255))
    
    fecha_exploracion = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relación
    historia_clinica = relationship("HistoriaClinicaPediatrica", back_populates="exploracion_fisica")


class AntecedentesNoPatologicos(Base):
    """
    Antecedentes No Patológicos (Alimentación, Vacunación, Desarrollo)
    """
    __tablename__ = "antecedentes_no_patologicos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    historia_clinica_id = Column(UUID(as_uuid=True), ForeignKey("historias_clinicas.id"), nullable=False)
    
    # ALIMENTACIÓN
    pecho_materno_duracion_meses = Column(Integer)
    ablactacion_meses = Column(Integer)
    destete_meses = Column(Integer)
    alimentacion_actual = Column(JSONB)  # {carne: dias/semana, leche: dias/semana, etc}
    
    # INMUNIZACIONES (JSONB con esquema completo)
    inmunizaciones = Column(JSONB)  # Estructura: {vacuna: [{dosis: 1, edad_meses: 0, fecha: "2024-01-01"}]}
    
    # DESARROLLO PSICOMOTOR
    desarrollo_siguio_objetos_meses = Column(Integer)
    desarrollo_sonrio_meses = Column(Integer)
    desarrollo_sostuvo_cabeza_meses = Column(Integer)
    desarrollo_se_sento_meses = Column(Integer)
    desarrollo_camino_meses = Column(Integer)
    desarrollo_control_esfinteres_vesical_meses = Column(Integer)
    desarrollo_control_esfinteres_anal_meses = Column(Integer)
    escolaridad_actual = Column(String(100))
    años_escolares_reprobados = Column(Integer)
    datos_anormales_desarrollo = Column(Text)
    
    # DESARROLLO PUBERAL
    inicio_telarca_edad = Column(Integer)
    inicio_pubarca_edad = Column(Integer)
    inicio_adrenarca_edad = Column(Integer)
    edad_espermarquia = Column(Integer)
    ciclos_menstruales_frecuencia_dias = Column(Integer)
    ciclos_menstruales_duracion_dias = Column(Integer)
    ciclos_menstruales_cantidad = Column(String(50))
    dismenorrea = Column(Boolean, default=False)
    
    # HABITACIÓN
    eliminacion_excretas_fecalismo = Column(Boolean, default=False)
    eliminacion_excretas_letrina = Column(Boolean, default=False)
    eliminacion_excretas_tipo_ingles = Column(Boolean, default=False)
    agua_intradomiciliaria = Column(Boolean, default=False)
    baño_familiar = Column(Boolean, default=False)
    baño_comunal = Column(Boolean, default=False)
    convivencia_animales = Column(Text)
    piso_casa_tierra = Column(Boolean, default=False)
    piso_casa_cemento = Column(Boolean, default=False)
    piso_casa_recubrimiento = Column(String(100))
    
    # Relación
    historia_clinica = relationship("HistoriaClinicaPediatrica", back_populates="antecedentes_no_patologicos")
