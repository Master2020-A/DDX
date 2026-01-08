"""
Script para poblar datos de prueba del módulo de seguridad
Ejecutar: python poblar_seguridad.py
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import get_db
from app.models.usuario import Usuario
from app.services.permission_service import PermissionService
from app.services.two_factor_service import TwoFactorService
from app.services.audit_service import AuditService
from sqlalchemy import select
import uuid


async def poblar_datos():
    """Poblar datos de prueba para el módulo de seguridad"""

    async for db in get_db():
        try:
            print("🔐 Iniciando población de datos de seguridad...")

            # 1. Inicializar roles y permisos por defecto
            print("\n1️⃣ Inicializando roles y permisos...")
            permission_service = PermissionService(db)
            await permission_service.initialize_default_roles()
            print("✅ Roles y permisos inicializados")

            # 2. Obtener roles
            roles = await permission_service.list_roles()
            roles_dict = {role.codigo: role for role in roles}

            print(f"   - Roles creados: {', '.join(roles_dict.keys())}")

            # 3. Crear usuarios de prueba si no existen
            print("\n2️⃣ Creando usuarios de prueba...")

            usuarios_prueba = [
                {
                    "email": "admin@ddx.com",
                    "nombre_completo": "Administrador del Sistema",
                    "rol": "admin",
                },
                {
                    "email": "garcia@ddx.com",
                    "nombre_completo": "Dr. Juan García",
                    "rol": "medico",
                },
                {
                    "email": "martinez@ddx.com",
                    "nombre_completo": "Dra. María Martínez",
                    "rol": "medico",
                },
                {
                    "email": "lopez@ddx.com",
                    "nombre_completo": "Enf. Ana López",
                    "rol": "enfermero",
                },
                {
                    "email": "rodriguez@ddx.com",
                    "nombre_completo": "Enf. Carlos Rodríguez",
                    "rol": "enfermero",
                },
                {
                    "email": "sanchez@ddx.com",
                    "nombre_completo": "Recep. Laura Sánchez",
                    "rol": "administrativo",
                },
            ]

            usuarios_creados = []
            for usuario_data in usuarios_prueba:
                # Verificar si ya existe
                result = await db.execute(
                    select(Usuario).where(Usuario.email == usuario_data["email"])
                )
                usuario_existente = result.scalar_one_or_none()

                if not usuario_existente:
                    # Crear usuario
                    nuevo_usuario = Usuario(
                        id=str(uuid.uuid4()),
                        email=usuario_data["email"],
                        nombre_completo=usuario_data["nombre_completo"],
                        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVqN4e5Oi",  # password: "password123"
                        rol=usuario_data["rol"],
                        activo=True,
                    )
                    db.add(nuevo_usuario)
                    await db.commit()
                    await db.refresh(nuevo_usuario)
                    usuarios_creados.append(nuevo_usuario)
                    print(f"   ✅ Usuario creado: {usuario_data['email']}")
                else:
                    usuarios_creados.append(usuario_existente)
                    print(f"   ℹ️  Usuario ya existe: {usuario_data['email']}")

            # 4. Asignar roles a usuarios
            print("\n3️⃣ Asignando roles a usuarios...")
            for i, usuario_data in enumerate(usuarios_prueba):
                usuario = usuarios_creados[i]
                rol_codigo = usuario_data["rol"]
                rol = roles_dict.get(rol_codigo)

                if rol:
                    # Verificar si ya tiene el rol
                    roles_actuales = await permission_service.get_user_roles(usuario.id)
                    tiene_rol = any(r.id == rol.id for r in roles_actuales)

                    if not tiene_rol:
                        await permission_service.assign_role_to_user(usuario.id, rol.id)
                        print(f"   Rol '{rol_codigo}' asignado a {usuario.email}")
                    else:
                        print(f"   {usuario.email} ya tiene el rol '{rol_codigo}'")

            # 5. Activar 2FA para algunos usuarios
            print("\n4️⃣ Configurando 2FA para usuarios...")
            two_factor_service = TwoFactorService(db)

            # Activar 2FA para admin y un médico
            usuarios_con_2fa = [
                usuarios_creados[0],
                usuarios_creados[1],
            ]  # admin y dr.garcia

            for usuario in usuarios_con_2fa:
                # Verificar si ya tiene 2FA
                is_enabled = await two_factor_service.is_enabled(usuario.id)
                if not is_enabled:
                    # Generar secreto y activar 2FA
                    secret, qr_code, provisioning_uri = (
                        await two_factor_service.generate_secret(usuario.id)
                    )
                    print(f"   ✅ 2FA configurado para {usuario.email}")
                else:
                    print(f"   ℹ️  {usuario.email} ya tiene 2FA configurado")

            # 6. Crear logs de auditoría de prueba
            print("\n5️⃣ Creando logs de auditoría de prueba...")
            audit_service = AuditService(db)

            acciones_prueba = [
                {
                    "usuario_id": usuarios_creados[0].id,
                    "accion": "login",
                    "recurso": "auth",
                    "descripcion": "Inicio de sesión exitoso",
                    "exitoso": True,
                    "ip_address": "192.168.1.100",
                },
                {
                    "usuario_id": usuarios_creados[1].id,
                    "accion": "crear",
                    "recurso": "paciente",
                    "descripcion": "Creó nuevo paciente",
                    "exitoso": True,
                    "ip_address": "192.168.1.101",
                },
                {
                    "usuario_id": usuarios_creados[1].id,
                    "accion": "editar",
                    "recurso": "consulta",
                    "descripcion": "Editó consulta médica",
                    "exitoso": True,
                    "ip_address": "192.168.1.101",
                },
                {
                    "usuario_id": usuarios_creados[2].id,
                    "accion": "login",
                    "recurso": "auth",
                    "descripcion": "Intento de inicio de sesión fallido",
                    "exitoso": False,
                    "ip_address": "192.168.1.102",
                    "mensaje_error": "Contraseña incorrecta",
                },
                {
                    "usuario_id": usuarios_creados[3].id,
                    "accion": "ver",
                    "recurso": "paciente",
                    "descripcion": "Consultó expediente de paciente",
                    "exitoso": True,
                    "ip_address": "192.168.1.103",
                },
                {
                    "usuario_id": usuarios_creados[0].id,
                    "accion": "asignar_rol",
                    "recurso": "usuario",
                    "descripcion": "Asignó rol 'médico' a usuario",
                    "exitoso": True,
                    "ip_address": "192.168.1.100",
                },
                {
                    "usuario_id": usuarios_creados[1].id,
                    "accion": "eliminar",
                    "recurso": "consulta",
                    "descripcion": "Intentó eliminar consulta sin permisos",
                    "exitoso": False,
                    "ip_address": "192.168.1.101",
                    "mensaje_error": "Permiso denegado",
                },
                {
                    "usuario_id": usuarios_creados[4].id,
                    "accion": "crear",
                    "recurso": "signos_vitales",
                    "descripcion": "Registró signos vitales de paciente",
                    "exitoso": True,
                    "ip_address": "192.168.1.104",
                },
            ]

            for accion_data in acciones_prueba:
                await audit_service.log_action(
                    usuario_id=accion_data["usuario_id"],
                    accion=accion_data["accion"],
                    recurso=accion_data["recurso"],
                    descripcion=accion_data["descripcion"],
                    exitoso=accion_data["exitoso"],
                    ip_address=accion_data["ip_address"],
                    mensaje_error=accion_data.get("mensaje_error"),
                )

            print(f"   ✅ {len(acciones_prueba)} logs de auditoría creados")

            # 7. Resumen
            print("\n" + "=" * 60)
            print("✅ DATOS DE SEGURIDAD POBLADOS EXITOSAMENTE")
            print("=" * 60)
            print(f"\n📊 Resumen:")
            print(f"   - Roles: {len(roles)} (admin, medico, enfermero, recepcionista)")
            print(f"   - Permisos: 19 permisos en total")
            print(f"   - Usuarios: {len(usuarios_creados)}")
            print(f"   - Usuarios con 2FA: {len(usuarios_con_2fa)}")
            print(f"   - Logs de auditoría: {len(acciones_prueba)}")

            print(f"\n👥 Usuarios creados:")
            for usuario_data in usuarios_prueba:
                print(
                    f"   - {usuario_data['email']} ({usuario_data['rol']}) - password: password123"
                )

            print(f"\n🔐 Acceso al panel de administración:")
            print(f"   - URL: http://localhost:3000/admin")
            print(f"   - Usuario: admin@ddx.com")
            print(f"   - Password: password123")

            print("\n" + "=" * 60)

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback

            traceback.print_exc()
        finally:
            await db.close()
            break


if __name__ == "__main__":
    asyncio.run(poblar_datos())
