"""
Servicio de Proveedores de IA
Soporte para Ollama, Groq, OpenAI, Anthropic
"""

import httpx
import os
from typing import Dict, Any, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AIProvider(str, Enum):
    """Proveedores de IA soportados"""

    OLLAMA = "ollama"
    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class AIProviderService:
    """Servicio unificado para múltiples proveedores de IA"""

    def __init__(self):
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")

    async def chat_completion(
        self,
        provider: str,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Ejecutar chat completion con el proveedor especificado

        Args:
            provider: ollama, groq, openai, anthropic
            model: nombre del modelo
            messages: lista de mensajes [{"role": "user", "content": "..."}]
            temperature: 0-100 (se convierte a 0-1 internamente)
            max_tokens: máximo de tokens a generar

        Returns:
            Dict con la respuesta del modelo
        """
        # Convertir temperatura de 0-100 a 0-1
        temp_normalized = temperature / 100.0 if temperature > 1 else temperature

        provider_lower = provider.lower()

        if provider_lower == "ollama":
            return await self._ollama_chat(model, messages, temp_normalized, max_tokens)
        elif provider_lower == "groq":
            return await self._groq_chat(model, messages, temp_normalized, max_tokens)
        elif provider_lower == "openai":
            return await self._openai_chat(model, messages, temp_normalized, max_tokens)
        elif provider_lower == "anthropic":
            return await self._anthropic_chat(
                model, messages, temp_normalized, max_tokens
            )
        else:
            raise ValueError(f"Proveedor no soportado: {provider}")

    async def _ollama_chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> Dict[str, Any]:
        """Chat con Ollama (local)"""
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/chat",
                    json={
                        "model": model,
                        "messages": messages,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens,
                        },
                    },
                )
                response.raise_for_status()
                data = response.json()

                return {
                    "provider": "ollama",
                    "model": model,
                    "content": data.get("message", {}).get("content", ""),
                    "usage": {
                        "prompt_tokens": data.get("prompt_eval_count", 0),
                        "completion_tokens": data.get("eval_count", 0),
                        "total_tokens": data.get("prompt_eval_count", 0)
                        + data.get("eval_count", 0),
                    },
                    "raw_response": data,
                }
        except Exception as e:
            logger.error(f"Error en Ollama: {e}")
            raise Exception(f"Error al conectar con Ollama: {str(e)}")

    async def _groq_chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> Dict[str, Any]:
        """Chat con Groq"""
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY no configurada")

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                )
                response.raise_for_status()
                data = response.json()

                return {
                    "provider": "groq",
                    "model": model,
                    "content": data["choices"][0]["message"]["content"],
                    "usage": data.get("usage", {}),
                    "raw_response": data,
                }
        except Exception as e:
            logger.error(f"Error en Groq: {e}")
            raise Exception(f"Error al conectar con Groq: {str(e)}")

    async def _openai_chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> Dict[str, Any]:
        """Chat con OpenAI"""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY no configurada")

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                )
                response.raise_for_status()
                data = response.json()

                return {
                    "provider": "openai",
                    "model": model,
                    "content": data["choices"][0]["message"]["content"],
                    "usage": data.get("usage", {}),
                    "raw_response": data,
                }
        except Exception as e:
            logger.error(f"Error en OpenAI: {e}")
            raise Exception(f"Error al conectar con OpenAI: {str(e)}")

    async def _anthropic_chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> Dict[str, Any]:
        """Chat con Anthropic (Claude)"""
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY no configurada")

        # Anthropic usa un formato diferente
        system_message = ""
        user_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                payload = {
                    "model": model,
                    "messages": user_messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }

                if system_message:
                    payload["system"] = system_message

                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.anthropic_api_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

                return {
                    "provider": "anthropic",
                    "model": model,
                    "content": data["content"][0]["text"],
                    "usage": data.get("usage", {}),
                    "raw_response": data,
                }
        except Exception as e:
            logger.error(f"Error en Anthropic: {e}")
            raise Exception(f"Error al conectar con Anthropic: {str(e)}")

    async def list_ollama_models(self) -> List[str]:
        """Listar modelos disponibles en Ollama"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.ollama_base_url}/api/tags")
                response.raise_for_status()
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            logger.error(f"Error listando modelos Ollama: {e}")
            return []


# Instancia global del servicio
ai_service = AIProviderService()
