import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


async def test():
    from sqlalchemy import select
    from app.core.database import AsyncSessionLocal
    from app.models.usuario import Usuario
    from app.models.paciente import Paciente
    import app.models.portal_paciente
    from app.models.portal_paciente import (
        CitaPaciente,
        SolicitudEstudio,
        PagoServicio,
        MensajePacienteMedico,
        RecordatorioMedicamento,
        ConfiguracionPortal,
    )

    async with AsyncSessionLocal() as db:
        # Verificar usuarios
        result = await db.execute(select(Usuario).limit(1))
        usuario = result.scalar_one_or_none()
        print(f"Usuario encontrado: {usuario.nombre if usuario else 'Ninguno'}")

        # Verificar pacientes
        result = await db.execute(select(Paciente).limit(1))
        paciente = result.scalar_one_or_none()
        print(f"Paciente encontrado: {paciente.nombre if paciente else 'Ninguno'}")

        # Verificar citas
        result = await db.execute(select(CitaPaciente))
        citas = result.scalars().all()
        print(f"Total citas: {len(citas)}")


asyncio.run(test())
