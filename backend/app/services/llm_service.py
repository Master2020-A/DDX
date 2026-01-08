"""
Servicio para Integración con Múltiples Proveedores de LLMs
"""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import asyncio
import os
from datetime import datetime


class LLMProvider(ABC):
    """Clase base para proveedores de LLM"""

    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    async def generate(
        self, prompt: str, system_prompt: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Generar respuesta"""
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Obtener modelos disponibles"""
        pass


class OpenAIProvider(LLMProvider):
    """Proveedor OpenAI"""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.client = None

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generar respuesta con OpenAI"""
        try:
            # Lazy import
            if not self.client:
                from openai import AsyncOpenAI

                self.client = AsyncOpenAI(api_key=self.api_key)

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            return {
                "success": True,
                "content": response.choices[0].message.content,
                "model": model,
                "provider": "openai",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "cost": self._calculate_cost(model, response.usage),
            }
        except Exception as e:
            return {"success": False, "error": str(e), "provider": "openai"}

    def get_available_models(self) -> List[str]:
        return ["gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-3.5-turbo"]

    def _calculate_cost(self, model: str, usage) -> float:
        """Calcular costo aproximado"""
        costs = {
            "gpt-4": {"prompt": 0.03, "completion": 0.06},
            "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03},
            "gpt-4o": {"prompt": 0.005, "completion": 0.015},
            "gpt-3.5-turbo": {"prompt": 0.0005, "completion": 0.0015},
        }

        if model not in costs:
            return 0.0

        prompt_cost = (usage.prompt_tokens / 1000) * costs[model]["prompt"]
        completion_cost = (usage.completion_tokens / 1000) * costs[model]["completion"]
        return prompt_cost + completion_cost


class AnthropicProvider(LLMProvider):
    """Proveedor Anthropic (Claude)"""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.client = None

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = "claude-3-sonnet-20240229",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generar respuesta con Anthropic"""
        try:
            if not self.client:
                from anthropic import AsyncAnthropic

                self.client = AsyncAnthropic(api_key=self.api_key)

            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )

            return {
                "success": True,
                "content": response.content[0].text,
                "model": model,
                "provider": "anthropic",
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens
                    + response.usage.output_tokens,
                },
                "cost": self._calculate_cost(model, response.usage),
            }
        except Exception as e:
            return {"success": False, "error": str(e), "provider": "anthropic"}

    def get_available_models(self) -> List[str]:
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]

    def _calculate_cost(self, model: str, usage) -> float:
        costs = {
            "claude-3-opus-20240229": {"prompt": 0.015, "completion": 0.075},
            "claude-3-sonnet-20240229": {"prompt": 0.003, "completion": 0.015},
            "claude-3-haiku-20240307": {"prompt": 0.00025, "completion": 0.00125},
        }

        if model not in costs:
            return 0.0

        prompt_cost = (usage.input_tokens / 1000) * costs[model]["prompt"]
        completion_cost = (usage.output_tokens / 1000) * costs[model]["completion"]
        return prompt_cost + completion_cost


class GoogleProvider(LLMProvider):
    """Proveedor Google (Gemini)"""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.client = None

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = "gemini-pro",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generar respuesta con Google Gemini"""
        try:
            if not self.client:
                import google.generativeai as genai

                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(model)

            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            response = await asyncio.to_thread(
                self.client.generate_content,
                full_prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )

            return {
                "success": True,
                "content": response.text,
                "model": model,
                "provider": "google",
                "usage": {
                    "prompt_tokens": 0,  # Google no proporciona tokens
                    "completion_tokens": 0,
                    "total_tokens": 0,
                },
                "cost": 0.0,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "provider": "google"}

    def get_available_models(self) -> List[str]:
        return ["gemini-pro", "gemini-pro-vision"]


class CohereProvider(LLMProvider):
    """Proveedor Cohere"""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.client = None

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = "command",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generar respuesta con Cohere"""
        try:
            if not self.client:
                import cohere

                self.client = cohere.AsyncClient(api_key=self.api_key)

            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            response = await self.client.generate(
                model=model,
                prompt=full_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            return {
                "success": True,
                "content": response.generations[0].text,
                "model": model,
                "provider": "cohere",
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                },
                "cost": 0.0,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "provider": "cohere"}

    def get_available_models(self) -> List[str]:
        return ["command", "command-light"]


class LLMService:
    """Servicio principal para gestionar múltiples proveedores de LLM"""

    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}
        self.usage_stats: Dict[str, Dict[str, Any]] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """Inicializar proveedores desde variables de entorno"""
        if os.getenv("OPENAI_API_KEY"):
            self.providers["openai"] = OpenAIProvider(os.getenv("OPENAI_API_KEY"))

        if os.getenv("ANTHROPIC_API_KEY"):
            self.providers["anthropic"] = AnthropicProvider(
                os.getenv("ANTHROPIC_API_KEY")
            )

        if os.getenv("GOOGLE_API_KEY"):
            self.providers["google"] = GoogleProvider(os.getenv("GOOGLE_API_KEY"))

        if os.getenv("COHERE_API_KEY"):
            self.providers["cohere"] = CohereProvider(os.getenv("COHERE_API_KEY"))

    def add_provider(self, name: str, provider: LLMProvider):
        """Agregar proveedor manualmente"""
        self.providers[name] = provider

    async def generate(
        self,
        prompt: str,
        provider: str = "openai",
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        fallback_providers: Optional[List[str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generar respuesta con fallback automático

        Args:
            prompt: Prompt del usuario
            provider: Proveedor principal
            model: Modelo específico
            system_prompt: Prompt del sistema
            fallback_providers: Lista de proveedores de respaldo
            **kwargs: Parámetros adicionales
        """
        # Intentar con proveedor principal
        if provider in self.providers:
            result = await self.providers[provider].generate(
                prompt, system_prompt, model=model, **kwargs
            )

            if result["success"]:
                self._track_usage(provider, result)
                return result

        # Intentar con proveedores de respaldo
        if fallback_providers:
            for fallback in fallback_providers:
                if fallback in self.providers:
                    result = await self.providers[fallback].generate(
                        prompt, system_prompt, **kwargs
                    )

                    if result["success"]:
                        self._track_usage(fallback, result)
                        return result

        return {
            "success": False,
            "error": "No hay proveedores disponibles",
            "provider": None,
        }

    def _track_usage(self, provider: str, result: Dict[str, Any]):
        """Registrar uso y costos"""
        if provider not in self.usage_stats:
            self.usage_stats[provider] = {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "successful_requests": 0,
                "failed_requests": 0,
            }

        stats = self.usage_stats[provider]
        stats["total_requests"] += 1

        if result["success"]:
            stats["successful_requests"] += 1
            stats["total_tokens"] += result["usage"]["total_tokens"]
            stats["total_cost"] += result.get("cost", 0.0)
        else:
            stats["failed_requests"] += 1

    def get_available_providers(self) -> List[str]:
        """Obtener proveedores disponibles"""
        return list(self.providers.keys())

    def get_available_models(self, provider: str) -> List[str]:
        """Obtener modelos disponibles de un proveedor"""
        if provider in self.providers:
            return self.providers[provider].get_available_models()
        return []

    def get_usage_stats(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """Obtener estadísticas de uso"""
        if provider:
            return self.usage_stats.get(provider, {})
        return self.usage_stats

    def get_total_cost(self) -> float:
        """Obtener costo total acumulado"""
        return sum(stats.get("total_cost", 0.0) for stats in self.usage_stats.values())


# Instancia global del servicio
llm_service = LLMService()
