"""
Script para poblar datos de prueba del módulo de Aplicación Móvil
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.app_movil import (
    DispositivoMovil,
    NotificacionPush,
    DocumentoEscaneado,
    SincronizacionOffline,
    CitaMovil,
    ConfiguracionAppMovil,
    SesionMovil,
)
from app.models.user import User
from app.models.paciente import Paciente


async def poblar_datos():
    print("🚀 Iniciando población de datos de prueba para Aplicación Móvil...")

    async with AsyncSessionLocal() as db:
        try:
            # Obtener usuarios y pacientes existentes
            result = await db.execute(select(User).limit(3))
            usuarios = result.scalars().all()

            if not usuarios:
                print("❌ No hay usuarios en la base de datos. Crea usuarios primero.")
                return

            result = await db.execute(select(Paciente).limit(5))
            pacientes = result.scalars().all()

            print(
                f"✅ Encontrados {len(usuarios)} usuarios y {len(pacientes)} pacientes"
            )

            # 1. CREAR DISPOSITIVOS MÓVILES
            print("\n📱 Creando dispositivos móviles...")
            dispositivos = []

            dispositivos_data = [
                {
                    "usuario_id": str(usuarios[0].id),
                    "plataforma": "ios",
                    "modelo": "iPhone 14 Pro",
                    "version_os": "iOS 17.2",
                    "version_app": "1.2.0",
                    "device_id": f"ios-{uuid4().hex[:16]}",
                    "estado": "activo",
                    "notificaciones_habilitadas": True,
                    "biometria_habilitada": True,
                    "sincronizacion_automatica": True,
                    "ultimo_acceso": datetime.now() - timedelta(hours=2),
                },
                {
                    "usuario_id": (
                        str(usuarios[0].id)
                        if len(usuarios) > 0
                        else str(usuarios[0].id)
                    ),
                    "plataforma": "android",
                    "modelo": "Samsung Galaxy S23",
                    "version_os": "Android 14",
                    "version_app": "1.2.0",
                    "device_id": f"android-{uuid4().hex[:16]}",
                    "estado": "activo",
                    "notificaciones_habilitadas": True,
                    "biometria_habilitada": False,
                    "sincronizacion_automatica": True,
                    "ultimo_acceso": datetime.now() - timedelta(hours=1),
                },
                {
                    "usuario_id": (
                        str(usuarios[1].id)
                        if len(usuarios) > 1
                        else str(usuarios[0].id)
                    ),
                    "plataforma": "ios",
                    "modelo": "iPhone 13",
                    "version_os": "iOS 16.5",
                    "version_app": "1.1.5",
                    "device_id": f"ios-{uuid4().hex[:16]}",
                    "estado": "activo",
                    "notificaciones_habilitadas": True,
                    "biometria_habilitada": True,
                    "sincronizacion_automatica": False,
                    "ultimo_acceso": datetime.now() - timedelta(days=1),
                },
                {
                    "usuario_id": (
                        str(usuarios[2].id)
                        if len(usuarios) > 2
                        else str(usuarios[0].id)
                    ),
                    "plataforma": "android",
                    "modelo": "Google Pixel 8",
                    "version_os": "Android 14",
                    "version_app": "1.2.0",
                    "device_id": f"android-{uuid4().hex[:16]}",
                    "estado": "inactivo",
                    "notificaciones_habilitadas": False,
                    "biometria_habilitada": False,
                    "sincronizacion_automatica": False,
                    "ultimo_acceso": datetime.now() - timedelta(days=7),
                },
            ]

            for data in dispositivos_data:
                dispositivo = DispositivoMovil(**data)
                db.add(dispositivo)
                dispositivos.append(dispositivo)

            await db.flush()
            print(f"✅ Creados {len(dispositivos)} dispositivos móviles")

            # 2. CREAR NOTIFICACIONES PUSH
            print("\n🔔 Creando notificaciones push...")
            notificaciones = []

            notificaciones_data = [
                {
                    "dispositivo_id": str(dispositivos[0].id),
                    "usuario_id": str(usuarios[0].id),
                    "tipo": "cita",
                    "titulo": "Recordatorio de Cita",
                    "mensaje": "Tienes una cita mañana a las 10:00 AM con el Dr. García",
                    "estado": "entregada",
                    "prioridad": "alta",
                    "fecha_envio": datetime.now() - timedelta(hours=3),
                    "fecha_entrega": datetime.now() - timedelta(hours=3),
                },
                {
                    "dispositivo_id": str(dispositivos[0].id),
                    "usuario_id": str(usuarios[0].id),
                    "tipo": "resultado",
                    "titulo": "Resultados de Laboratorio Disponibles",
                    "mensaje": "Tus resultados de análisis de sangre ya están disponibles",
                    "estado": "leida",
                    "prioridad": "normal",
                    "fecha_envio": datetime.now() - timedelta(days=1),
                    "fecha_entrega": datetime.now() - timedelta(days=1),
                    "fecha_lectura": datetime.now() - timedelta(hours=20),
                },
                {
                    "dispositivo_id": str(dispositivos[1].id),
                    "usuario_id": str(usuarios[0].id),
                    "tipo": "recordatorio",
                    "titulo": "Tomar Medicamento",
                    "mensaje": "Es hora de tomar tu medicamento: Losartán 50mg",
                    "estado": "enviada",
                    "prioridad": "alta",
                    "fecha_envio": datetime.now() - timedelta(hours=1),
                },
                {
                    "dispositivo_id": str(dispositivos[0].id),
                    "usuario_id": str(usuarios[0].id),
                    "tipo": "mensaje",
                    "titulo": "Nuevo Mensaje del Dr. García",
                    "mensaje": "Por favor confirma tu asistencia a la cita de mañana",
                    "estado": "entregada",
                    "prioridad": "normal",
                    "fecha_envio": datetime.now() - timedelta(hours=5),
                    "fecha_entrega": datetime.now() - timedelta(hours=5),
                },
                {
                    "dispositivo_id": str(dispositivos[1].id),
                    "usuario_id": str(usuarios[0].id),
                    "tipo": "alerta",
                    "titulo": "Valor Crítico Detectado",
                    "mensaje": "Tu presión arterial registrada está fuera del rango normal. Consulta a tu médico.",
                    "estado": "leida",
                    "prioridad": "alta",
                    "fecha_envio": datetime.now() - timedelta(hours=12),
                    "fecha_entrega": datetime.now() - timedelta(hours=12),
                    "fecha_lectura": datetime.now() - timedelta(hours=11),
                },
                {
                    "dispositivo_id": str(dispositivos[2].id),
                    "usuario_id": (
                        str(usuarios[1].id)
                        if len(usuarios) > 1
                        else str(usuarios[0].id)
                    ),
                    "tipo": "sistema",
                    "titulo": "Actualización Disponible",
                    "mensaje": "Hay una nueva versión de la aplicación disponible (v1.2.1)",
                    "estado": "enviada",
                    "prioridad": "baja",
                    "fecha_envio": datetime.now() - timedelta(days=2),
                },
                {
                    "dispositivo_id": str(dispositivos[0].id),
                    "usuario_id": str(usuarios[0].id),
                    "tipo": "cita",
                    "titulo": "Cita Confirmada",
                    "mensaje": "Tu cita para el 15 de diciembre ha sido confirmada",
                    "estado": "leida",
                    "prioridad": "normal",
                    "fecha_envio": datetime.now() - timedelta(days=3),
                    "fecha_entrega": datetime.now() - timedelta(days=3),
                    "fecha_lectura": datetime.now() - timedelta(days=3),
                },
                {
                    "usuario_id": str(usuarios[0].id),
                    "tipo": "sistema",
                    "titulo": "Bienvenido al Sistema Móvil",
                    "mensaje": "Gracias por usar nuestra aplicación móvil. Aquí podrás gestionar tus citas, ver resultados y más.",
                    "estado": "enviada",
                    "prioridad": "normal",
                    "fecha_envio": datetime.now() - timedelta(minutes=5),
                },
            ]

            for data in notificaciones_data:
                notificacion = NotificacionPush(**data)
                db.add(notificacion)
                notificaciones.append(notificacion)

            await db.flush()
            print(f"✅ Creadas {len(notificaciones)} notificaciones push")

            # 3. CREAR DOCUMENTOS ESCANEADOS
            print("\n📄 Creando documentos escaneados...")
            documentos = []

            documentos_data = [
                {
                    "dispositivo_id": str(dispositivos[0].id),
                    "usuario_id": str(usuarios[0].id),
                    "paciente_id": str(pacientes[0].id) if pacientes else None,
                    "tipo": "receta",
                    "nombre": "Receta Médica - Dr. García",
                    "descripcion": "Receta para medicamentos de control de presión arterial",
                    "ruta_archivo": "/uploads/documentos/receta_001.pdf",
                    "tamano_bytes": 245678,
                    "mime_type": "application/pdf",
                    "ocr_procesado": True,
                    "confianza_ocr": 95,
                    "firmado": True,
                    "fecha_firma": datetime.now() - timedelta(days=2),
                    "sincronizado": True,
                },
                {
                    "dispositivo_id": str(dispositivos[0].id),
                    "usuario_id": str(usuarios[0].id),
                    "paciente_id": str(pacientes[0].id) if pacientes else None,
                    "tipo": "laboratorio",
                    "nombre": "Resultados de Análisis de Sangre",
                    "descripcion": "Biometría hemática completa",
                    "ruta_archivo": "/uploads/documentos/lab_001.jpg",
                    "tamano_bytes": 1234567,
                    "mime_type": "image/jpeg",
                    "texto_extraido": "Hemoglobina: 14.5 g/dL, Leucocitos: 7200/mm3",
                    "ocr_procesado": True,
                    "confianza_ocr": 88,
                    "firmado": False,
                    "sincronizado": True,
                },
                {
                    "dispositivo_id": str(dispositivos[1].id),
                    "usuario_id": str(usuarios[0].id),
                    "paciente_id": str(pacientes[0].id) if pacientes else None,
                    "tipo": "identificacion",
                    "nombre": "INE - Identificación Oficial",
                    "descripcion": "Copia de identificación oficial",
                    "ruta_archivo": "/uploads/documentos/ine_001.jpg",
                    "tamano_bytes": 987654,
                    "mime_type": "image/jpeg",
                    "ocr_procesado": True,
                    "confianza_ocr": 92,
                    "firmado": False,
                    "sincronizado": True,
                },
                {
                    "dispositivo_id": str(dispositivos[0].id),
                    "usuario_id": str(usuarios[0].id),
                    "paciente_id": str(pacientes[0].id) if pacientes else None,
                    "tipo": "estudio",
                    "nombre": "Radiografía de Tórax",
                    "descripcion": "Estudio radiológico de control",
                    "ruta_archivo": "/uploads/documentos/rx_001.jpg",
                    "tamano_bytes": 2345678,
                    "mime_type": "image/jpeg",
                    "ocr_procesado": False,
                    "firmado": False,
                    "sincronizado": False,
                },
                {
                    "dispositivo_id": str(dispositivos[1].id),
                    "usuario_id": str(usuarios[0].id),
                    "paciente_id": str(pacientes[0].id) if pacientes else None,
                    "tipo": "consentimiento",
                    "nombre": "Consentimiento Informado - Cirugía",
                    "descripcion": "Consentimiento firmado para procedimiento quirúrgico",
                    "ruta_archivo": "/uploads/documentos/consent_001.pdf",
                    "tamano_bytes": 456789,
                    "mime_type": "application/pdf",
                    "ocr_procesado": True,
                    "confianza_ocr": 97,
                    "firmado": True,
                    "fecha_firma": datetime.now() - timedelta(days=5),
                    "sincronizado": True,
                },
            ]

            for data in documentos_data:
                documento = DocumentoEscaneado(**data)
                db.add(documento)
                documentos.append(documento)

            await db.flush()
            print(f"✅ Creados {len(documentos)} documentos escaneados")

            # 4. CREAR CITAS MÓVILES
            print("\n📅 Creando citas móviles...")
            citas = []

            citas_data = [
                {
                    "dispositivo_id": str(dispositivos[0].id),
                    "usuario_id": str(usuarios[0].id),
                    "paciente_id": str(pacientes[0].id) if pacientes else None,
                    "medico_id": (
                        str(usuarios[1].id)
                        if len(usuarios) > 1
                        else str(usuarios[0].id)
                    ),
                    "fecha_hora": datetime.now() + timedelta(days=1, hours=10),
                    "duracion_minutos": 30,
                    "motivo": "Consulta de control",
                    "notas": "Revisión de presión arterial y ajuste de medicamento",
                    "estado": "confirmada",
                    "es_telemedicina": False,
                },
                {
                    "dispositivo_id": str(dispositivos[0].id),
                    "usuario_id": str(usuarios[0].id),
                    "paciente_id": str(pacientes[0].id) if pacientes else None,
                    "medico_id": (
                        str(usuarios[1].id)
                        if len(usuarios) > 1
                        else str(usuarios[0].id)
                    ),
                    "fecha_hora": datetime.now() + timedelta(days=7, hours=15),
                    "duracion_minutos": 45,
                    "motivo": "Revisión de resultados de laboratorio",
                    "estado": "programada",
                    "es_telemedicina": True,
                },
                {
                    "dispositivo_id": str(dispositivos[1].id),
                    "usuario_id": str(usuarios[0].id),
                    "paciente_id": (
                        str(pacientes[1].id)
                        if len(pacientes) > 1
                        else (str(pacientes[0].id) if pacientes else None)
                    ),
                    "medico_id": (
                        str(usuarios[2].id)
                        if len(usuarios) > 2
                        else str(usuarios[0].id)
                    ),
                    "fecha_hora": datetime.now() - timedelta(days=3, hours=9),
                    "duracion_minutos": 30,
                    "motivo": "Consulta general",
                    "estado": "completada",
                    "es_telemedicina": False,
                    "fecha_completada": datetime.now()
                    - timedelta(days=3, hours=8, minutes=30),
                },
            ]

            for data in citas_data:
                cita = CitaMovil(**data)
                db.add(cita)
                citas.append(cita)

            await db.flush()
            print(f"✅ Creadas {len(citas)} citas móviles")

            # 5. CREAR CONFIGURACIÓN
            print("\n⚙️ Creando configuración de app móvil...")

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
            print("✅ Creada configuración de app móvil")

            # 6. CREAR SESIONES
            print("\n🔐 Creando sesiones móviles...")
            sesiones = []

            sesiones_data = [
                {
                    "dispositivo_id": str(dispositivos[0].id),
                    "usuario_id": str(usuarios[0].id),
                    "token": f"session-{uuid4().hex}",
                    "fecha_inicio": datetime.now() - timedelta(hours=2),
                    "fecha_expiracion": datetime.now() + timedelta(days=7),
                    "activa": True,
                },
                {
                    "dispositivo_id": str(dispositivos[1].id),
                    "usuario_id": str(usuarios[0].id),
                    "token": f"session-{uuid4().hex}",
                    "fecha_inicio": datetime.now() - timedelta(hours=1),
                    "fecha_expiracion": datetime.now() + timedelta(days=7),
                    "activa": True,
                },
                {
                    "dispositivo_id": str(dispositivos[2].id),
                    "usuario_id": (
                        str(usuarios[1].id)
                        if len(usuarios) > 1
                        else str(usuarios[0].id)
                    ),
                    "token": f"session-{uuid4().hex}",
                    "fecha_inicio": datetime.now() - timedelta(days=2),
                    "fecha_expiracion": datetime.now() + timedelta(days=5),
                    "activa": True,
                },
            ]

            for data in sesiones_data:
                sesion = SesionMovil(**data)
                db.add(sesion)
                sesiones.append(sesion)

            await db.flush()
            print(f"✅ Creadas {len(sesiones)} sesiones móviles")

            # Commit final
            await db.commit()

            print("\n" + "=" * 60)
            print("✅ POBLACIÓN DE DATOS COMPLETADA EXITOSAMENTE")
            print("=" * 60)
            print(f"\n📊 Resumen:")
            print(f"   • {len(dispositivos)} dispositivos móviles")
            print(f"   • {len(notificaciones)} notificaciones push")
            print(f"   • {len(documentos)} documentos escaneados")
            print(f"   • {len(citas)} citas móviles")
            print(f"   • 1 configuración de app")
            print(f"   • {len(sesiones)} sesiones activas")
            print(f"\n🎉 ¡El módulo de Aplicación Móvil está listo para usar!")
            print(f"   Accede a: http://localhost:5173/app-movil")

        except Exception as e:
            await db.rollback()
            print(f"\n❌ Error al poblar datos: {e}")
            import traceback

            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(poblar_datos())
