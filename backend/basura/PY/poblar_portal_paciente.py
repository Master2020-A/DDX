"""
Script para poblar datos de prueba del Portal del Paciente
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, date, time, timedelta
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent))


async def main():
    print("=" * 70)
    print("📊 POBLANDO DATOS DE PRUEBA - PORTAL DEL PACIENTE")
    print("=" * 70)

    from sqlalchemy import select
    from app.core.database import AsyncSessionLocal

    # Importar TODOS los modelos
    import app.models.telemedicina
    import app.models.ia_medica
    import app.models.paciente
    import app.models.usuario
    import app.models.portal_paciente

    from app.models.usuario import Usuario
    from app.models.paciente import Paciente
    from app.models.portal_paciente import (
        CitaPaciente,
        SolicitudEstudio,
        PagoServicio,
        MensajePacienteMedico,
        RecordatorioMedicamento,
        RegistroTomaMedicamento,
        ConfiguracionPortal,
    )

    async with AsyncSessionLocal() as db:
        try:
            # Obtener usuarios y pacientes
            result = await db.execute(select(Usuario).limit(3))
            usuarios = list(result.scalars().all())

            result = await db.execute(select(Paciente).limit(3))
            pacientes = list(result.scalars().all())

            print(
                f"\n✅ Encontrados {len(usuarios)} usuarios y {len(pacientes)} pacientes"
            )

            if not usuarios or not pacientes:
                print("⚠️  Se requieren usuarios y pacientes en la BD")
                return

            # 1. Citas
            print("\n📅 Creando citas...")
            citas_data = [
                {
                    "paciente": pacientes[0],
                    "medico": usuarios[0],
                    "tipo_cita": "primera_vez",
                    "especialidad": "Cardiología",
                    "motivo": "Dolor en el pecho y palpitaciones",
                    "fecha": date.today() + timedelta(days=3),
                    "hora": time(10, 0),
                    "estado": "confirmada",
                },
                {
                    "paciente": pacientes[1],
                    "medico": usuarios[1] if len(usuarios) > 1 else usuarios[0],
                    "tipo_cita": "seguimiento",
                    "especialidad": "Medicina Interna",
                    "motivo": "Control de diabetes",
                    "fecha": date.today() + timedelta(days=7),
                    "hora": time(14, 30),
                    "estado": "solicitada",
                },
                {
                    "paciente": pacientes[0],
                    "medico": None,
                    "tipo_cita": "urgencia",
                    "especialidad": "Urgencias",
                    "motivo": "Fiebre alta y malestar general",
                    "fecha": date.today() + timedelta(days=1),
                    "hora": None,
                    "estado": "solicitada",
                },
            ]

            for cita_data in citas_data:
                cita = CitaPaciente(
                    paciente_id=cita_data["paciente"].id,
                    medico_id=cita_data["medico"].id if cita_data["medico"] else None,
                    tipo_cita=cita_data["tipo_cita"],
                    especialidad_solicitada=cita_data["especialidad"],
                    motivo_consulta=cita_data["motivo"],
                    fecha_solicitada=cita_data["fecha"],
                    hora_solicitada=cita_data["hora"],
                    estado=cita_data["estado"],
                    fecha_confirmada=(
                        datetime.now() if cita_data["estado"] == "confirmada" else None
                    ),
                )
                db.add(cita)

            await db.flush()
            print(f"✅ {len(citas_data)} citas creadas")

            # 2. Solicitudes de estudios
            print("\n🔬 Creando solicitudes de estudios...")
            estudios_data = [
                {
                    "paciente": pacientes[0],
                    "tipo": "laboratorio",
                    "nombre": "Biometría Hemática Completa",
                    "descripcion": "Control de rutina",
                    "estado": "aprobada",
                    "prioridad": "normal",
                },
                {
                    "paciente": pacientes[0],
                    "tipo": "imagen",
                    "nombre": "Radiografía de Tórax",
                    "descripcion": "Evaluación de dolor torácico",
                    "estado": "en_proceso",
                    "prioridad": "urgente",
                },
                {
                    "paciente": pacientes[1],
                    "tipo": "laboratorio",
                    "nombre": "Perfil de Lípidos",
                    "descripcion": "Control de colesterol",
                    "estado": "completada",
                    "prioridad": "normal",
                },
                {
                    "paciente": pacientes[1],
                    "tipo": "especializado",
                    "nombre": "Electrocardiograma",
                    "descripcion": "Evaluación cardíaca",
                    "estado": "pendiente",
                    "prioridad": "normal",
                },
            ]

            for estudio_data in estudios_data:
                estudio = SolicitudEstudio(
                    paciente_id=estudio_data["paciente"].id,
                    medico_solicitante_id=usuarios[0].id,
                    tipo_estudio=estudio_data["tipo"],
                    nombre_estudio=estudio_data["nombre"],
                    descripcion=estudio_data["descripcion"],
                    estado=estudio_data["estado"],
                    prioridad=estudio_data["prioridad"],
                    fecha_solicitud=datetime.now() - timedelta(days=2),
                    fecha_autorizacion=(
                        datetime.now() - timedelta(days=1)
                        if estudio_data["estado"] != "pendiente"
                        else None
                    ),
                    resultado_disponible=(estudio_data["estado"] == "completada"),
                )
                db.add(estudio)

            await db.flush()
            print(f"✅ {len(estudios_data)} solicitudes de estudios creadas")

            # 3. Pagos
            print("\n💳 Creando pagos...")
            pagos_data = [
                {
                    "paciente": pacientes[0],
                    "concepto": "Consulta de Cardiología",
                    "monto": 800.00,
                    "estado": "completado",
                },
                {
                    "paciente": pacientes[0],
                    "concepto": "Biometría Hemática",
                    "monto": 250.00,
                    "estado": "completado",
                },
                {
                    "paciente": pacientes[1],
                    "concepto": "Consulta de Seguimiento",
                    "monto": 600.00,
                    "estado": "pendiente",
                },
            ]

            for pago_data in pagos_data:
                pago = PagoServicio(
                    paciente_id=pago_data["paciente"].id,
                    concepto=pago_data["concepto"],
                    monto=pago_data["monto"],
                    moneda="MXN",
                    metodo_pago="tarjeta_credito",
                    estado=pago_data["estado"],
                    fecha_pago=datetime.now() - timedelta(days=1),
                    fecha_procesado=(
                        datetime.now() - timedelta(days=1)
                        if pago_data["estado"] == "completado"
                        else None
                    ),
                    fecha_completado=(
                        datetime.now() - timedelta(days=1)
                        if pago_data["estado"] == "completado"
                        else None
                    ),
                    referencia_pago=(
                        f"REF-{uuid4().hex[:8].upper()}"
                        if pago_data["estado"] == "completado"
                        else None
                    ),
                )
                db.add(pago)

            await db.flush()
            print(f"✅ {len(pagos_data)} pagos creados")

            # 4. Mensajes
            print("\n💬 Creando mensajes...")
            mensajes_data = [
                {
                    "paciente": pacientes[0],
                    "medico": usuarios[0],
                    "remitente": "paciente",
                    "asunto": "Consulta sobre medicamento",
                    "mensaje": "Doctor, ¿puedo tomar el medicamento con alimentos?",
                    "leido": True,
                },
                {
                    "paciente": pacientes[0],
                    "medico": usuarios[0],
                    "remitente": "medico",
                    "asunto": "Re: Consulta sobre medicamento",
                    "mensaje": "Sí, puede tomarlo con alimentos. De hecho es recomendable.",
                    "leido": True,
                },
                {
                    "paciente": pacientes[1],
                    "medico": usuarios[0],
                    "remitente": "medico",
                    "asunto": "Resultados de laboratorio",
                    "mensaje": "Sus resultados de laboratorio están listos. Todo se ve bien.",
                    "leido": False,
                },
            ]

            for msg_data in mensajes_data:
                mensaje = MensajePacienteMedico(
                    paciente_id=msg_data["paciente"].id,
                    medico_id=msg_data["medico"].id,
                    remitente_tipo=msg_data["remitente"],
                    asunto=msg_data["asunto"],
                    mensaje=msg_data["mensaje"],
                    estado="entregado",
                    leido=msg_data["leido"],
                    fecha_lectura=(
                        datetime.now() - timedelta(hours=2)
                        if msg_data["leido"]
                        else None
                    ),
                )
                db.add(mensaje)

            await db.flush()
            print(f"✅ {len(mensajes_data)} mensajes creados")

            # 5. Recordatorios de medicamentos
            print("\n💊 Creando recordatorios de medicamentos...")
            recordatorios_data = [
                {
                    "paciente": pacientes[0],
                    "nombre": "Losartán 50mg",
                    "dosis": "50mg",
                    "frecuencia": "diario",
                    "horarios": ["08:00"],
                    "duracion": 30,
                },
                {
                    "paciente": pacientes[0],
                    "nombre": "Metformina 850mg",
                    "dosis": "850mg",
                    "frecuencia": "cada_12_horas",
                    "horarios": ["08:00", "20:00"],
                    "duracion": 30,
                },
                {
                    "paciente": pacientes[1],
                    "nombre": "Omeprazol 20mg",
                    "dosis": "20mg",
                    "frecuencia": "diario",
                    "horarios": ["07:00"],
                    "duracion": 14,
                },
            ]

            for rec_data in recordatorios_data:
                recordatorio = RecordatorioMedicamento(
                    paciente_id=rec_data["paciente"].id,
                    nombre_medicamento=rec_data["nombre"],
                    dosis=rec_data["dosis"],
                    via_administracion="oral",
                    frecuencia=rec_data["frecuencia"],
                    horarios=rec_data["horarios"],
                    fecha_inicio=date.today() - timedelta(days=5),
                    fecha_fin=date.today() + timedelta(days=rec_data["duracion"] - 5),
                    duracion_dias=rec_data["duracion"],
                    activo=True,
                    pausado=False,
                    tomas_registradas=5,
                    tomas_omitidas=0,
                )
                db.add(recordatorio)

            await db.flush()
            print(f"✅ {len(recordatorios_data)} recordatorios creados")

            # 6. Configuración del portal
            print("\n⚙️ Creando configuraciones del portal...")
            for paciente in pacientes[:2]:
                config = ConfiguracionPortal(
                    paciente_id=paciente.id,
                    notificaciones_email=True,
                    notificaciones_sms=False,
                    notificaciones_push=True,
                    compartir_datos_investigacion=False,
                    mostrar_perfil_publico=False,
                    idioma="es",
                    tema="light",
                    zona_horaria="America/Mexico_City",
                    recordatorios_citas=True,
                    recordatorios_medicamentos=True,
                    recordatorios_estudios=True,
                )
                db.add(config)

            await db.flush()
            print(f"✅ {len(pacientes[:2])} configuraciones creadas")

            await db.commit()

            print("\n" + "=" * 70)
            print("✅ ¡DATOS CREADOS EXITOSAMENTE!")
            print("=" * 70)
            print("\n📊 Resumen:")
            print(f"   ✓ {len(citas_data)} citas")
            print(f"   ✓ {len(estudios_data)} solicitudes de estudios")
            print(f"   ✓ {len(pagos_data)} pagos")
            print(f"   ✓ {len(mensajes_data)} mensajes")
            print(f"   ✓ {len(recordatorios_data)} recordatorios de medicamentos")
            print(f"   ✓ {len(pacientes[:2])} configuraciones del portal")
            print("\n🎉 ¡El Portal del Paciente está listo!")
            print("   Accede a: http://localhost:5173/portal-paciente")
            print("=" * 70)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
