"""
Script de prueba para crear tablas de app móvil
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


async def main():
    print("Iniciando creación de tablas...")

    try:
        from app.core.database import engine, Base
        from app.models import (
            DispositivoMovil,
            NotificacionPush,
            DocumentoEscaneado,
            SincronizacionOffline,
            CitaMovil,
            ConfiguracionAppMovil,
            SesionMovil,
        )

        print("Modelos importados correctamente")

        async with engine.begin() as conn:
            print("Creando tablas...")
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Tablas creadas exitosamente")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
