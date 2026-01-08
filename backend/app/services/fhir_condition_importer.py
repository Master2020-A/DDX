"""
Servicio para importar diagnósticos (Condition) desde servidores FHIR externos
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import logging

from app.models.fhir_condition import (
    FHIRCondition,
    ConditionClinicalStatus,
    ConditionVerificationStatus,
)
from app.services.fhir_client import FHIRClient

logger = logging.getLogger(__name__)


class FHIRConditionImporter:
    """Importador de recursos Condition desde servidores FHIR"""

    def __init__(self, db: AsyncSession, fhir_client: FHIRClient):
        self.db = db
        self.fhir_client = fhir_client

    def _parse_codeable_concept(
        self, codeable_concept: Optional[Dict]
    ) -> Optional[Dict]:
        """Parsear CodeableConcept de FHIR"""
        if not codeable_concept:
            return None
        return codeable_concept

    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parsear fecha FHIR a datetime"""
        if not date_str:
            return None

        try:
            # FHIR soporta varios formatos de fecha
            if "T" in date_str:
                # DateTime completo
                return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            else:
                # Solo fecha
                return datetime.strptime(date_str, "%Y-%m-%d")
        except Exception as e:
            logger.warning(f"Error parseando fecha FHIR: {date_str} - {str(e)}")
            return None

    def _map_clinical_status(self, fhir_status: Dict) -> ConditionClinicalStatus:
        """Mapear estado clínico de FHIR a enum local"""
        if not fhir_status or "coding" not in fhir_status:
            return ConditionClinicalStatus.ACTIVE

        code = fhir_status["coding"][0].get("code", "active")

        mapping = {
            "active": ConditionClinicalStatus.ACTIVE,
            "recurrence": ConditionClinicalStatus.RECURRENCE,
            "relapse": ConditionClinicalStatus.RELAPSE,
            "inactive": ConditionClinicalStatus.INACTIVE,
            "remission": ConditionClinicalStatus.REMISSION,
            "resolved": ConditionClinicalStatus.RESOLVED,
        }

        return mapping.get(code, ConditionClinicalStatus.ACTIVE)

    def _map_verification_status(
        self, fhir_status: Dict
    ) -> ConditionVerificationStatus:
        """Mapear estado de verificación de FHIR a enum local"""
        if not fhir_status or "coding" not in fhir_status:
            return ConditionVerificationStatus.CONFIRMED

        code = fhir_status["coding"][0].get("code", "confirmed")

        mapping = {
            "unconfirmed": ConditionVerificationStatus.UNCONFIRMED,
            "provisional": ConditionVerificationStatus.PROVISIONAL,
            "differential": ConditionVerificationStatus.DIFFERENTIAL,
            "confirmed": ConditionVerificationStatus.CONFIRMED,
            "refuted": ConditionVerificationStatus.REFUTED,
            "entered-in-error": ConditionVerificationStatus.ENTERED_IN_ERROR,
        }

        return mapping.get(code, ConditionVerificationStatus.CONFIRMED)

    async def import_condition(
        self,
        fhir_condition: Dict[str, Any],
        patient_id: str,
        encounter_id: Optional[str] = None,
    ) -> FHIRCondition:
        """
        Importar un recurso Condition desde FHIR

        Args:
            fhir_condition: Recurso Condition en formato FHIR JSON
            patient_id: UUID del paciente en el sistema local
            encounter_id: UUID de la consulta (opcional)

        Returns:
            Objeto FHIRCondition creado
        """
        # Extraer datos del recurso FHIR
        fhir_id = fhir_condition.get("id")

        # Estado clínico y verificación
        clinical_status = self._map_clinical_status(
            fhir_condition.get("clinicalStatus")
        )
        verification_status = self._map_verification_status(
            fhir_condition.get("verificationStatus")
        )

        # Código de la condición
        code = self._parse_codeable_concept(fhir_condition.get("code"))

        # Categoría
        category = fhir_condition.get("category", [])

        # Severidad
        severity = self._parse_codeable_concept(fhir_condition.get("severity"))

        # Sitio corporal
        body_site = fhir_condition.get("bodySite", [])

        # Fechas de inicio (onset)
        onset_datetime = None
        onset_string = None
        if "onsetDateTime" in fhir_condition:
            onset_datetime = self._parse_datetime(fhir_condition["onsetDateTime"])
        elif "onsetString" in fhir_condition:
            onset_string = fhir_condition["onsetString"]

        # Fechas de resolución (abatement)
        abatement_datetime = None
        abatement_string = None
        if "abatementDateTime" in fhir_condition:
            abatement_datetime = self._parse_datetime(
                fhir_condition["abatementDateTime"]
            )
        elif "abatementString" in fhir_condition:
            abatement_string = fhir_condition["abatementString"]

        # Fecha de registro
        recorded_date = self._parse_datetime(fhir_condition.get("recordedDate"))

        # Etapa
        stage = fhir_condition.get("stage", [])

        # Evidencia
        evidence = fhir_condition.get("evidence", [])

        # Notas
        note = fhir_condition.get("note", [])

        # Crear objeto FHIRCondition
        condition = FHIRCondition(
            fhir_id=fhir_id,
            fhir_server_url=self.fhir_client.base_url,
            clinical_status=clinical_status,
            verification_status=verification_status,
            category=category,
            severity=severity,
            code=code,
            body_site=body_site,
            subject_id=patient_id,
            encounter_id=encounter_id,
            onset_datetime=onset_datetime,
            onset_string=onset_string,
            abatement_datetime=abatement_datetime,
            abatement_string=abatement_string,
            recorded_date=recorded_date,
            stage=stage,
            evidence=evidence,
            note=note,
            source_system="FHIR",
            fhir_resource=fhir_condition,
        )

        self.db.add(condition)
        await self.db.commit()
        await self.db.refresh(condition)

        logger.info(f"Importado diagnóstico FHIR: {fhir_id} para paciente {patient_id}")

        return condition

    async def import_patient_conditions(
        self,
        fhir_patient_id: str,
        local_patient_id: str,
        clinical_status: Optional[str] = None,
    ) -> List[FHIRCondition]:
        """
        Importar todas las condiciones de un paciente desde FHIR

        Args:
            fhir_patient_id: ID del paciente en el servidor FHIR
            local_patient_id: UUID del paciente en el sistema local
            clinical_status: Filtrar por estado clínico (opcional)

        Returns:
            Lista de condiciones importadas
        """
        # Obtener condiciones desde servidor FHIR
        fhir_conditions = await self.fhir_client.get_patient_conditions(
            fhir_patient_id, clinical_status=clinical_status
        )

        imported_conditions = []

        for fhir_condition in fhir_conditions:
            try:
                condition = await self.import_condition(
                    fhir_condition, local_patient_id
                )
                imported_conditions.append(condition)
            except Exception as e:
                logger.error(f"Error importando condición: {str(e)}")
                continue

        logger.info(
            f"Importadas {len(imported_conditions)} condiciones para paciente {local_patient_id}"
        )

        return imported_conditions

    def extract_diagnosis_info(self, condition: FHIRCondition) -> Dict[str, Any]:
        """
        Extraer información legible del diagnóstico

        Returns:
            Diccionario con información del diagnóstico
        """
        # Extraer código principal
        code_text = "Desconocido"
        code_system = None
        code_value = None

        if condition.code and "coding" in condition.code:
            coding = condition.code["coding"][0]
            code_text = coding.get("display", condition.code.get("text", "Desconocido"))
            code_system = coding.get("system", "")
            code_value = coding.get("code", "")
        elif condition.code and "text" in condition.code:
            code_text = condition.code["text"]

        # Extraer severidad
        severity_text = None
        if condition.severity and "coding" in condition.severity:
            severity_text = condition.severity["coding"][0].get("display")

        # Extraer notas
        notes = []
        if condition.note:
            for note in condition.note:
                if "text" in note:
                    notes.append(note["text"])

        return {
            "id": str(condition.id),
            "diagnosis": code_text,
            "code": code_value,
            "code_system": code_system,
            "clinical_status": condition.clinical_status.value,
            "verification_status": condition.verification_status.value,
            "severity": severity_text,
            "onset_date": (
                condition.onset_datetime.isoformat()
                if condition.onset_datetime
                else condition.onset_string
            ),
            "recorded_date": (
                condition.recorded_date.isoformat() if condition.recorded_date else None
            ),
            "notes": notes,
            "fhir_id": condition.fhir_id,
            "source": condition.fhir_server_url,
        }
