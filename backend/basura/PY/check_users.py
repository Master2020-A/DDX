import asyncio
import sys
from sqlalchemy import select, text
from app.core.database import AsyncSessionLocal
from app.models.usuario import Usuario

async def check():
    async with AsyncSessionLocal() as session:
        try:
            # Verificar conexión
            result = await session.execute(text("SELECT 1"))
            print("✓ Conexión a DB exitosa")
            
            # Contar usuarios
            result = await session.execute(select(Usuario))
            usuarios = result.scalars().all()
            
            print(f"\n📊 Total usuarios: {len(usuarios)}")
            
            if usuarios:
                print("\n" + "="*70)
                for u in usuarios:
                    print(f"📧 Email: {u.email}")
                    print(f"👤 Nombre: {u.nombre_completo}")
                    print(f"🔑 Rol: {u.rol}")
                    print(f"✅ Activo: {u.activo}")
                    print("-"*70)
            else:
                print("\n⚠️  NO HAY USUARIOS EN LA BASE DE DATOS")
                print("\n💡 Ejecuta: python crear_admin.py")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

asyncio.run(check())
