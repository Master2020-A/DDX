"""
Script para crear usuario administrador
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.usuario import Usuario
from sqlalchemy import select


async def crear_admin():
    """Crear usuario administrador si no existe"""

    async with AsyncSessionLocal() as db:
        # Verificar si ya existe
        result = await db.execute(
            select(Usuario).where(Usuario.email == "admin@ddx.com")
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print("✅ Usuario admin@ddx.com ya existe")
            print(f"   ID: {existing_user.id}")
            print(f"   Nombre: {existing_user.nombre}")
            print(f"   Rol: {existing_user.rol}")
            return

        # Crear nuevo usuario admin
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

        print("✅ Usuario administrador creado exitosamente")
        print(f"   Email: admin@ddx.com")
        print(f"   Password: admin123")
        print(f"   ID: {admin_user.id}")
        print(f"   Rol: {admin_user.rol}")
        print("\n⚠️  IMPORTANTE: Cambia la contraseña después del primer login")


if __name__ == "__main__":
    asyncio.run(crear_admin())
