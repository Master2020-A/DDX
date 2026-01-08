"""
Servicio de Análisis de Interacciones Medicamentosas
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.paciente import Paciente
from app.services.openai_client import chat_completion

logger = logging.getLogger(__name__)


class InteraccionesMedicamentosasService:
    """
    Servicio para analizar interacciones entre medicamentos.

    Firma compatible con ia_medica.py:

        resultado = await service.analizar_interacciones(
            medicamentos=request.medicamentos,
            paciente_id=request.paciente_id,
            db=db,
            incluir_alergias=request.incluir_alergias,
            incluir_condiciones=request.incluir_condiciones,
        )

    Devuelve un dict con las claves que espera el endpoint:

        - medicamentos_analizados: List[str]
        - interacciones_encontradas: List[dict]
        - severidad_maxima: str | None
        - alertas_criticas: List[str]
        - recomendaciones_ajuste: List[str]
        - alergias_consideradas: List[str]
        - condiciones_consideradas: List[str]
        - fuente_datos: str
    """

    NIVELES_SEVERIDAD = {
        "contraindicada": 4,
        "severa": 3,
        "moderada": 2,
        "leve": 1,
    }

    async def analizar_interacciones(
        self,
        medicamentos: List[str],
        paciente_id: UUID,
        db: AsyncSession,
        incluir_alergias: bool = True,
        incluir_condiciones: bool = True,
    ) -> Dict[str, Any]:
        """Analiza interacciones entre medicamentos usando IA."""

        # Validaciones básicas
        meds = [m.strip() for m in medicamentos if m.strip()]
        if len(meds) < 2:
            return {
                "medicamentos_analizados": meds,
                "interacciones_encontradas": [],
                "severidad_maxima": None,
                "alertas_criticas": [
                    "Se requieren al menos 2 medicamentos para analizar interacciones."
                ],
                "recomendaciones_ajuste": [],
                "alergias_consideradas": [],
                "condiciones_consideradas": [],
                "fuente_datos": "IA-Demo",
            }

        # Obtener datos del paciente (alergias / condiciones)
        alergias_consideradas: List[str] = []
        condiciones_consideradas: List[str] = []

        try:
            result = await db.execute(
                select(Paciente).where(Paciente.id == paciente_id)
            )
            paciente: Optional[Paciente] = result.scalar_one_or_none()

            if paciente:
                if incluir_alergias:
                    alergias_consideradas = getattr(paciente, "alergias", []) or []

                if incluir_condiciones:
                    condiciones = getattr(paciente, "diagnosticos", None)
                    if isinstance(condiciones, list):
                        condiciones_consideradas = condiciones
        except Exception as e:
            logger.error(f"Error obteniendo datos del paciente {paciente_id}: {e}")

        # Construir prompt para la IA
        prompt = self._construir_prompt(
            medicamentos=meds,
            alergias=alergias_consideradas,
            condiciones=condiciones_consideradas,
        )

        analisis_ia: Dict[str, Any] = {}
        fuente_datos = "IA-Demo"

        # Llamar a OpenAI (o modo demo) con manejo robusto
        try:
            response = await chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": """Eres un experto en farmacología clínica especializado en interacciones medicamentosas.

Analiza los medicamentos proporcionados y detecta TODAS las interacciones posibles.

Para cada interacción incluye:
1. Medicamentos involucrados
2. Severidad (contraindicada, severa, moderada, leve)
3. Mecanismo de interacción
4. Efectos clínicos esperados
5. Recomendación de manejo

RESPONDE PREFERENTEMENTE EN JSON CON ESTA ESTRUCTURA (si no, se intentará parsear):

{
  "interacciones": [
    {
      "medicamento1": "nombre",
      "medicamento2": "nombre",
      "severidad": "contraindicada|severa|moderada|leve",
      "mecanismo": "descripción del mecanismo",
      "descripcion": "descripción detallada",
      "efectos": ["efecto1", "efecto2"],
      "manejo": "recomendación de manejo"
    }
  ],
  "alertas_criticas": ["alerta1", "alerta2"],
  "recomendaciones_generales": ["recomendación1", "recomendación2"]
}""",
                    },
                    {"role": "user", "content": prompt},
                ],
                model="gpt-4o",
                temperature=0.2,
            )
            content = response.choices[0].message.content
            analisis_ia = self._parse_json_seguro(content) or {}
            fuente_datos = f"OpenAI-{getattr(response, 'model', 'gpt-4o')}"
        except Exception as e:
            logger.error(f"Error llamando a chat_completion en interacciones: {e}")
            analisis_ia = {}

        # Extraer datos con defaults seguros
        interacciones_ia: List[Dict[str, Any]] = []
        if isinstance(analisis_ia, dict):
            interacciones_ia = analisis_ia.get("interacciones") or []
            if not isinstance(interacciones_ia, list):
                interacciones_ia = []

        alertas_criticas: List[str] = []
        if isinstance(analisis_ia, dict):
            ac = analisis_ia.get("alertas_criticas") or []
            if isinstance(ac, list):
                alertas_criticas = [str(x) for x in ac]

        recomendaciones_generales: List[str] = []
        if isinstance(analisis_ia, dict):
            rg = analisis_ia.get("recomendaciones_generales") or []
            if isinstance(rg, list):
                recomendaciones_generales = [str(x) for x in rg]

        severidad_maxima = self._calcular_severidad_maxima(interacciones_ia)

        return {
            "medicamentos_analizados": meds,
            "interacciones_encontradas": interacciones_ia,
            "severidad_maxima": severidad_maxima,
            "alertas_criticas": alertas_criticas,
            "recomendaciones_ajuste": recomendaciones_generales,
            "alergias_consideradas": alergias_consideradas,
            "condiciones_consideradas": condiciones_consideradas,
            "fuente_datos": fuente_datos,
        }

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _construir_prompt(
        self,
        medicamentos: List[str],
        alergias: List[str],
        condiciones: List[str],
    ) -> str:
        """Construye el prompt que se envía a la IA."""

        def _lista(items: List[str], default: str) -> str:
            if not items:
                return f"- {default}"
            return "\n".join(f"- {i}" for i in items)

        return f"""
Analiza las interacciones entre los siguientes medicamentos:

MEDICAMENTOS:
{_lista(medicamentos, "Ninguno")}

ALERGIAS DEL PACIENTE:
{_lista(alergias, "Ninguna conocida")}

CONDICIONES / DIAGNÓSTICOS DEL PACIENTE:
{_lista(condiciones, "No especificadas")}

Indica:
- TODAS las interacciones clínicamente relevantes
- Severidad (contraindicada, severa, moderada o leve)
- Mecanismos y efectos clínicos
- Recomendaciones prácticas de manejo
"""

    def _parse_json_seguro(self, content: str) -> Optional[Dict[str, Any]]:
        """Intenta extraer JSON aunque venga envuelto en markdown u otro texto."""
        if not content:
            return None

        texto = content.strip()

        # Intento 1: directo
        try:
            return json.loads(texto)
        except json.JSONDecodeError:
            pass

        # Intento 2: bloques ```json ... ```
        patrones = [
            r"```json\s*([\s\S]*?)\s*```",
            r"```\s*([\s\S]*?)\s*```",
        ]
        for patron in patrones:
            m = re.search(patron, texto)
            if m:
                posible = m.group(1)
                try:
                    return json.loads(posible)
                except json.JSONDecodeError:
                    continue

        # Intento 3: desde el primer '{' hasta el último '}'
        inicio = texto.find("{")
        fin = texto.rfind("}") + 1
        if inicio != -1 and fin > inicio:
            posible = texto[inicio:fin]
            try:
                return json.loads(posible)
            except json.JSONDecodeError:
                pass

        return None

    def _calcular_severidad_maxima(
        self, interacciones: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Devuelve la severidad máxima entre las interacciones encontradas."""
        max_nivel = 0
        max_nombre: Optional[str] = None

        for inter in interacciones or []:
            sev = str(inter.get("severidad", "")).lower().strip()
            nivel = self.NIVELES_SEVERIDAD.get(sev, 0)
            if nivel > max_nivel:
                max_nivel = nivel
                max_nombre = sev

        return max_nombre
