"""
Script para verificar si las tablas de workflows existen
"""

import asyncio
from sqlalchemy import text
from app.core.database import engine


async def verificar_tablas():
    """Verifica si las tablas y tipos existen"""

    async with engine.begin() as conn:
        # Verificar tipos ENUM
        result = await conn.execute(
            text(
                """
            SELECT typname FROM pg_type 
            WHERE typname IN ('workflowstatus', 'executionstatus', 'nodetype', 'agentmodel');
        """
            )
        )
        tipos = [row[0] for row in result]

        print("=== TIPOS ENUM ===")
        for tipo in ["workflowstatus", "executionstatus", "nodetype", "agentmodel"]:
            if tipo in tipos:
                print(f"✅ {tipo}")
            else:
                print(f"❌ {tipo} - NO EXISTE")

        # Verificar tablas
        result = await conn.execute(
            text(
                """
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename IN ('workflows', 'ai_agents', 'workflow_executions', 'workflow_templates');
        """
            )
        )
        tablas = [row[0] for row in result]

        print("\n=== TABLAS ===")
        for tabla in [
            "workflows",
            "ai_agents",
            "workflow_executions",
            "workflow_templates",
        ]:
            if tabla in tablas:
                print(f"✅ {tabla}")
            else:
                print(f"❌ {tabla} - NO EXISTE")


if __name__ == "__main__":
    asyncio.run(verificar_tablas())
