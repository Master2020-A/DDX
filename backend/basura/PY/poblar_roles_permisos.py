"""
Script para poblar roles y permisos del sistema
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.models import *
from app.core.database import get_db
from app.services.permission_service import PermissionService


async def poblar_roles_permisos():
    """Crea roles y permisos básicos del sistema"""

    async for db in get_db():
        try:
            service = PermissionService(db)

            print("🔧 Creando permisos básicos...\n")

            # Permisos de usuarios
            permisos_usuarios = [
                {
                    "nombre": "Ver Usuarios",
                    "codigo": "usuarios.ver",
                    "descripcion": "Permite ver la lista de usuarios",
                    "modulo": "usuarios",
                    "recurso": "usuario",
                    "accion": "ver",
                },
                {
                    "nombre": "Crear Usuarios",
                    "codigo": "usuarios.crear",
                    "descripcion": "Permite crear nuevos usuarios",
                    "modulo": "usuarios",
                    "recurso": "usuario",
                    "accion": "crear",
                },
                {
                    "nombre": "Editar Usuarios",
                    "codigo": "usuarios.editar",
                    "descripcion": "Permite editar usuarios existentes",
                    "modulo": "usuarios",
                    "recurso": "usuario",
                    "accion": "editar",
                },
                {
                    "nombre": "Eliminar Usuarios",
                    "codigo": "usuarios.eliminar",
                    "descripcion": "Permite eliminar usuarios",
                    "modulo": "usuarios",
                    "recurso": "usuario",
                    "accion": "eliminar",
                },
            ]

            # Permisos de pacientes
            permisos_pacientes = [
                {
                    "nombre": "Ver Pacientes",
                    "codigo": "pacientes.ver",
                    "descripcion": "Permite ver la lista de pacientes",
                    "modulo": "pacientes",
                    "recurso": "paciente",
                    "accion": "ver",
                },
                {
                    "nombre": "Crear Pacientes",
                    "codigo": "pacientes.crear",
                    "descripcion": "Permite registrar nuevos pacientes",
                    "modulo": "pacientes",
                    "recurso": "paciente",
                    "accion": "crear",
                },
                {
                    "nombre": "Editar Pacientes",
                    "codigo": "pacientes.editar",
                    "descripcion": "Permite editar datos de pacientes",
                    "modulo": "pacientes",
                    "recurso": "paciente",
                    "accion": "editar",
                },
            ]

            # Permisos de consultas
            permisos_consultas = [
                {
                    "nombre": "Ver Consultas",
                    "codigo": "consultas.ver",
                    "descripcion": "Permite ver consultas médicas",
                    "modulo": "consultas",
                    "recurso": "consulta",
                    "accion": "ver",
                },
                {
                    "nombre": "Crear Consultas",
                    "codigo": "consultas.crear",
                    "descripcion": "Permite crear nuevas consultas",
                    "modulo": "consultas",
                    "recurso": "consulta",
                    "accion": "crear",
                },
            ]

            # Permisos de administración
            permisos_admin = [
                {
                    "nombre": "Administrar Sistema",
                    "codigo": "admin.sistema",
                    "descripcion": "Acceso completo al sistema",
                    "modulo": "admin",
                    "recurso": "sistema",
                    "accion": "administrar",
                },
                {
                    "nombre": "Ver Auditoría",
                    "codigo": "admin.auditoria",
                    "descripcion": "Permite ver logs de auditoría",
                    "modulo": "admin",
                    "recurso": "auditoria",
                    "accion": "ver",
                },
            ]

            todos_permisos = (
                permisos_usuarios
                + permisos_pacientes
                + permisos_consultas
                + permisos_admin
            )

            # Primero verificar permisos existentes
            permisos_existentes = await service.list_permissions()
            codigos_existentes = {p.codigo for p in permisos_existentes}

            permisos_creados = []
            for perm_data in todos_permisos:
                if perm_data["codigo"] in codigos_existentes:
                    print(f"⏭️  Permiso ya existe: {perm_data['nombre']}")
                    continue

                try:
                    perm = await service.create_permission(**perm_data)
                    permisos_creados.append(perm)
                    print(f"✅ Permiso creado: {perm.nombre}")
                except Exception as e:
                    print(f"⚠️  Error al crear permiso {perm_data['nombre']}: {str(e)}")

            print(f"\n✅ {len(permisos_creados)} permisos nuevos creados")
            print(
                f"📊 Total de permisos en sistema: {len(permisos_existentes) + len(permisos_creados)}\n"
            )

            # Crear roles
            print("🔧 Creando roles del sistema...\n")

            roles_data = [
                {
                    "nombre": "Administrador",
                    "codigo": "admin",
                    "descripcion": "Acceso completo al sistema",
                    "nivel": 0,
                    "es_sistema": True,
                },
                {
                    "nombre": "Médico",
                    "codigo": "medico",
                    "descripcion": "Médico general con acceso a consultas y pacientes",
                    "nivel": 1,
                    "es_sistema": True,
                },
                {
                    "nombre": "Enfermero",
                    "codigo": "enfermero",
                    "descripcion": "Personal de enfermería",
                    "nivel": 2,
                    "es_sistema": True,
                },
                {
                    "nombre": "Administrativo",
                    "codigo": "administrativo",
                    "descripcion": "Personal administrativo",
                    "nivel": 3,
                    "es_sistema": True,
                },
            ]

            roles_creados = {}
            for role_data in roles_data:
                try:
                    role = await service.create_role(**role_data)
                    roles_creados[role.codigo] = role
                    print(f"✅ Rol creado: {role.nombre}")
                except Exception as e:
                    print(f"⚠️  Rol ya existe o error: {role_data['nombre']}")
                    # Intentar obtener el rol existente
                    roles = await service.list_roles()
                    for r in roles:
                        if r.codigo == role_data["codigo"]:
                            roles_creados[r.codigo] = r
                            break

            print(f"\n✅ {len(roles_creados)} roles disponibles\n")

            print("✅ Población de roles y permisos completada")

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback

            traceback.print_exc()
        finally:
            await db.close()
            break


if __name__ == "__main__":
    asyncio.run(poblar_roles_permisos())
