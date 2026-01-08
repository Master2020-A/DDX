"""
Adaptador básico HL7 v2 -> FHIR

Este módulo ilustra cómo transformar mensajes HL7 v2
(en formato texto) a recursos HL7 FHIR usando hl7apy.
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional

# Import opcional de hl7apy (para no tumbar la app si falta)
try:
    from hl7apy.parser import parse_message
except ImportError:
    parse_message = None  # se usará para detectar si la lib no está disponible

from fhir.resources.patient import Patient as FhirPatient
from fhir.resources.observation import Observation as FhirObservation


class HL7v2ToFHIRAdapter:
    """
    Adaptador de mensajes HL7 v2 (por ejemplo ORU^R01) a recursos FHIR.

    Este es solo un esquema base para que puedas ampliarlo según tus necesidades reales.
    """

    def parse_oru_r01(self, hl7_str: str) -> Dict[str, Any]:
        """
        Recibe un mensaje HL7 ORU^R01 en texto y devuelve un dict con recursos FHIR:
        {
          "patient": FhirPatient,
          "observations": [FhirObservation, ...]
        }
        """
        if parse_message is None:
            raise RuntimeError("hl7apy no está instalado en este entorno")

        msg = parse_message(hl7_str)

        patient_resource = self._parse_pid_to_fhir_patient(msg)
        observations = self._parse_obx_to_observations(msg)

        return {
            "patient": patient_resource,
            "observations": observations,
        }

    def _parse_pid_to_fhir_patient(self, msg) -> FhirPatient:
        """Mapea el segmento PID a un recurso FHIR Patient (simplificado)."""
        pid = msg.PID

        identifiers = []
        # Ejemplo: MRN en PID-3 (patient_identifier_list)
        if getattr(pid, "patient_identifier_list", None):
            try:
                mrn = pid.patient_identifier_list[0].cx_1.value
                if mrn:
                    identifiers.append(
                        {"system": "http://hospital.local/mrn", "value": mrn}
                    )
            except Exception:
                pass

        name_text = None
        if getattr(pid, "patient_name", None):
            try:
                pn = pid.patient_name[0]
                family = pn.family_name.fn_1.value if pn.family_name else ""
                given = pn.given_name.value if pn.given_name else ""
                name_text = f"{given} {family}".strip()
            except Exception:
                pass

        gender = None
        try:
            gender_hl7 = (
                pid.administrative_sex.value if pid.administrative_sex else None
            )
            if gender_hl7 in ("M", "F"):
                gender = "male" if gender_hl7 == "M" else "female"
        except Exception:
            pass

        birth_date = None
        try:
            birth_date = (
                pid.date_time_of_birth.ts_1.value if pid.date_time_of_birth else None
            )
        except Exception:
            pass

        resource = FhirPatient.construct(
            identifier=identifiers or None,
            name=[{"text": name_text}] if name_text else None,
            gender=gender,
            birthDate=birth_date,
        )

        return resource

    def _parse_obx_to_observations(self, msg) -> List[FhirObservation]:
        """
        Mapea segmentos OBX del mensaje HL7 a recursos FHIR Observation.

        Aquí devolvemos Observations con código, valor, unidad, rango y flag de anormalidad.
        """
        observations: List[FhirObservation] = []

        # Recorremos todos los hijos y filtramos los que son segmentos OBX
        for child in msg.children:
            if child.name != "OBX":
                continue

            obx = child

            # Tipo de valor
            value_type = getattr(obx, "value_type", None)
            value_type = value_type.value if value_type else None

            # Identificador de la prueba (LOINC, local, etc.)
            obs_id = "Unknown"
            obs_text = "Observation"
            try:
                if getattr(obx, "observation_identifier", None):
                    obs_id = obx.observation_identifier.ce_1.value or "Unknown"
                    obs_text = obx.observation_identifier.ce_2.value or "Observation"
            except Exception:
                pass

            # Valor del resultado
            value = None
            try:
                if getattr(obx, "observation_value", None):
                    if value_type == "NM":
                        value = obx.observation_value[0].data[0].value
                    else:
                        value = str(obx.observation_value[0])
            except Exception:
                pass

            # Unidad (OBX-6)
            unit = None
            try:
                if getattr(obx, "units", None):
                    unit = obx.units.ce_2.value or obx.units.ce_1.value
            except Exception:
                pass

            # Rango de referencia (OBX-7)
            reference_range = None
            try:
                if getattr(obx, "references_range", None):
                    reference_range = obx.references_range.value
            except Exception:
                pass

            # Flag de anormalidad (OBX-8: H, L, etc.)
            abnormal_flag = None
            try:
                if getattr(obx, "abnormal_flags", None):
                    abnormal_flag = obx.abnormal_flags[0].value
            except Exception:
                pass

            note_text = []
            if unit:
                note_text.append(f"Unidad: {unit}")
            if reference_range:
                note_text.append(f"Rango ref: {reference_range}")
            if abnormal_flag:
                note_text.append(f"Flag anormalidad: {abnormal_flag}")

            obs = FhirObservation.construct(
                status="final",
                code={
                    "text": obs_text,
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": obs_id,
                            "display": obs_text,
                        }
                    ],
                },
                valueString=str(value) if value is not None else None,
                note=[{"text": " | ".join(note_text)}] if note_text else None,
            )
            observations.append(obs)

        return observations
