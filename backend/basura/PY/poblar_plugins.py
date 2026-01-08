"""Script simple para poblar plugins en el marketplace"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from app.models.api_publica import Plugin


async def poblar_plugins():
    """Poblar plugins de ejemplo"""
    print("📦 Poblando plugins en el marketplace...")

    async with AsyncSessionLocal() as db:
        try:
            # Verificar si ya hay plugins
            result = await db.execute(text("SELECT COUNT(*) FROM plugins"))
            count = result.scalar()

            if count > 0:
                print(f"ℹ️  Ya existen {count} plugins. Eliminando para repoblar...")
                await db.execute(text("DELETE FROM plugins"))
                await db.commit()

            plugins = [
                Plugin(
                    nombre="Integración WhatsApp Business",
                    slug="integracion-whatsapp",
                    descripcion="Envía recordatorios de citas y resultados por WhatsApp",
                    autor="DDX Team",
                    version="1.2.0",
                    categoria="comunicacion",
                    tags=["whatsapp", "mensajeria"],
                    requiere_api_key=True,
                    permisos_requeridos=["pacientes:read"],
                    estado="aprobado",
                    verificado=True,
                    descargas=2500,
                    instalaciones_activas=450,
                    calificacion_promedio=4.8,
                    total_calificaciones=89,
                    es_gratuito=False,
                    precio_usd=29.0,
                ),
                Plugin(
                    nombre="Exportador de Reportes PDF",
                    slug="exportador-reportes-pdf",
                    descripcion="Genera reportes médicos profesionales en PDF",
                    autor="MedTech Solutions",
                    version="2.0.1",
                    categoria="reportes",
                    tags=["pdf", "reportes"],
                    requiere_api_key=False,
                    permisos_requeridos=["consultas:read"],
                    estado="aprobado",
                    verificado=True,
                    descargas=5200,
                    instalaciones_activas=1200,
                    calificacion_promedio=4.9,
                    total_calificaciones=234,
                    es_gratuito=True,
                ),
                Plugin(
                    nombre="Dashboard de Métricas",
                    slug="dashboard-metricas",
                    descripcion="Visualiza métricas clave de tu consultorio en tiempo real",
                    autor="DataViz Pro",
                    version="1.8.2",
                    categoria="analisis",
                    tags=["dashboard", "metricas"],
                    requiere_api_key=False,
                    permisos_requeridos=["consultas:read"],
                    estado="aprobado",
                    verificado=True,
                    descargas=3400,
                    instalaciones_activas=890,
                    calificacion_promedio=4.7,
                    total_calificaciones=156,
                    es_gratuito=True,
                ),
                Plugin(
                    nombre="Integración con Google Calendar",
                    slug="google-calendar-sync",
                    descripcion="Sincroniza automáticamente las citas con Google Calendar",
                    autor="DDX Team",
                    version="2.1.0",
                    categoria="productividad",
                    tags=["calendario", "google", "citas"],
                    requiere_api_key=True,
                    permisos_requeridos=["citas:read", "citas:write"],
                    estado="aprobado",
                    verificado=True,
                    descargas=4200,
                    instalaciones_activas=890,
                    calificacion_promedio=4.7,
                    total_calificaciones=156,
                    es_gratuito=False,
                    precio_usd=19.99,
                ),
                Plugin(
                    nombre="Firma Digital de Recetas",
                    slug="firma-digital-recetas",
                    descripcion="Firma electrónica avanzada para recetas médicas",
                    autor="MedSecurity Inc",
                    version="3.0.5",
                    categoria="seguridad",
                    tags=["firma", "recetas", "seguridad"],
                    requiere_api_key=True,
                    permisos_requeridos=["recetas:write"],
                    estado="aprobado",
                    verificado=True,
                    descargas=8900,
                    instalaciones_activas=2100,
                    calificacion_promedio=4.9,
                    total_calificaciones=412,
                    es_gratuito=False,
                    precio_usd=49.99,
                ),
                Plugin(
                    nombre="Telemedicina Video HD",
                    slug="telemedicina-video",
                    descripcion="Consultas por videollamada en alta definición",
                    autor="TeleMed Solutions",
                    version="2.3.1",
                    categoria="comunicacion",
                    tags=["video", "telemedicina", "consulta"],
                    requiere_api_key=True,
                    permisos_requeridos=["consultas:read", "consultas:write"],
                    estado="aprobado",
                    verificado=True,
                    descargas=6700,
                    instalaciones_activas=1450,
                    calificacion_promedio=4.8,
                    total_calificaciones=289,
                    es_gratuito=False,
                    precio_usd=39.99,
                ),
            ]

            for plugin in plugins:
                db.add(plugin)

            await db.commit()
            print(f"✅ {len(plugins)} plugins agregados exitosamente")

        except Exception as e:
            print(f"❌ Error: {e}")
            await db.rollback()


async def main():
    print("=" * 60)
    print("🛍️ POBLAR MARKETPLACE CON PLUGINS")
    print("=" * 60)

    await poblar_plugins()

    print("\n" + "=" * 60)
    print("✅ PROCESO COMPLETADO")
    print("=" * 60)
    print("\n🔄 Recarga la página del frontend para ver los plugins")


if __name__ == "__main__":
    asyncio.run(main())
