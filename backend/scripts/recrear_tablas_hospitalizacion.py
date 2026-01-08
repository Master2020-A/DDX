"""Script para recrear tablas de hospitalización con estructura correcta"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def main():
    print("\n" + "="*60)
    print("🔧 RECREANDO TABLAS DE HOSPITALIZACIÓN")
    print("="*60 + "\n")
    
    async with AsyncSessionLocal() as db:
        try:
            print("1. Eliminando tablas existentes...")
            await db.execute(text("""
                DROP TABLE IF EXISTS notas_alta CASCADE;
                DROP TABLE IF EXISTS indicaciones_medicas CASCADE;
                DROP TABLE IF EXISTS notas_evolucion CASCADE;
                DROP TABLE IF EXISTS hospitalizaciones CASCADE;
                DROP TABLE IF EXISTS camas CASCADE;
            """))
            await db.commit()
            print("✅ Tablas eliminadas\n")
            
            print("2. Creando tabla camas...")
            await db.execute(text("""
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
                CREATE UNIQUE INDEX ix_camas_numero_cama ON camas(numero_cama);
            """))
            await db.commit()
            print("✅ Tabla camas creada\n")
            
            print("3. Creando tabla hospitalizaciones...")
            await db.execute(text("""
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
                    resumen_clinico TEXT,
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
                CREATE INDEX ix_hospitalizaciones_fecha_ingreso ON hospitalizaciones(fecha_ingreso);
            """))
            await db.commit()
            print("✅ Tabla hospitalizaciones creada\n")
            
            print("4. Creando tabla notas_evolucion...")
            await db.execute(text("""
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
                CREATE INDEX ix_notas_evolucion_hospitalizacion_id ON notas_evolucion(hospitalizacion_id);
                CREATE INDEX ix_notas_evolucion_fecha_nota ON notas_evolucion(fecha_nota);
            """))
            await db.commit()
            print("✅ Tabla notas_evolucion creada\n")
            
            print("5. Creando tabla indicaciones_medicas...")
            await db.execute(text("""
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
                CREATE INDEX ix_indicaciones_medicas_hospitalizacion_id ON indicaciones_medicas(hospitalizacion_id);
                CREATE INDEX ix_indicaciones_medicas_estado ON indicaciones_medicas(estado);
            """))
            await db.commit()
            print("✅ Tabla indicaciones_medicas creada\n")
            
            print("6. Creando tabla notas_alta...")
            await db.execute(text("""
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
                CREATE INDEX ix_notas_alta_fecha_alta ON notas_alta(fecha_alta);
            """))
            await db.commit()
            print("✅ Tabla notas_alta creada\n")
            
            print("="*60)
            print("✅ TODAS LAS TABLAS CREADAS EXITOSAMENTE")
            print("="*60)
            print("\n💡 Ahora ejecuta: python -m scripts.poblar_hospitalizacion_interconsultas\n")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(main())
