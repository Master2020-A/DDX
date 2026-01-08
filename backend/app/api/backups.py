"""
API endpoints para el módulo de Backups y Recuperación
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.api.dependencies import get_current_user, get_current_admin
from app.models.usuario import Usuario
from app.services.backup_service import BackupService
from app.schemas.backups import (
    BackupCreate,
    BackupResponse,
    ProgramacionBackupCreate,
    ProgramacionBackupUpdate,
    ProgramacionBackupResponse,
    RestauracionCreate,
    RestauracionResponse,
    ReplicacionBDCreate,
    ReplicacionBDResponse,
    MonitoreoSaludResponse,
    AlertaBackupResponse,
    AlertaResolverRequest,
    PlanRecuperacionCreate,
    PlanRecuperacionResponse,
    EstadisticasBackupsResponse,
    EstadoSistemaResponse,
)
from app.models.backups import TipoBackup, EstadoBackup

router = APIRouter(prefix="/backups", tags=["Backups y Recuperación"])


# ==================== BACKUPS ====================


@router.post("/", response_model=BackupResponse, status_code=status.HTTP_201_CREATED)
async def crear_backup(
    backup_data: BackupCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Crear un nuevo backup manual

    **Requiere:** Rol de administrador
    """
    service = BackupService(db)

    # Crear registro de backup
    backup = await service.crear_backup(
        tipo=backup_data.tipo,
        nombre=backup_data.nombre,
        descripcion=backup_data.descripcion,
        automatico=False,
        usuario_id=str(current_user.id),
    )

    # Ejecutar backup en background
    background_tasks.add_task(service.ejecutar_backup, str(backup.id))

    return backup


@router.get("/", response_model=List[BackupResponse])
async def listar_backups(
    tipo: Optional[TipoBackup] = None,
    estado: Optional[EstadoBackup] = None,
    limite: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Listar backups

    **Requiere:** Rol de administrador
    """
    service = BackupService(db)
    backups = await service.listar_backups(tipo=tipo, estado=estado, limite=limite)
    return backups


@router.get("/{backup_id}", response_model=BackupResponse)
async def obtener_backup(
    backup_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Obtener detalles de un backup específico

    **Requiere:** Rol de administrador
    """
    from sqlalchemy import select
    from app.models.backups import Backup

    result = await db.execute(select(Backup).where(Backup.id == backup_id))
    backup = result.scalar_one_or_none()

    if not backup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Backup no encontrado"
        )

    return backup


@router.delete("/{backup_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_backup(
    backup_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Eliminar un backup

    **Requiere:** Rol de administrador
    """
    service = BackupService(db)

    eliminado = await service.eliminar_backup(backup_id)

    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Backup no encontrado"
        )


@router.post("/limpiar-antiguos")
async def limpiar_backups_antiguos(
    dias_retencion: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Limpiar backups antiguos según política de retención

    **Requiere:** Rol de administrador
    """
    service = BackupService(db)
    eliminados = await service.limpiar_backups_antiguos(dias_retencion)

    return {
        "mensaje": f"Se eliminaron {eliminados} backups antiguos",
        "eliminados": eliminados,
    }


# ==================== PROGRAMACIÓN DE BACKUPS ====================


@router.post(
    "/programacion",
    response_model=ProgramacionBackupResponse,
    status_code=status.HTTP_201_CREATED,
)
async def crear_programacion_backup(
    programacion_data: ProgramacionBackupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Crear programación de backup automático

    **Requiere:** Rol de administrador
    """
    service = BackupService(db)

    programacion = await service.crear_programacion(
        nombre=programacion_data.nombre,
        tipo_backup=programacion_data.tipo_backup,
        cron_expresion=programacion_data.cron_expresion,
        retencion_dias=programacion_data.retencion_dias,
        descripcion=programacion_data.descripcion,
        created_by=str(current_user.id),
    )

    return programacion


@router.get("/programacion", response_model=List[ProgramacionBackupResponse])
async def listar_programaciones(
    activo: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Listar programaciones de backups

    **Requiere:** Rol de administrador
    """
    service = BackupService(db)
    programaciones = await service.listar_programaciones(activo=activo)
    return programaciones


@router.patch(
    "/programacion/{programacion_id}", response_model=ProgramacionBackupResponse
)
async def actualizar_programacion(
    programacion_id: str,
    programacion_data: ProgramacionBackupUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Actualizar programación de backup

    **Requiere:** Rol de administrador
    """
    service = BackupService(db)

    try:
        programacion = await service.actualizar_programacion(
            programacion_id=programacion_id,
            activo=programacion_data.activo,
            cron_expresion=programacion_data.cron_expresion,
            retencion_dias=programacion_data.retencion_dias,
        )
        return programacion
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ==================== RESTAURACIÓN ====================


@router.post(
    "/restauracion",
    response_model=RestauracionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def crear_restauracion(
    restauracion_data: RestauracionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Crear solicitud de restauración

    **Requiere:** Rol de administrador
    **Nota:** La restauración requiere aprobación adicional antes de ejecutarse
    """
    service = BackupService(db)

    try:
        restauracion = await service.crear_restauracion(
            backup_id=str(restauracion_data.backup_id),
            tipo=restauracion_data.tipo,
            nombre=restauracion_data.nombre,
            motivo=restauracion_data.motivo,
            usuario_id=str(current_user.id),
            descripcion=restauracion_data.descripcion,
            punto_tiempo=restauracion_data.punto_tiempo,
            tablas_restaurar=restauracion_data.tablas_restaurar,
        )
        return restauracion
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/restauracion/{restauracion_id}/ejecutar", response_model=RestauracionResponse
)
async def ejecutar_restauracion(
    restauracion_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Ejecutar una restauración (requiere aprobación)

    **Requiere:** Rol de administrador
    **ADVERTENCIA:** Esta operación puede sobrescribir datos existentes
    """
    service = BackupService(db)

    try:
        # Ejecutar en background
        background_tasks.add_task(
            service.ejecutar_restauracion, restauracion_id, str(current_user.id)
        )

        # Obtener restauración actualizada
        from sqlalchemy import select
        from app.models.backups import Restauracion

        result = await db.execute(
            select(Restauracion).where(Restauracion.id == restauracion_id)
        )
        restauracion = result.scalar_one_or_none()

        return restauracion
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/restauracion", response_model=List[RestauracionResponse])
async def listar_restauraciones(
    limite: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Listar restauraciones

    **Requiere:** Rol de administrador
    """
    service = BackupService(db)
    restauraciones = await service.listar_restauraciones(limite=limite)
    return restauraciones


# ==================== MONITOREO ====================


@router.post("/monitoreo/salud", response_model=MonitoreoSaludResponse)
async def registrar_salud_sistema(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Registrar métricas de salud del sistema

    **Requiere:** Rol de administrador
    """
    service = BackupService(db)
    monitoreo = await service.registrar_salud_sistema()
    return monitoreo


@router.get("/monitoreo/salud/reciente", response_model=List[MonitoreoSaludResponse])
async def obtener_salud_reciente(
    horas: int = 24,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Obtener métricas de salud recientes

    **Requiere:** Rol de administrador
    """
    from datetime import datetime, timedelta
    from sqlalchemy import select
    from app.models.backups import MonitoreoSalud

    fecha_limite = datetime.utcnow() - timedelta(hours=horas)

    result = await db.execute(
        select(MonitoreoSalud)
        .where(MonitoreoSalud.timestamp >= fecha_limite)
        .order_by(MonitoreoSalud.timestamp.desc())
    )

    return result.scalars().all()


# ==================== ALERTAS ====================


@router.get("/alertas", response_model=List[AlertaBackupResponse])
async def listar_alertas(
    activas_solo: bool = True,
    limite: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Listar alertas del sistema de backups

    **Requiere:** Rol de administrador
    """
    service = BackupService(db)
    alertas = await service.listar_alertas(activas_solo=activas_solo, limite=limite)
    return alertas


@router.post("/alertas/{alerta_id}/resolver", response_model=AlertaBackupResponse)
async def resolver_alerta(
    alerta_id: str,
    resolver_data: AlertaResolverRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Resolver una alerta

    **Requiere:** Rol de administrador
    """
    service = BackupService(db)

    try:
        alerta = await service.resolver_alerta(
            alerta_id=alerta_id,
            resuelto_por=str(current_user.id),
            notas=resolver_data.notas,
        )
        return alerta
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ==================== ESTADÍSTICAS ====================


@router.get("/estadisticas", response_model=EstadisticasBackupsResponse)
async def obtener_estadisticas(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Obtener estadísticas de backups

    **Requiere:** Rol de administrador
    """
    service = BackupService(db)
    estadisticas = await service.obtener_estadisticas_backups()
    return estadisticas


@router.get("/estado-sistema", response_model=EstadoSistemaResponse)
async def obtener_estado_sistema(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Obtener estado general del sistema

    **Requiere:** Rol de administrador
    """
    from sqlalchemy import select, func
    from app.models.backups import Backup, AlertaBackup, MonitoreoSalud
    from datetime import datetime, timedelta

    # Último backup exitoso
    result = await db.execute(
        select(Backup)
        .where(Backup.estado == EstadoBackup.COMPLETADO)
        .order_by(Backup.fecha_fin.desc())
        .limit(1)
    )
    ultimo_backup = result.scalar_one_or_none()

    # Alertas activas
    result = await db.execute(
        select(func.count(AlertaBackup.id)).where(AlertaBackup.activa == True)
    )
    alertas_activas = result.scalar() or 0

    # Última métrica de salud
    result = await db.execute(
        select(MonitoreoSalud).order_by(MonitoreoSalud.timestamp.desc()).limit(1)
    )
    ultima_salud = result.scalar_one_or_none()

    # Calcular uptime (simulado)
    uptime_dias = 30  # En producción, calcular desde inicio del sistema

    # Determinar estado
    if alertas_activas > 5:
        estado = "critical"
        disponibilidad = 95.0
    elif alertas_activas > 0:
        estado = "degraded"
        disponibilidad = 98.0
    else:
        estado = "healthy"
        disponibilidad = 99.9

    return {
        "estado": estado,
        "disponibilidad_porcentaje": disponibilidad,
        "uptime_dias": uptime_dias,
        "ultimo_backup_exitoso": ultimo_backup.fecha_fin if ultimo_backup else None,
        "alertas_activas": alertas_activas,
        "replicacion_activa": False,  # Implementar cuando se configure replicación
        "espacio_disco_libre_gb": (
            ultima_salud.espacio_disco_libre_gb if ultima_salud else 0
        ),
    }


# ==================== PLANES DE RECUPERACIÓN ====================


@router.post(
    "/planes-recuperacion",
    response_model=PlanRecuperacionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def crear_plan_recuperacion(
    plan_data: PlanRecuperacionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Crear plan de recuperación ante desastres

    **Requiere:** Rol de administrador
    """
    from app.models.backups import PlanRecuperacion
    from datetime import datetime, timedelta

    plan = PlanRecuperacion(
        nombre=plan_data.nombre,
        descripcion=plan_data.descripcion,
        rto_minutos=plan_data.rto_minutos,
        rpo_minutos=plan_data.rpo_minutos,
        procedimientos=plan_data.procedimientos,
        contactos_emergencia=plan_data.contactos_emergencia,
        recursos_requeridos=plan_data.recursos_requeridos,
        frecuencia_prueba_dias=plan_data.frecuencia_prueba_dias,
        proxima_prueba=datetime.utcnow()
        + timedelta(days=plan_data.frecuencia_prueba_dias),
        created_by=current_user.id,
    )

    db.add(plan)
    await db.commit()
    await db.refresh(plan)

    return plan


@router.get("/planes-recuperacion", response_model=List[PlanRecuperacionResponse])
async def listar_planes_recuperacion(
    activo: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Listar planes de recuperación

    **Requiere:** Rol de administrador
    """
    from sqlalchemy import select
    from app.models.backups import PlanRecuperacion

    query = select(PlanRecuperacion).order_by(PlanRecuperacion.created_at.desc())

    if activo is not None:
        query = query.where(PlanRecuperacion.activo == activo)

    result = await db.execute(query)
    return result.scalars().all()
