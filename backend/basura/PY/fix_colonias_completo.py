"""
Script completo para arreglar las colonias del CP 83288
Ejecuta todos los pasos en orden
"""
import asyncio
from sqlalchemy import text, delete
from app.core.database import AsyncSessionLocal
from app.models.catalogos import CodigoPostal


async def fix_colonias():
    print("="*70)
    print("ARREGLAR SISTEMA DE COLONIAS")
    print("="*70)
    print()
    
    async with AsyncSessionLocal() as db:
        # PASO 1: Eliminar constraint UNIQUE
        print("1️⃣  Eliminando constraint UNIQUE...")
        try:
            await db.execute(text('ALTER TABLE codigos_postales DROP CONSTRAINT IF EXISTS codigos_postales_codigo_postal_key'))
            await db.commit()
            print("   ✅ Constraint UNIQUE eliminado")
        except Exception as e:
            print(f"   ⚠️  {e}")
        print()
        
        # PASO 2: Eliminar CP 83288 antiguo
        print("2️⃣  Eliminando CP 83288 antiguo...")
        try:
            result = await db.execute(delete(CodigoPostal).where(CodigoPostal.codigo_postal == '83288'))
            await db.commit()
            print(f"   ✅ Eliminados {result.rowcount} registros del CP 83288")
        except Exception as e:
            print(f"   ⚠️  {e}")
        print()
    
    # PASO 3: Agregar nuevos códigos con todas las colonias
    print("3️⃣  Agregando códigos postales con TODAS las colonias...")
    print("   Ejecuta ahora: python agregar_codigos_postales.py")
    print()
    print("="*70)
    print("LISTO - Ahora ejecuta agregar_codigos_postales.py")
    print("="*70)


if __name__ == "__main__":
    try:
        asyncio.run(fix_colonias())
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
