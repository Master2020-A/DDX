-- Migración: Crear tabla de imágenes médicas
-- Fecha: 2025-12-01
-- Descripción: Sistema de gestión de imágenes médicas con análisis IA

-- Tabla principal de imágenes médicas
CREATE TABLE IF NOT EXISTS imagenes_medicas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id UUID NOT NULL,
    consulta_id UUID,
    usuario_id UUID NOT NULL,
    
    -- Información del archivo
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    url_archivo VARCHAR(500),
    tipo_archivo VARCHAR(50) NOT NULL,
    tamanio_bytes INTEGER NOT NULL,
    
    -- Metadatos médicos
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    tipo_imagen VARCHAR(50) NOT NULL,
    modalidad VARCHAR(50),
    region_anatomica VARCHAR(100),
    lateralidad VARCHAR(20),
    
    -- Dimensiones
    ancho INTEGER,
    alto INTEGER,
    
    -- Metadatos DICOM (si aplica)
    es_dicom BOOLEAN DEFAULT FALSE,
    dicom_metadata JSONB,
    
    -- Análisis con IA
    analisis_ia_completado BOOLEAN DEFAULT FALSE,
    resultados_ia JSONB,
    confianza_ia FLOAT,
    hallazgos TEXT[],
    
    -- Anotaciones
    anotaciones JSONB,
    
    -- Estado y visibilidad
    requiere_revision BOOLEAN DEFAULT FALSE,
    aprobada BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    fecha_adquisicion TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign keys
    CONSTRAINT fk_imagenes_paciente FOREIGN KEY (paciente_id) 
        REFERENCES pacientes(id) ON DELETE CASCADE,
    CONSTRAINT fk_imagenes_consulta FOREIGN KEY (consulta_id) 
        REFERENCES consultas(id) ON DELETE SET NULL,
    CONSTRAINT fk_imagenes_usuario FOREIGN KEY (usuario_id) 
        REFERENCES usuarios(id) ON DELETE RESTRICT
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_imagenes_paciente ON imagenes_medicas(paciente_id);
CREATE INDEX IF NOT EXISTS idx_imagenes_consulta ON imagenes_medicas(consulta_id);
CREATE INDEX IF NOT EXISTS idx_imagenes_tipo ON imagenes_medicas(tipo_imagen);
CREATE INDEX IF NOT EXISTS idx_imagenes_region ON imagenes_medicas(region_anatomica);
CREATE INDEX IF NOT EXISTS idx_imagenes_ia ON imagenes_medicas(analisis_ia_completado);
CREATE INDEX IF NOT EXISTS idx_imagenes_fecha ON imagenes_medicas(created_at DESC);

-- Trigger para actualizar updated_at
CREATE OR REPLACE FUNCTION update_imagenes_medicas_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_imagenes_medicas_updated_at
    BEFORE UPDATE ON imagenes_medicas
    FOR EACH ROW
    EXECUTE FUNCTION update_imagenes_medicas_updated_at();

-- Comentarios para documentación
COMMENT ON TABLE imagenes_medicas IS 'Tabla de imágenes médicas con soporte para análisis IA (CheXNet, MONAI)';
COMMENT ON COLUMN imagenes_medicas.tipo_imagen IS 'Tipo de imagen: rayos_x, tomografia, resonancia, ecografia, fotografia, endoscopia, mamografia';
COMMENT ON COLUMN imagenes_medicas.modalidad IS 'Modalidad DICOM: CR, CT, MR, US, XA, MG, etc.';
COMMENT ON COLUMN imagenes_medicas.hallazgos IS 'Hallazgos detectados por IA (array de strings)';
COMMENT ON COLUMN imagenes_medicas.resultados_ia IS 'Resultados completos del análisis IA en formato JSON';
COMMENT ON COLUMN imagenes_medicas.anotaciones IS 'Anotaciones gráficas en formato JSON (rectangulos, circulos, flechas, texto)';
