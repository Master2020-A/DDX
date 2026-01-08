"""
Script para crear tablas de seguridad directamente
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.models.security import Base as SecurityBase


async def crear_tablas():
    print("Creando tablas de seguridad...")

    engine = create_async_engine(str(settings.DATABASE_URL))

    async with engine.begin() as conn:
        # Importar todos los modelos de seguridad
        from app.models.security import (
            TwoFactorAuth,
            AuditLog,
            UserSession,
            Permission,
            Role,
            RolePermission,
            UserRole,
            SSOProvider,
            SSOConnection,
            EncryptedData,
        )

        # Crear todas las tablas
        await conn.run_sync(SecurityBase.metadata.create_all)

    print("✅ Tablas de seguridad creadas exitosamente")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(crear_tablas())
