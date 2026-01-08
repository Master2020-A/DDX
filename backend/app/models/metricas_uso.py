from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class MetricaUso(Base):
    __tablename__ = "metricas_uso"
    __table_args__ = {"extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    institucion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("instituciones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Campos genéricos (si tu tabla real tiene más, no pasa nada)
    clave = Column(String(100), nullable=True, index=True)
    valor = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Si en Institucion tienes: metricas_uso = relationship("MetricaUso", back_populates="institucion")
    # esto lo satisface.
    institucion = relationship("Institucion", back_populates="metricas_uso")
