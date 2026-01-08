import asyncio
import sys
from pathlib import Path
from datetime import datetime, date

sys.path.insert(0, str(Path(__file__).parent))


async def crear_pacientes():
    from sqlalchemy import select
    from app.core.database import AsyncSessionLocal
    from app.models.paciente import Paciente
    import random
    import string

    def generar_expediente():
        year = "2024"
        random_part = "".join(random.choices(string.digits, k=6))
        return f"EXP-{year}-{random_part}"

    async with AsyncSessionLocal() as db:
        # Verificar si ya hay pacientes
        result = await db.execute(select(Paciente))
        pacientes_existentes = result.scalars().all()

        if len(pacientes_existentes) > 0:
            print(
                f"\n✅ Ya existen {len(pacientes_existentes)} pacientes en la base de datos"
            )
            print("\nPrimeros 5 pacientes:")
            for p in pacientes_existentes[:5]:
                print(f"  - {p.nombre} {p.apellido_paterno} (ID: {p.id})")
            return

        print("\n📝 Creando pacientes de prueba...")

        pacientes_data = [
            {
                "nombre": "Juan Carlos",
                "apellido_paterno": "García",
                "apellido_materno": "López",
                "fecha_nacimiento": date(1985, 3, 15),
                "sexo": "M",
                "curp": "GALJ850315HDFRPN01",
                "telefono": "5551234567",
                "email": "juan.garcia@email.com",
            },
            {
                "nombre": "María Elena",
                "apellido_paterno": "Martínez",
                "apellido_materno": "Hernández",
                "fecha_nacimiento": date(1990, 7, 22),
                "sexo": "F",
                "curp": "MAHM900722MDFRRR02",
                "telefono": "5559876543",
                "email": "maria.martinez@email.com",
            },
            {
                "nombre": "Pedro",
                "apellido_paterno": "Sánchez",
                "apellido_materno": "Ramírez",
                "fecha_nacimiento": date(1978, 11, 8),
                "sexo": "M",
                "curp": "SARP781108HDFSND03",
                "telefono": "5552345678",
                "email": "pedro.sanchez@email.com",
            },
            {
                "nombre": "Ana Laura",
                "apellido_paterno": "Rodríguez",
                "apellido_materno": "Torres",
                "fecha_nacimiento": date(1995, 5, 30),
                "sexo": "F",
                "curp": "ROTA950530MDFDRN04",
                "telefono": "5558765432",
                "email": "ana.rodriguez@email.com",
            },
            {
                "nombre": "Luis Fernando",
                "apellido_paterno": "González",
                "apellido_materno": "Flores",
                "fecha_nacimiento": date(1982, 9, 12),
                "sexo": "M",
                "curp": "GOFL820912HDFLRS05",
                "telefono": "5553456789",
                "email": "luis.gonzalez@email.com",
            },
            {
                "nombre": "Carmen",
                "apellido_paterno": "Pérez",
                "apellido_materno": "Morales",
                "fecha_nacimiento": date(1988, 2, 18),
                "sexo": "F",
                "curp": "PEMC880218MDFRRL06",
                "telefono": "5557654321",
                "email": "carmen.perez@email.com",
            },
            {
                "nombre": "Roberto",
                "apellido_paterno": "Jiménez",
                "apellido_materno": "Castro",
                "fecha_nacimiento": date(1975, 12, 25),
                "sexo": "M",
                "curp": "JICR751225HDFSBT07",
                "telefono": "5554567890",
                "email": "roberto.jimenez@email.com",
            },
            {
                "nombre": "Sofía",
                "apellido_paterno": "Díaz",
                "apellido_materno": "Ruiz",
                "fecha_nacimiento": date(1992, 4, 7),
                "sexo": "F",
                "curp": "DIRS920407MDFZFR08",
                "telefono": "5556543210",
                "email": "sofia.diaz@email.com",
            },
        ]

        for data in pacientes_data:
            paciente = Paciente(numero_expediente=generar_expediente(), **data)
            db.add(paciente)

        await db.commit()

        # Verificar creación
        result = await db.execute(select(Paciente))
        pacientes = result.scalars().all()

        print(f"\n✅ {len(pacientes)} pacientes creados exitosamente:\n")
        for p in pacientes:
            print(f"  - {p.nombre} {p.apellido_paterno} {p.apellido_materno or ''}")
            print(f"    Expediente: {p.numero_expediente}")
            print(f"    ID: {p.id}\n")


if __name__ == "__main__":
    asyncio.run(crear_pacientes())
