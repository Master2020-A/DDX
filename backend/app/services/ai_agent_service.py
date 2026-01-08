"""
Servicio de Agentes IA
Integración con múltiples LLMs (Ollama, Groq, OpenAI, Anthropic)
"""

from typing import Dict, Any, Optional, List
import os
import logging
import json
from datetime import datetime

from app.models.workflow import AIAgent, AgentModel
from app.services.ai_providers import ai_service

logger = logging.getLogger(__name__)


class AIAgentService:
    """Servicio para ejecutar agentes IA con diferentes modelos"""

    def __init__(self):
        self.ai_provider = ai_service

    async def execute_agent(
        self, agent: AIAgent, input_data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ejecuta un agente IA con el modelo configurado

        Args:
            agent: Configuración del agente
            input_data: Datos de entrada
            context: Contexto de ejecución

        Returns:
            Respuesta del agente
        """
        logger.info(
            f"Ejecutando agente '{agent.name}' con modelo '{agent.model.value}'"
        )

        # Preparar prompt
        user_prompt = self._prepare_user_prompt(agent, input_data, context)

        # Preparar mensajes
        messages = [
            {"role": "system", "content": agent.system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # Detectar proveedor según el modelo
        provider = self._detect_provider(agent.model.value)

        try:
            # Ejecutar con el proveedor unificado
            response = await self.ai_provider.chat_completion(
                provider=provider,
                model=agent.model.value,
                messages=messages,
                temperature=agent.temperature,
                max_tokens=agent.max_tokens,
            )

            return {
                "response": response["content"],
                "model": agent.model.value,
                "provider": response["provider"],
                "usage": response.get("usage", {}),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error ejecutando agente: {e}")
            return {
                "error": str(e),
                "model": agent.model.value,
                "timestamp": datetime.utcnow().isoformat(),
            }

    def _detect_provider(self, model: str) -> str:
        """Detecta el proveedor según el nombre del modelo"""
        model_lower = model.lower()

        # OpenAI
        if "gpt" in model_lower:
            return "openai"

        # Anthropic
        if "claude" in model_lower:
            return "anthropic"

        # Groq (modelos open source en Groq)
        if any(x in model_lower for x in ["llama", "mixtral", "gemma"]):
            return "groq"

        # Ollama (por defecto para modelos locales)
        if any(x in model_lower for x in ["qwen", "mistral", "phi", "deepseek"]):
            return "ollama"

        # Por defecto, intentar con Ollama
        return "ollama"

    def _prepare_user_prompt(
        self, agent: AIAgent, input_data: Dict[str, Any], context: Dict[str, Any]
    ) -> str:
        """Prepara el prompt del usuario con template y datos"""

        if agent.user_prompt_template:
            # Usar template si está definido
            template = agent.user_prompt_template

            # Reemplazar variables del template
            for key, value in input_data.items():
                template = template.replace(f"{{{key}}}", str(value))

            return template

        else:
            # Sin template, convertir input_data a texto
            return self._format_input_data(input_data)

    def _format_input_data(self, data: Dict[str, Any]) -> str:
        """Formatea los datos de entrada como texto"""
        lines = []

        for key, value in data.items():
            if isinstance(value, (dict, list)):
                import json

                value_str = json.dumps(value, indent=2, ensure_ascii=False)
            else:
                value_str = str(value)

            lines.append(f"{key}: {value_str}")

        return "\n".join(lines)
