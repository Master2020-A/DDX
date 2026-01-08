-- ============================================================================
-- Migración: Catálogos del Sistema
-- Descripción: Tablas de catálogos para código postal, instituciones, etc.
-- ============================================================================

-- Tabla: Códigos Postales
CREATE TABLE IF NOT EXISTS codigos_postales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo_postal VARCHAR(10) NOT NULL UNIQUE,
    pais VARCHAR(100) NOT NULL DEFAULT 'México',
    estado VARCHAR(100) NOT NULL,
    municipio VARCHAR(150) NOT NULL,
    ciudad VARCHAR(150),
    colonia VARCHAR(200),
    activo BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_cp_codigo ON codigos_postales(codigo_postal);
CREATE INDEX IF NOT EXISTS idx_cp_estado ON codigos_postales(estado);

-- Tabla: Instituciones de Salud
CREATE TABLE IF NOT EXISTS instituciones_salud (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(200) NOT NULL,
    tipo VARCHAR(100),
    pais VARCHAR(100) NOT NULL DEFAULT 'México',
    estado VARCHAR(100),
    municipio VARCHAR(150),
    localidad VARCHAR(200),
    direccion VARCHAR(500),
    telefono VARCHAR(20),
    nivel_atencion VARCHAR(50),
    activo BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_inst_pais ON instituciones_salud(pais);
CREATE INDEX IF NOT EXISTS idx_inst_estado ON instituciones_salud(estado);

-- Tabla: Tipos de Parentesco
CREATE TABLE IF NOT EXISTS parentescos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(100) NOT NULL UNIQUE,
    orden INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE
);

-- Tabla: Niveles de Escolaridad
CREATE TABLE IF NOT EXISTS niveles_escolaridad (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(100) NOT NULL,
    pais VARCHAR(100) DEFAULT 'México',
    orden INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE
);

-- Tabla: Tipos de Exámenes de Laboratorio
CREATE TABLE IF NOT EXISTS tipos_examen_laboratorio (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(200) NOT NULL,
    categoria VARCHAR(100),
    descripcion VARCHAR(500),
    orden INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE
);

-- Tabla: Sustancias Tóxicas
CREATE TABLE IF NOT EXISTS sustancias_toxicas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(200) NOT NULL UNIQUE,
    categoria VARCHAR(100),
    descripcion VARCHAR(500),
    nivel_peligrosidad VARCHAR(50),
    orden INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE
);

-- Comentarios
COMMENT ON TABLE codigos_postales IS 'Catálogo de códigos postales con información geográfica';
COMMENT ON TABLE instituciones_salud IS 'Catálogo de instituciones de salud por región';
COMMENT ON TABLE parentescos IS 'Catálogo de tipos de parentesco';
COMMENT ON TABLE niveles_escolaridad IS 'Catálogo de niveles educativos';
COMMENT ON TABLE tipos_examen_laboratorio IS 'Catálogo de tipos de exámenes médicos';
COMMENT ON TABLE sustancias_toxicas IS 'Catálogo de sustancias tóxicas conocidas';
