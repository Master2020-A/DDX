"""
Servicio de Pre-diagnóstico Inteligente
Genera sugerencias diagnósticas basadas en síntomas usando IA
"""

from typing import List, Dict, Any
from datetime import datetime
from groq import Groq
import os
import json

from app.schemas.prediagnostico import (
    PreDiagnosticoRequest,
    PreDiagnosticoResponse,
    DiagnosticoDiferencial,
    AlgoritmoDecisionRequest,
    AlgoritmoDecisionResponse,
)


class PreDiagnosticoService:
    """Servicio para generar pre-diagnósticos inteligentes"""

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "❌ GROQ_API_KEY no está configurada. "
                "Agrega GROQ_API_KEY=tu_api_key en el archivo .env"
            )
        self.client = Groq(api_key=api_key)
        # Modelo actualizado - llama-3.1-70b-versatile fue descontinuado
        self.model = "llama-3.3-70b-versatile"

    async def generar_prediagnostico(
        self, request: PreDiagnosticoRequest
    ) -> PreDiagnosticoResponse:
        """
        Genera pre-diagnóstico basado en síntomas
        """
        # Construir prompt para IA
        prompt = self._construir_prompt_prediagnostico(request)

        # Llamar a IA
        respuesta = await self._llamar_ia(prompt)

        # Parsear y estructurar respuesta
        resultado = self._parsear_respuesta_prediagnostico(respuesta)

        return resultado

    async def ejecutar_algoritmo_decision(
        self, request: AlgoritmoDecisionRequest
    ) -> AlgoritmoDecisionResponse:
        """
        Ejecuta algoritmo de decisión clínica
        """
        prompt = self._construir_prompt_algoritmo(request)
        respuesta = await self._llamar_ia(prompt)
        resultado = self._parsear_respuesta_algoritmo(respuesta)
        return resultado

    def _construir_prompt_prediagnostico(self, request: PreDiagnosticoRequest) -> str:
        """Construye prompt para generar pre-diagnóstico"""

        sintomas_texto = "\n".join(
            [
                f"- {s.descripcion}"
                + (f" (Intensidad: {s.intensidad})" if s.intensidad else "")
                + (f" (Duración: {s.duracion})" if s.duracion else "")
                for s in request.sintomas
            ]
        )

        prompt = f"""Eres un asistente médico experto en diagnóstico diferencial. 
Analiza los siguientes síntomas y genera un pre-diagnóstico con diagnósticos diferenciales.

SÍNTOMAS DEL PACIENTE:
{sintomas_texto}

ANTECEDENTES:
{request.antecedentes or 'No especificados'}

MEDICAMENTOS ACTUALES:
{', '.join(request.medicamentos_actuales) if request.medicamentos_actuales else 'Ninguno'}

ALERGIAS:
{', '.join(request.alergias) if request.alergias else 'Ninguna'}

INSTRUCCIONES:
1. Genera 3-5 diagnósticos diferenciales ordenados por probabilidad
2. Para cada diagnóstico incluye:
   - Nombre del diagnóstico
   - Código CIE-10 si aplica
   - Probabilidad estimada (0-100%)
   - Evidencias que lo soportan
   - Síntomas coincidentes
   - Síntomas que faltarían para confirmar
   - Nivel de urgencia (bajo/medio/alto/crítico)
   - Recomendaciones específicas

3. Identifica factores de riesgo relevantes
4. Sugiere exámenes complementarios necesarios
5. Lista signos de alarma a vigilar
6. Proporciona recomendaciones generales
7. Determina el nivel de urgencia global

FORMATO DE RESPUESTA (JSON):
{{
  "diagnosticos_diferenciales": [
    {{
      "nombre": "Nombre del diagnóstico",
      "codigo_cie10": "A00.0",
      "probabilidad": 75.5,
      "evidencias": ["Evidencia 1", "Evidencia 2"],
      "sintomas_coincidentes": ["Síntoma 1", "Síntoma 2"],
      "sintomas_faltantes": ["Síntoma X"],
      "urgencia": "medio",
      "recomendaciones": ["Recomendación 1"]
    }}
  ],
  "sintomas_analizados": ["Lista de síntomas"],
  "factores_riesgo": ["Factor 1", "Factor 2"],
  "examenes_sugeridos": ["Examen 1", "Examen 2"],
  "signos_alarma": ["Signo 1", "Signo 2"],
  "recomendaciones_generales": ["Recomendación 1"],
  "nivel_urgencia": "medio"
}}

Responde ÚNICAMENTE con el JSON, sin texto adicional."""

        return prompt

    def _construir_prompt_algoritmo(self, request: AlgoritmoDecisionRequest) -> str:
        """Construye prompt para algoritmo de decisión clínica"""

        sintomas_texto = "\n".join([f"- {s}" for s in request.sintomas])

        signos_vitales_texto = ""
        if request.signos_vitales:
            signos_vitales_texto = "\n".join(
                [f"- {k}: {v}" for k, v in request.signos_vitales.items()]
            )

        prompt = f"""Eres un médico experto en triaje y decisión clínica de emergencia.
Analiza la siguiente información y determina el curso de acción.

SÍNTOMAS:
{sintomas_texto}

SIGNOS VITALES:
{signos_vitales_texto or 'No disponibles'}

ANTECEDENTES:
{', '.join(request.antecedentes) if request.antecedentes else 'No especificados'}

DATOS DEMOGRÁFICOS:
- Edad: {request.edad or 'No especificada'}
- Sexo: {request.sexo or 'No especificado'}

INSTRUCCIONES:
Determina:
1. Decisión clínica (hospitalizar/ambulatorio/urgente/emergente)
2. Nivel de urgencia (bajo/medio/alto/crítico)
3. Acciones inmediatas a tomar
4. Exámenes prioritarios
5. Diagnósticos más probables
6. Justificación de la decisión
7. Score de gravedad (0-10)

FORMATO DE RESPUESTA (JSON):
{{
  "decision": "Descripción de la decisión",
  "nivel_urgencia": "alto",
  "acciones_inmediatas": ["Acción 1", "Acción 2"],
  "examenes_prioritarios": ["Examen 1", "Examen 2"],
  "diagnosticos_probables": ["Diagnóstico 1", "Diagnóstico 2"],
  "justificacion": "Explicación detallada",
  "score_gravedad": 7.5
}}

Responde ÚNICAMENTE con el JSON."""

        return prompt

    async def _llamar_ia(self, prompt: str) -> str:
        """Llama a la API de Groq"""
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente médico experto. Respondes siempre en formato JSON válido.",
                    },
                    {"role": "user", "content": prompt},
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=4000,
            )

            return chat_completion.choices[0].message.content

        except Exception as e:
            print(f"Error llamando a Groq: {e}")
            raise

    def _parsear_respuesta_prediagnostico(
        self, respuesta: str
    ) -> PreDiagnosticoResponse:
        """Parsea respuesta JSON de IA a PreDiagnosticoResponse"""
        try:
            # Limpiar respuesta si tiene markdown
            respuesta_limpia = respuesta.strip()
            if respuesta_limpia.startswith("```json"):
                respuesta_limpia = respuesta_limpia[7:]
            if respuesta_limpia.startswith("```"):
                respuesta_limpia = respuesta_limpia[3:]
            if respuesta_limpia.endswith("```"):
                respuesta_limpia = respuesta_limpia[:-3]

            data = json.loads(respuesta_limpia.strip())

            # Convertir a objetos Pydantic
            diagnosticos = [
                DiagnosticoDiferencial(**d)
                for d in data.get("diagnosticos_diferenciales", [])
            ]

            return PreDiagnosticoResponse(
                diagnosticos_diferenciales=diagnosticos,
                sintomas_analizados=data.get("sintomas_analizados", []),
                factores_riesgo=data.get("factores_riesgo", []),
                examenes_sugeridos=data.get("examenes_sugeridos", []),
                signos_alarma=data.get("signos_alarma", []),
                recomendaciones_generales=data.get("recomendaciones_generales", []),
                nivel_urgencia=data.get("nivel_urgencia", "medio"),
                timestamp=datetime.now().isoformat(),
            )

        except json.JSONDecodeError as e:
            print(f"Error parseando JSON: {e}")
            print(f"Respuesta recibida: {respuesta}")
            raise ValueError(f"Respuesta de IA no es JSON válido: {e}")

    def _parsear_respuesta_algoritmo(self, respuesta: str) -> AlgoritmoDecisionResponse:
        """Parsea respuesta JSON de algoritmo de decisión"""
        try:
            respuesta_limpia = respuesta.strip()
            if respuesta_limpia.startswith("```json"):
                respuesta_limpia = respuesta_limpia[7:]
            if respuesta_limpia.startswith("```"):
                respuesta_limpia = respuesta_limpia[3:]
            if respuesta_limpia.endswith("```"):
                respuesta_limpia = respuesta_limpia[:-3]

            data = json.loads(respuesta_limpia.strip())

            return AlgoritmoDecisionResponse(**data)

        except json.JSONDecodeError as e:
            print(f"Error parseando JSON: {e}")
            raise ValueError(f"Respuesta de IA no es JSON válido: {e}")
