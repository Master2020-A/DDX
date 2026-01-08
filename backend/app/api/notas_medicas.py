from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.nota_medica import NotaMedica
from app.models.usuario import Usuario
from app.schemas.nota_medica import (
    NotaMedicaCreate,
    NotaMedicaResponse,
    NotaMedicaUpdate
)
from app.api.dependencies import get_current_active_medico

router = APIRouter()


@router.post("/", response_model=NotaMedicaResponse, status_code=status.HTTP_201_CREATED)
async def crear_nota_medica(
    nota_data: NotaMedicaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Crear una nueva nota médica.
    """
    nueva_nota = NotaMedica(
        **nota_data.model_dump(),
        autor_id=current_user.id
    )
    
    db.add(nueva_nota)
    await db.commit()
    await db.refresh(nueva_nota)
    
    return nueva_nota


@router.get("/paciente/{paciente_id}", response_model=List[NotaMedicaResponse])
async def listar_notas_paciente(
    paciente_id: UUID,
    tipo_nota: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Listar todas las notas médicas de un paciente.
    Opcionalmente filtrar por tipo de nota.
    """
    query = select(NotaMedica).where(NotaMedica.paciente_id == paciente_id)
    
    if tipo_nota:
        query = query.where(NotaMedica.tipo_nota == tipo_nota)
    
    query = query.order_by(NotaMedica.fecha_nota.desc())
    
    result = await db.execute(query)
    notas = result.scalars().all()
    return notas


@router.get("/{nota_id}", response_model=NotaMedicaResponse)
async def obtener_nota_medica(
    nota_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Obtener una nota médica específica por su ID.
    """
    result = await db.execute(
        select(NotaMedica)
        .where(NotaMedica.id == nota_id)
    )
    nota = result.scalar_one_or_none()
    
    if not nota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota médica no encontrada"
        )
    
    return nota


@router.put("/{nota_id}", response_model=NotaMedicaResponse)
async def actualizar_nota_medica(
    nota_id: UUID,
    nota_data: NotaMedicaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Actualizar una nota médica existente.
    Solo el autor puede actualizar la nota.
    """
    result = await db.execute(
        select(NotaMedica)
        .where(NotaMedica.id == nota_id)
    )
    nota = result.scalar_one_or_none()
    
    if not nota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota médica no encontrada"
        )
    
    # Verificar que el usuario actual sea el autor
    if nota.autor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para actualizar esta nota"
        )
    
    # Actualizar campos
    update_data = nota_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(nota, field, value)
    
    await db.commit()
    await db.refresh(nota)
    
    return nota


@router.delete("/{nota_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_nota_medica(
    nota_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Eliminar una nota médica.
    Solo el autor puede eliminar la nota.
    """
    result = await db.execute(
        select(NotaMedica)
        .where(NotaMedica.id == nota_id)
    )
    nota = result.scalar_one_or_none()
    
    if not nota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota médica no encontrada"
        )
    
    # Verificar que el usuario actual sea el autor
    if nota.autor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para eliminar esta nota"
        )
    
    await db.delete(nota)
    await db.commit()
    
    return None


@router.post("/{nota_id}/firmar", response_model=NotaMedicaResponse)
async def firmar_nota_medica(
    nota_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Firmar una nota médica.
    Una vez firmada, no se puede editar.
    """
    result = await db.execute(
        select(NotaMedica)
        .where(NotaMedica.id == nota_id)
    )
    nota = result.scalar_one_or_none()
    
    if not nota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota médica no encontrada"
        )
    
    # Verificar que el usuario actual sea el autor
    if nota.autor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para firmar esta nota"
        )
    
    if nota.firmada:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La nota ya está firmada"
        )
    
    nota.firmada = True
    
    await db.commit()
    await db.refresh(nota)
    
    return nota
