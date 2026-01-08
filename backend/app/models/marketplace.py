"""
Modelos para el Marketplace de Templates de Workflows
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from app.core.database import Base


class MarketplaceTemplate(Base):
    """Template de workflow publicado en el marketplace"""

    __tablename__ = "workflow_templates_marketplace"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Información básica
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    category = Column(
        String(100), index=True
    )  # medical, administrative, diagnostic, etc.
    tags = Column(ARRAY(String), default=[])

    # Autor
    author_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    author_name = Column(String(200))
    organization = Column(String(200))

    # Contenido del template
    workflow_data = Column(JSONB, nullable=False)  # nodes, edges, config
    thumbnail_url = Column(String(500))
    screenshots = Column(ARRAY(String), default=[])

    # Versión y compatibilidad
    version = Column(String(20), default="1.0.0")
    min_system_version = Column(String(20))
    dependencies = Column(JSONB, default={})

    # Métricas de uso
    downloads_count = Column(Integer, default=0)
    installs_count = Column(Integer, default=0)
    rating_average = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)

    # Estado y moderación
    status = Column(String(20), default="draft")  # draft, pending, approved, rejected
    is_featured = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    is_free = Column(Boolean, default=True)
    price = Column(Float, default=0.0)

    # Documentación
    readme = Column(Text)
    changelog = Column(Text)
    usage_instructions = Column(Text)

    # Metadatos
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(
        String,
        default=lambda: datetime.utcnow().isoformat(),
        onupdate=lambda: datetime.utcnow().isoformat(),
    )
    published_at = Column(String)

    # Relaciones
    author = relationship("Usuario", foreign_keys=[author_id])
    reviews = relationship(
        "MarketplaceReview", back_populates="template", cascade="all, delete-orphan"
    )
    installations = relationship(
        "MarketplaceInstallation",
        back_populates="template",
        cascade="all, delete-orphan",
    )


class MarketplaceReview(Base):
    """Reseña de un template del marketplace"""

    __tablename__ = "template_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflow_templates_marketplace.id"),
        nullable=False,
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)

    # Calificación
    rating = Column(Integer, nullable=False)  # 1-5
    title = Column(String(200))
    comment = Column(Text)

    # Utilidad
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)

    # Estado
    is_verified_purchase = Column(Boolean, default=False)
    is_moderated = Column(Boolean, default=False)

    # Metadatos
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat())

    # Relaciones
    template = relationship("MarketplaceTemplate", back_populates="reviews")
    user = relationship("Usuario")


class MarketplaceInstallation(Base):
    """Registro de instalación de un template"""

    __tablename__ = "template_installations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflow_templates_marketplace.id"),
        nullable=False,
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"))

    # Información de instalación
    installed_version = Column(String(20))
    customizations = Column(JSONB, default={})

    # Estado
    is_active = Column(Boolean, default=True)
    last_used_at = Column(String)

    # Metadatos
    installed_at = Column(String, default=lambda: datetime.utcnow().isoformat())

    # Relaciones
    template = relationship("MarketplaceTemplate", back_populates="installations")
    user = relationship("Usuario")
    workflow = relationship("Workflow")


class MarketplaceCategory(Base):
    """Categoría de templates en el marketplace"""

    __tablename__ = "template_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)
    icon = Column(String(50))
    color = Column(String(20))

    # Orden y visibilidad
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    # Contador
    templates_count = Column(Integer, default=0)

    # Metadatos
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())


class MarketplaceCollection(Base):
    """Colección curada de templates"""

    __tablename__ = "template_collections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String(200), nullable=False)
    description = Column(Text)
    slug = Column(String(200), unique=True, index=True)

    # Curador
    curator_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    curator_name = Column(String(200))

    # Contenido
    template_ids = Column(ARRAY(UUID(as_uuid=True)), default=[])
    cover_image_url = Column(String(500))

    # Estado
    is_featured = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)

    # Métricas
    views_count = Column(Integer, default=0)

    # Metadatos
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat())

    # Relaciones
    curator = relationship("Usuario")
