from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.models.tratamiento import Tratamiento, Prescripcion
from app.models.usuario import Usuario
from app.schemas.tratamiento import TratamientoCreate, TratamientoResponse, PrescripcionCreate
from app.api.dependencies import get_current_active_medico

router = APIRouter()


@router.post("/", response_model=TratamientoResponse, status_code=status.HTTP_201_CREATED)
async def crear_tratamiento(
    tratamiento_data: TratamientoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Crear un nuevo tratamiento (farmacológico, físico, paliativo, etc.).
    """
    nuevo_tratamiento = Tratamiento(
        **tratamiento_data.model_dump(),
        prescrito_por=current_user.id
    )
    
    db.add(nuevo_tratamiento)
    await db.commit()
    await db.refresh(nuevo_tratamiento)
    
    return nuevo_tratamiento


@router.get("/consulta/{consulta_id}", response_model=List[TratamientoResponse])
async def listar_tratamientos_consulta(
    consulta_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Listar todos los tratamientos de una consulta.
    """
    result = await db.execute(
        select(Tratamiento)
        .where(Tratamiento.consulta_id == consulta_id)
        .order_by(Tratamiento.created_at.desc())
    )
    tratamientos = result.scalars().all()
    return tratamientos


@router.get("/{tratamiento_id}", response_model=TratamientoResponse)
async def obtener_tratamiento(
    tratamiento_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Obtener detalles de un tratamiento específico.
    """
    result = await db.execute(
        select(Tratamiento).where(Tratamiento.id == tratamiento_id)
    )
    tratamiento = result.scalar_one_or_none()
    
    if not tratamiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tratamiento no encontrado"
        )
    
    return tratamiento


@router.post("/prescripciones", status_code=status.HTTP_201_CREATED)
async def crear_prescripcion(
    prescripcion_data: PrescripcionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Crear una prescripción farmacológica dentro de un tratamiento.
    """
    # Verify that the treatment exists
    result = await db.execute(
        select(Tratamiento).where(Tratamiento.id == prescripcion_data.tratamiento_id)
    )
    tratamiento = result.scalar_one_or_none()
    
    if not tratamiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tratamiento no encontrado"
        )
    
    nueva_prescripcion = Prescripcion(**prescripcion_data.model_dump())
    
    db.add(nueva_prescripcion)
    await db.commit()
    await db.refresh(nueva_prescripcion)
    
    return nueva_prescripcion


@router.patch("/{tratamiento_id}/estado/{nuevo_estado}", response_model=TratamientoResponse)
async def actualizar_estado_tratamiento(
    tratamiento_id: UUID,
    nuevo_estado: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Actualizar el estado de un tratamiento.
    """
    result = await db.execute(
        select(Tratamiento).where(Tratamiento.id == tratamiento_id)
    )
    tratamiento = result.scalar_one_or_none()
    
    if not tratamiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tratamiento no encontrado"
        )
    
    # Validate state
    from app.models.tratamiento import EstadoTratamientoEnum
    try:
        estado_enum = EstadoTratamientoEnum(nuevo_estado)
        tratamiento.estado = estado_enum
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido. Debe ser: activo, completado, suspendido o modificado"
        )
    
    await db.commit()
    await db.refresh(tratamiento)
    
    return tratamiento
