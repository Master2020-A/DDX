"""Ver columnas reales de interconsultas"""
import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'interconsultas'
            ORDER BY ordinal_position
        """))
        
        columnas = result.fetchall()
        
        print("\n📋 COLUMNAS REALES EN interconsultas:")
        print("-" * 50)
        for col in columnas:
            print(f"  {col[0]:30} {col[1]}")
        print("-" * 50)
        print(f"\nTotal: {len(columnas)} columnas\n")

asyncio.run(main())
