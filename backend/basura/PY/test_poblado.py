"""
Script simple para probar el poblado de integraciones
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


async def main():
    try:
        print("\n" + "=" * 70)
        print("🧪 PROBANDO IMPORTACIONES Y CONEXIÓN A BD")
        print("=" * 70)

        from sqlalchemy import select, func
        from app.core.database import AsyncSessionLocal

        print("✅ Importaciones básicas OK")

        # Importar TODOS los modelos
        import app.models.telemedicina
        import app.models.ia_medica
        import app.models.paciente
        import app.models.usuario
        import app.models.integraciones

        print("✅ Modelos importados OK")

        from app.models.usuario import Usuario
        from app.models.paciente import Paciente
        from app.models.integraciones import (
            ConfiguracionIntegracion,
            RecetaElectronica,
            SolicitudFarmacia,
            FacturaElectronica,
        )

        print("✅ Clases específicas importadas OK")

        async with AsyncSessionLocal() as db:
            # Probar consulta simple
            result = await db.execute(select(func.count(Usuario.id)))
            usuarios_count = result.scalar()

            result = await db.execute(select(func.count(Paciente.id)))
            pacientes_count = result.scalar()

            result = await db.execute(select(func.count(ConfiguracionIntegracion.id)))
            configs_count = result.scalar()

            print(f"\n📊 Estado actual de la BD:")
            print(f"   Usuarios: {usuarios_count}")
            print(f"   Pacientes: {pacientes_count}")
            print(f"   Configuraciones: {configs_count}")

            if usuarios_count == 0 or pacientes_count == 0:
                print(
                    "\n⚠️  ADVERTENCIA: Se necesitan usuarios y pacientes para poblar integraciones"
                )
                print(
                    "   Ejecuta primero los scripts de poblado de usuarios y pacientes"
                )
            else:
                print("\n✅ La BD tiene datos suficientes para poblar integraciones")

            print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
