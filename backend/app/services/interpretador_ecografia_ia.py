"""
Servicio de interpretación avanzada de Ecografías usando IA (Groq)
"""
from groq import Groq
import os
import json
from typing import Dict, Any


class InterpretadorEcografiaIA:
    """Interpretador de Ecografías usando IA de Groq"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    def interpretar_ecografia_avanzado(self, parametros: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interpreta Ecografía usando IA para análisis más profundo
        
        Args:
            parametros: Parámetros de la ecografía
            
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
                        "content": "Eres un radiólogo experto en interpretación de ecografías. Analiza los parámetros de la ecografía y proporciona una interpretación clínica detallada. DEBES responder ÚNICAMENTE en formato JSON válido."
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
            raise Exception(f"Error al interpretar Ecografía con IA: {str(e)}")
    
    def _construir_prompt(self, parametros: Dict[str, Any]) -> str:
        """Construye el prompt para la IA"""
        
        tipo_eco = parametros.get('tipo_ecografia', 'Ecografía').upper()
        
        prompt = f"""Analiza la siguiente {tipo_eco} y proporciona una interpretación radiológica detallada.

INFORMACIÓN DE LA ECOGRAFÍA:
"""
        
        # Tipo y región
        prompt += f"- Tipo: {parametros.get('tipo_ecografia', 'No especificado')}\n"
        if parametros.get('region_anatomica'):
            prompt += f"- Región anatómica: {parametros['region_anatomica']}\n"
        
        # Técnica
        if parametros.get('modo'):
            prompt += f"- Modo: {parametros['modo']}\n"
        if parametros.get('via_acceso'):
            prompt += f"- Vía de acceso: {parametros['via_acceso']}\n"
        if parametros.get('transductor'):
            prompt += f"- Transductor: {parametros['transductor']}\n"
        
        # Datos obstétricos
        if parametros.get('es_obstetrica'):
            prompt += f"\nDATOS OBSTÉTRICOS:\n"
            if parametros.get('edad_gestacional_semanas'):
                prompt += f"- Edad gestacional: {parametros['edad_gestacional_semanas']} semanas\n"
            if parametros.get('numero_fetos'):
                prompt += f"- Número de fetos: {parametros['numero_fetos']}\n"
        
        # Hallazgos por modo
        if parametros.get('hallazgos_2d'):
            prompt += f"\nHALLAZGOS 2D:\n{parametros['hallazgos_2d']}\n"
        if parametros.get('hallazgos_3d'):
            prompt += f"\nHALLAZGOS 3D:\n{parametros['hallazgos_3d']}\n"
        if parametros.get('hallazgos_4d'):
            prompt += f"\nHALLAZGOS 4D:\n{parametros['hallazgos_4d']}\n"
        
        # Doppler
        if parametros.get('estudio_doppler'):
            prompt += f"\nESTUDIO DOPPLER:\n"
            if parametros.get('flujo_vascular'):
                prompt += f"- Flujo vascular: {parametros['flujo_vascular']}\n"
            if parametros.get('resistencia_vascular'):
                prompt += f"- Resistencia vascular: {parametros['resistencia_vascular']}\n"
        
        # Hallazgos adicionales
        if parametros.get('liquido_libre'):
            cantidad = parametros.get('cantidad_liquido', 'No especificada')
            prompt += f"\nLÍQUIDO LIBRE: Presente ({cantidad})\n"
        
        # Calidad
        if parametros.get('calidad_estudio'):
            prompt += f"\nCALIDAD DEL ESTUDIO: {parametros['calidad_estudio']}\n"
        if parametros.get('limitaciones'):
            prompt += f"Limitaciones: {parametros['limitaciones']}\n"
        
        # BI-RADS (para mamaria)
        if parametros.get('birads'):
            prompt += f"\nBI-RADS: {parametros['birads']}\n"
        
        # Motivo
        if parametros.get('motivo'):
            prompt += f"\nMOTIVO DEL ESTUDIO: {parametros['motivo']}\n"
        
        prompt += f"""

TAREA:
Proporciona una interpretación radiológica completa de la {tipo_eco} en formato JSON con la siguiente estructura:

{{
  "interpretacion": "Descripción detallada de los hallazgos",
  "diagnostico_principal": "Diagnóstico principal basado en los hallazgos",
  "diagnosticos_secundarios": ["Diagnóstico 1", "Diagnóstico 2"],
  "hallazgos_clave": [
    {{
      "estructura": "Nombre de la estructura",
      "hallazgo": "Descripción del hallazgo",
      "interpretacion": "Normal/Anormal",
      "significado_clinico": "Qué significa este hallazgo"
    }}
  ],
  "clasificacion": "normal/hallazgo_benigno/sospechoso/maligno",
  "requiere_atencion_inmediata": false,
  "recomendaciones": [
    "Recomendación 1",
    "Recomendación 2"
  ],
  "estudios_adicionales": ["Estudio 1", "Estudio 2"],
  "diagnosticos_diferenciales": [
    {{
      "diagnostico": "Nombre del diagnóstico",
      "probabilidad": "alta/media/baja",
      "criterios": "Criterios que lo soportan"
    }}
  ],
  "seguimiento_recomendado": "Descripción del seguimiento"
}}

Sé específico y clínico en tu interpretación. Considera el tipo de ecografía y el contexto clínico.
"""
        
        return prompt
