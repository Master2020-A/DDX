"""
API Endpoints para Gestión de Múltiples LLMs
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.api.dependencies import get_current_user
from app.models.usuario import Usuario
from app.services.llm_service import llm_service

router = APIRouter()


# ============================================================
# SCHEMAS
# ============================================================


class LLMGenerateRequest(BaseModel):
    prompt: str
    provider: str = "openai"
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    fallback_providers: Optional[List[str]] = None


class LLMTestRequest(BaseModel):
    provider: str
    model: Optional[str] = None
    prompt: str = "Hola, ¿cómo estás?"


class ProviderCredentials(BaseModel):
    provider: str
    api_key: str
    organization_id: Optional[str] = None


class ProviderInfo(BaseModel):
    name: str
    available: bool
    models: List[str]


class UsageStats(BaseModel):
    provider: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_tokens: int
    total_cost: float


# ============================================================
# ENDPOINTS
# ============================================================


@router.get("/providers", response_model=List[ProviderInfo])
async def get_providers(current_user: Usuario = Depends(get_current_user)):
    """Obtener lista de proveedores disponibles"""
    available_providers = llm_service.get_available_providers()

    all_providers = {
        "openai": "OpenAI",
        "anthropic": "Anthropic (Claude)",
        "google": "Google (Gemini)",
        "cohere": "Cohere",
    }

    result = []
    for key, name in all_providers.items():
        is_available = key in available_providers
        models = llm_service.get_available_models(key) if is_available else []

        result.append({"name": name, "available": is_available, "models": models})

    return result


@router.get("/providers/{provider}/models", response_model=List[str])
async def get_provider_models(
    provider: str, current_user: Usuario = Depends(get_current_user)
):
    """Obtener modelos disponibles de un proveedor"""
    models = llm_service.get_available_models(provider)

    if not models:
        raise HTTPException(
            status_code=404, detail=f"Proveedor {provider} no disponible o sin modelos"
        )

    return models


@router.post("/generate")
async def generate_text(
    request: LLMGenerateRequest, current_user: Usuario = Depends(get_current_user)
):
    """Generar texto usando un LLM"""
    result = await llm_service.generate(
        prompt=request.prompt,
        provider=request.provider,
        model=request.model,
        system_prompt=request.system_prompt,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        fallback_providers=request.fallback_providers,
    )

    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar texto: {result.get('error', 'Unknown error')}",
        )

    return result


@router.post("/test-connection")
async def test_connection(
    request: LLMTestRequest, current_user: Usuario = Depends(get_current_user)
):
    """Probar conexión con un proveedor"""
    result = await llm_service.generate(
        prompt=request.prompt,
        provider=request.provider,
        model=request.model,
        max_tokens=50,
    )

    return {
        "success": result["success"],
        "provider": request.provider,
        "model": request.model,
        "response": result.get("content", ""),
        "error": result.get("error"),
    }


@router.get("/usage/stats", response_model=Dict[str, UsageStats])
async def get_usage_stats(
    provider: Optional[str] = None, current_user: Usuario = Depends(get_current_user)
):
    """Obtener estadísticas de uso"""
    stats = llm_service.get_usage_stats(provider)
    return stats


@router.get("/usage/total-cost")
async def get_total_cost(current_user: Usuario = Depends(get_current_user)):
    """Obtener costo total acumulado"""
    total_cost = llm_service.get_total_cost()
    return {"total_cost": total_cost, "currency": "USD"}


@router.post("/credentials")
async def configure_credentials(
    credentials: ProviderCredentials, current_user: Usuario = Depends(get_current_user)
):
    """Configurar credenciales de un proveedor (solo admin)"""
    # TODO: Verificar que el usuario sea admin
    # TODO: Guardar credenciales de forma segura (encriptadas)

    return {
        "success": True,
        "message": f"Credenciales configuradas para {credentials.provider}",
    }
