"""Agregar TODAS las columnas faltantes una por una"""
import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def main():
    print("\n🔧 Agregando TODAS las columnas faltantes...")
    
    columnas_agregar = [
        ("piso", "VARCHAR(20)"),
        ("prioridad", "VARCHAR(20) DEFAULT 'normal'"),
        ("tipo_ingreso", "VARCHAR(50)"),
        ("alergias_conocidas", "VARCHAR[]"),
        ("antecedentes_relevantes", "TEXT"),
        ("tratamiento_actual", "TEXT"),
        ("tipo_seguro", "VARCHAR(100)"),
        ("numero_poliza", "VARCHAR(100)")
    ]
    
    async with AsyncSessionLocal() as db:
        for nombre, tipo in columnas_agregar:
            try:
                print(f"  Agregando {nombre}...", end=" ")
                await db.execute(text(f"ALTER TABLE hospitalizaciones ADD COLUMN IF NOT EXISTS {nombre} {tipo}"))
                await db.commit()
                print("✓")
            except Exception as e:
                print(f"✗ ({e})")
                await db.rollback()
        
        print("\n✅ Proceso completado!")
        
        # Verificar columnas finales
        result = await db.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'hospitalizaciones'
            ORDER BY ordinal_position
        """))
        columnas = [r[0] for r in result.fetchall()]
        print(f"\n📋 Total de columnas ahora: {len(columnas)}")
        print("Columnas:", ", ".join(columnas))

asyncio.run(main())
