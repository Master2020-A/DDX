-- Sistema de Gestión Clínica - Esquema de Base de Datos
-- PostgreSQL 15+

-- Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Tabla de usuarios del sistema (médicos, enfermeros, administradores)
CREATE TABLE usuarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(255) NOT NULL,
    rol VARCHAR(50) NOT NULL CHECK (rol IN ('medico', 'enfermero', 'administrativo', 'especialista', 'admin')),
    especialidad VARCHAR(100),
    cedula_profesional VARCHAR(50),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de pacientes
CREATE TABLE pacientes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    numero_expediente VARCHAR(50) UNIQUE NOT NULL,
    nombre_completo VARCHAR(255) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    genero VARCHAR(20) CHECK (genero IN ('masculino', 'femenino', 'otro', 'no_especifica')),
    tipo_sangre VARCHAR(5),
    telefono VARCHAR(20),
    email VARCHAR(255),
    direccion TEXT,
    contacto_emergencia_nombre VARCHAR(255),
    contacto_emergencia_telefono VARCHAR(20),
    alergias TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de consultas/visitas
CREATE TABLE consultas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    medico_id UUID NOT NULL REFERENCES usuarios(id),
    fecha_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tipo_consulta VARCHAR(50) CHECK (tipo_consulta IN ('primera_vez', 'seguimiento', 'urgencia', 'interconsulta')),
    motivo_consulta TEXT NOT NULL,
    sintomas TEXT[] NOT NULL,
    estado VARCHAR(50) DEFAULT 'en_proceso' CHECK (estado IN ('en_proceso', 'completada', 'hospitalizado', 'alta')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de expedientes clínicos (historial médico detallado)
CREATE TABLE expedientes_clinicos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    consulta_id UUID REFERENCES consultas(id),
    antecedentes_personales TEXT,
    antecedentes_familiares TEXT,
    padecimientos_cronicos TEXT[],
    cirugias_previas TEXT[],
    medicamentos_actuales TEXT[],
    habitos TEXT,
    signos_vitales JSONB,  -- {temperatura, presion_arterial, frecuencia_cardiaca, etc}
    exploracion_fisica TEXT,
    notas TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de pre-diagnósticos e hipótesis
CREATE TABLE diagnosticos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    consulta_id UUID NOT NULL REFERENCES consultas(id) ON DELETE CASCADE,
    medico_id UUID NOT NULL REFERENCES usuarios(id),
    tipo VARCHAR(50) CHECK (tipo IN ('pre_diagnostico', 'diagnostico_presuntivo', 'diagnostico_confirmado', 'diagnostico_diferencial')),
    codigo_cie10 VARCHAR(10),
    descripcion TEXT NOT NULL,
    confianza_nivel VARCHAR(20) CHECK (confianza_nivel IN ('bajo', 'medio', 'alto', 'confirmado')),
    justificacion TEXT,
    evidencias TEXT[],
    estado VARCHAR(50) DEFAULT 'activo' CHECK (estado IN ('activo', 'descartado', 'confirmado')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de pruebas/estudios solicitados
CREATE TABLE pruebas_medicas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    consulta_id UUID NOT NULL REFERENCES consultas(id) ON DELETE CASCADE,
    diagnostico_id UUID REFERENCES diagnosticos(id),
    tipo_prueba VARCHAR(50) CHECK (tipo_prueba IN ('laboratorio', 'imagen', 'biopsia', 'electrocardiograma', 'otro')),
    nombre_prueba VARCHAR(255) NOT NULL,
    descripcion TEXT,
    urgencia VARCHAR(20) CHECK (urgencia IN ('normal', 'urgente', 'emergencia')),
    estado VARCHAR(50) DEFAULT 'solicitada' CHECK (estado IN ('solicitada', 'en_proceso', 'completada', 'cancelada')),
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_programada TIMESTAMP,
    fecha_realizada TIMESTAMP,
    solicitado_por UUID NOT NULL REFERENCES usuarios(id),
    laboratorio_externo VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de resultados de pruebas
CREATE TABLE resultados_pruebas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prueba_id UUID NOT NULL REFERENCES pruebas_medicas(id) ON DELETE CASCADE,
    resultado_texto TEXT,
    resultado_numerico DECIMAL,
    unidad_medida VARCHAR(50),
    valores_referencia VARCHAR(255),
    interpretacion TEXT,
    anormal BOOLEAN DEFAULT FALSE,
    archivo_url TEXT,  -- URL del archivo (imagen, PDF, etc.)
    archivo_tipo VARCHAR(50),
    notas TEXT,
    registrado_por UUID REFERENCES usuarios(id),
    fecha_resultado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de archivos/imágenes médicas
CREATE TABLE archivos_medicos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    consulta_id UUID REFERENCES consultas(id),
    prueba_id UUID REFERENCES pruebas_medicas(id),
    tipo_archivo VARCHAR(50) CHECK (tipo_archivo IN ('imagen', 'documento', 'laboratorio', 'radiografia', 'ecografia', 'tomografia', 'resonancia')),
    nombre_archivo VARCHAR(255) NOT NULL,
    url_archivo TEXT NOT NULL,
    tamano_bytes BIGINT,
    mime_type VARCHAR(100),
    descripcion TEXT,
    subido_por UUID NOT NULL REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de tratamientos
CREATE TABLE tratamientos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    consulta_id UUID NOT NULL REFERENCES consultas(id) ON DELETE CASCADE,
    diagnostico_id UUID REFERENCES diagnosticos(id),
    tipo_tratamiento VARCHAR(50) CHECK (tipo_tratamiento IN ('farmacologico', 'fisico', 'paliativo', 'quirurgico', 'psicologico', 'otro')),
    descripcion TEXT NOT NULL,
    objetivo TEXT,
    duracion_dias INTEGER,
    fecha_inicio DATE,
    fecha_fin DATE,
    estado VARCHAR(50) DEFAULT 'activo' CHECK (estado IN ('activo', 'completado', 'suspendido', 'modificado')),
    prescrito_por UUID NOT NULL REFERENCES usuarios(id),
    notas TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de prescripciones farmacológicas
CREATE TABLE prescripciones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tratamiento_id UUID NOT NULL REFERENCES tratamientos(id) ON DELETE CASCADE,
    medicamento VARCHAR(255) NOT NULL,
    principio_activo VARCHAR(255),
    dosis VARCHAR(100) NOT NULL,
    frecuencia VARCHAR(100) NOT NULL,
    via_administracion VARCHAR(50),
    duracion_dias INTEGER,
    cantidad_total VARCHAR(50),
    instrucciones_especiales TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de interconsultas
CREATE TABLE interconsultas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    consulta_id UUID NOT NULL REFERENCES consultas(id) ON DELETE CASCADE,
    medico_solicitante_id UUID NOT NULL REFERENCES usuarios(id),
    especialista_id UUID REFERENCES usuarios(id),
    especialidad_requerida VARCHAR(100) NOT NULL,
    motivo TEXT NOT NULL,
    urgencia VARCHAR(20) CHECK (urgencia IN ('normal', 'urgente', 'emergencia')),
    estado VARCHAR(50) DEFAULT 'solicitada' CHECK (estado IN ('solicitada', 'aceptada', 'en_proceso', 'completada', 'rechazada')),
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_programada TIMESTAMP,
    fecha_realizada TIMESTAMP,
    diagnostico_especialista TEXT,
    recomendaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de seguimientos interdisciplinarios
CREATE TABLE seguimientos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    consulta_id UUID REFERENCES consultas(id),
    responsable_id UUID NOT NULL REFERENCES usuarios(id),
    tipo_seguimiento VARCHAR(50) CHECK (tipo_seguimiento IN ('medico', 'enfermeria', 'fisioterapia', 'nutricion', 'psicologia', 'trabajo_social')),
    fecha_seguimiento TIMESTAMP NOT NULL,
    evolucion TEXT NOT NULL,
    plan_accion TEXT,
    proxima_cita DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de hospitalizaciones
CREATE TABLE hospitalizaciones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    consulta_id UUID REFERENCES consultas(id),
    medico_responsable_id UUID NOT NULL REFERENCES usuarios(id),
    fecha_ingreso TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_alta TIMESTAMP,
    motivo_ingreso TEXT NOT NULL,
    diagnostico_ingreso TEXT NOT NULL,
    diagnostico_egreso TEXT,
    area_hospitalizacion VARCHAR(100),
    numero_cama VARCHAR(20),
    estado VARCHAR(50) DEFAULT 'activo' CHECK (estado IN ('activo', 'alta_medica', 'alta_voluntaria', 'defuncion', 'traslado')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de notas médicas (evoluciones diarias, notas de alta, etc.)
CREATE TABLE notas_medicas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    consulta_id UUID REFERENCES consultas(id),
    hospitalizacion_id UUID REFERENCES hospitalizaciones(id),
    autor_id UUID NOT NULL REFERENCES usuarios(id),
    tipo_nota VARCHAR(50) CHECK (tipo_nota IN ('evolucion', 'ingreso', 'alta', 'interconsulta', 'procedimiento', 'defuncion')),
    titulo VARCHAR(255) NOT NULL,
    contenido TEXT NOT NULL,
    fecha_nota TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    firmada BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de auditoría
CREATE TABLE auditoria (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID REFERENCES usuarios(id),
    accion VARCHAR(100) NOT NULL,
    tabla_afectada VARCHAR(100),
    registro_id UUID,
    datos_anteriores JSONB,
    datos_nuevos JSONB,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para optimizar consultas
CREATE INDEX idx_pacientes_expediente ON pacientes(numero_expediente);
CREATE INDEX idx_consultas_paciente ON consultas(paciente_id);
CREATE INDEX idx_consultas_medico ON consultas(medico_id);
CREATE INDEX idx_consultas_fecha ON consultas(fecha_hora);
CREATE INDEX idx_diagnosticos_consulta ON diagnosticos(consulta_id);
CREATE INDEX idx_pruebas_consulta ON pruebas_medicas(consulta_id);
CREATE INDEX idx_resultados_prueba ON resultados_pruebas(prueba_id);
CREATE INDEX idx_tratamientos_consulta ON tratamientos(consulta_id);
CREATE INDEX idx_interconsultas_consulta ON interconsultas(consulta_id);
CREATE INDEX idx_seguimientos_paciente ON seguimientos(paciente_id);
CREATE INDEX idx_hospitalizaciones_paciente ON hospitalizaciones(paciente_id);
CREATE INDEX idx_notas_paciente ON notas_medicas(paciente_id);
CREATE INDEX idx_archivos_paciente ON archivos_medicos(paciente_id);

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para updated_at
CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pacientes_updated_at BEFORE UPDATE ON pacientes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_consultas_updated_at BEFORE UPDATE ON consultas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_expedientes_updated_at BEFORE UPDATE ON expedientes_clinicos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_diagnosticos_updated_at BEFORE UPDATE ON diagnosticos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pruebas_updated_at BEFORE UPDATE ON pruebas_medicas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tratamientos_updated_at BEFORE UPDATE ON tratamientos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_interconsultas_updated_at BEFORE UPDATE ON interconsultas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_hospitalizaciones_updated_at BEFORE UPDATE ON hospitalizaciones
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comentarios en tablas
COMMENT ON TABLE pacientes IS 'Información demográfica y de contacto de pacientes';
COMMENT ON TABLE consultas IS 'Registro de consultas médicas y visitas';
COMMENT ON TABLE expedientes_clinicos IS 'Historia clínica detallada del paciente';
COMMENT ON TABLE diagnosticos IS 'Diagnósticos, pre-diagnósticos e hipótesis médicas';
COMMENT ON TABLE pruebas_medicas IS 'Estudios y pruebas solicitadas';
COMMENT ON TABLE tratamientos IS 'Tratamientos prescritos';
COMMENT ON TABLE interconsultas IS 'Solicitudes de interconsulta con especialistas';
COMMENT ON TABLE hospitalizaciones IS 'Registro de hospitalizaciones';
COMMENT ON TABLE notas_medicas IS 'Notas médicas, evoluciones y notas de alta';
