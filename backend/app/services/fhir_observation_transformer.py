from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.models.fhir_observation import (
    FHIRObservation,
    ObservationStatus,
    ObservationCategory,
)
from app.schemas.fhir_observation import (
    CodeableConcept,
    Coding,
    Quantity,
    Reference,
    ReferenceRange,
    Annotation,
    ObservationComponent,
)


class FHIRObservationTransformer:
    """
    Transformador para convertir datos del sistema a recursos FHIR Observation
    """

    # Mapeo de códigos LOINC comunes
    LOINC_CODES = {
        # Signos vitales
        "presion_arterial_sistolica": {
            "code": "8480-6",
            "display": "Systolic blood pressure",
        },
        "presion_arterial_diastolica": {
            "code": "8462-4",
            "display": "Diastolic blood pressure",
        },
        "frecuencia_cardiaca": {"code": "8867-4", "display": "Heart rate"},
        "frecuencia_respiratoria": {"code": "9279-1", "display": "Respiratory rate"},
        "temperatura": {"code": "8310-5", "display": "Body temperature"},
        "saturacion_oxigeno": {"code": "2708-6", "display": "Oxygen saturation"},
        "peso": {"code": "29463-7", "display": "Body weight"},
        "talla": {"code": "8302-2", "display": "Body height"},
        "imc": {"code": "39156-5", "display": "Body mass index"},
        # Hematología
        "hemoglobina": {"code": "718-7", "display": "Hemoglobin"},
        "hematocrito": {"code": "4544-3", "display": "Hematocrit"},
        "leucocitos": {"code": "6690-2", "display": "Leukocytes"},
        "plaquetas": {"code": "777-3", "display": "Platelets"},
        "eritrocitos": {"code": "789-8", "display": "Erythrocytes"},
        # Química clínica
        "glucosa": {"code": "2345-7", "display": "Glucose"},
        "creatinina": {"code": "2160-0", "display": "Creatinine"},
        "urea": {"code": "3094-0", "display": "Urea nitrogen"},
        "acido_urico": {"code": "3084-1", "display": "Uric acid"},
        "colesterol_total": {"code": "2093-3", "display": "Cholesterol"},
        "trigliceridos": {"code": "2571-8", "display": "Triglyceride"},
        "hdl": {"code": "2085-9", "display": "HDL Cholesterol"},
        "ldl": {"code": "2089-1", "display": "LDL Cholesterol"},
        "tgo": {"code": "1920-8", "display": "Aspartate aminotransferase"},
        "tgp": {"code": "1742-6", "display": "Alanine aminotransferase"},
        "bilirrubina_total": {"code": "1975-2", "display": "Bilirubin.total"},
        "fosfatasa_alcalina": {"code": "6768-6", "display": "Alkaline phosphatase"},
    }

    # Rangos de referencia comunes
    REFERENCE_RANGES = {
        "hemoglobina": {"low": 12.0, "high": 16.0, "unit": "g/dL"},
        "glucosa": {"low": 70.0, "high": 100.0, "unit": "mg/dL"},
        "creatinina": {"low": 0.6, "high": 1.2, "unit": "mg/dL"},
        "colesterol_total": {"low": 0.0, "high": 200.0, "unit": "mg/dL"},
        "frecuencia_cardiaca": {"low": 60, "high": 100, "unit": "bpm"},
        "presion_arterial_sistolica": {"low": 90, "high": 120, "unit": "mmHg"},
        "presion_arterial_diastolica": {"low": 60, "high": 80, "unit": "mmHg"},
        "temperatura": {"low": 36.0, "high": 37.5, "unit": "Cel"},
        "saturacion_oxigeno": {"low": 95, "high": 100, "unit": "%"},
    }

    @staticmethod
    def crear_codeable_concept(
        code: str, display: str, system: str = "http://loinc.org"
    ) -> dict:
        """Crear un CodeableConcept FHIR"""
        return {
            "coding": [{"system": system, "code": code, "display": display}],
            "text": display,
        }

    @staticmethod
    def crear_quantity(
        value: float,
        unit: str,
        system: str = "http://unitsofmeasure.org",
        code: str = None,
    ) -> dict:
        """Crear una Quantity FHIR"""
        return {"value": value, "unit": unit, "system": system, "code": code or unit}

    @staticmethod
    def crear_reference_range(low: float, high: float, unit: str) -> dict:
        """Crear un rango de referencia"""
        return {
            "low": {
                "value": low,
                "unit": unit,
                "system": "http://unitsofmeasure.org",
                "code": unit,
            },
            "high": {
                "value": high,
                "unit": unit,
                "system": "http://unitsofmeasure.org",
                "code": unit,
            },
        }

    @classmethod
    def from_signo_vital(
        cls,
        nombre_parametro: str,
        valor: float,
        unidad: str,
        paciente_id: UUID,
        consulta_id: Optional[UUID] = None,
        fecha: Optional[datetime] = None,
        medico_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """
        Transformar un signo vital a Observation FHIR
        """
        # Obtener código LOINC
        loinc_info = cls.LOINC_CODES.get(nombre_parametro.lower().replace(" ", "_"))

        if not loinc_info:
            # Código genérico si no está mapeado
            code = {"text": nombre_parametro}
        else:
            code = cls.crear_codeable_concept(loinc_info["code"], loinc_info["display"])

        # Crear observación
        observation_data = {
            "status": ObservationStatus.FINAL,
            "category": ["vital-signs"],
            "code": code,
            "subject_type": "Patient",
            "subject_id": paciente_id,
            "encounter_id": consulta_id,
            "effective_datetime": fecha or datetime.utcnow(),
            "value_quantity": cls.crear_quantity(valor, unidad),
            "source_type": "signo_vital",
        }

        # Agregar rango de referencia si existe
        ref_range = cls.REFERENCE_RANGES.get(nombre_parametro.lower().replace(" ", "_"))
        if ref_range:
            observation_data["reference_range"] = [
                cls.crear_reference_range(
                    ref_range["low"], ref_range["high"], ref_range["unit"]
                )
            ]

            # Agregar interpretación
            if valor < ref_range["low"]:
                observation_data["interpretation"] = [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                                "code": "L",
                                "display": "Low",
                            }
                        ]
                    }
                ]
            elif valor > ref_range["high"]:
                observation_data["interpretation"] = [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                                "code": "H",
                                "display": "High",
                            }
                        ]
                    }
                ]
            else:
                observation_data["interpretation"] = [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                                "code": "N",
                                "display": "Normal",
                            }
                        ]
                    }
                ]

        # Agregar performer si hay médico
        if medico_id:
            observation_data["performer"] = [
                {"reference": f"Practitioner/{medico_id}", "type": "Practitioner"}
            ]

        return observation_data

    @classmethod
    def from_parametro_laboratorio(
        cls,
        nombre_parametro: str,
        valor: float,
        unidad: str,
        paciente_id: UUID,
        prueba_id: UUID,
        fecha: datetime,
        medico_id: Optional[UUID] = None,
        interpretacion: Optional[str] = None,
        estado_anormal: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Transformar un parámetro de laboratorio a Observation FHIR
        """
        # Normalizar nombre del parámetro
        param_key = (
            nombre_parametro.lower()
            .replace(" ", "_")
            .replace("á", "a")
            .replace("é", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
        )

        # Obtener código LOINC
        loinc_info = cls.LOINC_CODES.get(param_key)

        if not loinc_info:
            code = {"text": nombre_parametro}
        else:
            code = cls.crear_codeable_concept(loinc_info["code"], loinc_info["display"])

        # Crear observación
        observation_data = {
            "status": ObservationStatus.FINAL,
            "category": ["laboratory"],
            "code": code,
            "subject_type": "Patient",
            "subject_id": paciente_id,
            "effective_datetime": fecha,
            "issued": datetime.utcnow(),
            "value_quantity": cls.crear_quantity(valor, unidad),
            "source_type": "laboratorio",
            "source_id": prueba_id,
        }

        # Agregar rango de referencia
        ref_range = cls.REFERENCE_RANGES.get(param_key)
        if ref_range:
            observation_data["reference_range"] = [
                cls.crear_reference_range(
                    ref_range["low"], ref_range["high"], ref_range["unit"]
                )
            ]

        # Agregar interpretación basada en estado
        if estado_anormal:
            if estado_anormal.lower() == "bajo":
                observation_data["interpretation"] = [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                                "code": "L",
                                "display": "Low",
                            }
                        ]
                    }
                ]
            elif estado_anormal.lower() == "alto":
                observation_data["interpretation"] = [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                                "code": "H",
                                "display": "High",
                            }
                        ]
                    }
                ]
            elif estado_anormal.lower() == "critico":
                observation_data["interpretation"] = [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                                "code": "AA",
                                "display": "Critical abnormal",
                            }
                        ]
                    }
                ]
        else:
            # Si no hay estado anormal, asumir normal
            observation_data["interpretation"] = [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                            "code": "N",
                            "display": "Normal",
                        }
                    ]
                }
            ]

        # Agregar nota con interpretación IA si existe
        if interpretacion:
            observation_data["note"] = [
                {"text": interpretacion, "time": datetime.utcnow().isoformat()}
            ]

        # Agregar performer
        if medico_id:
            observation_data["performer"] = [
                {"reference": f"Practitioner/{medico_id}", "type": "Practitioner"}
            ]

        return observation_data

    @classmethod
    def from_presion_arterial(
        cls,
        sistolica: float,
        diastolica: float,
        paciente_id: UUID,
        consulta_id: Optional[UUID] = None,
        fecha: Optional[datetime] = None,
        medico_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """
        Crear Observation multi-componente para presión arterial
        """
        code = cls.crear_codeable_concept(
            "85354-9", "Blood pressure panel", "http://loinc.org"
        )

        # Componentes
        components = [
            {
                "code": cls.crear_codeable_concept("8480-6", "Systolic blood pressure"),
                "valueQuantity": cls.crear_quantity(sistolica, "mmHg"),
            },
            {
                "code": cls.crear_codeable_concept(
                    "8462-4", "Diastolic blood pressure"
                ),
                "valueQuantity": cls.crear_quantity(diastolica, "mmHg"),
            },
        ]

        observation_data = {
            "status": ObservationStatus.FINAL,
            "category": ["vital-signs"],
            "code": code,
            "subject_type": "Patient",
            "subject_id": paciente_id,
            "encounter_id": consulta_id,
            "effective_datetime": fecha or datetime.utcnow(),
            "component": components,
            "source_type": "signo_vital",
        }

        # Interpretación
        if sistolica > 140 or diastolica > 90:
            observation_data["interpretation"] = [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                            "code": "H",
                            "display": "High",
                        }
                    ],
                    "text": "Hipertensión",
                }
            ]
        elif sistolica < 90 or diastolica < 60:
            observation_data["interpretation"] = [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                            "code": "L",
                            "display": "Low",
                        }
                    ],
                    "text": "Hipotensión",
                }
            ]
        else:
            observation_data["interpretation"] = [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                            "code": "N",
                            "display": "Normal",
                        }
                    ]
                }
            ]

        if medico_id:
            observation_data["performer"] = [
                {"reference": f"Practitioner/{medico_id}", "type": "Practitioner"}
            ]

        return observation_data

    @classmethod
    def crear_bundle_observations(cls, observations: List[FHIRObservation]) -> dict:
        """
        Crear un Bundle FHIR con múltiples Observations
        """
        entries = []

        for obs in observations:
            entries.append(
                {"fullUrl": f"Observation/{obs.id}", "resource": obs.to_fhir_dict()}
            )

        return {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": len(observations),
            "entry": entries,
        }
