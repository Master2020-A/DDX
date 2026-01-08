-- Migración: Agregar tablas de webhooks para interoperabilidad
-- Fecha: 2024
-- Descripción: Sistema de suscripciones a eventos y webhooks para notificaciones automáticas

-- Crear enum para eventos de webhook
CREATE TYPE evento_webhook AS ENUM (
    'solicitud.creada',
    'solicitud.aprobada',
    'solicitud.rechazada',
    'solicitud.completada',
    'solicitud.error',
    'institucion.creada',
    'institucion.actualizada',
    'institucion.desactivada',
    'consentimiento.creado',
    'consentimiento.revocado',
    'consentimiento.expirando',
    'bundle.generado',
    'historia.creada'
);

-- Crear enum para estado de webhook
CREATE TYPE estado_webhook AS ENUM (
    'activo',
    'pausado',
    'desactivado',
    'error'
);

-- Crear tabla de suscripciones de webhooks
CREATE TABLE webhook_suscripciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Información básica
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    
    -- URL de destino
    url VARCHAR(500) NOT NULL,
    
    -- Eventos suscritos (array JSON)
    eventos JSONB NOT NULL,
    
    -- Autenticación
    secret_key VARCHAR(100) NOT NULL,
    headers_adicionales JSONB,
    
    -- Configuración
    timeout_segundos INTEGER NOT NULL DEFAULT 30,
    reintentos_max INTEGER NOT NULL DEFAULT 3,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    estado estado_webhook NOT NULL DEFAULT 'activo',
    
    -- Filtros opcionales
    filtros JSONB,
    
    -- Propietario
    usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    institucion_id UUID REFERENCES instituciones_externas(id) ON DELETE SET NULL,
    
    -- Estadísticas
    total_envios INTEGER NOT NULL DEFAULT 0,
    total_exitosos INTEGER NOT NULL DEFAULT 0,
    total_fallidos INTEGER NOT NULL DEFAULT 0,
    ultimo_envio TIMESTAMP,
    ultimo_exito TIMESTAMP,
    ultimo_error TEXT,
    ultimo_error_fecha TIMESTAMP,
    
    -- Auditoría
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear tabla de entregas de webhooks
CREATE TABLE webhook_entregas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Suscripción
    suscripcion_id UUID NOT NULL REFERENCES webhook_suscripciones(id) ON DELETE CASCADE,
    
    -- Evento
    evento VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    
    -- Entrega
    url VARCHAR(500) NOT NULL,
    metodo VARCHAR(10) NOT NULL DEFAULT 'POST',
    headers JSONB,
    
    -- Resultado
    exitoso BOOLEAN NOT NULL,
    codigo_http INTEGER,
    respuesta TEXT,
    error TEXT,
    tiempo_respuesta_ms INTEGER,
    
    -- Reintentos
    intento INTEGER NOT NULL DEFAULT 1,
    max_intentos INTEGER NOT NULL DEFAULT 3,
    
    -- Auditoría
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completado_at TIMESTAMP
);

-- Índices para webhook_suscripciones
CREATE INDEX idx_webhook_suscripciones_usuario ON webhook_suscripciones(usuario_id);
CREATE INDEX idx_webhook_suscripciones_institucion ON webhook_suscripciones(institucion_id);
CREATE INDEX idx_webhook_suscripciones_activo ON webhook_suscripciones(activo);
CREATE INDEX idx_webhook_suscripciones_estado ON webhook_suscripciones(estado);
CREATE INDEX idx_webhook_suscripciones_created ON webhook_suscripciones(created_at DESC);
CREATE INDEX idx_webhook_suscripciones_eventos ON webhook_suscripciones USING GIN(eventos);

-- Índices para webhook_entregas
CREATE INDEX idx_webhook_entregas_suscripcion ON webhook_entregas(suscripcion_id);
CREATE INDEX idx_webhook_entregas_evento ON webhook_entregas(evento);
CREATE INDEX idx_webhook_entregas_exitoso ON webhook_entregas(exitoso);
CREATE INDEX idx_webhook_entregas_created ON webhook_entregas(created_at DESC);
CREATE INDEX idx_webhook_entregas_suscripcion_created ON webhook_entregas(suscripcion_id, created_at DESC);

-- Trigger para actualizar updated_at en webhook_suscripciones
CREATE OR REPLACE FUNCTION update_webhook_suscripciones_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_webhook_suscripciones_updated_at
    BEFORE UPDATE ON webhook_suscripciones
    FOR EACH ROW
    EXECUTE FUNCTION update_webhook_suscripciones_updated_at();

-- Comentarios
COMMENT ON TABLE webhook_suscripciones IS 'Suscripciones de webhooks para eventos de interoperabilidad';
COMMENT ON COLUMN webhook_suscripciones.nombre IS 'Nombre descriptivo de la suscripción';
COMMENT ON COLUMN webhook_suscripciones.url IS 'URL de destino donde se enviarán los eventos';
COMMENT ON COLUMN webhook_suscripciones.eventos IS 'Array JSON de eventos suscritos';
COMMENT ON COLUMN webhook_suscripciones.secret_key IS 'Clave secreta para firmar payloads (HMAC-SHA256)';
COMMENT ON COLUMN webhook_suscripciones.headers_adicionales IS 'Headers HTTP adicionales en formato JSON';
COMMENT ON COLUMN webhook_suscripciones.timeout_segundos IS 'Timeout en segundos para las peticiones HTTP';
COMMENT ON COLUMN webhook_suscripciones.reintentos_max IS 'Número máximo de reintentos en caso de fallo';
COMMENT ON COLUMN webhook_suscripciones.filtros IS 'Filtros opcionales para eventos en formato JSON';

COMMENT ON TABLE webhook_entregas IS 'Historial de entregas de webhooks';
COMMENT ON COLUMN webhook_entregas.evento IS 'Tipo de evento enviado';
COMMENT ON COLUMN webhook_entregas.payload IS 'Payload completo enviado en formato JSON';
COMMENT ON COLUMN webhook_entregas.exitoso IS 'Indica si la entrega fue exitosa (código HTTP 2xx)';
COMMENT ON COLUMN webhook_entregas.tiempo_respuesta_ms IS 'Tiempo de respuesta en milisegundos';
COMMENT ON COLUMN webhook_entregas.intento IS 'Número de intento actual';

-- Función para limpiar entregas antiguas (opcional)
CREATE OR REPLACE FUNCTION limpiar_webhook_entregas_antiguas(dias_antiguedad INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    registros_eliminados INTEGER;
BEGIN
    DELETE FROM webhook_entregas
    WHERE created_at < CURRENT_TIMESTAMP - (dias_antiguedad || ' days')::INTERVAL
    AND exitoso = TRUE;
    
    GET DIAGNOSTICS registros_eliminados = ROW_COUNT;
    RETURN registros_eliminados;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION limpiar_webhook_entregas_antiguas IS 'Elimina entregas exitosas más antiguas que X días para mantener la tabla limpia';

-- Datos de ejemplo (opcional - comentado por defecto)
/*
-- Insertar webhook de ejemplo
INSERT INTO webhook_suscripciones (
    nombre,
    descripcion,
    url,
    eventos,
    secret_key,
    usuario_id
) VALUES (
    'Webhook de Prueba',
    'Webhook de ejemplo para pruebas del sistema',
    'https://webhook.site/unique-id',
    '["solicitud.creada", "solicitud.aprobada"]'::jsonb,
    'secret_key_ejemplo_12345',
    (SELECT id FROM usuarios LIMIT 1)
);
*/

-- Verificación
DO $$
BEGIN
    RAISE NOTICE 'Migración completada: Tablas de webhooks creadas exitosamente';
    RAISE NOTICE 'Tablas creadas: 2 (webhook_suscripciones, webhook_entregas)';
    RAISE NOTICE 'Índices creados: 11';
    RAISE NOTICE 'Triggers creados: 1';
    RAISE NOTICE 'Funciones creadas: 1 (limpiar_webhook_entregas_antiguas)';
END $$;
