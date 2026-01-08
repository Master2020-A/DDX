"""
Schemas para CIE-10
"""

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class CIE10Base(BaseModel):
    codigo: str
    descripcion: str
    categoria: Optional[str] = None
    subcategoria: Optional[str] = None
    keywords: Optional[str] = None
    sinonimos: Optional[str] = None


class CIE10Create(CIE10Base):
    pass


class CIE10Response(CIE10Base):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CIE10SearchResult(BaseModel):
    """Resultado de búsqueda con score de relevancia"""

    id: UUID
    codigo: str
    descripcion: str
    categoria: Optional[str]
    relevancia: float  # Score de 0 a 1

    class Config:
        from_attributes = True
