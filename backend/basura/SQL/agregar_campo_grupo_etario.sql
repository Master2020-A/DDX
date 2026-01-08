-- Migración para agregar campo grupo_etario a rangos_referencia
-- Ejecutar en la base de datos PostgreSQL

-- Agregar columna grupo_etario
ALTER TABLE rangos_referencia 
ADD COLUMN IF NOT EXISTS grupo_etario VARCHAR(50);

-- Crear índice para mejorar búsquedas
CREATE INDEX IF NOT EXISTS idx_rangos_grupo_etario 
ON rangos_referencia(grupo_etario);

-- Crear índice compuesto para búsquedas por sexo y grupo etario
CREATE INDEX IF NOT EXISTS idx_rangos_sexo_grupo 
ON rangos_referencia(sexo, grupo_etario);

-- Comentarios
COMMENT ON COLUMN rangos_referencia.grupo_etario IS 'Grupo etario: recien_nacido, pediatrico, adolescente, adulto, embarazo';

-- Verificar
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'rangos_referencia'
AND column_name = 'grupo_etario';
