"""
Servicio para Intercambio de Expedientes Clínicos
Implementa la lógica de negocio para compartir información entre instituciones
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.models.interoperabilidad import (
    InstitucionExterna,
    SolicitudIntercambio,
    HistoriaClinicaUnificada,
    ConsentimientoIntercambio,
    LogIntercambio,
    TipoIntercambio,
    EstadoIntercambio,
    ProtocoloIntercambio,
)
from app.models.paciente import Paciente
from app.models.consulta import Consulta
from app.models.laboratorio import PruebaLaboratorio
from app.models.imagenes import ImagenMedica
from app.fhir.mappers import paciente_to_fhir_patient


class ServicioIntercambioExpedientes:
    """
    Servicio para gestionar el intercambio de expedientes clínicos
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def verificar_consentimiento(
        self, paciente_id: UUID, institucion_destino_id: UUID, tipo_datos: str
    ) -> bool:
        """
        Verifica si el paciente ha dado consentimiento para compartir información
        """
        query = select(ConsentimientoIntercambio).where(
            and_(
                ConsentimientoIntercambio.paciente_id == paciente_id,
                ConsentimientoIntercambio.activo == True,
                ConsentimientoIntercambio.revocado == False,
            )
        )

        result = await self.db.execute(query)
        consentimientos = result.scalars().all()

        for consentimiento in consentimientos:
            # Verificar si la institución está autorizada
            if consentimiento.instituciones_autorizadas == ["todas"]:
                instituciones_ok = True
            else:
                instituciones_ok = (
                    str(institucion_destino_id)
                    in consentimiento.instituciones_autorizadas
                )

            # Verificar si el tipo de datos está autorizado
            tipos_ok = tipo_datos in consentimiento.tipos_datos_autorizados

            # Verificar permisos específicos
            permisos_ok = True
            if (
                tipo_datos == "diagnosticos"
                and not consentimiento.puede_compartir_diagnosticos
            ):
                permisos_ok = False
            elif (
                tipo_datos == "laboratorios"
                and not consentimiento.puede_compartir_laboratorios
            ):
                permisos_ok = False
            elif (
                tipo_datos == "imagenes" and not consentimiento.puede_compartir_imagenes
            ):
                permisos_ok = False
            elif tipo_datos == "recetas" and not consentimiento.puede_compartir_recetas:
                permisos_ok = False

            # Verificar vigencia
            vigencia_ok = True
            if consentimiento.fecha_expiracion:
                vigencia_ok = datetime.utcnow() < consentimiento.fecha_expiracion

            if instituciones_ok and tipos_ok and permisos_ok and vigencia_ok:
                return True

        return False

    async def generar_expediente_fhir(
        self,
        paciente_id: UUID,
        incluir_consultas: bool = True,
        incluir_laboratorios: bool = True,
        incluir_imagenes: bool = True,
        periodo_inicio: Optional[datetime] = None,
        periodo_fin: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Genera un expediente completo en formato FHIR Bundle
        """
        # Obtener paciente
        result = await self.db.execute(
            select(Paciente).where(Paciente.id == paciente_id)
        )
        paciente = result.scalar_one_or_none()

        if not paciente:
            raise ValueError("Paciente no encontrado")

        # Crear Bundle FHIR
        bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "timestamp": datetime.utcnow().isoformat(),
            "entry": [],
        }

        # Agregar Patient
        patient_resource = paciente_to_fhir_patient(paciente)
        bundle["entry"].append(
            {
                "fullUrl": f"Patient/{paciente.id}",
                "resource": patient_resource.dict(),
            }
        )

        # Agregar Consultas como Encounters
        if incluir_consultas:
            consultas_query = select(Consulta).where(
                Consulta.paciente_id == paciente_id
            )

            if periodo_inicio:
                consultas_query = consultas_query.where(
                    Consulta.fecha >= periodo_inicio
                )
            if periodo_fin:
                consultas_query = consultas_query.where(Consulta.fecha <= periodo_fin)

            result = await self.db.execute(consultas_query)
            consultas = result.scalars().all()

            for consulta in consultas:
                encounter = self._consulta_to_fhir_encounter(consulta)
                bundle["entry"].append(
                    {
                        "fullUrl": f"Encounter/{consulta.id}",
                        "resource": encounter,
                    }
                )

        # Agregar Laboratorios como Observations
        if incluir_laboratorios:
            labs_query = select(PruebaLaboratorio).where(
                PruebaLaboratorio.paciente_id == paciente_id
            )

            if periodo_inicio:
                labs_query = labs_query.where(
                    PruebaLaboratorio.fecha_realizacion >= periodo_inicio
                )
            if periodo_fin:
                labs_query = labs_query.where(
                    PruebaLaboratorio.fecha_realizacion <= periodo_fin
                )

            result = await self.db.execute(labs_query)
            labs = result.scalars().all()

            for lab in labs:
                observations = self._laboratorio_to_fhir_observations(lab)
                for obs in observations:
                    bundle["entry"].append(
                        {
                            "fullUrl": f"Observation/{obs['id']}",
                            "resource": obs,
                        }
                    )

        # Agregar Imágenes como ImagingStudy
        if incluir_imagenes:
            imagenes_query = select(ImagenMedica).where(
                ImagenMedica.paciente_id == paciente_id
            )

            if periodo_inicio:
                imagenes_query = imagenes_query.where(
                    ImagenMedica.fecha_estudio >= periodo_inicio
                )
            if periodo_fin:
                imagenes_query = imagenes_query.where(
                    ImagenMedica.fecha_estudio <= periodo_fin
                )

            result = await self.db.execute(imagenes_query)
            imagenes = result.scalars().all()

            for imagen in imagenes:
                imaging_study = self._imagen_to_fhir_imagingstudy(imagen)
                bundle["entry"].append(
                    {
                        "fullUrl": f"ImagingStudy/{imagen.id}",
                        "resource": imaging_study,
                    }
                )

        return bundle

    def _consulta_to_fhir_encounter(self, consulta: Consulta) -> Dict[str, Any]:
        """Convierte una Consulta a FHIR Encounter"""
        return {
            "resourceType": "Encounter",
            "id": str(consulta.id),
            "status": "finished",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "AMB",
                "display": "ambulatory",
            },
            "subject": {"reference": f"Patient/{consulta.paciente_id}"},
            "period": {
                "start": consulta.fecha.isoformat() if consulta.fecha else None,
            },
            "reasonCode": (
                [
                    {
                        "text": consulta.motivo_consulta,
                    }
                ]
                if consulta.motivo_consulta
                else []
            ),
            "diagnosis": [
                {
                    "condition": {
                        "display": diag.get("descripcion", ""),
                    },
                    "use": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/diagnosis-role",
                                "code": "AD",
                                "display": "Admission diagnosis",
                            }
                        ]
                    },
                }
                for diag in (consulta.diagnosticos or [])
            ],
        }

    def _laboratorio_to_fhir_observations(
        self, lab: PruebaLaboratorio
    ) -> List[Dict[str, Any]]:
        """Convierte una PruebaLaboratorio a lista de FHIR Observations"""
        observations = []

        for resultado in lab.resultados or []:
            obs = {
                "resourceType": "Observation",
                "id": f"{lab.id}-{resultado.get('parametro', '')}",
                "status": "final",
                "category": [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                                "code": "laboratory",
                                "display": "Laboratory",
                            }
                        ]
                    }
                ],
                "code": {
                    "text": resultado.get("parametro", ""),
                },
                "subject": {"reference": f"Patient/{lab.paciente_id}"},
                "effectiveDateTime": (
                    lab.fecha_realizacion.isoformat() if lab.fecha_realizacion else None
                ),
                "valueQuantity": {
                    "value": resultado.get("valor"),
                    "unit": resultado.get("unidad", ""),
                },
                "referenceRange": (
                    [
                        {
                            "low": {
                                "value": resultado.get("rango_min"),
                            },
                            "high": {
                                "value": resultado.get("rango_max"),
                            },
                        }
                    ]
                    if resultado.get("rango_min") and resultado.get("rango_max")
                    else []
                ),
                "interpretation": [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                                "code": resultado.get("estado", "N"),
                            }
                        ]
                    }
                ],
            }
            observations.append(obs)

        return observations

    def _imagen_to_fhir_imagingstudy(self, imagen: ImagenMedica) -> Dict[str, Any]:
        """Convierte una ImagenMedica a FHIR ImagingStudy"""
        return {
            "resourceType": "ImagingStudy",
            "id": str(imagen.id),
            "status": "available",
            "subject": {"reference": f"Patient/{imagen.paciente_id}"},
            "started": (
                imagen.fecha_estudio.isoformat() if imagen.fecha_estudio else None
            ),
            "modality": [
                {
                    "system": "http://dicom.nema.org/resources/ontology/DCM",
                    "code": imagen.modalidad or "OT",
                }
            ],
            "description": imagen.descripcion,
            "numberOfSeries": 1,
            "numberOfInstances": 1,
            "procedureCode": (
                [
                    {
                        "text": imagen.tipo_estudio,
                    }
                ]
                if imagen.tipo_estudio
                else []
            ),
        }

    async def consolidar_historia_clinica(
        self, paciente_id: UUID, datos_externos: Dict[str, Any], institucion_origen: str
    ) -> None:
        """
        Consolida información externa en la historia clínica unificada
        """
        # Obtener o crear historia unificada
        result = await self.db.execute(
            select(HistoriaClinicaUnificada).where(
                HistoriaClinicaUnificada.paciente_id == paciente_id
            )
        )
        historia = result.scalar_one_or_none()

        if not historia:
            historia = HistoriaClinicaUnificada(paciente_id=paciente_id)
            self.db.add(historia)

        # Actualizar contadores
        if "consultas" in datos_externos:
            historia.consultas_totales += len(datos_externos["consultas"])

        if "hospitalizaciones" in datos_externos:
            historia.hospitalizaciones_totales += len(
                datos_externos["hospitalizaciones"]
            )

        # Consolidar diagnósticos
        if "diagnosticos" in datos_externos:
            diagnosticos_actuales = historia.diagnosticos_activos or []
            for diag in datos_externos["diagnosticos"]:
                if diag not in diagnosticos_actuales:
                    diagnosticos_actuales.append(
                        {
                            **diag,
                            "institucion": institucion_origen,
                            "fecha_consolidacion": datetime.utcnow().isoformat(),
                        }
                    )
            historia.diagnosticos_activos = diagnosticos_actuales

        # Consolidar medicamentos
        if "medicamentos" in datos_externos:
            medicamentos_actuales = historia.medicamentos_actuales or []
            for med in datos_externos["medicamentos"]:
                if med not in medicamentos_actuales:
                    medicamentos_actuales.append(
                        {
                            **med,
                            "institucion": institucion_origen,
                        }
                    )
            historia.medicamentos_actuales = medicamentos_actuales

        # Agregar institución contribuyente
        instituciones = historia.instituciones_contribuyentes or []
        if institucion_origen not in instituciones:
            instituciones.append(institucion_origen)
        historia.instituciones_contribuyentes = instituciones

        # Actualizar timestamp
        historia.ultima_actualizacion_externa = datetime.utcnow()
        historia.updated_at = datetime.utcnow()

        await self.db.commit()

    async def generar_checksum(self, datos: Dict[str, Any]) -> str:
        """
        Genera un checksum SHA-256 para validar integridad de datos
        """
        datos_str = json.dumps(datos, sort_keys=True, default=str)
        return hashlib.sha256(datos_str.encode()).hexdigest()

    async def registrar_log_intercambio(
        self,
        solicitud_id: UUID,
        accion: str,
        protocolo: str,
        direccion: str,
        endpoint: Optional[str] = None,
        codigo_respuesta: Optional[int] = None,
        tiempo_respuesta_ms: Optional[int] = None,
        error: Optional[str] = None,
        usuario_id: Optional[UUID] = None,
    ) -> None:
        """
        Registra un log de auditoría del intercambio
        """
        log = LogIntercambio(
            solicitud_id=solicitud_id,
            accion=accion,
            protocolo=protocolo,
            direccion=direccion,
            endpoint=endpoint,
            codigo_respuesta=codigo_respuesta,
            tiempo_respuesta_ms=tiempo_respuesta_ms,
            error=error,
            usuario_id=usuario_id,
        )
        self.db.add(log)
        await self.db.commit()
