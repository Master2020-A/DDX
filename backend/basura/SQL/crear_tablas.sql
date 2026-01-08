-- Script SQL para crear tablas de Hospitalización e Interconsultas
-- Ejecutar en PostgreSQL

-- ==================== CAMAS ====================
CREATE TABLE IF NOT EXISTS camas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_cama VARCHAR NOT NULL UNIQUE,
    area VARCHAR NOT NULL,
    piso VARCHAR,
    habitacion VARCHAR,
    estado VARCHAR NOT NULL DEFAULT 'disponible',
    tipo_cama VARCHAR,
    tiene_oxigeno BOOLEAN NOT NULL DEFAULT FALSE,
    tiene_monitor BOOLEAN NOT NULL DEFAULT FALSE,
    tiene_ventilador BOOLEAN NOT NULL DEFAULT FALSE,
    capacidad_peso FLOAT,
    hospitalizacion_actual_id UUID,
    fecha_ultima_limpieza TIMESTAMP WITH TIME ZONE,
    fecha_ultimo_mantenimiento TIMESTAMP WITH TIME ZONE,
    observaciones TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_camas_estado ON camas(estado);
CREATE INDEX IF NOT EXISTS ix_camas_area ON camas(area);

-- ==================== HOSPITALIZACIONES ====================
CREATE TABLE IF NOT EXISTS hospitalizaciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    consulta_id UUID REFERENCES consultas(id) ON DELETE SET NULL,
    medico_responsable_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
    fecha_ingreso TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    fecha_alta TIMESTAMP WITH TIME ZONE,
    motivo_ingreso TEXT NOT NULL,
    diagnostico_ingreso TEXT NOT NULL,
    diagnostico_egreso TEXT,
    resumen_clinico TEXT,
    area_hospitalizacion VARCHAR,
    numero_cama VARCHAR,
    piso VARCHAR,
    estado VARCHAR NOT NULL DEFAULT 'activo',
    prioridad VARCHAR NOT NULL DEFAULT 'normal',
    tipo_ingreso VARCHAR,
    alergias_conocidas VARCHAR[],
    antecedentes_relevantes TEXT,
    tratamiento_actual TEXT,
    tipo_seguro VARCHAR,
    numero_poliza VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_hospitalizaciones_paciente_id ON hospitalizaciones(paciente_id);
CREATE INDEX IF NOT EXISTS ix_hospitalizaciones_estado ON hospitalizaciones(estado);
CREATE INDEX IF NOT EXISTS ix_hospitalizaciones_fecha_ingreso ON hospitalizaciones(fecha_ingreso);

-- ==================== NOTAS DE EVOLUCIÓN ====================
CREATE TABLE IF NOT EXISTS notas_evolucion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hospitalizacion_id UUID NOT NULL REFERENCES hospitalizaciones(id) ON DELETE CASCADE,
    medico_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
    fecha_nota TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    tipo_nota VARCHAR NOT NULL DEFAULT 'evolucion',
    turno VARCHAR,
    subjetivo TEXT,
    objetivo TEXT,
    temperatura FLOAT,
    presion_arterial_sistolica INTEGER,
    presion_arterial_diastolica INTEGER,
    frecuencia_cardiaca INTEGER,
    frecuencia_respiratoria INTEGER,
    saturacion_oxigeno FLOAT,
    evaluacion TEXT,
    plan TEXT,
    estudios_solicitados VARCHAR[],
    procedimientos_realizados VARCHAR[],
    estado_general VARCHAR,
    nivel_conciencia VARCHAR,
    observaciones TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_notas_evolucion_hospitalizacion_id ON notas_evolucion(hospitalizacion_id);
CREATE INDEX IF NOT EXISTS ix_notas_evolucion_fecha_nota ON notas_evolucion(fecha_nota);

-- ==================== INDICACIONES MÉDICAS ====================
CREATE TABLE IF NOT EXISTS indicaciones_medicas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hospitalizacion_id UUID NOT NULL REFERENCES hospitalizaciones(id) ON DELETE CASCADE,
    medico_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
    fecha_indicacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    tipo_indicacion VARCHAR NOT NULL,
    descripcion TEXT NOT NULL,
    dosis VARCHAR,
    via_administracion VARCHAR,
    frecuencia VARCHAR,
    duracion VARCHAR,
    prioridad VARCHAR NOT NULL DEFAULT 'normal',
    estado VARCHAR NOT NULL DEFAULT 'activa',
    fecha_inicio TIMESTAMP WITH TIME ZONE,
    fecha_fin TIMESTAMP WITH TIME ZONE,
    fecha_suspension TIMESTAMP WITH TIME ZONE,
    motivo_suspension TEXT,
    observaciones TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_indicaciones_medicas_hospitalizacion_id ON indicaciones_medicas(hospitalizacion_id);
CREATE INDEX IF NOT EXISTS ix_indicaciones_medicas_estado ON indicaciones_medicas(estado);

-- ==================== NOTAS DE ALTA ====================
CREATE TABLE IF NOT EXISTS notas_alta (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hospitalizacion_id UUID NOT NULL UNIQUE REFERENCES hospitalizaciones(id) ON DELETE CASCADE,
    medico_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
    fecha_alta TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    tipo_alta VARCHAR NOT NULL,
    motivo_ingreso TEXT NOT NULL,
    resumen_evolucion TEXT NOT NULL,
    diagnostico_egreso TEXT NOT NULL,
    procedimientos_realizados TEXT,
    complicaciones TEXT,
    condicion_egreso VARCHAR,
    estado_funcional VARCHAR,
    medicamentos_egreso TEXT,
    dieta_recomendada TEXT,
    cuidados_domiciliarios TEXT,
    restricciones TEXT,
    fecha_control TIMESTAMP WITH TIME ZONE,
    especialidad_control VARCHAR,
    estudios_pendientes VARCHAR[],
    pronostico VARCHAR,
    observaciones TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_notas_alta_fecha_alta ON notas_alta(fecha_alta);

-- ==================== INTERCONSULTAS ====================
CREATE TABLE IF NOT EXISTS interconsultas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    consulta_id UUID REFERENCES consultas(id) ON DELETE SET NULL,
    hospitalizacion_id UUID REFERENCES hospitalizaciones(id) ON DELETE SET NULL,
    medico_solicitante_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
    especialista_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    especialidad_requerida VARCHAR(100) NOT NULL,
    motivo_solicitud TEXT NOT NULL,
    antecedentes_relevantes TEXT,
    estudios_adjuntos VARCHAR[],
    urgencia VARCHAR(20) NOT NULL DEFAULT 'normal',
    estado VARCHAR(50) NOT NULL DEFAULT 'solicitada',
    fecha_solicitud TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    fecha_aceptacion TIMESTAMP WITH TIME ZONE,
    fecha_programada TIMESTAMP WITH TIME ZONE,
    fecha_realizada TIMESTAMP WITH TIME ZONE,
    fecha_completada TIMESTAMP WITH TIME ZONE,
    diagnostico_especialista TEXT,
    hallazgos TEXT,
    recomendaciones TEXT,
    plan_tratamiento TEXT,
    requiere_seguimiento BOOLEAN DEFAULT FALSE,
    fecha_seguimiento TIMESTAMP WITH TIME ZONE,
    motivo_rechazo TEXT,
    prioridad_clinica INTEGER DEFAULT 1,
    notas_internas TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_interconsultas_paciente_id ON interconsultas(paciente_id);
CREATE INDEX IF NOT EXISTS ix_interconsultas_consulta_id ON interconsultas(consulta_id);
CREATE INDEX IF NOT EXISTS ix_interconsultas_estado ON interconsultas(estado);
CREATE INDEX IF NOT EXISTS ix_interconsultas_especialidad ON interconsultas(especialidad_requerida);
CREATE INDEX IF NOT EXISTS ix_interconsultas_fecha_solicitud ON interconsultas(fecha_solicitud);

-- ==================== NOTIFICACIONES INTERCONSULTA ====================
CREATE TABLE IF NOT EXISTS notificaciones_interconsulta (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interconsulta_id UUID NOT NULL REFERENCES interconsultas(id) ON DELETE CASCADE,
    medico_destinatario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    tipo VARCHAR(50) NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    mensaje TEXT NOT NULL,
    leida BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_lectura TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_notificaciones_interconsulta_id ON notificaciones_interconsulta(interconsulta_id);
CREATE INDEX IF NOT EXISTS ix_notificaciones_medico_id ON notificaciones_interconsulta(medico_destinatario_id);
CREATE INDEX IF NOT EXISTS ix_notificaciones_leida ON notificaciones_interconsulta(leida);

-- ==================== MENSAJES INTERCONSULTA ====================
CREATE TABLE IF NOT EXISTS mensajes_interconsulta (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interconsulta_id UUID NOT NULL REFERENCES interconsultas(id) ON DELETE CASCADE,
    medico_emisor_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    mensaje TEXT NOT NULL,
    archivos_adjuntos VARCHAR[],
    leido BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_lectura TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_mensajes_interconsulta_id ON mensajes_interconsulta(interconsulta_id);
CREATE INDEX IF NOT EXISTS ix_mensajes_created_at ON mensajes_interconsulta(created_at);

-- ==================== SEGUIMIENTOS INTERCONSULTA ====================
CREATE TABLE IF NOT EXISTS seguimientos_interconsulta (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interconsulta_id UUID NOT NULL REFERENCES interconsultas(id) ON DELETE CASCADE,
    medico_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    tipo_seguimiento VARCHAR(50) NOT NULL,
    observaciones TEXT NOT NULL,
    estado_paciente VARCHAR(100),
    cambios_tratamiento TEXT,
    proxima_revision TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_seguimientos_interconsulta_id ON seguimientos_interconsulta(interconsulta_id);

-- Mensaje final
SELECT 'Tablas creadas exitosamente!' AS resultado;
