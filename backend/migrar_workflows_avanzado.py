"""
Script de migración para funcionalidades avanzadas de workflows:
- Versionado
- A/B Testing
- Nuevos tipos de nodos (Loop, Subworkflow)
"""

import asyncio
import asyncpg
from datetime import datetime

# Configuración de la base de datos
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "ddx",
    "user": "postgres",
    "password": "postgres",
    "timeout": 30,
    "command_timeout": 60,
}


async def migrate():
    """Ejecuta las migraciones"""
    print("=" * 60)
    print("MIGRACIÓN DE WORKFLOWS AVANZADOS")
    print("=" * 60)
    print()

    try:
        # Conectar a la base de datos
        print("📡 Conectando a la base de datos...")
        conn = await asyncpg.connect(**DATABASE_CONFIG)
        print("✅ Conexión establecida\n")

        # 1. Actualizar ENUM nodetype para agregar loop y subworkflow
        print("1️⃣ Actualizando ENUM nodetype...")
        try:
            await conn.execute(
                """
                ALTER TYPE nodetype ADD VALUE IF NOT EXISTS 'loop';
            """
            )
            print("   ✅ Agregado tipo 'loop'")

            await conn.execute(
                """
                ALTER TYPE nodetype ADD VALUE IF NOT EXISTS 'subworkflow';
            """
            )
            print("   ✅ Agregado tipo 'subworkflow'\n")
        except Exception as e:
            print(f"   ⚠️  Tipos ya existen o error: {e}\n")

        # 2. Crear tabla workflow_versions
        print("2️⃣ Creando tabla workflow_versions...")
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS workflow_versions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
                
                -- Información de versión
                version_number VARCHAR(20) NOT NULL,
                version_name VARCHAR(200),
                is_current BOOLEAN DEFAULT FALSE,
                is_published BOOLEAN DEFAULT FALSE,
                
                -- Snapshot del workflow
                nodes JSONB NOT NULL,
                edges JSONB NOT NULL,
                config JSONB DEFAULT '{}'::jsonb,
                variables JSONB DEFAULT '{}'::jsonb,
                
                -- Changelog
                changes_description TEXT,
                breaking_changes BOOLEAN DEFAULT FALSE,
                
                -- Métricas
                execution_count INTEGER DEFAULT 0,
                success_rate FLOAT DEFAULT 0.0,
                avg_duration_ms INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                
                -- Auditoría
                created_by_id UUID REFERENCES usuarios(id),
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
                published_at TIMESTAMP WITHOUT TIME ZONE,
                deprecated_at TIMESTAMP WITHOUT TIME ZONE,
                
                -- Índices
                CONSTRAINT unique_workflow_version UNIQUE (workflow_id, version_number)
            );
            
            CREATE INDEX IF NOT EXISTS idx_workflow_versions_workflow 
                ON workflow_versions(workflow_id);
            CREATE INDEX IF NOT EXISTS idx_workflow_versions_current 
                ON workflow_versions(workflow_id, is_current) WHERE is_current = TRUE;
            CREATE INDEX IF NOT EXISTS idx_workflow_versions_published 
                ON workflow_versions(is_published) WHERE is_published = TRUE;
        """
        )
        print("   ✅ Tabla workflow_versions creada\n")

        # 3. Crear ENUM para estados de A/B test
        print("3️⃣ Creando ENUM abtestatus...")
        try:
            await conn.execute(
                """
                DO $$ BEGIN
                    CREATE TYPE abtestatus AS ENUM (
                        'draft',
                        'running',
                        'paused',
                        'completed',
                        'cancelled'
                    );
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """
            )
            print("   ✅ ENUM abtestatus creado\n")
        except Exception as e:
            print(f"   ⚠️  ENUM ya existe: {e}\n")

        # 4. Crear tabla ab_tests
        print("4️⃣ Creando tabla ab_tests...")
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ab_tests (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
                
                -- Información del test
                test_name VARCHAR(200) NOT NULL,
                description TEXT,
                hypothesis TEXT,
                status VARCHAR(20) DEFAULT 'draft',
                
                -- Variantes
                variant_a_version_id UUID NOT NULL REFERENCES workflow_versions(id),
                variant_b_version_id UUID NOT NULL REFERENCES workflow_versions(id),
                
                -- Configuración
                traffic_split FLOAT DEFAULT 0.5,
                sample_size INTEGER,
                confidence_level FLOAT DEFAULT 0.95,
                
                -- Métricas
                primary_metric VARCHAR(100),
                secondary_metrics JSONB DEFAULT '[]'::jsonb,
                
                -- Resultados
                variant_a_executions INTEGER DEFAULT 0,
                variant_b_executions INTEGER DEFAULT 0,
                variant_a_metrics JSONB DEFAULT '{}'::jsonb,
                variant_b_metrics JSONB DEFAULT '{}'::jsonb,
                winner VARCHAR(1),
                statistical_significance FLOAT,
                
                -- Fechas
                started_at TIMESTAMP WITHOUT TIME ZONE,
                completed_at TIMESTAMP WITHOUT TIME ZONE,
                duration_days INTEGER,
                
                -- Auditoría
                created_by_id UUID REFERENCES usuarios(id),
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_ab_tests_workflow 
                ON ab_tests(workflow_id);
            CREATE INDEX IF NOT EXISTS idx_ab_tests_status 
                ON ab_tests(status);
            CREATE INDEX IF NOT EXISTS idx_ab_tests_running 
                ON ab_tests(workflow_id, status) WHERE status = 'running';
        """
        )
        print("   ✅ Tabla ab_tests creada\n")

        # 5. Crear tabla ab_test_executions
        print("5️⃣ Creando tabla ab_test_executions...")
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ab_test_executions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                ab_test_id UUID NOT NULL REFERENCES ab_tests(id) ON DELETE CASCADE,
                execution_id UUID NOT NULL REFERENCES workflow_executions(id) ON DELETE CASCADE,
                
                -- Variante asignada
                variant VARCHAR(1) NOT NULL,
                version_id UUID REFERENCES workflow_versions(id),
                
                -- Métricas capturadas
                duration_ms INTEGER,
                success BOOLEAN,
                error_occurred BOOLEAN DEFAULT FALSE,
                custom_metrics JSONB DEFAULT '{}'::jsonb,
                
                -- Auditoría
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_ab_test_executions_test 
                ON ab_test_executions(ab_test_id);
            CREATE INDEX IF NOT EXISTS idx_ab_test_executions_execution 
                ON ab_test_executions(execution_id);
            CREATE INDEX IF NOT EXISTS idx_ab_test_executions_variant 
                ON ab_test_executions(ab_test_id, variant);
        """
        )
        print("   ✅ Tabla ab_test_executions creada\n")

        # 6. Agregar columnas a workflows si no existen
        print("6️⃣ Verificando columnas adicionales en workflows...")
        try:
            # Verificar si la columna parent_workflow_id existe
            result = await conn.fetchval(
                """
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_name = 'workflows' 
                AND column_name = 'parent_workflow_id'
            """
            )

            if result == 0:
                await conn.execute(
                    """
                    ALTER TABLE workflows 
                    ADD COLUMN parent_workflow_id UUID REFERENCES workflows(id);
                """
                )
                print("   ✅ Agregada columna parent_workflow_id")
            else:
                print("   ℹ️  Columna parent_workflow_id ya existe")

        except Exception as e:
            print(f"   ⚠️  Error al agregar columnas: {e}\n")

        # 7. Crear función para actualizar métricas de versiones
        print("7️⃣ Creando función para actualizar métricas...")
        await conn.execute(
            """
            CREATE OR REPLACE FUNCTION update_version_metrics()
            RETURNS TRIGGER AS $$
            BEGIN
                -- Actualizar métricas de la versión cuando se completa una ejecución
                IF NEW.status = 'completed' OR NEW.status = 'failed' THEN
                    UPDATE workflow_versions
                    SET 
                        execution_count = execution_count + 1,
                        success_rate = (
                            SELECT COUNT(*)::FLOAT / NULLIF(COUNT(*), 0)
                            FROM workflow_executions we
                            WHERE we.workflow_id = NEW.workflow_id
                            AND we.status = 'completed'
                        ),
                        avg_duration_ms = (
                            SELECT AVG(duration_ms)::INTEGER
                            FROM workflow_executions we
                            WHERE we.workflow_id = NEW.workflow_id
                            AND we.duration_ms IS NOT NULL
                        ),
                        error_count = (
                            SELECT COUNT(*)
                            FROM workflow_executions we
                            WHERE we.workflow_id = NEW.workflow_id
                            AND we.status = 'failed'
                        )
                    WHERE workflow_id = NEW.workflow_id
                    AND is_current = TRUE;
                END IF;
                
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            
            DROP TRIGGER IF EXISTS trigger_update_version_metrics ON workflow_executions;
            
            CREATE TRIGGER trigger_update_version_metrics
            AFTER UPDATE ON workflow_executions
            FOR EACH ROW
            WHEN (OLD.status IS DISTINCT FROM NEW.status)
            EXECUTE FUNCTION update_version_metrics();
        """
        )
        print("   ✅ Función y trigger creados\n")

        # 8. Crear versiones iniciales para workflows existentes
        print("8️⃣ Creando versiones iniciales para workflows existentes...")
        workflows = await conn.fetch(
            """
            SELECT id, name, nodes, edges, config, variables, created_by_id
            FROM workflows
            WHERE status = 'active'
        """
        )

        created_versions = 0
        for workflow in workflows:
            # Verificar si ya tiene versión
            existing = await conn.fetchval(
                """
                SELECT COUNT(*) FROM workflow_versions WHERE workflow_id = $1
            """,
                workflow["id"],
            )

            if existing == 0:
                await conn.execute(
                    """
                    INSERT INTO workflow_versions (
                        workflow_id, version_number, version_name,
                        is_current, is_published,
                        nodes, edges, config, variables,
                        created_by_id, published_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """,
                    workflow["id"],
                    "1.0.0",
                    "Versión Inicial",
                    True,
                    True,
                    workflow["nodes"],
                    workflow["edges"],
                    workflow["config"] or {},
                    workflow["variables"] or {},
                    workflow["created_by_id"],
                    datetime.utcnow(),
                )
                created_versions += 1

        print(f"   ✅ Creadas {created_versions} versiones iniciales\n")

        # Cerrar conexión
        await conn.close()
        print("=" * 60)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print()
        print("📊 Resumen:")
        print(f"   • ENUM nodetype actualizado (loop, subworkflow)")
        print(f"   • Tabla workflow_versions creada")
        print(f"   • Tabla ab_tests creada")
        print(f"   • Tabla ab_test_executions creada")
        print(f"   • {created_versions} versiones iniciales creadas")
        print(f"   • Triggers y funciones configurados")
        print()
        print("🎉 El sistema de workflows avanzados está listo!")
        print()

    except Exception as e:
        print(f"\n❌ ERROR EN LA MIGRACIÓN: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    print("\n")
    print("🚀 Iniciando migración de workflows avanzados...")
    print()

    success = asyncio.run(migrate())

    if success:
        print("✅ Migración completada. Reinicia el backend para aplicar los cambios.")
    else:
        print("❌ La migración falló. Revisa los errores anteriores.")

    print()
    input("Presiona Enter para salir...")
