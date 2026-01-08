"""
Script para verificar y crear tablas de seguridad
"""

import asyncio
from sqlalchemy import text
from app.core.database import engine


async def verificar_tablas():
    async with engine.begin() as conn:
        # Verificar si existen las tablas de seguridad
        result = await conn.execute(
            text(
                """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN (
                'permissions', 'roles', 'role_permissions', 'user_roles',
                'two_factor_auth', 'audit_logs', 'user_sessions',
                'sso_providers', 'sso_connections', 'encrypted_data'
            )
        """
            )
        )

        tablas_existentes = [row[0] for row in result]

        print("=" * 60)
        print("VERIFICACIÓN DE TABLAS DE SEGURIDAD")
        print("=" * 60)

        tablas_requeridas = [
            "permissions",
            "roles",
            "role_permissions",
            "user_roles",
            "two_factor_auth",
            "audit_logs",
            "user_sessions",
            "sso_providers",
            "sso_connections",
            "encrypted_data",
        ]

        print(f"\nTablas requeridas: {len(tablas_requeridas)}")
        print(f"Tablas existentes: {len(tablas_existentes)}")
        print(f"\nTablas encontradas: {tablas_existentes}")

        tablas_faltantes = [t for t in tablas_requeridas if t not in tablas_existentes]

        if tablas_faltantes:
            print(f"\n⚠️  TABLAS FALTANTES: {tablas_faltantes}")
            print("\nPara crear las tablas, ejecuta:")
            print("  alembic upgrade head")
        else:
            print("\n✅ Todas las tablas de seguridad existen")

        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(verificar_tablas())
