"""
Servicio para sistema de roles y permisos granulares (RBAC)
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import Optional, List, Set
from uuid import UUID

from app.models.security import Permission, Role, RolePermission, UserRole
from app.models.usuario import Usuario


class PermissionService:
    """Servicio para gestión de permisos granulares"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== PERMISOS ====================

    async def create_permission(
        self,
        nombre: str,
        codigo: str,
        modulo: str,
        recurso: str,
        accion: str,
        descripcion: Optional[str] = None,
    ) -> Permission:
        """
        Crea un nuevo permiso
        """
        permission = Permission(
            nombre=nombre,
            codigo=codigo,
            modulo=modulo,
            recurso=recurso,
            accion=accion,
            descripcion=descripcion,
            activo=True,
        )

        self.db.add(permission)
        await self.db.commit()
        await self.db.refresh(permission)

        return permission

    async def get_permission(self, permission_id: UUID) -> Optional[Permission]:
        """
        Obtiene un permiso por ID
        """
        result = await self.db.execute(
            select(Permission).where(Permission.id == permission_id)
        )
        return result.scalar_one_or_none()

    async def get_permission_by_code(self, codigo: str) -> Optional[Permission]:
        """
        Obtiene un permiso por código
        """
        result = await self.db.execute(
            select(Permission).where(Permission.codigo == codigo)
        )
        return result.scalar_one_or_none()

    async def list_permissions(
        self, modulo: Optional[str] = None, activo: Optional[bool] = None
    ) -> List[Permission]:
        """
        Lista permisos con filtros opcionales
        """
        query = select(Permission)

        conditions = []
        if modulo:
            conditions.append(Permission.modulo == modulo)
        if activo is not None:
            conditions.append(Permission.activo == activo)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(Permission.modulo, Permission.recurso, Permission.accion)

        result = await self.db.execute(query)
        return result.scalars().all()

    # ==================== ROLES ====================

    async def create_role(
        self,
        nombre: str,
        codigo: str,
        descripcion: Optional[str] = None,
        nivel: int = 0,
        rol_padre_id: Optional[UUID] = None,
    ) -> Role:
        """
        Crea un nuevo rol
        """
        role = Role(
            nombre=nombre,
            codigo=codigo,
            descripcion=descripcion,
            nivel=nivel,
            rol_padre_id=rol_padre_id,
            activo=True,
            es_sistema=False,
        )

        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)

        return role

    async def get_role(self, role_id: UUID) -> Optional[Role]:
        """
        Obtiene un rol por ID
        """
        result = await self.db.execute(select(Role).where(Role.id == role_id))
        return result.scalar_one_or_none()

    async def get_role_by_code(self, codigo: str) -> Optional[Role]:
        """
        Obtiene un rol por código
        """
        result = await self.db.execute(select(Role).where(Role.codigo == codigo))
        return result.scalar_one_or_none()

    async def list_roles(self, activo: Optional[bool] = None) -> List[Role]:
        """
        Lista roles con filtros opcionales
        """
        query = select(Role)

        if activo is not None:
            query = query.where(Role.activo == activo)

        query = query.order_by(Role.nivel, Role.nombre)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def assign_permission_to_role(
        self,
        role_id: UUID,
        permission_id: UUID,
        concedido_por_id: Optional[UUID] = None,
    ) -> RolePermission:
        """
        Asigna un permiso a un rol
        """
        # Verificar si ya existe
        result = await self.db.execute(
            select(RolePermission).where(
                and_(
                    RolePermission.role_id == role_id,
                    RolePermission.permission_id == permission_id,
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            return existing

        role_permission = RolePermission(
            role_id=role_id,
            permission_id=permission_id,
            concedido_por_id=concedido_por_id,
        )

        self.db.add(role_permission)
        await self.db.commit()
        await self.db.refresh(role_permission)

        return role_permission

    async def remove_permission_from_role(
        self, role_id: UUID, permission_id: UUID
    ) -> bool:
        """
        Remueve un permiso de un rol
        """
        result = await self.db.execute(
            select(RolePermission).where(
                and_(
                    RolePermission.role_id == role_id,
                    RolePermission.permission_id == permission_id,
                )
            )
        )
        role_permission = result.scalar_one_or_none()

        if role_permission:
            await self.db.delete(role_permission)
            await self.db.commit()
            return True

        return False

    async def get_role_permissions(self, role_id: UUID) -> List[Permission]:
        """
        Obtiene todos los permisos de un rol
        """
        result = await self.db.execute(
            select(Permission)
            .join(RolePermission)
            .where(RolePermission.role_id == role_id)
        )
        return result.scalars().all()

    # ==================== ASIGNACIÓN DE ROLES A USUARIOS ====================

    async def assign_role_to_user(
        self,
        usuario_id: UUID,
        role_id: UUID,
        asignado_por_id: Optional[UUID] = None,
    ) -> UserRole:
        """
        Asigna un rol a un usuario
        """
        # Verificar si ya existe
        result = await self.db.execute(
            select(UserRole).where(
                and_(
                    UserRole.usuario_id == usuario_id,
                    UserRole.role_id == role_id,
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            return existing

        user_role = UserRole(
            usuario_id=usuario_id,
            role_id=role_id,
            asignado_por_id=asignado_por_id,
        )

        self.db.add(user_role)
        await self.db.commit()
        await self.db.refresh(user_role)

        return user_role

    async def remove_role_from_user(self, usuario_id: UUID, role_id: UUID) -> bool:
        """
        Remueve un rol de un usuario
        """
        result = await self.db.execute(
            select(UserRole).where(
                and_(
                    UserRole.usuario_id == usuario_id,
                    UserRole.role_id == role_id,
                )
            )
        )
        user_role = result.scalar_one_or_none()

        if user_role:
            await self.db.delete(user_role)
            await self.db.commit()
            return True

        return False

    async def get_user_roles(self, usuario_id: UUID) -> List[Role]:
        """
        Obtiene todos los roles de un usuario
        """
        result = await self.db.execute(
            select(Role).join(UserRole).where(UserRole.usuario_id == usuario_id)
        )
        return result.scalars().all()

    async def get_user_permissions(self, usuario_id: UUID) -> Set[str]:
        """
        Obtiene todos los códigos de permisos de un usuario (de todos sus roles)
        """
        result = await self.db.execute(
            select(Permission.codigo)
            .join(RolePermission)
            .join(Role)
            .join(UserRole)
            .where(UserRole.usuario_id == usuario_id)
        )

        permissions = set(result.scalars().all())
        return permissions

    async def user_has_permission(self, usuario_id: UUID, permission_code: str) -> bool:
        """
        Verifica si un usuario tiene un permiso específico
        """
        permissions = await self.get_user_permissions(usuario_id)
        return permission_code in permissions

    async def user_has_any_permission(
        self, usuario_id: UUID, permission_codes: List[str]
    ) -> bool:
        """
        Verifica si un usuario tiene al menos uno de los permisos especificados
        """
        permissions = await self.get_user_permissions(usuario_id)
        return any(code in permissions for code in permission_codes)

    async def user_has_all_permissions(
        self, usuario_id: UUID, permission_codes: List[str]
    ) -> bool:
        """
        Verifica si un usuario tiene todos los permisos especificados
        """
        permissions = await self.get_user_permissions(usuario_id)
        return all(code in permissions for code in permission_codes)

    # ==================== INICIALIZACIÓN DE PERMISOS ====================

    async def initialize_default_permissions(self):
        """
        Inicializa permisos por defecto del sistema
        """
        default_permissions = [
            # Pacientes
            ("Ver Pacientes", "pacientes.view", "pacientes", "paciente", "view"),
            ("Crear Pacientes", "pacientes.create", "pacientes", "paciente", "create"),
            ("Editar Pacientes", "pacientes.edit", "pacientes", "paciente", "edit"),
            (
                "Eliminar Pacientes",
                "pacientes.delete",
                "pacientes",
                "paciente",
                "delete",
            ),
            # Consultas
            ("Ver Consultas", "consultas.view", "consultas", "consulta", "view"),
            ("Crear Consultas", "consultas.create", "consultas", "consulta", "create"),
            ("Editar Consultas", "consultas.edit", "consultas", "consulta", "edit"),
            (
                "Eliminar Consultas",
                "consultas.delete",
                "consultas",
                "consulta",
                "delete",
            ),
            # Diagnósticos
            (
                "Ver Diagnósticos",
                "diagnosticos.view",
                "diagnosticos",
                "diagnostico",
                "view",
            ),
            (
                "Crear Diagnósticos",
                "diagnosticos.create",
                "diagnosticos",
                "diagnostico",
                "create",
            ),
            (
                "Editar Diagnósticos",
                "diagnosticos.edit",
                "diagnosticos",
                "diagnostico",
                "edit",
            ),
            (
                "Eliminar Diagnósticos",
                "diagnosticos.delete",
                "diagnosticos",
                "diagnostico",
                "delete",
            ),
            # Hospitalización
            (
                "Ver Hospitalizaciones",
                "hospitalizacion.view",
                "hospitalizacion",
                "hospitalizacion",
                "view",
            ),
            (
                "Crear Hospitalizaciones",
                "hospitalizacion.create",
                "hospitalizacion",
                "hospitalizacion",
                "create",
            ),
            (
                "Editar Hospitalizaciones",
                "hospitalizacion.edit",
                "hospitalizacion",
                "hospitalizacion",
                "edit",
            ),
            (
                "Dar Alta",
                "hospitalizacion.alta",
                "hospitalizacion",
                "hospitalizacion",
                "alta",
            ),
            # Analytics
            ("Ver Analytics", "analytics.view", "analytics", "reporte", "view"),
            ("Exportar Reportes", "analytics.export", "analytics", "reporte", "export"),
            # Administración
            ("Gestionar Usuarios", "admin.users", "admin", "usuario", "manage"),
            ("Gestionar Roles", "admin.roles", "admin", "rol", "manage"),
            ("Ver Auditoría", "admin.audit", "admin", "auditoria", "view"),
        ]

        for nombre, codigo, modulo, recurso, accion in default_permissions:
            existing = await self.get_permission_by_code(codigo)
            if not existing:
                await self.create_permission(nombre, codigo, modulo, recurso, accion)

    async def initialize_default_roles(self):
        """
        Inicializa roles por defecto del sistema
        """
        # Crear roles si no existen
        roles_data = [
            ("Administrador", "admin", "Acceso completo al sistema", 100),
            ("Médico", "medico", "Acceso a funciones médicas", 50),
            ("Enfermero", "enfermero", "Acceso a funciones de enfermería", 30),
            (
                "Recepcionista",
                "recepcionista",
                "Acceso a funciones administrativas",
                10,
            ),
        ]

        roles = {}
        for nombre, codigo, descripcion, nivel in roles_data:
            existing = await self.get_role_by_code(codigo)
            if not existing:
                role = await self.create_role(nombre, codigo, descripcion, nivel)
                roles[codigo] = role
            else:
                roles[codigo] = existing

        # Asignar permisos a roles usando método directo sin múltiples commits
        # Admin: todos los permisos
        all_permissions = await self.list_permissions()
        for perm in all_permissions:
            # Verificar si ya existe
            result = await self.db.execute(
                select(RolePermission).where(
                    and_(
                        RolePermission.role_id == roles["admin"].id,
                        RolePermission.permission_id == perm.id,
                    )
                )
            )
            if not result.scalar_one_or_none():
                role_perm = RolePermission(
                    role_id=roles["admin"].id,
                    permission_id=perm.id,
                )
                self.db.add(role_perm)

        await self.db.commit()

        # Médico: permisos médicos
        medico_perms = [
            "pacientes.view",
            "pacientes.create",
            "pacientes.edit",
            "consultas.view",
            "consultas.create",
            "consultas.edit",
            "diagnosticos.view",
            "diagnosticos.create",
            "diagnosticos.edit",
            "hospitalizacion.view",
            "hospitalizacion.create",
            "hospitalizacion.edit",
            "hospitalizacion.alta",
            "analytics.view",
        ]
        for code in medico_perms:
            perm = await self.get_permission_by_code(code)
            if perm:
                result = await self.db.execute(
                    select(RolePermission).where(
                        and_(
                            RolePermission.role_id == roles["medico"].id,
                            RolePermission.permission_id == perm.id,
                        )
                    )
                )
                if not result.scalar_one_or_none():
                    role_perm = RolePermission(
                        role_id=roles["medico"].id,
                        permission_id=perm.id,
                    )
                    self.db.add(role_perm)

        # Enfermero: permisos de enfermería
        enfermero_perms = ["pacientes.view", "consultas.view", "hospitalizacion.view"]
        for code in enfermero_perms:
            perm = await self.get_permission_by_code(code)
            if perm:
                result = await self.db.execute(
                    select(RolePermission).where(
                        and_(
                            RolePermission.role_id == roles["enfermero"].id,
                            RolePermission.permission_id == perm.id,
                        )
                    )
                )
                if not result.scalar_one_or_none():
                    role_perm = RolePermission(
                        role_id=roles["enfermero"].id,
                        permission_id=perm.id,
                    )
                    self.db.add(role_perm)

        # Recepcionista: permisos administrativos
        recepcionista_perms = ["pacientes.view", "pacientes.create", "consultas.view"]
        for code in recepcionista_perms:
            perm = await self.get_permission_by_code(code)
            if perm:
                result = await self.db.execute(
                    select(RolePermission).where(
                        and_(
                            RolePermission.role_id == roles["recepcionista"].id,
                            RolePermission.permission_id == perm.id,
                        )
                    )
                )
                if not result.scalar_one_or_none():
                    role_perm = RolePermission(
                        role_id=roles["recepcionista"].id,
                        permission_id=perm.id,
                    )
                    self.db.add(role_perm)

        await self.db.commit()
