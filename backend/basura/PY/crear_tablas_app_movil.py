"""
Script para crear las tablas del módulo de Aplicación Móvil
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

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


async def main():
    print("🔧 Creando tablas del módulo de Aplicación Móvil...")

    try:
        async with engine.begin() as conn:
            # Crear las tablas
            await conn.run_sync(Base.metadata.create_all)

        print("✅ Tablas creadas exitosamente:")
        print("   - dispositivos_moviles")
        print("   - notificaciones_push")
        print("   - documentos_escaneados")
        print("   - sincronizacion_offline")
        print("   - citas_moviles")
        print("   - configuracion_app_movil")
        print("   - sesiones_moviles")
        print("\n✅ Migración completada exitosamente")
        print("\n📝 Próximos pasos:")
        print("   1. Configurar Firebase Cloud Messaging (FCM) para Android")
        print("   2. Configurar Apple Push Notification Service (APNs) para iOS")
        print("   3. Instalar Tesseract OCR para escaneo de documentos:")
        print("      - Linux: sudo apt-get install tesseract-ocr")
        print("      - macOS: brew install tesseract")
        print(
            "      - Windows: Descargar desde https://github.com/UB-Mannheim/tesseract/wiki"
        )
        print("   4. Configurar variables de entorno:")
        print(
            "      - FIREBASE_CREDENTIALS_PATH: Ruta al archivo de credenciales de Firebase"
        )
        print("      - APNS_KEY_PATH: Ruta a la clave privada de APNs")
        print("      - APNS_KEY_ID: ID de la clave de APNs")
        print("      - APNS_TEAM_ID: ID del equipo de Apple Developer")
        print("   5. Desarrollar aplicaciones móviles nativas (iOS/Android)")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
