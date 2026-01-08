"""
Script simplificado para poblar datos del Portal del Paciente
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, date, time, timedelta
from uuid import UUID

sys.path.insert(0, str(Path(__file__).parent))


async def poblar_datos():
    from sqlalchemy import select
    from app.core.database import AsyncSessionLocal

    # Importar TODOS los modelos para evitar errores de relaciones
    import app.models.usuario
    import app.models.paciente
    import app.models.telemedicina
    import app.models.portal_paciente
    import app.models.ia_medica
    import app.models.consulta
    import app.models.laboratorio
    import app.models.imagen_medica
    import app.models.diagnostico
    import app.models.tratamiento
    import app.models.historia_clinica

    from app.models.portal_paciente import (
        CitaPaciente,
        SolicitudEstudio,
        PagoServicio,
        MensajePacienteMedico,
        RecordatorioMedicamento,
        ConfiguracionPortal,
    )

    # ID del paciente que estamos usando en el frontend
    paciente_id = UUID("49bfb1e1-699c-4161-90cd-9162c226259c")

    print("=" * 70)
    print("POBLANDO PORTAL DEL PACIENTE")
    print("=" * 70)

    async with AsyncSessionLocal() as db:
        try:
            # 1. CITAS
            print("\n📅 Creando citas...")
            citas = [
                CitaPaciente(
                    paciente_id=paciente_id,
                    tipo_cita="primera_vez",
                    especialidad_solicitada="Cardiología",
                    motivo_consulta="Dolor en el pecho y palpitaciones frecuentes",
                    fecha_solicitada=date.today() + timedelta(days=3),
                    hora_solicitada=time(10, 0),
                    estado="confirmada",
                    notas_paciente="Síntomas desde hace 2 semanas",
                ),
                CitaPaciente(
                    paciente_id=paciente_id,
                    tipo_cita="seguimiento",
                    especialidad_solicitada="Medicina Interna",
                    motivo_consulta="Control de presión arterial",
                    fecha_solicitada=date.today() + timedelta(days=7),
                    hora_solicitada=time(14, 30),
                    estado="solicitada",
                ),
                CitaPaciente(
                    paciente_id=paciente_id,
                    tipo_cita="urgencia",
                    especialidad_solicitada="Urgencias",
                    motivo_consulta="Fiebre alta y malestar general",
                    fecha_solicitada=date.today() + timedelta(days=1),
                    estado="solicitada",
                ),
                CitaPaciente(
                    paciente_id=paciente_id,
                    tipo_cita="seguimiento",
                    especialidad_solicitada="Neurología",
                    motivo_consulta="Seguimiento de migraña",
                    fecha_solicitada=date.today() - timedelta(days=5),
                    hora_solicitada=time(11, 0),
                    estado="completada",
                    fecha_confirmada=date.today() - timedelta(days=5),
                ),
            ]

            for cita in citas:
                db.add(cita)

            await db.flush()
            print(f"✅ {len(citas)} citas creadas")

            # 2. ESTUDIOS
            print("\n🔬 Creando solicitudes de estudios...")
            estudios = [
                SolicitudEstudio(
                    paciente_id=paciente_id,
                    tipo_estudio="laboratorio",
                    nombre_estudio="Perfil Lipídico Completo",
                    descripcion="Colesterol total, HDL, LDL, Triglicéridos",
                    estado="aprobada",
                    prioridad="normal",
                    fecha_solicitud=datetime.now() - timedelta(days=2),
                    fecha_autorizacion=datetime.now() - timedelta(days=1),
                    fecha_programada=date.today() + timedelta(days=3),
                    resultado_disponible=False,
                ),
                SolicitudEstudio(
                    paciente_id=paciente_id,
                    tipo_estudio="imagen",
                    nombre_estudio="Radiografía de Tórax",
                    descripcion="Evaluación pulmonar",
                    estado="completada",
                    prioridad="urgente",
                    fecha_solicitud=datetime.now() - timedelta(days=10),
                    fecha_autorizacion=datetime.now() - timedelta(days=9),
                    fecha_realizacion=datetime.now() - timedelta(days=7),
                    resultado_disponible=True,
                ),
                SolicitudEstudio(
                    paciente_id=paciente_id,
                    tipo_estudio="laboratorio",
                    nombre_estudio="Hemograma Completo",
                    descripcion="Biometría hemática",
                    estado="pendiente",
                    prioridad="normal",
                    fecha_solicitud=datetime.now(),
                ),
                SolicitudEstudio(
                    paciente_id=paciente_id,
                    tipo_estudio="especializado",
                    nombre_estudio="Electrocardiograma",
                    descripcion="Evaluación cardíaca",
                    estado="en_proceso",
                    prioridad="urgente",
                    fecha_solicitud=datetime.now() - timedelta(days=1),
                    fecha_autorizacion=datetime.now(),
                    resultado_disponible=False,
                ),
            ]

            for estudio in estudios:
                db.add(estudio)

            await db.flush()
            print(f"✅ {len(estudios)} estudios creados")

            # 3. PAGOS
            print("\n💳 Creando pagos...")
            pagos = [
                PagoServicio(
                    paciente_id=paciente_id,
                    concepto="Consulta Cardiología",
                    descripcion="Consulta de primera vez con cardiólogo",
                    monto=850.00,
                    moneda="MXN",
                    metodo_pago="tarjeta_credito",
                    estado="completado",
                    fecha_pago=datetime.now() - timedelta(days=3),
                    fecha_procesado=datetime.now() - timedelta(days=3),
                    fecha_completado=datetime.now() - timedelta(days=3),
                    referencia_pago="TXN-2024-001234",
                ),
                PagoServicio(
                    paciente_id=paciente_id,
                    concepto="Estudios de Laboratorio",
                    descripcion="Perfil lipídico y hemograma",
                    monto=450.00,
                    moneda="MXN",
                    metodo_pago="efectivo",
                    estado="pagado",
                    fecha_pago=datetime.now() - timedelta(days=1),
                    referencia_pago="CASH-2024-005678",
                ),
                PagoServicio(
                    paciente_id=paciente_id,
                    concepto="Radiografía de Tórax",
                    descripcion="Estudio de imagen",
                    monto=320.00,
                    moneda="MXN",
                    metodo_pago="transferencia",
                    estado="procesando",
                    fecha_pago=datetime.now(),
                ),
            ]

            for pago in pagos:
                db.add(pago)

            await db.flush()
            print(f"✅ {len(pagos)} pagos creados")

            # 4. MENSAJES
            print("\n💬 Creando mensajes...")
            mensajes = [
                MensajePacienteMedico(
                    paciente_id=paciente_id,
                    medico_id=UUID(
                        "00000000-0000-0000-0000-000000000001"
                    ),  # ID ficticio
                    remitente_tipo="medico",
                    asunto="Resultados de laboratorio",
                    mensaje="Sus resultados de laboratorio están listos. Todo se ve bien, pero necesitamos hacer seguimiento del colesterol.",
                    estado="enviado",
                    leido=False,
                ),
                MensajePacienteMedico(
                    paciente_id=paciente_id,
                    medico_id=UUID("00000000-0000-0000-0000-000000000001"),
                    remitente_tipo="paciente",
                    asunto="Consulta sobre medicamento",
                    mensaje="Doctor, ¿puedo tomar el medicamento en ayunas?",
                    estado="enviado",
                    leido=True,
                    fecha_lectura=datetime.now() - timedelta(hours=2),
                ),
                MensajePacienteMedico(
                    paciente_id=paciente_id,
                    medico_id=UUID("00000000-0000-0000-0000-000000000002"),
                    remitente_tipo="medico",
                    asunto="Recordatorio de cita",
                    mensaje="Le recordamos su cita de cardiología el próximo martes a las 10:00 AM.",
                    estado="enviado",
                    leido=True,
                    fecha_lectura=datetime.now() - timedelta(days=1),
                ),
            ]

            for mensaje in mensajes:
                db.add(mensaje)

            await db.flush()
            print(f"✅ {len(mensajes)} mensajes creados")

            # 5. RECORDATORIOS DE MEDICAMENTOS
            print("\n💊 Creando recordatorios de medicamentos...")
            recordatorios = [
                RecordatorioMedicamento(
                    paciente_id=paciente_id,
                    nombre_medicamento="Losartán 50mg",
                    dosis="1 tableta",
                    via_administracion="oral",
                    frecuencia="cada_24_horas",
                    horarios=["08:00"],
                    fecha_inicio=date.today() - timedelta(days=30),
                    duracion_dias=90,
                    activo=True,
                    notificar_email=True,
                    notificar_sms=True,
                    tomas_registradas=28,
                    tomas_omitidas=2,
                ),
                RecordatorioMedicamento(
                    paciente_id=paciente_id,
                    nombre_medicamento="Metformina 850mg",
                    dosis="1 tableta",
                    via_administracion="oral",
                    frecuencia="cada_12_horas",
                    horarios=["08:00", "20:00"],
                    fecha_inicio=date.today() - timedelta(days=60),
                    duracion_dias=180,
                    activo=True,
                    notificar_push=True,
                    tomas_registradas=115,
                    tomas_omitidas=5,
                ),
                RecordatorioMedicamento(
                    paciente_id=paciente_id,
                    nombre_medicamento="Omeprazol 20mg",
                    dosis="1 cápsula",
                    via_administracion="oral",
                    frecuencia="cada_24_horas",
                    horarios=["07:00"],
                    fecha_inicio=date.today() - timedelta(days=15),
                    duracion_dias=30,
                    activo=True,
                    notificar_email=True,
                    tomas_registradas=14,
                    tomas_omitidas=1,
                ),
            ]

            for recordatorio in recordatorios:
                db.add(recordatorio)

            await db.flush()
            print(f"✅ {len(recordatorios)} recordatorios creados")

            # 6. CONFIGURACIÓN
            print("\n⚙️  Creando configuración...")
            config = ConfiguracionPortal(
                paciente_id=paciente_id,
                notificaciones_email=True,
                notificaciones_sms=True,
                notificaciones_push=True,
                recordatorios_medicamentos=True,
                recordatorios_citas=True,
                idioma="es",
                zona_horaria="America/Mexico_City",
                tema="light",
            )
            db.add(config)

            await db.commit()
            print("✅ Configuración creada")

            print("\n" + "=" * 70)
            print("✅ DATOS POBLADOS EXITOSAMENTE")
            print("=" * 70)
            print(f"\n📊 Resumen:")
            print(f"   - {len(citas)} citas")
            print(f"   - {len(estudios)} estudios")
            print(f"   - {len(pagos)} pagos")
            print(f"   - {len(mensajes)} mensajes")
            print(f"   - {len(recordatorios)} recordatorios")
            print(f"   - 1 configuración")
            print(f"\n🎯 Paciente ID: {paciente_id}")

        except Exception as e:
            await db.rollback()
            print(f"\n❌ Error: {e}")
            import traceback

            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(poblar_datos())
