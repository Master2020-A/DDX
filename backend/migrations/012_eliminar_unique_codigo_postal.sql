-- Migración: Eliminar constraint UNIQUE de codigo_postal para permitir múltiples colonias
-- Fecha: 2024-12-01
-- Descripción: Permite guardar múltiples colonias para el mismo código postal

-- 1. Eliminar constraint UNIQUE de codigo_postal
ALTER TABLE codigos_postales DROP CONSTRAINT IF EXISTS codigos_postales_codigo_postal_key;

-- 2. Nota: El índice se mantiene para búsquedas rápidas, solo se elimina la restricción UNIQUE
-- El índice ya existe: codigos_postales_codigo_postal_idx

COMMENT ON COLUMN codigos_postales.codigo_postal IS 'Código postal (puede repetirse para diferentes colonias)';
