"""
Servicio de Generación Automática de Resúmenes Clínicos
"""

from typing import Dict, Any, Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from datetime import datetime, timedelta
import json
import logging

from app.models.pln import ResumenClinico
from app.models.paciente import Paciente
from app.models.consulta import Consulta
from app.models.laboratorio import PruebaLaboratorio
from app.services.openai_client import chat_completion

logger = logging.getLogger(__name__)


class ResumenClinicoService:
    """Servicio para generar resúmenes automáticos de historias clínicas"""

    async def generar_resumen(
        self,
        paciente_id: UUID,
        medico_id: UUID,
        tipo_resumen: str = "completo",
        periodo_dias: Optional[int] = None,
        incluir_consultas: bool = True,
        incluir_laboratorios: bool = True,
        incluir_imagenes: bool = True,
        incluir_medicamentos: bool = True,
        db: AsyncSession = None,
    ) -> Dict[str, Any]:
        """
        Generar resumen clínico automático

        Args:
            paciente_id: ID del paciente
            medico_id: ID del médico
            tipo_resumen: Tipo (completo, ejecutivo, por_sistema, cronologico)
            periodo_dias: Días hacia atrás (None = todo el historial)
            incluir_consultas: Incluir consultas
            incluir_laboratorios: Incluir laboratorios
            incluir_imagenes: Incluir estudios de imagen
            incluir_medicamentos: Incluir medicamentos
            db: Sesión de base de datos

        Returns:
            Dict con resumen generado
        """

        # Obtener datos del paciente
        datos = await self._recopilar_datos_paciente(
            paciente_id,
            periodo_dias,
            incluir_consultas,
            incluir_laboratorios,
            incluir_imagenes,
            incluir_medicamentos,
            db,
        )

        # Generar resumen con IA
        resumen = await self._generar_resumen_con_ia(datos, tipo_resumen)

        # Guardar en base de datos
        if db:
            periodo_inicio = None
            periodo_fin = datetime.utcnow()

            if periodo_dias:
                periodo_inicio = periodo_fin - timedelta(days=periodo_dias)

            resumen_db = ResumenClinico(
                paciente_id=paciente_id,
                medico_id=medico_id,
                tipo_resumen=tipo_resumen,
                periodo_inicio=periodo_inicio,
                periodo_fin=periodo_fin,
                incluye_consultas=incluir_consultas,
                incluye_laboratorios=incluir_laboratorios,
                incluye_imagenes=incluir_imagenes,
                incluye_medicamentos=incluir_medicamentos,
                resumen_texto=resumen["resumen_texto"],
                resumen_estructurado=resumen["resumen_estructurado"],
                datos_demograficos=resumen.get("datos_demograficos"),
                motivo_consulta_principal=resumen.get("motivo_consulta_principal"),
                antecedentes_relevantes=resumen.get("antecedentes_relevantes"),
                evolucion_clinica=resumen.get("evolucion_clinica"),
                diagnosticos_actuales=resumen.get("diagnosticos_actuales"),
                tratamiento_actual=resumen.get("tratamiento_actual"),
                estudios_pendientes=resumen.get("estudios_pendientes"),
                plan_seguimiento=resumen.get("plan_seguimiento"),
                numero_documentos_analizados=datos["total_documentos"],
                modelo_utilizado="gpt-4o",
            )

            db.add(resumen_db)
            await db.commit()
            await db.refresh(resumen_db)

            resumen["id"] = str(resumen_db.id)

        return resumen

    async def _recopilar_datos_paciente(
        self,
        paciente_id: UUID,
        periodo_dias: Optional[int],
        incluir_consultas: bool,
        incluir_laboratorios: bool,
        incluir_imagenes: bool,
        incluir_medicamentos: bool,
        db: AsyncSession,
    ) -> Dict[str, Any]:
        """Recopilar todos los datos relevantes del paciente"""

        datos = {
            "paciente": {},
            "consultas": [],
            "laboratorios": [],
            "imagenes": [],
            "medicamentos": [],
            "total_documentos": 0,
        }

        # Calcular fecha límite
        fecha_limite = None
        if periodo_dias:
            fecha_limite = datetime.utcnow() - timedelta(days=periodo_dias)

        # Datos del paciente
        result = await db.execute(select(Paciente).where(Paciente.id == paciente_id))
        paciente = result.scalar_one_or_none()

        if paciente:
            datos["paciente"] = {
                "nombre": f"{paciente.nombre} {paciente.apellido_paterno} {paciente.apellido_materno or ''}".strip(),
                "edad": paciente.edad if hasattr(paciente, "edad") else None,
                "sexo": paciente.genero if hasattr(paciente, "genero") else None,
                "fecha_nacimiento": (
                    paciente.fecha_nacimiento.isoformat()
                    if paciente.fecha_nacimiento
                    else None
                ),
                "alergias": paciente.alergias or [],
                "tipo_sangre": (
                    paciente.tipo_sangre if hasattr(paciente, "tipo_sangre") else None
                ),
            }

        # Consultas
        if incluir_consultas:
            query = select(Consulta).where(Consulta.paciente_id == paciente_id)
            if fecha_limite:
                query = query.where(Consulta.fecha_hora >= fecha_limite)
            query = query.order_by(desc(Consulta.fecha_hora))

            result = await db.execute(query)
            consultas = result.scalars().all()

            datos["consultas"] = [
                {
                    "fecha": c.fecha_hora.isoformat(),
                    "motivo": c.motivo_consulta,
                    "sintomas": c.sintomas if hasattr(c, "sintomas") else None,
                    "diagnostico": c.diagnostico if hasattr(c, "diagnostico") else None,
                    "tratamiento": (
                        c.plan_tratamiento if hasattr(c, "plan_tratamiento") else None
                    ),
                    "signos_vitales": {
                        "presion_arterial": (
                            f"{c.presion_sistolica}/{c.presion_diastolica}"
                            if hasattr(c, "presion_sistolica")
                            else None
                        ),
                        "frecuencia_cardiaca": (
                            c.frecuencia_cardiaca
                            if hasattr(c, "frecuencia_cardiaca")
                            else None
                        ),
                        "temperatura": (
                            c.temperatura if hasattr(c, "temperatura") else None
                        ),
                        "peso": c.peso if hasattr(c, "peso") else None,
                    },
                }
                for c in consultas
            ]
            datos["total_documentos"] += len(consultas)

        # Laboratorios
        if incluir_laboratorios:
            query = select(PruebaLaboratorio).where(
                PruebaLaboratorio.paciente_id == paciente_id
            )
            if fecha_limite:
                query = query.where(PruebaLaboratorio.fecha_resultado >= fecha_limite)
            query = query.order_by(desc(PruebaLaboratorio.fecha_resultado))

            result = await db.execute(query)
            laboratorios = result.scalars().all()

            datos["laboratorios"] = [
                {
                    "fecha": lab.fecha_resultado.isoformat(),
                    "area": lab.area,
                    "tipo": lab.tipo_prueba,
                    "resultados": lab.resultados,
                    "valores_anormales": lab.valores_anormales or [],
                    "valores_criticos": lab.valores_criticos or [],
                    "interpretacion": (
                        lab.interpretacion_ia
                        if hasattr(lab, "interpretacion_ia")
                        else None
                    ),
                }
                for lab in laboratorios
            ]
            datos["total_documentos"] += len(laboratorios)

        return datos

    async def _generar_resumen_con_ia(
        self, datos: Dict[str, Any], tipo_resumen: str
    ) -> Dict[str, Any]:
        """Generar resumen usando IA"""

        prompt = f"""Genera un resumen clínico {tipo_resumen} basado en la siguiente información del paciente:

DATOS DEL PACIENTE:
{json.dumps(datos["paciente"], indent=2, ensure_ascii=False)}

NÚMERO DE CONSULTAS: {len(datos["consultas"])}
NÚMERO DE LABORATORIOS: {len(datos["laboratorios"])}

CONSULTAS RECIENTES:
{json.dumps(datos["consultas"][:5], indent=2, ensure_ascii=False)}

LABORATORIOS RECIENTES:
{json.dumps(datos["laboratorios"][:5], indent=2, ensure_ascii=False)}

Genera un resumen clínico que incluya:

1. **DATOS DEMOGRÁFICOS**: Resumen de datos básicos del paciente

2. **MOTIVO DE CONSULTA PRINCIPAL**: Motivo más frecuente o relevante

3. **ANTECEDENTES RELEVANTES**: 
   - Alergias
   - Enfermedades crónicas
   - Cirugías previas
   - Antecedentes familiares importantes

4. **EVOLUCIÓN CLÍNICA**: Cronología de eventos médicos importantes

5. **DIAGNÓSTICOS ACTUALES**: Diagnósticos activos y su estado

6. **TRATAMIENTO ACTUAL**:
   - Medicamentos
   - Terapias no farmacológicas
   - Cambios en estilo de vida

7. **ESTUDIOS PENDIENTES**: Estudios sugeridos pero no realizados

8. **PLAN DE SEGUIMIENTO**: Recomendaciones para seguimiento

IMPORTANTE: Responde SOLO con JSON válido.

Formato JSON:
{{
    "resumen_texto": "Resumen narrativo completo en párrafos...",
    "resumen_estructurado": {{
        "datos_demograficos": {{}},
        "motivo_consulta_principal": "...",
        "antecedentes_relevantes": [],
        "evolucion_clinica": "...",
        "diagnosticos_actuales": [],
        "tratamiento_actual": [],
        "estudios_pendientes": [],
        "plan_seguimiento": "..."
    }}
}}"""

        try:
            response = await chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": """Eres un médico experto en elaboración de resúmenes clínicos.
Genera resúmenes concisos, precisos y bien estructurados.
Prioriza información clínicamente relevante.
Usa lenguaje médico apropiado pero claro.
IMPORTANTE: Responde SOLO con JSON válido.""",
                    },
                    {"role": "user", "content": prompt},
                ],
                model="gpt-4o",
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            raw_content = response.choices[0].message.content

            try:
                resultado = json.loads(raw_content)

                # Extraer campos individuales del resumen estructurado
                resumen_est = resultado.get("resumen_estructurado", {})

                return {
                    "resumen_texto": resultado.get("resumen_texto", ""),
                    "resumen_estructurado": resumen_est,
                    "datos_demograficos": resumen_est.get("datos_demograficos"),
                    "motivo_consulta_principal": resumen_est.get(
                        "motivo_consulta_principal"
                    ),
                    "antecedentes_relevantes": resumen_est.get(
                        "antecedentes_relevantes"
                    ),
                    "evolucion_clinica": resumen_est.get("evolucion_clinica"),
                    "diagnosticos_actuales": resumen_est.get("diagnosticos_actuales"),
                    "tratamiento_actual": resumen_est.get("tratamiento_actual"),
                    "estudios_pendientes": resumen_est.get("estudios_pendientes"),
                    "plan_seguimiento": resumen_est.get("plan_seguimiento"),
                }

            except json.JSONDecodeError:
                logger.error(f"Error parseando JSON: {raw_content[:500]}")
                return self._resumen_vacio()

        except Exception as e:
            logger.error(f"Error generando resumen: {str(e)}")
            return self._resumen_vacio()

    def _resumen_vacio(self) -> Dict[str, Any]:
        """Resumen vacío de fallback"""
        return {
            "resumen_texto": "No se pudo generar el resumen automáticamente.",
            "resumen_estructurado": {},
            "datos_demograficos": {},
            "motivo_consulta_principal": None,
            "antecedentes_relevantes": [],
            "evolucion_clinica": None,
            "diagnosticos_actuales": [],
            "tratamiento_actual": [],
            "estudios_pendientes": [],
            "plan_seguimiento": None,
        }

    async def obtener_resumenes_paciente(
        self, paciente_id: UUID, db: AsyncSession, limite: int = 5
    ) -> List[Dict[str, Any]]:
        """Obtener resúmenes previos de un paciente"""

        result = await db.execute(
            select(ResumenClinico)
            .where(
                and_(
                    ResumenClinico.paciente_id == paciente_id,
                    ResumenClinico.es_version_actual == True,
                )
            )
            .order_by(desc(ResumenClinico.created_at))
            .limit(limite)
        )

        resumenes = result.scalars().all()

        return [
            {
                "id": str(r.id),
                "tipo": r.tipo_resumen,
                "fecha": r.created_at.isoformat(),
                "resumen_texto": (
                    r.resumen_texto[:500] + "..."
                    if len(r.resumen_texto) > 500
                    else r.resumen_texto
                ),
                "periodo": {
                    "inicio": (
                        r.periodo_inicio.isoformat() if r.periodo_inicio else None
                    ),
                    "fin": r.periodo_fin.isoformat() if r.periodo_fin else None,
                },
            }
            for r in resumenes
        ]
