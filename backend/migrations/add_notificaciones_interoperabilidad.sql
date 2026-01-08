-- Migración: Agregar tabla de notificaciones para interoperabilidad
-- Fecha: 2024
-- Descripción: Sistema de notificaciones push en tiempo real para el módulo de interoperabilidad

-- Crear enum para tipos de notificación
CREATE TYPE tipo_notificacion_interop AS ENUM (
    'solicitud_nueva',
    'solicitud_aprobada',
    'solicitud_rechazada',
    'solicitud_completada',
    'solicitud_error',
    'consentimiento_expira',
    'consentimiento_expirado',
    'institucion_nueva',
    'institucion_inactiva',
    'alerta_sistema'
);

-- Crear enum para prioridad de notificación
CREATE TYPE prioridad_notificacion_interop AS ENUM (
    'baja',
    'media',
    'alta',
    'urgente'
);

-- Crear tabla de notificaciones
CREATE TABLE notificaciones_interoperabilidad (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Tipo y prioridad
    tipo tipo_notificacion_interop NOT NULL,
    prioridad prioridad_notificacion_interop NOT NULL DEFAULT 'media',
    
    -- Contenido
    titulo VARCHAR(200) NOT NULL,
    mensaje TEXT NOT NULL,
    datos_adicionales TEXT,
    
    -- Destinatario
    usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    
    -- Referencias
    solicitud_id UUID REFERENCES solicitudes_intercambio(id) ON DELETE SET NULL,
    institucion_id UUID REFERENCES instituciones_externas(id) ON DELETE SET NULL,
    
    -- Estado
    leida BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_lectura TIMESTAMP,
    
    -- Acciones
    accion_url VARCHAR(500),
    accion_texto VARCHAR(100),
    
    -- Auditoría
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para mejorar rendimiento
CREATE INDEX idx_notif_interop_usuario ON notificaciones_interoperabilidad(usuario_id);
CREATE INDEX idx_notif_interop_tipo ON notificaciones_interoperabilidad(tipo);
CREATE INDEX idx_notif_interop_prioridad ON notificaciones_interoperabilidad(prioridad);
CREATE INDEX idx_notif_interop_leida ON notificaciones_interoperabilidad(leida);
CREATE INDEX idx_notif_interop_solicitud ON notificaciones_interoperabilidad(solicitud_id);
CREATE INDEX idx_notif_interop_institucion ON notificaciones_interoperabilidad(institucion_id);
CREATE INDEX idx_notif_interop_created ON notificaciones_interoperabilidad(created_at DESC);
CREATE INDEX idx_notif_interop_usuario_leida ON notificaciones_interoperabilidad(usuario_id, leida);

-- Trigger para actualizar updated_at
CREATE OR REPLACE FUNCTION update_notificaciones_interop_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_notificaciones_interop_updated_at
    BEFORE UPDATE ON notificaciones_interoperabilidad
    FOR EACH ROW
    EXECUTE FUNCTION update_notificaciones_interop_updated_at();

-- Comentarios
COMMENT ON TABLE notificaciones_interoperabilidad IS 'Notificaciones push en tiempo real para el sistema de interoperabilidad';
COMMENT ON COLUMN notificaciones_interoperabilidad.tipo IS 'Tipo de notificación (solicitud_nueva, aprobada, rechazada, etc.)';
COMMENT ON COLUMN notificaciones_interoperabilidad.prioridad IS 'Nivel de prioridad (baja, media, alta, urgente)';
COMMENT ON COLUMN notificaciones_interoperabilidad.titulo IS 'Título corto de la notificación';
COMMENT ON COLUMN notificaciones_interoperabilidad.mensaje IS 'Mensaje descriptivo de la notificación';
COMMENT ON COLUMN notificaciones_interoperabilidad.datos_adicionales IS 'Datos adicionales en formato JSON';
COMMENT ON COLUMN notificaciones_interoperabilidad.usuario_id IS 'Usuario destinatario de la notificación';
COMMENT ON COLUMN notificaciones_interoperabilidad.solicitud_id IS 'Solicitud relacionada (opcional)';
COMMENT ON COLUMN notificaciones_interoperabilidad.institucion_id IS 'Institución relacionada (opcional)';
COMMENT ON COLUMN notificaciones_interoperabilidad.leida IS 'Indica si la notificación ha sido leída';
COMMENT ON COLUMN notificaciones_interoperabilidad.fecha_lectura IS 'Fecha y hora en que se leyó la notificación';
COMMENT ON COLUMN notificaciones_interoperabilidad.accion_url IS 'URL para acción relacionada con la notificación';
COMMENT ON COLUMN notificaciones_interoperabilidad.accion_texto IS 'Texto del botón de acción';

-- Datos de ejemplo (opcional - comentado por defecto)
/*
-- Insertar notificación de ejemplo
INSERT INTO notificaciones_interoperabilidad (
    tipo,
    prioridad,
    titulo,
    mensaje,
    usuario_id,
    accion_url,
    accion_texto
) VALUES (
    'alerta_sistema',
    'media',
    'Sistema de Notificaciones Activado',
    'El sistema de notificaciones push en tiempo real ha sido activado exitosamente.',
    (SELECT id FROM usuarios LIMIT 1),
    '/interoperabilidad',
    'Ver Interoperabilidad'
);
*/

-- Verificación
DO $$
BEGIN
    RAISE NOTICE 'Migración completada: Tabla notificaciones_interoperabilidad creada exitosamente';
    RAISE NOTICE 'Índices creados: 8';
    RAISE NOTICE 'Triggers creados: 1';
END $$;
