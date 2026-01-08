import enum
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class RolEnum(str, enum.Enum):
    MEDICO = "medico"
    ENFERMERO = "enfermero"
    ADMINISTRATIVO = "administrativo"
    ESPECIALISTA = "especialista"
    ADMIN = "admin"


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nombre_completo = Column(String(255), nullable=False)
    rol = Column(String(50), nullable=False)
    especialidad = Column(String(100))
    cedula_profesional = Column(String(50))
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # ✅ CLAVE: FK que enlaza usuarios -> instituciones
    institucion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("instituciones.id"),
        nullable=True,  # ponlo en False si SIEMPRE deben pertenecer a una institución
        index=True,
    )

    # ✅ Relación inversa
    institucion = relationship("Institucion", back_populates="usuarios")

    # Relaciones de seguridad
    two_factor_auth = relationship(
        "TwoFactorAuth",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan",
    )
    sessions = relationship(
        "UserSession",
        back_populates="usuario",
        cascade="all, delete-orphan",
    )
    roles = relationship(
        "UserRole",
        foreign_keys="UserRole.usuario_id",
        back_populates="usuario",
        cascade="all, delete-orphan",
    )

    # Relaciones de dominio
    consultas_remotas = relationship("ConsultaRemota", back_populates="medico")
    prescripciones_emitidas = relationship(
        "PrescripcionElectronica", back_populates="medico"
    )

    # Relaciones de cumplimiento
    firmas_electronicas = relationship(
        "FirmaElectronica",
        back_populates="usuario",
        cascade="all, delete-orphan",
    )
    logs_acceso_sensible = relationship(
        "LogAccesoSensible",
        back_populates="usuario",
        cascade="all, delete-orphan",
    )
