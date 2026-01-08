-- Migración: Agregar tabla de Observaciones FHIR
-- Fecha: 2024-12-21
-- Descripción: Tabla para almacenar recursos Observation HL7 FHIR R4

-- Crear tipo ENUM para estado de observación
CREATE TYPE observation_status AS ENUM (
    'registered',
    'preliminary',
    'final',
    'amended',
    'corrected',
    'cancelled',
    'entered-in-error',
    'unknown'
);

-- Crear tabla de observaciones FHIR
CREATE TABLE fhir_observations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identificadores
    identifier JSONB,
    
    -- Estado y categoría
    status observation_status NOT NULL DEFAULT 'final',
    category TEXT[],
    
    -- Código de la observación (LOINC, SNOMED, etc)
    code JSONB NOT NULL,
    
    -- Referencias
    subject_type VARCHAR(50) NOT NULL DEFAULT 'Patient',
    subject_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    encounter_id UUID REFERENCES consultas(id) ON DELETE SET NULL,
    
    -- Tiempo
    effective_datetime TIMESTAMP,
    effective_period_start TIMESTAMP,
    effective_period_end TIMESTAMP,
    issued TIMESTAMP,
    
    -- Performer (quien realizó la observación)
    performer JSONB,
    
    -- Valores de la observación (solo uno debe estar presente)
    value_quantity JSONB,
    value_codeable_concept JSONB,
    value_string TEXT,
    value_boolean BOOLEAN,
    value_integer INTEGER,
    value_range JSONB,
    value_ratio JSONB,
    value_sampled_data JSONB,
    value_time VARCHAR(20),
    value_datetime TIMESTAMP,
    value_period JSONB,
    
    -- Interpretación
    interpretation JSONB,
    
    -- Notas
    note JSONB,
    
    -- Método
    method JSONB,
    
    -- Sitio corporal
    body_site JSONB,
    
    -- Rango de referencia
    reference_range JSONB,
    
    -- Componentes (para observaciones multi-componente)
    component JSONB,
    
    -- Datos derivados
    derived_from JSONB,
    
    -- Metadatos FHIR
    meta JSONB,
    
    -- Datos originales (para trazabilidad)
    source_type VARCHAR(50),
    source_id UUID,
    
    -- Auditoría
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    
    -- Constraints
    CONSTRAINT chk_effective_time CHECK (
        effective_datetime IS NOT NULL OR 
        (effective_period_start IS NOT NULL OR effective_period_end IS NOT NULL)
    ),
    CONSTRAINT chk_single_value CHECK (
        (value_quantity IS NOT NULL)::int +
        (value_codeable_concept IS NOT NULL)::int +
        (value_string IS NOT NULL)::int +
        (value_boolean IS NOT NULL)::int +
        (value_integer IS NOT NULL)::int +
        (value_range IS NOT NULL)::int +
        (value_ratio IS NOT NULL)::int +
        (value_sampled_data IS NOT NULL)::int +
        (value_time IS NOT NULL)::int +
        (value_datetime IS NOT NULL)::int +
        (value_period IS NOT NULL)::int +
        (component IS NOT NULL)::int <= 1
    )
);

-- Índices para mejorar rendimiento
CREATE INDEX idx_fhir_obs_subject ON fhir_observations(subject_id);
CREATE INDEX idx_fhir_obs_encounter ON fhir_observations(encounter_id);
CREATE INDEX idx_fhir_obs_status ON fhir_observations(status);
CREATE INDEX idx_fhir_obs_category ON fhir_observations USING GIN(category);
CREATE INDEX idx_fhir_obs_effective_datetime ON fhir_observations(effective_datetime DESC);
CREATE INDEX idx_fhir_obs_source ON fhir_observations(source_type, source_id);
CREATE INDEX idx_fhir_obs_created_at ON fhir_observations(created_at DESC);

-- Índice GIN para búsqueda en código JSONB
CREATE INDEX idx_fhir_obs_code ON fhir_observations USING GIN(code);

-- Índice para búsqueda de códigos específicos
CREATE INDEX idx_fhir_obs_code_coding ON fhir_observations USING GIN(code jsonb_path_ops);

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_fhir_observation_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para actualizar updated_at
CREATE TRIGGER trg_fhir_observation_updated_at
    BEFORE UPDATE ON fhir_observations
    FOR EACH ROW
    EXECUTE FUNCTION update_fhir_observation_updated_at();

-- Comentarios en la tabla
COMMENT ON TABLE fhir_observations IS 'Recursos Observation HL7 FHIR R4 - Mediciones y observaciones clínicas';
COMMENT ON COLUMN fhir_observations.code IS 'Código de la observación (LOINC, SNOMED CT, etc)';
COMMENT ON COLUMN fhir_observations.category IS 'Categorías: vital-signs, laboratory, imaging, procedure, survey, exam, therapy, activity';
COMMENT ON COLUMN fhir_observations.status IS 'Estado: registered, preliminary, final, amended, corrected, cancelled, entered-in-error, unknown';
COMMENT ON COLUMN fhir_observations.value_quantity IS 'Valor numérico con unidad (ej: 120 mmHg)';
COMMENT ON COLUMN fhir_observations.component IS 'Componentes para observaciones multi-valor (ej: presión arterial)';
COMMENT ON COLUMN fhir_observations.reference_range IS 'Rangos de referencia normales';
COMMENT ON COLUMN fhir_observations.interpretation IS 'Interpretación: Normal, High, Low, Critical, etc';
COMMENT ON COLUMN fhir_observations.source_type IS 'Tipo de origen: signo_vital, laboratorio, estudio_especial';
COMMENT ON COLUMN fhir_observations.source_id IS 'ID del recurso original en el sistema';

-- Insertar datos de ejemplo (opcional)
-- Ejemplo de observación de glucosa
INSERT INTO fhir_observations (
    status,
    category,
    code,
    subject_id,
    effective_datetime,
    value_quantity,
    interpretation,
    reference_range,
    source_type
) VALUES (
    'final',
    ARRAY['laboratory'],
    '{
        "coding": [{
            "system": "http://loinc.org",
            "code": "2345-7",
            "display": "Glucose"
        }],
        "text": "Glucosa"
    }'::jsonb,
    (SELECT id FROM pacientes LIMIT 1),
    NOW(),
    '{
        "value": 95,
        "unit": "mg/dL",
        "system": "http://unitsofmeasure.org",
        "code": "mg/dL"
    }'::jsonb,
    '[{
        "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
            "code": "N",
            "display": "Normal"
        }]
    }]'::jsonb,
    '[{
        "low": {
            "value": 70,
            "unit": "mg/dL",
            "system": "http://unitsofmeasure.org",
            "code": "mg/dL"
        },
        "high": {
            "value": 100,
            "unit": "mg/dL",
            "system": "http://unitsofmeasure.org",
            "code": "mg/dL"
        }
    }]'::jsonb,
    'laboratorio'
) ON CONFLICT DO NOTHING;

-- Ejemplo de observación de presión arterial (multi-componente)
INSERT INTO fhir_observations (
    status,
    category,
    code,
    subject_id,
    effective_datetime,
    component,
    interpretation,
    source_type
) VALUES (
    'final',
    ARRAY['vital-signs'],
    '{
        "coding": [{
            "system": "http://loinc.org",
            "code": "85354-9",
            "display": "Blood pressure panel"
        }],
        "text": "Presión Arterial"
    }'::jsonb,
    (SELECT id FROM pacientes LIMIT 1),
    NOW(),
    '[
        {
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "8480-6",
                    "display": "Systolic blood pressure"
                }]
            },
            "valueQuantity": {
                "value": 120,
                "unit": "mmHg",
                "system": "http://unitsofmeasure.org",
                "code": "mm[Hg]"
            }
        },
        {
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "8462-4",
                    "display": "Diastolic blood pressure"
                }]
            },
            "valueQuantity": {
                "value": 80,
                "unit": "mmHg",
                "system": "http://unitsofmeasure.org",
                "code": "mm[Hg]"
            }
        }
    ]'::jsonb,
    '[{
        "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
            "code": "N",
            "display": "Normal"
        }]
    }]'::jsonb,
    'signo_vital'
) ON CONFLICT DO NOTHING;

-- Vista para consultas simplificadas
CREATE OR REPLACE VIEW v_fhir_observations_summary AS
SELECT 
    o.id,
    o.status,
    o.category,
    o.code->>'text' as observation_name,
    o.subject_id,
    p.nombre_completo as patient_name,
    o.effective_datetime,
    COALESCE(
        o.value_quantity->>'value',
        o.value_string,
        o.value_boolean::text,
        o.value_integer::text
    ) as value,
    COALESCE(
        o.value_quantity->>'unit',
        ''
    ) as unit,
    o.interpretation,
    o.source_type,
    o.created_at
FROM fhir_observations o
JOIN pacientes p ON o.subject_id = p.id
ORDER BY o.effective_datetime DESC;

-- Permisos
GRANT SELECT, INSERT, UPDATE, DELETE ON fhir_observations TO ddx_user;
GRANT SELECT ON v_fhir_observations_summary TO ddx_user;

-- Verificación
SELECT 'Migración de FHIR Observations completada exitosamente' as status;
