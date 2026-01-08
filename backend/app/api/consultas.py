from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.models.consulta import Consulta
from app.models.usuario import Usuario
from app.schemas.consulta import ConsultaCreate, ConsultaResponse, ConsultaUpdate
from app.api.dependencies import get_current_active_medico

router = APIRouter()


@router.get("/", response_model=List[ConsultaResponse])
async def listar_consultas(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Listar todas las consultas del sistema.
    """
    result = await db.execute(
        select(Consulta)
        .offset(skip)
        .limit(limit)
        .order_by(Consulta.fecha_hora.desc())
    )
    consultas = result.scalars().all()
    return consultas


@router.post("/", response_model=ConsultaResponse, status_code=status.HTTP_201_CREATED)
async def crear_consulta(
    consulta_data: ConsultaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Crear una nueva consulta médica.
    """
    nueva_consulta = Consulta(
        **consulta_data.model_dump(),
        medico_id=current_user.id
    )
    
    db.add(nueva_consulta)
    await db.commit()
    await db.refresh(nueva_consulta)
    
    return nueva_consulta


@router.get("/paciente/{paciente_id}", response_model=List[ConsultaResponse])
async def listar_consultas_paciente(
    paciente_id: UUID,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Listar todas las consultas de un paciente.
    """
    result = await db.execute(
        select(Consulta)
        .where(Consulta.paciente_id == paciente_id)
        .offset(skip)
        .limit(limit)
        .order_by(Consulta.fecha_hora.desc())
    )
    consultas = result.scalars().all()
    return consultas


@router.get("/{consulta_id}", response_model=ConsultaResponse)
async def obtener_consulta(
    consulta_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Obtener detalles de una consulta específica.
    """
    result = await db.execute(
        select(Consulta).where(Consulta.id == consulta_id)
    )
    consulta = result.scalar_one_or_none()
    
    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta no encontrada"
        )
    
    return consulta


@router.put("/{consulta_id}", response_model=ConsultaResponse)
async def actualizar_consulta(
    consulta_id: UUID,
    consulta_data: ConsultaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Actualizar información de una consulta.
    """
    result = await db.execute(
        select(Consulta).where(Consulta.id == consulta_id)
    )
    consulta = result.scalar_one_or_none()
    
    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta no encontrada"
        )
    
    # Update only provided fields
    update_data = consulta_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(consulta, field, value)
    
    await db.commit()
    await db.refresh(consulta)
    
    return consulta
