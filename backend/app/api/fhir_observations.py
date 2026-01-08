from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.models.fhir_observation import FHIRObservation, ObservationStatus
from app.models.usuario import Usuario
from app.models.paciente import Paciente
from app.schemas.fhir_observation import (
    ObservationCreate,
    ObservationUpdate,
    ObservationResponse,
    ObservationFHIR,
    ObservationBundle,
)
from app.api.dependencies import get_current_user
from app.services.fhir_observation_transformer import FHIRObservationTransformer

router = APIRouter()


@router.post(
    "/", response_model=ObservationResponse, status_code=status.HTTP_201_CREATED
)
async def crear_observation(
    observation: ObservationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Crear una nueva Observation FHIR

    - **code**: Código de la observación (LOINC, SNOMED, etc)
    - **subject_id**: ID del paciente
    - **value**: Valor de la observación (quantity, string, boolean, etc)
    - **category**: Categoría (vital-signs, laboratory, etc)
    """
    # Verificar que el paciente existe
    result = await db.execute(
        select(Paciente).where(Paciente.id == observation.subject_id)
    )
    paciente = result.scalar_one_or_none()

    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado"
        )

    # Convertir schemas Pydantic a dict para almacenar en JSONB
    observation_dict = observation.model_dump(exclude_unset=True)

    # Convertir objetos Pydantic a dict
    if observation.code:
        observation_dict["code"] = observation.code.model_dump(exclude_none=True)
    if observation.value_quantity:
        observation_dict["value_quantity"] = observation.value_quantity.model_dump(
            exclude_none=True
        )
    if observation.value_codeable_concept:
        observation_dict["value_codeable_concept"] = (
            observation.value_codeable_concept.model_dump(exclude_none=True)
        )
    if observation.value_range:
        observation_dict["value_range"] = observation.value_range.model_dump(
            exclude_none=True
        )
    if observation.value_ratio:
        observation_dict["value_ratio"] = observation.value_ratio.model_dump(
            exclude_none=True
        )
    if observation.value_period:
        observation_dict["value_period"] = observation.value_period.model_dump(
            exclude_none=True
        )
    if observation.interpretation:
        observation_dict["interpretation"] = [
            i.model_dump(exclude_none=True) for i in observation.interpretation
        ]
    if observation.note:
        observation_dict["note"] = [
            n.model_dump(exclude_none=True) for n in observation.note
        ]
    if observation.method:
        observation_dict["method"] = observation.method.model_dump(exclude_none=True)
    if observation.body_site:
        observation_dict["body_site"] = observation.body_site.model_dump(
            exclude_none=True
        )
    if observation.reference_range:
        observation_dict["reference_range"] = [
            r.model_dump(exclude_none=True) for r in observation.reference_range
        ]
    if observation.component:
        observation_dict["component"] = [
            c.model_dump(exclude_none=True) for c in observation.component
        ]
    if observation.performer:
        observation_dict["performer"] = [
            p.model_dump(exclude_none=True) for p in observation.performer
        ]
    if observation.derived_from:
        observation_dict["derived_from"] = [
            d.model_dump(exclude_none=True) for d in observation.derived_from
        ]
    if observation.identifier:
        observation_dict["identifier"] = [
            i.model_dump(exclude_none=True) for i in observation.identifier
        ]

    # Crear la observación
    nueva_observation = FHIRObservation(**observation_dict, created_by=current_user.id)

    db.add(nueva_observation)
    await db.commit()
    await db.refresh(nueva_observation)

    return nueva_observation


@router.get("/", response_model=List[ObservationResponse])
async def listar_observations(
    patient: Optional[UUID] = Query(None, description="Filtrar por paciente"),
    category: Optional[str] = Query(None, description="Filtrar por categoría"),
    code: Optional[str] = Query(None, description="Filtrar por código"),
    date: Optional[str] = Query(None, description="Filtrar por fecha (YYYY-MM-DD)"),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Listar Observations con filtros opcionales

    Parámetros de búsqueda compatibles con FHIR:
    - **patient**: UUID del paciente
    - **category**: vital-signs, laboratory, imaging, etc
    - **code**: Código de la observación
    - **date**: Fecha efectiva (YYYY-MM-DD)
    - **status**: Estado de la observación
    """
    query = select(FHIRObservation)

    # Aplicar filtros
    conditions = []

    if patient:
        conditions.append(FHIRObservation.subject_id == patient)

    if category:
        conditions.append(FHIRObservation.category.contains([category]))

    if code:
        conditions.append(
            func.jsonb_path_exists(
                FHIRObservation.code, f'$.coding[*] ? (@.code == "{code}")'
            )
        )

    if date:
        try:
            fecha = datetime.strptime(date, "%Y-%m-%d")
            conditions.append(
                func.date(FHIRObservation.effective_datetime) == fecha.date()
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha inválido. Use YYYY-MM-DD",
            )

    if status:
        try:
            status_enum = ObservationStatus(status)
            conditions.append(FHIRObservation.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estado inválido: {status}",
            )

    if conditions:
        query = query.where(and_(*conditions))

    query = (
        query.offset(skip)
        .limit(limit)
        .order_by(FHIRObservation.effective_datetime.desc())
    )

    result = await db.execute(query)
    observations = result.scalars().all()

    return observations


@router.get("/{observation_id}", response_model=ObservationResponse)
async def obtener_observation(
    observation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener una Observation por ID
    """
    result = await db.execute(
        select(FHIRObservation).where(FHIRObservation.id == observation_id)
    )
    observation = result.scalar_one_or_none()

    if not observation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Observation no encontrada"
        )

    return observation


@router.put("/{observation_id}", response_model=ObservationResponse)
async def actualizar_observation(
    observation_id: UUID,
    observation_update: ObservationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Actualizar una Observation existente
    """
    result = await db.execute(
        select(FHIRObservation).where(FHIRObservation.id == observation_id)
    )
    observation = result.scalar_one_or_none()

    if not observation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Observation no encontrada"
        )

    # Actualizar campos
    update_data = observation_update.model_dump(exclude_unset=True)

    # Convertir objetos Pydantic a dict
    if observation_update.code:
        update_data["code"] = observation_update.code.model_dump(exclude_none=True)
    if observation_update.value_quantity:
        update_data["value_quantity"] = observation_update.value_quantity.model_dump(
            exclude_none=True
        )
    if observation_update.value_codeable_concept:
        update_data["value_codeable_concept"] = (
            observation_update.value_codeable_concept.model_dump(exclude_none=True)
        )
    if observation_update.interpretation:
        update_data["interpretation"] = [
            i.model_dump(exclude_none=True) for i in observation_update.interpretation
        ]
    if observation_update.note:
        update_data["note"] = [
            n.model_dump(exclude_none=True) for n in observation_update.note
        ]
    if observation_update.reference_range:
        update_data["reference_range"] = [
            r.model_dump(exclude_none=True) for r in observation_update.reference_range
        ]
    if observation_update.component:
        update_data["component"] = [
            c.model_dump(exclude_none=True) for c in observation_update.component
        ]

    for key, value in update_data.items():
        setattr(observation, key, value)

    await db.commit()
    await db.refresh(observation)

    return observation


@router.delete("/{observation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_observation(
    observation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Eliminar una Observation
    """
    result = await db.execute(
        select(FHIRObservation).where(FHIRObservation.id == observation_id)
    )
    observation = result.scalar_one_or_none()

    if not observation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Observation no encontrada"
        )

    await db.delete(observation)
    await db.commit()

    return None


@router.get("/{observation_id}/fhir", response_model=ObservationFHIR)
async def obtener_observation_fhir(
    observation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener una Observation en formato FHIR R4 completo
    """
    result = await db.execute(
        select(FHIRObservation).where(FHIRObservation.id == observation_id)
    )
    observation = result.scalar_one_or_none()

    if not observation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Observation no encontrada"
        )

    return observation.to_fhir_dict()


@router.get("/patient/{patient_id}/bundle", response_model=ObservationBundle)
async def obtener_observations_bundle(
    patient_id: UUID,
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener todas las Observations de un paciente en formato Bundle FHIR
    """
    query = select(FHIRObservation).where(FHIRObservation.subject_id == patient_id)

    if category:
        query = query.where(FHIRObservation.category.contains([category]))

    query = query.order_by(FHIRObservation.effective_datetime.desc())

    result = await db.execute(query)
    observations = result.scalars().all()

    bundle = FHIRObservationTransformer.crear_bundle_observations(observations)

    return bundle


@router.post("/from-vital-sign", response_model=ObservationResponse)
async def crear_observation_desde_signo_vital(
    nombre_parametro: str,
    valor: float,
    unidad: str,
    paciente_id: UUID,
    consulta_id: Optional[UUID] = None,
    fecha: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Crear una Observation FHIR desde un signo vital

    Transforma automáticamente el signo vital a formato FHIR con códigos LOINC
    """
    # Transformar a FHIR
    observation_data = FHIRObservationTransformer.from_signo_vital(
        nombre_parametro=nombre_parametro,
        valor=valor,
        unidad=unidad,
        paciente_id=paciente_id,
        consulta_id=consulta_id,
        fecha=fecha,
        medico_id=current_user.id,
    )

    # Crear observación
    nueva_observation = FHIRObservation(**observation_data, created_by=current_user.id)

    db.add(nueva_observation)
    await db.commit()
    await db.refresh(nueva_observation)

    return nueva_observation


@router.post("/from-blood-pressure", response_model=ObservationResponse)
async def crear_observation_presion_arterial(
    sistolica: float,
    diastolica: float,
    paciente_id: UUID,
    consulta_id: Optional[UUID] = None,
    fecha: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Crear una Observation FHIR multi-componente para presión arterial
    """
    observation_data = FHIRObservationTransformer.from_presion_arterial(
        sistolica=sistolica,
        diastolica=diastolica,
        paciente_id=paciente_id,
        consulta_id=consulta_id,
        fecha=fecha,
        medico_id=current_user.id,
    )

    nueva_observation = FHIRObservation(**observation_data, created_by=current_user.id)

    db.add(nueva_observation)
    await db.commit()
    await db.refresh(nueva_observation)

    return nueva_observation


@router.post("/from-lab-parameter", response_model=ObservationResponse)
async def crear_observation_desde_laboratorio(
    nombre_parametro: str,
    valor: float,
    unidad: str,
    paciente_id: UUID,
    prueba_id: UUID,
    fecha: datetime,
    interpretacion: Optional[str] = None,
    estado_anormal: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Crear una Observation FHIR desde un parámetro de laboratorio

    Transforma automáticamente el parámetro a formato FHIR con códigos LOINC
    """
    observation_data = FHIRObservationTransformer.from_parametro_laboratorio(
        nombre_parametro=nombre_parametro,
        valor=valor,
        unidad=unidad,
        paciente_id=paciente_id,
        prueba_id=prueba_id,
        fecha=fecha,
        medico_id=current_user.id,
        interpretacion=interpretacion,
        estado_anormal=estado_anormal,
    )

    nueva_observation = FHIRObservation(**observation_data, created_by=current_user.id)

    db.add(nueva_observation)
    await db.commit()
    await db.refresh(nueva_observation)

    return nueva_observation


@router.get("/statistics/summary")
async def obtener_estadisticas_observations(
    patient_id: Optional[UUID] = Query(None),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener estadísticas de Observations
    """
    query = select(FHIRObservation)

    if patient_id:
        query = query.where(FHIRObservation.subject_id == patient_id)

    if category:
        query = query.where(FHIRObservation.category.contains([category]))

    result = await db.execute(query)
    observations = result.scalars().all()

    # Calcular estadísticas
    total = len(observations)
    por_categoria = {}
    por_estado = {}

    for obs in observations:
        # Por categoría
        if obs.category:
            for cat in obs.category:
                por_categoria[cat] = por_categoria.get(cat, 0) + 1

        # Por estado
        estado = obs.status.value
        por_estado[estado] = por_estado.get(estado, 0) + 1

    return {
        "total": total,
        "por_categoria": por_categoria,
        "por_estado": por_estado,
        "ultima_actualizacion": (
            max([obs.updated_at for obs in observations]) if observations else None
        ),
    }
