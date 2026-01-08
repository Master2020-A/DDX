-- Script SQL para crear tablas del módulo de Procesamiento de Lenguaje Natural (PLN)
-- Ejecutar este script en PostgreSQL

-- 1. Tabla de transcripciones de voz
CREATE TABLE IF NOT EXISTS transcripciones_voz (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id UUID REFERENCES pacientes(id),
    medico_id UUID NOT NULL REFERENCES usuarios(id),
    consulta_id UUID REFERENCES consultas(id),
    
    -- Datos del audio
    archivo_audio VARCHAR(500),
    duracion_segundos FLOAT,
    formato_audio VARCHAR(50),
    
    -- Transcripción
    texto_transcrito TEXT NOT NULL,
    idioma_detectado VARCHAR(10),
    confianza FLOAT,
    
    -- Metadatos
    modelo_utilizado VARCHAR(100),
    tiempo_procesamiento FLOAT,
    
    -- Información extraída (opcional)
    informacion_extraida JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. Tabla de extracción de información
CREATE TABLE IF NOT EXISTS extracciones_informacion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id UUID REFERENCES pacientes(id),
    medico_id UUID NOT NULL REFERENCES usuarios(id),
    consulta_id UUID REFERENCES consultas(id),
    transcripcion_id UUID REFERENCES transcripciones_voz(id),
    
    -- Texto fuente
    texto_original TEXT NOT NULL,
    tipo_documento VARCHAR(100),
    
    -- Información extraída
    sintomas JSONB,
    diagnosticos JSONB,
    medicamentos JSONB,
    procedimientos JSONB,
    signos_vitales JSONB,
    antecedentes JSONB,
    alergias JSONB,
    
    -- Entidades nombradas
    entidades_medicas JSONB,
    
    -- Metadatos
    modelo_utilizado VARCHAR(100),
    confianza_promedio FLOAT,
    tiempo_procesamiento FLOAT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3. Tabla de resúmenes clínicos
CREATE TABLE IF NOT EXISTS resumenes_clinicos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id UUID NOT NULL REFERENCES pacientes(id),
    medico_id UUID NOT NULL REFERENCES usuarios(id),
    
    -- Configuración del resumen
    tipo_resumen VARCHAR(100),
    periodo_inicio TIMESTAMP,
    periodo_fin TIMESTAMP,
    
    -- Fuentes incluidas
    incluye_consultas BOOLEAN DEFAULT TRUE,
    incluye_laboratorios BOOLEAN DEFAULT TRUE,
    incluye_imagenes BOOLEAN DEFAULT TRUE,
    incluye_medicamentos BOOLEAN DEFAULT TRUE,
    
    -- Resumen generado
    resumen_texto TEXT NOT NULL,
    resumen_estructurado JSONB,
    
    -- Secciones del resumen
    datos_demograficos JSONB,
    motivo_consulta_principal TEXT,
    antecedentes_relevantes JSONB,
    evolucion_clinica TEXT,
    diagnosticos_actuales JSONB,
    tratamiento_actual JSONB,
    estudios_pendientes JSONB,
    plan_seguimiento TEXT,
    
    -- Metadatos
    numero_documentos_analizados INTEGER,
    modelo_utilizado VARCHAR(100),
    tiempo_procesamiento FLOAT,
    
    -- Control de versiones
    version INTEGER DEFAULT 1,
    es_version_actual BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 4. Tabla de traducciones médicas
CREATE TABLE IF NOT EXISTS traducciones_medicas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    medico_id UUID REFERENCES usuarios(id),
    
    -- Texto original
    texto_original TEXT NOT NULL,
    idioma_origen VARCHAR(10) NOT NULL,
    
    -- Traducción
    texto_traducido TEXT NOT NULL,
    idioma_destino VARCHAR(10) NOT NULL,
    
    -- Tipo de traducción
    tipo_contenido VARCHAR(100),
    especialidad VARCHAR(100),
    
    -- Terminología médica identificada
    terminos_medicos_origen JSONB,
    terminos_medicos_destino JSONB,
    
    -- Alternativas y sinónimos
    traducciones_alternativas JSONB,
    sinonimos JSONB,
    
    -- Contexto adicional
    definicion TEXT,
    notas_clinicas TEXT,
    
    -- Metadatos
    modelo_utilizado VARCHAR(100),
    confianza FLOAT,
    tiempo_procesamiento FLOAT,
    
    -- Validación
    validado_por_medico BOOLEAN DEFAULT FALSE,
    fecha_validacion TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- 5. Tabla de diccionario médico
CREATE TABLE IF NOT EXISTS diccionario_medico (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Término principal
    termino_es VARCHAR(500),
    termino_en VARCHAR(500),
    termino_la VARCHAR(500),
    
    -- Clasificación
    categoria VARCHAR(100),
    especialidad VARCHAR(100),
    
    -- Definiciones
    definicion_es TEXT,
    definicion_en TEXT,
    
    -- Sinónimos
    sinonimos_es JSONB,
    sinonimos_en JSONB,
    
    -- Abreviaturas
    abreviaturas JSONB,
    
    -- Códigos estándar
    codigo_cie10 VARCHAR(20),
    codigo_snomed VARCHAR(50),
    codigo_loinc VARCHAR(50),
    
    -- Uso clínico
    frecuencia_uso INTEGER DEFAULT 0,
    
    -- Metadatos
    fuente VARCHAR(200),
    verificado BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_transcripciones_paciente ON transcripciones_voz(paciente_id);
CREATE INDEX IF NOT EXISTS idx_transcripciones_medico ON transcripciones_voz(medico_id);
CREATE INDEX IF NOT EXISTS idx_transcripciones_fecha ON transcripciones_voz(created_at);

CREATE INDEX IF NOT EXISTS idx_extracciones_paciente ON extracciones_informacion(paciente_id);
CREATE INDEX IF NOT EXISTS idx_extracciones_medico ON extracciones_informacion(medico_id);
CREATE INDEX IF NOT EXISTS idx_extracciones_tipo ON extracciones_informacion(tipo_documento);

CREATE INDEX IF NOT EXISTS idx_resumenes_paciente ON resumenes_clinicos(paciente_id);
CREATE INDEX IF NOT EXISTS idx_resumenes_medico ON resumenes_clinicos(medico_id);
CREATE INDEX IF NOT EXISTS idx_resumenes_tipo ON resumenes_clinicos(tipo_resumen);
CREATE INDEX IF NOT EXISTS idx_resumenes_version ON resumenes_clinicos(es_version_actual);

CREATE INDEX IF NOT EXISTS idx_traducciones_medico ON traducciones_medicas(medico_id);
CREATE INDEX IF NOT EXISTS idx_traducciones_idiomas ON traducciones_medicas(idioma_origen, idioma_destino);

CREATE INDEX IF NOT EXISTS idx_diccionario_termino_es ON diccionario_medico(termino_es);
CREATE INDEX IF NOT EXISTS idx_diccionario_termino_en ON diccionario_medico(termino_en);
CREATE INDEX IF NOT EXISTS idx_diccionario_categoria ON diccionario_medico(categoria);
CREATE INDEX IF NOT EXISTS idx_diccionario_especialidad ON diccionario_medico(especialidad);

-- Verificar tablas creadas
SELECT 
    'transcripciones_voz' as tabla,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_name = 'transcripciones_voz'
ORDER BY ordinal_position;

SELECT 
    'extracciones_informacion' as tabla,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_name = 'extracciones_informacion'
ORDER BY ordinal_position;

SELECT 
    'resumenes_clinicos' as tabla,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_name = 'resumenes_clinicos'
ORDER BY ordinal_position;

SELECT 
    'traducciones_medicas' as tabla,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_name = 'traducciones_medicas'
ORDER BY ordinal_position;

SELECT 
    'diccionario_medico' as tabla,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_name = 'diccionario_medico'
ORDER BY ordinal_position;

-- Fin del script
