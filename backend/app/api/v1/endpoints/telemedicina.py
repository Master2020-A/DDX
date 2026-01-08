# app/api/v1/endpoints/telemedicina.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.usuario import Usuario
from app.models.telemedicina import EstadoConsulta, EmisorTipo
from app.services.telemedicina_service import TelemedicinaService
from app.schemas.telemedicina import (
    ConsultaRemotaCreate,
    ConsultaRemotaResponse,
    ConsultaRemotaUpdate,
    IniciarConsultaResponse,
    FinalizarConsultaRequest,
    FinalizarConsultaResponse,
    MensajeChatCreate,
    MensajeChatResponse,
    PrescripcionCreate,
    PrescripcionResponse,
    SeguimientoCreate,
    SeguimientoResponse,
    EstadisticasTelemedicina,
)

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> TelemedicinaService:
    return TelemedicinaService(db)


# ════════════════════════════════════════════════════════════════════════════════
# IMPORTANTE: Las rutas ESPECÍFICAS deben ir ANTES de las rutas con {parámetros}
# ════════════════════════════════════════════════════════════════════════════════


# ============================================================
# CONSULTAS - RUTAS ESPECÍFICAS (van primero)
# ============================================================


@router.get(
    "/consultas/programadas",
    response_model=List[ConsultaRemotaResponse],
    summary="Listar consultas programadas",
)
async def listar_consultas_programadas(
    fecha_inicio: Optional[date] = Query(None, description="Fecha inicio del rango"),
    fecha_fin: Optional[date] = Query(None, description="Fecha fin del rango"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: TelemedicinaService = Depends(get_service),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Listar consultas remotas programadas.
    - Médicos ven sus propias consultas
    - Admins ven todas las consultas
    """
    medico_id = None if current_user.rol == "admin" else current_user.id

    # Convertir dates a datetime si se proporcionan
    fecha_inicio_dt = (
        datetime.combine(fecha_inicio, datetime.min.time()) if fecha_inicio else None
    )
    fecha_fin_dt = (
        datetime.combine(fecha_fin, datetime.max.time()) if fecha_fin else None
    )

    consultas = service.listar_consultas_programadas(
        medico_id=medico_id,
        fecha_inicio=fecha_inicio_dt,
        fecha_fin=fecha_fin_dt,
        skip=skip,
        limit=limit,
    )

    return consultas


@router.get(
    "/consultas/hoy",
    response_model=List[ConsultaRemotaResponse],
    summary="Consultas de hoy",
)
async def listar_consultas_hoy(
    service: TelemedicinaService = Depends(get_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Listar consultas programadas para hoy del médico actual"""
    return service.listar_consultas_hoy(current_user.id)


@router.get(
    "/estadisticas",
    response_model=EstadisticasTelemedicina,
    summary="Estadísticas de telemedicina",
)
async def obtener_estadisticas(
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    service: TelemedicinaService = Depends(get_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener estadísticas de telemedicina"""
    medico_id = None if current_user.rol == "admin" else current_user.id

    fecha_inicio_dt = (
        datetime.combine(fecha_inicio, datetime.min.time()) if fecha_inicio else None
    )
    fecha_fin_dt = (
        datetime.combine(fecha_fin, datetime.max.time()) if fecha_fin else None
    )

    return service.obtener_estadisticas(
        medico_id=medico_id, fecha_inicio=fecha_inicio_dt, fecha_fin=fecha_fin_dt
    )


# ============================================================
# CONSULTAS - RUTAS GENERALES
# ============================================================


@router.get(
    "/consultas",
    response_model=List[ConsultaRemotaResponse],
    summary="Listar todas las consultas",
)
async def listar_consultas(
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Listar todas las consultas con filtros opcionales"""
    from app.models.telemedicina import ConsultaRemota

    query = db.query(ConsultaRemota)

    if current_user.rol != "admin":
        query = query.filter(ConsultaRemota.medico_id == current_user.id)

    if estado:
        query = query.filter(ConsultaRemota.estado == estado)

    return (
        query.order_by(ConsultaRemota.created_at.desc()).offset(skip).limit(limit).all()
    )


@router.post(
    "/consultas",
    response_model=ConsultaRemotaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear consulta remota",
)
async def crear_consulta(
    data: ConsultaRemotaCreate,
    service: TelemedicinaService = Depends(get_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Crear una nueva consulta remota"""
    consulta = service.crear_consulta(data, current_user.id)
    return consulta


# ============================================================
# CONSULTAS - RUTAS CON PARÁMETROS (van al final)
# ============================================================


@router.get(
    "/consultas/{consulta_id}",
    response_model=ConsultaRemotaResponse,
    summary="Obtener consulta por ID",
)
async def obtener_consulta(
    consulta_id: UUID,
    service: TelemedicinaService = Depends(get_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener una consulta específica por ID"""
    consulta = service.obtener_consulta(consulta_id)

    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Consulta no encontrada"
        )

    # Verificar acceso
    if current_user.rol != "admin" and consulta.medico_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene acceso a esta consulta",
        )

    return consulta


@router.post(
    "/consultas/{consulta_id}/iniciar",
    response_model=IniciarConsultaResponse,
    summary="Iniciar consulta",
)
async def iniciar_consulta(
    consulta_id: UUID,
    service: TelemedicinaService = Depends(get_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Iniciar una consulta programada"""
    try:
        consulta = service.iniciar_consulta(consulta_id, current_user.id)
        return IniciarConsultaResponse(
            id=consulta.id,
            estado=consulta.estado,
            fecha_inicio=consulta.fecha_inicio,
            sala_id=consulta.sala_id,
            url_sala_medico=consulta.url_sala_medico,
            url_sala_paciente=consulta.url_sala_paciente,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post(
    "/consultas/{consulta_id}/finalizar",
    response_model=FinalizarConsultaResponse,
    summary="Finalizar consulta",
)
async def finalizar_consulta(
    consulta_id: UUID,
    data: FinalizarConsultaRequest,
    service: TelemedicinaService = Depends(get_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Finalizar una consulta en curso"""
    try:
        consulta = service.finalizar_consulta(consulta_id, current_user.id, data)
        return FinalizarConsultaResponse(
            id=consulta.id,
            estado=consulta.estado,
            fecha_fin=consulta.fecha_fin,
            duracion_minutos=consulta.duracion_minutos or 0,
            notas_medico=consulta.notas_medico,
            diagnostico_preliminar=consulta.diagnostico_preliminar,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post(
    "/consultas/{consulta_id}/cancelar",
    response_model=ConsultaRemotaResponse,
    summary="Cancelar consulta",
)
async def cancelar_consulta(
    consulta_id: UUID,
    motivo: Optional[str] = None,
    service: TelemedicinaService = Depends(get_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Cancelar una consulta programada"""
    try:
        return service.cancelar_consulta(consulta_id, current_user.id, motivo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# CHAT
# ============================================================


@router.post(
    "/chat/mensaje",
    response_model=MensajeChatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar mensaje",
)
async def enviar_mensaje(
    data: MensajeChatCreate,
    service: TelemedicinaService = Depends(get_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Enviar un mensaje en el chat de la consulta"""
    # Verificar que la consulta existe y está en curso
    consulta = service.obtener_consulta(data.consulta_remota_id)

    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")

    # Determinar tipo de emisor
    emisor_tipo = (
        EmisorTipo.MEDICO
        if current_user.rol in ["admin", "medico"]
        else EmisorTipo.PACIENTE
    )

    mensaje = service.enviar_mensaje(data, current_user.id, emisor_tipo)
    return mensaje


@router.get(
    "/chat/{consulta_id}/mensajes",
    response_model=List[MensajeChatResponse],
    summary="Obtener mensajes",
)
async def obtener_mensajes(
    consulta_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: TelemedicinaService = Depends(get_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener mensajes del chat de una consulta"""
    # Verificar acceso
    consulta = service.obtener_consulta(consulta_id)
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")

    if current_user.rol != "admin" and consulta.medico_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene acceso a esta consulta")

    # Marcar como leídos
    service.marcar_mensajes_leidos(consulta_id, current_user.id)

    return service.obtener_mensajes(consulta_id, skip, limit)


# ============================================================
# PRESCRIPCIONES
# ============================================================


@router.post(
    "/prescripciones",
    response_model=PrescripcionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear prescripción",
)
async def crear_prescripcion(
    data: PrescripcionCreate,
    service: TelemedicinaService = Depends(get_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Crear una prescripción electrónica"""
    if current_user.rol not in ["admin", "medico"]:
        raise HTTPException(
            status_code=403, detail="Solo médicos pueden emitir prescripciones"
        )

    prescripcion = service.crear_prescripcion(data, current_user.id)
    return prescripcion


@router.get(
    "/prescripciones/{prescripcion_id}",
    response_model=PrescripcionResponse,
    summary="Obtener prescripción",
)
async def obtener_prescripcion(
    prescripcion_id: UUID,
    service: TelemedicinaService = Depends(get_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener una prescripción por ID"""
    prescripcion = service.obtener_prescripcion(prescripcion_id)

    if not prescripcion:
        raise HTTPException(status_code=404, detail="Prescripción no encontrada")

    return prescripcion


@router.get(
    "/prescripciones/paciente/{paciente_id}",
    response_model=List[PrescripcionResponse],
    summary="Prescripciones de paciente",
)
async def listar_prescripciones_paciente(
    paciente_id: UUID,
    solo_activas: bool = Query(True),
    service: TelemedicinaService = Depends(get_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Listar prescripciones de un paciente"""
    return service.listar_prescripciones_paciente(paciente_id, solo_activas)


# ============================================================
# SEGUIMIENTOS
# ============================================================


@router.post(
    "/seguimientos",
    response_model=SeguimientoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear seguimiento",
)
async def crear_seguimiento(
    data: SeguimientoCreate,
    service: TelemedicinaService = Depends(get_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Crear un seguimiento post-consulta"""
    seguimiento = service.crear_seguimiento(data, current_user.id)
    return seguimiento


@router.get(
    "/seguimientos/pendientes",
    response_model=List[SeguimientoResponse],
    summary="Seguimientos pendientes",
)
async def listar_seguimientos_pendientes(
    service: TelemedicinaService = Depends(get_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Listar seguimientos pendientes de enviar"""
    medico_id = None if current_user.rol == "admin" else current_user.id
    return service.obtener_seguimientos_pendientes(medico_id)
