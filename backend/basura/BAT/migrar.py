import asyncio
import sys
from pathlib import Path

# Agregar el directorio backend al path
sys.path.insert(0, str(Path(__file__).parent))


async def crear_tablas():
    print("=" * 70)
    print("📦 CREANDO TABLAS DEL MÓDULO DE INTEGRACIONES")
    print("=" * 70)

    from app.core.database import engine, Base
    from app.models.integraciones import (
        ConfiguracionIntegracion,
        ConfiguracionPACS,
        ConfiguracionLIS,
        RecetaElectronica,
        SolicitudFarmacia,
        FacturaElectronica,
        IntegracionERP,
        LogIntegracion,
    )

    print("\n📋 Creando tablas...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("\n✅ Tablas creadas exitosamente")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(crear_tablas())
