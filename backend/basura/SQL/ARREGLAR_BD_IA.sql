-- Script SQL para arreglar problemas de base de datos del módulo IA
-- Ejecutar este script en PostgreSQL para resolver errores de columnas faltantes

-- 1. Agregar columna updated_at a predicciones_riesgo (si no existe)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'predicciones_riesgo' AND column_name = 'updated_at'
    ) THEN
        ALTER TABLE predicciones_riesgo 
        ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();
        
        -- Actualizar registros existentes
        UPDATE predicciones_riesgo 
        SET updated_at = created_at 
        WHERE updated_at IS NULL;
        
        RAISE NOTICE 'Columna updated_at agregada a predicciones_riesgo';
    ELSE
        RAISE NOTICE 'Columna updated_at ya existe en predicciones_riesgo';
    END IF;
END $$;

-- 2. Agregar columna medico_id a anomalias_detectadas (si no existe)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'anomalias_detectadas' AND column_name = 'medico_id'
    ) THEN
        ALTER TABLE anomalias_detectadas 
        ADD COLUMN medico_id UUID REFERENCES usuarios(id);
        
        RAISE NOTICE 'Columna medico_id agregada a anomalias_detectadas';
    ELSE
        RAISE NOTICE 'Columna medico_id ya existe en anomalias_detectadas';
    END IF;
END $$;

-- 3. Agregar columna sesion_id a asistente_ia (si no existe)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'asistente_ia' AND column_name = 'sesion_id'
    ) THEN
        ALTER TABLE asistente_ia 
        ADD COLUMN sesion_id UUID DEFAULT gen_random_uuid();
        
        RAISE NOTICE 'Columna sesion_id agregada a asistente_ia';
    ELSE
        RAISE NOTICE 'Columna sesion_id ya existe en asistente_ia';
    END IF;
END $$;

-- 4. Agregar columna contexto a asistente_ia (si no existe)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'asistente_ia' AND column_name = 'contexto'
    ) THEN
        ALTER TABLE asistente_ia 
        ADD COLUMN contexto JSONB;
        
        RAISE NOTICE 'Columna contexto agregada a asistente_ia';
    ELSE
        RAISE NOTICE 'Columna contexto ya existe en asistente_ia';
    END IF;
END $$;

-- 5. Verificar estructura de tablas
SELECT 
    'predicciones_riesgo' as tabla,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'predicciones_riesgo'
ORDER BY ordinal_position;

SELECT 
    'anomalias_detectadas' as tabla,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'anomalias_detectadas'
ORDER BY ordinal_position;

SELECT 
    'asistente_ia' as tabla,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'asistente_ia'
ORDER BY ordinal_position;

-- Fin del script
