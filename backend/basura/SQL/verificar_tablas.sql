-- Verificar si las tablas de IA existen
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'analisis_ia',
    'predicciones_riesgo',
    'recomendaciones_tratamiento',
    'interacciones_medicamentosas',
    'anomalias_detectadas',
    'asistente_ia'
)
ORDER BY table_name;

-- Verificar columnas de pacientes
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'pacientes'
AND column_name IN ('edad', 'genero', 'alergias')
ORDER BY column_name;

-- Verificar columnas de expedientes_clinicos
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'expedientes_clinicos'
AND column_name = 'signos_vitales';

-- Verificar columnas de consultas
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'consultas'
AND column_name IN ('fecha', 'fecha_hora')
ORDER BY column_name;
