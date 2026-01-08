"""
Script simple para crear roles básicos del sistema
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.models import *
from app.core.database import get_db
from sqlalchemy import select


async def crear_roles():
    """Crea roles básicos directamente en la BD"""

    async for db in get_db():
        try:
            print("🔧 Verificando roles existentes...\n")

            # Verificar roles existentes
            result = await db.execute(select(Role))
            roles_existentes = result.scalars().all()

            codigos_existentes = {r.codigo for r in roles_existentes}
            print(f"📊 Roles existentes: {len(roles_existentes)}")
            for r in roles_existentes:
                print(f"   - {r.nombre} ({r.codigo})")
            print()

            # Roles a crear
            roles_data = [
                {
                    "nombre": "Administrador",
                    "codigo": "admin",
                    "descripcion": "Acceso completo al sistema",
                    "nivel": 0,
                    "activo": True,
                    "es_sistema": True,
                },
                {
                    "nombre": "Médico",
                    "codigo": "medico",
                    "descripcion": "Médico general con acceso a consultas y pacientes",
                    "nivel": 1,
                    "activo": True,
                    "es_sistema": True,
                },
                {
                    "nombre": "Enfermero",
                    "codigo": "enfermero",
                    "descripcion": "Personal de enfermería",
                    "nivel": 2,
                    "activo": True,
                    "es_sistema": True,
                },
                {
                    "nombre": "Administrativo",
                    "codigo": "administrativo",
                    "descripcion": "Personal administrativo",
                    "nivel": 3,
                    "activo": True,
                    "es_sistema": True,
                },
            ]

            print("🔧 Creando roles nuevos...\n")

            roles_creados = 0
            for role_data in roles_data:
                if role_data["codigo"] in codigos_existentes:
                    print(f"⏭️  Rol ya existe: {role_data['nombre']}")
                    continue

                try:
                    nuevo_rol = Role(**role_data)
                    db.add(nuevo_rol)
                    await db.commit()
                    await db.refresh(nuevo_rol)
                    roles_creados += 1
                    print(f"✅ Rol creado: {nuevo_rol.nombre}")
                except Exception as e:
                    await db.rollback()
                    print(f"⚠️  Error al crear rol {role_data['nombre']}: {str(e)}")

            print(f"\n✅ {roles_creados} roles nuevos creados")

            # Mostrar resumen final
            result = await db.execute(select(Role))
            todos_roles = result.scalars().all()
            print(f"📊 Total de roles en sistema: {len(todos_roles)}\n")

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback

            traceback.print_exc()
        finally:
            await db.close()
            break


if __name__ == "__main__":
    asyncio.run(crear_roles())
