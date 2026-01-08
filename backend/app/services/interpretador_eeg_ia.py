"""
Servicio de interpretación avanzada de EEG usando IA (Groq)
"""
from groq import Groq
import os
import json
from typing import Dict, Any


class InterpretadorEEGIA:
    """Interpretador de EEG usando IA de Groq"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    def interpretar_eeg_avanzado(self, parametros: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interpreta EEG usando IA para análisis más profundo
        
        Args:
            parametros: Parámetros del EEG
            
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
                        "content": "Eres un neurólogo experto en interpretación de electroencefalogramas. Analiza los parámetros del EEG y proporciona una interpretación clínica detallada. DEBES responder ÚNICAMENTE en formato JSON válido."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            resultado = json.loads(response.choices[0].message.content)
            return resultado
            
        except Exception as e:
            raise Exception(f"Error al interpretar EEG con IA: {str(e)}")
    
    def _construir_prompt(self, parametros: Dict[str, Any]) -> str:
        """Construye el prompt para la IA"""
        
        prompt = f"""Analiza el siguiente electroencefalograma y proporciona una interpretación neurológica detallada.

PARÁMETROS DEL EEG:
"""
        
        # Datos del paciente
        if parametros.get('edad_paciente'):
            prompt += f"- Edad del paciente: {parametros['edad_paciente']} años\n"
        if parametros.get('medicamentos_actuales'):
            prompt += f"- Medicamentos: {parametros['medicamentos_actuales']}\n"
        
        # Tipo de estudio
        if parametros.get('tipo_estudio'):
            prompt += f"\nTIPO DE ESTUDIO: {parametros['tipo_estudio']}\n"
        if parametros.get('duracion_minutos'):
            prompt += f"Duración: {parametros['duracion_minutos']} minutos\n"
        
        # Condiciones
        if parametros.get('estado_conciencia'):
            prompt += f"Estado de conciencia: {parametros['estado_conciencia']}\n"
        if parametros.get('cooperacion_paciente'):
            prompt += f"Cooperación: {parametros['cooperacion_paciente']}\n"
        
        prompt += "\nACTIVIDAD CEREBRAL:\n"
        
        # Actividad de fondo
        if parametros.get('actividad_fondo'):
            prompt += f"- Actividad de fondo: {parametros['actividad_fondo']}\n"
        if parametros.get('frecuencia_dominante'):
            prompt += f"- Frecuencia dominante: {parametros['frecuencia_dominante']} Hz\n"
        if parametros.get('amplitud_promedio'):
            prompt += f"- Amplitud promedio: {parametros['amplitud_promedio']} μV (Normal: 10-100 μV)\n"
        
        # Simetría y reactividad
        if parametros.get('simetria'):
            prompt += f"- Simetría: {parametros['simetria']}\n"
        if parametros.get('reactividad'):
            prompt += f"- Reactividad: {parametros['reactividad']}\n"
        
        # Ritmos cerebrales
        prompt += "\nRITMOS CEREBRALES:\n"
        if parametros.get('ritmo_alfa'):
            prompt += f"- Alfa (8-13 Hz): {parametros['ritmo_alfa']}\n"
        if parametros.get('ritmo_beta'):
            prompt += f"- Beta (13-30 Hz): {parametros['ritmo_beta']}\n"
        if parametros.get('ritmo_theta'):
            prompt += f"- Theta (4-8 Hz): {parametros['ritmo_theta']}\n"
        if parametros.get('ritmo_delta'):
            prompt += f"- Delta (0.5-4 Hz): {parametros['ritmo_delta']}\n"
        
        # Hallazgos anormales
        hallazgos_anormales = []
        if parametros.get('ondas_agudas'):
            hallazgos_anormales.append("Ondas agudas presentes")
        if parametros.get('espigas'):
            hallazgos_anormales.append("Espigas presentes")
        if parametros.get('complejos_punta_onda'):
            hallazgos_anormales.append("Complejos punta-onda presentes")
        if parametros.get('actividad_paroxistica'):
            hallazgos_anormales.append("Actividad paroxística presente")
        
        if hallazgos_anormales:
            prompt += f"\nHALLAZGOS ANORMALES:\n"
            for hallazgo in hallazgos_anormales:
                prompt += f"- {hallazgo}\n"
        
        # Localización
        if parametros.get('localizacion_hallazgos'):
            prompt += f"\nLOCALIZACIÓN: {', '.join(parametros['localizacion_hallazgos'])}\n"
        if parametros.get('lateralidad'):
            prompt += f"Lateralidad: {parametros['lateralidad']}\n"
        
        # Pruebas de activación
        if parametros.get('fotoestimulacion'):
            prompt += f"\nFotoestimulación: {parametros['fotoestimulacion']}\n"
        if parametros.get('hiperventilacion'):
            prompt += f"Hiperventilación: {parametros['hiperventilacion']}\n"
        
        # Motivo del estudio
        if parametros.get('motivo'):
            prompt += f"\nMOTIVO DEL ESTUDIO: {parametros['motivo']}\n"
        
        prompt += """

TAREA:
Proporciona una interpretación neurológica completa del EEG en formato JSON con la siguiente estructura:

{
  "interpretacion": "Descripción detallada de los hallazgos neurológicos",
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
  "riesgo_epileptico": "bajo/moderado/alto",
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
  ],
  "consideraciones_tratamiento": ["Consideración 1", "Consideración 2"]
}

Sé específico y clínico en tu interpretación. Considera la edad del paciente y el contexto clínico.
"""
        
        return prompt
