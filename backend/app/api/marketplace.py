"""
API Endpoints para el Marketplace de Templates de Workflows
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.usuario import Usuario
from app.schemas.marketplace import (
    WorkflowTemplateCreate,
    WorkflowTemplateUpdate,
    WorkflowTemplatePublish,
    WorkflowTemplateInDB,
    WorkflowTemplatePublic,
    WorkflowTemplateDetail,
    TemplateSearchParams,
    TemplateSearchResult,
    TemplateReviewCreate,
    TemplateReviewInDB,
    TemplateInstallationCreate,
    TemplateInstallationInDB,
    TemplateCategoryInDB,
    MarketplaceStats,
)
from app.services.marketplace_service import MarketplaceService

router = APIRouter()


# ============================================================
# ENDPOINTS DE TEMPLATES
# ============================================================


@router.get("/templates", response_model=TemplateSearchResult)
async def search_templates(
    query: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    min_rating: Optional[float] = None,
    is_free: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    sort_by: str = "downloads",
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """Buscar templates en el marketplace"""
    tags_list = tags.split(",") if tags else None

    params = TemplateSearchParams(
        query=query,
        category=category,
        tags=tags_list,
        min_rating=min_rating,
        is_free=is_free,
        is_verified=is_verified,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )

    templates, total = await MarketplaceService.search_templates(db, params)

    total_pages = (total + page_size - 1) // page_size

    return {
        "templates": templates,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/templates/featured", response_model=List[WorkflowTemplatePublic])
async def get_featured_templates(limit: int = 10, db: AsyncSession = Depends(get_db)):
    """Obtener templates destacados"""
    templates = await MarketplaceService.get_featured_templates(db, limit)
    return templates


@router.get("/templates/trending", response_model=List[WorkflowTemplatePublic])
async def get_trending_templates(limit: int = 10, db: AsyncSession = Depends(get_db)):
    """Obtener templates en tendencia"""
    templates = await MarketplaceService.get_trending_templates(db, limit)
    return templates


@router.get("/templates/{template_id}", response_model=WorkflowTemplateDetail)
async def get_template(template_id: UUID, db: AsyncSession = Depends(get_db)):
    """Obtener detalles de un template"""
    template = await MarketplaceService.get_template_by_id(db, template_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template no encontrado")

    return template


@router.post("/templates", response_model=WorkflowTemplateInDB)
async def create_template(
    template_data: WorkflowTemplateCreate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Crear un nuevo template"""
    template = await MarketplaceService.create_template(
        db, template_data, current_user.id, current_user.nombre_completo
    )
    return template


@router.put("/templates/{template_id}", response_model=WorkflowTemplateInDB)
async def update_template(
    template_id: UUID,
    template_data: WorkflowTemplateUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Actualizar un template"""
    template = await MarketplaceService.update_template(
        db, template_id, template_data, current_user.id
    )

    if not template:
        raise HTTPException(
            status_code=404, detail="Template no encontrado o no tienes permisos"
        )

    return template


@router.post("/templates/{template_id}/publish", response_model=WorkflowTemplateInDB)
async def publish_template(
    template_id: UUID,
    publish_data: WorkflowTemplatePublish,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Publicar un template (enviar a revisión)"""
    # Actualizar readme y usage_instructions
    update_data = WorkflowTemplateUpdate(
        readme=publish_data.readme,
        usage_instructions=publish_data.usage_instructions,
        changelog=publish_data.changelog,
    )

    template = await MarketplaceService.update_template(
        db, template_id, update_data, current_user.id
    )

    if not template:
        raise HTTPException(
            status_code=404, detail="Template no encontrado o no tienes permisos"
        )

    # Cambiar status a pending
    template = await MarketplaceService.publish_template(
        db, template_id, current_user.id
    )

    return template


@router.post("/templates/{template_id}/approve", response_model=WorkflowTemplateInDB)
async def approve_template(
    template_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Aprobar un template (solo admin)"""
    # TODO: Verificar que el usuario sea admin

    template = await MarketplaceService.approve_template(db, template_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template no encontrado")

    return template


@router.get("/templates/user/my-templates", response_model=List[WorkflowTemplateInDB])
async def get_my_templates(
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtener mis templates creados"""
    templates = await MarketplaceService.get_user_templates(db, current_user.id)
    return templates


# ============================================================
# ENDPOINTS DE INSTALACIÓN
# ============================================================


@router.post("/templates/{template_id}/install", response_model=dict)
async def install_template(
    template_id: UUID,
    customizations: dict = {},
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Instalar un template (crear workflow desde template)"""
    installation_data = TemplateInstallationCreate(
        template_id=template_id, customizations=customizations
    )

    try:
        installation, workflow = await MarketplaceService.install_template(
            db, installation_data, current_user.id
        )

        return {
            "installation_id": installation.id,
            "workflow_id": workflow.id,
            "workflow_name": workflow.name,
            "message": "Template instalado exitosamente",
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/installations", response_model=List[TemplateInstallationInDB])
async def get_my_installations(
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtener mis templates instalados"""
    installations = await MarketplaceService.get_user_installations(db, current_user.id)
    return installations


# ============================================================
# ENDPOINTS DE RESEÑAS
# ============================================================


@router.post("/templates/{template_id}/reviews", response_model=TemplateReviewInDB)
async def create_review(
    template_id: UUID,
    rating: int = Query(..., ge=1, le=5),
    title: Optional[str] = None,
    comment: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Crear una reseña para un template"""
    review_data = TemplateReviewCreate(
        template_id=template_id, rating=rating, title=title, comment=comment
    )

    review = await MarketplaceService.create_review(db, review_data, current_user.id)
    return review


@router.get("/templates/{template_id}/reviews", response_model=List[TemplateReviewInDB])
async def get_template_reviews(
    template_id: UUID,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """Obtener reseñas de un template"""
    from sqlalchemy import select, desc
    from app.models.marketplace import TemplateReview

    result = await db.execute(
        select(TemplateReview)
        .where(TemplateReview.template_id == template_id)
        .order_by(desc(TemplateReview.created_at))
        .offset(offset)
        .limit(limit)
    )
    reviews = result.scalars().all()
    return list(reviews)


# ============================================================
# ENDPOINTS DE CATEGORÍAS
# ============================================================


@router.get("/categories", response_model=List[TemplateCategoryInDB])
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Obtener todas las categorías"""
    categories = await MarketplaceService.get_categories(db)
    return categories


# ============================================================
# ENDPOINTS DE ESTADÍSTICAS
# ============================================================


@router.get("/stats", response_model=MarketplaceStats)
async def get_marketplace_stats(db: AsyncSession = Depends(get_db)):
    """Obtener estadísticas del marketplace"""
    stats = await MarketplaceService.get_marketplace_stats(db)

    # Obtener top categories
    from sqlalchemy import select, func, desc
    from app.models.marketplace import WorkflowTemplate

    result = await db.execute(
        select(
            WorkflowTemplate.category, func.count(WorkflowTemplate.id).label("count")
        )
        .where(WorkflowTemplate.status == "approved")
        .group_by(WorkflowTemplate.category)
        .order_by(desc("count"))
        .limit(5)
    )
    top_categories = [{"category": row[0], "count": row[1]} for row in result.all()]

    # Obtener trending templates
    trending = await MarketplaceService.get_trending_templates(db, 5)

    return {
        **stats,
        "categories_count": len(top_categories),
        "top_categories": top_categories,
        "trending_templates": trending,
    }


@router.get("/templates/{template_id}/stats")
async def get_template_stats(template_id: UUID, db: AsyncSession = Depends(get_db)):
    """Obtener estadísticas detalladas de un template"""
    from sqlalchemy import select, func
    from app.models.marketplace import TemplateReview

    template = await MarketplaceService.get_template_by_id(
        db, template_id, increment_views=False
    )

    if not template:
        raise HTTPException(status_code=404, detail="Template no encontrado")

    # Distribución de ratings
    result = await db.execute(
        select(TemplateReview.rating, func.count(TemplateReview.id))
        .where(TemplateReview.template_id == template_id)
        .group_by(TemplateReview.rating)
    )
    rating_distribution = {row[0]: row[1] for row in result.all()}

    # Reseñas recientes
    recent_reviews_result = await db.execute(
        select(TemplateReview)
        .where(TemplateReview.template_id == template_id)
        .order_by(TemplateReview.created_at.desc())
        .limit(5)
    )
    recent_reviews = list(recent_reviews_result.scalars().all())

    return {
        "template_id": template_id,
        "downloads_count": template.downloads_count,
        "installs_count": template.installs_count,
        "views_count": template.views_count,
        "rating_average": template.rating_average,
        "rating_count": template.rating_count,
        "rating_distribution": rating_distribution,
        "recent_reviews": recent_reviews,
    }
