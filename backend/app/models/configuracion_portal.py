# backend/app/models/configuracion_portal.py

"""
Modelo de configuración del portal del paciente
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class ConfiguracionPortal(Base):
    """
    Configuración personalizada del portal para cada paciente
    """

    __tablename__ = "configuracion_portal"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    paciente_id = Column(
        UUID(as_uuid=True),
        ForeignKey("pacientes.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Notificaciones
    notificaciones_email = Column(Boolean, default=True)
    notificaciones_sms = Column(Boolean, default=False)
    notificaciones_push = Column(Boolean, default=True)

    # Privacidad
    compartir_datos_investigacion = Column(Boolean, default=False)
    mostrar_perfil_publico = Column(Boolean, default=False)

    # Preferencias de interfaz
    idioma = Column(String(10), default="es")
    tema = Column(String(20), default="light")  # light, dark, auto
    zona_horaria = Column(String(50), default="America/Mexico_City")

    # Recordatorios
    recordatorios_citas = Column(Boolean, default=True)
    recordatorios_medicamentos = Column(Boolean, default=True)
    recordatorios_estudios = Column(Boolean, default=True)

    # Configuración adicional flexible (JSON)
    configuracion_adicional = Column(JSONB, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación
    paciente = relationship("Paciente", back_populates="configuracion_portal")
