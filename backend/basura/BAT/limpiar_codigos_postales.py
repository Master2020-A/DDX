"""
Script para limpiar la tabla de códigos postales
Úsalo solo si quieres eliminar todos los CPs y empezar de cero
"""
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.catalogos import CodigoPostal
from sqlalchemy import delete


async def limpiar_tabla():
    """Eliminar todos los códigos postales de la BD"""
    print("="*70)
    print("LIMPIAR TABLA DE CÓDIGOS POSTALES")
    print("="*70)
    print()
    print("⚠️  ADVERTENCIA: Esto eliminará TODOS los códigos postales actuales")
    print()
    
    respuesta = input("¿Estás seguro? Escribe 'SI' para confirmar: ")
    
    if respuesta.upper() != "SI":
        print("\n❌ Operación cancelada")
        return False
    
    async with AsyncSessionLocal() as session:
        try:
            # Eliminar todos los registros
            await session.execute(delete(CodigoPostal))
            await session.commit()
            
            print("\n✅ Tabla limpiada correctamente")
            print("Ahora puedes ejecutar: python agregar_codigos_postales.py")
            return True
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ ERROR: {e}")
            return False


if __name__ == "__main__":
    try:
        asyncio.run(limpiar_tabla())
    except KeyboardInterrupt:
        print("\n\n⚠️  Operación cancelada")
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
