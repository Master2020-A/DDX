from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.models.prueba import PruebaMedica, ResultadoPrueba
from app.models.usuario import Usuario
from app.schemas.prueba import PruebaMedicaCreate, PruebaMedicaResponse, ResultadoPruebaCreate
from app.api.dependencies import get_current_active_medico

router = APIRouter()


@router.post("/", response_model=PruebaMedicaResponse, status_code=status.HTTP_201_CREATED)
async def solicitar_prueba(
    prueba_data: PruebaMedicaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Solicitar una nueva prueba médica (laboratorio, imagen, etc.).
    """
    nueva_prueba = PruebaMedica(
        **prueba_data.model_dump(),
        solicitado_por=current_user.id
    )
    
    db.add(nueva_prueba)
    await db.commit()
    await db.refresh(nueva_prueba)
    
    return nueva_prueba


@router.get("/consulta/{consulta_id}", response_model=List[PruebaMedicaResponse])
async def listar_pruebas_consulta(
    consulta_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Listar todas las pruebas médicas de una consulta.
    """
    result = await db.execute(
        select(PruebaMedica)
        .where(PruebaMedica.consulta_id == consulta_id)
        .order_by(PruebaMedica.fecha_solicitud.desc())
    )
    pruebas = result.scalars().all()
    return pruebas


@router.get("/{prueba_id}", response_model=PruebaMedicaResponse)
async def obtener_prueba(
    prueba_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Obtener detalles de una prueba médica específica.
    """
    result = await db.execute(
        select(PruebaMedica).where(PruebaMedica.id == prueba_id)
    )
    prueba = result.scalar_one_or_none()
    
    if not prueba:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prueba no encontrada"
        )
    
    return prueba


@router.post("/resultados", status_code=status.HTTP_201_CREATED)
async def registrar_resultado(
    resultado_data: ResultadoPruebaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Registrar el resultado de una prueba médica.
    """
    # Verify that the test exists
    result = await db.execute(
        select(PruebaMedica).where(PruebaMedica.id == resultado_data.prueba_id)
    )
    prueba = result.scalar_one_or_none()
    
    if not prueba:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prueba no encontrada"
        )
    
    nuevo_resultado = ResultadoPrueba(
        **resultado_data.model_dump(),
        registrado_por=current_user.id
    )
    
    db.add(nuevo_resultado)
    
    # Update test status
    from app.models.prueba import EstadoPruebaEnum
    from datetime import datetime
    prueba.estado = EstadoPruebaEnum.COMPLETADA
    prueba.fecha_realizada = datetime.now()
    
    await db.commit()
    await db.refresh(nuevo_resultado)
    
    return nuevo_resultado


@router.patch("/{prueba_id}/estado/{nuevo_estado}", response_model=PruebaMedicaResponse)
async def actualizar_estado_prueba(
    prueba_id: UUID,
    nuevo_estado: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Actualizar el estado de una prueba médica.
    """
    result = await db.execute(
        select(PruebaMedica).where(PruebaMedica.id == prueba_id)
    )
    prueba = result.scalar_one_or_none()
    
    if not prueba:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prueba no encontrada"
        )
    
    # Validate state
    from app.models.prueba import EstadoPruebaEnum
    try:
        estado_enum = EstadoPruebaEnum(nuevo_estado)
        prueba.estado = estado_enum
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido. Debe ser: solicitada, en_proceso, completada o cancelada"
        )
    
    await db.commit()
    await db.refresh(prueba)
    
    return prueba
