-- Migración para Sistema de Interoperabilidad HL7 FHIR
-- Red Nacional de Salud e Intercambio de Expedientes

-- ==================== ENUMS ====================

CREATE TYPE tipo_intercambio AS ENUM (
    'expediente_completo',
    'consultas',
    'laboratorios',
    'imagenes',
    'recetas',
    'hospitalizacion'
);

CREATE TYPE estado_intercambio AS ENUM (
    'pendiente',
    'aprobada',
    'rechazada',
    'en_proceso',
    'completada',
    'error'
);

CREATE TYPE protocolo_intercambio AS ENUM (
    'FHIR_R4',
    'FHIR_R5',
    'HL7V2',
    'REST_API'
);

-- ==================== INSTITUCIONES EXTERNAS ====================

CREATE TABLE IF NOT EXISTS instituciones_externas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(255) NOT NULL,
    codigo_institucional VARCHAR(50) UNIQUE NOT NULL,
    nivel_atencion VARCHAR(20) NOT NULL CHECK (nivel_atencion IN ('primario', 'secundario', 'terciario', 'especializado')),
    tipo_institucion VARCHAR(20) NOT NULL CHECK (tipo_institucion IN ('publico', 'privado', 'mixto')),
    
    -- Ubicación
    pais VARCHAR(100) NOT NULL DEFAULT 'México',
    estado VARCHAR(100),
    ciudad VARCHAR(100),
    direccion TEXT,
    
    -- Contacto
    telefono VARCHAR(20),
    email VARCHAR(255),
    
    -- Endpoints de interoperabilidad
    url_endpoint_fhir TEXT,
    url_endpoint_hl7v2 TEXT,
    certificado_ssl TEXT,
    
    -- Estado
    activa BOOLEAN DEFAULT TRUE,
    
    -- Capacidades
    protocolos_soportados TEXT[] DEFAULT ARRAY['FHIR_R4'],
    versiones_fhir TEXT[] DEFAULT ARRAY['4.0.1'],
    capacidades JSONB,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_instituciones_externas_codigo ON instituciones_externas(codigo_institucional);
CREATE INDEX idx_instituciones_externas_activa ON instituciones_externas(activa);

-- ==================== SOLICITUDES DE INTERCAMBIO ====================

CREATE TABLE IF NOT EXISTS solicitudes_intercambio (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Referencias
    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    institucion_origen_id UUID NOT NULL REFERENCES instituciones(id) ON DELETE CASCADE,
    institucion_destino_id UUID NOT NULL REFERENCES instituciones_externas(id) ON DELETE CASCADE,
    
    -- Tipo de intercambio
    tipo_intercambio tipo_intercambio NOT NULL,
    protocolo protocolo_intercambio NOT NULL DEFAULT 'FHIR_R4',
    
    -- Estado
    estado estado_intercambio NOT NULL DEFAULT 'pendiente',
    prioridad VARCHAR(20) DEFAULT 'normal' CHECK (prioridad IN ('baja', 'normal', 'alta', 'urgente')),
    
    -- Detalles
    motivo_solicitud TEXT,
    periodo_inicio TIMESTAMP,
    periodo_fin TIMESTAMP,
    
    -- Aprobación
    solicitante_id UUID NOT NULL REFERENCES usuarios(id),
    aprobador_id UUID REFERENCES usuarios(id),
    fecha_aprobacion TIMESTAMP,
    fecha_completado TIMESTAMP,
    
    -- Datos
    datos_enviados JSONB,
    datos_recibidos JSONB,
    checksum_datos VARCHAR(64),
    
    -- Errores
    motivo_rechazo TEXT,
    errores TEXT[],
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_solicitudes_paciente ON solicitudes_intercambio(paciente_id);
CREATE INDEX idx_solicitudes_estado ON solicitudes_intercambio(estado);
CREATE INDEX idx_solicitudes_tipo ON solicitudes_intercambio(tipo_intercambio);
CREATE INDEX idx_solicitudes_origen ON solicitudes_intercambio(institucion_origen_id);
CREATE INDEX idx_solicitudes_destino ON solicitudes_intercambio(institucion_destino_id);

-- ==================== HISTORIA CLÍNICA UNIFICADA ====================

CREATE TABLE IF NOT EXISTS historia_clinica_unificada (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id UUID UNIQUE NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    
    -- Contadores
    consultas_totales INTEGER DEFAULT 0,
    hospitalizaciones_totales INTEGER DEFAULT 0,
    
    -- Datos consolidados
    diagnosticos_activos JSONB DEFAULT '[]'::jsonb,
    medicamentos_actuales JSONB DEFAULT '[]'::jsonb,
    alergias_consolidadas JSONB DEFAULT '[]'::jsonb,
    vacunas_consolidadas JSONB DEFAULT '[]'::jsonb,
    
    -- Instituciones que han contribuido
    instituciones_contribuyentes TEXT[] DEFAULT ARRAY[]::TEXT[],
    
    -- Timestamps
    ultima_actualizacion_externa TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_historia_unificada_paciente ON historia_clinica_unificada(paciente_id);

-- ==================== LOGS DE INTERCAMBIO ====================

CREATE TABLE IF NOT EXISTS logs_intercambio (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solicitud_id UUID NOT NULL REFERENCES solicitudes_intercambio(id) ON DELETE CASCADE,
    
    -- Detalles del evento
    accion VARCHAR(100) NOT NULL,
    protocolo VARCHAR(20) NOT NULL,
    direccion VARCHAR(20) NOT NULL CHECK (direccion IN ('ENTRADA', 'SALIDA')),
    
    -- Endpoint
    endpoint TEXT,
    codigo_respuesta INTEGER,
    tiempo_respuesta_ms INTEGER,
    
    -- Error
    error TEXT,
    
    -- Usuario
    usuario_id UUID REFERENCES usuarios(id),
    
    -- Timestamp
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_solicitud ON logs_intercambio(solicitud_id);
CREATE INDEX idx_logs_timestamp ON logs_intercambio(timestamp);

-- ==================== CONSENTIMIENTOS ====================

CREATE TABLE IF NOT EXISTS consentimientos_intercambio (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    
    -- Estado
    activo BOOLEAN DEFAULT TRUE,
    fecha_consentimiento TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP,
    revocado BOOLEAN DEFAULT FALSE,
    fecha_revocacion TIMESTAMP,
    
    -- Alcance
    instituciones_autorizadas TEXT[] DEFAULT ARRAY['todas'],
    tipos_datos_autorizados TEXT[] DEFAULT ARRAY['consultas', 'laboratorios', 'imagenes', 'recetas'],
    
    -- Permisos específicos
    puede_compartir_diagnosticos BOOLEAN DEFAULT TRUE,
    puede_compartir_laboratorios BOOLEAN DEFAULT TRUE,
    puede_compartir_imagenes BOOLEAN DEFAULT TRUE,
    puede_compartir_recetas BOOLEAN DEFAULT TRUE,
    
    -- Propósito
    proposito_uso TEXT[] DEFAULT ARRAY['atencion_medica'],
    
    -- Documento
    documento_firmado_url TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_consentimientos_paciente ON consentimientos_intercambio(paciente_id);
CREATE INDEX idx_consentimientos_activo ON consentimientos_intercambio(activo);

-- ==================== MAPEO DE CÓDIGOS ====================

CREATE TABLE IF NOT EXISTS mapeo_codigos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Sistema origen
    sistema_origen VARCHAR(100) NOT NULL,
    codigo_origen VARCHAR(50) NOT NULL,
    descripcion_origen TEXT,
    
    -- Sistema destino
    sistema_destino VARCHAR(100) NOT NULL,
    codigo_destino VARCHAR(50) NOT NULL,
    descripcion_destino TEXT,
    
    -- Tipo de mapeo
    tipo_concepto VARCHAR(50) NOT NULL,
    equivalencia VARCHAR(20) DEFAULT 'exacta' CHECK (equivalencia IN ('exacta', 'aproximada', 'parcial')),
    
    -- Validación
    validado BOOLEAN DEFAULT FALSE,
    validado_por UUID REFERENCES usuarios(id),
    fecha_validacion TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(sistema_origen, codigo_origen, sistema_destino)
);

CREATE INDEX idx_mapeo_origen ON mapeo_codigos(sistema_origen, codigo_origen);
CREATE INDEX idx_mapeo_destino ON mapeo_codigos(sistema_destino, codigo_destino);

-- ==================== TRIGGERS ====================

-- Trigger para updated_at en instituciones_externas
CREATE OR REPLACE FUNCTION update_instituciones_externas_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_instituciones_externas_updated_at
    BEFORE UPDATE ON instituciones_externas
    FOR EACH ROW
    EXECUTE FUNCTION update_instituciones_externas_updated_at();

-- Trigger para updated_at en solicitudes_intercambio
CREATE OR REPLACE FUNCTION update_solicitudes_intercambio_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_solicitudes_intercambio_updated_at
    BEFORE UPDATE ON solicitudes_intercambio
    FOR EACH ROW
    EXECUTE FUNCTION update_solicitudes_intercambio_updated_at();

-- Trigger para updated_at en historia_clinica_unificada
CREATE OR REPLACE FUNCTION update_historia_unificada_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_historia_unificada_updated_at
    BEFORE UPDATE ON historia_clinica_unificada
    FOR EACH ROW
    EXECUTE FUNCTION update_historia_unificada_updated_at();

-- ==================== DATOS DE EJEMPLO ====================

-- Instituciones externas de ejemplo
INSERT INTO instituciones_externas (nombre, codigo_institucional, nivel_atencion, tipo_institucion, pais, estado, ciudad, activa, protocolos_soportados, versiones_fhir)
VALUES 
    ('Hospital General de México', 'HGM-001', 'terciario', 'publico', 'México', 'Ciudad de México', 'Ciudad de México', TRUE, ARRAY['FHIR_R4', 'HL7V2'], ARRAY['4.0.1']),
    ('Instituto Nacional de Cardiología', 'INC-002', 'especializado', 'publico', 'México', 'Ciudad de México', 'Ciudad de México', TRUE, ARRAY['FHIR_R4'], ARRAY['4.0.1']),
    ('Hospital ABC', 'ABC-003', 'terciario', 'privado', 'México', 'Ciudad de México', 'Ciudad de México', TRUE, ARRAY['FHIR_R4', 'REST_API'], ARRAY['4.0.1', '5.0.0']),
    ('Centro de Salud Comunitario Norte', 'CSC-004', 'primario', 'publico', 'México', 'Nuevo León', 'Monterrey', TRUE, ARRAY['FHIR_R4'], ARRAY['4.0.1']),
    ('Clínica Especializada del Bajío', 'CEB-005', 'secundario', 'privado', 'México', 'Guanajuato', 'León', TRUE, ARRAY['FHIR_R4'], ARRAY['4.0.1'])
ON CONFLICT (codigo_institucional) DO NOTHING;

-- Mapeos de códigos comunes
INSERT INTO mapeo_codigos (sistema_origen, codigo_origen, descripcion_origen, sistema_destino, codigo_destino, descripcion_destino, tipo_concepto, equivalencia, validado)
VALUES
    ('CIE-10', 'E11', 'Diabetes mellitus tipo 2', 'SNOMED-CT', '44054006', 'Type 2 diabetes mellitus', 'diagnostico', 'exacta', TRUE),
    ('CIE-10', 'I10', 'Hipertensión esencial (primaria)', 'SNOMED-CT', '59621000', 'Essential hypertension', 'diagnostico', 'exacta', TRUE),
    ('CIE-10', 'J00', 'Rinofaringitis aguda [resfriado común]', 'SNOMED-CT', '82272006', 'Common cold', 'diagnostico', 'exacta', TRUE),
    ('LOINC', '2345-7', 'Glucosa [Masa/volumen] en Suero o Plasma', 'SNOMED-CT', '33747003', 'Glucose measurement', 'laboratorio', 'exacta', TRUE),
    ('LOINC', '2160-0', 'Creatinina [Masa/volumen] en Suero o Plasma', 'SNOMED-CT', '70901006', 'Creatinine measurement', 'laboratorio', 'exacta', TRUE)
ON CONFLICT (sistema_origen, codigo_origen, sistema_destino) DO NOTHING;

-- ==================== COMENTARIOS ====================

COMMENT ON TABLE instituciones_externas IS 'Registro de instituciones externas en la red nacional de salud';
COMMENT ON TABLE solicitudes_intercambio IS 'Solicitudes de intercambio de información entre instituciones';
COMMENT ON TABLE historia_clinica_unificada IS 'Historia clínica consolidada del paciente con datos de múltiples instituciones';
COMMENT ON TABLE logs_intercambio IS 'Auditoría de todas las operaciones de intercambio';
COMMENT ON TABLE consentimientos_intercambio IS 'Consentimientos de pacientes para compartir información';
COMMENT ON TABLE mapeo_codigos IS 'Mapeo entre diferentes sistemas de codificación (CIE-10, SNOMED-CT, LOINC, etc.)';
