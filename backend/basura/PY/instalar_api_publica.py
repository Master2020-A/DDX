"""
Script de instalación para el sistema de API Pública y Marketplace
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.core.database import engine, AsyncSessionLocal
from app.models.api_publica import (
    APIKey,
    LogAPIPublica,
    Webhook,
    EntregaWebhook,
    Plugin,
    InstalacionPlugin,
    ResenaPlugin,
    EstadoPlugin,
)


async def crear_tablas():
    """Crear tablas de API Pública"""
    print("📦 Creando tablas de API Pública...")

    async with engine.begin() as conn:
        # Leer y ejecutar el archivo SQL
        sql_file = Path(__file__).parent / "migrations" / "api_publica_marketplace.sql"

        if not sql_file.exists():
            print("❌ No se encontró el archivo de migración SQL")
            return False

        with open(sql_file, "r", encoding="utf-8") as f:
            sql_content = f.read()

        # Ejecutar cada statement
        for statement in sql_content.split(";"):
            statement = statement.strip()
            if statement and not statement.startswith("--"):
                try:
                    await conn.execute(text(statement))
                except Exception as e:
                    # Ignorar errores de tablas que ya existen
                    if "already exists" not in str(e):
                        print(f"⚠️  Error en statement: {str(e)[:100]}")

    print("✅ Tablas creadas exitosamente")
    return True


async def poblar_datos_ejemplo():
    """Poblar datos de ejemplo"""
    print("\n📝 Poblando datos de ejemplo...")

    async with AsyncSessionLocal() as db:
        # Verificar si ya hay datos
        result = await db.execute(text("SELECT COUNT(*) FROM plugins"))
        count = result.scalar()

        if count > 0:
            print("ℹ️  Ya existen datos en la base de datos")
            return

        # Crear plugins de ejemplo
        plugins_ejemplo = [
            Plugin(
                nombre="Integración WhatsApp Business",
                slug="integracion-whatsapp",
                descripcion="Envía recordatorios de citas y resultados por WhatsApp",
                descripcion_larga="Plugin completo para integrar WhatsApp Business API con DDX. Envía recordatorios automáticos de citas, notificaciones de resultados de laboratorio, y permite comunicación bidireccional con pacientes.",
                autor="DDX Team",
                email_autor="plugins@ddx.com",
                version="1.2.0",
                version_minima_ddx="1.0.0",
                categoria="comunicacion",
                tags=["whatsapp", "mensajeria", "notificaciones", "recordatorios"],
                url_repositorio="https://github.com/ddx/plugin-whatsapp",
                url_documentacion="https://docs.ddx.com/plugins/whatsapp",
                requiere_api_key=True,
                permisos_requeridos=["pacientes:read", "consultas:read"],
                estado=EstadoPlugin.APROBADO,
                verificado=True,
                descargas=2500,
                instalaciones_activas=450,
                calificacion_promedio=5,
                total_calificaciones=89,
                es_gratuito=False,
                precio_usd=29,
            ),
            Plugin(
                nombre="Exportador de Reportes PDF",
                slug="exportador-reportes-pdf",
                descripcion="Genera reportes médicos profesionales en PDF",
                descripcion_larga="Crea reportes médicos personalizados con tu logo, firma digital y formato profesional. Incluye plantillas para consultas, laboratorios, estudios de imagen y más.",
                autor="MedTech Solutions",
                email_autor="contact@medtech.com",
                version="2.0.1",
                categoria="reportes",
                tags=["pdf", "reportes", "documentos", "impresion"],
                url_repositorio="https://github.com/medtech/ddx-pdf-exporter",
                url_documentacion="https://medtech.com/ddx-plugin-docs",
                requiere_api_key=False,
                permisos_requeridos=["consultas:read", "laboratorio:read"],
                estado=EstadoPlugin.APROBADO,
                verificado=True,
                descargas=5200,
                instalaciones_activas=1200,
                calificacion_promedio=5,
                total_calificaciones=234,
                es_gratuito=True,
            ),
            Plugin(
                nombre="Análisis Predictivo con ML",
                slug="analisis-predictivo-ml",
                descripcion="Predicciones de riesgo usando Machine Learning",
                descripcion_larga="Utiliza modelos de Machine Learning para predecir riesgos de enfermedades crónicas, readmisiones hospitalarias y complicaciones. Basado en datos históricos del paciente.",
                autor="AI Health Labs",
                email_autor="info@aihealth.io",
                version="1.5.3",
                categoria="analisis",
                tags=["ml", "ia", "prediccion", "riesgo", "analytics"],
                url_repositorio="https://github.com/aihealth/ddx-ml-predictor",
                url_documentacion="https://aihealth.io/docs",
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
                calificacion_promedio=4,
                total_calificaciones=67,
                es_gratuito=False,
                precio_usd=99,
            ),
            Plugin(
                nombre="Integración con SAP",
                slug="integracion-sap",
                descripcion="Sincroniza datos con SAP ERP",
                descripcion_larga="Integración bidireccional con SAP para sincronizar pacientes, servicios, facturación e inventarios. Compatible con SAP S/4HANA y SAP Business One.",
                autor="Enterprise Integrations Inc",
                email_autor="sales@entint.com",
                version="3.1.0",
                categoria="integracion",
                tags=["sap", "erp", "enterprise", "facturacion"],
                url_repositorio="https://github.com/entint/ddx-sap-connector",
                requiere_api_key=True,
                permisos_requeridos=[
                    "pacientes:read",
                    "pacientes:write",
                    "facturacion:read",
                    "facturacion:write",
                ],
                estado=EstadoPlugin.APROBADO,
                verificado=True,
                descargas=450,
                instalaciones_activas=85,
                calificacion_promedio=4,
                total_calificaciones=23,
                es_gratuito=False,
                precio_usd=299,
            ),
            Plugin(
                nombre="Dashboard de Métricas",
                slug="dashboard-metricas",
                descripcion="Visualiza KPIs y métricas del consultorio",
                descripcion_larga="Dashboard interactivo con métricas clave: pacientes atendidos, ingresos, ocupación, satisfacción del paciente, y más. Incluye gráficas en tiempo real y exportación a Excel.",
                autor="DataViz Pro",
                email_autor="hello@datavizpro.com",
                version="1.8.2",
                categoria="analisis",
                tags=["dashboard", "metricas", "kpi", "analytics", "reportes"],
                requiere_api_key=False,
                permisos_requeridos=["consultas:read", "facturacion:read"],
                estado=EstadoPlugin.APROBADO,
                verificado=True,
                descargas=3400,
                instalaciones_activas=890,
                calificacion_promedio=5,
                total_calificaciones=156,
                es_gratuito=True,
            ),
            Plugin(
                nombre="Firma Digital Avanzada",
                slug="firma-digital-avanzada",
                descripcion="Firma electrónica avanzada con validez legal",
                descripcion_larga="Implementa firma electrónica avanzada (FIEL) con validez legal en México. Compatible con certificados del SAT. Firma recetas, consentimientos informados y documentos médicos.",
                autor="SecureSign MX",
                email_autor="soporte@securesign.mx",
                version="2.3.0",
                categoria="seguridad",
                tags=["firma", "fiel", "seguridad", "legal", "sat"],
                url_documentacion="https://securesign.mx/ddx-docs",
                requiere_api_key=True,
                permisos_requeridos=["recetas:write"],
                estado=EstadoPlugin.APROBADO,
                verificado=True,
                descargas=1200,
                instalaciones_activas=340,
                calificacion_promedio=5,
                total_calificaciones=78,
                es_gratuito=False,
                precio_usd=49,
            ),
        ]

        for plugin in plugins_ejemplo:
            db.add(plugin)

        await db.commit()
        print(f"✅ Se crearon {len(plugins_ejemplo)} plugins de ejemplo")


async def main():
    """Función principal"""
    print("=" * 60)
    print("🚀 INSTALACIÓN DE API PÚBLICA Y MARKETPLACE")
    print("=" * 60)

    try:
        # Crear tablas
        if not await crear_tablas():
            return

        # Poblar datos de ejemplo
        await poblar_datos_ejemplo()

        print("\n" + "=" * 60)
        print("✅ INSTALACIÓN COMPLETADA")
        print("=" * 60)
        print("\n📚 Próximos pasos:")
        print("1. Reinicia el servidor backend")
        print("2. Accede a /api-publica en el frontend")
        print("3. Crea tu primera API Key")
        print("4. Lee la documentación en DOCUMENTACION_API_PUBLICA.md")
        print("\n🔗 Endpoints disponibles:")
        print("   - POST /api-publica/keys (Crear API Key)")
        print("   - GET  /api-publica/marketplace/plugins (Listar plugins)")
        print("   - POST /api-publica/webhooks (Crear webhook)")
        print("\n📖 Documentación interactiva:")
        print("   - http://localhost:8000/docs (Swagger UI)")
        print("   - http://localhost:8000/redoc (ReDoc)")

    except Exception as e:
        print(f"\n❌ Error durante la instalación: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
