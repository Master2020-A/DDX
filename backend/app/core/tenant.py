"""
Middleware y utilidades para Multi-Tenancy
Aislamiento de datos por institución
"""

from typing import Optional
from uuid import UUID
from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from contextvars import ContextVar

from app.core.database import get_db
from app.models.institucion import Institucion
from app.models.usuario import Usuario

# Context variable para almacenar el tenant_id actual
current_tenant_id: ContextVar[Optional[UUID]] = ContextVar(
    "current_tenant_id", default=None
)


class TenantContext:
    """Contexto del tenant actual"""

    @staticmethod
    def set_tenant_id(tenant_id: UUID):
        """Establece el tenant_id en el contexto actual"""
        current_tenant_id.set(tenant_id)

    @staticmethod
    def get_tenant_id() -> Optional[UUID]:
        """Obtiene el tenant_id del contexto actual"""
        return current_tenant_id.get()

    @staticmethod
    def clear():
        """Limpia el contexto del tenant"""
        current_tenant_id.set(None)


async def get_current_tenant_id(request: Request) -> UUID:
    """
    Obtiene el tenant_id del usuario autenticado
    Se usa como dependencia en los endpoints
    """
    # Obtener usuario del request (asumiendo que ya está autenticado)
    user = getattr(request.state, "user", None)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no autenticado"
        )

    if not hasattr(user, "institucion_id") or not user.institucion_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario no tiene institución asignada",
        )

    # Establecer en el contexto
    TenantContext.set_tenant_id(user.institucion_id)

    return user.institucion_id


async def get_current_institucion(
    tenant_id: UUID = Depends(get_current_tenant_id), db: AsyncSession = Depends(get_db)
) -> Institucion:
    """
    Obtiene la institución actual del usuario autenticado
    Valida que esté activa
    """
    result = await db.execute(select(Institucion).where(Institucion.id == tenant_id))
    institucion = result.scalar_one_or_none()

    if not institucion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Institución no encontrada"
        )

    if not institucion.activa:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Institución suspendida o inactiva",
        )

    return institucion


def verificar_limite_usuarios(institucion: Institucion):
    """Verifica si la institución ha alcanzado el límite de usuarios"""
    if institucion.usuarios_activos >= institucion.max_usuarios:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Límite de usuarios alcanzado ({institucion.max_usuarios}). Actualice su plan.",
        )


def verificar_limite_pacientes(institucion: Institucion):
    """Verifica si la institución ha alcanzado el límite de pacientes"""
    if institucion.pacientes_registrados >= institucion.max_pacientes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Límite de pacientes alcanzado ({institucion.max_pacientes}). Actualice su plan.",
        )


def verificar_limite_almacenamiento(
    institucion: Institucion, tamano_adicional_gb: float = 0
):
    """Verifica si la institución ha alcanzado el límite de almacenamiento"""
    uso_total = float(institucion.almacenamiento_usado_gb) + tamano_adicional_gb

    if uso_total >= institucion.max_almacenamiento_gb:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Límite de almacenamiento alcanzado ({institucion.max_almacenamiento_gb}GB). Actualice su plan.",
        )


def verificar_modulo_activo(institucion: Institucion, modulo: str):
    """Verifica si un módulo está activo para la institución"""
    config = institucion.configuracion or {}
    modulos_activos = config.get("modulos_activos", [])

    if modulo not in modulos_activos:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"El módulo '{modulo}' no está activo para su institución",
        )


class TenantFilter:
    """
    Clase helper para agregar filtros de tenant_id a las queries
    """

    @staticmethod
    def apply(query, model, tenant_id: UUID = None):
        """
        Aplica el filtro de tenant_id a una query

        Args:
            query: Query de SQLAlchemy
            model: Modelo que tiene el campo institucion_id
            tenant_id: ID del tenant (si no se provee, usa el del contexto)

        Returns:
            Query con el filtro aplicado
        """
        if tenant_id is None:
            tenant_id = TenantContext.get_tenant_id()

        if tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No se pudo determinar la institución",
            )

        # Verificar que el modelo tenga el campo institucion_id
        if not hasattr(model, "institucion_id"):
            raise ValueError(
                f"El modelo {model.__name__} no tiene campo institucion_id"
            )

        return query.where(model.institucion_id == tenant_id)


async def require_super_admin(request: Request):
    """
    Dependencia que requiere que el usuario sea super admin
    Para acceso al dashboard multi-tenant
    """
    user = getattr(request.state, "user", None)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no autenticado"
        )

    # Verificar si es super admin (sin institución asignada o con rol especial)
    if hasattr(user, "is_super_admin") and not user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requieren permisos de super administrador.",
        )

    return user


# Decorador para endpoints que requieren tenant
def require_tenant(func):
    """
    Decorador para endpoints que requieren tenant_id
    Automáticamente filtra los datos por institución
    """

    async def wrapper(*args, **kwargs):
        tenant_id = TenantContext.get_tenant_id()
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No se pudo determinar la institución",
            )
        return await func(*args, **kwargs)

    return wrapper
