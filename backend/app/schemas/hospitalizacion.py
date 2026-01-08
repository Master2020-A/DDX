"""
Schemas de Pydantic para Hospitalización
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ==================== HOSPITALIZACIÓN ====================


class HospitalizacionBase(BaseModel):
    motivo_ingreso: str
    diagnostico_ingreso: str
    area_hospitalizacion: Optional[str] = None
    numero_cama: Optional[str] = None
    # piso: Optional[str] = None  # Comentado - no existe en BD
    prioridad: str = "normal"
    tipo_ingreso: Optional[str] = None
    alergias_conocidas: Optional[List[str]] = None
    antecedentes_relevantes: Optional[str] = None
    tratamiento_actual: Optional[str] = None
    tipo_seguro: Optional[str] = None
    numero_poliza: Optional[str] = None


class HospitalizacionCreate(HospitalizacionBase):
    paciente_id: UUID
    consulta_id: Optional[UUID] = None


class HospitalizacionUpdate(BaseModel):
    motivo_ingreso: Optional[str] = None
    diagnostico_ingreso: Optional[str] = None
    diagnostico_egreso: Optional[str] = None
    # resumen_clinico: Optional[str] = None  # Comentado temporalmente
    area_hospitalizacion: Optional[str] = None
    numero_cama: Optional[str] = None
    # piso: Optional[str] = None  # Comentado - no existe en BD
    estado: Optional[str] = None
    prioridad: Optional[str] = None
    alergias_conocidas: Optional[List[str]] = None
    antecedentes_relevantes: Optional[str] = None
    tratamiento_actual: Optional[str] = None


class HospitalizacionResponse(HospitalizacionBase):
    id: UUID
    paciente_id: UUID
    consulta_id: Optional[UUID]
    medico_responsable_id: UUID
    fecha_ingreso: datetime
    fecha_alta: Optional[datetime]
    diagnostico_egreso: Optional[str]
    # resumen_clinico: Optional[str]  # Comentado temporalmente
    estado: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== CAMA ====================


class CamaBase(BaseModel):
    numero_cama: str
    area: str
    piso: Optional[str] = None
    habitacion: Optional[str] = None
    tipo_cama: Optional[str] = None
    tiene_oxigeno: bool = False
    tiene_monitor: bool = False
    tiene_ventilador: bool = False
    capacidad_peso: Optional[float] = None
    observaciones: Optional[str] = None


class CamaCreate(CamaBase):
    pass


class CamaUpdate(BaseModel):
    numero_cama: Optional[str] = None
    area: Optional[str] = None
    piso: Optional[str] = None
    habitacion: Optional[str] = None
    estado: Optional[str] = None
    tipo_cama: Optional[str] = None
    tiene_oxigeno: Optional[bool] = None
    tiene_monitor: Optional[bool] = None
    tiene_ventilador: Optional[bool] = None
    capacidad_peso: Optional[float] = None
    observaciones: Optional[str] = None


class CamaResponse(CamaBase):
    id: UUID
    estado: str
    hospitalizacion_actual_id: Optional[UUID]
    fecha_ultima_limpieza: Optional[datetime]
    fecha_ultimo_mantenimiento: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== NOTA DE EVOLUCIÓN ====================


class NotaEvolucionBase(BaseModel):
    tipo_nota: str = "evolucion"
    turno: Optional[str] = None
    subjetivo: Optional[str] = None
    objetivo: Optional[str] = None
    temperatura: Optional[float] = None
    presion_arterial_sistolica: Optional[int] = None
    presion_arterial_diastolica: Optional[int] = None
    frecuencia_cardiaca: Optional[int] = None
    frecuencia_respiratoria: Optional[int] = None
    saturacion_oxigeno: Optional[float] = None
    evaluacion: Optional[str] = None
    plan: Optional[str] = None
    estudios_solicitados: Optional[List[str]] = None
    procedimientos_realizados: Optional[List[str]] = None
    estado_general: Optional[str] = None
    nivel_conciencia: Optional[str] = None
    observaciones: Optional[str] = None


class NotaEvolucionCreate(NotaEvolucionBase):
    hospitalizacion_id: UUID


class NotaEvolucionUpdate(BaseModel):
    tipo_nota: Optional[str] = None
    turno: Optional[str] = None
    subjetivo: Optional[str] = None
    objetivo: Optional[str] = None
    temperatura: Optional[float] = None
    presion_arterial_sistolica: Optional[int] = None
    presion_arterial_diastolica: Optional[int] = None
    frecuencia_cardiaca: Optional[int] = None
    frecuencia_respiratoria: Optional[int] = None
    saturacion_oxigeno: Optional[float] = None
    evaluacion: Optional[str] = None
    plan: Optional[str] = None
    estudios_solicitados: Optional[List[str]] = None
    procedimientos_realizados: Optional[List[str]] = None
    estado_general: Optional[str] = None
    nivel_conciencia: Optional[str] = None
    observaciones: Optional[str] = None


class NotaEvolucionResponse(NotaEvolucionBase):
    id: UUID
    hospitalizacion_id: UUID
    medico_id: UUID
    fecha_nota: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== INDICACIÓN MÉDICA ====================


class IndicacionMedicaBase(BaseModel):
    tipo_indicacion: str
    descripcion: str
    dosis: Optional[str] = None
    via_administracion: Optional[str] = None
    frecuencia: Optional[str] = None
    duracion: Optional[str] = None
    prioridad: str = "normal"
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    observaciones: Optional[str] = None


class IndicacionMedicaCreate(IndicacionMedicaBase):
    hospitalizacion_id: UUID


class IndicacionMedicaUpdate(BaseModel):
    tipo_indicacion: Optional[str] = None
    descripcion: Optional[str] = None
    dosis: Optional[str] = None
    via_administracion: Optional[str] = None
    frecuencia: Optional[str] = None
    duracion: Optional[str] = None
    prioridad: Optional[str] = None
    estado: Optional[str] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    fecha_suspension: Optional[datetime] = None
    motivo_suspension: Optional[str] = None
    observaciones: Optional[str] = None


class IndicacionMedicaResponse(IndicacionMedicaBase):
    id: UUID
    hospitalizacion_id: UUID
    medico_id: UUID
    fecha_indicacion: datetime
    estado: str
    fecha_suspension: Optional[datetime]
    motivo_suspension: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== NOTA DE ALTA ====================


class NotaAltaBase(BaseModel):
    tipo_alta: str
    motivo_ingreso: str
    resumen_evolucion: str
    diagnostico_egreso: str
    procedimientos_realizados: Optional[str] = None
    complicaciones: Optional[str] = None
    condicion_egreso: Optional[str] = None
    estado_funcional: Optional[str] = None
    medicamentos_egreso: Optional[str] = None
    dieta_recomendada: Optional[str] = None
    cuidados_domiciliarios: Optional[str] = None
    restricciones: Optional[str] = None
    fecha_control: Optional[datetime] = None
    especialidad_control: Optional[str] = None
    estudios_pendientes: Optional[List[str]] = None
    pronostico: Optional[str] = None
    observaciones: Optional[str] = None


class NotaAltaCreate(NotaAltaBase):
    hospitalizacion_id: UUID


class NotaAltaUpdate(BaseModel):
    tipo_alta: Optional[str] = None
    motivo_ingreso: Optional[str] = None
    resumen_evolucion: Optional[str] = None
    diagnostico_egreso: Optional[str] = None
    procedimientos_realizados: Optional[str] = None
    complicaciones: Optional[str] = None
    condicion_egreso: Optional[str] = None
    estado_funcional: Optional[str] = None
    medicamentos_egreso: Optional[str] = None
    dieta_recomendada: Optional[str] = None
    cuidados_domiciliarios: Optional[str] = None
    restricciones: Optional[str] = None
    fecha_control: Optional[datetime] = None
    especialidad_control: Optional[str] = None
    estudios_pendientes: Optional[List[str]] = None
    pronostico: Optional[str] = None
    observaciones: Optional[str] = None


class NotaAltaResponse(NotaAltaBase):
    id: UUID
    hospitalizacion_id: UUID
    medico_id: UUID
    fecha_alta: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== CENSO HOSPITALARIO ====================


class CensoHospitalarioResponse(BaseModel):
    total_hospitalizados: int
    por_area: dict
    por_estado: dict
    camas_disponibles: int
    camas_ocupadas: int
    camas_totales: int
    porcentaje_ocupacion: float
    hospitalizaciones_recientes: List[HospitalizacionResponse]
