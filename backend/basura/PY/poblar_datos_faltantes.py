import asyncio
from app.core.database import AsyncSessionLocal
from app.models.hospitalizacion import Hospitalizacion, Cama
from app.models.interconsulta import Interconsulta
from app.models.paciente import Paciente
from app.models.usuario import Usuario
from sqlalchemy import select
from datetime import datetime
import random

async def main():
    print("\n🚀 Poblando hospitalizaciones e interconsultas...\n")
    
    async with AsyncSessionLocal() as db:
        # Obtener pacientes y usuarios
        result = await db.execute(select(Paciente).limit(10))
        pacientes = result.scalars().all()
        
        result = await db.execute(select(Usuario).limit(5))
        usuarios = result.scalars().all()
        
        result = await db.execute(select(Cama).limit(10))
        camas = result.scalars().all()
        
        print(f"Pacientes: {len(pacientes)}")
        print(f"Usuarios: {len(usuarios)}")
        print(f"Camas: {len(camas)}")
        
        if not pacientes or not usuarios:
            print("\n❌ No hay pacientes o usuarios en la BD")
            return
        
        # Crear hospitalizaciones
        print("\n📋 Creando hospitalizaciones...")
        areas = ['Urgencias', 'UCI', 'Medicina Interna', 'Cirugía', 'Pediatría']
        
        for i in range(min(8, len(pacientes), len(camas))):
            hosp = Hospitalizacion(
                paciente_id=pacientes[i].id,
                medico_responsable_id=usuarios[0].id,
                motivo_ingreso=f"Dolor abdominal agudo - Caso {i+1}",
                diagnostico_ingreso=f"Apendicitis aguda - Paciente {i+1}",
                area_hospitalizacion=random.choice(areas),
                numero_cama=camas[i].numero_cama,
                estado='activo',
                prioridad='normal',
                tipo_ingreso='urgencia'
            )
            db.add(hosp)
            
            # Marcar cama como ocupada
            camas[i].estado = 'ocupada'
        
        await db.commit()
        print("✅ Hospitalizaciones creadas")
        
        # Crear interconsultas
        print("\n🔄 Creando interconsultas...")
        especialidades = [
            'Cardiología', 'Neurología', 'Traumatología', 'Pediatría',
            'Gastroenterología', 'Neumología', 'Nefrología', 'Endocrinología'
        ]
        
        for i in range(min(12, len(pacientes))):
            ic = Interconsulta(
                paciente_id=pacientes[i % len(pacientes)].id,
                medico_solicitante_id=usuarios[0].id,
                especialidad_requerida=random.choice(especialidades),
                motivo_solicitud=f"Evaluación por {random.choice(especialidades)} - Caso {i+1}",
                urgencia=random.choice(['normal', 'urgente', 'emergencia']),
                estado=random.choice(['solicitada', 'aceptada', 'en_proceso'])
            )
            db.add(ic)
        
        await db.commit()
        print("✅ Interconsultas creadas")
        
        # Verificar
        result = await db.execute(select(Hospitalizacion))
        hosp_count = len(result.scalars().all())
        
        result = await db.execute(select(Interconsulta))
        ic_count = len(result.scalars().all())
        
        print(f"\n✅ COMPLETADO!")
        print(f"   Hospitalizaciones: {hosp_count}")
        print(f"   Interconsultas: {ic_count}")
        print("\n💡 Recarga el frontend ahora!\n")

asyncio.run(main())
