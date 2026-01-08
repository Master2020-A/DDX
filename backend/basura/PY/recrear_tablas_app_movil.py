"""
Script para eliminar y recrear las tablas del módulo de Aplicación Móvil
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


async def main():
    print("=" * 70)
    print("🔄 RECREANDO TABLAS DEL MÓDULO DE APLICACIÓN MÓVIL")
    print("=" * 70)

    from sqlalchemy import text
    from app.core.database import engine

    # Eliminar tablas en orden correcto (respetando foreign keys)
    print("\n🗑️  Eliminando tablas existentes...")

    tablas = [
        "sesiones_moviles",
        "sincronizacion_offline",
        "citas_moviles",
        "documentos_escaneados",
        "notificaciones_push",
        "configuracion_app_movil",
        "dispositivos_moviles",
    ]

    async with engine.begin() as conn:
        for tabla in tablas:
            try:
                await conn.execute(text(f"DROP TABLE IF EXISTS {tabla} CASCADE"))
                print(f"   ✓ {tabla} eliminada")
            except Exception as e:
                print(f"   ⚠️  {tabla}: {e}")

    print("\n✅ Tablas eliminadas")

    # Recrear tablas
    print("\n📦 Creando tablas nuevas...")

    from app.core.database import Base
    from app.models.app_movil import (
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

    print("✅ Tablas creadas exitosamente:")
    print("   • dispositivos_moviles")
    print("   • notificaciones_push (con dispositivo_id nullable)")
    print("   • documentos_escaneados")
    print("   • sincronizacion_offline")
    print("   • citas_moviles")
    print("   • configuracion_app_movil")
    print("   • sesiones_moviles")

    print("\n" + "=" * 70)
    print("✅ TABLAS RECREADAS EXITOSAMENTE")
    print("=" * 70)
    print("\n💡 Ahora ejecuta: python setup_app_movil_completo.py")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
