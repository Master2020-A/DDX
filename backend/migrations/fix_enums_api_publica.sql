-- Fix: Agregar tipos ENUM faltantes para API Pública

-- Crear tipo ENUM para TipoEvento
DO $$ BEGIN
    CREATE TYPE tipoevento AS ENUM (
        'paciente.creado',
        'paciente.actualizado',
        'paciente.eliminado',
        'consulta.creada',
        'consulta.actualizada',
        'consulta.finalizada',
        'laboratorio.creado',
        'laboratorio.completado',
        'factura.generada',
        'factura.timbrada',
        'cita.creada',
        'cita.cancelada'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Crear tipo ENUM para EstadoPlugin
DO $$ BEGIN
    CREATE TYPE estadoplugin AS ENUM (
        'pendiente',
        'en_revision',
        'aprobado',
        'rechazado',
        'suspendido',
        'obsoleto'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Actualizar tabla plugins para usar el ENUM si existe
DO $$ 
BEGIN
    -- Verificar si la columna existe y es VARCHAR
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'plugins' 
        AND column_name = 'estado' 
        AND data_type = 'character varying'
    ) THEN
        -- Convertir la columna a ENUM
        ALTER TABLE plugins 
        ALTER COLUMN estado TYPE estadoplugin 
        USING estado::estadoplugin;
    END IF;
END $$;

-- Actualizar tabla webhooks para usar el ENUM si existe
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'webhooks' 
        AND column_name = 'eventos'
    ) THEN
        -- La columna eventos ya existe como TEXT[]
        NULL;
    END IF;
END $$;
