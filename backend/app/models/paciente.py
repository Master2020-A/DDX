from datetime import date
import enum
import uuid

from sqlalchemy import (
    Column,
    String,
    Date,
    DateTime,
    ARRAY,
    ForeignKey,
    UniqueConstraint,  # ✅
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class GeneroEnum(str, enum.Enum):
    MASCULINO = "masculino"
    FEMENINO = "femenino"
    OTRO = "otro"
    NO_ESPECIFICA = "no_especifica"


class Paciente(Base):
    __tablename__ = "pacientes"

    # ✅ Unicidad por institución:
    # Un mismo numero_expediente puede repetirse en otra institución,
    # pero NO dentro de la misma.
    __table_args__ = (
        UniqueConstraint(
            "institucion_id",
            "numero_expediente",
            name="uq_pacientes_institucion_expediente",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Multi-tenancy
    institucion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("instituciones.id"),
        nullable=True,  # Recomendación: en multi-tenant real suele ser False
        index=True,
    )

    # ⚠️ Antes: unique=True (global). Ahora: SIN unique=True
    numero_expediente = Column(String(50), nullable=False, index=True)

    nombre_completo = Column(String(255), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    genero = Column(String(20))
    tipo_sangre = Column(String(5))
    telefono = Column(String(20))
    email = Column(String(255))
    direccion = Column(String)
    contacto_emergencia_nombre = Column(String(255))
    contacto_emergencia_telefono = Column(String(20))
    alergias = Column(ARRAY(String))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relación con Institucion
    institucion = relationship("Institucion", back_populates="pacientes")

    # Consultas remotas (telemedicina)
    consultas_remotas = relationship(
        "ConsultaRemota",
        back_populates="paciente",
        cascade="all, delete-orphan",
    )

    prescripciones_electronicas = relationship(
        "PrescripcionElectronica", back_populates="paciente"
    )
    seguimientos = relationship("SeguimientoPostConsulta", back_populates="paciente")

    # Relaciones del Portal del Paciente
    citas_portal = relationship(
        "CitaPaciente", back_populates="paciente", cascade="all, delete-orphan"
    )
    solicitudes_estudios = relationship(
        "SolicitudEstudio", back_populates="paciente", cascade="all, delete-orphan"
    )
    pagos = relationship(
        "PagoServicio", back_populates="paciente", cascade="all, delete-orphan"
    )
    mensajes = relationship(
        "MensajePacienteMedico", back_populates="paciente", cascade="all, delete-orphan"
    )
    recordatorios_medicamentos = relationship(
        "RecordatorioMedicamento",
        back_populates="paciente",
        cascade="all, delete-orphan",
    )
    configuracion_portal = relationship(
        "ConfiguracionPortal",
        back_populates="paciente",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # Interoperabilidad
    historia_unificada = relationship(
        "HistoriaClinicaUnificada",
        back_populates="paciente",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="select",
    )

    # Relaciones
    pruebas_laboratorio = relationship(
        "PruebaLaboratorio", back_populates="paciente", lazy="select"
    )
    consentimientos_informados = relationship(
        "ConsentimientoInformado",
        back_populates="paciente",
        cascade="all, delete-orphan",
    )
    logs_acceso_sensible = relationship(
        "LogAccesoSensible", back_populates="paciente", cascade="all, delete-orphan"
    )
    solicitudes_datos_personales = relationship(
        "SolicitudDatosPersonales",
        back_populates="paciente",
        cascade="all, delete-orphan",
    )

    # Relaciones de IA Médica
    analisis_ia = relationship(
        "AnalisisIA",
        back_populates="paciente",
        cascade="all, delete-orphan",
    )
    predicciones_riesgo = relationship(
        "PrediccionRiesgo",
        back_populates="paciente",
        cascade="all, delete-orphan",
    )
    recomendaciones_tratamiento = relationship(
        "RecomendacionTratamiento",
        back_populates="paciente",
        cascade="all, delete-orphan",
    )
    interacciones_medicamentosas = relationship(
        "InteraccionMedicamentosa",
        back_populates="paciente",
        cascade="all, delete-orphan",
    )
    anomalias_detectadas = relationship(
        "AnomaliaDetectada",
        back_populates="paciente",
        cascade="all, delete-orphan",
    )
    consultas_asistente_ia = relationship(
        "AsistenteIA",
        back_populates="paciente",
        cascade="all, delete-orphan",
    )

    @property
    def edad(self) -> float:
        """Calcula la edad del paciente en años"""
        if not self.fecha_nacimiento:
            return 0.0

        hoy = date.today()
        edad_anos = hoy.year - self.fecha_nacimiento.year

        if hoy.month < self.fecha_nacimiento.month or (
            hoy.month == self.fecha_nacimiento.month
            and hoy.day < self.fecha_nacimiento.day
        ):
            edad_anos -= 1

        return float(edad_anos)

    @property
    def sexo(self) -> str:
        """Retorna sexo en formato M/F para compatibilidad con laboratorio"""
        if not self.genero:
            return "M"

        genero_lower = str(self.genero).lower()
        if "masc" in genero_lower or genero_lower == "m":
            return "M"
        if "fem" in genero_lower or genero_lower == "f":
            return "F"
        return "M"
