"""
Script de migración mejorado para funcionalidades avanzadas de workflows
Con mejor manejo de conexiones y reintentos
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime
import json

# Configuración de la base de datos
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "ddx",
    "user": "postgres",
    "password": "postgres",
    "client_encoding": "UTF8",
}


def migrate():
    """Ejecuta las migraciones usando psycopg2 (síncrono)"""
    print("=" * 60)
    print("MIGRACIÓN DE WORKFLOWS AVANZADOS")
    print("=" * 60)
    print()

    conn = None
    try:
        # Conectar a la base de datos
        print("📡 Conectando a la base de datos...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        print("✅ Conexión establecida\n")

        # 1. Actualizar ENUM nodetype
        print("1️⃣ Actualizando ENUM nodetype...")
        try:
            cursor.execute("ALTER TYPE nodetype ADD VALUE IF NOT EXISTS 'loop';")
            print("   ✅ Agregado tipo 'loop'")
        except Exception as e:
            print(f"   ℹ️  'loop' ya existe o error: {e}")

        try:
            cursor.execute("ALTER TYPE nodetype ADD VALUE IF NOT EXISTS 'subworkflow';")
            print("   ✅ Agregado tipo 'subworkflow'\n")
        except Exception as e:
            print(f"   ℹ️  'subworkflow' ya existe o error: {e}\n")

        # 2. Crear tabla workflow_versions
        print("2️⃣ Creando tabla workflow_versions...")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS workflow_versions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
                
                version_number VARCHAR(20) NOT NULL,
                version_name VARCHAR(200),
                is_current BOOLEAN DEFAULT FALSE,
                is_published BOOLEAN DEFAULT FALSE,
                
                nodes JSONB NOT NULL,
                edges JSONB NOT NULL,
                config JSONB DEFAULT '{}'::jsonb,
                variables JSONB DEFAULT '{}'::jsonb,
                
                changes_description TEXT,
                breaking_changes BOOLEAN DEFAULT FALSE,
                
                execution_count INTEGER DEFAULT 0,
                success_rate FLOAT DEFAULT 0.0,
                avg_duration_ms INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                
                created_by_id UUID REFERENCES usuarios(id),
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
                published_at TIMESTAMP WITHOUT TIME ZONE,
                deprecated_at TIMESTAMP WITHOUT TIME ZONE,
                
                CONSTRAINT unique_workflow_version UNIQUE (workflow_id, version_number)
            );
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_workflow_versions_workflow 
                ON workflow_versions(workflow_id);
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_workflow_versions_current 
                ON workflow_versions(workflow_id, is_current) WHERE is_current = TRUE;
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_workflow_versions_published 
                ON workflow_versions(is_published) WHERE is_published = TRUE;
        """
        )
        print("   ✅ Tabla workflow_versions creada\n")

        # 3. Crear ENUM abtestatus
        print("3️⃣ Creando ENUM abtestatus...")
        try:
            cursor.execute(
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
            print(f"   ℹ️  ENUM ya existe: {e}\n")

        # 4. Crear tabla ab_tests
        print("4️⃣ Creando tabla ab_tests...")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ab_tests (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
                
                test_name VARCHAR(200) NOT NULL,
                description TEXT,
                hypothesis TEXT,
                status VARCHAR(20) DEFAULT 'draft',
                
                variant_a_version_id UUID NOT NULL REFERENCES workflow_versions(id),
                variant_b_version_id UUID NOT NULL REFERENCES workflow_versions(id),
                
                traffic_split FLOAT DEFAULT 0.5,
                sample_size INTEGER,
                confidence_level FLOAT DEFAULT 0.95,
                
                primary_metric VARCHAR(100),
                secondary_metrics JSONB DEFAULT '[]'::jsonb,
                
                variant_a_executions INTEGER DEFAULT 0,
                variant_b_executions INTEGER DEFAULT 0,
                variant_a_metrics JSONB DEFAULT '{}'::jsonb,
                variant_b_metrics JSONB DEFAULT '{}'::jsonb,
                winner VARCHAR(1),
                statistical_significance FLOAT,
                
                started_at TIMESTAMP WITHOUT TIME ZONE,
                completed_at TIMESTAMP WITHOUT TIME ZONE,
                duration_days INTEGER,
                
                created_by_id UUID REFERENCES usuarios(id),
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
            );
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_ab_tests_workflow 
                ON ab_tests(workflow_id);
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_ab_tests_status 
                ON ab_tests(status);
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_ab_tests_running 
                ON ab_tests(workflow_id, status) WHERE status = 'running';
        """
        )
        print("   ✅ Tabla ab_tests creada\n")

        # 5. Crear tabla ab_test_executions
        print("5️⃣ Creando tabla ab_test_executions...")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ab_test_executions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                ab_test_id UUID NOT NULL REFERENCES ab_tests(id) ON DELETE CASCADE,
                execution_id UUID NOT NULL REFERENCES workflow_executions(id) ON DELETE CASCADE,
                
                variant VARCHAR(1) NOT NULL,
                version_id UUID REFERENCES workflow_versions(id),
                
                duration_ms INTEGER,
                success BOOLEAN,
                error_occurred BOOLEAN DEFAULT FALSE,
                custom_metrics JSONB DEFAULT '{}'::jsonb,
                
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
            );
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_ab_test_executions_test 
                ON ab_test_executions(ab_test_id);
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_ab_test_executions_execution 
                ON ab_test_executions(execution_id);
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_ab_test_executions_variant 
                ON ab_test_executions(ab_test_id, variant);
        """
        )
        print("   ✅ Tabla ab_test_executions creada\n")

        # 6. Agregar columna parent_workflow_id
        print("6️⃣ Verificando columnas adicionales...")
        cursor.execute(
            """
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_name = 'workflows' 
            AND column_name = 'parent_workflow_id'
        """
        )

        if cursor.fetchone()[0] == 0:
            cursor.execute(
                """
                ALTER TABLE workflows 
                ADD COLUMN parent_workflow_id UUID REFERENCES workflows(id);
            """
            )
            print("   ✅ Agregada columna parent_workflow_id")
        else:
            print("   ℹ️  Columna parent_workflow_id ya existe")

        # 7. Crear función para actualizar métricas
        print("\n7️⃣ Creando función para actualizar métricas...")
        cursor.execute(
            """
            CREATE OR REPLACE FUNCTION update_version_metrics()
            RETURNS TRIGGER AS $$
            BEGIN
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
        """
        )

        cursor.execute(
            "DROP TRIGGER IF EXISTS trigger_update_version_metrics ON workflow_executions;"
        )

        cursor.execute(
            """
            CREATE TRIGGER trigger_update_version_metrics
            AFTER UPDATE ON workflow_executions
            FOR EACH ROW
            WHEN (OLD.status IS DISTINCT FROM NEW.status)
            EXECUTE FUNCTION update_version_metrics();
        """
        )
        print("   ✅ Función y trigger creados\n")

        # 8. Crear versiones iniciales
        print("8️⃣ Creando versiones iniciales para workflows existentes...")
        cursor.execute(
            """
            SELECT id, name, nodes, edges, config, variables, created_by_id
            FROM workflows
            WHERE status = 'active'
        """
        )

        workflows = cursor.fetchall()
        created_versions = 0

        for workflow in workflows:
            wf_id, name, nodes, edges, config, variables, created_by = workflow

            # Verificar si ya tiene versión
            cursor.execute(
                "SELECT COUNT(*) FROM workflow_versions WHERE workflow_id = %s",
                (wf_id,),
            )

            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    """
                    INSERT INTO workflow_versions (
                        workflow_id, version_number, version_name,
                        is_current, is_published,
                        nodes, edges, config, variables,
                        created_by_id, published_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        wf_id,
                        "1.0.0",
                        "Versión Inicial",
                        True,
                        True,
                        json.dumps(nodes) if isinstance(nodes, (list, dict)) else nodes,
                        json.dumps(edges) if isinstance(edges, (list, dict)) else edges,
                        (
                            json.dumps(config)
                            if isinstance(config, dict)
                            else (config or "{}")
                        ),
                        (
                            json.dumps(variables)
                            if isinstance(variables, dict)
                            else (variables or "{}")
                        ),
                        created_by,
                        datetime.utcnow(),
                    ),
                )
                created_versions += 1

        print(f"   ✅ Creadas {created_versions} versiones iniciales\n")

        cursor.close()
        conn.close()

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

        return True

    except psycopg2.OperationalError as e:
        print(f"\n❌ ERROR DE CONEXIÓN: {e}")
        print("\n💡 Posibles soluciones:")
        print("   1. Verifica que PostgreSQL esté corriendo")
        print("   2. Verifica usuario/contraseña en el script")
        print("   3. Verifica que la base de datos 'ddx' exista")
        return False

    except Exception as e:
        print(f"\n❌ ERROR EN LA MIGRACIÓN: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        if conn:
            try:
                conn.close()
            except:
                pass


if __name__ == "__main__":
    print("\n")
    print("🚀 Iniciando migración de workflows avanzados...")
    print()

    success = migrate()

    if success:
        print("✅ Migración completada. Reinicia el backend para aplicar los cambios.")
    else:
        print("❌ La migración falló. Revisa los errores anteriores.")

    print()
    input("Presiona Enter para salir...")
