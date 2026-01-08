"""Hacer motivo nullable en interconsultas"""
import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def main():
    print("\n🔧 Haciendo motivo nullable...")
    
    async with AsyncSessionLocal() as db:
        try:
            await db.execute(text("ALTER TABLE interconsultas ALTER COLUMN motivo DROP NOT NULL"))
            await db.commit()
            print("✅ motivo ahora es nullable!")
        except Exception as e:
            print(f"❌ Error: {e}")
            await db.rollback()

asyncio.run(main())
