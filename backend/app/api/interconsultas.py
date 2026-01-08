"""
API endpoints para Interconsultas
Incluye: Solicitudes, Notificaciones, Chat, Seguimiento
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.dependencies import get_current_user, get_current_active_medico
from app.models.usuario import Usuario
from app.models.interconsulta import (
    Interconsulta, NotificacionInterconsulta, 
    MensajeInterconsulta, SeguimientoInterconsulta
)
from app.models.paciente import Paciente
from app.schemas.interconsulta import (
    InterconsultaCreate, InterconsultaUpdate, InterconsultaResponse,
    NotificacionInterconsultaCreate, NotificacionInterconsultaResponse,
    MensajeInterconsultaCreate, MensajeInterconsultaResponse,
    SeguimientoInterconsultaCreate, SeguimientoInterconsultaResponse,
    AceptarInterconsultaRequest, RechazarInterconsultaRequest,
    ResponderInterconsultaRequest, EstadisticasInterconsultasResponse
)

router = APIRouter(tags=["Interconsultas"])


# ==================== INTERCONSULTAS ====================

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=InterconsultaResponse)
async def crear_interconsulta(
    data: InterconsultaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """Crear una nueva solicitud de interconsulta"""
    
    # Verificar que el paciente existe
    result = await db.execute(select(Paciente).where(Paciente.id == data.paciente_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    # Crear interconsulta
    interconsulta = Interconsulta(
        **data.model_dump(),
        medico_solicitante_id=current_user.id,
        estado='solicitada'
    )
    
    db.add(interconsulta)
    await db.flush()
    
    # Crear notificación para el especialista (si está asignado)
    if data.especialista_id:
        notificacion = NotificacionInterconsulta(
            interconsulta_id=interconsulta.id,
            medico_destinatario_id=data.especialista_id,
            tipo='nueva_solicitud',
            titulo=f'Nueva interconsulta de {data.especialidad_requerida}',
            mensaje=f'Solicitud de interconsulta con urgencia {data.urgencia}: {data.motivo_solicitud[:100]}...'
        )
        db.add(notificacion)
    
    await db.commit()
    await db.refresh(interconsulta)
    
    return interconsulta


@router.get("/", response_model=List[InterconsultaResponse])
async def listar_interconsultas(
    skip: int = 0,
    limit: int = 100,
    estado: Optional[str] = None,
    especialidad: Optional[str] = None,
    urgencia: Optional[str] = None,
    paciente_id: Optional[UUID] = None,
    mis_solicitudes: bool = False,
    mis_interconsultas: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar interconsultas con filtros"""
    
    query = select(Interconsulta)
    
    # Filtros
    if estado:
        query = query.where(Interconsulta.estado == estado)
    if especialidad:
        query = query.where(Interconsulta.especialidad_requerida == especialidad)
    if urgencia:
        query = query.where(Interconsulta.urgencia == urgencia)
    if paciente_id:
        query = query.where(Interconsulta.paciente_id == paciente_id)
    if mis_solicitudes:
        query = query.where(Interconsulta.medico_solicitante_id == current_user.id)
    if mis_interconsultas:
        query = query.where(Interconsulta.especialista_id == current_user.id)
    
    query = query.order_by(desc(Interconsulta.fecha_solicitud))
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{interconsulta_id}", response_model=InterconsultaResponse)
async def obtener_interconsulta(
    interconsulta_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener detalles de una interconsulta"""
    
    result = await db.execute(
        select(Interconsulta).where(Interconsulta.id == interconsulta_id)
    )
    interconsulta = result.scalar_one_or_none()
    
    if not interconsulta:
        raise HTTPException(status_code=404, detail="Interconsulta no encontrada")
    
    return interconsulta


@router.put("/{interconsulta_id}", response_model=InterconsultaResponse)
async def actualizar_interconsulta(
    interconsulta_id: UUID,
    data: InterconsultaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """Actualizar una interconsulta"""
    
    result = await db.execute(
        select(Interconsulta).where(Interconsulta.id == interconsulta_id)
    )
    interconsulta = result.scalar_one_or_none()
    
    if not interconsulta:
        raise HTTPException(status_code=404, detail="Interconsulta no encontrada")
    
    # Actualizar campos
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(interconsulta, field, value)
    
    await db.commit()
    await db.refresh(interconsulta)
    
    return interconsulta


@router.post("/{interconsulta_id}/aceptar", response_model=InterconsultaResponse)
async def aceptar_interconsulta(
    interconsulta_id: UUID,
    data: AceptarInterconsultaRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """Aceptar una interconsulta como especialista"""
    
    result = await db.execute(
        select(Interconsulta).where(Interconsulta.id == interconsulta_id)
    )
    interconsulta = result.scalar_one_or_none()
    
    if not interconsulta:
        raise HTTPException(status_code=404, detail="Interconsulta no encontrada")
    
    if interconsulta.estado != 'solicitada':
        raise HTTPException(status_code=400, detail="La interconsulta ya fue procesada")
    
    # Actualizar interconsulta
    interconsulta.especialista_id = current_user.id
    interconsulta.estado = 'aceptada'
    interconsulta.fecha_aceptacion = datetime.now()
    if data.fecha_programada:
        interconsulta.fecha_programada = data.fecha_programada
    if data.notas:
        interconsulta.notas_internas = data.notas
    
    # Notificar al médico solicitante
    notificacion = NotificacionInterconsulta(
        interconsulta_id=interconsulta.id,
        medico_destinatario_id=interconsulta.medico_solicitante_id,
        tipo='aceptada',
        titulo='Interconsulta aceptada',
        mensaje=f'Su solicitud de interconsulta ha sido aceptada por el especialista.'
    )
    db.add(notificacion)
    
    await db.commit()
    await db.refresh(interconsulta)
    
    return interconsulta


@router.post("/{interconsulta_id}/rechazar", response_model=InterconsultaResponse)
async def rechazar_interconsulta(
    interconsulta_id: UUID,
    data: RechazarInterconsultaRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """Rechazar una interconsulta"""
    
    result = await db.execute(
        select(Interconsulta).where(Interconsulta.id == interconsulta_id)
    )
    interconsulta = result.scalar_one_or_none()
    
    if not interconsulta:
        raise HTTPException(status_code=404, detail="Interconsulta no encontrada")
    
    interconsulta.estado = 'rechazada'
    interconsulta.motivo_rechazo = data.motivo_rechazo
    interconsulta.especialista_id = current_user.id
    
    # Notificar al médico solicitante
    notificacion = NotificacionInterconsulta(
        interconsulta_id=interconsulta.id,
        medico_destinatario_id=interconsulta.medico_solicitante_id,
        tipo='rechazada',
        titulo='Interconsulta rechazada',
        mensaje=f'Motivo: {data.motivo_rechazo}'
    )
    db.add(notificacion)
    
    await db.commit()
    await db.refresh(interconsulta)
    
    return interconsulta


@router.post("/{interconsulta_id}/responder", response_model=InterconsultaResponse)
async def responder_interconsulta(
    interconsulta_id: UUID,
    data: ResponderInterconsultaRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """Responder una interconsulta con diagnóstico y recomendaciones"""
    
    result = await db.execute(
        select(Interconsulta).where(Interconsulta.id == interconsulta_id)
    )
    interconsulta = result.scalar_one_or_none()
    
    if not interconsulta:
        raise HTTPException(status_code=404, detail="Interconsulta no encontrada")
    
    if interconsulta.especialista_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado para responder esta interconsulta")
    
    # Actualizar respuesta
    interconsulta.diagnostico_especialista = data.diagnostico_especialista
    interconsulta.hallazgos = data.hallazgos
    interconsulta.recomendaciones = data.recomendaciones
    interconsulta.plan_tratamiento = data.plan_tratamiento
    interconsulta.requiere_seguimiento = data.requiere_seguimiento
    interconsulta.fecha_seguimiento = data.fecha_seguimiento
    interconsulta.estado = 'completada'
    interconsulta.fecha_completada = datetime.now()
    interconsulta.fecha_realizada = datetime.now()
    
    # Notificar al médico solicitante
    notificacion = NotificacionInterconsulta(
        interconsulta_id=interconsulta.id,
        medico_destinatario_id=interconsulta.medico_solicitante_id,
        tipo='respuesta_disponible',
        titulo='Respuesta de interconsulta disponible',
        mensaje=f'El especialista ha completado la interconsulta.'
    )
    db.add(notificacion)
    
    await db.commit()
    await db.refresh(interconsulta)
    
    return interconsulta


# ==================== NOTIFICACIONES ====================

@router.get("/notificaciones/mis-notificaciones", response_model=List[NotificacionInterconsultaResponse])
async def obtener_mis_notificaciones(
    skip: int = 0,
    limit: int = 50,
    solo_no_leidas: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener notificaciones del usuario actual"""
    
    query = select(NotificacionInterconsulta).where(
        NotificacionInterconsulta.medico_destinatario_id == current_user.id
    )
    
    if solo_no_leidas:
        query = query.where(NotificacionInterconsulta.leida == False)
    
    query = query.order_by(desc(NotificacionInterconsulta.created_at))
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.put("/notificaciones/{notificacion_id}/marcar-leida")
async def marcar_notificacion_leida(
    notificacion_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Marcar una notificación como leída"""
    
    result = await db.execute(
        select(NotificacionInterconsulta).where(
            NotificacionInterconsulta.id == notificacion_id,
            NotificacionInterconsulta.medico_destinatario_id == current_user.id
        )
    )
    notificacion = result.scalar_one_or_none()
    
    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    
    notificacion.leida = True
    notificacion.fecha_lectura = datetime.now()
    
    await db.commit()
    
    return {"message": "Notificación marcada como leída"}


# ==================== CHAT/MENSAJES ====================

@router.post("/mensajes", status_code=status.HTTP_201_CREATED, response_model=MensajeInterconsultaResponse)
async def enviar_mensaje(
    data: MensajeInterconsultaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """Enviar un mensaje en el chat de una interconsulta"""
    
    # Verificar que la interconsulta existe
    result = await db.execute(
        select(Interconsulta).where(Interconsulta.id == data.interconsulta_id)
    )
    interconsulta = result.scalar_one_or_none()
    
    if not interconsulta:
        raise HTTPException(status_code=404, detail="Interconsulta no encontrada")
    
    # Crear mensaje
    mensaje = MensajeInterconsulta(
        **data.model_dump(),
        medico_emisor_id=current_user.id
    )
    
    db.add(mensaje)
    
    # Notificar al otro médico
    destinatario_id = (
        interconsulta.especialista_id 
        if current_user.id == interconsulta.medico_solicitante_id 
        else interconsulta.medico_solicitante_id
    )
    
    if destinatario_id:
        notificacion = NotificacionInterconsulta(
            interconsulta_id=interconsulta.id,
            medico_destinatario_id=destinatario_id,
            tipo='mensaje_nuevo',
            titulo='Nuevo mensaje en interconsulta',
            mensaje=data.mensaje[:100] + ('...' if len(data.mensaje) > 100 else '')
        )
        db.add(notificacion)
    
    await db.commit()
    await db.refresh(mensaje)
    
    return mensaje


@router.get("/mensajes/{interconsulta_id}", response_model=List[MensajeInterconsultaResponse])
async def obtener_mensajes(
    interconsulta_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener mensajes de una interconsulta"""
    
    query = select(MensajeInterconsulta).where(
        MensajeInterconsulta.interconsulta_id == interconsulta_id
    ).order_by(MensajeInterconsulta.created_at)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


# ==================== SEGUIMIENTO ====================

@router.post("/seguimientos", status_code=status.HTTP_201_CREATED, response_model=SeguimientoInterconsultaResponse)
async def crear_seguimiento(
    data: SeguimientoInterconsultaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """Crear un seguimiento interdisciplinario"""
    
    seguimiento = SeguimientoInterconsulta(
        **data.model_dump(),
        medico_id=current_user.id
    )
    
    db.add(seguimiento)
    await db.commit()
    await db.refresh(seguimiento)
    
    return seguimiento


@router.get("/seguimientos/{interconsulta_id}", response_model=List[SeguimientoInterconsultaResponse])
async def obtener_seguimientos(
    interconsulta_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener seguimientos de una interconsulta"""
    
    query = select(SeguimientoInterconsulta).where(
        SeguimientoInterconsulta.interconsulta_id == interconsulta_id
    ).order_by(desc(SeguimientoInterconsulta.created_at))
    
    result = await db.execute(query)
    return result.scalars().all()


# ==================== ESTADÍSTICAS ====================

@router.get("/estadisticas/general", response_model=EstadisticasInterconsultasResponse)
async def obtener_estadisticas(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener estadísticas generales de interconsultas"""
    
    # Total solicitadas
    result_total = await db.execute(select(func.count(Interconsulta.id)))
    total_solicitadas = result_total.scalar()
    
    # Por estado
    result_pendientes = await db.execute(
        select(func.count(Interconsulta.id)).where(Interconsulta.estado == 'solicitada')
    )
    pendientes = result_pendientes.scalar()
    
    result_aceptadas = await db.execute(
        select(func.count(Interconsulta.id)).where(Interconsulta.estado == 'aceptada')
    )
    aceptadas = result_aceptadas.scalar()
    
    result_completadas = await db.execute(
        select(func.count(Interconsulta.id)).where(Interconsulta.estado == 'completada')
    )
    completadas = result_completadas.scalar()
    
    result_rechazadas = await db.execute(
        select(func.count(Interconsulta.id)).where(Interconsulta.estado == 'rechazada')
    )
    rechazadas = result_rechazadas.scalar()
    
    # Por especialidad
    result_especialidad = await db.execute(
        select(
            Interconsulta.especialidad_requerida,
            func.count(Interconsulta.id)
        ).group_by(Interconsulta.especialidad_requerida)
    )
    por_especialidad = {esp: count for esp, count in result_especialidad.all()}
    
    # Por urgencia
    result_urgencia = await db.execute(
        select(
            Interconsulta.urgencia,
            func.count(Interconsulta.id)
        ).group_by(Interconsulta.urgencia)
    )
    por_urgencia = {urg: count for urg, count in result_urgencia.all()}
    
    return {
        "total_solicitadas": total_solicitadas,
        "pendientes": pendientes,
        "aceptadas": aceptadas,
        "completadas": completadas,
        "rechazadas": rechazadas,
        "por_especialidad": por_especialidad,
        "por_urgencia": por_urgencia,
        "tiempo_promedio_respuesta": None  # Calcular si es necesario
    }
