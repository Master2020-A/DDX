import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def main():
    print("\n🔧 Agregando columna resumen_clinico...")
    
    async with AsyncSessionLocal() as db:
        try:
            # Agregar columna
            await db.execute(text("""
                ALTER TABLE hospitalizaciones 
                ADD COLUMN IF NOT EXISTS resumen_clinico TEXT;
            """))
            await db.commit()
            print("✅ Columna agregada exitosamente!")
            
            # Verificar
            result = await db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'hospitalizaciones' 
                AND column_name = 'resumen_clinico';
            """))
            columna = result.fetchone()
            
            if columna:
                print(f"✅ Verificado: columna '{columna[0]}' existe")
            else:
                print("❌ La columna no se agregó")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            await db.rollback()

asyncio.run(main())
