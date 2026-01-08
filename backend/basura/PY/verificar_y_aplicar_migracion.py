"""Script para verificar y aplicar migración del Portal del Paciente"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


async def main():
    from sqlalchemy import text
    from app.core.database import AsyncSessionLocal

    print("=" * 70)
    print("🔍 VERIFICANDO ESTADO DE LA BASE DE DATOS")
    print("=" * 70)

    async with AsyncSessionLocal() as db:
        # 1. Verificar versión de Alembic
        try:
            result = await db.execute(text("SELECT version_num FROM alembic_version"))
            version = result.scalar_one_or_none()
            print(f"\n✅ Versión actual de Alembic: {version}")
        except Exception as e:
            print(f"\n❌ Error al obtener versión de Alembic: {e}")

        # 2. Verificar si existe la tabla citas_pacientes
        try:
            result = await db.execute(
                text(
                    """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'citas_pacientes'
                )
            """
                )
            )
            existe = result.scalar()

            if existe:
                print("✅ La tabla 'citas_pacientes' existe")
            else:
                print("❌ La tabla 'citas_pacientes' NO existe")
                print("\n⚠️  La migración no se aplicó correctamente.")
                print("   Ejecuta: alembic upgrade head")
        except Exception as e:
            print(f"❌ Error al verificar tabla: {e}")

        # 3. Listar todas las tablas del portal
        try:
            result = await db.execute(
                text(
                    """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND (
                    table_name LIKE '%citas%' OR
                    table_name LIKE '%solicitud%' OR
                    table_name LIKE '%pago%' OR
                    table_name LIKE '%mensaje%' OR
                    table_name LIKE '%recordatorio%' OR
                    table_name LIKE '%configuracion_portal%' OR
                    table_name LIKE '%acceso%'
                )
                ORDER BY table_name
            """
                )
            )

            tables = result.fetchall()
            if tables:
                print(
                    f"\n📋 Tablas del Portal del Paciente encontradas ({len(tables)}):"
                )
                for table in tables:
                    print(f"   ✓ {table[0]}")
            else:
                print("\n⚠️  No se encontraron tablas del Portal del Paciente")
        except Exception as e:
            print(f"❌ Error al listar tablas: {e}")

    print("\n" + "=" * 70)


asyncio.run(main())
