"""
Migración simple para workflows - ejecuta SQL directo
"""

import sys
import asyncio
from sqlalchemy import text
from app.core.database import engine


async def main():
    try:
        async with engine.begin() as conn:
            print("Creando tipos ENUM...")

            # WorkflowStatus
            await conn.execute(
                text(
                    """
                DO $$ BEGIN
                    CREATE TYPE workflowstatus AS ENUM ('draft', 'active', 'paused', 'archived');
                EXCEPTION
                    WHEN duplicate_object THEN 
                        RAISE NOTICE 'workflowstatus ya existe';
                END $$;
            """
                )
            )
            print("✅ workflowstatus")

            # ExecutionStatus
            await conn.execute(
                text(
                    """
                DO $$ BEGIN
                    CREATE TYPE executionstatus AS ENUM ('pending', 'running', 'completed', 'failed', 'cancelled');
                EXCEPTION
                    WHEN duplicate_object THEN 
                        RAISE NOTICE 'executionstatus ya existe';
                END $$;
            """
                )
            )
            print("✅ executionstatus")

            # NodeType
            await conn.execute(
                text(
                    """
                DO $$ BEGIN
                    CREATE TYPE nodetype AS ENUM ('start', 'end', 'agent', 'condition', 'action', 'form', 'api_call', 'database', 'notification', 'delay');
                EXCEPTION
                    WHEN duplicate_object THEN 
                        RAISE NOTICE 'nodetype ya existe';
                END $$;
            """
                )
            )
            print("✅ nodetype")

            # AgentModel
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
                    WHEN duplicate_object THEN 
                        RAISE NOTICE 'agentmodel ya existe';
                END $$;
            """
                )
            )
            print("✅ agentmodel")

            print("\nCreando tabla workflows...")
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
            print("✅ Tabla workflows creada")

            print("\nCreando índices...")
            await conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_workflows_workflow_id ON workflows(workflow_id);"
                )
            )
            await conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status);"
                )
            )
            await conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_workflows_created_by ON workflows(created_by_id);"
                )
            )
            print("✅ Índices creados")

            print("\n🎉 Migración completada exitosamente!")
            return 0

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
