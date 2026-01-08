-- Migración para agregar Multi-Tenancy al sistema
-- Agrega campo institucion_id a todos los modelos principales

-- 1. Crear tabla de instituciones
CREATE TABLE IF NOT EXISTS instituciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    nombre_comercial VARCHAR(255),
    tipo VARCHAR(50) NOT NULL DEFAULT 'clinica',
    razon_social VARCHAR(255),
    rfc VARCHAR(13) UNIQUE,
    registro_sanitario VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(255) NOT NULL,
    sitio_web VARCHAR(255),
    direccion TEXT,
    ciudad VARCHAR(100),
    estado VARCHAR(100),
    codigo_postal VARCHAR(10),
    pais VARCHAR(100) DEFAULT 'México',
    plan VARCHAR(50) NOT NULL DEFAULT 'basico',
    estado_institucion VARCHAR(20) NOT NULL DEFAULT 'prueba',
    fecha_inicio_suscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_fin_prueba TIMESTAMP,
    fecha_renovacion TIMESTAMP,
    max_usuarios INTEGER DEFAULT 5,
    max_pacientes INTEGER DEFAULT 100,
    max_almacenamiento_gb INTEGER DEFAULT 10,
    usuarios_activos INTEGER DEFAULT 0,
    pacientes_registrados INTEGER DEFAULT 0,
    almacenamiento_usado_gb NUMERIC(10, 2) DEFAULT 0,
    configuracion JSONB DEFAULT '{}',
    metodo_pago VARCHAR(50),
    dia_facturacion INTEGER DEFAULT 1,
    moneda VARCHAR(3) DEFAULT 'MXN',
    logo_url VARCHAR(500),
    favicon_url VARCHAR(500),
    color_primario VARCHAR(7) DEFAULT '#1976d2',
    color_secundario VARCHAR(7) DEFAULT '#dc004e',
    ip_permitidas JSONB,
    require_2fa BOOLEAN DEFAULT FALSE,
    sesion_timeout_minutos INTEGER DEFAULT 60,
    notas_internas TEXT,
    activa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Crear tabla de métricas de uso
CREATE TABLE IF NOT EXISTS metricas_uso (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institucion_id UUID NOT NULL,
    fecha TIMESTAMP NOT NULL,
    tipo_periodo VARCHAR(20) DEFAULT 'diario',
    usuarios_activos INTEGER DEFAULT 0,
    pacientes_nuevos INTEGER DEFAULT 0,
    consultas_realizadas INTEGER DEFAULT 0,
    estudios_laboratorio INTEGER DEFAULT 0,
    estudios_imagenes INTEGER DEFAULT 0,
    almacenamiento_gb NUMERIC(10, 2) DEFAULT 0,
    uso_telemedicina_minutos INTEGER DEFAULT 0,
    uso_ia_analisis INTEGER DEFAULT 0,
    mensajes_enviados INTEGER DEFAULT 0,
    reportes_generados INTEGER DEFAULT 0,
    api_calls INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metricas_institucion_fecha ON metricas_uso(institucion_id, fecha);

-- 3. Crear tabla de facturas
CREATE TABLE IF NOT EXISTS facturas_instituciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institucion_id UUID NOT NULL,
    numero_factura VARCHAR(50) UNIQUE NOT NULL,
    fecha_emision TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_vencimiento TIMESTAMP NOT NULL,
    periodo_inicio TIMESTAMP NOT NULL,
    periodo_fin TIMESTAMP NOT NULL,
    subtotal NUMERIC(10, 2) NOT NULL,
    impuestos NUMERIC(10, 2) DEFAULT 0,
    descuentos NUMERIC(10, 2) DEFAULT 0,
    total NUMERIC(10, 2) NOT NULL,
    moneda VARCHAR(3) DEFAULT 'MXN',
    conceptos JSONB,
    estado VARCHAR(20) DEFAULT 'pendiente',
    fecha_pago TIMESTAMP,
    metodo_pago VARCHAR(50),
    referencia_pago VARCHAR(100),
    pdf_url VARCHAR(500),
    xml_url VARCHAR(500),
    notas TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_facturas_institucion ON facturas_instituciones(institucion_id);
CREATE INDEX idx_facturas_estado ON facturas_instituciones(estado);

-- 4. Crear tabla de configuraciones de módulos
CREATE TABLE IF NOT EXISTS configuraciones_modulos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institucion_id UUID NOT NULL,
    modulo VARCHAR(50) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    configuracion JSONB DEFAULT '{}',
    permisos JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_config_modulos_institucion ON configuraciones_modulos(institucion_id);

-- 5. Crear institución por defecto para datos existentes
INSERT INTO instituciones (
    codigo,
    nombre,
    tipo,
    email,
    plan,
    estado_institucion,
    max_usuarios,
    max_pacientes,
    max_almacenamiento_gb
) VALUES (
    'default',
    'Institución Principal',
    'hospital_privado',
    'admin@hospital.com',
    'empresarial',
    'activa',
    999,
    99999,
    1000
) ON CONFLICT (codigo) DO NOTHING;

-- 6. Agregar columna institucion_id a tablas existentes
-- IMPORTANTE: Ajustar según las tablas que existan en tu sistema

-- Usuarios
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS institucion_id UUID;
UPDATE usuarios SET institucion_id = (SELECT id FROM instituciones WHERE codigo = 'default') WHERE institucion_id IS NULL;
CREATE INDEX IF NOT EXISTS idx_usuarios_institucion ON usuarios(institucion_id);

-- Pacientes
ALTER TABLE pacientes ADD COLUMN IF NOT EXISTS institucion_id UUID;
UPDATE pacientes SET institucion_id = (SELECT id FROM instituciones WHERE codigo = 'default') WHERE institucion_id IS NULL;
CREATE INDEX IF NOT EXISTS idx_pacientes_institucion ON pacientes(institucion_id);

-- Citas del portal
ALTER TABLE citas_paciente ADD COLUMN IF NOT EXISTS institucion_id UUID;
UPDATE citas_paciente SET institucion_id = (SELECT id FROM instituciones WHERE codigo = 'default') WHERE institucion_id IS NULL;
CREATE INDEX IF NOT EXISTS idx_citas_paciente_institucion ON citas_paciente(institucion_id);

-- Solicitudes de estudios
ALTER TABLE solicitudes_estudios ADD COLUMN IF NOT EXISTS institucion_id UUID;
UPDATE solicitudes_estudios SET institucion_id = (SELECT id FROM instituciones WHERE codigo = 'default') WHERE institucion_id IS NULL;
CREATE INDEX IF NOT EXISTS idx_solicitudes_estudios_institucion ON solicitudes_estudios(institucion_id);

-- Mensajes
ALTER TABLE mensajes_paciente_medico ADD COLUMN IF NOT EXISTS institucion_id UUID;
UPDATE mensajes_paciente_medico SET institucion_id = (SELECT id FROM instituciones WHERE codigo = 'default') WHERE institucion_id IS NULL;
CREATE INDEX IF NOT EXISTS idx_mensajes_institucion ON mensajes_paciente_medico(institucion_id);

-- Recordatorios de medicamentos
ALTER TABLE recordatorios_medicamentos ADD COLUMN IF NOT EXISTS institucion_id UUID;
UPDATE recordatorios_medicamentos SET institucion_id = (SELECT id FROM instituciones WHERE codigo = 'default') WHERE institucion_id IS NULL;
CREATE INDEX IF NOT EXISTS idx_recordatorios_institucion ON recordatorios_medicamentos(institucion_id);

-- Pruebas de laboratorio
ALTER TABLE pruebas_laboratorio ADD COLUMN IF NOT EXISTS institucion_id UUID;
UPDATE pruebas_laboratorio SET institucion_id = (SELECT id FROM instituciones WHERE codigo = 'default') WHERE institucion_id IS NULL;
CREATE INDEX IF NOT EXISTS idx_pruebas_lab_institucion ON pruebas_laboratorio(institucion_id);

-- Imágenes médicas
ALTER TABLE imagenes_medicas ADD COLUMN IF NOT EXISTS institucion_id UUID;
UPDATE imagenes_medicas SET institucion_id = (SELECT id FROM instituciones WHERE codigo = 'default') WHERE institucion_id IS NULL;
CREATE INDEX IF NOT EXISTS idx_imagenes_institucion ON imagenes_medicas(institucion_id);

-- Consultas remotas
ALTER TABLE consultas_remotas ADD COLUMN IF NOT EXISTS institucion_id UUID;
UPDATE consultas_remotas SET institucion_id = (SELECT id FROM instituciones WHERE codigo = 'default') WHERE institucion_id IS NULL;
CREATE INDEX IF NOT EXISTS idx_consultas_remotas_institucion ON consultas_remotas(institucion_id);

-- 7. Agregar foreign keys (opcional, según preferencias)
-- ALTER TABLE usuarios ADD CONSTRAINT fk_usuarios_institucion FOREIGN KEY (institucion_id) REFERENCES instituciones(id);
-- ALTER TABLE pacientes ADD CONSTRAINT fk_pacientes_institucion FOREIGN KEY (institucion_id) REFERENCES instituciones(id);
-- etc...

-- 8. Crear función para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 9. Crear triggers para updated_at
CREATE TRIGGER update_instituciones_updated_at BEFORE UPDATE ON instituciones
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_facturas_updated_at BEFORE UPDATE ON facturas_instituciones
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_config_modulos_updated_at BEFORE UPDATE ON configuraciones_modulos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 10. Crear vistas útiles para reportes

-- Vista de resumen de instituciones
CREATE OR REPLACE VIEW vista_resumen_instituciones AS
SELECT 
    i.id,
    i.codigo,
    i.nombre,
    i.plan,
    i.estado_institucion,
    i.usuarios_activos,
    i.pacientes_registrados,
    i.almacenamiento_usado_gb,
    i.max_usuarios,
    i.max_pacientes,
    i.max_almacenamiento_gb,
    ROUND((i.usuarios_activos::NUMERIC / i.max_usuarios * 100), 2) as uso_usuarios_pct,
    ROUND((i.pacientes_registrados::NUMERIC / i.max_pacientes * 100), 2) as uso_pacientes_pct,
    ROUND((i.almacenamiento_usado_gb / i.max_almacenamiento_gb * 100), 2) as uso_almacenamiento_pct,
    i.fecha_renovacion,
    CASE 
        WHEN i.fecha_renovacion IS NOT NULL THEN 
            EXTRACT(DAY FROM (i.fecha_renovacion - CURRENT_TIMESTAMP))
        ELSE NULL 
    END as dias_hasta_renovacion
FROM instituciones i;

-- Vista de facturación pendiente
CREATE OR REPLACE VIEW vista_facturacion_pendiente AS
SELECT 
    f.id,
    f.institucion_id,
    i.nombre as institucion_nombre,
    f.numero_factura,
    f.total,
    f.fecha_vencimiento,
    EXTRACT(DAY FROM (CURRENT_TIMESTAMP - f.fecha_vencimiento)) as dias_vencida
FROM facturas_instituciones f
JOIN instituciones i ON f.institucion_id = i.id
WHERE f.estado = 'pendiente'
ORDER BY f.fecha_vencimiento;

COMMIT;
