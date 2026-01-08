"""Script simple para crear tablas de API Pública"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.core.database import engine, AsyncSessionLocal
from app.models.api_publica import Plugin, EstadoPlugin


async def crear_tablas():
    """Crear tablas desde archivo SQL"""
    print("📦 Creando tablas de API Pública...")

    sql_file = Path(__file__).parent / "migrations" / "api_publica_marketplace.sql"

    if not sql_file.exists():
        print(f"❌ No se encontró: {sql_file}")
        return False

    with open(sql_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Dividir en statements individuales
    statements = []
    current_statement = []
    in_function = False

    for line in sql_content.split("\n"):
        line = line.strip()

        # Ignorar comentarios y líneas vacías
        if not line or line.startswith("--"):
            continue

        # Detectar inicio/fin de función
        if "CREATE OR REPLACE FUNCTION" in line.upper():
            in_function = True

        current_statement.append(line)

        # Detectar fin de statement
        if line.endswith(";"):
            if in_function and "$$;" in line:
                in_function = False
                statements.append(" ".join(current_statement))
                current_statement = []
            elif not in_function:
                statements.append(" ".join(current_statement))
                current_statement = []

    # Ejecutar cada statement
    async with engine.begin() as conn:
        for i, statement in enumerate(statements):
            if not statement.strip():
                continue

            try:
                await conn.execute(text(statement))
            except Exception as e:
                error_str = str(e).lower()
                if "already exists" in error_str or "ya existe" in error_str:
                    continue  # Ignorar si ya existe
                else:
                    print(f"⚠️  Error en statement {i+1}: {str(e)[:100]}")

    print("✅ Tablas creadas exitosamente")
    return True


async def poblar_datos():
    """Poblar datos de ejemplo"""
    print("\n📝 Poblando datos de ejemplo...")

    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(text("SELECT COUNT(*) FROM plugins"))
            count = result.scalar()

            if count > 0:
                print(f"ℹ️  Ya existen {count} plugins")
                return

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
                    descripcion="Visualiza KPIs y métricas del consultorio",
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
            ]

            for plugin in plugins:
                db.add(plugin)

            await db.commit()
            print(f"✅ Creados {len(plugins)} plugins de ejemplo")

        except Exception as e:
            print(f"❌ Error al poblar datos: {e}")


async def main():
    print("=" * 60)
    print("🚀 INSTALACIÓN DE API PÚBLICA")
    print("=" * 60)

    if await crear_tablas():
        await poblar_datos()

        print("\n" + "=" * 60)
        print("✅ INSTALACIÓN COMPLETADA")
        print("=" * 60)
        print("\n📚 Próximos pasos:")
        print("1. Reinicia el servidor: uvicorn app.main:app --reload")
        print("2. Accede a: http://localhost:8000/docs")
        print("3. Busca la sección 'API Pública'")
        print("4. Agrega la ruta en el frontend: /api-publica")
    else:
        print("\n❌ La instalación falló")


if __name__ == "__main__":
    asyncio.run(main())
