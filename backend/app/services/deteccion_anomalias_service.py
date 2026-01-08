"""
Servicio de Detección de Anomalías en Estudios Médicos
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

from app.models.laboratorio import PruebaLaboratorio
from app.models.estudios_especiales import EstudioEKG, EstudioEEG, Ecografia
from app.services.openai_client import chat_completion


class DeteccionAnomaliasService:
    """Servicio para detección automática de anomalías en estudios"""

    def __init__(self):
        pass

    async def detectar_anomalias_laboratorio(
        self, prueba_id: UUID, db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Detectar anomalías en resultados de laboratorio"""

        result = await db.execute(
            select(PruebaLaboratorio).where(PruebaLaboratorio.id == prueba_id)
        )
        prueba = result.scalar_one_or_none()

        if not prueba:
            return []

        anomalias = []

        # Detectar valores críticos
        if prueba.valores_criticos:
            for param in prueba.valores_criticos:
                anomalias.append(
                    {
                        "tipo_anomalia": "valor_critico",
                        "severidad": "critica",
                        "descripcion": f"Valor crítico detectado: {param}",
                        "valores_anormales": {param: prueba.resultados.get(param)},
                        "requiere_atencion_inmediata": True,
                        "recomendaciones": [
                            "Notificar al médico inmediatamente",
                            "Evaluar al paciente urgentemente",
                            "Considerar repetir el estudio",
                        ],
                    }
                )

        # Detectar valores anormales
        if prueba.valores_anormales:
            for param in prueba.valores_anormales:
                if param not in (prueba.valores_criticos or []):
                    anomalias.append(
                        {
                            "tipo_anomalia": "valor_anormal",
                            "severidad": "moderada",
                            "descripcion": f"Valor fuera de rango: {param}",
                            "valores_anormales": {param: prueba.resultados.get(param)},
                            "requiere_atencion_inmediata": False,
                            "recomendaciones": [
                                "Revisar con el contexto clínico del paciente",
                                "Considerar estudios complementarios",
                            ],
                        }
                    )

        # Análisis con IA para patrones
        if prueba.resultados:
            analisis_ia = await self._analizar_patron_laboratorio(
                prueba.tipo_prueba, prueba.resultados
            )

            if analisis_ia.get("anomalias_detectadas"):
                anomalias.extend(analisis_ia["anomalias_detectadas"])

        return anomalias

    async def detectar_anomalias_ekg(
        self, ekg_id: UUID, db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Detectar anomalías en EKG"""

        result = await db.execute(select(EstudioEKG).where(EstudioEKG.id == ekg_id))
        ekg = result.scalar_one_or_none()

        if not ekg:
            return []

        anomalias = []

        # Detectar arritmias
        if ekg.ritmo and ekg.ritmo != "Sinusal":
            anomalias.append(
                {
                    "tipo_anomalia": "arritmia",
                    "severidad": self._evaluar_severidad_arritmia(ekg.ritmo),
                    "descripcion": f"Ritmo anormal detectado: {ekg.ritmo}",
                    "patron_detectado": ekg.ritmo,
                    "requiere_atencion_inmediata": ekg.ritmo
                    in ["Fibrilación Ventricular", "Taquicardia Ventricular"],
                    "recomendaciones": self._recomendaciones_arritmia(ekg.ritmo),
                }
            )

        # Detectar frecuencia anormal
        if ekg.frecuencia_cardiaca:
            if ekg.frecuencia_cardiaca < 60:
                anomalias.append(
                    {
                        "tipo_anomalia": "bradicardia",
                        "severidad": (
                            "moderada" if ekg.frecuencia_cardiaca > 40 else "severa"
                        ),
                        "descripcion": f"Bradicardia: {ekg.frecuencia_cardiaca} lpm",
                        "valores_anormales": {
                            "frecuencia_cardiaca": ekg.frecuencia_cardiaca
                        },
                        "requiere_atencion_inmediata": ekg.frecuencia_cardiaca < 40,
                    }
                )
            elif ekg.frecuencia_cardiaca > 100:
                anomalias.append(
                    {
                        "tipo_anomalia": "taquicardia",
                        "severidad": (
                            "moderada" if ekg.frecuencia_cardiaca < 150 else "severa"
                        ),
                        "descripcion": f"Taquicardia: {ekg.frecuencia_cardiaca} lpm",
                        "valores_anormales": {
                            "frecuencia_cardiaca": ekg.frecuencia_cardiaca
                        },
                        "requiere_atencion_inmediata": ekg.frecuencia_cardiaca > 150,
                    }
                )

        # Análisis con IA
        if ekg.interpretacion_ia:
            analisis_ia = await self._analizar_ekg_con_ia(ekg)
            if analisis_ia.get("anomalias_adicionales"):
                anomalias.extend(analisis_ia["anomalias_adicionales"])

        return anomalias

    async def detectar_anomalias_imagen(
        self, imagen_id: UUID, tipo_imagen: str, db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Detectar anomalías en imágenes médicas"""

        # Este método se integraría con el servicio de análisis de imágenes existente
        # Por ahora, retornamos estructura básica

        return []

    async def _analizar_patron_laboratorio(
        self, tipo_prueba: str, resultados: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analizar patrones en resultados de laboratorio con IA"""

        prompt = f"""Analiza estos resultados de laboratorio ({tipo_prueba}) y detecta patrones anormales:

RESULTADOS:
{self._formatear_resultados(resultados)}

Identifica:
1. Patrones que sugieran condiciones específicas
2. Combinaciones de valores que sean preocupantes
3. Tendencias anormales
4. Hallazgos incidentales importantes

Formato JSON:
{{
    "anomalias_detectadas": [
        {{
            "tipo_anomalia": "patron_anormal",
            "severidad": "leve/moderada/severa/critica",
            "descripcion": "...",
            "patron_detectado": "...",
            "valores_anormales": {{}},
            "requiere_atencion_inmediata": true/false,
            "recomendaciones": ["..."],
            "estudios_adicionales": ["..."]
        }}
    ],
    "condiciones_sugeridas": ["..."]
}}"""

        response = await chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": "Eres un patólogo clínico experto en interpretación de laboratorios.",
                },
                {"role": "user", "content": prompt},
            ],
            model="gpt-4o",
            temperature=0.2,
            response_format={"type": "json_object"},
        )

        return json.loads(response.choices[0].message.content)

    async def _analizar_ekg_con_ia(self, ekg: EstudioEKG) -> Dict[str, Any]:
        """Análisis adicional de EKG con IA"""

        datos_ekg = {
            "frecuencia_cardiaca": ekg.frecuencia_cardiaca,
            "ritmo": ekg.ritmo,
            "intervalo_pr": ekg.intervalo_pr,
            "complejo_qrs": ekg.complejo_qrs,
            "intervalo_qt": ekg.intervalo_qt,
            "eje_qrs": ekg.eje_qrs,
        }

        prompt = f"""Analiza este EKG y detecta anomalías adicionales:

DATOS:
{self._formatear_resultados(datos_ekg)}

INTERPRETACIÓN PREVIA:
{ekg.interpretacion_ia or "No disponible"}

Identifica anomalías sutiles o patrones que requieran atención.

Formato JSON:
{{
    "anomalias_adicionales": [
        {{
            "tipo_anomalia": "...",
            "severidad": "...",
            "descripcion": "...",
            "requiere_atencion_inmediata": true/false,
            "recomendaciones": ["..."]
        }}
    ]
}}"""

        response = await chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": "Eres un cardiólogo experto en interpretación de electrocardiogramas.",
                },
                {"role": "user", "content": prompt},
            ],
            model="gpt-4o",
            temperature=0.2,
            response_format={"type": "json_object"},
        )

        return json.loads(response.choices[0].message.content)

    def _evaluar_severidad_arritmia(self, ritmo: str) -> str:
        """Evaluar severidad de arritmia"""

        arritmias_criticas = [
            "Fibrilación Ventricular",
            "Taquicardia Ventricular",
            "Asistolia",
        ]
        arritmias_severas = ["Bloqueo AV Completo", "Taquicardia Supraventricular"]
        arritmias_moderadas = ["Fibrilación Auricular", "Flutter Auricular"]

        if ritmo in arritmias_criticas:
            return "critica"
        elif ritmo in arritmias_severas:
            return "severa"
        elif ritmo in arritmias_moderadas:
            return "moderada"
        else:
            return "leve"

    def _recomendaciones_arritmia(self, ritmo: str) -> List[str]:
        """Recomendaciones según tipo de arritmia"""

        recomendaciones_map = {
            "Fibrilación Ventricular": [
                "Reanimación cardiopulmonar inmediata",
                "Desfibrilación urgente",
                "Activar código azul",
            ],
            "Taquicardia Ventricular": [
                "Evaluación urgente",
                "Considerar cardioversión",
                "Monitoreo continuo",
            ],
            "Fibrilación Auricular": [
                "Evaluar anticoagulación",
                "Control de frecuencia o ritmo",
                "Ecocardiograma",
            ],
            "Bloqueo AV Completo": [
                "Evaluación urgente",
                "Considerar marcapasos temporal",
                "Monitoreo continuo",
            ],
        }

        return recomendaciones_map.get(
            ritmo, ["Evaluación cardiológica", "Monitoreo según severidad"]
        )

    def _formatear_resultados(self, resultados: Dict[str, Any]) -> str:
        """Formatear resultados para prompt"""
        lines = []
        for key, value in resultados.items():
            if isinstance(value, dict):
                valor = value.get("valor", value)
            else:
                valor = value
            lines.append(f"- {key}: {valor}")
        return "\n".join(lines)
