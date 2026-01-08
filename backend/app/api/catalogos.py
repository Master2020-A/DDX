"""
API endpoints para catálogos del sistema
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.core.database import get_db
from app.models.catalogos import (
    CodigoPostal,
    InstitucionSalud,
    Parentesco,
    NivelEscolaridad,
    TipoExamenLaboratorio,
    SustanciaToxica,
)
from app.services.codigo_postal import CodigoPostalService

router = APIRouter(tags=["Catálogos"])


@router.get("/codigo-postal/{cp}")
async def obtener_datos_cp(cp: str, db: AsyncSession = Depends(get_db)):
    """
    Obtener información geográfica por código postal
    Consulta primero BD local, luego API SEPOMEX si no existe
    """
    try:
        print(f"🔍 Buscando CP: {cp}")
        service = CodigoPostalService(db)
        datos = await service.buscar_por_cp(cp)

        if not datos:
            print(f"❌ CP {cp} no encontrado en ninguna fuente")
            raise HTTPException(
                status_code=404, detail=f"Código postal {cp} no encontrado"
            )

        print(f"✅ CP {cp} encontrado: {datos.get('estado')}, {datos.get('municipio')}")
        return datos
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error inesperado buscando CP {cp}: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error al buscar código postal: {str(e)}"
        )


@router.get("/instituciones-salud")
async def listar_instituciones(
    pais: Optional[str] = "México",
    estado: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Listar instituciones de salud filtradas por ubicación"""
    query = select(InstitucionSalud).where(
        InstitucionSalud.activo == True, InstitucionSalud.pais == pais
    )

    if estado:
        query = query.where(InstitucionSalud.estado == estado)

    result = await db.execute(query.order_by(InstitucionSalud.nombre))
    instituciones = result.scalars().all()

    return [
        {
            "id": str(inst.id),
            "nombre": inst.nombre,
            "tipo": inst.tipo,
            "estado": inst.estado,
            "municipio": inst.municipio,
            "nivel_atencion": inst.nivel_atencion,
        }
        for inst in instituciones
    ]


@router.get("/parentescos")
async def listar_parentescos(db: AsyncSession = Depends(get_db)):
    """Listar tipos de parentesco"""
    result = await db.execute(
        select(Parentesco)
        .where(Parentesco.activo == True)
        .order_by(Parentesco.orden, Parentesco.nombre)
    )
    parentescos = result.scalars().all()

    return [{"id": str(p.id), "nombre": p.nombre} for p in parentescos]


@router.get("/escolaridades")
async def listar_escolaridades(
    pais: Optional[str] = "México", db: AsyncSession = Depends(get_db)
):
    """Listar niveles de escolaridad"""
    result = await db.execute(
        select(NivelEscolaridad)
        .where(NivelEscolaridad.activo == True, NivelEscolaridad.pais == pais)
        .order_by(NivelEscolaridad.orden, NivelEscolaridad.nombre)
    )
    niveles = result.scalars().all()

    return [{"id": str(n.id), "nombre": n.nombre} for n in niveles]


@router.get("/examenes-laboratorio")
async def listar_examenes(db: AsyncSession = Depends(get_db)):
    """Listar tipos de exámenes de laboratorio"""
    result = await db.execute(
        select(TipoExamenLaboratorio)
        .where(TipoExamenLaboratorio.activo == True)
        .order_by(TipoExamenLaboratorio.categoria, TipoExamenLaboratorio.orden)
    )
    examenes = result.scalars().all()

    return [
        {
            "id": str(e.id),
            "nombre": e.nombre,
            "categoria": e.categoria,
            "descripcion": e.descripcion,
        }
        for e in examenes
    ]


@router.get("/sustancias-toxicas")
async def listar_sustancias(db: AsyncSession = Depends(get_db)):
    """Listar sustancias tóxicas conocidas"""
    result = await db.execute(
        select(SustanciaToxica)
        .where(SustanciaToxica.activo == True)
        .order_by(SustanciaToxica.categoria, SustanciaToxica.orden)
    )
    sustancias = result.scalars().all()

    return [
        {
            "id": str(s.id),
            "nombre": s.nombre,
            "categoria": s.categoria,
            "nivel_peligrosidad": s.nivel_peligrosidad,
        }
        for s in sustancias
    ]
