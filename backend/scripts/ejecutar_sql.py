"""Ejecutar script SQL para crear tablas"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def main():
    print("\n🔧 Ejecutando script SQL...")
    
    # Leer archivo SQL
    sql_file = Path(__file__).parent.parent / "crear_tablas.sql"
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    async with AsyncSessionLocal() as db:
        try:
            # Ejecutar el script
            await db.execute(text(sql_script))
            await db.commit()
            print("✅ Tablas creadas exitosamente!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(main())
