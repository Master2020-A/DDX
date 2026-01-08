-- Agregar campo medico_id a la tabla anomalias_detectadas
-- Ejecuta este script en pgAdmin o psql

-- Verificar si la columna existe
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'anomalias_detectadas' 
        AND column_name = 'medico_id'
    ) THEN
        -- Agregar la columna
        ALTER TABLE anomalias_detectadas 
        ADD COLUMN medico_id UUID REFERENCES usuarios(id) ON DELETE CASCADE;
        
        RAISE NOTICE 'Columna medico_id agregada exitosamente';
    ELSE
        RAISE NOTICE 'Columna medico_id ya existe';
    END IF;
END $$;

-- Verificar las columnas de la tabla
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'anomalias_detectadas'
ORDER BY ordinal_position;
