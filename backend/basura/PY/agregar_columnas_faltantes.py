"""Agregar todas las columnas faltantes a hospitalizaciones"""
import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def main():
    print("\n🔧 Agregando columnas faltantes a hospitalizaciones...")
    
    async with AsyncSessionLocal() as db:
        try:
            # Agregar cada columna por separado
            columnas = [
                ("prioridad", "VARCHAR(20) DEFAULT 'normal'"),
                ("tipo_ingreso", "VARCHAR(50)"),
                ("alergias_conocidas", "VARCHAR[]"),
                ("antecedentes_relevantes", "TEXT"),
                ("tratamiento_actual", "TEXT"),
                ("tipo_seguro", "VARCHAR(100)"),
                ("numero_poliza", "VARCHAR(100)")
            ]
            
            for nombre, tipo in columnas:
                await db.execute(text(f"ALTER TABLE hospitalizaciones ADD COLUMN IF NOT EXISTS {nombre} {tipo}"))
                print(f"   ✓ {nombre}")
            
            await db.commit()
            print("\n✅ Todas las columnas agregadas exitosamente!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await db.rollback()

asyncio.run(main())
