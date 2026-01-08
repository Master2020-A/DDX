"""
Analizador de ECG usando IA (OpenAI Vision API)
Analiza imágenes de ECG y extrae parámetros automáticamente
"""
import os
import base64
from typing import Dict, Any, Optional
from pathlib import Path
import json
import re

try:
    from openai import OpenAI
    OPENAI_DISPONIBLE = True
except ImportError:
    OPENAI_DISPONIBLE = False
    print("⚠️ OpenAI library no disponible. Instala: pip install openai")


class AnalizadorECGIA:
    """
    Analizador de ECG usando IA (OpenAI GPT-4 Vision)
    Extrae parámetros de imágenes de ECG automáticamente
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el analizador
        
        Args:
            api_key: API key de OpenAI (opcional, usa variable de entorno si no se provee)
        """
        if not OPENAI_DISPONIBLE:
            raise ImportError("OpenAI library no está instalada. Ejecuta: pip install openai")
        
        # Obtener API key
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "API key de OpenAI no encontrada. "
                "Configura la variable de entorno OPENAI_API_KEY"
            )
        
        # Configurar cliente OpenAI
        self.client = OpenAI(api_key=self.api_key)
    
    def analizar_ecg(self, imagen_path: str) -> Dict[str, Any]:
        """
        Analiza una imagen de ECG y extrae parámetros
        
        Args:
            imagen_path: Ruta a la imagen del ECG
            
        Returns:
            Dict con datos extraídos y anomalías detectadas
        """
        try:
            print("🔍 Iniciando análisis de ECG con IA...")
            
            # Codificar imagen en base64
            print("📸 Codificando imagen en base64...")
            imagen_base64 = self._codificar_imagen(imagen_path)
            print(f"✅ Imagen codificada ({len(imagen_base64)} caracteres)")
            
            # Crear prompt para análisis
            prompt = self._crear_prompt_analisis()
            print("✅ Prompt creado")
            
            # Llamar a OpenAI Vision API
            print("🌐 Enviando solicitud a OpenAI Vision API...")
            respuesta = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un cardiólogo experto especializado en análisis de electrocardiogramas."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{imagen_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )
            print("✅ Respuesta recibida de OpenAI")
            
            # Extraer respuesta
            contenido = respuesta.choices[0].message.content
            print(f"\n{'='*60}")
            print("📝 RESPUESTA COMPLETA DE OPENAI:")
            print(f"{'='*60}")
            print(contenido)
            print(f"{'='*60}\n")
            
            # Parsear respuesta JSON
            print("🔄 Parseando respuesta...")
            datos = self._parsear_respuesta(contenido)
            print(f"✅ Datos parseados exitosamente")
            print(f"   📊 Parámetros encontrados: {len(datos.get('parametros', {}))}")
            print(f"   🔑 Claves: {list(datos.get('parametros', {}).keys())}")
            print(f"   ⚠️  Anomalías: {datos.get('anomalias', [])}")
            print(f"   📈 Confianza: {datos.get('confianza', 0)}")
            
            resultado = {
                'tipo_estudio': 'ekg',
                'datos': datos['parametros'],
                'anomalias': datos['anomalias'],
                'interpretacion': datos['interpretacion'],
                'confianza': datos['confianza'],
                'metodo': 'ia_vision',
                'modelo': 'gpt-4o'
            }
            
            print(f"✅ Retornando resultado con {len(resultado['datos'])} parámetros")
            return resultado
        
        except Exception as e:
            print(f"\n❌ ERROR EN ANÁLISIS CON IA:")
            print(f"   Tipo: {type(e).__name__}")
            print(f"   Mensaje: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return {
                'tipo_estudio': 'ekg',
                'datos': {},
                'anomalias': [],
                'error': f'Error en análisis con IA: {str(e)}',
                'confianza': 0.0
            }
    
    def _codificar_imagen(self, imagen_path: str) -> str:
        """Codifica imagen en base64"""
        with open(imagen_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def _crear_prompt_analisis(self) -> str:
        """Crea el prompt para análisis de ECG"""
        return """
Analiza esta imagen de electrocardiograma (ECG) y extrae la siguiente información:

**PARÁMETROS A EXTRAER:**
1. Frecuencia Cardíaca (FC) en lpm
2. Intervalo PR en ms
3. Duración QRS en ms
4. Intervalo QT en ms
5. Intervalo QTc (QT corregido) en ms
6. Eje QRS en grados

**ANOMALÍAS A DETECTAR:**
- Bradicardia (FC < 60)
- Taquicardia (FC > 100)
- Bloqueo AV (PR > 200ms)
- Bloqueo de rama (QRS > 120ms)
- QT prolongado (QTc > 440ms)
- Desviación de eje (fuera de -30° a +90°)
- Elevación/depresión del ST
- Ondas Q patológicas
- Inversión de onda T
- Arritmias

**FORMATO DE RESPUESTA (JSON):**
```json
{
  "parametros": {
    "frecuencia_cardiaca": 75,
    "intervalo_pr": 160,
    "duracion_qrs": 90,
    "intervalo_qt": 400,
    "intervalo_qtc": 420,
    "eje_qrs": 60
  },
  "anomalias": ["taquicardia", "qt_prolongado"],
  "interpretacion": "Electrocardiograma con taquicardia sinusal y QT prolongado. Se recomienda evaluación cardiológica.",
  "confianza": 0.85
}
```

**INSTRUCCIONES:**
1. Si no puedes medir un parámetro con precisión, omítelo
2. Lista todas las anomalías detectadas
3. Proporciona una interpretación clínica breve
4. Indica tu nivel de confianza (0.0 a 1.0)
5. Responde SOLO con el JSON, sin texto adicional
"""
    
    def _parsear_respuesta(self, contenido: str) -> Dict[str, Any]:
        """Parsea la respuesta de la IA"""
        try:
            # Extraer JSON de la respuesta
            # Buscar entre ```json y ``` o directamente el JSON
            match = re.search(r'```json\s*(.*?)\s*```', contenido, re.DOTALL)
            if match:
                json_str = match.group(1)
            else:
                # Intentar extraer JSON directamente
                match = re.search(r'\{.*\}', contenido, re.DOTALL)
                if match:
                    json_str = match.group(0)
                else:
                    json_str = contenido
            
            # Parsear JSON
            datos = json.loads(json_str)
            
            # Validar estructura
            if 'parametros' not in datos:
                datos['parametros'] = {}
            if 'anomalias' not in datos:
                datos['anomalias'] = []
            if 'interpretacion' not in datos:
                datos['interpretacion'] = 'Análisis completado'
            if 'confianza' not in datos:
                datos['confianza'] = 0.7
            
            return datos
        
        except json.JSONDecodeError:
            # Si falla el parseo, intentar extraer manualmente
            return self._parsear_respuesta_manual(contenido)
    
    def _parsear_respuesta_manual(self, contenido: str) -> Dict[str, Any]:
        """Parsea la respuesta manualmente si falla el JSON"""
        datos = {
            'parametros': {},
            'anomalias': [],
            'interpretacion': contenido[:200],
            'confianza': 0.5
        }
        
        # Extraer FC
        match = re.search(r'(?:FC|frecuencia[_ ]cardiaca)[:\s]*(\d+)', contenido, re.IGNORECASE)
        if match:
            datos['parametros']['frecuencia_cardiaca'] = int(match.group(1))
        
        # Extraer PR
        match = re.search(r'(?:PR|intervalo[_ ]pr)[:\s]*(\d+)', contenido, re.IGNORECASE)
        if match:
            datos['parametros']['intervalo_pr'] = int(match.group(1))
        
        # Extraer QRS
        match = re.search(r'(?:QRS|duracion[_ ]qrs)[:\s]*(\d+)', contenido, re.IGNORECASE)
        if match:
            datos['parametros']['duracion_qrs'] = int(match.group(1))
        
        # Extraer QTc
        match = re.search(r'(?:QTc|qt[_ ]corregido)[:\s]*(\d+)', contenido, re.IGNORECASE)
        if match:
            datos['parametros']['intervalo_qtc'] = int(match.group(1))
        
        # Detectar anomalías mencionadas
        anomalias_posibles = [
            'bradicardia', 'taquicardia', 'bloqueo', 'arritmia',
            'qt_prolongado', 'isquemia', 'infarto'
        ]
        for anomalia in anomalias_posibles:
            if anomalia in contenido.lower():
                datos['anomalias'].append(anomalia)
        
        return datos


# Función de conveniencia
def analizar_ecg_con_ia(imagen_path: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Función de conveniencia para analizar ECG con IA
    
    Args:
        imagen_path: Ruta a la imagen del ECG
        api_key: API key de OpenAI (opcional)
        
    Returns:
        Dict con datos extraídos
    """
    analizador = AnalizadorECGIA(api_key=api_key)
    return analizador.analizar_ecg(imagen_path)
