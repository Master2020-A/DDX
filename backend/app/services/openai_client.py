"""
Cliente centralizado para múltiples proveedores de IA
"""

from openai import AsyncOpenAI
from app.core.config import settings
from typing import Optional, Dict, Any, List
import os

# Determinar proveedor de IA
AI_PROVIDER = os.getenv("AI_PROVIDER", "groq").lower()  # groq, openai, ollama

# Configurar cliente según proveedor
if AI_PROVIDER == "groq":
    # Groq (gratuito, rápido, modelos open-source)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    if GROQ_API_KEY:
        client = AsyncOpenAI(
            api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1"
        )
        DEFAULT_MODEL = (
            "llama-3.3-70b-versatile"  # Modelo gratuito de Groq (actualizado)
        )
    else:
        print("⚠️  GROQ_API_KEY no configurada, usando modo demo")
        client = None
        DEFAULT_MODEL = "demo"
elif AI_PROVIDER == "openai":
    # OpenAI (de pago)
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    DEFAULT_MODEL = "gpt-4o"
else:
    # Modo demo sin IA real
    print(f"⚠️  Proveedor {AI_PROVIDER} no soportado, usando modo demo")
    client = None
    DEFAULT_MODEL = "demo"


async def chat_completion(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    response_format: Optional[Dict[str, str]] = None,
) -> Any:
    """
    Realizar una llamada a la API de chat completion con múltiples proveedores

    Args:
        messages: Lista de mensajes en formato OpenAI
        model: Modelo a utilizar (None = usar modelo por defecto del proveedor)
        temperature: Temperatura para la generación
        max_tokens: Máximo de tokens a generar
        response_format: Formato de respuesta (ej: {"type": "json_object"})

    Returns:
        Respuesta compatible con formato OpenAI
    """
    # Usar modelo por defecto si no se especifica
    if model is None:
        model = DEFAULT_MODEL

    # Modo demo (sin IA real)
    if client is None or model == "demo":
        return _generate_demo_response(messages, response_format)

    # Ajustar modelo según proveedor
    if AI_PROVIDER == "groq":
        # Mapear modelos de OpenAI a Groq
        model_map = {
            "gpt-4o": "llama-3.3-70b-versatile",
            "gpt-4": "llama-3.3-70b-versatile",
            "gpt-3.5-turbo": "llama-3.1-8b-instant",
        }
        model = model_map.get(model, "llama-3.3-70b-versatile")

    kwargs = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    if max_tokens:
        kwargs["max_tokens"] = max_tokens

    # Groq no soporta response_format="json_object" directamente
    # Agregar instrucción en el mensaje del sistema
    if response_format and response_format.get("type") == "json_object":
        if AI_PROVIDER == "groq":
            # Agregar instrucción JSON al último mensaje del sistema
            for msg in messages:
                if msg["role"] == "system":
                    msg[
                        "content"
                    ] += "\n\nIMPORTANTE: Responde ÚNICAMENTE con JSON válido, sin texto adicional."
                    break
        else:
            kwargs["response_format"] = response_format

    response = await client.chat.completions.create(**kwargs)
    return response


def _generate_demo_response(
    messages: List[Dict[str, str]], response_format: Optional[Dict[str, str]] = None
) -> Any:
    """
    Generar respuesta demo cuando no hay cliente de IA configurado
    """
    import json
    from datetime import datetime

    # Crear objeto de respuesta compatible con OpenAI
    class DemoChoice:
        def __init__(self, content: str):
            self.message = type("obj", (object,), {"content": content})
            self.finish_reason = "stop"

    class DemoResponse:
        def __init__(self, content: str):
            self.choices = [DemoChoice(content)]
            self.model = "demo"
            self.created = int(datetime.utcnow().timestamp())

    # Generar respuesta demo según el contexto
    last_message = messages[-1]["content"].lower() if messages else ""

    if response_format and response_format.get("type") == "json_object":
        # Respuesta JSON demo
        if "riesgo" in last_message or "cardiovascular" in last_message:
            demo_content = json.dumps(
                {
                    "tipo_riesgo": "cardiovascular",
                    "nivel_riesgo": "moderado",
                    "porcentaje_riesgo": 35.5,
                    "factores_riesgo": ["Edad", "Presión arterial elevada"],
                    "factores_protectores": ["No fumador", "Actividad física regular"],
                    "recomendaciones": [
                        "Control de presión arterial",
                        "Dieta baja en sodio",
                    ],
                    "estudios_sugeridos": ["Perfil lipídico", "Electrocardiograma"],
                }
            )
        elif "tratamiento" in last_message or "recomendacion" in last_message:
            demo_content = json.dumps(
                {
                    "medicamentos_sugeridos": [
                        {
                            "nombre": "Enalapril",
                            "dosis": "10mg",
                            "frecuencia": "cada 12 horas",
                            "duracion": "continuo",
                        }
                    ],
                    "terapias_no_farmacologicas": ["Ejercicio aeróbico 30 min/día"],
                    "cambios_estilo_vida": ["Reducir consumo de sal", "Dieta DASH"],
                    "contraindicaciones": ["Embarazo", "Angioedema previo"],
                    "precauciones": ["Monitorear función renal"],
                    "nivel_evidencia": "A",
                }
            )
        elif "interaccion" in last_message:
            demo_content = json.dumps(
                {
                    "interacciones": [
                        {
                            "medicamento1": "Enalapril",
                            "medicamento2": "Ibuprofeno",
                            "severidad": "moderada",
                            "descripcion": "Los AINEs pueden reducir el efecto antihipertensivo",
                            "manejo": "Monitorear presión arterial, considerar alternativas",
                        }
                    ],
                    "severidad_maxima": "moderada",
                    "requiere_ajuste": True,
                    "recomendaciones": [
                        "Monitoreo de presión arterial",
                        "Considerar paracetamol como alternativa",
                    ],
                }
            )
        else:
            demo_content = json.dumps(
                {
                    "respuesta": "Análisis completado (modo demo)",
                    "confianza": 0.85,
                    "recomendaciones": ["Consultar con especialista"],
                }
            )
    else:
        # Respuesta texto demo
        demo_content = f"""Basándome en la información proporcionada (MODO DEMO - Sin IA real):

Este es un análisis simulado. Para usar IA real, configura una de estas opciones:

1. **Groq (GRATIS y RÁPIDO)**:
   - Obtén API key en: https://console.groq.com/keys
   - Agrega a .env: GROQ_API_KEY=tu-key
   - Agrega a .env: AI_PROVIDER=groq

2. **OpenAI (De pago)**:
   - Usa tu OPENAI_API_KEY existente
   - Agrega a .env: AI_PROVIDER=openai

Contexto de la consulta: {last_message[:100]}...
"""

    return DemoResponse(demo_content)
