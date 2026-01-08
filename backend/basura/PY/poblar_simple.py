import asyncio
from app.core.database import AsyncSessionLocal
from app.models.hospitalizacion import Hospitalizacion, Cama
from app.models.interconsulta import Interconsulta
from app.models.paciente import Paciente
from app.models.usuario import Usuario
from sqlalchemy import select
from datetime import datetime
import uuid

async def main():
    async with AsyncSessionLocal() as db:
        # Obtener primer paciente y usuario
        result = await db.execute(select(Paciente).limit(1))
        paciente = result.scalar_one_or_none()
        
        result = await db.execute(select(Usuario).limit(1))
        usuario = result.scalar_one_or_none()
        
        result = await db.execute(select(Cama).limit(1))
        cama = result.scalar_one_or_none()
        
        print(f"Paciente: {paciente.id if paciente else 'NO ENCONTRADO'}")
        print(f"Usuario: {usuario.id if usuario else 'NO ENCONTRADO'}")
        print(f"Cama: {cama.numero_cama if cama else 'NO ENCONTRADA'}")
        
        if not paciente or not usuario or not cama:
            print("\n❌ Faltan datos básicos (pacientes, usuarios o camas)")
            return
        
        # Crear 1 hospitalización
        print("\nCreando hospitalización...")
        hosp = Hospitalizacion(
            id=uuid.uuid4(),
            paciente_id=paciente.id,
            medico_responsable_id=usuario.id,
            motivo_ingreso="Dolor abdominal agudo",
            diagnostico_ingreso="Apendicitis aguda",
            area_hospitalizacion="Urgencias",
            numero_cama=cama.numero_cama,
            estado='activo',
            prioridad='normal',
            tipo_ingreso='urgencia'
        )
        db.add(hosp)
        await db.commit()
        print("✅ Hospitalización creada")
        
        # Crear 1 interconsulta
        print("\nCreando interconsulta...")
        ic = Interconsulta(
            id=uuid.uuid4(),
            paciente_id=paciente.id,
            medico_solicitante_id=usuario.id,
            especialidad_requerida='Cardiología',
            motivo_solicitud='Evaluación cardiovascular',
            urgencia='normal',
            estado='solicitada'
        )
        db.add(ic)
        await db.commit()
        print("✅ Interconsulta creada")
        
        print("\n✅ COMPLETADO!")

asyncio.run(main())
