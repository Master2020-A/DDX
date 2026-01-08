import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal


async def verificar():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("SELECT workflow_id, name, status FROM workflows")
        )
        rows = result.fetchall()
        print(f"\n📊 Workflows encontrados: {len(rows)}")
        for r in rows:
            print(f"  - {r.workflow_id}: {r.name} ({r.status})")

        if len(rows) == 0:
            print("\n❌ No hay workflows en la base de datos")
            print("   Ejecuta: python crear_workflow_ejemplo.py")


asyncio.run(verificar())
