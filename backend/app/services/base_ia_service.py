"""
Clase base para todos los servicios de IA
"""

import json
import re
import logging
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

from openai import AsyncOpenAI
from sqlalchemy.orm import Session

from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseIAService(ABC):
    """
    Clase base con funcionalidades comunes para todos los servicios de IA.
    Maneja las llamadas a OpenAI y el parseo seguro de JSON.
    """

    def __init__(self, db: Session):
        self.db = db
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL or "gpt-4o"

    async def _llamar_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        json_response: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Llamada genérica a OpenAI con manejo robusto de errores.

        Args:
            system_prompt: Instrucciones del sistema
            user_prompt: Mensaje del usuario
            temperature: Creatividad (0-1)
            max_tokens: Máximo de tokens en respuesta
            json_response: Si debe forzar respuesta JSON

        Returns:
            Dict con la respuesta parseada o None si falla
        """

        try:
            # Validar API Key
            if not settings.OPENAI_API_KEY:
                logger.error("OPENAI_API_KEY no está configurada")
                return None

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            # Forzar respuesta JSON si es necesario
            if json_response:
                kwargs["response_format"] = {"type": "json_object"}

            logger.info(f"📤 Llamando a OpenAI ({self.model})...")

            response = await self.client.chat.completions.create(**kwargs)

            content = response.choices[0].message.content

            # Validar que no esté vacío
            if not content or content.strip() == "":
                logger.error("❌ Respuesta vacía de OpenAI")
                return None

            logger.info(f"📥 Respuesta recibida ({len(content)} caracteres)")

            # Parsear JSON si es necesario
            if json_response:
                return self._parse_json_seguro(content)

            return {"content": content}

        except Exception as e:
            logger.error(f"❌ Error en llamada a OpenAI: {str(e)}")
            return None

    def _parse_json_seguro(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Parsea JSON de forma segura, manejando diferentes formatos.

        Args:
            content: String con contenido JSON

        Returns:
            Dict parseado o None si falla
        """

        if not content:
            return None

        content = content.strip()

        # ===== Intento 1: Parseo directo =====
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            logger.debug("Parseo directo falló, intentando limpiar...")

        # ===== Intento 2: Extraer de bloques markdown =====
        patterns = [
            r"```json\s*([\s\S]*?)\s*```",  # ```json ... ```
            r"```\s*([\s\S]*?)\s*```",  # ``` ... ```
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    json_str = match.group(1).strip()
                    return json.loads(json_str)
                except (json.JSONDecodeError, IndexError):
                    continue

        # ===== Intento 3: Buscar objeto JSON en el texto =====
        try:
            # Encontrar el primer { y el último }
            start = content.find("{")
            end = content.rfind("}") + 1

            if start != -1 and end > start:
                json_str = content[start:end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        # ===== Intento 4: Limpiar caracteres problemáticos =====
        try:
            # Remover caracteres de control
            cleaned = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", content)
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        logger.error(f"❌ No se pudo parsear JSON: {content[:200]}...")
        return None

    def _calcular_tokens_aproximados(self, texto: str) -> int:
        """Estimación aproximada de tokens (1 token ≈ 0.75 palabras)"""
        palabras = len(texto.split())
        return int(palabras * 1.33)

    def _formatear_lista(
        self, lista: Optional[List[str]], default: str = "Ninguno"
    ) -> str:
        """Formatea una lista para incluir en prompts"""
        if not lista:
            return f"- {default}"
        return "\n".join([f"- {item}" for item in lista])

    @abstractmethod
    async def procesar(self, *args, **kwargs) -> Dict[str, Any]:
        """Método principal a implementar por cada servicio"""
        pass
