"""
Script de prueba para verificar el endpoint del dashboard administrativo
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import get_db
from sqlalchemy import select, func
from app.models.usuario import Usuario
from app.models.security import TwoFactorAuth, UserSession, AuditLog, UserRole, Role
from datetime import datetime, timedelta


async def test_dashboard():
    """Prueba el endpoint del dashboard"""

    async for db in get_db():
        try:
            print("🔍 Probando consultas del dashboard administrativo...\n")

            # Total de usuarios
            result = await db.execute(select(func.count(Usuario.id)))
            total_usuarios = result.scalar() or 0
            print(f"✅ Total de usuarios: {total_usuarios}")

            # Usuarios con 2FA
            result = await db.execute(
                select(func.count(TwoFactorAuth.usuario_id.distinct())).where(
                    TwoFactorAuth.enabled == True
                )
            )
            usuarios_con_2fa = result.scalar() or 0
            print(f"✅ Usuarios con 2FA: {usuarios_con_2fa}")

            # Sesiones activas
            result = await db.execute(
                select(func.count(UserSession.id))
                .where(UserSession.activa == True)
                .where(UserSession.revocada == False)
            )
            sesiones_activas = result.scalar() or 0
            print(f"✅ Sesiones activas: {sesiones_activas}")

            # Acciones último día
            hace_24h = datetime.utcnow() - timedelta(days=1)

            result = await db.execute(
                select(func.count(AuditLog.id)).where(AuditLog.created_at >= hace_24h)
            )
            acciones_ultimo_dia = result.scalar() or 0
            print(f"✅ Acciones último día: {acciones_ultimo_dia}")

            # Acciones fallidas último día
            result = await db.execute(
                select(func.count(AuditLog.id))
                .where(AuditLog.created_at >= hace_24h)
                .where(AuditLog.exitoso == False)
            )
            acciones_fallidas_ultimo_dia = result.scalar() or 0
            print(f"✅ Acciones fallidas último día: {acciones_fallidas_ultimo_dia}")

            # Distribución de roles
            result = await db.execute(
                select(Role.nombre, func.count(UserRole.usuario_id))
                .join(UserRole, Role.id == UserRole.role_id)
                .group_by(Role.nombre)
            )
            roles_dict = {row[0]: row[1] for row in result.all()}
            print(f"✅ Distribución de roles: {roles_dict}")

            print("\n" + "=" * 60)
            print("✅ TODAS LAS CONSULTAS FUNCIONAN CORRECTAMENTE")
            print("=" * 60)

            print("\n📊 Respuesta del dashboard:")
            dashboard_data = {
                "total_usuarios": total_usuarios,
                "usuarios_con_2fa": usuarios_con_2fa,
                "sesiones_activas": sesiones_activas,
                "acciones_ultimo_dia": acciones_ultimo_dia,
                "acciones_fallidas_ultimo_dia": acciones_fallidas_ultimo_dia,
                "roles": roles_dict,
            }

            import json

            print(json.dumps(dashboard_data, indent=2, ensure_ascii=False))

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback

            traceback.print_exc()
        finally:
            await db.close()
            break


if __name__ == "__main__":
    asyncio.run(test_dashboard())
