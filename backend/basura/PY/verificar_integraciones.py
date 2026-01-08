"""
Script para verificar datos de integraciones
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


async def main():
    from sqlalchemy import select, func
    from app.core.database import AsyncSessionLocal

    # Importar modelos
    import app.models.telemedicina
    import app.models.paciente
    import app.models.usuario
    import app.models.integraciones

    from app.models.integraciones import (
        ConfiguracionIntegracion,
        RecetaElectronica,
        SolicitudFarmacia,
        FacturaElectronica,
    )

    async with AsyncSessionLocal() as db:
        try:
            # Contar configuraciones
            result = await db.execute(select(func.count(ConfiguracionIntegracion.id)))
            configs_count = result.scalar()

            # Contar recetas
            result = await db.execute(select(func.count(RecetaElectronica.id)))
            recetas_count = result.scalar()

            # Contar solicitudes
            result = await db.execute(select(func.count(SolicitudFarmacia.id)))
            solicitudes_count = result.scalar()

            # Contar facturas
            result = await db.execute(select(func.count(FacturaElectronica.id)))
            facturas_count = result.scalar()

            print("\n" + "=" * 70)
            print("📊 ESTADO DEL MÓDULO DE INTEGRACIONES")
            print("=" * 70)
            print(f"\n✅ Configuraciones: {configs_count}")
            print(f"✅ Recetas Electrónicas: {recetas_count}")
            print(f"✅ Solicitudes de Farmacia: {solicitudes_count}")
            print(f"✅ Facturas Electrónicas: {facturas_count}")
            print("\n" + "=" * 70)

            if configs_count > 0 or recetas_count > 0:
                print("✅ El módulo tiene datos!")
            else:
                print(
                    "⚠️  El módulo está vacío. Ejecuta: python poblar_integraciones.py"
                )
            print("=" * 70 + "\n")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
