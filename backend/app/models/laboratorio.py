"""
Modelos para resultados de laboratorio clínico
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.database import Base


class PruebaLaboratorio(Base):
    """Registro de pruebas de laboratorio realizadas"""
    __tablename__ = 'pruebas_laboratorio'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey('pacientes.id'), nullable=False)
    consulta_id = Column(UUID(as_uuid=True), ForeignKey('consultas.id'), nullable=True)
    medico_id = Column(UUID(as_uuid=True), ForeignKey('usuarios.id'), nullable=False)
    
    # Información general
    fecha_solicitud = Column(DateTime, default=datetime.utcnow)
    fecha_resultado = Column(DateTime, nullable=True)
    laboratorio_externo = Column(String(200), nullable=True)
    numero_orden = Column(String(50), nullable=True)
    
    # Tipo de área
    area = Column(String(50), nullable=False)  # hematologia, quimica_clinica, bacteriologia, etc.
    tipo_prueba = Column(String(100), nullable=False)  # nombre de la prueba específica
    
    # Resultados
    resultados = Column(JSON, nullable=True)  # Almacena todos los valores de la prueba
    interpretacion = Column(Text, nullable=True)  # Interpretación automática
    valores_anormales = Column(JSON, nullable=True)  # Lista de valores fuera de rango
    valores_criticos = Column(JSON, nullable=True)  # Valores que requieren atención inmediata
    
    # Estado y validación
    estado = Column(String(20), default='pendiente')  # pendiente, completado, validado
    requiere_atencion = Column(Boolean, default=False)
    notas_medico = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    paciente = relationship("Paciente", back_populates="pruebas_laboratorio")
    consulta = relationship("Consulta", back_populates="pruebas_laboratorio")
    medico = relationship("Usuario")


class RangoReferencia(Base):
    """Rangos de referencia para pruebas de laboratorio"""
    __tablename__ = 'rangos_referencia'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Identificación de la prueba
    area = Column(String(50), nullable=False)
    tipo_prueba = Column(String(100), nullable=False)
    parametro = Column(String(100), nullable=False)  # Ej: hemoglobina, glucosa, etc.
    
    # Rangos por sexo y edad
    sexo = Column(String(10), nullable=True)  # M, F, ambos (null)
    grupo_etario = Column(String(50), nullable=True)  # recien_nacido, pediatrico, adolescente, adulto, embarazo
    edad_min = Column(Float, nullable=True)  # años
    edad_max = Column(Float, nullable=True)  # años
    
    # Valores de referencia
    valor_min = Column(Float, nullable=True)
    valor_max = Column(Float, nullable=True)
    valor_normal = Column(String(100), nullable=True)  # Para valores cualitativos
    
    # Valores críticos
    critico_bajo = Column(Float, nullable=True)
    critico_alto = Column(Float, nullable=True)
    
    # Unidades y descripción
    unidad = Column(String(50), nullable=True)
    descripcion = Column(Text, nullable=True)
    interpretacion_bajo = Column(Text, nullable=True)
    interpretacion_alto = Column(Text, nullable=True)
    
    # Metadata
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
