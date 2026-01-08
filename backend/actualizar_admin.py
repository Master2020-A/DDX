import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash


async def actualizar_admin():
    """Actualizar contraseña del usuario administrador"""

    async with AsyncSessionLocal() as db:
        # Generar hash correcto
        nuevo_hash = get_password_hash("admin123")
        print(f"Hash generado: {nuevo_hash}")

        # Actualizar usando SQL directo para evitar problemas de relaciones
        result = await db.execute(
            text(
                """
                UPDATE usuarios 
                SET password_hash = :hash,
                    rol = 'admin',
                    activo = TRUE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE email = 'admin@ddx.com'
                RETURNING id, email, nombre_completo, rol
            """
            ),
            {"hash": nuevo_hash},
        )

        user = result.fetchone()

        if user:
            await db.commit()
            print("✅ Usuario administrador actualizado exitosamente")
            print(f"   Email: {user.email}")
            print(f"   ID: {user.id}")
            print(f"   Nombre: {user.nombre_completo}")
            print(f"   Rol: {user.rol}")
            print(f"   Password: admin123")
        else:
            print("❌ Usuario admin@ddx.com no encontrado")
            print("   Creando nuevo usuario...")

            # Crear nuevo usuario
            result = await db.execute(
                text(
                    """
                    INSERT INTO usuarios (
                        id, email, nombre_completo, password_hash, 
                        rol, activo, especialidad, created_at, updated_at
                    ) VALUES (
                        gen_random_uuid(), :email, :nombre, :hash,
                        'admin', TRUE, 'Administración', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                    RETURNING id, email, nombre_completo, rol
                """
                ),
                {
                    "email": "admin@ddx.com",
                    "nombre": "Administrador Sistema",
                    "hash": nuevo_hash,
                },
            )

            user = result.fetchone()
            await db.commit()

            print("✅ Usuario administrador creado exitosamente")
            print(f"   Email: {user.email}")
            print(f"   ID: {user.id}")
            print(f"   Password: admin123")


if __name__ == "__main__":
    asyncio.run(actualizar_admin())
