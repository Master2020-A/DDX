"""
Script para poblar datos de prueba de Hospitalización e Interconsultas
Ejecutar: python -m scripts.poblar_hospitalizacion_interconsultas
"""
import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import random

from app.core.database import AsyncSessionLocal
from app.models.paciente import Paciente
from app.models.usuario import Usuario
from app.models.hospitalizacion import Hospitalizacion, Cama, NotaEvolucion, IndicacionMedica
from app.models.interconsulta import Interconsulta, NotificacionInterconsulta, MensajeInterconsulta


async def crear_camas(db: AsyncSession):
    """Crear camas de prueba"""
    print("📋 Creando camas...")
    
    areas = ['Urgencias', 'UCI', 'Medicina Interna', 'Cirugía', 'Pediatría']
    camas_data = []
    
    for area in areas:
        for i in range(1, 6):  # 5 camas por área
            cama = Cama(
                numero_cama=f"{area[:3].upper()}-{i:02d}",
                area=area,
                piso=str(random.randint(1, 5)),
                habitacion=f"{random.randint(100, 599)}",
                estado=random.choice(['disponible', 'disponible', 'disponible', 'ocupada']),
                tipo_cama=random.choice(['Estándar', 'Eléctrica', 'UCI']),
                tiene_oxigeno=random.choice([True, False]),
                tiene_monitor=area in ['UCI', 'Urgencias'],
                tiene_ventilador=area == 'UCI',
                capacidad_peso=150.0
            )
            camas_data.append(cama)
    
    db.add_all(camas_data)
    await db.commit()
    print(f"✅ Creadas {len(camas_data)} camas")


async def crear_hospitalizaciones(db: AsyncSession):
    """Crear hospitalizaciones de prueba"""
    print("🏥 Creando hospitalizaciones...")
    
    # Obtener pacientes y médicos
    result_pacientes = await db.execute(select(Paciente).limit(10))
    pacientes = result_pacientes.scalars().all()
    
    result_medicos = await db.execute(select(Usuario).where(Usuario.rol == 'medico').limit(5))
    medicos = result_medicos.scalars().all()
    
    if not pacientes or not medicos:
        print("⚠️  No hay pacientes o médicos disponibles")
        return
    
    # Obtener camas disponibles
    result_camas = await db.execute(select(Cama).where(Cama.estado == 'disponible'))
    camas_disponibles = result_camas.scalars().all()
    
    diagnosticos = [
        "Neumonía adquirida en la comunidad",
        "Insuficiencia cardíaca congestiva",
        "Diabetes mellitus descompensada",
        "Infección de vías urinarias complicada",
        "Apendicitis aguda",
        "Pancreatitis aguda",
        "Accidente cerebrovascular isquémico",
        "Infarto agudo de miocardio",
        "Obstrucción intestinal",
        "Sepsis de origen abdominal"
    ]
    
    hospitalizaciones = []
    for i in range(min(8, len(pacientes))):
        cama = camas_disponibles[i] if i < len(camas_disponibles) else None
        dias_atras = random.randint(1, 15)
        
        hosp = Hospitalizacion(
            paciente_id=pacientes[i].id,
            medico_responsable_id=random.choice(medicos).id,
            fecha_ingreso=datetime.now() - timedelta(days=dias_atras),
            motivo_ingreso=f"Paciente con cuadro clínico de {random.choice(diagnosticos).lower()}",
            diagnostico_ingreso=random.choice(diagnosticos),
            area_hospitalizacion=cama.area if cama else random.choice(['Urgencias', 'UCI', 'Medicina Interna']),
            numero_cama=cama.numero_cama if cama else None,
            piso=cama.piso if cama else str(random.randint(1, 5)),
            estado=random.choice(['activo', 'activo', 'activo', 'alta_medica']),
            prioridad=random.choice(['normal', 'alta', 'urgente']),
            tipo_ingreso=random.choice(['urgencia', 'programada', 'traslado']),
            alergias_conocidas=['Penicilina'] if random.random() > 0.7 else None,
            antecedentes_relevantes="Hipertensión arterial, Diabetes mellitus tipo 2" if random.random() > 0.5 else None,
            prioridad_clinica=random.randint(1, 5)
        )
        
        if cama:
            cama.estado = 'ocupada'
            cama.hospitalizacion_actual_id = hosp.id
        
        hospitalizaciones.append(hosp)
    
    db.add_all(hospitalizaciones)
    await db.commit()
    print(f"✅ Creadas {len(hospitalizaciones)} hospitalizaciones")
    
    # Crear notas de evolución
    await crear_notas_evolucion(db, hospitalizaciones, medicos)
    
    # Crear indicaciones médicas
    await crear_indicaciones(db, hospitalizaciones, medicos)


async def crear_notas_evolucion(db: AsyncSession, hospitalizaciones, medicos):
    """Crear notas de evolución"""
    print("📝 Creando notas de evolución...")
    
    notas = []
    for hosp in hospitalizaciones[:5]:  # Solo para las primeras 5
        for dia in range(1, random.randint(2, 4)):
            nota = NotaEvolucion(
                hospitalizacion_id=hosp.id,
                medico_id=random.choice(medicos).id,
                fecha_nota=hosp.fecha_ingreso + timedelta(days=dia),
                tipo_nota='evolucion',
                turno=random.choice(['matutino', 'vespertino', 'nocturno']),
                subjetivo="Paciente refiere mejoría del dolor, tolera vía oral",
                objetivo="Paciente consciente, orientado, hemodinámicamente estable",
                temperatura=random.uniform(36.5, 37.5),
                presion_arterial_sistolica=random.randint(110, 140),
                presion_arterial_diastolica=random.randint(70, 90),
                frecuencia_cardiaca=random.randint(60, 90),
                frecuencia_respiratoria=random.randint(14, 20),
                saturacion_oxigeno=random.uniform(95, 99),
                evaluacion="Evolución favorable, sin complicaciones",
                plan="Continuar manejo actual, vigilar signos de alarma",
                estado_general=random.choice(['estable', 'mejoría', 'regular']),
                nivel_conciencia='alerta'
            )
            notas.append(nota)
    
    db.add_all(notas)
    await db.commit()
    print(f"✅ Creadas {len(notas)} notas de evolución")


async def crear_indicaciones(db: AsyncSession, hospitalizaciones, medicos):
    """Crear indicaciones médicas"""
    print("💊 Creando indicaciones médicas...")
    
    medicamentos = [
        ("Paracetamol", "1g", "IV", "cada 8 horas"),
        ("Omeprazol", "40mg", "IV", "cada 24 horas"),
        ("Ceftriaxona", "2g", "IV", "cada 12 horas"),
        ("Metoclopramida", "10mg", "IV", "cada 8 horas PRN"),
        ("Enoxaparina", "40mg", "SC", "cada 24 horas"),
    ]
    
    indicaciones = []
    for hosp in hospitalizaciones[:6]:
        for _ in range(random.randint(2, 4)):
            med = random.choice(medicamentos)
            indicacion = IndicacionMedica(
                hospitalizacion_id=hosp.id,
                medico_id=random.choice(medicos).id,
                fecha_indicacion=hosp.fecha_ingreso,
                tipo_indicacion='medicamento',
                descripcion=med[0],
                dosis=med[1],
                via_administracion=med[2],
                frecuencia=med[3],
                duracion='7 días',
                prioridad=random.choice(['normal', 'urgente']),
                estado='activa',
                fecha_inicio=hosp.fecha_ingreso
            )
            indicaciones.append(indicacion)
    
    db.add_all(indicaciones)
    await db.commit()
    print(f"✅ Creadas {len(indicaciones)} indicaciones médicas")


async def crear_interconsultas(db: AsyncSession):
    """Crear interconsultas de prueba"""
    print("🔄 Creando interconsultas...")
    
    # Obtener datos necesarios
    result_pacientes = await db.execute(select(Paciente).limit(10))
    pacientes = result_pacientes.scalars().all()
    
    result_medicos = await db.execute(select(Usuario).where(Usuario.rol == 'medico'))
    medicos = result_medicos.scalars().all()
    
    if not pacientes or len(medicos) < 2:
        print("⚠️  No hay suficientes pacientes o médicos")
        return
    
    especialidades = [
        'Cardiología', 'Neurología', 'Gastroenterología', 'Neumología',
        'Nefrología', 'Endocrinología', 'Infectología', 'Cirugía General'
    ]
    
    motivos = [
        "Evaluación de dolor torácico atípico, descartar origen cardíaco",
        "Paciente con cefalea persistente, requiere valoración neurológica",
        "Dolor abdominal recurrente, solicito evaluación por gastroenterología",
        "Disnea progresiva, favor valorar función pulmonar",
        "Creatinina elevada, requiere manejo por nefrología",
        "Descontrol glucémico, solicito ajuste de tratamiento",
        "Fiebre de origen desconocido, requiere protocolo de estudio",
        "Valoración prequirúrgica para procedimiento programado"
    ]
    
    interconsultas = []
    for i in range(12):
        dias_atras = random.randint(0, 10)
        estado = random.choice(['solicitada', 'aceptada', 'en_proceso', 'completada'])
        
        ic = Interconsulta(
            paciente_id=random.choice(pacientes).id,
            medico_solicitante_id=medicos[0].id,
            especialista_id=medicos[1].id if estado != 'solicitada' else None,
            especialidad_requerida=random.choice(especialidades),
            motivo_solicitud=random.choice(motivos),
            antecedentes_relevantes="HTA, DM2, dislipidemia" if random.random() > 0.5 else None,
            urgencia=random.choice(['normal', 'normal', 'urgente', 'emergencia']),
            estado=estado,
            fecha_solicitud=datetime.now() - timedelta(days=dias_atras),
            fecha_aceptacion=datetime.now() - timedelta(days=dias_atras-1) if estado != 'solicitada' else None,
            prioridad_clinica=random.randint(1, 5)
        )
        
        if estado == 'completada':
            ic.diagnostico_especialista = "Paciente evaluado, se confirma diagnóstico"
            ic.recomendaciones = "Continuar manejo actual, control en 2 semanas"
            ic.fecha_completada = datetime.now() - timedelta(days=random.randint(0, 3))
        
        interconsultas.append(ic)
    
    db.add_all(interconsultas)
    await db.commit()
    print(f"✅ Creadas {len(interconsultas)} interconsultas")
    
    # Crear notificaciones y mensajes
    await crear_notificaciones(db, interconsultas, medicos)
    await crear_mensajes(db, interconsultas, medicos)


async def crear_notificaciones(db: AsyncSession, interconsultas, medicos):
    """Crear notificaciones de interconsultas"""
    print("🔔 Creando notificaciones...")
    
    notificaciones = []
    for ic in interconsultas[:8]:
        if ic.especialista_id:
            notif = NotificacionInterconsulta(
                interconsulta_id=ic.id,
                medico_destinatario_id=ic.especialista_id,
                tipo='nueva_solicitud',
                titulo=f'Nueva interconsulta de {ic.especialidad_requerida}',
                mensaje=f'Solicitud con urgencia {ic.urgencia}: {ic.motivo_solicitud[:80]}...',
                leida=random.choice([True, False])
            )
            notificaciones.append(notif)
    
    db.add_all(notificaciones)
    await db.commit()
    print(f"✅ Creadas {len(notificaciones)} notificaciones")


async def crear_mensajes(db: AsyncSession, interconsultas, medicos):
    """Crear mensajes de chat"""
    print("💬 Creando mensajes de chat...")
    
    mensajes_texto = [
        "Buenos días, revisé el caso y requiero algunos estudios adicionales",
        "Paciente evaluado, sugiero iniciar tratamiento específico",
        "¿Tiene los resultados de laboratorio más recientes?",
        "Programé valoración para mañana en la mañana",
        "Gracias por la interconsulta, paciente con evolución favorable"
    ]
    
    mensajes = []
    for ic in interconsultas[:6]:
        if ic.especialista_id:
            for _ in range(random.randint(1, 3)):
                mensaje = MensajeInterconsulta(
                    interconsulta_id=ic.id,
                    medico_emisor_id=random.choice([ic.medico_solicitante_id, ic.especialista_id]),
                    mensaje=random.choice(mensajes_texto),
                    leido=random.choice([True, False])
                )
                mensajes.append(mensaje)
    
    db.add_all(mensajes)
    await db.commit()
    print(f"✅ Creados {len(mensajes)} mensajes")


async def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🚀 POBLANDO DATOS DE HOSPITALIZACIÓN E INTERCONSULTAS")
    print("="*60 + "\n")
    
    async with AsyncSessionLocal() as db:
        try:
            # Hospitalización
            await crear_camas(db)
            await crear_hospitalizaciones(db)
            
            # Interconsultas
            await crear_interconsultas(db)
            
            print("\n" + "="*60)
            print("✅ DATOS CREADOS EXITOSAMENTE")
            print("="*60)
            print("\n📊 Resumen:")
            print("   • 25 camas en 5 áreas diferentes")
            print("   • 8 hospitalizaciones activas")
            print("   • Notas de evolución y signos vitales")
            print("   • Indicaciones médicas activas")
            print("   • 12 interconsultas en diferentes estados")
            print("   • Notificaciones y mensajes de chat")
            print("\n🎯 Ahora puedes probar ambos módulos con datos reales!\n")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
