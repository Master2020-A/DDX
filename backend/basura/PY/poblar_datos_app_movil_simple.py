"""
Script simplificado para poblar datos del módulo de Aplicación Móvil
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.usuario import Usuario
from app.models.paciente import Paciente
from app.models.app_movil import (
    DispositivoMovil,
    NotificacionPush,
    DocumentoEscaneado,
    CitaMovil,
    ConfiguracionAppMovil,
)


async def main():
    print("=" * 70)
    print("📊 POBLANDO DATOS DE PRUEBA - APLICACIÓN MÓVIL")
    print("=" * 70)

    async with AsyncSessionLocal() as db:
        try:
            # Obtener usuarios
            result = await db.execute(select(Usuario).limit(3))
            usuarios = list(result.scalars().all())

            result = await db.execute(select(Paciente).limit(5))
            pacientes = list(result.scalars().all())

            print(
                f"\n✅ Encontrados {len(usuarios)} usuarios y {len(pacientes)} pacientes"
            )

            if not usuarios:
                print("⚠️  No hay usuarios en la BD. Por favor crea usuarios primero.")
                return

            # 1. Dispositivos
            print("\n📱 Creando dispositivos...")
            dispositivos = []
            for i, (plat, modelo, os) in enumerate(
                [
                    ("ios", "iPhone 14 Pro", "iOS 17.2"),
                    ("android", "Samsung Galaxy S23", "Android 14"),
                ]
            ):
                disp = DispositivoMovil(
                    usuario_id=str(usuarios[0].id),
                    plataforma=plat,
                    modelo=modelo,
                    version_os=os,
                    version_app="1.2.0",
                    device_id=f"{plat}-{uuid4().hex[:16]}",
                    estado="activo",
                    notificaciones_habilitadas=True,
                    biometria_habilitada=True,
                    sincronizacion_automatica=True,
                    ultimo_acceso=datetime.now() - timedelta(hours=i + 1),
                )
                db.add(disp)
                dispositivos.append(disp)

            await db.flush()
            print(f"✅ {len(dispositivos)} dispositivos creados")

            # 2. Notificaciones
            print("\n🔔 Creando notificaciones...")
            notifs = [
                (
                    "cita",
                    "Recordatorio de Cita",
                    "Tienes una cita mañana",
                    "alta",
                    "entregada",
                    3,
                    True,
                ),
                (
                    "resultado",
                    "Resultados Disponibles",
                    "Tus resultados están listos",
                    "normal",
                    "leida",
                    24,
                    False,
                ),
                (
                    "recordatorio",
                    "Tomar Medicamento",
                    "Es hora de tu medicamento",
                    "alta",
                    "enviada",
                    1,
                    True,
                ),
                (
                    "mensaje",
                    "Mensaje del Dr. García",
                    "Confirma tu asistencia",
                    "normal",
                    "entregada",
                    5,
                    True,
                ),
                (
                    "alerta",
                    "Valor Crítico",
                    "Presión arterial fuera de rango",
                    "alta",
                    "leida",
                    12,
                    False,
                ),
                (
                    "sistema",
                    "Actualización",
                    "Nueva versión disponible",
                    "baja",
                    "enviada",
                    48,
                    False,
                ),
                (
                    "cita",
                    "Cita Confirmada",
                    "Tu cita ha sido confirmada",
                    "normal",
                    "leida",
                    72,
                    False,
                ),
                (
                    "sistema",
                    "Bienvenido",
                    "Gracias por usar nuestra app",
                    "normal",
                    "enviada",
                    0,
                    True,
                ),
            ]

            for tipo, titulo, msg, prio, estado, horas, con_disp in notifs:
                fecha = datetime.now() - timedelta(hours=horas)
                notif = NotificacionPush(
                    dispositivo_id=str(dispositivos[0].id) if con_disp else None,
                    usuario_id=str(usuarios[0].id),
                    tipo=tipo,
                    titulo=titulo,
                    mensaje=msg,
                    estado=estado,
                    prioridad=prio,
                    fecha_envio=fecha,
                    fecha_entrega=fecha if estado in ["entregada", "leida"] else None,
                    fecha_lectura=fecha if estado == "leida" else None,
                )
                db.add(notif)

            await db.flush()
            print(f"✅ {len(notifs)} notificaciones creadas")

            # 3. Documentos
            print("\n📄 Creando documentos...")
            docs = [
                ("receta", "Receta Médica", True, 95, True),
                ("laboratorio", "Resultados de Sangre", True, 88, False),
                ("identificacion", "INE", True, 92, False),
            ]

            for tipo, nombre, ocr, conf, firmado in docs:
                doc = DocumentoEscaneado(
                    dispositivo_id=str(dispositivos[0].id),
                    usuario_id=str(usuarios[0].id),
                    paciente_id=str(pacientes[0].id) if pacientes else None,
                    tipo=tipo,
                    nombre=nombre,
                    ruta_archivo=f"/uploads/{tipo}_{uuid4().hex[:8]}.pdf",
                    tamano_bytes=500000,
                    mime_type="application/pdf",
                    ocr_procesado=ocr,
                    confianza_ocr=conf if ocr else None,
                    firmado=firmado,
                    fecha_firma=datetime.now() - timedelta(days=2) if firmado else None,
                    sincronizado=True,
                )
                db.add(doc)

            await db.flush()
            print(f"✅ {len(docs)} documentos creados")

            # 4. Citas
            print("\n📅 Creando citas...")
            citas = [
                (1, 10, 30, True, "Consulta de control"),
                (7, 15, 45, False, "Revisión de resultados"),
            ]

            for dias, hora, dur, conf, motivo in citas:
                cita = CitaMovil(
                    dispositivo_id=str(dispositivos[0].id),
                    paciente_id=str(pacientes[0].id) if pacientes else None,
                    medico_id=(
                        str(usuarios[1].id)
                        if len(usuarios) > 1
                        else str(usuarios[0].id)
                    ),
                    fecha_hora=datetime.now() + timedelta(days=dias, hours=hora),
                    duracion_minutos=dur,
                    motivo=motivo,
                    confirmada=conf,
                    fecha_confirmacion=datetime.now() if conf else None,
                )
                db.add(cita)

            await db.flush()
            print(f"✅ {len(citas)} citas creadas")

            # 5. Configuración
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
            print("✅ ¡DATOS CREADOS EXITOSAMENTE!")
            print("=" * 70)
            print("\n📊 Resumen:")
            print(f"   ✓ {len(dispositivos)} dispositivos móviles")
            print(f"   ✓ {len(notifs)} notificaciones push")
            print(f"   ✓ {len(docs)} documentos escaneados")
            print(f"   ✓ {len(citas)} citas móviles")
            print(f"   ✓ 1 configuración")
            print("\n🎉 ¡Listo! Recarga el navegador y verás las notificaciones")
            print("   http://localhost:5173/app-movil")
            print("=" * 70)

        except Exception as e:
            await db.rollback()
            print(f"\n❌ Error: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
