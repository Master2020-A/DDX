-- Script SQL para crear tablas del módulo de Telemedicina
-- Ejecutar este script en PostgreSQL

-- 1. Tabla de consultas remotas
CREATE TABLE IF NOT EXISTS consultas_remotas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Relaciones
    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    medico_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    consulta_id UUID REFERENCES consultas(id) ON DELETE SET NULL,
    
    -- Información de la sesión
    sala_id VARCHAR(100) UNIQUE NOT NULL,
    estado VARCHAR(50) DEFAULT 'programada',
    tipo VARCHAR(50) DEFAULT 'videollamada',
    
    -- Programación
    fecha_programada TIMESTAMP NOT NULL,
    fecha_inicio TIMESTAMP,
    fecha_fin TIMESTAMP,
    duracion_minutos INTEGER,
    
    -- Configuración de la llamada
    video_habilitado BOOLEAN DEFAULT TRUE,
    audio_habilitado BOOLEAN DEFAULT TRUE,
    compartir_pantalla BOOLEAN DEFAULT FALSE,
    grabacion_habilitada BOOLEAN DEFAULT FALSE,
    
    -- URLs y tokens
    url_sala_medico VARCHAR(500),
    url_sala_paciente VARCHAR(500),
    token_acceso VARCHAR(200),
    
    -- Calidad de la conexión
    calidad_video VARCHAR(20) DEFAULT 'hd',
    ancho_banda_usado INTEGER,
    
    -- Notas y seguimiento
    motivo_consulta TEXT,
    notas_medico TEXT,
    diagnostico_preliminar TEXT,
    plan_tratamiento TEXT,
    
    -- Prescripciones generadas
    prescripciones_generadas JSONB,
    
    -- Archivos compartidos
    archivos_compartidos JSONB,
    
    -- Evaluación post-consulta
    calificacion_paciente INTEGER CHECK (calificacion_paciente >= 1 AND calificacion_paciente <= 5),
    comentarios_paciente TEXT,
    
    -- Seguimiento
    requiere_seguimiento BOOLEAN DEFAULT FALSE,
    fecha_seguimiento TIMESTAMP,
    
    -- Metadatos
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Tabla de mensajes de chat
CREATE TABLE IF NOT EXISTS mensajes_chat (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Relación con consulta remota
    consulta_remota_id UUID NOT NULL REFERENCES consultas_remotas(id) ON DELETE CASCADE,
    
    -- Emisor del mensaje
    emisor_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    emisor_tipo VARCHAR(20) NOT NULL,
    
    -- Contenido
    tipo_mensaje VARCHAR(50) DEFAULT 'texto',
    contenido TEXT NOT NULL,
    archivo_url VARCHAR(500),
    archivo_nombre VARCHAR(200),
    archivo_tipo VARCHAR(50),
    
    -- Estado
    leido BOOLEAN DEFAULT FALSE,
    fecha_lectura TIMESTAMP,
    
    -- Metadatos
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3. Tabla de seguimiento post-consulta
CREATE TABLE IF NOT EXISTS seguimientos_post_consulta (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Relaciones
    consulta_remota_id UUID NOT NULL REFERENCES consultas_remotas(id) ON DELETE CASCADE,
    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    medico_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    
    -- Tipo de seguimiento
    tipo VARCHAR(50) NOT NULL,
    estado VARCHAR(50) DEFAULT 'pendiente',
    
    -- Programación
    fecha_programada TIMESTAMP NOT NULL,
    fecha_enviado TIMESTAMP,
    fecha_completado TIMESTAMP,
    
    -- Contenido
    titulo VARCHAR(200) NOT NULL,
    mensaje TEXT NOT NULL,
    
    -- Respuesta del paciente
    respuesta_paciente TEXT,
    datos_seguimiento JSONB,
    
    -- Recordatorios
    recordatorio_enviado BOOLEAN DEFAULT FALSE,
    metodo_notificacion VARCHAR(50) DEFAULT 'email',
    
    -- Metadatos
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 4. Tabla de prescripciones electrónicas
CREATE TABLE IF NOT EXISTS prescripciones_electronicas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Relaciones
    consulta_remota_id UUID REFERENCES consultas_remotas(id) ON DELETE SET NULL,
    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    medico_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    
    -- Información de la receta
    numero_receta VARCHAR(50) UNIQUE NOT NULL,
    fecha_emision TIMESTAMP DEFAULT NOW(),
    fecha_vigencia TIMESTAMP,
    
    -- Medicamentos prescritos
    medicamentos JSONB NOT NULL,
    
    -- Diagnóstico
    diagnostico TEXT NOT NULL,
    codigo_cie10 VARCHAR(20),
    
    -- Indicaciones
    indicaciones_generales TEXT,
    
    -- Firma digital
    firma_digital TEXT,
    hash_documento VARCHAR(200),
    certificado_digital TEXT,
    
    -- Estado
    estado VARCHAR(50) DEFAULT 'activa',
    
    -- Envío
    enviada_paciente BOOLEAN DEFAULT FALSE,
    fecha_envio TIMESTAMP,
    metodo_envio VARCHAR(50),
    
    -- PDF generado
    pdf_url VARCHAR(500),
    
    -- Metadatos
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices para mejorar el rendimiento

-- Consultas remotas
CREATE INDEX IF NOT EXISTS idx_consultas_remotas_paciente ON consultas_remotas(paciente_id);
CREATE INDEX IF NOT EXISTS idx_consultas_remotas_medico ON consultas_remotas(medico_id);
CREATE INDEX IF NOT EXISTS idx_consultas_remotas_sala ON consultas_remotas(sala_id);
CREATE INDEX IF NOT EXISTS idx_consultas_remotas_estado ON consultas_remotas(estado);
CREATE INDEX IF NOT EXISTS idx_consultas_remotas_fecha_programada ON consultas_remotas(fecha_programada);

-- Mensajes de chat
CREATE INDEX IF NOT EXISTS idx_mensajes_chat_consulta ON mensajes_chat(consulta_remota_id);
CREATE INDEX IF NOT EXISTS idx_mensajes_chat_emisor ON mensajes_chat(emisor_id);
CREATE INDEX IF NOT EXISTS idx_mensajes_chat_created ON mensajes_chat(created_at);

-- Seguimientos
CREATE INDEX IF NOT EXISTS idx_seguimientos_consulta ON seguimientos_post_consulta(consulta_remota_id);
CREATE INDEX IF NOT EXISTS idx_seguimientos_paciente ON seguimientos_post_consulta(paciente_id);
CREATE INDEX IF NOT EXISTS idx_seguimientos_estado ON seguimientos_post_consulta(estado);
CREATE INDEX IF NOT EXISTS idx_seguimientos_fecha_programada ON seguimientos_post_consulta(fecha_programada);

-- Prescripciones
CREATE INDEX IF NOT EXISTS idx_prescripciones_consulta ON prescripciones_electronicas(consulta_remota_id);
CREATE INDEX IF NOT EXISTS idx_prescripciones_paciente ON prescripciones_electronicas(paciente_id);
CREATE INDEX IF NOT EXISTS idx_prescripciones_medico ON prescripciones_electronicas(medico_id);
CREATE INDEX IF NOT EXISTS idx_prescripciones_numero ON prescripciones_electronicas(numero_receta);
CREATE INDEX IF NOT EXISTS idx_prescripciones_estado ON prescripciones_electronicas(estado);

-- Comentarios sobre las tablas
COMMENT ON TABLE consultas_remotas IS 'Consultas médicas remotas por videollamada';
COMMENT ON TABLE mensajes_chat IS 'Mensajes de chat durante consultas remotas';
COMMENT ON TABLE seguimientos_post_consulta IS 'Seguimiento después de consultas remotas';
COMMENT ON TABLE prescripciones_electronicas IS 'Prescripciones generadas durante consultas remotas';

-- Verificar que las tablas se crearon correctamente
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as num_columnas
FROM information_schema.tables t
WHERE table_schema = 'public' 
AND table_name IN ('consultas_remotas', 'mensajes_chat', 'seguimientos_post_consulta', 'prescripciones_electronicas')
ORDER BY table_name;
