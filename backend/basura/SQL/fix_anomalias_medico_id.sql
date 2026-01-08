-- Agregar columna medico_id a la tabla anomalias_detectadas
ALTER TABLE anomalias_detectadas 
ADD COLUMN IF NOT EXISTS medico_id UUID REFERENCES usuarios(id) ON DELETE CASCADE;

-- Verificar que se agregó correctamente
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'anomalias_detectadas'
ORDER BY ordinal_position;
