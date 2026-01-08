"""
Modelos para configuración de N8N
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base


class N8NConfig(Base):
    """Configuración de integración con N8N"""

    __tablename__ = "n8n_config"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # API Key para autenticación
    api_key = Column(String(255), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False, default="N8N Integration")
    descripcion = Column(Text, nullable=True)

    # URLs de N8N
    n8n_webhook_url = Column(String(500), nullable=False)
    n8n_api_url = Column(String(500), nullable=True)

    # Estado
    activo = Column(Boolean, default=True, nullable=False)

    # Configuración de webhooks
    webhooks_habilitados = Column(Boolean, default=True, nullable=False)
    timeout_segundos = Column(Integer, default=5, nullable=False)

    # Eventos habilitados (JSON array)
    eventos_habilitados = Column(JSON, nullable=True)

    # Estadísticas
    total_eventos_enviados = Column(Integer, default=0, nullable=False)
    total_eventos_exitosos = Column(Integer, default=0, nullable=False)
    total_eventos_fallidos = Column(Integer, default=0, nullable=False)
    ultimo_evento_enviado = Column(DateTime, nullable=True)

    # Auditoría
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def incrementar_estadisticas(self, exitoso: bool = True):
        """Incrementar estadísticas de envío"""
        self.total_eventos_enviados += 1
        if exitoso:
            self.total_eventos_exitosos += 1
        else:
            self.total_eventos_fallidos += 1
        self.ultimo_evento_enviado = datetime.utcnow()


class N8NEventLog(Base):
    """Log de eventos enviados a N8N"""

    __tablename__ = "n8n_event_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Evento
    evento_tipo = Column(String(100), nullable=False, index=True)
    evento_data = Column(JSON, nullable=False)
    prioridad = Column(String(20), default="normal", nullable=False)

    # Envío
    webhook_url = Column(String(500), nullable=False)
    exitoso = Column(Boolean, nullable=False)
    codigo_http = Column(Integer, nullable=True)
    tiempo_respuesta_ms = Column(Integer, nullable=True)
    error = Column(Text, nullable=True)

    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
