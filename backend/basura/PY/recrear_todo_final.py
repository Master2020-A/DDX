"""Script final para recrear todas las tablas correctamente"""
import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def main():
    print("\n" + "="*70)
    print("🔧 RECREANDO TODAS LAS TABLAS - VERSIÓN FINAL")
    print("="*70 + "\n")
    
    async with AsyncSessionLocal() as db:
        try:
            # 1. Eliminar tablas existentes
            print("1. Eliminando tablas existentes...")
            await db.execute(text("""
                DROP TABLE IF EXISTS seguimientos_interconsulta CASCADE;
                DROP TABLE IF EXISTS mensajes_interconsulta CASCADE;
                DROP TABLE IF EXISTS notificaciones_interconsulta CASCADE;
                DROP TABLE IF EXISTS interconsultas CASCADE;
                DROP TABLE IF EXISTS notas_alta CASCADE;
                DROP TABLE IF EXISTS indicaciones_medicas CASCADE;
                DROP TABLE IF EXISTS notas_evolucion CASCADE;
                DROP TABLE IF EXISTS hospitalizaciones CASCADE;
                DROP TABLE IF EXISTS camas CASCADE;
            """))
            await db.commit()
            print("   ✅ Tablas eliminadas\n")
            
            # 2. Crear tablas de hospitalización
            print("2. Creando tablas de hospitalización...")
            await db.execute(text("""
                -- CAMAS
                CREATE TABLE camas (
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
                CREATE INDEX ix_camas_estado ON camas(estado);
                CREATE INDEX ix_camas_area ON camas(area);
                
                -- HOSPITALIZACIONES (SIN resumen_clinico)
                CREATE TABLE hospitalizaciones (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
                    consulta_id UUID REFERENCES consultas(id) ON DELETE SET NULL,
                    medico_responsable_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
                    fecha_ingreso TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    fecha_alta TIMESTAMP WITH TIME ZONE,
                    motivo_ingreso TEXT NOT NULL,
                    diagnostico_ingreso TEXT NOT NULL,
                    diagnostico_egreso TEXT,
                    area_hospitalizacion VARCHAR(100),
                    numero_cama VARCHAR(20),
                    piso VARCHAR(20),
                    estado VARCHAR(50) NOT NULL DEFAULT 'activo',
                    prioridad VARCHAR(20) NOT NULL DEFAULT 'normal',
                    tipo_ingreso VARCHAR(50),
                    alergias_conocidas VARCHAR[],
                    antecedentes_relevantes TEXT,
                    tratamiento_actual TEXT,
                    tipo_seguro VARCHAR(100),
                    numero_poliza VARCHAR(100),
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                );
                CREATE INDEX ix_hospitalizaciones_paciente_id ON hospitalizaciones(paciente_id);
                CREATE INDEX ix_hospitalizaciones_estado ON hospitalizaciones(estado);
                
                -- NOTAS EVOLUCIÓN
                CREATE TABLE notas_evolucion (
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
                
                -- INDICACIONES MÉDICAS
                CREATE TABLE indicaciones_medicas (
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
                
                -- NOTAS ALTA
                CREATE TABLE notas_alta (
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
            """))
            await db.commit()
            print("   ✅ Tablas de hospitalización creadas\n")
            
            # 3. Crear tablas de interconsultas
            print("3. Creando tablas de interconsultas...")
            await db.execute(text("""
                -- INTERCONSULTAS
                CREATE TABLE interconsultas (
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
                CREATE INDEX ix_interconsultas_paciente_id ON interconsultas(paciente_id);
                CREATE INDEX ix_interconsultas_estado ON interconsultas(estado);
                
                -- NOTIFICACIONES
                CREATE TABLE notificaciones_interconsulta (
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
                
                -- MENSAJES
                CREATE TABLE mensajes_interconsulta (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    interconsulta_id UUID NOT NULL REFERENCES interconsultas(id) ON DELETE CASCADE,
                    medico_emisor_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                    mensaje TEXT NOT NULL,
                    archivos_adjuntos VARCHAR[],
                    leido BOOLEAN NOT NULL DEFAULT FALSE,
                    fecha_lectura TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                );
                
                -- SEGUIMIENTOS
                CREATE TABLE seguimientos_interconsulta (
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
            """))
            await db.commit()
            print("   ✅ Tablas de interconsultas creadas\n")
            
            print("="*70)
            print("✅ TODAS LAS TABLAS CREADAS EXITOSAMENTE")
            print("="*70)
            print("\n💡 Ahora ejecuta: python poblar_datos_faltantes.py\n")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()

asyncio.run(main())
