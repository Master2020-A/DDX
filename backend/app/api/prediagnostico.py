"""
API endpoints para Pre-diagnóstico Inteligente
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.usuario import Usuario
from app.models.cie10 import CIE10
from app.models.cie11 import CIE11
from app.schemas.cie10 import CIE10SearchResult, CIE10Response
from app.schemas.cie11 import CIE11SearchResult, CIE11Response
from app.api.dependencies import get_current_active_medico
from app.schemas.prediagnostico import (
    PreDiagnosticoRequest,
    PreDiagnosticoResponse,
    AlgoritmoDecisionRequest,
    AlgoritmoDecisionResponse,
)
from app.services.prediagnostico_service import PreDiagnosticoService

router = APIRouter(prefix="/prediagnostico", tags=["Pre-diagnóstico Inteligente"])


@router.post("/generar/test")
async def generar_prediagnostico_test(
    request: PreDiagnosticoRequest,
):
    """
    Endpoint de prueba sin autenticación para debugging
    """
    print(f"📥 TEST Request recibido: {request.model_dump()}")

    try:
        service = PreDiagnosticoService()
        resultado = await service.generar_prediagnostico(request)
        print(f"✅ Pre-diagnóstico generado exitosamente")
        return resultado
    except Exception as e:
        print(f"❌ Error generando pre-diagnóstico: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generar", response_model=PreDiagnosticoResponse)
async def generar_prediagnostico(
    request: PreDiagnosticoRequest,
    current_user: Usuario = Depends(get_current_active_medico),
):
    """
    Genera pre-diagnóstico inteligente basado en síntomas
    Incluye diagnósticos diferenciales, exámenes sugeridos y nivel de urgencia
    """
    print(f"📥 Request recibido: {request}")
    print(f"👤 Usuario: {current_user.email}")

    try:
        service = PreDiagnosticoService()
        resultado = await service.generar_prediagnostico(request)
        print(f"✅ Pre-diagnóstico generado exitosamente")
        return resultado
    except Exception as e:
        print(f"❌ Error generando pre-diagnóstico: {e}")
        import traceback

        traceback.print_exc()
        raise


@router.post("/algoritmo-decision", response_model=AlgoritmoDecisionResponse)
async def ejecutar_algoritmo_decision(
    request: AlgoritmoDecisionRequest,
    current_user: Usuario = Depends(get_current_active_medico),
):
    """
    Ejecuta algoritmo de decisión clínica
    Determina nivel de urgencia y acciones inmediatas
    """
    service = PreDiagnosticoService()
    resultado = await service.ejecutar_algoritmo_decision(request)
    return resultado


@router.get("/cie10/buscar", response_model=List[CIE10SearchResult])
async def buscar_cie10(
    q: str = Query(..., min_length=2, description="Término de búsqueda"),
    limit: int = Query(default=10, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico),
):
    """
    Búsqueda de códigos CIE-10 con autocompletado
    Busca en código, descripción, keywords y sinónimos
    """
    # Búsqueda con ILIKE para PostgreSQL
    search_term = f"%{q}%"

    query = (
        select(CIE10)
        .where(
            or_(
                CIE10.codigo.ilike(search_term),
                CIE10.descripcion.ilike(search_term),
                CIE10.keywords.ilike(search_term),
                CIE10.sinonimos.ilike(search_term),
            )
        )
        .limit(limit)
    )

    result = await db.execute(query)
    resultados = result.scalars().all()

    # Calcular relevancia simple (puede mejorarse con full-text search)
    resultados_con_score = []
    for r in resultados:
        score = 1.0
        # Mayor score si coincide con el código
        if q.upper() in r.codigo.upper():
            score = 1.0
        # Score medio si coincide con descripción
        elif q.lower() in r.descripcion.lower():
            score = 0.8
        else:
            score = 0.5

        resultados_con_score.append(
            CIE10SearchResult(
                id=r.id,
                codigo=r.codigo,
                descripcion=r.descripcion,
                categoria=r.categoria,
                relevancia=score,
            )
        )

    # Ordenar por relevancia
    resultados_con_score.sort(key=lambda x: x.relevancia, reverse=True)

    return resultados_con_score


@router.get("/cie10/{codigo}", response_model=CIE10Response)
async def obtener_cie10_por_codigo(
    codigo: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico),
):
    """
    Obtiene información detallada de un código CIE-10
    """
    result = await db.execute(select(CIE10).where(CIE10.codigo == codigo.upper()))
    cie10 = result.scalar_one_or_none()

    if not cie10:
        raise HTTPException(status_code=404, detail="Código CIE-10 no encontrado")

    return cie10


@router.get("/cie10/categoria/{categoria}", response_model=List[CIE10Response])
async def listar_cie10_por_categoria(
    categoria: str,
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico),
):
    """
    Lista códigos CIE-10 por categoría
    """
    result = await db.execute(
        select(CIE10).where(CIE10.categoria.ilike(f"%{categoria}%")).limit(limit)
    )
    resultados = result.scalars().all()
    return resultados
