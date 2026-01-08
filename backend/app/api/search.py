"""API endpoint para busqueda global"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import Dict, Any
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.usuario import Usuario
from app.models.paciente import Paciente
from app.models.interconsulta import Interconsulta

router = APIRouter()


@router.get("/")
async def busqueda_global(
    q: str = Query(..., min_length=2, description="Termino de busqueda"),
    limit: int = Query(10, le=50, description="Limite de resultados por categoria"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> Dict[str, Any]:
    """Busqueda global en pacientes e interconsultas."""
    resultados = {"pacientes": [], "interconsultas": [], "query": q}
    search_term = f"%{q}%"

    pacientes_query = (
        select(Paciente)
        .where(
            or_(
                Paciente.nombre_completo.ilike(search_term),
                Paciente.numero_expediente.ilike(search_term),
            )
        )
        .limit(limit)
    )

    pacientes_result = await db.execute(pacientes_query)
    pacientes = pacientes_result.scalars().all()

    resultados["pacientes"] = [
        {
            "id": str(p.id),
            "tipo": "paciente",
            "titulo": p.nombre_completo,
            "subtitulo": f"Expediente: {p.numero_expediente}",
            "url": f"/pacientes/{p.id}",
            "icono": "user",
        }
        for p in pacientes
    ]

    interconsultas_query = (
        select(Interconsulta)
        .where(
            or_(
                Interconsulta.especialidad_requerida.ilike(search_term),
                Interconsulta.motivo_solicitud.ilike(search_term),
            )
        )
        .limit(limit)
    )

    interconsultas_result = await db.execute(interconsultas_query)
    interconsultas = interconsultas_result.scalars().all()

    resultados["interconsultas"] = [
        {
            "id": str(ic.id),
            "tipo": "interconsulta",
            "titulo": f"Interconsulta - {ic.especialidad_requerida}",
            "subtitulo": f"{ic.estado.capitalize()} - {ic.urgencia}",
            "url": "/interconsultas",
            "icono": "arrow-right-left",
        }
        for ic in interconsultas
    ]

    return resultados
