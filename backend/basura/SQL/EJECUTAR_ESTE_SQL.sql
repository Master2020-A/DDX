-- ============================================================
-- SCRIPT PARA CORREGIR LA BASE DE DATOS
-- Ejecuta este SQL en tu cliente PostgreSQL (pgAdmin, DBeaver, etc.)
-- ============================================================

-- 1. Agregar columna medico_id a anomalias_detectadas
ALTER TABLE anomalias_detectadas 
ADD COLUMN IF NOT EXISTS medico_id UUID REFERENCES usuarios(id) ON DELETE CASCADE;

-- 2. Verificar que se agregó correctamente
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'anomalias_detectadas'
ORDER BY ordinal_position;

-- ============================================================
-- Si ves "medico_id" en los resultados, la corrección fue exitosa
-- ============================================================
