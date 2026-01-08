"""
Script simple para crear usuario administrador
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal, engine
from app.core.security import get_password_hash
from app.models.usuario import Usuario
from sqlalchemy import select, text


async def crear_admin():
    """Crear usuario administrador"""

    try:
        # Verificar conexión a la base de datos
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✅ Conexión a base de datos exitosa")

        async with AsyncSessionLocal() as db:
            # Verificar si ya existe el usuario
            result = await db.execute(
                select(Usuario).where(Usuario.email == "admin@ddx.com")
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print("✅ Usuario admin@ddx.com ya existe")
                print(f"   ID: {existing_user.id}")
                print(f"   Nombre: {existing_user.nombre}")
                print(f"   Email: {existing_user.email}")
                print(f"   Rol: {existing_user.rol}")
                print(f"   Activo: {existing_user.activo}")
                return existing_user

            # Crear nuevo usuario admin
            print("📝 Creando usuario administrador...")
            admin_user = Usuario(
                email="admin@ddx.com",
                nombre="Administrador",
                apellido="Sistema",
                password_hash=get_password_hash("admin123"),
                rol="administrador",
                activo=True,
                especialidad="Administración",
            )

            db.add(admin_user)
            await db.commit()
            await db.refresh(admin_user)

            print("\n✅ Usuario administrador creado exitosamente")
            print("=" * 50)
            print(f"   Email: admin@ddx.com")
            print(f"   Password: admin123")
            print(f"   ID: {admin_user.id}")
            print(f"   Rol: {admin_user.rol}")
            print("=" * 50)
            print("\n⚠️  IMPORTANTE: Cambia la contraseña después del primer login\n")

            return admin_user

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("\n🚀 Iniciando creación de usuario administrador...\n")
    asyncio.run(crear_admin())
    print("✅ Proceso completado\n")
