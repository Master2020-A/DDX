"""
Script para ejecutar la migración SQL de API Pública
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.core.database import engine


async def ejecutar_migracion():
    """Ejecutar migración SQL"""
    print("=" * 60)
    print("🚀 EJECUTANDO MIGRACIÓN DE API PÚBLICA")
    print("=" * 60)

    sql_file = Path(__file__).parent / "migrations" / "api_publica_marketplace.sql"

    if not sql_file.exists():
        print(f"❌ No se encontró el archivo: {sql_file}")
        return False

    print(f"\n📄 Leyendo archivo SQL...")
    with open(sql_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    print(f"✅ Archivo leído ({len(sql_content)} caracteres)")

    # Ejecutar todo el SQL en una sola transacción
    print(f"\n🔄 Ejecutando migración...")

    async with engine.begin() as conn:
        try:
            await conn.execute(text(sql_content))
            print("✅ Migración ejecutada exitosamente")
            return True
        except Exception as e:
            error_msg = str(e)
            if "already exists" in error_msg:
                print("⚠️  Las tablas ya existen, continuando...")
                return True
            else:
                print(f"❌ Error al ejecutar migración: {error_msg}")
                return False


async def poblar_datos():
    """Poblar datos de ejemplo"""
    print("\n📝 Poblando datos de ejemplo...")

    from app.models.api_publica import Plugin, EstadoPlugin
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        # Verificar si ya hay datos
        result = await db.execute(text("SELECT COUNT(*) FROM plugins"))
        count = result.scalar()

        if count > 0:
            print(f"ℹ️  Ya existen {count} plugins en la base de datos")
            return

        # Crear plugins de ejemplo
        plugins = [
            Plugin(
                nombre="Integración WhatsApp Business",
                slug="integracion-whatsapp",
                descripcion="Envía recordatorios de citas y resultados por WhatsApp",
                descripcion_larga="Plugin completo para integrar WhatsApp Business API con DDX.",
                autor="DDX Team",
                email_autor="plugins@ddx.com",
                version="1.2.0",
                categoria="comunicacion",
                tags=["whatsapp", "mensajeria", "notificaciones"],
                requiere_api_key=True,
                permisos_requeridos=["pacientes:read", "consultas:read"],
                estado=EstadoPlugin.APROBADO,
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
                tags=["pdf", "reportes", "documentos"],
                requiere_api_key=False,
                permisos_requeridos=["consultas:read"],
                estado=EstadoPlugin.APROBADO,
                verificado=True,
                descargas=5200,
                instalaciones_activas=1200,
                calificacion_promedio=4.9,
                total_calificaciones=234,
                es_gratuito=True,
            ),
            Plugin(
                nombre="Análisis Predictivo con ML",
                slug="analisis-predictivo-ml",
                descripcion="Predicciones de riesgo usando Machine Learning",
                autor="AI Health Labs",
                version="1.5.3",
                categoria="analisis",
                tags=["ml", "ia", "prediccion"],
                requiere_api_key=True,
                permisos_requeridos=[
                    "pacientes:read",
                    "consultas:read",
                    "laboratorio:read",
                ],
                estado=EstadoPlugin.APROBADO,
                verificado=True,
                descargas=1800,
                instalaciones_activas=320,
                calificacion_promedio=4.5,
                total_calificaciones=67,
                es_gratuito=False,
                precio_usd=99.0,
            ),
            Plugin(
                nombre="Dashboard de Métricas",
                slug="dashboard-metricas",
                descripcion="Visualiza KPIs y métricas del consultorio",
                autor="DataViz Pro",
                version="1.8.2",
                categoria="analisis",
                tags=["dashboard", "metricas", "kpi"],
                requiere_api_key=False,
                permisos_requeridos=["consultas:read"],
                estado=EstadoPlugin.APROBADO,
                verificado=True,
                descargas=3400,
                instalaciones_activas=890,
                calificacion_promedio=4.7,
                total_calificaciones=156,
                es_gratuito=True,
            ),
        ]

        for plugin in plugins:
            db.add(plugin)

        await db.commit()
        print(f"✅ Se crearon {len(plugins)} plugins de ejemplo")


async def main():
    """Función principal"""
    try:
        # Ejecutar migración
        if not await ejecutar_migracion():
            return

        # Poblar datos
        await poblar_datos()

        print("\n" + "=" * 60)
        print("✅ INSTALACIÓN COMPLETADA")
        print("=" * 60)
        print("\n📚 Próximos pasos:")
        print("1. Reinicia el servidor backend")
        print("2. Accede a http://localhost:8000/docs")
        print("3. Busca la sección 'API Pública'")
        print("4. Crea tu primera API Key desde el frontend")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
