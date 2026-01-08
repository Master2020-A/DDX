"""
Verificar si las tablas de app móvil existen
"""

import asyncio
from sqlalchemy import text
from app.core.database import engine


async def main():
    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%movil%'
            ORDER BY table_name;
        """
            )
        )

        tablas = result.fetchall()

        if tablas:
            print("✅ Tablas de app móvil encontradas:")
            for tabla in tablas:
                print(f"   - {tabla[0]}")
        else:
            print("❌ No se encontraron tablas de app móvil")
            print("\nCreando tablas...")

            from app.core.database import Base
            from app.models import (
                DispositivoMovil,
                NotificacionPush,
                DocumentoEscaneado,
                SincronizacionOffline,
                CitaMovil,
                ConfiguracionAppMovil,
                SesionMovil,
            )

            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            print("✅ Tablas creadas exitosamente")


if __name__ == "__main__":
    asyncio.run(main())
