"""
Script para verificar el usuario actual y su rol
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Importar todos los modelos para que SQLAlchemy pueda resolver las relaciones
from app.models import *
from app.core.database import get_db
from app.models.usuario import Usuario
from sqlalchemy import select


async def verificar_usuario():
    """Verifica el usuario con email admin@ddx.com"""

    async for db in get_db():
        try:
            print("🔍 Verificando usuario admin@ddx.com...\n")

            result = await db.execute(
                select(Usuario).where(Usuario.email == "admin@ddx.com")
            )
            usuario = result.scalar_one_or_none()

            if usuario:
                print(f"✅ Usuario encontrado:")
                print(f"   - ID: {usuario.id}")
                print(f"   - Email: {usuario.email}")
                print(f"   - Nombre: {usuario.nombre_completo}")
                print(f"   - Rol: {usuario.rol}")
                print(f"   - Activo: {usuario.activo}")

                # Verificar si el rol es admin
                if usuario.rol == "admin":
                    print("\n✅ El usuario tiene rol de admin")
                else:
                    print(
                        f"\n⚠️  El usuario NO tiene rol de admin, tiene: {usuario.rol}"
                    )
                    print("   Actualizando a admin...")
                    usuario.rol = "admin"
                    await db.commit()
                    print("   ✅ Rol actualizado a admin")
            else:
                print("❌ Usuario admin@ddx.com no encontrado")

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback

            traceback.print_exc()
        finally:
            await db.close()
            break


if __name__ == "__main__":
    asyncio.run(verificar_usuario())
