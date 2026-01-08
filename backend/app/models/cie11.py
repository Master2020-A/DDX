"""
Modelo para catálogo CIE-11 (Clasificación Internacional de Enfermedades, 11ª revisión)
"""

from sqlalchemy import Column, String, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import DateTime
import uuid
from app.core.database import Base


class CIE11(Base):
    __tablename__ = "cie11"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(String(20), unique=True, nullable=False, index=True)
    descripcion = Column(Text, nullable=False)
    categoria = Column(String(150), index=True)
    subcategoria = Column(String(250))

    # Campos para búsqueda y filtrado
    keywords = Column(Text)  # Palabras clave para búsqueda
    sinonimos = Column(Text)  # Sinónimos y términos relacionados

    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Índices para búsqueda rápida (PostgreSQL trigram)
    __table_args__ = (
        Index(
            "idx_cie11_descripcion_trgm",
            "descripcion",
            postgresql_using="gin",
            postgresql_ops={"descripcion": "gin_trgm_ops"},
        ),
        Index(
            "idx_cie11_keywords_trgm",
            "keywords",
            postgresql_using="gin",
            postgresql_ops={"keywords": "gin_trgm_ops"},
        ),
    )
