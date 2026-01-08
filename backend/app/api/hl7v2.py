"""
API para recibir mensajes HL7 v2 y convertirlos a FHIR / modelos internos
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID, uuid4
from datetime import datetime

from fhir.resources.patient import Patient as FhirPatient
from fhir.resources.observation import Observation as FhirObservation

from app.core.database import get_db
from app.models.paciente import Paciente
from app.models.ia_medica import AnomaliaDetectada
from app.fhir.mappers import apply_fhir_patient_to_paciente
from app.integrations.hl7v2_adapter import HL7v2ToFHIRAdapter

router = APIRouter(prefix="/hl7v2", tags=["HL7 v2 Integración"])


# ===== Schemas de entrada / salida =====


class HL7v2ORURequest(BaseModel):
    """
    Mensaje HL7 v2 ORU^R01 en texto.
    """

    message: str = Field(
        ...,
        description="Mensaje HL7 v2 ORU^R01 en formato texto",
        example=(
            "MSH|^~\\&|LIS|HOSPITAL|DDX|HOSPITAL|202512160800||ORU^R01|1234|P|2.5\r"
            "PID|1||123456^^^HOSPITAL^MR||DOE^JOHN||19800101|M\r"
            "OBR|1||5678^LIS||GLUCOSA\r"
            "OBX|1|NM|2345-7^GLUCOSE^LN||250|mg/dL|70-110|H|||F\r"
        ),
    )


class HL7v2ORUResponse(BaseModel):
    """
    Resumen de lo que se hizo con el mensaje HL7
    """

    success: bool
    patient_id: Optional[str] = None
    observations_created: int = 0
    detail: Optional[str] = None
    fhir_patient: Optional[Dict[str, Any]] = None


# ===== Endpoint principal =====


@router.post(
    "/oru",
    response_model=HL7v2ORUResponse,
    summary="Recibir mensaje HL7 ORU^R01 (resultados) y convertir a FHIR / modelos internos",
)
async def recibir_oru_r01(
    request: HL7v2ORURequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Recibe un mensaje HL7 v2 ORU^R01, lo convierte a recursos FHIR usando HL7v2ToFHIRAdapter
    y los mapea a tus modelos internos:

    - PID -> Paciente
    - OBX -> AnomaliaDetectada (simplificado, como hallazgos anómalos)
    """

    adapter = HL7v2ToFHIRAdapter()

    try:
        parsed = adapter.parse_oru_r01(request.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al parsear mensaje HL7: {e}",
        )

    fhir_patient: FhirPatient = parsed.get("patient")
    fhir_observations: List[FhirObservation] = parsed.get("observations", [])

    if not fhir_patient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El mensaje HL7 no contiene un segmento PID válido",
        )

    # 1) Crear / actualizar paciente usando FHIR Patient
    paciente = await _upsert_paciente_from_fhir(fhir_patient, db)

    # 2) Mapear Observations a AnomaliaDetectada muy simplificadas
    created_count = 0
    for obs in fhir_observations:
        try:
            await _crear_anomalia_desde_observation(paciente.id, obs, db)
            created_count += 1
        except Exception:
            # No tiramos todo si una falla
            continue

    await db.commit()

    from app.fhir.mappers import paciente_to_fhir_patient

    fhir_patient_out = paciente_to_fhir_patient(paciente)

    return HL7v2ORUResponse(
        success=True,
        patient_id=str(paciente.id),
        observations_created=created_count,
        detail="Mensaje HL7 procesado correctamente",
        fhir_patient=fhir_patient_out.dict(),
    )


# ===== Helpers internos =====


async def _upsert_paciente_from_fhir(
    resource: FhirPatient,
    db: AsyncSession,
) -> Paciente:
    """
    Crea o actualiza un Paciente a partir de un Patient FHIR (similar a POST /fhir/Patient).
    """

    from uuid import UUID as UUID_cls

    paciente: Optional[Paciente] = None
    pid: Optional[UUID] = None

    # Buscar por id FHIR (si es UUID)
    if resource.id:
        try:
            pid = UUID_cls(str(resource.id))
            result = await db.execute(select(Paciente).where(Paciente.id == pid))
            paciente = result.scalar_one_or_none()
        except ValueError:
            pid = None

    # Buscar por MRN u otro identificador si quisieras (ejemplo con MRN HL7)
    expediente = None
    if resource.identifier:
        for ident in resource.identifier:
            if ident.system == "http://hospital.local/mrn" and ident.value:
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
        await db.flush()  # para que tenga id
    else:
        paciente = apply_fhir_patient_to_paciente(resource, paciente)

    return paciente


async def _crear_anomalia_desde_observation(
    paciente_id: UUID,
    obs: FhirObservation,
    db: AsyncSession,
):
    """
    Crea una AnomaliaDetectada a partir de una Observation FHIR generada desde OBX.
    Intentamos mapear:
    - code.text -> descripcion / patron_detectado
    - valueString -> valores_anormales['valor']
    - note[0].text -> añadida a valores_anormales['detalle']
    - abnormal_flag en note -> severidad aproximada
    """

    from uuid import uuid4

    descripcion = obs.code.text if obs.code and obs.code.text else "Hallazgo en HL7"

    valores_anormales = {}
    if getattr(obs, "valueString", None):
        valores_anormales["valor"] = obs.valueString

    if getattr(obs, "note", None) and len(obs.note) > 0 and obs.note[0].text:
        valores_anormales["detalle"] = obs.note[0].text

        # Intentar deducir flag de anormalidad (H, L, etc.)
        # Ej: "Unidad: mg/dL | Rango ref: 70-110 | Flag anormalidad: H"
        detalle_lower = obs.note[0].text.lower()
        if "flag anormalidad" in detalle_lower:
            if " h" in detalle_lower or " h|" in detalle_lower:
                sev = "severa"
            elif " l" in detalle_lower or " l|" in detalle_lower:
                sev = "moderada"
            else:
                sev = "leve"
        else:
            sev = "moderada"
    else:
        sev = "moderada"

    nueva = AnomaliaDetectada(
        id=uuid4(),
        paciente_id=paciente_id,
        tipo_estudio="laboratorio",
        estudio_id=None,
        tipo_anomalia="hl7_obx",
        severidad=sev,
        descripcion=descripcion,
        localizacion=None,
        valores_anormales=valores_anormales or None,
        patron_detectado=descripcion,
        confianza_deteccion=0.7,
        requiere_atencion_inmediata=False,
        recomendaciones=[],
        estudios_adicionales=[],
        revisado_por_medico=False,
        created_at=datetime.utcnow(),
    )

    db.add(nueva)
