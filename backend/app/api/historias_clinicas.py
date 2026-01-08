from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.historia_clinica import HistoriaClinicaPediatrica, ExploracionFisica, AntecedentesNoPatologicos
from app.models.paciente import Paciente
from app.schemas.historia_clinica import (
    HistoriaClinicaCreate,
    HistoriaClinicaUpdate,
    HistoriaClinicaResponse,
    HistoriaClinicaCompletaResponse,
    ExploracionFisicaCreate,
    ExploracionFisicaUpdate,
    ExploracionFisicaResponse,
    AntecedentesNoPatologicosCreate,
    AntecedentesNoPatologicosUpdate,
    AntecedentesNoPatologicosResponse,
)

router = APIRouter()


# ============================================================================
# HISTORIA CLÍNICA PEDIÁTRICA
# ============================================================================

@router.post("/", response_model=HistoriaClinicaResponse, status_code=status.HTTP_201_CREATED)
async def crear_historia_clinica(
    historia_data: HistoriaClinicaCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Crear una nueva historia clínica pediátrica para un paciente
    """
    # Verificar que el paciente existe
    result = await db.execute(select(Paciente).where(Paciente.id == historia_data.paciente_id))
    paciente = result.scalar_one_or_none()
    
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )
    
    # Crear historia clínica
    historia = HistoriaClinicaPediatrica(**historia_data.model_dump())
    db.add(historia)
    await db.commit()
    await db.refresh(historia)
    
    return historia


@router.get("/{historia_id}", response_model=HistoriaClinicaCompletaResponse)
async def obtener_historia_clinica(
    historia_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener una historia clínica completa con todas sus secciones
    """
    result = await db.execute(
        select(HistoriaClinicaPediatrica)
        .options(
            selectinload(HistoriaClinicaPediatrica.exploracion_fisica),
            selectinload(HistoriaClinicaPediatrica.antecedentes_no_patologicos)
        )
        .where(HistoriaClinicaPediatrica.id == historia_id)
    )
    historia = result.scalar_one_or_none()
    
    if not historia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Historia clínica no encontrada"
        )
    
    return historia


@router.get("/paciente/{paciente_id}", response_model=List[HistoriaClinicaCompletaResponse])
async def listar_historias_por_paciente(
    paciente_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Listar todas las historias clínicas de un paciente específico
    """
    result = await db.execute(
        select(HistoriaClinicaPediatrica)
        .options(
            selectinload(HistoriaClinicaPediatrica.exploracion_fisica),
            selectinload(HistoriaClinicaPediatrica.antecedentes_no_patologicos)
        )
        .where(HistoriaClinicaPediatrica.paciente_id == paciente_id)
        .order_by(HistoriaClinicaPediatrica.fecha.desc())
    )
    historias = result.scalars().all()
    
    return historias


@router.put("/{historia_id}", response_model=HistoriaClinicaResponse)
async def actualizar_historia_clinica(
    historia_id: UUID,
    historia_data: HistoriaClinicaUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar los datos de una historia clínica
    """
    result = await db.execute(
        select(HistoriaClinicaPediatrica).where(HistoriaClinicaPediatrica.id == historia_id)
    )
    historia = result.scalar_one_or_none()
    
    if not historia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Historia clínica no encontrada"
        )
    
    # Actualizar campos
    update_data = historia_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(historia, field, value)
    
    await db.commit()
    await db.refresh(historia)
    
    return historia


@router.delete("/{historia_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_historia_clinica(
    historia_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Eliminar una historia clínica
    """
    result = await db.execute(
        select(HistoriaClinicaPediatrica).where(HistoriaClinicaPediatrica.id == historia_id)
    )
    historia = result.scalar_one_or_none()
    
    if not historia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Historia clínica no encontrada"
        )
    
    await db.delete(historia)
    await db.commit()


# ============================================================================
# EXPLORACIÓN FÍSICA
# ============================================================================

@router.post("/{historia_id}/exploracion", response_model=ExploracionFisicaResponse, status_code=status.HTTP_201_CREATED)
async def crear_exploracion_fisica(
    historia_id: UUID,
    exploracion_data: ExploracionFisicaCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Crear o actualizar la exploración física de una historia clínica
    """
    # Verificar que la historia existe
    result = await db.execute(
        select(HistoriaClinicaPediatrica).where(HistoriaClinicaPediatrica.id == historia_id)
    )
    historia = result.scalar_one_or_none()
    
    if not historia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Historia clínica no encontrada"
        )
    
    # Verificar si ya existe una exploración física
    result = await db.execute(
        select(ExploracionFisica).where(ExploracionFisica.historia_clinica_id == historia_id)
    )
    exploracion_existente = result.scalar_one_or_none()
    
    if exploracion_existente:
        # Actualizar
        update_data = exploracion_data.model_dump(exclude_unset=True, exclude={'historia_clinica_id'})
        for field, value in update_data.items():
            setattr(exploracion_existente, field, value)
        await db.commit()
        await db.refresh(exploracion_existente)
        return exploracion_existente
    else:
        # Crear nueva
        exploracion = ExploracionFisica(historia_clinica_id=historia_id, **exploracion_data.model_dump(exclude={'historia_clinica_id'}))
        db.add(exploracion)
        await db.commit()
        await db.refresh(exploracion)
        return exploracion


@router.put("/{historia_id}/exploracion", response_model=ExploracionFisicaResponse)
async def actualizar_exploracion_fisica(
    historia_id: UUID,
    exploracion_data: ExploracionFisicaUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar la exploración física
    """
    result = await db.execute(
        select(ExploracionFisica).where(ExploracionFisica.historia_clinica_id == historia_id)
    )
    exploracion = result.scalar_one_or_none()
    
    if not exploracion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exploración física no encontrada"
        )
    
    # Actualizar campos
    update_data = exploracion_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(exploracion, field, value)
    
    await db.commit()
    await db.refresh(exploracion)
    
    return exploracion


# ============================================================================
# ANTECEDENTES NO PATOLÓGICOS
# ============================================================================

@router.post("/{historia_id}/antecedentes-no-patologicos", response_model=AntecedentesNoPatologicosResponse, status_code=status.HTTP_201_CREATED)
async def crear_antecedentes_no_patologicos(
    historia_id: UUID,
    antecedentes_data: AntecedentesNoPatologicosCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Crear o actualizar los antecedentes no patológicos
    """
    # Verificar que la historia existe
    result = await db.execute(
        select(HistoriaClinicaPediatrica).where(HistoriaClinicaPediatrica.id == historia_id)
    )
    historia = result.scalar_one_or_none()
    
    if not historia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Historia clínica no encontrada"
        )
    
    # Verificar si ya existen antecedentes
    result = await db.execute(
        select(AntecedentesNoPatologicos).where(AntecedentesNoPatologicos.historia_clinica_id == historia_id)
    )
    antecedentes_existentes = result.scalar_one_or_none()
    
    if antecedentes_existentes:
        # Actualizar
        update_data = antecedentes_data.model_dump(exclude_unset=True, exclude={'historia_clinica_id'})
        for field, value in update_data.items():
            setattr(antecedentes_existentes, field, value)
        await db.commit()
        await db.refresh(antecedentes_existentes)
        return antecedentes_existentes
    else:
        # Crear nuevos
        antecedentes = AntecedentesNoPatologicos(
            historia_clinica_id=historia_id, 
            **antecedentes_data.model_dump(exclude={'historia_clinica_id'})
        )
        db.add(antecedentes)
        await db.commit()
        await db.refresh(antecedentes)
        return antecedentes


@router.put("/{historia_id}/antecedentes-no-patologicos", response_model=AntecedentesNoPatologicosResponse)
async def actualizar_antecedentes_no_patologicos(
    historia_id: UUID,
    antecedentes_data: AntecedentesNoPatologicosUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar los antecedentes no patológicos
    """
    result = await db.execute(
        select(AntecedentesNoPatologicos).where(AntecedentesNoPatologicos.historia_clinica_id == historia_id)
    )
    antecedentes = result.scalar_one_or_none()
    
    if not antecedentes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Antecedentes no patológicos no encontrados"
        )
    
    # Actualizar campos
    update_data = antecedentes_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(antecedentes, field, value)
    
    await db.commit()
    await db.refresh(antecedentes)
    
    return antecedentes
