"""
Cliente FHIR para conectar con servidores HL7 FHIR externos
Soporta FHIR R4
"""

import httpx
from typing import Optional, Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FHIRClient:
    """Cliente para interactuar con servidores FHIR externos"""

    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        """
        Inicializar cliente FHIR

        Args:
            base_url: URL base del servidor FHIR (ej: https://hapi.fhir.org/baseR4)
            auth_token: Token de autenticación Bearer (opcional)
        """
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self.headers = {
            "Accept": "application/fhir+json",
            "Content-Type": "application/fhir+json",
        }
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"

    async def get_resource(
        self, resource_type: str, resource_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obtener un recurso FHIR por ID

        Args:
            resource_type: Tipo de recurso (Patient, Condition, Observation, etc.)
            resource_id: ID del recurso

        Returns:
            Recurso FHIR en formato JSON o None si no se encuentra
        """
        url = f"{self.base_url}/{resource_type}/{resource_id}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, timeout=30.0)

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    logger.warning(f"Recurso no encontrado: {url}")
                    return None
                else:
                    logger.error(
                        f"Error al obtener recurso: {response.status_code} - {response.text}"
                    )
                    return None

        except Exception as e:
            logger.error(f"Error al conectar con servidor FHIR: {str(e)}")
            return None

    async def search_resources(
        self, resource_type: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Buscar recursos FHIR

        Args:
            resource_type: Tipo de recurso (Patient, Condition, Observation, etc.)
            params: Parámetros de búsqueda (ej: {'patient': '123', 'category': 'encounter-diagnosis'})

        Returns:
            Bundle FHIR con resultados de búsqueda
        """
        url = f"{self.base_url}/{resource_type}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url, headers=self.headers, params=params or {}, timeout=30.0
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(
                        f"Error en búsqueda: {response.status_code} - {response.text}"
                    )
                    return None

        except Exception as e:
            logger.error(f"Error al buscar recursos FHIR: {str(e)}")
            return None

    async def get_patient_conditions(
        self,
        patient_id: str,
        clinical_status: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Obtener todas las condiciones (diagnósticos) de un paciente

        Args:
            patient_id: ID del paciente en el servidor FHIR
            clinical_status: Filtrar por estado clínico (active, resolved, etc.)
            category: Filtrar por categoría (problem-list-item, encounter-diagnosis)

        Returns:
            Lista de recursos Condition
        """
        params = {"patient": patient_id}

        if clinical_status:
            params["clinical-status"] = clinical_status
        if category:
            params["category"] = category

        bundle = await self.search_resources("Condition", params)

        if not bundle or bundle.get("resourceType") != "Bundle":
            return []

        conditions = []
        for entry in bundle.get("entry", []):
            resource = entry.get("resource")
            if resource and resource.get("resourceType") == "Condition":
                conditions.append(resource)

        return conditions

    async def get_patient_observations(
        self,
        patient_id: str,
        category: Optional[str] = None,
        code: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Obtener observaciones de un paciente

        Args:
            patient_id: ID del paciente
            category: Categoría (vital-signs, laboratory, etc.)
            code: Código LOINC
            date_from: Fecha desde (formato YYYY-MM-DD)
            date_to: Fecha hasta (formato YYYY-MM-DD)

        Returns:
            Lista de recursos Observation
        """
        params = {"patient": patient_id}

        if category:
            params["category"] = category
        if code:
            params["code"] = code
        if date_from:
            params["date"] = f"ge{date_from}"
        if date_to:
            if "date" in params:
                params["date"] = f"{params['date']}&le{date_to}"
            else:
                params["date"] = f"le{date_to}"

        bundle = await self.search_resources("Observation", params)

        if not bundle or bundle.get("resourceType") != "Bundle":
            return []

        observations = []
        for entry in bundle.get("entry", []):
            resource = entry.get("resource")
            if resource and resource.get("resourceType") == "Observation":
                observations.append(resource)

        return observations

    async def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Obtener información de un paciente"""
        return await self.get_resource("Patient", patient_id)

    async def search_patients(
        self,
        name: Optional[str] = None,
        identifier: Optional[str] = None,
        birthdate: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Buscar pacientes

        Args:
            name: Nombre del paciente
            identifier: Identificador (ej: número de documento)
            birthdate: Fecha de nacimiento (YYYY-MM-DD)

        Returns:
            Lista de recursos Patient
        """
        params = {}
        if name:
            params["name"] = name
        if identifier:
            params["identifier"] = identifier
        if birthdate:
            params["birthdate"] = birthdate

        bundle = await self.search_resources("Patient", params)

        if not bundle or bundle.get("resourceType") != "Bundle":
            return []

        patients = []
        for entry in bundle.get("entry", []):
            resource = entry.get("resource")
            if resource and resource.get("resourceType") == "Patient":
                patients.append(resource)

        return patients

    async def test_connection(self) -> bool:
        """
        Probar conexión con el servidor FHIR

        Returns:
            True si la conexión es exitosa
        """
        try:
            url = f"{self.base_url}/metadata"
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, timeout=10.0)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Error al probar conexión FHIR: {str(e)}")
            return False


# Servidores FHIR públicos de prueba
PUBLIC_FHIR_SERVERS = {
    "hapi_r4": {
        "name": "HAPI FHIR R4 Public Test Server",
        "url": "https://hapi.fhir.org/baseR4",
        "description": "Servidor público de prueba con datos de ejemplo",
    },
    "smart_health_it": {
        "name": "SMART Health IT",
        "url": "https://launch.smarthealthit.org/v/r4/fhir",
        "description": "Servidor de prueba de SMART on FHIR",
    },
}
