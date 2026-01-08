"""
Modelos de catálogos para el sistema DDX
"""
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class CodigoPostal(Base):
    """Catálogo de Códigos Postales con información geográfica"""
    __tablename__ = "codigos_postales"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo_postal = Column(String(10), nullable=False, index=True)  # Removido unique=True para permitir múltiples colonias
    pais = Column(String(100), nullable=False, default="México")
    estado = Column(String(100), nullable=False, index=True)
    municipio = Column(String(150), nullable=False)
    ciudad = Column(String(150))
    colonia = Column(String(200))
    activo = Column(Boolean, default=True)


class InstitucionSalud(Base):
    """Catálogo de Instituciones de Salud por región"""
    __tablename__ = "instituciones_salud"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(200), nullable=False)  # IMSS, ISSSTE, SSA, etc.
    tipo = Column(String(100))  # Pública, Privada, Seguridad Social
    pais = Column(String(100), nullable=False, default="México", index=True)
    estado = Column(String(100), index=True)
    municipio = Column(String(150))
    localidad = Column(String(200))
    direccion = Column(String(500))
    telefono = Column(String(20))
    nivel_atencion = Column(String(50))  # Primer nivel, Segundo nivel, Tercer nivel
    activo = Column(Boolean, default=True)


class Parentesco(Base):
    """Catálogo de tipos de parentesco"""
    __tablename__ = "parentescos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100), nullable=False, unique=True)  # Madre, Padre, Tío, etc.
    orden = Column(Integer, default=0)  # Para ordenar en el select
    activo = Column(Boolean, default=True)


class NivelEscolaridad(Base):
    """Catálogo de niveles de escolaridad"""
    __tablename__ = "niveles_escolaridad"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100), nullable=False)  # Primaria, Secundaria, etc.
    pais = Column(String(100), default="México")  # Por si varía por país
    orden = Column(Integer, default=0)
    activo = Column(Boolean, default=True)


class TipoExamenLaboratorio(Base):
    """Catálogo de tipos de exámenes de laboratorio"""
    __tablename__ = "tipos_examen_laboratorio"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(200), nullable=False)  # Biometría Hemática, Química Sanguínea, etc.
    categoria = Column(String(100))  # Laboratorio, Gabinete
    descripcion = Column(String(500))
    orden = Column(Integer, default=0)
    activo = Column(Boolean, default=True)


class SustanciaToxica(Base):
    """Catálogo de sustancias tóxicas conocidas"""
    __tablename__ = "sustancias_toxicas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(200), nullable=False, unique=True)  # Cocaína, Cannabis, LSD, etc.
    categoria = Column(String(100))  # Droga, Químico, Inhalante, etc.
    descripcion = Column(String(500))
    nivel_peligrosidad = Column(String(50))  # Bajo, Medio, Alto
    orden = Column(Integer, default=0)
    activo = Column(Boolean, default=True)
