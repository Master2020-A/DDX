"""
Script para crear las tablas del módulo de Integraciones
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


async def main():
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

    print("\n📋 Modelos a crear:")
    print("   • ConfiguracionIntegracion")
    print("   • ConfiguracionPACS")
    print("   • ConfiguracionLIS")
    print("   • RecetaElectronica")
    print("   • SolicitudFarmacia")
    print("   • FacturaElectronica")
    print("   • IntegracionERP")
    print("   • LogIntegracion")

    print("\n🔨 Creando tablas...")

    async with engine.begin() as conn:
        # Crear solo las tablas del módulo de integraciones
        await conn.run_sync(Base.metadata.create_all)

    print("\n✅ Tablas creadas exitosamente:")
    print("   ✓ configuraciones_integracion")
    print("   ✓ configuracion_pacs")
    print("   ✓ configuracion_lis")
    print("   ✓ recetas_electronicas")
    print("   ✓ solicitudes_farmacia")
    print("   ✓ facturas_electronicas")
    print("   ✓ integraciones_erp")
    print("   ✓ logs_integracion")

    print("\n" + "=" * 70)
    print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 70)
    print("\n💡 Próximos pasos:")
    print("   1. Configurar integraciones desde el panel de administración")
    print("   2. Probar conectividad con sistemas externos")
    print("   3. Revisar logs de integración")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
