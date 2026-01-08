"""
Schemas para CIE-11
"""

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class CIE11Base(BaseModel):
    codigo: str
    descripcion: str
    categoria: Optional[str] = None
    subcategoria: Optional[str] = None
    keywords: Optional[str] = None
    sinonimos: Optional[str] = None


class CIE11Create(CIE11Base):
    pass


class CIE11Response(CIE11Base):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CIE11SearchResult(BaseModel):
    id: UUID
    codigo: str
    descripcion: str
    categoria: Optional[str]
    relevancia: float

    class Config:
        from_attributes = True
