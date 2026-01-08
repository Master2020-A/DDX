# app/api/v1/endpoints/telemedicina.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.usuario import Usuario
from app.models.telemedicina import ConsultaRemota
from app.schemas.telemedicina import (
    ConsultaRemotaCreate,
    ConsultaRemotaResponse,
    ConsultaRemotaList,
)

router = APIRouter()


# ═══════════════════════════════════════════════════════════════
# IMPORTANTE: Rutas específicas PRIMERO, rutas con {param} DESPUÉS
# ═══════════════════════════════════════════════════════════════


@router.get("/consultas/programadas", response_model=List[ConsultaRemotaResponse])
async def listar_consultas_programadas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    fecha_inicio: Optional[date] = Query(None, description="Fecha inicio del rango"),
    fecha_fin: Optional[date] = Query(None, description="Fecha fin del rango"),
    medico_id: Optional[UUID] = Query(None, description="Filtrar por médico"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """
    Listar consultas remotas programadas.
    - Médicos ven sus propias consultas
    - Admins ven todas las consultas
    """
    query = db.query(ConsultaRemota).filter(ConsultaRemota.estado == "programada")

    # Filtrar por médico si no es admin
    if current_user.rol != "admin":
        query = query.filter(ConsultaRemota.medico_id == current_user.id)
    elif medico_id:
        query = query.filter(ConsultaRemota.medico_id == medico_id)

    # Filtrar por rango de fechas
    if fecha_inicio:
        query = query.filter(ConsultaRemota.fecha_programada >= fecha_inicio)
    if fecha_fin:
        query = query.filter(ConsultaRemota.fecha_programada <= fecha_fin)

    # Ordenar por fecha programada
    query = query.order_by(ConsultaRemota.fecha_programada.asc())

    consultas = query.offset(skip).limit(limit).all()

    return consultas


@router.get("/consultas/hoy", response_model=List[ConsultaRemotaResponse])
async def listar_consultas_hoy(
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
):
    """Listar consultas programadas para hoy"""
    hoy = date.today()

    query = db.query(ConsultaRemota).filter(
        and_(
            ConsultaRemota.fecha_programada
            >= datetime.combine(hoy, datetime.min.time()),
            ConsultaRemota.fecha_programada
            <= datetime.combine(hoy, datetime.max.time()),
            ConsultaRemota.estado.in_(["programada", "en_curso"]),
        )
    )

    if current_user.rol != "admin":
        query = query.filter(ConsultaRemota.medico_id == current_user.id)

    return query.order_by(ConsultaRemota.fecha_programada.asc()).all()


@router.get("/consultas/activas", response_model=List[ConsultaRemotaResponse])
async def listar_consultas_activas(
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
):
    """Listar consultas actualmente en curso"""
    query = db.query(ConsultaRemota).filter(ConsultaRemota.estado == "en_curso")

    if current_user.rol != "admin":
        query = query.filter(ConsultaRemota.medico_id == current_user.id)

    return query.all()


# ═══════════════════════════════════════════════════════════════
# Rutas con parámetros dinámicos van DESPUÉS
# ═══════════════════════════════════════════════════════════════


@router.get("/consultas", response_model=List[ConsultaRemotaResponse])
async def listar_consultas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """Listar todas las consultas con filtros opcionales"""
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
)
async def crear_consulta(
    consulta_data: ConsultaRemotaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crear nueva consulta remota"""
    # Tu código existente para crear consulta...
    pass


@router.get("/consultas/{consulta_id}", response_model=ConsultaRemotaResponse)
async def obtener_consulta(
    consulta_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener una consulta específica por ID"""
    consulta = db.query(ConsultaRemota).filter(ConsultaRemota.id == consulta_id).first()

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


@router.post("/consultas/{consulta_id}/iniciar")
async def iniciar_consulta(
    consulta_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Iniciar una consulta programada"""
    # Tu código existente...
    pass


@router.post("/consultas/{consulta_id}/finalizar")
async def finalizar_consulta(
    consulta_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Finalizar una consulta en curso"""
    # Tu código existente...
    pass
