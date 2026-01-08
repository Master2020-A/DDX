from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.expediente import ExpedienteClinico
from app.models.usuario import Usuario
from app.schemas.expediente import (
    ExpedienteClinicoCreate,
    ExpedienteClinicoResponse,
    ExpedienteClinicoUpdate
)
from app.api.dependencies import get_current_active_medico

router = APIRouter()


@router.post("/", response_model=ExpedienteClinicoResponse, status_code=status.HTTP_201_CREATED)
async def crear_expediente(
    expediente_data: ExpedienteClinicoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Crear un nuevo expediente clínico para un paciente.
    """
    nuevo_expediente = ExpedienteClinico(**expediente_data.model_dump())
    
    db.add(nuevo_expediente)
    await db.commit()
    await db.refresh(nuevo_expediente)
    
    return nuevo_expediente


@router.get("/paciente/{paciente_id}", response_model=List[ExpedienteClinicoResponse])
async def listar_expedientes_paciente(
    paciente_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Listar todos los expedientes clínicos de un paciente.
    """
    result = await db.execute(
        select(ExpedienteClinico)
        .where(ExpedienteClinico.paciente_id == paciente_id)
        .order_by(ExpedienteClinico.created_at.desc())
    )
    expedientes = result.scalars().all()
    return expedientes


@router.get("/{expediente_id}", response_model=ExpedienteClinicoResponse)
async def obtener_expediente(
    expediente_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Obtener un expediente clínico específico por su ID.
    """
    result = await db.execute(
        select(ExpedienteClinico)
        .where(ExpedienteClinico.id == expediente_id)
    )
    expediente = result.scalar_one_or_none()
    
    if not expediente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expediente clínico no encontrado"
        )
    
    return expediente


@router.put("/{expediente_id}", response_model=ExpedienteClinicoResponse)
async def actualizar_expediente(
    expediente_id: UUID,
    expediente_data: ExpedienteClinicoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Actualizar un expediente clínico existente.
    """
    result = await db.execute(
        select(ExpedienteClinico)
        .where(ExpedienteClinico.id == expediente_id)
    )
    expediente = result.scalar_one_or_none()
    
    if not expediente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expediente clínico no encontrado"
        )
    
    # Actualizar campos
    update_data = expediente_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(expediente, field, value)
    
    await db.commit()
    await db.refresh(expediente)
    
    return expediente


@router.delete("/{expediente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_expediente(
    expediente_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Eliminar un expediente clínico.
    """
    result = await db.execute(
        select(ExpedienteClinico)
        .where(ExpedienteClinico.id == expediente_id)
    )
    expediente = result.scalar_one_or_none()
    
    if not expediente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expediente clínico no encontrado"
        )
    
    await db.delete(expediente)
    await db.commit()
    
    return None
