"""Script para agregar columnas faltantes a las tablas"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def main():
    print("\n🔧 Agregando columnas faltantes...")
    
    async with AsyncSessionLocal() as db:
        try:
            # Verificar y agregar columna resumen_clinico si no existe
            await db.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='hospitalizaciones' AND column_name='resumen_clinico'
                    ) THEN
                        ALTER TABLE hospitalizaciones ADD COLUMN resumen_clinico TEXT;
                        RAISE NOTICE 'Columna resumen_clinico agregada';
                    END IF;
                END $$;
            """))
            
            await db.commit()
            print("✅ Columnas verificadas y actualizadas!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(main())
