"""
Schemas de Pydantic para el Marketplace de Templates
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


# ============================================================
# WORKFLOW TEMPLATE SCHEMAS
# ============================================================


class WorkflowTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: str
    tags: List[str] = []
    thumbnail_url: Optional[str] = None
    screenshots: List[str] = []
    version: str = "1.0.0"
    readme: Optional[str] = None
    usage_instructions: Optional[str] = None


class WorkflowTemplateCreate(WorkflowTemplateBase):
    workflow_data: Dict[str, Any]  # nodes, edges, config
    organization: Optional[str] = None
    is_free: bool = True
    price: float = 0.0


class WorkflowTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    workflow_data: Optional[Dict[str, Any]] = None
    thumbnail_url: Optional[str] = None
    screenshots: Optional[List[str]] = None
    version: Optional[str] = None
    readme: Optional[str] = None
    usage_instructions: Optional[str] = None
    changelog: Optional[str] = None


class WorkflowTemplatePublish(BaseModel):
    readme: str = Field(..., min_length=50)
    usage_instructions: str = Field(..., min_length=20)
    changelog: Optional[str] = None


class WorkflowTemplateInDB(WorkflowTemplateBase):
    id: UUID
    author_id: UUID
    author_name: str
    organization: Optional[str]
    workflow_data: Dict[str, Any]
    min_system_version: Optional[str]
    dependencies: Dict[str, Any]
    downloads_count: int
    installs_count: int
    rating_average: float
    rating_count: int
    views_count: int
    status: str
    is_featured: bool
    is_verified: bool
    is_free: bool
    price: float
    changelog: Optional[str]
    created_at: str
    updated_at: str
    published_at: Optional[str]

    class Config:
        from_attributes = True


class WorkflowTemplatePublic(BaseModel):
    """Template público (sin workflow_data completo)"""

    id: UUID
    name: str
    description: Optional[str]
    category: str
    tags: List[str]
    author_name: str
    organization: Optional[str]
    thumbnail_url: Optional[str]
    version: str
    downloads_count: int
    installs_count: int
    rating_average: float
    rating_count: int
    is_featured: bool
    is_verified: bool
    is_free: bool
    price: float
    created_at: str
    published_at: Optional[str]

    class Config:
        from_attributes = True


class WorkflowTemplateDetail(WorkflowTemplateInDB):
    """Template con todos los detalles incluyendo workflow_data"""

    pass


# ============================================================
# TEMPLATE REVIEW SCHEMAS
# ============================================================


class TemplateReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=200)
    comment: Optional[str] = None


class TemplateReviewCreate(TemplateReviewBase):
    template_id: UUID


class TemplateReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = None
    comment: Optional[str] = None


class TemplateReviewInDB(TemplateReviewBase):
    id: UUID
    template_id: UUID
    user_id: UUID
    helpful_count: int
    not_helpful_count: int
    is_verified_purchase: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# ============================================================
# TEMPLATE INSTALLATION SCHEMAS
# ============================================================


class TemplateInstallationCreate(BaseModel):
    template_id: UUID
    customizations: Dict[str, Any] = {}


class TemplateInstallationInDB(BaseModel):
    id: UUID
    template_id: UUID
    user_id: UUID
    workflow_id: Optional[UUID]
    installed_version: str
    customizations: Dict[str, Any]
    is_active: bool
    last_used_at: Optional[str]
    installed_at: str

    class Config:
        from_attributes = True


# ============================================================
# TEMPLATE CATEGORY SCHEMAS
# ============================================================


class TemplateCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class TemplateCategoryCreate(TemplateCategoryBase):
    display_order: int = 0


class TemplateCategoryInDB(TemplateCategoryBase):
    id: UUID
    display_order: int
    is_active: bool
    templates_count: int
    created_at: str

    class Config:
        from_attributes = True


# ============================================================
# TEMPLATE COLLECTION SCHEMAS
# ============================================================


class TemplateCollectionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    slug: str = Field(..., min_length=1, max_length=200)


class TemplateCollectionCreate(TemplateCollectionBase):
    template_ids: List[UUID] = []
    cover_image_url: Optional[str] = None
    is_public: bool = True


class TemplateCollectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    template_ids: Optional[List[UUID]] = None
    cover_image_url: Optional[str] = None
    is_public: Optional[bool] = None


class TemplateCollectionInDB(TemplateCollectionBase):
    id: UUID
    curator_id: UUID
    curator_name: str
    template_ids: List[UUID]
    cover_image_url: Optional[str]
    is_featured: bool
    is_public: bool
    views_count: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# ============================================================
# SEARCH AND FILTER SCHEMAS
# ============================================================


class TemplateSearchParams(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    is_free: Optional[bool] = None
    is_verified: Optional[bool] = None
    sort_by: str = "downloads"  # downloads, rating, recent, popular
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class TemplateSearchResult(BaseModel):
    templates: List[WorkflowTemplatePublic]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================
# STATISTICS SCHEMAS
# ============================================================


class MarketplaceStats(BaseModel):
    total_templates: int
    total_downloads: int
    total_installs: int
    total_reviews: int
    average_rating: float
    featured_templates: int
    verified_templates: int
    categories_count: int
    top_categories: List[Dict[str, Any]]
    trending_templates: List[WorkflowTemplatePublic]


class TemplateStats(BaseModel):
    template_id: UUID
    downloads_count: int
    installs_count: int
    views_count: int
    rating_average: float
    rating_count: int
    rating_distribution: Dict[int, int]  # {1: count, 2: count, ...}
    recent_reviews: List[TemplateReviewInDB]
    download_trend: List[Dict[str, Any]]  # [{date, count}, ...]
