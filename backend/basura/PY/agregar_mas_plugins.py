"""Script para agregar más plugins al marketplace"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from app.models.api_publica import Plugin, EstadoPlugin


async def agregar_plugins():
    """Agregar más plugins de ejemplo al marketplace"""
    print("📦 Agregando más plugins al marketplace...")

    async with AsyncSessionLocal() as db:
        try:
            # Verificar cuántos plugins hay
            result = await db.execute(text("SELECT COUNT(*) FROM plugins"))
            count = result.scalar()
            print(f"ℹ️  Plugins actuales: {count}")

            nuevos_plugins = [
                Plugin(
                    nombre="Integración con Google Calendar",
                    slug="google-calendar-sync",
                    descripcion="Sincroniza automáticamente las citas con Google Calendar. Envía notificaciones y recordatorios.",
                    autor="DDX Team",
                    version="2.1.0",
                    categoria="productividad",
                    tags=["calendario", "google", "citas", "sincronizacion"],
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
                    url_repositorio="https://github.com/ddx/google-calendar-plugin",
                    url_documentacion="https://docs.ddx.com/plugins/google-calendar",
                ),
                Plugin(
                    nombre="Firma Digital de Recetas",
                    slug="firma-digital-recetas",
                    descripcion="Firma electrónica avanzada para recetas médicas. Cumple con NOM-024-SSA3-2012.",
                    autor="MedSecurity Inc",
                    version="3.0.5",
                    categoria="seguridad",
                    tags=["firma", "recetas", "seguridad", "nom"],
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
                    url_repositorio="https://github.com/medsecurity/firma-digital",
                    url_documentacion="https://docs.medsecurity.com/firma-digital",
                ),
                Plugin(
                    nombre="Análisis de Imágenes con IA",
                    slug="ai-image-analysis",
                    descripcion="Análisis automático de radiografías, tomografías y resonancias usando IA. Detecta anomalías y genera reportes preliminares.",
                    autor="AI MedTech",
                    version="1.5.2",
                    categoria="analisis",
                    tags=["ia", "imagenes", "diagnostico", "radiologia"],
                    requiere_api_key=True,
                    permisos_requeridos=["estudios:read", "estudios:write"],
                    estado="aprobado",
                    verificado=True,
                    descargas=3400,
                    instalaciones_activas=670,
                    calificacion_promedio=4.6,
                    total_calificaciones=98,
                    es_gratuito=False,
                    precio_usd=99.99,
                    url_repositorio="https://github.com/aimedtech/image-analysis",
                    url_documentacion="https://docs.aimedtech.com/analysis",
                ),
                Plugin(
                    nombre="Telemedicina Video HD",
                    slug="telemedicina-video",
                    descripcion="Consultas por videollamada en alta definición. Incluye grabación de sesiones, compartir pantalla y chat.",
                    autor="TeleMed Solutions",
                    version="2.3.1",
                    categoria="comunicacion",
                    tags=["video", "telemedicina", "consulta", "remoto"],
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
                    url_repositorio="https://github.com/telemed/video-plugin",
                    url_documentacion="https://docs.telemed.com/video",
                ),
                Plugin(
                    nombre="Recordatorios SMS",
                    slug="sms-reminders",
                    descripcion="Envía recordatorios de citas por SMS. Reduce el ausentismo hasta en 40%.",
                    autor="DDX Team",
                    version="1.8.0",
                    categoria="comunicacion",
                    tags=["sms", "recordatorios", "citas", "notificaciones"],
                    requiere_api_key=True,
                    permisos_requeridos=["pacientes:read", "citas:read"],
                    estado="aprobado",
                    verificado=True,
                    descargas=5600,
                    instalaciones_activas=1200,
                    calificacion_promedio=4.7,
                    total_calificaciones=234,
                    es_gratuito=False,
                    precio_usd=14.99,
                    url_repositorio="https://github.com/ddx/sms-reminders",
                    url_documentacion="https://docs.ddx.com/plugins/sms",
                ),
                Plugin(
                    nombre="Inventario de Medicamentos",
                    slug="inventario-medicamentos",
                    descripcion="Control completo de inventario de medicamentos. Alertas de stock bajo, caducidad y reorden automático.",
                    autor="PharmaTech",
                    version="2.0.0",
                    categoria="gestion",
                    tags=["inventario", "medicamentos", "farmacia", "stock"],
                    requiere_api_key=False,
                    permisos_requeridos=["inventario:read", "inventario:write"],
                    estado="aprobado",
                    verificado=True,
                    descargas=4100,
                    instalaciones_activas=780,
                    calificacion_promedio=4.5,
                    total_calificaciones=167,
                    es_gratuito=True,
                    url_repositorio="https://github.com/pharmatech/inventario",
                    url_documentacion="https://docs.pharmatech.com/inventario",
                ),
                Plugin(
                    nombre="Expediente Clínico Electrónico Plus",
                    slug="ece-plus",
                    descripcion="Expediente clínico electrónico avanzado con plantillas personalizables, firmas digitales y cumplimiento NOM-004.",
                    autor="HealthIT Pro",
                    version="4.2.1",
                    categoria="gestion",
                    tags=["expediente", "ece", "nom", "historico"],
                    requiere_api_key=False,
                    permisos_requeridos=["pacientes:read", "consultas:read"],
                    estado="aprobado",
                    verificado=True,
                    descargas=7800,
                    instalaciones_activas=1890,
                    calificacion_promedio=4.9,
                    total_calificaciones=456,
                    es_gratuito=False,
                    precio_usd=59.99,
                    url_repositorio="https://github.com/healthit/ece-plus",
                    url_documentacion="https://docs.healthit.com/ece",
                ),
                Plugin(
                    nombre="Integración con Laboratorios",
                    slug="lab-integration",
                    descripcion="Conecta con laboratorios externos para recibir resultados automáticamente. Compatible con Chopo, Polanco y más.",
                    autor="LabConnect",
                    version="1.9.3",
                    categoria="integracion",
                    tags=["laboratorio", "resultados", "integracion", "api"],
                    requiere_api_key=True,
                    permisos_requeridos=["laboratorio:read", "laboratorio:write"],
                    estado="aprobado",
                    verificado=True,
                    descargas=3900,
                    instalaciones_activas=650,
                    calificacion_promedio=4.6,
                    total_calificaciones=123,
                    es_gratuito=False,
                    precio_usd=34.99,
                    url_repositorio="https://github.com/labconnect/integration",
                    url_documentacion="https://docs.labconnect.com/ddx",
                ),
                Plugin(
                    nombre="Estadísticas y Reportes Avanzados",
                    slug="advanced-analytics",
                    descripcion="Dashboards interactivos con métricas clave, gráficas personalizables y exportación a Excel/PDF.",
                    autor="DataViz Pro",
                    version="3.1.0",
                    categoria="analisis",
                    tags=["estadisticas", "reportes", "dashboard", "metricas"],
                    requiere_api_key=False,
                    permisos_requeridos=["consultas:read", "pacientes:read"],
                    estado="aprobado",
                    verificado=True,
                    descargas=5400,
                    instalaciones_activas=1100,
                    calificacion_promedio=4.8,
                    total_calificaciones=267,
                    es_gratuito=True,
                    url_repositorio="https://github.com/dataviz/analytics",
                    url_documentacion="https://docs.dataviz.com/analytics",
                ),
                Plugin(
                    nombre="Backup Automático en la Nube",
                    slug="cloud-backup",
                    descripcion="Respaldos automáticos cifrados en Google Drive, Dropbox o AWS S3. Recuperación en un click.",
                    autor="CloudSafe",
                    version="2.5.0",
                    categoria="seguridad",
                    tags=["backup", "nube", "seguridad", "respaldo"],
                    requiere_api_key=True,
                    permisos_requeridos=["admin"],
                    estado="aprobado",
                    verificado=True,
                    descargas=6200,
                    instalaciones_activas=1340,
                    calificacion_promedio=4.9,
                    total_calificaciones=312,
                    es_gratuito=False,
                    precio_usd=24.99,
                    url_repositorio="https://github.com/cloudsafe/backup",
                    url_documentacion="https://docs.cloudsafe.com/backup",
                ),
            ]

            for plugin in nuevos_plugins:
                db.add(plugin)

            await db.commit()
            print(f"✅ Agregados {len(nuevos_plugins)} plugins nuevos")
            print(f"📊 Total de plugins ahora: {count + len(nuevos_plugins)}")

        except Exception as e:
            print(f"❌ Error al agregar plugins: {e}")
            await db.rollback()


async def main():
    print("=" * 60)
    print("🛍️ AGREGAR MÁS PLUGINS AL MARKETPLACE")
    print("=" * 60)

    await agregar_plugins()

    print("\n" + "=" * 60)
    print("✅ PROCESO COMPLETADO")
    print("=" * 60)
    print("\n📚 Recarga la página del frontend para ver los nuevos plugins")


if __name__ == "__main__":
    asyncio.run(main())
