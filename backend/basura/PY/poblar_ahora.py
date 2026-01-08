"""Poblar datos ahora con output visible"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*60)
print("🚀 POBLANDO DATOS - VERSIÓN DIRECTA")
print("="*60 + "\n")

async def main():
    from sqlalchemy import select, func
    from app.core.database import AsyncSessionLocal
    from app.models.hospitalizacion import Cama, Hospitalizacion
    from app.models.interconsulta import Interconsulta
    from app.models.paciente import Paciente
    from app.models.usuario import Usuario
    from datetime import datetime, timedelta
    import random
    
    async with AsyncSessionLocal() as db:
        # Verificar si ya hay datos
        result = await db.execute(select(func.count(Cama.id)))
        camas_count = result.scalar()
        
        if camas_count > 0:
            print(f"⚠️  Ya existen {camas_count} camas. Limpiando...")
            await db.execute(select(Cama).delete())
            await db.commit()
        
        print("1. Obteniendo pacientes y usuarios...")
        result = await db.execute(select(Paciente).limit(10))
        pacientes = result.scalars().all()
        print(f"   Pacientes encontrados: {len(pacientes)}")
        
        result = await db.execute(select(Usuario).limit(5))
        usuarios = result.scalars().all()
        print(f"   Usuarios encontrados: {len(usuarios)}")
        
        if not pacientes or not usuarios:
            print("❌ No hay pacientes o usuarios. Crea datos básicos primero.")
            return
        
        print("\n2. Creando 25 camas...")
        areas = ['Urgencias', 'UCI', 'Medicina Interna', 'Cirugía', 'Pediatría']
        camas = []
        for i, area in enumerate(areas):
            for j in range(5):
                cama = Cama(
                    numero_cama=f"{area[:3].upper()}-{j+1:02d}",
                    area=area,
                    piso=str(random.randint(1, 4)),
                    habitacion=str(random.randint(100, 600)),
                    estado='disponible',
                    tipo_cama=random.choice(['Estándar', 'UCI', 'Eléctrica']),
                    tiene_oxigeno=random.choice([True, False]),
                    tiene_monitor=area == 'UCI',
                    tiene_ventilador=False,
                    capacidad_peso=150.0
                )
                camas.append(cama)
                db.add(cama)
        
        await db.commit()
        print(f"   ✅ {len(camas)} camas creadas")
        
        print("\n3. Creando 8 hospitalizaciones...")
        hospitalizaciones = []
        for i in range(min(8, len(pacientes))):
            hosp = Hospitalizacion(
                paciente_id=pacientes[i].id,
                medico_responsable_id=usuarios[0].id,
                motivo_ingreso=f"Motivo de ingreso {i+1}",
                diagnostico_ingreso=f"Diagnóstico inicial {i+1}",
                area_hospitalizacion=random.choice(areas),
                numero_cama=camas[i].numero_cama,
                estado='activo',
                prioridad='normal',
                tipo_ingreso='urgencia'
            )
            hospitalizaciones.append(hosp)
            db.add(hosp)
            
            # Marcar cama como ocupada
            camas[i].estado = 'ocupada'
        
        await db.commit()
        print(f"   ✅ {len(hospitalizaciones)} hospitalizaciones creadas")
        
        print("\n4. Creando 12 interconsultas...")
        especialidades = ['Cardiología', 'Neurología', 'Traumatología', 'Pediatría']
        interconsultas = []
        for i in range(min(12, len(pacientes))):
            ic = Interconsulta(
                paciente_id=pacientes[i % len(pacientes)].id,
                medico_solicitante_id=usuarios[0].id,
                especialidad_requerida=random.choice(especialidades),
                motivo_solicitud=f"Solicitud de interconsulta {i+1}",
                urgencia=random.choice(['normal', 'urgente', 'emergencia']),
                estado=random.choice(['solicitada', 'aceptada', 'en_proceso', 'completada'])
            )
            interconsultas.append(ic)
            db.add(ic)
        
        await db.commit()
        print(f"   ✅ {len(interconsultas)} interconsultas creadas")
        
        print("\n" + "="*60)
        print("✅ DATOS POBLADOS EXITOSAMENTE")
        print("="*60)
        print(f"\n📊 Resumen:")
        print(f"   🛏️  Camas: {len(camas)}")
        print(f"   🏨 Hospitalizaciones: {len(hospitalizaciones)}")
        print(f"   🔄 Interconsultas: {len(interconsultas)}")
        print("\n💡 Recarga el frontend ahora!\n")

if __name__ == "__main__":
    asyncio.run(main())
