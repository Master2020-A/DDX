"""Poblar con el modelo simplificado"""
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.hospitalizacion_simple import HospitalizacionSimple
from app.models.interconsulta import Interconsulta
from app.models.paciente import Paciente
from app.models.usuario import Usuario
from app.models.hospitalizacion import Cama
from sqlalchemy import select
import uuid

async def main():
    async with AsyncSessionLocal() as db:
        # Obtener datos básicos
        result = await db.execute(select(Paciente).limit(1))
        paciente = result.scalar_one_or_none()
        
        result = await db.execute(select(Usuario).limit(1))
        usuario = result.scalar_one_or_none()
        
        result = await db.execute(select(Cama).limit(1))
        cama = result.scalar_one_or_none()
        
        if not paciente or not usuario or not cama:
            print("❌ Faltan datos básicos")
            return
        
        print(f"✓ Paciente: {paciente.id}")
        print(f"✓ Usuario: {usuario.id}")
        print(f"✓ Cama: {cama.numero_cama}")
        
        # Crear hospitalización con SOLO las columnas que existen
        print("\n📋 Creando hospitalización...")
        hosp = HospitalizacionSimple(
            id=uuid.uuid4(),
            paciente_id=paciente.id,
            medico_responsable_id=usuario.id,
            motivo_ingreso="Dolor abdominal agudo",
            diagnostico_ingreso="Apendicitis aguda",
            area_hospitalizacion="Urgencias",
            numero_cama=cama.numero_cama,
            estado='activo',
            resumen_clinico="Paciente ingresa por dolor abdominal"
        )
        db.add(hosp)
        await db.commit()
        print("✅ Hospitalización creada!")
        
        # Crear interconsulta
        print("\n🔄 Creando interconsulta...")
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
        print("✅ Interconsulta creada!")
        
        # Verificar
        result = await db.execute(select(HospitalizacionSimple))
        hosp_count = len(result.scalars().all())
        
        result = await db.execute(select(Interconsulta))
        ic_count = len(result.scalars().all())
        
        print(f"\n✅ COMPLETADO!")
        print(f"   Hospitalizaciones: {hosp_count}")
        print(f"   Interconsultas: {ic_count}")

asyncio.run(main())
