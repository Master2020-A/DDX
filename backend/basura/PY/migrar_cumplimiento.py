"""
Script simplificado para crear las tablas del módulo de Cumplimiento Normativo
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.core.database import engine, Base
from app.models import (
    ConfiguracionCumplimiento,
    FirmaElectronica,
    ConsentimientoInformado,
    LogAccesoSensible,
    SolicitudDatosPersonales,
    AuditoriaHIPAA,
)


async def main():
    print("🔧 Creando tablas del módulo de Cumplimiento Normativo...")

    try:
        async with engine.begin() as conn:
            # Crear las tablas
            await conn.run_sync(Base.metadata.create_all)

        print("✅ Tablas creadas exitosamente:")
        print("   - configuracion_cumplimiento")
        print("   - firmas_electronicas")
        print("   - consentimientos_informados")
        print("   - logs_acceso_sensible")
        print("   - solicitudes_datos_personales")
        print("   - auditoria_hipaa")
        print("\n✅ Migración completada exitosamente")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
