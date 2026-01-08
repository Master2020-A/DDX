"""Poblar interconsultas con datos de prueba"""
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.interconsulta import Interconsulta
from app.models.paciente import Paciente
from app.models.usuario import Usuario
from sqlalchemy import select
import uuid
import random

async def main():
    print("\n🔄 Poblando interconsultas...")
    
    async with AsyncSessionLocal() as db:
        # Obtener pacientes y usuarios
        result = await db.execute(select(Paciente).limit(10))
        pacientes = result.scalars().all()
        
        result = await db.execute(select(Usuario).limit(5))
        usuarios = result.scalars().all()
        
        if not pacientes or not usuarios:
            print("❌ No hay pacientes o usuarios")
            return
        
        print(f"✓ {len(pacientes)} pacientes encontrados")
        print(f"✓ {len(usuarios)} usuarios encontrados")
        
        especialidades = [
            'Cardiología', 'Neurología', 'Traumatología', 'Pediatría',
            'Gastroenterología', 'Neumología', 'Nefrología', 'Endocrinología',
            'Dermatología', 'Oftalmología', 'Otorrinolaringología', 'Urología'
        ]
        
        estados = ['solicitada', 'aceptada', 'en_proceso', 'completada']
        urgencias = ['normal', 'urgente', 'emergencia']
        
        motivos = [
            'Evaluación de dolor torácico',
            'Valoración de cefalea persistente',
            'Evaluación de lesión traumática',
            'Control de enfermedad crónica',
            'Valoración de síntomas digestivos',
            'Evaluación respiratoria',
            'Control de función renal',
            'Valoración endocrinológica'
        ]
        
        print("\n📝 Creando interconsultas...")
        for i in range(12):
            ic = Interconsulta(
                id=uuid.uuid4(),
                paciente_id=random.choice(pacientes).id,
                medico_solicitante_id=random.choice(usuarios).id,
                especialidad_requerida=random.choice(especialidades),
                motivo_solicitud=random.choice(motivos),
                urgencia=random.choice(urgencias),
                estado=random.choice(estados),
                antecedentes_relevantes=f"Antecedentes clínicos del paciente {i+1}",
                requiere_seguimiento=random.choice([True, False]),
                prioridad_clinica=random.randint(1, 3)
            )
            
            # Si está completada, agregar diagnóstico y recomendaciones
            if ic.estado == 'completada':
                ic.diagnostico_especialista = f"Diagnóstico de especialista para caso {i+1}"
                ic.recomendaciones = f"Recomendaciones de tratamiento para caso {i+1}"
            
            db.add(ic)
            print(f"  ✓ Interconsulta {i+1}: {ic.especialidad_requerida} - {ic.estado}")
        
        await db.commit()
        
        # Verificar
        result = await db.execute(select(Interconsulta))
        total = len(result.scalars().all())
        
        print(f"\n✅ COMPLETADO!")
        print(f"   Total de interconsultas: {total}")
        print("\n💡 Recarga el frontend para ver los datos\n")

asyncio.run(main())
