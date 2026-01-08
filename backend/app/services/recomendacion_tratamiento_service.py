"""
Servicio de Recomendación de Tratamiento con IA
"""

from __future__ import annotations

import json
import re
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession  # solo para type hints

from app.services.openai_client import chat_completion

logger = logging.getLogger(__name__)


class RecomendacionTratamientoService:
    """
    Genera recomendaciones de tratamiento usando IA (OpenAI).

    Esta implementación:
    - Usa el mismo patrón que AsistenteIAService (chat_completion).
    - Fuerza al modelo a responder en JSON (response_format={"type": "json_object"}).
    - Evita el JSONDecodeError con parseo robusto y un fallback seguro.
    - Mantiene EXACTAMENTE la firma que usas en ia_medica.py.
    """

    async def generar_recomendacion(
        self,
        paciente_id: UUID,
        diagnostico_principal: str,
        codigo_cie10: str,
        sintomas: List[str],
        comorbilidades: List[str],
        db: AsyncSession,  # se mantiene por compatibilidad, aunque aquí no se usa
    ) -> Dict[str, Any]:
        """
        Llamada principal desde el endpoint (ia_medica.py).

        Devuelve un diccionario con las claves que espera ia_medica.py:
        - medicamentos_sugeridos
        - terapias_no_farmacologicas
        - cambios_estilo_vida
        - contraindicaciones
        - precauciones
        - guias_clinicas
        - prioridad
        """
        contexto = {
            "paciente_id": str(paciente_id),
            "diagnostico_principal": diagnostico_principal,
            "codigo_cie10": codigo_cie10,
            "sintomas": sintomas or [],
            "comorbilidades": comorbilidades or [],
        }

        prompt = self._construir_prompt(diagnostico_principal, contexto)

        try:
            response = await chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": """Eres un médico especialista en farmacología clínica y medicina interna.
Generas esquemas de tratamiento basados en guías clínicas y evidencia científica.

OBJETIVO:
- Proponer medicamentos de primera línea apropiados
- Considerar comorbilidades y posibles contraindicaciones
- Sugerir terapias no farmacológicas
- Indicar cambios de estilo de vida
- Priorizar la seguridad del paciente

RESPONDE ÚNICAMENTE con JSON VÁLIDO (sin markdown, sin texto adicional).""",
                    },
                    {"role": "user", "content": prompt},
                ],
                model="gpt-4o",
                temperature=0.3,
                max_tokens=2000,
                # 👇 clave para evitar muchos problemas de parseo
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content

            if not content or not content.strip():
                logger.error(
                    "Respuesta vacía del modelo en recomendación_tratamiento_service"
                )
                data = self._respuesta_fallback(diagnostico_principal)
            else:
                # Intento directo
                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    logger.warning(
                        "Error json.loads directo en recomendación_tratamiento. "
                        f"Contenido (primeros 200 chars): {content[:200]!r}"
                    )
                    data = self._parse_json_seguro(content) or self._respuesta_fallback(
                        diagnostico_principal
                    )

        except Exception as e:
            logger.error(
                f"Error llamando a OpenAI en recomendación_tratamiento_service: {e}"
            )
            data = self._respuesta_fallback(diagnostico_principal)

        # Normalizamos nombre de claves a lo que usa el endpoint
        return {
            "medicamentos_sugeridos": data.get("medicamentos_sugeridos", []),
            "terapias_no_farmacologicas": data.get("terapias_no_farmacologicas", []),
            "cambios_estilo_vida": data.get("cambios_estilo_vida", []),
            "contraindicaciones": data.get("contraindicaciones", []),
            "precauciones": data.get("precauciones", []),
            "guias_clinicas": data.get("guias_clinicas", []),
            "prioridad": data.get("prioridad", "media"),
        }

    def _construir_prompt(
        self, diagnostico_principal: str, contexto: Dict[str, Any]
    ) -> str:
        """Arma el prompt que se envía al modelo."""
        sintomas = contexto.get("sintomas") or []
        comorbilidades = contexto.get("comorbilidades") or []
        codigo = contexto.get("codigo_cie10") or "No especificado"

        def _formatear_lista(items: List[str]) -> str:
            if not items:
                return "- Ninguno especificado"
            return "\n".join(f"- {i}" for i in items)

        return f"""
Genera una recomendación de tratamiento para el siguiente caso:

DIAGNÓSTICO PRINCIPAL:
- {diagnostico_principal}
CÓDIGO CIE-10:
- {codigo}

SÍNTOMAS PRINCIPALES:
{_formatear_lista(sintomas)}

COMORBILIDADES IMPORTANTES:
{_formatear_lista(comorbilidades)}

Ten en cuenta riesgo/beneficio, contraindicaciones y la necesidad de seguimiento.

La respuesta DEBE ser un JSON con esta estructura EXPLÍCITA (no añadas texto fuera del JSON):

{{
  "medicamentos_sugeridos": [
    {{
      "nombre": "nombre genérico del medicamento",
      "via": "oral / IV / IM / etc.",
      "dosis": "ej: 50 mg",
      "frecuencia": "ej: cada 12 horas",
      "duracion": "ej: 7 días",
      "indicacion": "por qué se indica este fármaco",
      "comentarios": "ajustes o precauciones (p.ej. en insuficiencia renal, hepática, etc.)"
    }}
  ],
  "terapias_no_farmacologicas": [
    "medida o terapia no farmacológica 1",
    "medida o terapia 2"
  ],
  "cambios_estilo_vida": [
    "cambio 1",
    "cambio 2"
  ],
  "contraindicaciones": [
    "contraindicación 1",
    "contraindicación 2"
  ],
  "precauciones": [
    "precaución 1",
    "precaución 2"
  ],
  "guias_clinicas": [
    "nombre de la guía o sociedad científica 1",
    "nombre de la guía 2"
  ],
  "prioridad": "inmediata | alta | media | baja"
}}
"""

    def _parse_json_seguro(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Intenta extraer un objeto JSON de un string aunque venga envuelto en markdown
        u otros textos.
        """
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

    def _respuesta_fallback(self, diagnostico_principal: str) -> Dict[str, Any]:
        """
        Respuesta de respaldo si la llamada a IA falla o la respuesta no es parseable.
        No lanza excepción, para no tumbar el endpoint.
        """
        return {
            "medicamentos_sugeridos": [],
            "terapias_no_farmacologicas": [
                "Derivar a consulta presencial con especialista para definir el tratamiento"
            ],
            "cambios_estilo_vida": [
                "Dieta saludable",
                "Ejercicio moderado adaptado a la condición clínica",
                "Evitar tabaco y limitar alcohol",
            ],
            "contraindicaciones": [],
            "precauciones": [
                "Las recomendaciones automáticas no se pudieron generar correctamente.",
                "Es imprescindible valoración médica presencial antes de iniciar tratamiento.",
            ],
            "guias_clinicas": [],
            "prioridad": "media",
        }
