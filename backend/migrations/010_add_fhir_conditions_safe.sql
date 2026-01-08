-- Migración: Agregar tabla de Condiciones/Diagnósticos FHIR (versión segura)
-- Fecha: 2024-12-21
-- Descripción: Tabla para almacenar recursos Condition HL7 FHIR R4 (diagnósticos importados)

-- Crear tipos ENUM para estados (solo si no existen)
DO $$ BEGIN
    CREATE TYPE condition_clinical_status AS ENUM (
        'active',
        'recurrence',
        'relapse',
        'inactive',
        'remission',
        'resolved'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE condition_verification_status AS ENUM (
        'unconfirmed',
        'provisional',
        'differential',
        'confirmed',
        'refuted',
        'entered-in-error'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Crear tabla de condiciones FHIR (solo si no existe)
CREATE TABLE IF NOT EXISTS fhir_conditions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identificadores externos (FHIR)
    identifier JSONB,
    fhir_id VARCHAR(255),
    fhir_server_url VARCHAR(500),
    
    -- Estado clínico y verificación
    clinical_status condition_clinical_status NOT NULL DEFAULT 'active',
    verification_status condition_verification_status NOT NULL DEFAULT 'confirmed',
    
    -- Categoría y severidad
    category JSONB,
    severity JSONB,
    
    -- Código de la condición (ICD-10, SNOMED CT, etc.)
    code JSONB NOT NULL,
    
    -- Sitio corporal afectado
    body_site JSONB,
    
    -- Paciente
    subject_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    
    -- Encuentro/Consulta relacionada
    encounter_id UUID REFERENCES consultas(id) ON DELETE SET NULL,
    
    -- Fechas de inicio (onset)
    onset_datetime TIMESTAMP,
    onset_age JSONB,
    onset_period JSONB,
    onset_range JSONB,
    onset_string VARCHAR(500),
    
    -- Fechas de resolución (abatement)
    abatement_datetime TIMESTAMP,
    abatement_age JSONB,
    abatement_period JSONB,
    abatement_range JSONB,
    abatement_string VARCHAR(500),
    
    -- Fecha de registro
    recorded_date TIMESTAMP,
    
    -- Quién registró y quién afirmó
    recorder_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    asserter_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    
    -- Etapa de la condición
    stage JSONB,
    
    -- Evidencia
    evidence JSONB,
    
    -- Notas
    note JSONB,
    
    -- Metadatos de origen
    source_system VARCHAR(255),
    source_record_id VARCHAR(255),
    
    -- Recurso FHIR completo
    fhir_resource JSONB,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices (solo si no existen)
CREATE INDEX IF NOT EXISTS idx_fhir_conditions_subject ON fhir_conditions(subject_id);
CREATE INDEX IF NOT EXISTS idx_fhir_conditions_encounter ON fhir_conditions(encounter_id);
CREATE INDEX IF NOT EXISTS idx_fhir_conditions_fhir_id ON fhir_conditions(fhir_id);
CREATE INDEX IF NOT EXISTS idx_fhir_conditions_clinical_status ON fhir_conditions(clinical_status);
CREATE INDEX IF NOT EXISTS idx_fhir_conditions_verification_status ON fhir_conditions(verification_status);
CREATE INDEX IF NOT EXISTS idx_fhir_conditions_recorded_date ON fhir_conditions(recorded_date DESC);
CREATE INDEX IF NOT EXISTS idx_fhir_conditions_code ON fhir_conditions USING GIN (code);
CREATE INDEX IF NOT EXISTS idx_fhir_conditions_category ON fhir_conditions USING GIN (category);

-- Crear trigger para actualizar updated_at (solo si no existe)
DO $$ BEGIN
    CREATE TRIGGER update_fhir_conditions_updated_at
        BEFORE UPDATE ON fhir_conditions
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Comentarios
COMMENT ON TABLE fhir_conditions IS 'Recursos Condition HL7 FHIR R4 - Diagnósticos y condiciones clínicas importadas';
COMMENT ON COLUMN fhir_conditions.fhir_id IS 'ID del recurso en el servidor FHIR externo';
COMMENT ON COLUMN fhir_conditions.fhir_server_url IS 'URL del servidor FHIR de origen';
COMMENT ON COLUMN fhir_conditions.clinical_status IS 'Estado clínico: active, resolved, etc.';
COMMENT ON COLUMN fhir_conditions.verification_status IS 'Estado de verificación: confirmed, provisional, etc.';
COMMENT ON COLUMN fhir_conditions.code IS 'Código de la condición (CodeableConcept) - ICD-10, SNOMED CT';
COMMENT ON COLUMN fhir_conditions.source_system IS 'Sistema de origen: FHIR, HL7 v2, interno';
COMMENT ON COLUMN fhir_conditions.fhir_resource IS 'Recurso FHIR completo en formato JSON';

-- Mensaje de éxito
DO $$ BEGIN
    RAISE NOTICE '✅ Migración completada: Tabla fhir_conditions creada/verificada correctamente';
END $$;
