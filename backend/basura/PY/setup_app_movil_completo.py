"""
Script completo para crear tablas y poblar datos del módulo de Aplicación Móvil
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent))


async def main():
    print("=" * 70)
    print("🚀 CONFIGURACIÓN COMPLETA DEL MÓDULO DE APLICACIÓN MÓVIL")
    print("=" * 70)

    # PASO 1: Crear tablas
    print("\n📦 PASO 1: Creando tablas de base de datos...")
    try:
        from app.core.database import engine, Base
        from app.models.app_movil import (
            DispositivoMovil,
            NotificacionPush,
            DocumentoEscaneado,
            SincronizacionOffline,
            CitaMovil,
            ConfiguracionAppMovil,
            SesionMovil,
        )

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        print("✅ Tablas creadas exitosamente:")
        print("   • dispositivos_moviles")
        print("   • notificaciones_push")
        print("   • documentos_escaneados")
        print("   • sincronizacion_offline")
        print("   • citas_moviles")
        print("   • configuracion_app_movil")
        print("   • sesiones_moviles")

    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        import traceback

        traceback.print_exc()
        return

    # PASO 2: Poblar datos
    print("\n📊 PASO 2: Poblando datos de prueba...")

    from sqlalchemy import select
    from app.core.database import AsyncSessionLocal
    from app.models.usuario import Usuario
    from app.models.paciente import Paciente

    async with AsyncSessionLocal() as db:
        try:
            # Obtener usuarios
            result = await db.execute(select(Usuario).limit(3))
            usuarios = result.scalars().all()

            if not usuarios:
                print("⚠️  No hay usuarios. Creando usuario de prueba...")
                # Crear usuario de prueba si no existe
                from app.core.security import get_password_hash

                usuario_prueba = Usuario(
                    email="admin@ddx.com",
                    username="admin",
                    hashed_password=get_password_hash("admin123"),
                    nombre="Administrador",
                    apellido="Sistema",
                    rol="admin",
                    activo=True,
                )
                db.add(usuario_prueba)
                await db.flush()
                usuarios = [usuario_prueba]

            result = await db.execute(select(Paciente).limit(5))
            pacientes = result.scalars().all()

            print(
                f"✅ Encontrados {len(usuarios)} usuarios y {len(pacientes)} pacientes"
            )

            # Crear dispositivos
            print("\n📱 Creando 4 dispositivos móviles...")
            dispositivos = []

            for i, (plataforma, modelo, version_os, estado) in enumerate(
                [
                    ("ios", "iPhone 14 Pro", "iOS 17.2", "activo"),
                    ("android", "Samsung Galaxy S23", "Android 14", "activo"),
                    ("ios", "iPhone 13", "iOS 16.5", "activo"),
                    ("android", "Google Pixel 8", "Android 14", "inactivo"),
                ]
            ):
                dispositivo = DispositivoMovil(
                    usuario_id=str(usuarios[min(i, len(usuarios) - 1)].id),
                    plataforma=plataforma,
                    modelo=modelo,
                    version_os=version_os,
                    version_app="1.2.0",
                    device_id=f"{plataforma}-{uuid4().hex[:16]}",
                    estado=estado,
                    notificaciones_habilitadas=True,
                    biometria_habilitada=(plataforma == "ios"),
                    sincronizacion_automatica=True,
                    ultimo_acceso=datetime.now() - timedelta(hours=i + 1),
                )
                db.add(dispositivo)
                dispositivos.append(dispositivo)

            await db.flush()
            print(f"✅ {len(dispositivos)} dispositivos creados")

            # Crear notificaciones
            print("\n🔔 Creando 8 notificaciones push...")
            notificaciones_data = [
                (
                    "cita",
                    "Recordatorio de Cita",
                    "Tienes una cita mañana a las 10:00 AM",
                    "alta",
                    "entregada",
                    3,
                ),
                (
                    "resultado",
                    "Resultados Disponibles",
                    "Tus resultados de laboratorio están listos",
                    "normal",
                    "leida",
                    24,
                ),
                (
                    "recordatorio",
                    "Tomar Medicamento",
                    "Es hora de tomar tu medicamento",
                    "alta",
                    "enviada",
                    1,
                ),
                (
                    "mensaje",
                    "Mensaje del Dr. García",
                    "Por favor confirma tu asistencia",
                    "normal",
                    "entregada",
                    5,
                ),
                (
                    "alerta",
                    "Valor Crítico",
                    "Tu presión arterial está fuera del rango",
                    "alta",
                    "leida",
                    12,
                ),
                (
                    "sistema",
                    "Actualización Disponible",
                    "Nueva versión disponible (v1.2.1)",
                    "baja",
                    "enviada",
                    48,
                ),
                (
                    "cita",
                    "Cita Confirmada",
                    "Tu cita ha sido confirmada",
                    "normal",
                    "leida",
                    72,
                ),
                (
                    "sistema",
                    "Bienvenido",
                    "Gracias por usar nuestra app",
                    "normal",
                    "enviada",
                    0,
                ),
            ]

            for (
                tipo,
                titulo,
                mensaje,
                prioridad,
                estado,
                horas_atras,
            ) in notificaciones_data:
                fecha_envio = datetime.now() - timedelta(hours=horas_atras)
                notif = NotificacionPush(
                    dispositivo_id=(
                        str(dispositivos[0].id) if horas_atras < 24 else None
                    ),
                    usuario_id=str(usuarios[0].id),
                    tipo=tipo,
                    titulo=titulo,
                    mensaje=mensaje,
                    estado=estado,
                    prioridad=prioridad,
                    fecha_envio=fecha_envio,
                    fecha_entrega=(
                        fecha_envio if estado in ["entregada", "leida"] else None
                    ),
                    fecha_lectura=fecha_envio if estado == "leida" else None,
                )
                db.add(notif)

            await db.flush()
            print("✅ 8 notificaciones creadas")

            # Crear documentos
            print("\n📄 Creando 5 documentos escaneados...")
            documentos_data = [
                ("receta", "Receta Médica", "application/pdf", True, 95, True),
                ("laboratorio", "Resultados de Sangre", "image/jpeg", True, 88, False),
                ("identificacion", "INE", "image/jpeg", True, 92, False),
                ("estudio", "Radiografía", "image/jpeg", False, None, False),
                (
                    "consentimiento",
                    "Consentimiento Quirúrgico",
                    "application/pdf",
                    True,
                    97,
                    True,
                ),
            ]

            for tipo, nombre, mime, ocr, confianza, firmado in documentos_data:
                doc = DocumentoEscaneado(
                    dispositivo_id=str(dispositivos[0].id),
                    usuario_id=str(usuarios[0].id),
                    paciente_id=str(pacientes[0].id) if pacientes else None,
                    tipo=tipo,
                    nombre=nombre,
                    ruta_archivo=f"/uploads/{tipo}_{uuid4().hex[:8]}.pdf",
                    tamano_bytes=500000 + (len(nombre) * 1000),
                    mime_type=mime,
                    ocr_procesado=ocr,
                    confianza_ocr=confianza,
                    firmado=firmado,
                    fecha_firma=datetime.now() - timedelta(days=2) if firmado else None,
                    sincronizado=True,
                )
                db.add(doc)

            await db.flush()
            print("✅ 5 documentos creados")

            # Crear citas
            print("\n📅 Creando 3 citas móviles...")
            citas_data = [
                (1, 10, 30, True, False, False, "Consulta de control"),
                (7, 15, 45, False, False, True, "Revisión de resultados"),
                (-3, 9, 30, True, False, False, "Consulta general"),
            ]

            for dias, hora, duracion, confirmada, cancelada, tele, motivo in citas_data:
                cita = CitaMovil(
                    dispositivo_id=str(dispositivos[0].id),
                    paciente_id=str(pacientes[0].id) if pacientes else None,
                    medico_id=(
                        str(usuarios[1].id)
                        if len(usuarios) > 1
                        else str(usuarios[0].id)
                    ),
                    fecha_hora=datetime.now() + timedelta(days=dias, hours=hora),
                    duracion_minutos=duracion,
                    motivo=motivo,
                    confirmada=confirmada,
                    cancelada=cancelada,
                    es_telemedicina=tele,
                    fecha_confirmacion=(
                        datetime.now() - timedelta(hours=1) if confirmada else None
                    ),
                )
                db.add(cita)

            await db.flush()
            print("✅ 3 citas creadas")
            # Crear configuración
            print("\n⚙️ Creando configuración...")
            config = ConfiguracionAppMovil(
                usuario_id=str(usuarios[0].id),
                notificaciones_citas=True,
                notificaciones_resultados=True,
                notificaciones_mensajes=True,
                notificaciones_recordatorios=True,
                recordatorio_citas_minutos=60,
                sincronizar_solo_wifi=True,
                sincronizar_automaticamente=True,
                intervalo_sincronizacion_minutos=30,
                requerir_biometria=True,
                timeout_sesion_minutos=15,
                tema="auto",
                idioma="es",
                limpiar_cache_automaticamente=True,
                dias_retener_datos_offline=30,
            )
            db.add(config)
            await db.flush()
            print("✅ Configuración creada")

            # Commit
            await db.commit()

            print("\n" + "=" * 70)
            print("✅ ¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE!")
            print("=" * 70)
            print("\n📊 Resumen:")
            print(f"   ✓ 4 dispositivos móviles")
            print(f"   ✓ 8 notificaciones push")
            print(f"   ✓ 5 documentos escaneados")
            print(f"   ✓ 3 citas móviles")
            print(f"   ✓ 1 configuración")
            print("\n🎉 El módulo está listo para usar!")
            print("   Accede a: http://localhost:5173/app-movil")
            print("=" * 70)

        except Exception as e:
            await db.rollback()
            print(f"\n❌ Error al poblar datos: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
