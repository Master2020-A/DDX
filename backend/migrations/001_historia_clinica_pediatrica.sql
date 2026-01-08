-- ============================================================================
-- Migración: Historia Clínica Pediátrica
-- Descripción: Tablas para historia clínica pediátrica completa basada en formato IMSS
-- ============================================================================

-- Tabla principal: Historias Clínicas
CREATE TABLE IF NOT EXISTS historias_clinicas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    numero_afiliacion VARCHAR(50),
    
    -- Datos básicos
    informante_parentesco VARCHAR(100),
    informante_edad INTEGER,
    escolaridad_paciente VARCHAR(100),
    
    -- Padecimiento Actual
    padecimiento_actual TEXT,
    diagnosticos_previos TEXT,
    examenes_previos TEXT,
    terapeutica_previa TEXT,
    
    -- Antecedentes Familiares - Madre
    madre_vive BOOLEAN DEFAULT TRUE,
    madre_edad INTEGER,
    madre_escolaridad VARCHAR(100),
    madre_ocupacion VARCHAR(100),
    madre_gesta INTEGER,
    madre_parto INTEGER,
    madre_abortos INTEGER,
    madre_cesareas INTEGER,
    madre_toxicomanias VARCHAR(200),
    madre_toxicomanias_especifique TEXT,
    
    -- Antecedentes Familiares - Padre
    padre_vive BOOLEAN DEFAULT TRUE,
    padre_edad INTEGER,
    padre_escolaridad VARCHAR(100),
    padre_ocupacion VARCHAR(100),
    padre_toxicomanias VARCHAR(200),
    padre_toxicomanias_especifique TEXT,
    
    -- Hermanos
    hermanos_numero INTEGER,
    hermanos_vivos INTEGER,
    hermanos_muertos INTEGER,
    hermanos_muertos_causa TEXT,
    hermanos_edades VARCHAR(200),
    
    -- Padecimientos Heredofamiliares
    heredofam_diabeticos VARCHAR(100),
    heredofam_hipertension VARCHAR(100),
    heredofam_neurologicos VARCHAR(100),
    heredofam_cardiopatas VARCHAR(100),
    heredofam_hematologicos VARCHAR(100),
    heredofam_nefropatias VARCHAR(100),
    heredofam_oncologicos VARCHAR(100),
    heredofam_malformaciones VARCHAR(100),
    heredofam_alergicos VARCHAR(100),
    heredofam_especificar TEXT,
    contacto_enfermedades_infecciosas TEXT,
    
    -- Antecedentes Perinatales
    embarazo_numero INTEGER,
    embarazo_curso_normal BOOLEAN,
    embarazo_causa TEXT,
    gestacion_semanas INTEGER,
    sitio_atencion_parto VARCHAR(200),
    parto_eutocico BOOLEAN,
    parto_causa TEXT,
    peso_nacimiento FLOAT,
    talla_nacimiento FLOAT,
    ruptura_membranas_horas FLOAT,
    anestesia VARCHAR(100),
    anestesia_cual TEXT,
    apnea_neonatal BOOLEAN DEFAULT FALSE,
    convulsiones_neonatales BOOLEAN DEFAULT FALSE,
    hemorragias_neonatales BOOLEAN DEFAULT FALSE,
    ictericia_neonatal BOOLEAN DEFAULT FALSE,
    cianosis_neonatal BOOLEAN DEFAULT FALSE,
    otros_perinatales TEXT,
    informacion_adicional_perinatal TEXT,
    
    -- Vivienda
    num_cuartos_casa INTEGER,
    num_personas_duermen_casa INTEGER,
    tiene_refrigerador BOOLEAN DEFAULT FALSE,
    tiene_telefono BOOLEAN DEFAULT FALSE,
    tiene_automovil BOOLEAN DEFAULT FALSE,
    exposicion_sustancias_toxicas TEXT,
    
    -- Personales Patológicos
    personales_patologicos TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Exploración Física
CREATE TABLE IF NOT EXISTS exploracion_fisica (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    historia_clinica_id UUID NOT NULL REFERENCES historias_clinicas(id) ON DELETE CASCADE,
    
    -- Signos vitales y medidas
    peso FLOAT,
    talla FLOAT,
    perimetro_cefalico FLOAT,
    perimetro_braquial FLOAT,
    perimetro_pierna FLOAT,
    segmento_superior FLOAT,
    segmento_inferior FLOAT,
    frecuencia_cardiaca INTEGER,
    frecuencia_respiratoria INTEGER,
    temperatura FLOAT,
    tension_arterial VARCHAR(20),
    
    -- Aspecto General
    piel_faneras TEXT,
    cabeza TEXT,
    ojos TEXT,
    oidos TEXT,
    boca_faringe TEXT,
    cuello TEXT,
    torax_ap_respiratorio TEXT,
    torax_ap_cardiovascular TEXT,
    tanner_mamario VARCHAR(10),
    abdomen TEXT,
    extremidades TEXT,
    genitales TEXT,
    tanner_genital VARCHAR(10),
    ano_recto TEXT,
    tanner_pubico VARCHAR(10),
    vasos_perifericos TEXT,
    neurologico TEXT,
    columna_vertebral TEXT,
    
    -- Médicos
    medico_realizo_nombre VARCHAR(255),
    medico_realizo_firma VARCHAR(255),
    medico_reviso_nombre VARCHAR(255),
    medico_reviso_firma VARCHAR(255),
    
    fecha_exploracion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_exploracion_historia UNIQUE(historia_clinica_id)
);

-- Tabla: Antecedentes No Patológicos
CREATE TABLE IF NOT EXISTS antecedentes_no_patologicos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    historia_clinica_id UUID NOT NULL REFERENCES historias_clinicas(id) ON DELETE CASCADE,
    
    -- Alimentación
    pecho_materno_duracion_meses INTEGER,
    ablactacion_meses INTEGER,
    destete_meses INTEGER,
    alimentacion_actual JSONB,
    
    -- Inmunizaciones
    inmunizaciones JSONB,
    
    -- Desarrollo Psicomotor
    desarrollo_siguio_objetos_meses INTEGER,
    desarrollo_sonrio_meses INTEGER,
    desarrollo_sostuvo_cabeza_meses INTEGER,
    desarrollo_se_sento_meses INTEGER,
    desarrollo_camino_meses INTEGER,
    desarrollo_control_esfinteres_vesical_meses INTEGER,
    desarrollo_control_esfinteres_anal_meses INTEGER,
    escolaridad_actual VARCHAR(100),
    años_escolares_reprobados INTEGER,
    datos_anormales_desarrollo TEXT,
    
    -- Desarrollo Puberal
    inicio_telarca_edad INTEGER,
    inicio_pubarca_edad INTEGER,
    inicio_adrenarca_edad INTEGER,
    edad_espermarquia INTEGER,
    ciclos_menstruales_frecuencia_dias INTEGER,
    ciclos_menstruales_duracion_dias INTEGER,
    ciclos_menstruales_cantidad VARCHAR(50),
    dismenorrea BOOLEAN DEFAULT FALSE,
    
    -- Habitación
    eliminacion_excretas_fecalismo BOOLEAN DEFAULT FALSE,
    eliminacion_excretas_letrina BOOLEAN DEFAULT FALSE,
    eliminacion_excretas_tipo_ingles BOOLEAN DEFAULT FALSE,
    agua_intradomiciliaria BOOLEAN DEFAULT FALSE,
    baño_familiar BOOLEAN DEFAULT FALSE,
    baño_comunal BOOLEAN DEFAULT FALSE,
    convivencia_animales TEXT,
    piso_casa_tierra BOOLEAN DEFAULT FALSE,
    piso_casa_cemento BOOLEAN DEFAULT FALSE,
    piso_casa_recubrimiento VARCHAR(100),
    
    CONSTRAINT fk_antecedentes_historia UNIQUE(historia_clinica_id)
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_historias_clinicas_paciente ON historias_clinicas(paciente_id);
CREATE INDEX IF NOT EXISTS idx_historias_clinicas_fecha ON historias_clinicas(fecha DESC);
CREATE INDEX IF NOT EXISTS idx_exploracion_fisica_historia ON exploracion_fisica(historia_clinica_id);
CREATE INDEX IF NOT EXISTS idx_antecedentes_historia ON antecedentes_no_patologicos(historia_clinica_id);

-- Trigger para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_historias_clinicas_updated_at 
    BEFORE UPDATE ON historias_clinicas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comentarios en las tablas
COMMENT ON TABLE historias_clinicas IS 'Historia Clínica Pediátrica completa basada en formato IMSS';
COMMENT ON TABLE exploracion_fisica IS 'Exploración física detallada del paciente';
COMMENT ON TABLE antecedentes_no_patologicos IS 'Antecedentes no patológicos: alimentación, vacunación, desarrollo';
