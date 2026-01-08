"""
Mapeadores entre modelos internos y recursos FHIR
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional, List

from fhir.resources.patient import Patient as FhirPatient
from fhir.resources.humanname import HumanName
from fhir.resources.identifier import Identifier

from fhir.resources.detectedissue import DetectedIssue
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from fhir.resources.observation import Observation
from fhir.resources.careplan import CarePlan
from fhir.resources.medicationrequest import MedicationRequest
from fhir.resources.dosage import Dosage
from fhir.resources.annotation import Annotation

from app.models.paciente import Paciente
from app.models.ia_medica import (
    InteraccionMedicamentosa,
    AnomaliaDetectada,
    RecomendacionTratamiento,
)


# ---------------------------------------------------------------------
# Paciente -> FHIR Patient
# ---------------------------------------------------------------------


def _build_human_name(p: Paciente) -> HumanName:
    """Construye el nombre FHIR a partir de tu modelo Paciente."""

    given: List[str] = []
    family: Optional[str] = None

    if hasattr(p, "nombre") and p.nombre:
        given.append(p.nombre)
    if hasattr(p, "apellido_materno") and p.apellido_materno:
        given.append(p.apellido_materno)
    if hasattr(p, "apellido_paterno") and p.apellido_paterno:
        family = p.apellido_paterno

    if not given and hasattr(p, "nombre_completo") and p.nombre_completo:
        partes = str(p.nombre_completo).split()
        if partes:
            family = partes[-1]
            given = partes[:-1]

    return HumanName.construct(
        family=family,
        given=given or None,
        text=getattr(p, "nombre_completo", None),
    )


def _build_identifiers(p: Paciente):
    identifiers: List[Identifier] = []

    if hasattr(p, "numero_expediente") and p.numero_expediente:
        identifiers.append(
            Identifier.construct(
                system="http://ddx.local/expediente",
                value=str(p.numero_expediente),
            )
        )

    return identifiers or None


def _convert_birth_date(fecha) -> Optional[date]:
    if not fecha:
        return None
    if isinstance(fecha, date):
        return fecha
    if isinstance(fecha, datetime):
        return fecha.date()
    try:
        return date.fromisoformat(str(fecha)[:10])
    except Exception:
        return None


def paciente_to_fhir_patient(p: Paciente) -> FhirPatient:
    name = _build_human_name(p)
    identifiers = _build_identifiers(p)

    gender: Optional[str] = None
    if hasattr(p, "genero") and p.genero:
        gender = str(p.genero).lower()
    elif hasattr(p, "sexo") and p.sexo:
        gender = str(p.sexo).lower()

    birth_date: Optional[date] = None
    if hasattr(p, "fecha_nacimiento"):
        birth_date = _convert_birth_date(getattr(p, "fecha_nacimiento"))

    return FhirPatient.construct(
        id=str(p.id),
        identifier=identifiers,
        name=[name],
        gender=gender,
        birthDate=birth_date,
        active=True,
    )


# ---------------------------------------------------------------------
# InteraccionMedicamentosa -> FHIR DetectedIssue
# ---------------------------------------------------------------------


def _map_severidad_interaccion(sev: Optional[str]) -> Optional[str]:
    """Mapea severidad local a high|moderate|low."""
    if not sev:
        return None
    s = sev.lower()
    if s in ("contraindicada", "severa"):
        return "high"
    if s == "moderada":
        return "moderate"
    if s == "leve":
        return "low"
    return None


def interaccion_to_fhir_detectedissue(
    inter: InteraccionMedicamentosa,
) -> DetectedIssue:
    patient_ref = Reference.construct(
        reference=f"Patient/{inter.paciente_id}",
    )

    severity = _map_severidad_interaccion(inter.severidad_maxima)

    code = CodeableConcept.construct(
        text="Interacciones medicamentosas detectadas",
        coding=[
            Coding.construct(
                system="http://terminology.hl7.org/CodeSystem/v3-ActCode",
                code="DRGINT",
                display="Drug interaction",
            )
        ],
    )

    meds = inter.medicamentos_analizados or []
    inters = inter.interacciones_encontradas or []
    detalle_meds = ", ".join(meds) if meds else "sin medicamentos listados"

    detail = (
        f"Se detectaron {len(inters)} posibles interacciones entre: {detalle_meds}."
    )

    descripciones = []
    for it in inters:
        desc = it.get("descripcion") or ""
        if desc:
            descripciones.append(desc)

    if descripciones:
        detail += " Ejemplos: " + " | ".join(descripciones[:3])

    return DetectedIssue.construct(
        id=str(inter.id),
        status="final",
        code=code,
        severity=severity,
        patient=patient_ref,
        identifiedDateTime=inter.created_at.isoformat() if inter.created_at else None,
        detail=detail,
    )


# ---------------------------------------------------------------------
# AnomaliaDetectada -> FHIR Observation
# ---------------------------------------------------------------------


def _map_categoria_observacion(tipo_estudio: Optional[str]) -> CodeableConcept:
    system = "http://terminology.hl7.org/CodeSystem/observation-category"
    te = (tipo_estudio or "").lower()

    if te == "laboratorio":
        code = "laboratory"
        display = "Laboratory"
    elif te in ("imagen", "ecografia", "radiografia", "tomografia", "resonancia"):
        code = "imaging"
        display = "Imaging"
    elif te in ("ekg", "eeg"):
        code = "procedure"
        display = "Procedure"
    else:
        code = "clinical"
        display = "Clinical"

    return CodeableConcept.construct(
        coding=[
            Coding.construct(
                system=system,
                code=code,
                display=display,
            )
        ],
        text=display,
    )


def anomalia_to_fhir_observation(anom: AnomaliaDetectada) -> Observation:
    patient_ref = Reference.construct(
        reference=f"Patient/{anom.paciente_id}",
    )

    category = _map_categoria_observacion(anom.tipo_estudio)

    code = CodeableConcept.construct(
        text=f"Anomalía detectada ({anom.tipo_anomalia})",
        coding=[
            Coding.construct(
                system="http://snomed.info/sct",
                code="271299001",
                display="Abnormal clinical finding",
            )
        ],
    )

    notas = []

    if anom.severidad:
        notas.append(f"Severidad: {anom.severidad}")

    if anom.descripcion:
        notas.append(f"Descripción: {anom.descripcion}")

    if anom.patron_detectado:
        notas.append(f"Patrón: {anom.patron_detectado}")

    if anom.requiere_atencion_inmediata:
        notas.append("Requiere atención inmediata.")

    detail_text = " | ".join(notas) if notas else None

    if anom.valores_anormales:
        detail_text = (
            detail_text + " | " if detail_text else ""
        ) + f"Valores anormales: {anom.valores_anormales}"

    return Observation.construct(
        id=str(anom.id),
        status="final",
        category=[category],
        code=code,
        subject=patient_ref,
        effectiveDateTime=anom.created_at.isoformat() if anom.created_at else None,
        note=[{"text": detail_text}] if detail_text else None,
    )


# ---------------------------------------------------------------------
# RecomendacionTratamiento -> FHIR CarePlan & MedicationRequest
# ---------------------------------------------------------------------


def _map_prioridad_to_careplan_status(rec: RecomendacionTratamiento) -> str:
    if rec.aplicado:
        return "completed"
    return "active"


def recc_to_fhir_careplan(rec: RecomendacionTratamiento) -> CarePlan:
    subject = Reference.construct(reference=f"Patient/{rec.paciente_id}")
    author = Reference.construct(reference=f"Practitioner/{rec.medico_id}")

    status = _map_prioridad_to_careplan_status(rec)
    intent = "plan"

    category = [
        CodeableConcept.construct(
            coding=[
                Coding.construct(
                    system="http://terminology.hl7.org/CodeSystem/care-plan-category",
                    code="assess-plan",
                    display="Assessment and Plan",
                )
            ],
            text="Plan de tratamiento",
        )
    ]

    title = (
        f"Plan de tratamiento para {rec.diagnostico_principal}"
        if rec.diagnostico_principal
        else "Plan de tratamiento"
    )

    description = f"Tratamiento recomendado para {rec.diagnostico_principal or 'diagnóstico no especificado'}."

    notes: List[Annotation] = []

    if rec.evidencia_cientifica:
        notes.append(
            Annotation.construct(
                text=f"Evidencia científica: {rec.evidencia_cientifica}"
            )
        )

    if rec.guias_clinicas:
        notes.append(
            Annotation.construct(
                text="Guías clínicas: " + ", ".join(rec.guias_clinicas)
            )
        )

    if rec.contraindicaciones:
        notes.append(
            Annotation.construct(
                text="Contraindicaciones globales: " + "; ".join(rec.contraindicaciones)
            )
        )

    if rec.precauciones:
        notes.append(
            Annotation.construct(
                text="Precauciones globales: " + "; ".join(rec.precauciones)
            )
        )

    activities = []

    for t in rec.terapias_no_farmacologicas or []:
        activities.append(
            {
                "detail": {
                    "kind": "ServiceRequest",
                    "description": t,
                }
            }
        )

    for c in rec.cambios_estilo_vida or []:
        activities.append(
            {
                "detail": {
                    "kind": "ServiceRequest",
                    "description": c,
                }
            }
        )

    return CarePlan.construct(
        id=str(rec.id),
        status=status,
        intent=intent,
        category=category,
        title=title,
        description=description,
        subject=subject,
        author=[author],
        created=rec.created_at.isoformat() if rec.created_at else None,
        activity=activities or None,
        note=notes or None,
    )


def recc_to_fhir_medicationrequests(
    rec: RecomendacionTratamiento,
) -> List[MedicationRequest]:
    meds = rec.medicamentos_sugeridos or []
    if not isinstance(meds, list):
        return []

    subject = Reference.construct(reference=f"Patient/{rec.paciente_id}")
    requester = Reference.construct(reference=f"Practitioner/{rec.medico_id}")
    status = "completed" if rec.aplicado else "active"
    intent = "order"
    authored_on = rec.created_at.isoformat() if rec.created_at else None

    resultado: List[MedicationRequest] = []

    for idx, med in enumerate(meds):
        if not isinstance(med, dict):
            continue

        nombre = (
            med.get("nombre")
            or med.get("nombre_generico")
            or med.get("nombre_comercial")
            or "Medicamento"
        )

        partes = []
        if med.get("dosis"):
            partes.append(f"Dosis: {med['dosis']}")
        if med.get("frecuencia"):
            partes.append(f"Frecuencia: {med['frecuencia']}")
        if med.get("duracion"):
            partes.append(f"Duración: {med['duracion']}")
        if med.get("via_administracion") or med.get("via"):
            partes.append(f"Vía: {med.get('via_administracion') or med.get('via')}")

        instr_text = " | ".join(partes) if partes else None

        dosage = None
        if instr_text:
            dosage = [Dosage.construct(text=instr_text)]

        note_texts = []
        if med.get("indicacion"):
            note_texts.append(f"Indicacion: {med['indicacion']}")
        if med.get("comentarios"):
            note_texts.append(f"Comentarios: {med['comentarios']}")
        if rec.contraindicaciones:
            note_texts.append(
                "Contraindicaciones globales: " + "; ".join(rec.contraindicaciones)
            )
        if rec.precauciones:
            note_texts.append("Precauciones globales: " + "; ".join(rec.precauciones))

        notes = (
            [Annotation.construct(text=nt) for nt in note_texts] if note_texts else None
        )

        mr = MedicationRequest.construct(
            id=f"{rec.id}-{idx}",
            status=status,
            intent=intent,
            subject=subject,
            requester=requester,
            medicationCodeableConcept=CodeableConcept.construct(text=nombre),
            authoredOn=authored_on,
            dosageInstruction=dosage,
            note=notes,
        )

        resultado.append(mr)

    return resultado


# ---------------------------------------------------------------------
# FHIR Patient -> modelo Paciente (update/create)
# ---------------------------------------------------------------------


def apply_fhir_patient_to_paciente(
    resource: FhirPatient, paciente: Paciente
) -> Paciente:
    """Aplica los datos de un Patient FHIR sobre una instancia de Paciente."""

    full_name = None
    if resource.name and len(resource.name) > 0:
        n0 = resource.name[0]
        if n0.text:
            full_name = n0.text
        else:
            given = " ".join(n0.given or [])
            family = n0.family or ""
            full_name = (given + " " + family).strip() or None

    if full_name and hasattr(paciente, "nombre_completo"):
        paciente.nombre_completo = full_name

    if resource.gender and hasattr(paciente, "genero"):
        paciente.genero = resource.gender

    if resource.birthDate and hasattr(paciente, "fecha_nacimiento"):
        paciente.fecha_nacimiento = resource.birthDate

    if resource.identifier:
        for ident in resource.identifier:
            if ident.system == "http://ddx.local/expediente" and ident.value:
                if hasattr(paciente, "numero_expediente"):
                    paciente.numero_expediente = ident.value
                break

    return paciente
