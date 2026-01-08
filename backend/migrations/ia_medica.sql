-- Migración para módulo de Inteligencia Artificial Médica

-- Tabla de análisis generales de IA
CREATE TABLE IF NOT EXISTS analisis_ia (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    medico_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    
    tipo_analisis VARCHAR(100) NOT NULL,
    contexto JSONB,
    resultado JSONB,
    confianza FLOAT,
    
    modelo_ia VARCHAR(100),
    version_modelo VARCHAR(50),
    tokens_utilizados INTEGER,
    tiempo_procesamiento FLOAT,
    
    validado_por_medico BOOLEAN DEFAULT FALSE,
    fecha_validacion TIMESTAMP,
    notas_medico TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analisis_ia_paciente ON analisis_ia(paciente_id);
CREATE INDEX idx_analisis_ia_medico ON analisis_ia(medico_id);
CREATE INDEX idx_analisis_ia_tipo ON analisis_ia(tipo_analisis);
CREATE INDEX idx_analisis_ia_fecha ON analisis_ia(created_at);

-- Tabla de predicciones de riesgo
CREATE TABLE IF NOT EXISTS predicciones_riesgo (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    medico_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    
    tipo_riesgo VARCHAR(100) NOT NULL,
    nivel_riesgo VARCHAR(50),
    porcentaje_riesgo FLOAT,
    
    factores_riesgo TEXT[],
    factores_protectores TEXT[],
    
    recomendaciones TEXT[],
    estudios_sugeridos TEXT[],
    
    datos_utilizados JSONB,
    algoritmo VARCHAR(100),
    
    valido_hasta TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_predicciones_paciente ON predicciones_riesgo(paciente_id);
CREATE INDEX idx_predicciones_tipo ON predicciones_riesgo(tipo_riesgo);
CREATE INDEX idx_predicciones_valido ON predicciones_riesgo(valido_hasta);

-- Tabla de recomendaciones de tratamiento
CREATE TABLE IF NOT EXISTS recomendaciones_tratamiento (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    medico_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    diagnostico_id UUID,
    
    diagnostico_principal VARCHAR(200),
    codigo_cie10 VARCHAR(10),
    
    medicamentos_sugeridos JSONB,
    terapias_no_farmacologicas TEXT[],
    cambios_estilo_vida TEXT[],
    
    contraindicaciones TEXT[],
    precauciones TEXT[],
    
    evidencia_cientifica JSONB,
    guias_clinicas TEXT[],
    
    prioridad VARCHAR(50),
    
    aplicado BOOLEAN DEFAULT FALSE,
    fecha_aplicacion TIMESTAMP,
    resultado_aplicacion TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_recomendaciones_paciente ON recomendaciones_tratamiento(paciente_id);
CREATE INDEX idx_recomendaciones_diagnostico ON recomendaciones_tratamiento(diagnostico_principal);
CREATE INDEX idx_recomendaciones_aplicado ON recomendaciones_tratamiento(aplicado);

-- Tabla de interacciones medicamentosas
CREATE TABLE IF NOT EXISTS interacciones_medicamentosas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    medico_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    
    medicamentos_analizados TEXT[],
    
    interacciones_encontradas JSONB,
    severidad_maxima VARCHAR(50),
    
    alertas_criticas TEXT[],
    recomendaciones_ajuste TEXT[],
    
    alergias_consideradas TEXT[],
    condiciones_consideradas TEXT[],
    
    fuente_datos VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_interacciones_paciente ON interacciones_medicamentosas(paciente_id);
CREATE INDEX idx_interacciones_severidad ON interacciones_medicamentosas(severidad_maxima);
CREATE INDEX idx_interacciones_fecha ON interacciones_medicamentosas(created_at);

-- Tabla de anomalías detectadas
CREATE TABLE IF NOT EXISTS anomalias_detectadas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    medico_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    
    tipo_estudio VARCHAR(100),
    estudio_id UUID,
    
    tipo_anomalia VARCHAR(100),
    severidad VARCHAR(50),
    
    descripcion TEXT,
    localizacion VARCHAR(200),
    
    valores_anormales JSONB,
    patron_detectado VARCHAR(200),
    
    confianza_deteccion FLOAT,
    requiere_atencion_inmediata BOOLEAN DEFAULT FALSE,
    
    recomendaciones TEXT[],
    estudios_adicionales TEXT[],
    
    revisado_por_medico BOOLEAN DEFAULT FALSE,
    fecha_revision TIMESTAMP,
    confirmado BOOLEAN,
    notas_revision TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_anomalias_paciente ON anomalias_detectadas(paciente_id);
CREATE INDEX idx_anomalias_tipo_estudio ON anomalias_detectadas(tipo_estudio);
CREATE INDEX idx_anomalias_severidad ON anomalias_detectadas(severidad);
CREATE INDEX idx_anomalias_revisado ON anomalias_detectadas(revisado_por_medico);
CREATE INDEX idx_anomalias_urgente ON anomalias_detectadas(requiere_atencion_inmediata);

-- Tabla de asistente de IA
CREATE TABLE IF NOT EXISTS asistente_ia (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    medico_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    paciente_id UUID REFERENCES pacientes(id) ON DELETE CASCADE,
    
    sesion_id UUID DEFAULT gen_random_uuid(),
    
    pregunta TEXT NOT NULL,
    respuesta TEXT NOT NULL,
    
    contexto JSONB,
    tipo_consulta VARCHAR(100),
    
    util BOOLEAN,
    
    modelo_ia VARCHAR(100),
    tokens_utilizados INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_asistente_medico ON asistente_ia(medico_id);
CREATE INDEX idx_asistente_paciente ON asistente_ia(paciente_id);
CREATE INDEX idx_asistente_sesion ON asistente_ia(sesion_id);
CREATE INDEX idx_asistente_fecha ON asistente_ia(created_at);

-- Agregar relaciones a tabla de pacientes (si no existen)
DO $$ 
BEGIN
    -- Estas columnas pueden no existir aún, las agregamos si es necesario
    -- En producción, verificar si ya existen antes de agregar
    NULL;
END $$;
