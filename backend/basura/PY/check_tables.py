"""Script para verificar tablas en la base de datos"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


async def main():
    from sqlalchemy import text
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        # Verificar tablas del portal del paciente
        result = await db.execute(
            text(
                """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%paciente%'
            ORDER BY table_name
        """
            )
        )

        tables = result.fetchall()
        print("Tablas relacionadas con 'paciente':")
        for table in tables:
            print(f"  - {table[0]}")

        # Verificar versión de Alembic
        result = await db.execute(text("SELECT version_num FROM alembic_version"))
        version = result.scalar_one_or_none()
        print(f"\nVersión actual de Alembic: {version}")


asyncio.run(main())
