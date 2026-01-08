import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


async def verificar_pacientes():
    from sqlalchemy import select
    from app.core.database import AsyncSessionLocal
    from app.models.paciente import Paciente

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Paciente))
        pacientes = result.scalars().all()

        print(f"\n{'='*60}")
        print(f"PACIENTES EN LA BASE DE DATOS: {len(pacientes)}")
        print(f"{'='*60}\n")

        if len(pacientes) == 0:
            print("⚠️  NO HAY PACIENTES EN LA BASE DE DATOS")
            print("\nPara crear pacientes de prueba, ejecuta:")
            print("  python crear_pacientes_prueba.py")
        else:
            print("✅ Pacientes encontrados:\n")
            for i, p in enumerate(pacientes[:10], 1):
                print(
                    f"{i}. {p.nombre} {p.apellido_paterno} {p.apellido_materno or ''}"
                )
                print(f"   ID: {p.id}")
                print(f"   Expediente: {p.numero_expediente}")
                print()

            if len(pacientes) > 10:
                print(f"... y {len(pacientes) - 10} más")


if __name__ == "__main__":
    asyncio.run(verificar_pacientes())
