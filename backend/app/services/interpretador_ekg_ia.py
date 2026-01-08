"""
Servicio de interpretación avanzada de EKG usando IA (Groq)
"""
from groq import Groq
import os
import json
from typing import Dict, Any


class InterpretadorEKGIA:
    """Interpretador de EKG usando IA de Groq"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    def interpretar_ekg_avanzado(self, parametros: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interpreta EKG usando IA para análisis más profundo
        
        Args:
            parametros: Parámetros del EKG
            
        Returns:
            Dict con interpretación avanzada
        """
        prompt = self._construir_prompt(parametros)
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un cardiólogo experto en interpretación de electrocardiogramas. Analiza los parámetros del EKG y proporciona una interpretación clínica detallada. DEBES responder ÚNICAMENTE en formato JSON válido."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,  # Muy determinista para diagnósticos cardíacos
                response_format={"type": "json_object"}
            )
            
            resultado = json.loads(response.choices[0].message.content)
            return resultado
            
        except Exception as e:
            raise Exception(f"Error al interpretar EKG con IA: {str(e)}")
    
    def _construir_prompt(self, parametros: Dict[str, Any]) -> str:
        """Construye el prompt para la IA"""
        
        prompt = f"""Analiza el siguiente electrocardiograma y proporciona una interpretación clínica detallada.

PARÁMETROS DEL EKG:
"""
        
        # Datos del paciente
        if parametros.get('edad_paciente'):
            prompt += f"- Edad del paciente: {parametros['edad_paciente']} años\n"
        if parametros.get('presion_arterial'):
            prompt += f"- Presión arterial: {parametros['presion_arterial']}\n"
        
        prompt += "\nMEDICIONES:\n"
        
        # Frecuencia cardíaca
        if parametros.get('frecuencia_cardiaca'):
            fc = parametros['frecuencia_cardiaca']
            prompt += f"- Frecuencia cardíaca: {fc} lpm (Normal: 60-100 lpm)\n"
        
        # Ritmo
        if parametros.get('ritmo'):
            prompt += f"- Ritmo: {parametros['ritmo']}\n"
        if parametros.get('ritmo_regular') is not None:
            prompt += f"- Ritmo regular: {'Sí' if parametros['ritmo_regular'] else 'No'}\n"
        
        # Intervalos
        if parametros.get('intervalo_pr'):
            pr = parametros['intervalo_pr']
            prompt += f"- Intervalo PR: {pr} ms (Normal: 120-200 ms)\n"
        
        if parametros.get('duracion_qrs'):
            qrs = parametros['duracion_qrs']
            prompt += f"- Duración QRS: {qrs} ms (Normal: 80-120 ms)\n"
        
        if parametros.get('intervalo_qt'):
            qt = parametros['intervalo_qt']
            prompt += f"- Intervalo QT: {qt} ms\n"
        
        if parametros.get('intervalo_qtc'):
            qtc = parametros['intervalo_qtc']
            prompt += f"- QTc (corregido): {qtc} ms (Normal: 350-450 ms)\n"
        
        # Eje
        if parametros.get('eje_qrs'):
            eje = parametros['eje_qrs']
            prompt += f"- Eje QRS: {eje}° (Normal: -30° a +90°)\n"
        
        # Ondas y segmentos
        if parametros.get('onda_p'):
            prompt += f"- Onda P: {parametros['onda_p']}\n"
        if parametros.get('complejo_qrs'):
            prompt += f"- Complejo QRS: {parametros['complejo_qrs']}\n"
        if parametros.get('segmento_st'):
            prompt += f"- Segmento ST: {parametros['segmento_st']}\n"
        if parametros.get('onda_t'):
            prompt += f"- Onda T: {parametros['onda_t']}\n"
        
        # Hallazgos previos
        if parametros.get('hallazgos'):
            prompt += f"\nHALLAZGOS PRELIMINARES:\n"
            for hallazgo in parametros['hallazgos']:
                prompt += f"- {hallazgo}\n"
        
        # Motivo del estudio
        if parametros.get('motivo'):
            prompt += f"\nMOTIVO DEL ESTUDIO: {parametros['motivo']}\n"
        
        prompt += """

TAREA:
Proporciona una interpretación clínica completa del EKG en formato JSON con la siguiente estructura:

{
  "interpretacion": "Descripción detallada de los hallazgos",
  "diagnostico_principal": "Diagnóstico principal basado en los hallazgos",
  "diagnosticos_secundarios": ["Diagnóstico 1", "Diagnóstico 2"],
  "hallazgos_clave": [
    {
      "parametro": "Nombre del parámetro",
      "valor": "Valor medido",
      "interpretacion": "Normal/Anormal",
      "significado_clinico": "Qué significa este hallazgo"
    }
  ],
  "clasificacion": "normal/anormal_leve/anormal_moderado/anormal_severo",
  "es_critico": false,
  "requiere_atencion_inmediata": false,
  "recomendaciones": [
    "Recomendación 1",
    "Recomendación 2"
  ],
  "estudios_adicionales": ["Estudio 1", "Estudio 2"],
  "diagnosticos_diferenciales": [
    {
      "diagnostico": "Nombre del diagnóstico",
      "probabilidad": "alta/media/baja",
      "criterios": "Criterios que lo soportan"
    }
  ]
}

Sé específico y clínico en tu interpretación. Considera la edad del paciente y el contexto clínico.
"""
        
        return prompt
