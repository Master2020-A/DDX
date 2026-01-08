import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


async def test():
    from sqlalchemy import text
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        # Verificar tabla
        result = await db.execute(
            text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'citas_pacientes')"
            )
        )
        existe = result.scalar()
        print(f"Tabla citas_pacientes existe: {existe}")

        if not existe:
            print("Ejecutando crear_tablas_portal.py...")
            import subprocess

            subprocess.run([sys.executable, "crear_tablas_portal.py"], check=True)
            print("Tablas creadas. Ejecutando poblado...")
            subprocess.run([sys.executable, "poblar_portal_paciente.py"], check=True)
        else:
            print("Ejecutando poblado...")
            subprocess.run([sys.executable, "poblar_portal_paciente.py"], check=True)


asyncio.run(test())

print("Python ejecutándose correctamente")
print(f"Python version: {sys.version}")
print(f"Path: {sys.executable}")

try:
    from app.models.historia_clinica import HistoriaClinicaPediatrica

    print("✅ Modelos importados correctamente")
except Exception as e:
    print(f"❌ Error al importar modelos: {e}")

print("\nPara generar datos, asegúrate de que:")
print("1. PostgreSQL esté corriendo")
print("2. El archivo .env tenga las credenciales correctas")
print("3. Las tablas hayan sido creadas con la migración")
