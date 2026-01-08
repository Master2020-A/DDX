"""
Script para activar 2FA y crear logs de auditoría
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import get_db
from app.models.usuario import Usuario
from app.models.security import TwoFactorAuth
from app.services.audit_service import AuditService
from sqlalchemy import select, update


async def activar_2fa_y_logs():
    """Activa 2FA para usuarios y crea logs"""

    async for db in get_db():
        try:
            print("🔐 Activando 2FA y creando logs...\n")

            # 1. Activar 2FA para admin y garcia
            print("1️⃣ Activando 2FA...")
            emails_2fa = ["admin@ddx.com", "garcia@ddx.com"]

            for email in emails_2fa:
                # Obtener usuario
                result = await db.execute(select(Usuario).where(Usuario.email == email))
                usuario = result.scalar_one_or_none()

                if usuario:
                    # Buscar registro 2FA
                    result = await db.execute(
                        select(TwoFactorAuth).where(
                            TwoFactorAuth.usuario_id == usuario.id
                        )
                    )
                    two_fa = result.scalar_one_or_none()

                    if two_fa:
                        # Activar 2FA
                        two_fa.enabled = True
                        two_fa.verified = True
                        await db.commit()
                        print(f"   ✅ 2FA activado para {email}")
                    else:
                        print(f"   ⚠️  No hay registro 2FA para {email}")
                else:
                    print(f"   ⚠️  Usuario {email} no encontrado")

            # 2. Crear logs de auditoría
            print("\n2️⃣ Creando logs de auditoría...")

            # Obtener usuarios para los logs
            result = await db.execute(select(Usuario))
            usuarios = result.scalars().all()
            usuarios_dict = {u.email: u for u in usuarios}

            audit_service = AuditService(db)

            acciones = [
                {
                    "email": "admin@ddx.com",
                    "accion": "login",
                    "recurso": "auth",
                    "descripcion": "Inicio de sesión exitoso",
                    "exitoso": True,
                    "ip_address": "192.168.1.100",
                },
                {
                    "email": "garcia@ddx.com",
                    "accion": "crear",
                    "recurso": "paciente",
                    "descripcion": "Creó nuevo paciente",
                    "exitoso": True,
                    "ip_address": "192.168.1.101",
                },
                {
                    "email": "garcia@ddx.com",
                    "accion": "editar",
                    "recurso": "consulta",
                    "descripcion": "Editó consulta médica",
                    "exitoso": True,
                    "ip_address": "192.168.1.101",
                },
                {
                    "email": "martinez@ddx.com",
                    "accion": "login",
                    "recurso": "auth",
                    "descripcion": "Intento de inicio de sesión fallido",
                    "exitoso": False,
                    "ip_address": "192.168.1.102",
                    "mensaje_error": "Contraseña incorrecta",
                },
                {
                    "email": "lopez@ddx.com",
                    "accion": "ver",
                    "recurso": "paciente",
                    "descripcion": "Consultó expediente de paciente",
                    "exitoso": True,
                    "ip_address": "192.168.1.103",
                },
                {
                    "email": "admin@ddx.com",
                    "accion": "asignar_rol",
                    "recurso": "usuario",
                    "descripcion": "Asignó rol 'médico' a usuario",
                    "exitoso": True,
                    "ip_address": "192.168.1.100",
                },
                {
                    "email": "garcia@ddx.com",
                    "accion": "eliminar",
                    "recurso": "consulta",
                    "descripcion": "Intentó eliminar consulta sin permisos",
                    "exitoso": False,
                    "ip_address": "192.168.1.101",
                    "mensaje_error": "Permiso denegado",
                },
                {
                    "email": "rodriguez@ddx.com",
                    "accion": "crear",
                    "recurso": "signos_vitales",
                    "descripcion": "Registró signos vitales de paciente",
                    "exitoso": True,
                    "ip_address": "192.168.1.104",
                },
            ]

            logs_creados = 0
            for accion_data in acciones:
                usuario = usuarios_dict.get(accion_data["email"])
                if usuario:
                    await audit_service.log_action(
                        usuario_id=usuario.id,
                        accion=accion_data["accion"],
                        recurso=accion_data["recurso"],
                        descripcion=accion_data["descripcion"],
                        exitoso=accion_data["exitoso"],
                        ip_address=accion_data["ip_address"],
                        mensaje_error=accion_data.get("mensaje_error"),
                    )
                    logs_creados += 1

            print(f"   ✅ {logs_creados} logs de auditoría creados")

            print("\n" + "=" * 60)
            print("✅ 2FA Y LOGS CONFIGURADOS EXITOSAMENTE")
            print("=" * 60)

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback

            traceback.print_exc()
        finally:
            await db.close()
            break


if __name__ == "__main__":
    asyncio.run(activar_2fa_y_logs())
