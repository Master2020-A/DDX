"""
API endpoints para Seguridad Avanzada
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user, get_current_admin
from app.models.usuario import Usuario
from app.services.two_factor_service import TwoFactorService
from app.services.audit_service import AuditService
from app.services.session_service import SessionService
from app.services.permission_service import PermissionService
from app.services.encryption_service import EncryptionService
from app.schemas.security import (
    TwoFactorSetupResponse,
    TwoFactorVerifyRequest,
    TwoFactorStatusResponse,
    BackupCodesResponse,
    SessionInfo,
    SessionListResponse,
    SessionStatistics,
    PermissionCreate,
    PermissionResponse,
    RoleCreate,
    RoleResponse,
    RoleWithPermissions,
    AssignPermissionRequest,
    AssignRoleRequest,
    UserPermissionsResponse,
    AuditLogResponse,
    AuditLogListResponse,
    AuditStatistics,
    SecurityDashboard,
    PasswordChangeRequest,
)

router = APIRouter(prefix="/security", tags=["security"])


# ==================== 2FA ENDPOINTS ====================


@router.post("/2fa/setup", response_model=TwoFactorSetupResponse)
async def setup_2fa(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Inicia la configuración de 2FA para el usuario actual
    """
    try:
        service = TwoFactorService(db)
        secret, qr_code, provisioning_uri = await service.generate_secret(
            current_user.id
        )
        backup_codes = await service.get_backup_codes(current_user.id)

        return TwoFactorSetupResponse(
            secret=secret,
            qr_code=qr_code,
            provisioning_uri=provisioning_uri,
            backup_codes=backup_codes or [],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/2fa/verify")
async def verify_2fa(
    request: TwoFactorVerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Verifica el token 2FA y habilita 2FA si es correcto
    """
    service = TwoFactorService(db)
    verified = await service.verify_and_enable(current_user.id, request.token)

    if not verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido"
        )

    return {"message": "2FA habilitado exitosamente"}


@router.get("/2fa/status", response_model=TwoFactorStatusResponse)
async def get_2fa_status(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtiene el estado de 2FA del usuario actual
    """
    service = TwoFactorService(db)
    enabled = await service.is_enabled(current_user.id)

    # Obtener más detalles si está habilitado
    if enabled and current_user.two_factor_auth:
        return TwoFactorStatusResponse(
            enabled=True,
            verified=current_user.two_factor_auth.verified,
            method=current_user.two_factor_auth.method,
            last_used_at=current_user.two_factor_auth.last_used_at,
        )

    return TwoFactorStatusResponse(
        enabled=False,
        verified=False,
        method="totp",
        last_used_at=None,
    )


@router.post("/2fa/disable")
async def disable_2fa(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Deshabilita 2FA para el usuario actual
    """
    service = TwoFactorService(db)
    disabled = await service.disable(current_user.id)

    if not disabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="2FA no está configurado"
        )

    return {"message": "2FA deshabilitado exitosamente"}


@router.post("/2fa/backup-codes/regenerate", response_model=BackupCodesResponse)
async def regenerate_backup_codes(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Regenera los códigos de respaldo
    """
    try:
        service = TwoFactorService(db)
        backup_codes = await service.regenerate_backup_codes(current_user.id)

        return BackupCodesResponse(backup_codes=backup_codes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== SESIONES ENDPOINTS ====================


@router.get("/sessions", response_model=SessionListResponse)
async def get_user_sessions(
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtiene todas las sesiones del usuario actual
    """
    service = SessionService(db)
    sessions = await service.get_user_sessions(current_user.id, include_inactive)

    # Convertir a SessionInfo
    session_infos = []
    for session in sessions:
        session_infos.append(
            SessionInfo(
                id=session.id,
                ip_address=session.ip_address,
                user_agent=session.user_agent,
                device_info=session.device_info,
                location=session.location,
                activa=session.activa,
                created_at=session.created_at,
                last_activity_at=session.last_activity_at,
                expires_at=session.expires_at,
                is_current=False,  # TODO: detectar sesión actual
            )
        )

    active_count = sum(1 for s in sessions if s.activa and not s.revocada)

    return SessionListResponse(
        sessions=session_infos,
        total=len(sessions),
        active_count=active_count,
    )


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Revoca una sesión específica
    """
    service = SessionService(db)

    # Verificar que la sesión pertenece al usuario
    session = await service.get_session(str(session_id))
    if not session or session.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sesión no encontrada"
        )

    revoked = await service.revoke_session(session.session_token)

    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo revocar la sesión",
        )

    return {"message": "Sesión revocada exitosamente"}


@router.delete("/sessions/all")
async def revoke_all_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Revoca todas las sesiones del usuario excepto la actual
    """
    service = SessionService(db)
    count = await service.revoke_all_user_sessions(current_user.id)

    return {"message": f"{count} sesiones revocadas exitosamente"}


@router.get("/sessions/statistics", response_model=SessionStatistics)
async def get_session_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtiene estadísticas de sesiones del usuario
    """
    service = SessionService(db)
    stats = await service.get_session_statistics(current_user.id)

    return SessionStatistics(**stats)


# ==================== PERMISOS Y ROLES ENDPOINTS ====================


@router.post("/permissions", response_model=PermissionResponse)
async def create_permission(
    permission: PermissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Crea un nuevo permiso (solo admin)
    """
    # TODO: Verificar que el usuario tiene permiso admin.permissions
    service = PermissionService(db)

    try:
        perm = await service.create_permission(
            nombre=permission.nombre,
            codigo=permission.codigo,
            modulo=permission.modulo,
            recurso=permission.recurso,
            accion=permission.accion,
            descripcion=permission.descripcion,
        )

        return PermissionResponse(
            id=perm.id,
            nombre=perm.nombre,
            codigo=perm.codigo,
            descripcion=perm.descripcion,
            modulo=perm.modulo,
            recurso=perm.recurso,
            accion=perm.accion,
            activo=perm.activo,
            created_at=perm.created_at,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/permissions", response_model=List[PermissionResponse])
async def list_permissions(
    modulo: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Lista todos los permisos
    """
    service = PermissionService(db)
    permissions = await service.list_permissions(modulo=modulo)

    return [
        PermissionResponse(
            id=p.id,
            nombre=p.nombre,
            codigo=p.codigo,
            descripcion=p.descripcion,
            modulo=p.modulo,
            recurso=p.recurso,
            accion=p.accion,
            activo=p.activo,
            created_at=p.created_at,
        )
        for p in permissions
    ]


@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Crea un nuevo rol (solo admin)
    """
    service = PermissionService(db)

    try:
        r = await service.create_role(
            nombre=role.nombre,
            codigo=role.codigo,
            descripcion=role.descripcion,
            nivel=role.nivel,
            rol_padre_id=role.rol_padre_id,
        )

        return RoleResponse(
            id=r.id,
            nombre=r.nombre,
            codigo=r.codigo,
            descripcion=r.descripcion,
            nivel=r.nivel,
            activo=r.activo,
            es_sistema=r.es_sistema,
            created_at=r.created_at,
            permisos_count=0,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Lista todos los roles
    """
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.models.security import Role

    # Usar eager loading para cargar permisos
    result = await db.execute(
        select(Role)
        .options(selectinload(Role.permisos))
        .order_by(Role.created_at.desc())
    )
    roles = result.scalars().all()

    return [
        RoleResponse(
            id=r.id,
            nombre=r.nombre,
            codigo=r.codigo,
            descripcion=r.descripcion,
            nivel=r.nivel,
            activo=r.activo,
            es_sistema=r.es_sistema,
            created_at=r.created_at,
            permisos_count=len(r.permisos) if r.permisos else 0,
        )
        for r in roles
    ]


@router.get("/roles/{role_id}", response_model=RoleWithPermissions)
async def get_role(
    role_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtiene un rol con sus permisos
    """
    service = PermissionService(db)
    role = await service.get_role(role_id)

    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    permissions = await service.get_role_permissions(role_id)

    return RoleWithPermissions(
        id=role.id,
        nombre=role.nombre,
        codigo=role.codigo,
        descripcion=role.descripcion,
        nivel=role.nivel,
        activo=role.activo,
        es_sistema=role.es_sistema,
        created_at=role.created_at,
        permisos_count=len(permissions),
        permisos=[
            PermissionResponse(
                id=p.id,
                nombre=p.nombre,
                codigo=p.codigo,
                descripcion=p.descripcion,
                modulo=p.modulo,
                recurso=p.recurso,
                accion=p.accion,
                activo=p.activo,
                created_at=p.created_at,
            )
            for p in permissions
        ],
    )


@router.post("/roles/{role_id}/permissions")
async def assign_permission_to_role(
    role_id: UUID,
    request: AssignPermissionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Asigna un permiso a un rol
    """
    service = PermissionService(db)

    try:
        await service.assign_permission_to_role(
            role_id=role_id,
            permission_id=request.permission_id,
            concedido_por_id=current_user.id,
        )

        return {"message": "Permiso asignado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/users/{usuario_id}/roles")
async def assign_role_to_user(
    usuario_id: UUID,
    request: AssignRoleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Asigna un rol a un usuario
    """
    service = PermissionService(db)

    try:
        await service.assign_role_to_user(
            usuario_id=usuario_id,
            role_id=request.role_id,
            asignado_por_id=current_user.id,
        )

        return {"message": "Rol asignado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/users/{usuario_id}/permissions", response_model=UserPermissionsResponse)
async def get_user_permissions(
    usuario_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtiene todos los permisos de un usuario
    """
    service = PermissionService(db)

    roles = await service.get_user_roles(usuario_id)
    permissions = await service.get_user_permissions(usuario_id)

    return UserPermissionsResponse(
        usuario_id=usuario_id,
        roles=[
            RoleResponse(
                id=r.id,
                nombre=r.nombre,
                codigo=r.codigo,
                descripcion=r.descripcion,
                nivel=r.nivel,
                activo=r.activo,
                es_sistema=r.es_sistema,
                created_at=r.created_at,
                permisos_count=0,
            )
            for r in roles
        ],
        permissions=list(permissions),
    )


# ==================== AUDITORÍA ENDPOINTS ====================


@router.get("/audit/logs", response_model=AuditLogListResponse)
async def get_audit_logs(
    usuario_id: Optional[UUID] = None,
    accion: Optional[str] = None,
    recurso: Optional[str] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    exitoso: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Obtiene logs de auditoría con filtros
    """
    service = AuditService(db)

    logs = await service.get_logs(
        usuario_id=usuario_id,
        accion=accion,
        recurso=recurso,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        exitoso=exitoso,
        limit=limit,
        offset=offset,
    )

    return AuditLogListResponse(
        logs=[
            AuditLogResponse(
                id=log.id,
                usuario_id=log.usuario_id,
                accion=log.accion,
                recurso=log.recurso,
                recurso_id=log.recurso_id,
                descripcion=log.descripcion,
                ip_address=log.ip_address,
                metodo_http=log.metodo_http,
                endpoint=log.endpoint,
                exitoso=log.exitoso,
                codigo_estado=log.codigo_estado,
                mensaje_error=log.mensaje_error,
                created_at=log.created_at,
            )
            for log in logs
        ],
        total=len(logs),
    )


@router.get("/audit/statistics", response_model=AuditStatistics)
async def get_audit_statistics(
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtiene estadísticas de auditoría
    """
    service = AuditService(db)
    stats = await service.get_statistics(fecha_inicio, fecha_fin)

    return AuditStatistics(**stats)


@router.get("/audit/user/{usuario_id}", response_model=AuditLogListResponse)
async def get_user_activity(
    usuario_id: UUID,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtiene la actividad de un usuario específico
    """
    service = AuditService(db)

    logs = await service.get_user_activity(
        usuario_id=usuario_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        limit=limit,
    )

    return AuditLogListResponse(
        logs=[
            AuditLogResponse(
                id=log.id,
                usuario_id=log.usuario_id,
                accion=log.accion,
                recurso=log.recurso,
                recurso_id=log.recurso_id,
                descripcion=log.descripcion,
                ip_address=log.ip_address,
                metodo_http=log.metodo_http,
                endpoint=log.endpoint,
                exitoso=log.exitoso,
                codigo_estado=log.codigo_estado,
                mensaje_error=log.mensaje_error,
                created_at=log.created_at,
            )
            for log in logs
        ],
        total=len(logs),
    )


# ==================== DASHBOARD DE SEGURIDAD ====================


@router.get("/dashboard", response_model=SecurityDashboard)
async def get_security_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtiene el dashboard de seguridad del usuario actual
    """
    # 2FA
    two_factor_service = TwoFactorService(db)
    two_factor_enabled = await two_factor_service.is_enabled(current_user.id)

    # Sesiones
    session_service = SessionService(db)
    session_stats = await session_service.get_session_statistics(current_user.id)

    # Permisos
    permission_service = PermissionService(db)
    roles = await permission_service.get_user_roles(current_user.id)
    permissions = await permission_service.get_user_permissions(current_user.id)

    return SecurityDashboard(
        two_factor_enabled=two_factor_enabled,
        active_sessions=session_stats["active_sessions"],
        total_sessions=session_stats["total_sessions"],
        roles=[r.nombre for r in roles],
        permissions_count=len(permissions),
        last_login=None,  # TODO: implementar
        failed_login_attempts=0,
        account_locked=False,
    )


@router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Lista todos los usuarios del sistema
    """
    from sqlalchemy import select

    result = await db.execute(select(Usuario).order_by(Usuario.created_at.desc()))
    usuarios = result.scalars().all()

    return [
        {
            "id": str(u.id),
            "email": u.email,
            "nombre_completo": u.nombre_completo,
            "rol": u.rol,
            "activo": u.activo,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in usuarios
    ]


@router.post("/users")
async def create_user(
    user_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Crea un nuevo usuario (solo admin)
    """
    from app.core.security import get_password_hash
    from sqlalchemy import select

    # Verificar si el email ya existe
    result = await db.execute(
        select(Usuario).where(Usuario.email == user_data.get("email"))
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado",
        )

    # Crear nuevo usuario
    new_user = Usuario(
        email=user_data.get("email"),
        password_hash=get_password_hash(user_data.get("password")),
        nombre_completo=user_data.get("nombre_completo"),
        rol=user_data.get("rol", "medico"),
        especialidad=user_data.get("especialidad"),
        cedula_profesional=user_data.get("cedula_profesional"),
        activo=True,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {
        "id": str(new_user.id),
        "email": new_user.email,
        "nombre_completo": new_user.nombre_completo,
        "rol": new_user.rol,
        "activo": new_user.activo,
        "created_at": new_user.created_at.isoformat() if new_user.created_at else None,
    }


@router.get("/admin/dashboard")
async def get_admin_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Obtiene estadísticas globales del sistema de seguridad (solo admin)
    """
    from sqlalchemy import select, func
    from app.models.security import TwoFactorAuth, UserSession, AuditLog, UserRole

    # Total de usuarios
    result = await db.execute(select(func.count(Usuario.id)))
    total_usuarios = result.scalar() or 0

    # Usuarios con 2FA
    result = await db.execute(
        select(func.count(TwoFactorAuth.usuario_id.distinct())).where(
            TwoFactorAuth.enabled == True
        )
    )
    usuarios_con_2fa = result.scalar() or 0

    # Sesiones activas
    result = await db.execute(
        select(func.count(UserSession.id))
        .where(UserSession.activa == True)
        .where(UserSession.revocada == False)
    )
    sesiones_activas = result.scalar() or 0

    # Acciones último día
    from datetime import datetime, timedelta

    hace_24h = datetime.utcnow() - timedelta(days=1)

    result = await db.execute(
        select(func.count(AuditLog.id)).where(AuditLog.created_at >= hace_24h)
    )
    acciones_ultimo_dia = result.scalar() or 0

    # Acciones fallidas último día
    result = await db.execute(
        select(func.count(AuditLog.id))
        .where(AuditLog.created_at >= hace_24h)
        .where(AuditLog.exitoso == False)
    )
    acciones_fallidas_ultimo_dia = result.scalar() or 0

    # Distribución de roles
    from app.models.security import Role

    result = await db.execute(
        select(Role.nombre, func.count(UserRole.usuario_id))
        .join(UserRole, Role.id == UserRole.role_id)
        .group_by(Role.nombre)
    )
    roles_dict = {row[0]: row[1] for row in result.all()}

    return {
        "total_usuarios": total_usuarios,
        "usuarios_con_2fa": usuarios_con_2fa,
        "sesiones_activas": sesiones_activas,
        "acciones_ultimo_dia": acciones_ultimo_dia,
        "acciones_fallidas_ultimo_dia": acciones_fallidas_ultimo_dia,
        "roles": roles_dict,
    }


# ==================== INICIALIZACIÓN ====================


@router.post("/initialize")
async def initialize_security_system(
    db: AsyncSession = Depends(get_db),
):
    """
    Inicializa el sistema de seguridad con permisos y roles por defecto

    NOTA: Este endpoint no requiere autenticación para permitir la configuración inicial.
    En producción, considere deshabilitarlo después de la primera ejecución.
    """
    service = PermissionService(db)

    # Verificar si ya está inicializado
    existing_permissions = await service.list_permissions()
    if len(existing_permissions) > 0:
        raise HTTPException(
            status_code=400,
            detail="El sistema ya ha sido inicializado. Los permisos y roles ya existen.",
        )

    await service.initialize_default_permissions()
    await service.initialize_default_roles()

    return {
        "message": "Sistema de seguridad inicializado exitosamente",
        "permisos_creados": len(await service.list_permissions()),
        "roles_creados": 4,
    }
