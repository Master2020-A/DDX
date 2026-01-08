"""
Endpoints FHIR (HL7 FHIR R4) para la aplicación
"""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fhir.resources.patient import Patient
from fhir.resources.detectedissue import DetectedIssue
from fhir.resources.observation import Observation
from fhir.resources.careplan import CarePlan
from fhir.resources.medicationrequest import MedicationRequest

from app.core.database import get_db
from app.models.paciente import Paciente
from app.models.ia_medica import (
    InteraccionMedicamentosa,
    AnomaliaDetectada,
    RecomendacionTratamiento,
)
from app.fhir.mappers import (
    paciente_to_fhir_patient,
    interaccion_to_fhir_detectedissue,
    anomalia_to_fhir_observation,
    recc_to_fhir_careplan,
    recc_to_fhir_medicationrequests,
    apply_fhir_patient_to_paciente,
)

router = APIRouter(prefix="/fhir", tags=["FHIR"])


# ---------------------------------------------------------------------
# Patient
# ---------------------------------------------------------------------


@router.get(
    "/Patient/{paciente_id}",
    response_model=Patient,
    summary="Get Fhir Patient",
    description="Devuelve un recurso FHIR Patient construido a partir del modelo Paciente. URL final: /api/fhir/Patient/{paciente_id}",
)
async def get_fhir_patient(
    paciente_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Paciente).where(Paciente.id == paciente_id))
    paciente = result.scalar_one_or_none()

    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado",
        )

    resource = paciente_to_fhir_patient(paciente)
    return resource


@router.post(
    "/Patient",
    response_model=Patient,
    summary="Crear o actualizar un paciente a partir de un Patient FHIR",
    status_code=status.HTTP_201_CREATED,
)
async def create_or_update_patient(
    resource: Patient,
    db: AsyncSession = Depends(get_db),
):
    """
    Crea o actualiza un paciente usando un recurso FHIR Patient.

    Reglas:
    - Si resource.id corresponde a un Paciente existente, se actualiza.
    - Si no, pero hay un identifier con system http://ddx.local/expediente
      y coincide con numero_expediente, se actualiza ese Paciente.
    - En otro caso, se crea un Paciente nuevo.
    """

    paciente: Optional[Paciente] = None

    pid: Optional[UUID] = None
    if resource.id:
        from uuid import UUID as UUID_cls

        try:
            pid = UUID_cls(str(resource.id))
            result = await db.execute(select(Paciente).where(Paciente.id == pid))
            paciente = result.scalar_one_or_none()
        except ValueError:
            pid = None

    expediente = None
    if resource.identifier:
        for ident in resource.identifier:
            if ident.system == "http://ddx.local/expediente" and ident.value:
                expediente = ident.value
                break

    if not paciente and expediente:
        result = await db.execute(
            select(Paciente).where(Paciente.numero_expediente == expediente)
        )
        paciente = result.scalar_one_or_none()

    if not paciente:
        paciente = Paciente()
        if pid is not None:
            paciente.id = pid
        paciente = apply_fhir_patient_to_paciente(resource, paciente)
        db.add(paciente)
    else:
        paciente = apply_fhir_patient_to_paciente(resource, paciente)

    await db.commit()
    await db.refresh(paciente)

    return paciente_to_fhir_patient(paciente)


# ---------------------------------------------------------------------
# DetectedIssue (Interacciones medicamentosas)
# ---------------------------------------------------------------------


@router.get(
    "/DetectedIssue/{interaccion_id}",
    response_model=DetectedIssue,
    summary="Obtener una interacción medicamentosa como DetectedIssue FHIR",
)
async def get_detected_issue(
    interaccion_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InteraccionMedicamentosa).where(
            InteraccionMedicamentosa.id == interaccion_id
        )
    )
    interaccion = result.scalar_one_or_none()

    if not interaccion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interacción no encontrada",
        )

    resource = interaccion_to_fhir_detectedissue(interaccion)
    return resource


@router.get(
    "/DetectedIssue",
    response_model=List[DetectedIssue],
    summary="Listar interacciones medicamentosas FHIR por paciente",
)
async def search_detected_issues(
    patient: Optional[UUID] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    query = select(InteraccionMedicamentosa)

    if patient:
        query = query.where(InteraccionMedicamentosa.paciente_id == patient)

    query = query.order_by(InteraccionMedicamentosa.created_at.desc()).limit(limit)

    result = await db.execute(query)
    interacciones = result.scalars().all()

    resources = [interaccion_to_fhir_detectedissue(inter) for inter in interacciones]

    return resources


# ---------------------------------------------------------------------
# Observation (Anomalías detectadas)
# ---------------------------------------------------------------------


@router.get(
    "/Observation/{anomalia_id}",
    response_model=Observation,
    summary="Obtener una anomalía como Observation FHIR",
)
async def get_observation(
    anomalia_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AnomaliaDetectada).where(AnomaliaDetectada.id == anomalia_id)
    )
    anomalia = result.scalar_one_or_none()

    if not anomalia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anomalía no encontrada",
        )

    resource = anomalia_to_fhir_observation(anomalia)
    return resource


@router.get(
    "/Observation",
    response_model=List[Observation],
    summary="Listar anomalías FHIR por paciente",
)
async def search_observations(
    patient: Optional[UUID] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    query = select(AnomaliaDetectada)

    if patient:
        query = query.where(AnomaliaDetectada.paciente_id == patient)

    query = query.order_by(AnomaliaDetectada.created_at.desc()).limit(limit)

    result = await db.execute(query)
    anomalias = result.scalars().all()

    resources = [anomalia_to_fhir_observation(a) for a in anomalias]

    return resources


# ---------------------------------------------------------------------
# CarePlan (Recomendaciones de tratamiento)
# ---------------------------------------------------------------------


@router.get(
    "/CarePlan/{recomendacion_id}",
    response_model=CarePlan,
    summary="Obtener un plan de tratamiento como CarePlan FHIR",
)
async def get_careplan(
    recomendacion_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RecomendacionTratamiento).where(
            RecomendacionTratamiento.id == recomendacion_id
        )
    )
    rec = result.scalar_one_or_none()

    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recomendación de tratamiento no encontrada",
        )

    resource = recc_to_fhir_careplan(rec)
    return resource


@router.get(
    "/CarePlan",
    response_model=List[CarePlan],
    summary="Listar planes de tratamiento FHIR por paciente",
)
async def search_careplans(
    patient: Optional[UUID] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    query = select(RecomendacionTratamiento)

    if patient:
        query = query.where(RecomendacionTratamiento.paciente_id == patient)

    query = query.order_by(RecomendacionTratamiento.created_at.desc()).limit(limit)

    result = await db.execute(query)
    recs = result.scalars().all()

    resources = [recc_to_fhir_careplan(r) for r in recs]

    return resources


# ---------------------------------------------------------------------
# MedicationRequest (órdenes de medicación)
# ---------------------------------------------------------------------


@router.get(
    "/MedicationRequest",
    response_model=List[MedicationRequest],
    summary="Listar MedicationRequest FHIR derivados de recomendaciones",
)
async def search_medication_requests(
    patient: Optional[UUID] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    query = select(RecomendacionTratamiento)

    if patient:
        query = query.where(RecomendacionTratamiento.paciente_id == patient)

    query = query.order_by(RecomendacionTratamiento.created_at.desc())

    result = await db.execute(query)
    recs = result.scalars().all()

    resources: List[MedicationRequest] = []

    for rec in recs:
        for mr in recc_to_fhir_medicationrequests(rec):
            resources.append(mr)
            if len(resources) >= limit:
                return resources

    return resources
