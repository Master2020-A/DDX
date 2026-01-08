from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import date, datetime
from uuid import UUID


# ============================================================================
# HISTORIA CLÍNICA PEDIÁTRICA
# ============================================================================

class HistoriaClinicaBase(BaseModel):
    """Base schema para Historia Clínica Pediátrica"""
    numero_afiliacion: Optional[str] = None
    informante_parentesco: Optional[str] = None
    informante_edad: Optional[int] = None
    escolaridad_paciente: Optional[str] = None
    
    # Padecimiento Actual
    padecimiento_actual: Optional[str] = None
    diagnosticos_previos: Optional[str] = None
    examenes_previos: Optional[str] = None
    terapeutica_previa: Optional[str] = None
    
    # Antecedentes Familiares - Madre
    madre_vive: Optional[bool] = True
    madre_edad: Optional[int] = None
    madre_escolaridad: Optional[str] = None
    madre_ocupacion: Optional[str] = None
    madre_gesta: Optional[int] = None
    madre_parto: Optional[int] = None
    madre_abortos: Optional[int] = None
    madre_cesareas: Optional[int] = None
    madre_toxicomanias: Optional[str] = None
    madre_toxicomanias_especifique: Optional[str] = None
    
    # Antecedentes Familiares - Padre
    padre_vive: Optional[bool] = True
    padre_edad: Optional[int] = None
    padre_escolaridad: Optional[str] = None
    padre_ocupacion: Optional[str] = None
    padre_toxicomanias: Optional[str] = None
    padre_toxicomanias_especifique: Optional[str] = None
    
    # Hermanos
    hermanos_numero: Optional[int] = None
    hermanos_vivos: Optional[int] = None
    hermanos_muertos: Optional[int] = None
    hermanos_muertos_causa: Optional[str] = None
    hermanos_edades: Optional[str] = None
    
    # Padecimientos Heredofamiliares
    heredofam_diabeticos: Optional[str] = None
    heredofam_hipertension: Optional[str] = None
    heredofam_neurologicos: Optional[str] = None
    heredofam_cardiopatas: Optional[str] = None
    heredofam_hematologicos: Optional[str] = None
    heredofam_nefropatias: Optional[str] = None
    heredofam_oncologicos: Optional[str] = None
    heredofam_malformaciones: Optional[str] = None
    heredofam_alergicos: Optional[str] = None
    heredofam_especificar: Optional[str] = None
    
    contacto_enfermedades_infecciosas: Optional[str] = None
    
    # Antecedentes Perinatales
    embarazo_numero: Optional[int] = None
    embarazo_curso_normal: Optional[bool] = None
    embarazo_causa: Optional[str] = None
    gestacion_semanas: Optional[int] = None
    sitio_atencion_parto: Optional[str] = None
    parto_eutocico: Optional[bool] = None
    parto_causa: Optional[str] = None
    peso_nacimiento: Optional[float] = None
    talla_nacimiento: Optional[float] = None
    ruptura_membranas_horas: Optional[float] = None
    anestesia: Optional[str] = None
    anestesia_cual: Optional[str] = None
    apnea_neonatal: Optional[bool] = False
    convulsiones_neonatales: Optional[bool] = False
    hemorragias_neonatales: Optional[bool] = False
    ictericia_neonatal: Optional[bool] = False
    cianosis_neonatal: Optional[bool] = False
    otros_perinatales: Optional[str] = None
    informacion_adicional_perinatal: Optional[str] = None
    
    # Vivienda
    num_cuartos_casa: Optional[int] = None
    num_personas_duermen_casa: Optional[int] = None
    tiene_refrigerador: Optional[bool] = False
    tiene_telefono: Optional[bool] = False
    tiene_automovil: Optional[bool] = False
    exposicion_sustancias_toxicas: Optional[str] = None
    
    # Personales Patológicos
    personales_patologicos: Optional[str] = None


class HistoriaClinicaCreate(HistoriaClinicaBase):
    """Schema para crear Historia Clínica"""
    paciente_id: UUID
    fecha: Optional[date] = None


class HistoriaClinicaUpdate(HistoriaClinicaBase):
    """Schema para actualizar Historia Clínica"""
    pass


class HistoriaClinicaResponse(HistoriaClinicaBase):
    """Schema para respuesta de Historia Clínica"""
    id: UUID
    paciente_id: UUID
    fecha: date
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# EXPLORACIÓN FÍSICA
# ============================================================================

class ExploracionFisicaBase(BaseModel):
    """Base schema para Exploración Física"""
    peso: Optional[float] = None
    talla: Optional[float] = None
    perimetro_cefalico: Optional[float] = None
    perimetro_braquial: Optional[float] = None
    perimetro_pierna: Optional[float] = None
    segmento_superior: Optional[float] = None
    segmento_inferior: Optional[float] = None
    frecuencia_cardiaca: Optional[int] = None
    frecuencia_respiratoria: Optional[int] = None
    temperatura: Optional[float] = None
    tension_arterial: Optional[str] = None
    
    # Aspecto General
    piel_faneras: Optional[str] = None
    cabeza: Optional[str] = None
    ojos: Optional[str] = None
    oidos: Optional[str] = None
    boca_faringe: Optional[str] = None
    cuello: Optional[str] = None
    torax_ap_respiratorio: Optional[str] = None
    torax_ap_cardiovascular: Optional[str] = None
    tanner_mamario: Optional[str] = None
    abdomen: Optional[str] = None
    extremidades: Optional[str] = None
    genitales: Optional[str] = None
    tanner_genital: Optional[str] = None
    ano_recto: Optional[str] = None
    tanner_pubico: Optional[str] = None
    vasos_perifericos: Optional[str] = None
    neurologico: Optional[str] = None
    columna_vertebral: Optional[str] = None
    
    # Médicos
    medico_realizo_nombre: Optional[str] = None
    medico_realizo_firma: Optional[str] = None
    medico_reviso_nombre: Optional[str] = None
    medico_reviso_firma: Optional[str] = None


class ExploracionFisicaCreate(ExploracionFisicaBase):
    """Schema para crear Exploración Física"""
    historia_clinica_id: UUID


class ExploracionFisicaUpdate(ExploracionFisicaBase):
    """Schema para actualizar Exploración Física"""
    pass


class ExploracionFisicaResponse(ExploracionFisicaBase):
    """Schema para respuesta de Exploración Física"""
    id: UUID
    historia_clinica_id: UUID
    fecha_exploracion: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# ANTECEDENTES NO PATOLÓGICOS
# ============================================================================

class AntecedentesNoPatologicosBase(BaseModel):
    """Base schema para Antecedentes No Patológicos"""
    # Alimentación
    pecho_materno_duracion_meses: Optional[int] = None
    ablactacion_meses: Optional[int] = None
    destete_meses: Optional[int] = None
    alimentacion_actual: Optional[Dict[str, int]] = None  # {carne: 3, leche: 7, etc}
    
    # Inmunizaciones
    inmunizaciones: Optional[Dict[str, List[Dict]]] = None  # {BCG: [{dosis: 1, fecha: "2024-01-01"}]}
    
    # Desarrollo Psicomotor
    desarrollo_siguio_objetos_meses: Optional[int] = None
    desarrollo_sonrio_meses: Optional[int] = None
    desarrollo_sostuvo_cabeza_meses: Optional[int] = None
    desarrollo_se_sento_meses: Optional[int] = None
    desarrollo_camino_meses: Optional[int] = None
    desarrollo_control_esfinteres_vesical_meses: Optional[int] = None
    desarrollo_control_esfinteres_anal_meses: Optional[int] = None
    escolaridad_actual: Optional[str] = None
    años_escolares_reprobados: Optional[int] = None
    datos_anormales_desarrollo: Optional[str] = None
    
    # Desarrollo Puberal
    inicio_telarca_edad: Optional[int] = None
    inicio_pubarca_edad: Optional[int] = None
    inicio_adrenarca_edad: Optional[int] = None
    edad_espermarquia: Optional[int] = None
    ciclos_menstruales_frecuencia_dias: Optional[int] = None
    ciclos_menstruales_duracion_dias: Optional[int] = None
    ciclos_menstruales_cantidad: Optional[str] = None
    dismenorrea: Optional[bool] = False
    
    # Habitación
    eliminacion_excretas_fecalismo: Optional[bool] = False
    eliminacion_excretas_letrina: Optional[bool] = False
    eliminacion_excretas_tipo_ingles: Optional[bool] = False
    agua_intradomiciliaria: Optional[bool] = False
    baño_familiar: Optional[bool] = False
    baño_comunal: Optional[bool] = False
    convivencia_animales: Optional[str] = None
    piso_casa_tierra: Optional[bool] = False
    piso_casa_cemento: Optional[bool] = False
    piso_casa_recubrimiento: Optional[str] = None


class AntecedentesNoPatologicosCreate(AntecedentesNoPatologicosBase):
    """Schema para crear Antecedentes No Patológicos"""
    historia_clinica_id: UUID


class AntecedentesNoPatologicosUpdate(AntecedentesNoPatologicosBase):
    """Schema para actualizar Antecedentes No Patológicos"""
    pass


class AntecedentesNoPatologicosResponse(AntecedentesNoPatologicosBase):
    """Schema para respuesta de Antecedentes No Patológicos"""
    id: UUID
    historia_clinica_id: UUID
    
    class Config:
        from_attributes = True


# ============================================================================
# SCHEMA COMPLETO CON TODAS LAS SECCIONES
# ============================================================================

class HistoriaClinicaCompletaResponse(HistoriaClinicaResponse):
    """Schema completo con todas las secciones de la Historia Clínica"""
    exploracion_fisica: Optional[ExploracionFisicaResponse] = None
    antecedentes_no_patologicos: Optional[AntecedentesNoPatologicosResponse] = None
    
    class Config:
        from_attributes = True
