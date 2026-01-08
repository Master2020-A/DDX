"""
Schemas para el módulo de Analytics y Reportes
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from uuid import UUID


class FiltrosReporte(BaseModel):
    """Filtros para generar reportes"""

    fecha_inicio: date
    fecha_fin: date
    medico_id: Optional[UUID] = None
    tipo_consulta: Optional[str] = None
    estado: Optional[str] = None


class EstadisticasGenerales(BaseModel):
    """Estadísticas generales del sistema"""

    total_consultas: int
    total_pacientes: int
    total_diagnosticos: int
    total_hospitalizaciones: int
    total_interconsultas: int
    consultas_hoy: int
    pacientes_nuevos_mes: int
    tasa_hospitalizacion: float = Field(
        description="Porcentaje de consultas que resultan en hospitalización"
    )


class EstadisticasConsultas(BaseModel):
    """Estadísticas detalladas de consultas"""

    total: int
    por_tipo: Dict[str, int]
    por_estado: Dict[str, int]
    por_mes: List[Dict[str, Any]]
    promedio_diario: float
    tendencia: str = Field(description="ascendente, descendente, estable")


class IndicadoresCalidad(BaseModel):
    """Indicadores de calidad de atención"""

    tiempo_promedio_atencion: float = Field(description="Minutos promedio de atención")
    tiempo_espera_promedio: float = Field(description="Minutos promedio de espera")
    satisfaccion_paciente: Optional[float] = Field(
        default=None, description="Porcentaje de satisfacción"
    )
    tasa_reingreso: float = Field(
        description="Porcentaje de pacientes que reingresan en 30 días"
    )
    tasa_complicaciones: float = Field(description="Porcentaje de complicaciones")
    adherencia_protocolos: float = Field(
        description="Porcentaje de adherencia a protocolos"
    )
    diagnosticos_confirmados: float = Field(
        description="Porcentaje de diagnósticos confirmados"
    )


class TiemposAtencion(BaseModel):
    """Métricas de tiempos de atención"""

    tiempo_promedio_consulta: float
    tiempo_minimo: float
    tiempo_maximo: float
    tiempo_mediano: float
    por_tipo_consulta: Dict[str, float]
    por_medico: List[Dict[str, Any]]
    distribucion_horaria: List[Dict[str, Any]]


class EstadisticasDiagnosticos(BaseModel):
    """Estadísticas de diagnósticos"""

    total: int
    por_tipo: Dict[str, int]
    top_diagnosticos: List[Dict[str, Any]]
    por_categoria_cie10: Dict[str, int]
    tasa_confirmacion: float


class EstadisticasHospitalizacion(BaseModel):
    """Estadísticas de hospitalización"""

    total_hospitalizaciones: int
    ocupacion_actual: float = Field(description="Porcentaje de ocupación")
    estancia_promedio: float = Field(description="Días promedio de estancia")
    por_servicio: Dict[str, int]
    altas_mes: int
    reingresos: int


class DashboardData(BaseModel):
    """Datos completos para el dashboard"""

    estadisticas_generales: EstadisticasGenerales
    estadisticas_consultas: EstadisticasConsultas
    indicadores_calidad: IndicadoresCalidad
    tiempos_atencion: TiemposAtencion
    estadisticas_diagnosticos: EstadisticasDiagnosticos
    estadisticas_hospitalizacion: EstadisticasHospitalizacion
    ultima_actualizacion: datetime


class ReporteConsultas(BaseModel):
    """Reporte detallado de consultas"""

    periodo: str
    total_consultas: int
    consultas: List[Dict[str, Any]]
    estadisticas: EstadisticasConsultas
    graficos: Dict[str, List[Dict[str, Any]]]


class ReporteCalidad(BaseModel):
    """Reporte de indicadores de calidad"""

    periodo: str
    indicadores: IndicadoresCalidad
    comparacion_periodo_anterior: Dict[str, float]
    recomendaciones: List[str]


class ReporteMedico(BaseModel):
    """Reporte de desempeño por médico"""

    medico_id: UUID
    medico_nombre: str
    periodo: str
    total_consultas: int
    tiempo_promedio_atencion: float
    diagnosticos_realizados: int
    tasa_confirmacion: float
    pacientes_atendidos: int
    satisfaccion: Optional[float] = None


class ExportConfig(BaseModel):
    """Configuración para exportar reportes"""

    formato: str = Field(description="pdf, excel, csv")
    incluir_graficos: bool = True
    incluir_detalles: bool = True
    orientacion: str = Field(default="portrait", description="portrait, landscape")


class GraficoData(BaseModel):
    """Datos para gráficos"""

    tipo: str = Field(description="line, bar, pie, area")
    titulo: str
    labels: List[str]
    datasets: List[Dict[str, Any]]
    opciones: Optional[Dict[str, Any]] = None
