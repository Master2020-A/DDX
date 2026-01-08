"""
Servicio de Asistente de IA para diagnóstico y consultas médicas
"""

import logging
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models.paciente import Paciente
from app.models.consulta import Consulta
from app.models.laboratorio import PruebaLaboratorio
from app.models.estudios_especiales import EstudioEKG, EstudioEEG, Ecografia
from app.services.openai_client import chat_completion

logger = logging.getLogger(__name__)


class AsistenteIAService:
    """Servicio para el asistente de IA médico."""

    def __init__(self) -> None:
        pass

    async def consultar_asistente(
        self,
        pregunta: str,
        paciente_id: Optional[UUID],
        db: AsyncSession,
        incluir_historial: bool = True,
        incluir_estudios: bool = True,
    ) -> Dict[str, Any]:
        """
        Consultar al asistente de IA con contexto del paciente.

        Devuelve siempre un dict con:
        - respuesta: str
        - contexto_utilizado: dict
        - tokens_utilizados: int
        - modelo: str
        """
        # 1) Construir contexto del paciente
        contexto = await self._construir_contexto(
            paciente_id, db, incluir_historial, incluir_estudios
        )

        # 2) Construir prompt completo
        prompt = self._construir_prompt(pregunta, contexto)

        # 3) Llamar a OpenAI con manejo robusto de errores
        try:
            response = await chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": """Eres un asistente médico experto con amplio conocimiento en medicina clínica.
Tu objetivo es ayudar a médicos con:
- Diagnósticos diferenciales
- Interpretación de estudios
- Recomendaciones de tratamiento
- Análisis de casos clínicos

IMPORTANTE:
- Siempre basa tus respuestas en evidencia científica
- Menciona guías clínicas cuando sea relevante
- Indica el nivel de certeza de tus recomendaciones
- Sugiere estudios adicionales cuando sea necesario
- Recuerda que eres un ASISTENTE, el médico toma la decisión final""",
                    },
                    {"role": "user", "content": prompt},
                ],
                model="gpt-4o",
                temperature=0.3,
            )
        except Exception as e:
            logger.error(f"Error llamando a chat_completion en AsistenteIA: {e}")
            # Respuesta de respaldo si falla la llamada a OpenAI
            return self._respuesta_fallback(pregunta, contexto)

        # 4) Validar respuesta
        if not response or not getattr(response, "choices", None):
            logger.error("Respuesta inválida de chat_completion (sin choices)")
            return self._respuesta_fallback(pregunta, contexto)

        try:
            respuesta = response.choices[0].message.content
        except Exception as e:
            logger.error(f"No se pudo extraer message.content de la respuesta: {e}")
            return self._respuesta_fallback(pregunta, contexto)

        # 5) Extraer tokens utilizados de forma segura (puede no existir usage)
        tokens_utilizados = self._obtener_total_tokens(response)

        return {
            "respuesta": respuesta,
            "contexto_utilizado": contexto,
            "tokens_utilizados": tokens_utilizados,
            "modelo": "gpt-4o",
        }

    def _obtener_total_tokens(self, response: Any) -> int:
        """
        Intenta obtener response.usage.total_tokens de forma robusta.

        - Si el objeto no tiene .usage (como DemoResponse), devuelve 0.
        - Si .usage es dict, usa usage['total_tokens'].
        - Si .usage es objeto, intenta usage.total_tokens.
        """
        try:
            usage = getattr(response, "usage", None)
            if not usage:
                return 0

            # Caso: usage es un dict
            if isinstance(usage, dict):
                return int(usage.get("total_tokens", 0))

            # Caso: usage es un objeto con atributo total_tokens
            return int(getattr(usage, "total_tokens", 0))
        except Exception:
            return 0

    def _respuesta_fallback(
        self, pregunta: str, contexto: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Respuesta de respaldo cuando falla OpenAI o la respuesta viene mal."""
        texto = (
            "No pude procesar tu consulta automáticamente en este momento. "
            "Por favor, reformula la pregunta o intenta nuevamente. "
            "Recuerda que siempre es necesaria la valoración clínica presencial."
        )
        return {
            "respuesta": texto,
            "contexto_utilizado": contexto,
            "tokens_utilizados": 0,
            "modelo": "demo",
        }

    async def _construir_contexto(
        self,
        paciente_id: Optional[UUID],
        db: AsyncSession,
        incluir_historial: bool,
        incluir_estudios: bool,
    ) -> Dict[str, Any]:
        """Construir contexto del paciente para la consulta."""

        if not paciente_id:
            return {}

        contexto: Dict[str, Any] = {}

        # Datos básicos del paciente
        result = await db.execute(select(Paciente).where(Paciente.id == paciente_id))
        paciente = result.scalar_one_or_none()

        if paciente:
            contexto["paciente"] = {
                "edad": getattr(paciente, "edad", None),
                "sexo": getattr(paciente, "genero", None),
                "alergias": getattr(paciente, "alergias", []) or [],
                "antecedentes": [],
            }

        # Historial de consultas recientes
        if incluir_historial:
            result = await db.execute(
                select(Consulta)
                .where(Consulta.paciente_id == paciente_id)
                .order_by(desc(Consulta.fecha_hora))
                .limit(5)
            )
            consultas = result.scalars().all()

            contexto["consultas_recientes"] = [
                {
                    "fecha": c.fecha_hora.isoformat(),
                    "motivo": c.motivo_consulta,
                    "diagnostico": getattr(c, "diagnostico", None),
                    "tratamiento": getattr(c, "plan_tratamiento", None),
                }
                for c in consultas
            ]

        # Estudios recientes
        if incluir_estudios:
            # Laboratorios últimos 90 días
            result = await db.execute(
                select(PruebaLaboratorio)
                .where(PruebaLaboratorio.paciente_id == paciente_id)
                .where(
                    PruebaLaboratorio.fecha_resultado
                    >= datetime.utcnow() - timedelta(days=90)
                )
                .order_by(desc(PruebaLaboratorio.fecha_resultado))
                .limit(10)
            )
            labs = result.scalars().all()

            if labs:
                contexto["laboratorios_recientes"] = [
                    {
                        "fecha": (
                            lab.fecha_resultado.isoformat()
                            if lab.fecha_resultado
                            else lab.fecha_solicitud.isoformat()
                        ),
                        "tipo": lab.tipo_prueba,
                        "estado": lab.estado,
                        "valores_criticos": lab.valores_criticos or [],
                    }
                    for lab in labs
                ]

            # Aquí podrías añadir EKG, EEG, Ecografía, etc. si lo necesitas,
            # usando EstudioEKG, EstudioEEG, Ecografia, etc.

        return contexto

    def _construir_prompt(self, pregunta: str, contexto: Dict[str, Any]) -> str:
        """Construir prompt completo con contexto."""

        prompt_parts: List[str] = []

        if contexto:
            prompt_parts.append("CONTEXTO DEL PACIENTE:")

            if "paciente" in contexto:
                p = contexto["paciente"]
                prompt_parts.append(f"- Edad: {p.get('edad', 'No especificada')}")
                prompt_parts.append(f"- Sexo: {p.get('sexo', 'No especificado')}")

                if p.get("alergias"):
                    prompt_parts.append(f"- Alergias: {', '.join(p['alergias'])}")

                if p.get("antecedentes"):
                    prompt_parts.append(
                        f"- Antecedentes: {', '.join(p['antecedentes'])}"
                    )

            if contexto.get("consultas_recientes"):
                prompt_parts.append("\nCONSULTAS RECIENTES:")
                for c in contexto["consultas_recientes"][:3]:
                    prompt_parts.append(
                        f"- {c['fecha']}: {c['motivo']} → {c.get('diagnostico')}"
                    )

            if contexto.get("laboratorios_recientes"):
                prompt_parts.append("\nLABORATORIOS RECIENTES:")
                for lab in contexto["laboratorios_recientes"][:5]:
                    prompt_parts.append(
                        f"- {lab['fecha']}: {lab['tipo']} - Estado: {lab['estado']}"
                    )

            prompt_parts.append("\n" + "=" * 50 + "\n")

        prompt_parts.append(f"CONSULTA DEL MÉDICO:\n{pregunta}")

        return "\n".join(prompt_parts)

    async def interpretar_estudio(
        self,
        tipo_estudio: str,
        datos_estudio: Dict[str, Any],
        contexto_paciente: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Interpretar un estudio específico (laboratorio, EKG, imagen, etc.)
        """

        prompt = f"""Interpreta el siguiente estudio {tipo_estudio}:

DATOS DEL ESTUDIO:
{self._formatear_datos_estudio(datos_estudio)}
"""

        if contexto_paciente:
            prompt += f"\n\nCONTEXTO DEL PACIENTE:\n{contexto_paciente}"

        prompt += """
Proporciona:
1. Interpretación de los hallazgos
2. Significado clínico
3. Diagnósticos diferenciales si aplica
4. Recomendaciones de seguimiento
5. Estudios adicionales sugeridos si es necesario
"""

        response = await chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": "Eres un médico experto en interpretación de estudios clínicos y de imagen.",
                },
                {"role": "user", "content": prompt},
            ],
            model="gpt-4o",
            temperature=0.3,
        )

        return response.choices[0].message.content

    def _formatear_datos_estudio(self, datos: Dict[str, Any]) -> str:
        """Formatear datos del estudio para el prompt."""
        lines: List[str] = []
        for key, value in datos.items():
            if isinstance(value, dict):
                lines.append(f"{key}:")
                for k, v in value.items():
                    lines.append(f"  - {k}: {v}")
            else:
                lines.append(f"- {key}: {value}")
        return "\n".join(lines)
