"""
Endpoints para importar recursos FHIR desde servidores externos
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel, HttpUrl
import logging

from app.core.database import get_db
from app.models.usuario import Usuario
from app.models.paciente import Paciente
from app.models.fhir_condition import FHIRCondition
from app.api.dependencies import get_current_user
from app.services.fhir_client import FHIRClient, PUBLIC_FHIR_SERVERS
from app.services.fhir_condition_importer import FHIRConditionImporter

logger = logging.getLogger(__name__)
router = APIRouter()


# Schemas
class FHIRServerConfig(BaseModel):
    """Configuración de servidor FHIR"""

    url: str
    auth_token: Optional[str] = None
    name: Optional[str] = None


class ImportConditionsRequest(BaseModel):
    """Request para importar condiciones"""

    fhir_server_url: str
    fhir_patient_id: str
    local_patient_id: str
    auth_token: Optional[str] = None
    clinical_status: Optional[str] = None


class ImportObservationsRequest(BaseModel):
    """Request para importar observaciones"""

    fhir_server_url: str
    fhir_patient_id: str
    local_patient_id: str
    auth_token: Optional[str] = None
    category: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None


class FHIRPatientSearchRequest(BaseModel):
    """Request para buscar pacientes en FHIR"""

    fhir_server_url: str
    name: Optional[str] = None
    identifier: Optional[str] = None
    birthdate: Optional[str] = None
    auth_token: Optional[str] = None


@router.get("/servers/public")
async def get_public_fhir_servers():
    """
    Obtener lista de servidores FHIR públicos de prueba
    """
    return PUBLIC_FHIR_SERVERS


@router.post("/test-connection")
async def test_fhir_connection(config: FHIRServerConfig):
    """
    Probar conexión con un servidor FHIR (no requiere autenticación)
    """
    client = FHIRClient(config.url, config.auth_token)
    is_connected = await client.test_connection()

    return {
        "success": is_connected,
        "server_url": config.url,
        "message": (
            "Conexión exitosa"
            if is_connected
            else "Error al conectar con el servidor FHIR"
        ),
    }


@router.post("/search-patients")
async def search_fhir_patients(
    request: FHIRPatientSearchRequest, current_user: Usuario = Depends(get_current_user)
):
    """
    Buscar pacientes en un servidor FHIR externo
    """
    client = FHIRClient(request.fhir_server_url, request.auth_token)

    patients = await client.search_patients(
        name=request.name, identifier=request.identifier, birthdate=request.birthdate
    )

    # Simplificar respuesta
    simplified_patients = []
    for patient in patients:
        name_parts = []
        if "name" in patient and len(patient["name"]) > 0:
            name_obj = patient["name"][0]
            if "given" in name_obj:
                name_parts.extend(name_obj["given"])
            if "family" in name_obj:
                name_parts.append(name_obj["family"])

        full_name = " ".join(name_parts) if name_parts else "Sin nombre"

        simplified_patients.append(
            {
                "id": patient.get("id"),
                "name": full_name,
                "birthDate": patient.get("birthDate"),
                "gender": patient.get("gender"),
                "identifier": patient.get("identifier", []),
            }
        )

    return {"total": len(simplified_patients), "patients": simplified_patients}


@router.post("/import/conditions")
async def import_patient_conditions(
    request: ImportConditionsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Importar diagnósticos (Condition) de un paciente desde servidor FHIR
    """
    # Verificar que el paciente existe
    result = await db.execute(
        select(Paciente).where(Paciente.id == request.local_patient_id)
    )
    patient = result.scalar_one_or_none()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado"
        )

    # Crear cliente FHIR
    client = FHIRClient(request.fhir_server_url, request.auth_token)

    # Crear importador
    importer = FHIRConditionImporter(db, client)

    # Importar condiciones
    try:
        conditions = await importer.import_patient_conditions(
            request.fhir_patient_id, request.local_patient_id, request.clinical_status
        )

        # Extraer información legible
        conditions_info = [
            importer.extract_diagnosis_info(condition) for condition in conditions
        ]

        return {
            "success": True,
            "total_imported": len(conditions),
            "conditions": conditions_info,
            "patient_id": request.local_patient_id,
            "source": request.fhir_server_url,
        }

    except Exception as e:
        logger.error(f"Error importando condiciones: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al importar diagnósticos: {str(e)}",
        )


@router.get("/conditions/patient/{patient_id}")
async def get_patient_imported_conditions(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    clinical_status: Optional[str] = None,
    limit: int = 100,
):
    """
    Obtener diagnósticos importados de un paciente
    """
    query = select(FHIRCondition).where(FHIRCondition.subject_id == patient_id)

    if clinical_status:
        query = query.where(FHIRCondition.clinical_status == clinical_status)

    query = query.limit(limit).order_by(FHIRCondition.recorded_date.desc())

    result = await db.execute(query)
    conditions = result.scalars().all()

    # Crear importador para extraer info
    client = FHIRClient("dummy")  # No se usa para extraer info
    importer = FHIRConditionImporter(db, client)

    conditions_info = [
        importer.extract_diagnosis_info(condition) for condition in conditions
    ]

    return {"total": len(conditions_info), "conditions": conditions_info}


@router.get("/conditions/{condition_id}")
async def get_condition_detail(
    condition_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener detalle completo de un diagnóstico importado
    """
    result = await db.execute(
        select(FHIRCondition).where(FHIRCondition.id == condition_id)
    )
    condition = result.scalar_one_or_none()

    if not condition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Diagnóstico no encontrado"
        )

    # Crear importador para extraer info
    client = FHIRClient("dummy")
    importer = FHIRConditionImporter(db, client)

    condition_info = importer.extract_diagnosis_info(condition)

    # Agregar recurso FHIR completo
    condition_info["fhir_resource"] = condition.fhir_resource

    return condition_info


@router.delete("/conditions/{condition_id}")
async def delete_imported_condition(
    condition_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Eliminar un diagnóstico importado
    """
    result = await db.execute(
        select(FHIRCondition).where(FHIRCondition.id == condition_id)
    )
    condition = result.scalar_one_or_none()

    if not condition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Diagnóstico no encontrado"
        )

    await db.delete(condition)
    await db.commit()

    return {"success": True, "message": "Diagnóstico eliminado correctamente"}


@router.post("/sync/patient/{patient_id}")
async def sync_patient_from_fhir(
    patient_id: str,
    fhir_server_url: str,
    fhir_patient_id: str,
    auth_token: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Sincronizar todos los datos de un paciente desde FHIR
    (Conditions, Observations, etc.)
    """
    # Verificar paciente
    result = await db.execute(select(Paciente).where(Paciente.id == patient_id))
    patient = result.scalar_one_or_none()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado"
        )

    client = FHIRClient(fhir_server_url, auth_token)
    importer = FHIRConditionImporter(db, client)

    results = {"patient_id": patient_id, "source": fhir_server_url, "imported": {}}

    # Importar condiciones
    try:
        conditions = await importer.import_patient_conditions(
            fhir_patient_id, patient_id
        )
        results["imported"]["conditions"] = len(conditions)
    except Exception as e:
        logger.error(f"Error importando condiciones: {str(e)}")
        results["imported"]["conditions"] = 0
        results["errors"] = results.get("errors", [])
        results["errors"].append(f"Conditions: {str(e)}")

    # TODO: Importar Observations, MedicationStatements, etc.

    return results
