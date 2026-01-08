"""
Servicio para el Marketplace de Templates de Workflows
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.models.marketplace import (
    MarketplaceTemplate,
    MarketplaceReview,
    MarketplaceInstallation,
    MarketplaceCategory,
    MarketplaceCollection,
)
from app.models.workflow import Workflow
from app.schemas.marketplace import (
    WorkflowTemplateCreate,
    WorkflowTemplateUpdate,
    TemplateSearchParams,
    TemplateReviewCreate,
    TemplateInstallationCreate,
)


class MarketplaceService:
    """Servicio para gestionar el marketplace de templates"""

    @staticmethod
    async def create_template(
        db: AsyncSession,
        template_data: WorkflowTemplateCreate,
        user_id: UUID,
        user_name: str,
    ) -> MarketplaceTemplate:
        """Crear un nuevo template"""
        template = MarketplaceTemplate(
            **template_data.model_dump(),
            author_id=user_id,
            author_name=user_name,
            status="draft",
        )
        db.add(template)
        await db.commit()
        await db.refresh(template)
        return template

    @staticmethod
    async def update_template(
        db: AsyncSession,
        template_id: UUID,
        template_data: WorkflowTemplateUpdate,
        user_id: UUID,
    ) -> Optional[MarketplaceTemplate]:
        """Actualizar un template"""
        result = await db.execute(
            select(MarketplaceTemplate).where(
                and_(
                    MarketplaceTemplate.id == template_id,
                    MarketplaceTemplate.author_id == user_id,
                )
            )
        )
        template = result.scalar_one_or_none()

        if not template:
            return None

        update_data = template_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(template, field, value)

        template.updated_at = datetime.utcnow().isoformat()
        await db.commit()
        await db.refresh(template)
        return template

    @staticmethod
    async def publish_template(
        db: AsyncSession, template_id: UUID, user_id: UUID
    ) -> Optional[MarketplaceTemplate]:
        """Publicar un template (cambiar status a pending)"""
        result = await db.execute(
            select(MarketplaceTemplate).where(
                and_(
                    MarketplaceTemplate.id == template_id,
                    MarketplaceTemplate.author_id == user_id,
                )
            )
        )
        template = result.scalar_one_or_none()

        if not template:
            return None

        template.status = "pending"
        template.updated_at = datetime.utcnow().isoformat()
        await db.commit()
        await db.refresh(template)
        return template

    @staticmethod
    async def approve_template(
        db: AsyncSession, template_id: UUID
    ) -> Optional[MarketplaceTemplate]:
        """Aprobar un template (solo admin)"""
        result = await db.execute(
            select(MarketplaceTemplate).where(MarketplaceTemplate.id == template_id)
        )
        template = result.scalar_one_or_none()

        if not template:
            return None

        template.status = "approved"
        template.published_at = datetime.utcnow().isoformat()
        template.updated_at = datetime.utcnow().isoformat()
        await db.commit()
        await db.refresh(template)
        return template

    @staticmethod
    async def search_templates(
        db: AsyncSession, params: TemplateSearchParams
    ) -> tuple[List[MarketplaceTemplate], int]:
        """Buscar templates con filtros"""
        query = select(MarketplaceTemplate).where(
            MarketplaceTemplate.status == "approved"
        )

        # Filtros
        if params.query:
            search_term = f"%{params.query}%"
            query = query.where(
                or_(
                    MarketplaceTemplate.name.ilike(search_term),
                    MarketplaceTemplate.description.ilike(search_term),
                )
            )

        if params.category:
            query = query.where(MarketplaceTemplate.category == params.category)

        if params.tags:
            query = query.where(MarketplaceTemplate.tags.overlap(params.tags))

        if params.min_rating is not None:
            query = query.where(MarketplaceTemplate.rating_average >= params.min_rating)

        if params.is_free is not None:
            query = query.where(MarketplaceTemplate.is_free == params.is_free)

        if params.is_verified is not None:
            query = query.where(MarketplaceTemplate.is_verified == params.is_verified)

        # Ordenamiento
        if params.sort_by == "downloads":
            query = query.order_by(desc(MarketplaceTemplate.downloads_count))
        elif params.sort_by == "rating":
            query = query.order_by(desc(MarketplaceTemplate.rating_average))
        elif params.sort_by == "recent":
            query = query.order_by(desc(MarketplaceTemplate.published_at))
        elif params.sort_by == "popular":
            query = query.order_by(desc(MarketplaceTemplate.views_count))

        # Contar total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Paginación
        offset = (params.page - 1) * params.page_size
        query = query.offset(offset).limit(params.page_size)

        result = await db.execute(query)
        templates = result.scalars().all()

        return list(templates), total

    @staticmethod
    async def get_template_by_id(
        db: AsyncSession, template_id: UUID, increment_views: bool = True
    ) -> Optional[MarketplaceTemplate]:
        """Obtener un template por ID"""
        result = await db.execute(
            select(MarketplaceTemplate).where(MarketplaceTemplate.id == template_id)
        )
        template = result.scalar_one_or_none()

        if template and increment_views:
            template.views_count += 1
            await db.commit()
            await db.refresh(template)

        return template

    @staticmethod
    async def install_template(
        db: AsyncSession, installation_data: TemplateInstallationCreate, user_id: UUID
    ) -> tuple[MarketplaceInstallation, Workflow]:
        """Instalar un template (crear workflow desde template)"""
        # Obtener template
        template = await MarketplaceService.get_template_by_id(
            db, installation_data.template_id, increment_views=False
        )

        if not template:
            raise ValueError("Template no encontrado")

        # Crear workflow desde template
        workflow_data = template.workflow_data
        workflow = Workflow(
            name=f"{template.name} (Instalado)",
            description=template.description,
            nodes=workflow_data.get("nodes", []),
            edges=workflow_data.get("edges", []),
            config=workflow_data.get("config", {}),
            variables=workflow_data.get("variables", {}),
            created_by_id=user_id,
            status="draft",
        )
        db.add(workflow)
        await db.flush()

        # Registrar instalación
        installation = MarketplaceInstallation(
            template_id=template.id,
            user_id=user_id,
            workflow_id=workflow.id,
            installed_version=template.version,
            customizations=installation_data.customizations,
        )
        db.add(installation)

        # Actualizar contadores
        template.installs_count += 1
        template.downloads_count += 1

        await db.commit()
        await db.refresh(installation)
        await db.refresh(workflow)

        return installation, workflow

    @staticmethod
    async def create_review(
        db: AsyncSession, review_data: TemplateReviewCreate, user_id: UUID
    ) -> MarketplaceReview:
        """Crear una reseña"""
        # Verificar que el usuario haya instalado el template
        result = await db.execute(
            select(MarketplaceInstallation).where(
                and_(
                    MarketplaceInstallation.template_id == review_data.template_id,
                    MarketplaceInstallation.user_id == user_id,
                )
            )
        )
        installation = result.scalar_one_or_none()

        review = MarketplaceReview(
            **review_data.model_dump(),
            user_id=user_id,
            is_verified_purchase=installation is not None,
        )
        db.add(review)
        await db.flush()

        # Actualizar rating del template
        await MarketplaceService._update_template_rating(db, review_data.template_id)

        await db.commit()
        await db.refresh(review)
        return review

    @staticmethod
    async def _update_template_rating(db: AsyncSession, template_id: UUID):
        """Actualizar el rating promedio de un template"""
        result = await db.execute(
            select(
                func.avg(MarketplaceReview.rating), func.count(MarketplaceReview.id)
            ).where(MarketplaceReview.template_id == template_id)
        )
        avg_rating, count = result.one()

        template_result = await db.execute(
            select(MarketplaceTemplate).where(MarketplaceTemplate.id == template_id)
        )
        template = template_result.scalar_one_or_none()

        if template:
            template.rating_average = float(avg_rating or 0)
            template.rating_count = count or 0

    @staticmethod
    async def get_featured_templates(
        db: AsyncSession, limit: int = 10
    ) -> List[MarketplaceTemplate]:
        """Obtener templates destacados"""
        result = await db.execute(
            select(MarketplaceTemplate)
            .where(
                and_(
                    MarketplaceTemplate.status == "approved",
                    MarketplaceTemplate.is_featured == True,
                )
            )
            .order_by(desc(MarketplaceTemplate.rating_average))
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_trending_templates(
        db: AsyncSession, limit: int = 10
    ) -> List[MarketplaceTemplate]:
        """Obtener templates en tendencia (más instalados recientemente)"""
        result = await db.execute(
            select(MarketplaceTemplate)
            .where(MarketplaceTemplate.status == "approved")
            .order_by(desc(MarketplaceTemplate.installs_count))
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_categories(db: AsyncSession) -> List[MarketplaceCategory]:
        """Obtener todas las categorías"""
        result = await db.execute(
            select(MarketplaceCategory)
            .where(MarketplaceCategory.is_active == True)
            .order_by(MarketplaceCategory.display_order)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_user_templates(
        db: AsyncSession, user_id: UUID
    ) -> List[MarketplaceTemplate]:
        """Obtener templates creados por un usuario"""
        result = await db.execute(
            select(MarketplaceTemplate)
            .where(MarketplaceTemplate.author_id == user_id)
            .order_by(desc(MarketplaceTemplate.created_at))
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_user_installations(
        db: AsyncSession, user_id: UUID
    ) -> List[MarketplaceInstallation]:
        """Obtener templates instalados por un usuario"""
        result = await db.execute(
            select(MarketplaceInstallation)
            .where(MarketplaceInstallation.user_id == user_id)
            .order_by(desc(MarketplaceInstallation.installed_at))
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_marketplace_stats(db: AsyncSession) -> Dict[str, Any]:
        """Obtener estadísticas del marketplace"""
        # Total templates
        total_templates_result = await db.execute(
            select(func.count())
            .select_from(MarketplaceTemplate)
            .where(MarketplaceTemplate.status == "approved")
        )
        total_templates = total_templates_result.scalar()

        # Total downloads e installs
        stats_result = await db.execute(
            select(
                func.sum(MarketplaceTemplate.downloads_count),
                func.sum(MarketplaceTemplate.installs_count),
                func.avg(MarketplaceTemplate.rating_average),
            ).where(MarketplaceTemplate.status == "approved")
        )
        total_downloads, total_installs, avg_rating = stats_result.one()

        # Total reviews
        total_reviews_result = await db.execute(
            select(func.count()).select_from(MarketplaceReview)
        )
        total_reviews = total_reviews_result.scalar()

        # Featured y verified
        featured_result = await db.execute(
            select(func.count())
            .select_from(MarketplaceTemplate)
            .where(
                and_(
                    MarketplaceTemplate.status == "approved",
                    MarketplaceTemplate.is_featured == True,
                )
            )
        )
        featured_count = featured_result.scalar()

        verified_result = await db.execute(
            select(func.count())
            .select_from(MarketplaceTemplate)
            .where(
                and_(
                    MarketplaceTemplate.status == "approved",
                    MarketplaceTemplate.is_verified == True,
                )
            )
        )
        verified_count = verified_result.scalar()

        return {
            "total_templates": total_templates,
            "total_downloads": int(total_downloads or 0),
            "total_installs": int(total_installs or 0),
            "total_reviews": total_reviews,
            "average_rating": float(avg_rating or 0),
            "featured_templates": featured_count,
            "verified_templates": verified_count,
        }
