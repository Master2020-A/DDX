"""
Script para crear la tabla workflows y tipos ENUM necesarios
"""

import asyncio
from sqlalchemy import text
from app.core.database import engine


async def create_workflow_tables():
    """Crea los tipos ENUM y tablas para workflows"""

    async with engine.begin() as conn:
        # Crear tipo ENUM WorkflowStatus si no existe
        await conn.execute(
            text(
                """
            DO $$ BEGIN
                CREATE TYPE workflowstatus AS ENUM ('draft', 'active', 'paused', 'archived');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """
            )
        )

        # Crear tipo ENUM ExecutionStatus si no existe
        await conn.execute(
            text(
                """
            DO $$ BEGIN
                CREATE TYPE executionstatus AS ENUM ('pending', 'running', 'completed', 'failed', 'cancelled');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """
            )
        )

        # Crear tipo ENUM NodeType si no existe
        await conn.execute(
            text(
                """
            DO $$ BEGIN
                CREATE TYPE nodetype AS ENUM ('start', 'end', 'agent', 'condition', 'action', 'form', 'api_call', 'database', 'notification', 'delay');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """
            )
        )

        # Crear tipo ENUM AgentModel si no existe
        await conn.execute(
            text(
                """
            DO $$ BEGIN
                CREATE TYPE agentmodel AS ENUM (
                    'gpt-4', 'gpt-4-turbo', 'gpt-4o', 'gpt-4o-mini',
                    'claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku',
                    'gemini-2.0-flash', 'gemini-pro'
                );
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """
            )
        )

        print("✅ Tipos ENUM creados exitosamente")

        # Crear tabla workflows si no existe
        await conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS workflows (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                workflow_id VARCHAR(100) UNIQUE NOT NULL,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                category VARCHAR(100),
                status workflowstatus NOT NULL DEFAULT 'draft',
                version VARCHAR(20) DEFAULT '1.0.0',
                nodes JSONB NOT NULL DEFAULT '[]',
                edges JSONB NOT NULL DEFAULT '[]',
                config JSONB DEFAULT '{}',
                variables JSONB DEFAULT '{}',
                icon VARCHAR(50),
                color VARCHAR(20),
                tags JSONB DEFAULT '[]',
                created_by_id UUID REFERENCES usuarios(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
            )
        )

        print("✅ Tabla workflows creada exitosamente")

        # Crear índices
        await conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_workflows_workflow_id ON workflows(workflow_id);
            CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status);
            CREATE INDEX IF NOT EXISTS idx_workflows_created_by ON workflows(created_by_id);
        """
            )
        )

        print("✅ Índices creados exitosamente")

        # Crear tabla ai_agents si no existe
        await conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS ai_agents (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                workflow_id UUID REFERENCES workflows(id) ON DELETE CASCADE,
                agent_id VARCHAR(100) NOT NULL,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                model agentmodel NOT NULL,
                system_prompt TEXT,
                temperature FLOAT DEFAULT 0.7,
                max_tokens INTEGER DEFAULT 2000,
                config JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
            )
        )

        print("✅ Tabla ai_agents creada exitosamente")

        # Crear tabla workflow_executions si no existe
        await conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS workflow_executions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                workflow_id UUID REFERENCES workflows(id) ON DELETE CASCADE,
                status executionstatus NOT NULL DEFAULT 'pending',
                input_data JSONB DEFAULT '{}',
                output_data JSONB,
                error TEXT,
                triggered_by VARCHAR(100),
                user_id UUID REFERENCES usuarios(id),
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                execution_time_ms INTEGER
            );
        """
            )
        )

        print("✅ Tabla workflow_executions creada exitosamente")

        # Crear índices para executions
        await conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_executions_workflow ON workflow_executions(workflow_id);
            CREATE INDEX IF NOT EXISTS idx_executions_status ON workflow_executions(status);
            CREATE INDEX IF NOT EXISTS idx_executions_user ON workflow_executions(user_id);
        """
            )
        )

        print("✅ Índices de executions creados exitosamente")

        # Crear tabla workflow_templates si no existe
        await conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS workflow_templates (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                template_id VARCHAR(100) UNIQUE NOT NULL,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                category VARCHAR(100),
                icon VARCHAR(50),
                color VARCHAR(20),
                tags JSONB DEFAULT '[]',
                nodes JSONB NOT NULL DEFAULT '[]',
                edges JSONB NOT NULL DEFAULT '[]',
                config JSONB DEFAULT '{}',
                is_public BOOLEAN DEFAULT true,
                created_by_id UUID REFERENCES usuarios(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
            )
        )

        print("✅ Tabla workflow_templates creada exitosamente")

        print("\n🎉 Todas las tablas de workflows creadas exitosamente!")


if __name__ == "__main__":
    print("Creando tablas de workflows...")
    asyncio.run(create_workflow_tables())
    print("✅ Proceso completado")
