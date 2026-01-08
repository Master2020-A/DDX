-- ============================================================================
-- Migración: Mejoras Historia Clínica
-- Descripción: Agregar campos para servicio médico, exámenes y sustancias
-- ============================================================================

-- Agregar servicio de atención médica
ALTER TABLE historias_clinicas 
ADD COLUMN IF NOT EXISTS servicio_atencion_medica VARCHAR(200);

-- Agregar checkboxes de exámenes previos
ALTER TABLE historias_clinicas 
ADD COLUMN IF NOT EXISTS examenes_previos_realizados JSONB;

-- Agregar checkboxes de sustancias tóxicas
ALTER TABLE historias_clinicas 
ADD COLUMN IF NOT EXISTS sustancias_toxicas_checkboxes JSONB;

-- Comentarios
COMMENT ON COLUMN historias_clinicas.servicio_atencion_medica IS 'Institución de salud donde se atiende (IMSS, ISSSTE, etc.)';
COMMENT ON COLUMN historias_clinicas.examenes_previos_realizados IS 'Checkboxes de exámenes de laboratorio realizados';
COMMENT ON COLUMN historias_clinicas.sustancias_toxicas_checkboxes IS 'Checkboxes de exposición a sustancias tóxicas';
