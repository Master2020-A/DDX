"""
Modelo para catálogo CIE-10 (Clasificación Internacional de Enfermedades)
"""

from sqlalchemy import Column, String, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import DateTime
import uuid
from app.core.database import Base


class CIE10(Base):
    __tablename__ = "cie10"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(String(10), unique=True, nullable=False, index=True)
    descripcion = Column(Text, nullable=False)
    categoria = Column(String(100), index=True)
    subcategoria = Column(String(200))

    # Campos para búsqueda y filtrado
    keywords = Column(Text)  # Palabras clave para búsqueda
    sinonimos = Column(Text)  # Sinónimos y términos relacionados

    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Índices para búsqueda rápida
    __table_args__ = (
        Index(
            "idx_cie10_descripcion_trgm",
            "descripcion",
            postgresql_using="gin",
            postgresql_ops={"descripcion": "gin_trgm_ops"},
        ),
        Index(
            "idx_cie10_keywords_trgm",
            "keywords",
            postgresql_using="gin",
            postgresql_ops={"keywords": "gin_trgm_ops"},
        ),
    )
