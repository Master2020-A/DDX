import api from '@/lib/api';

export interface EstadisticasGenerales {
  total_consultas: number;
  total_pacientes: number;
  total_diagnosticos: number;
  total_hospitalizaciones: number;
  total_interconsultas: number;
  consultas_hoy: number;
  pacientes_nuevos_mes: number;
  tasa_hospitalizacion: number;
}

export interface EstadisticasConsultas {
  total: number;
  por_tipo: Record<string, number>;
  por_estado: Record<string, number>;
  por_mes: Array<{ mes: string; count: number }>;
  promedio_diario: number;
  tendencia: string;
}

export interface IndicadoresCalidad {
  tiempo_promedio_atencion: number;
  tiempo_espera_promedio: number;
  satisfaccion_paciente: number | null;
  tasa_reingreso: number;
  tasa_complicaciones: number;
  adherencia_protocolos: number;
  diagnosticos_confirmados: number;
}

export interface TiemposAtencion {
  tiempo_promedio_consulta: number;
  tiempo_minimo: number;
  tiempo_maximo: number;
  tiempo_mediano: number;
  por_tipo_consulta: Record<string, number>;
  por_medico: Array<{ medico: string; tiempo_promedio: number; consultas: number }>;
  distribucion_horaria: Array<{ hora: string; consultas: number; tiempo_promedio: number }>;
}

export interface EstadisticasDiagnosticos {
  total: number;
  por_tipo: Record<string, number>;
  top_diagnosticos: Array<{ descripcion: string; codigo_cie10: string; count: number }>;
  por_categoria_cie10: Record<string, number>;
  tasa_confirmacion: number;
}

export interface EstadisticasHospitalizacion {
  total_hospitalizaciones: number;
  ocupacion_actual: number;
  estancia_promedio: number;
  por_servicio: Record<string, number>;
  altas_mes: number;
  reingresos: number;
}

export interface DashboardData {
  estadisticas_generales: EstadisticasGenerales;
  estadisticas_consultas: EstadisticasConsultas;
  indicadores_calidad: IndicadoresCalidad;
  tiempos_atencion: TiemposAtencion;
  estadisticas_diagnosticos: EstadisticasDiagnosticos;
  estadisticas_hospitalizacion: EstadisticasHospitalizacion;
  ultima_actualizacion: string;
}

class AnalyticsService {
  async getDashboard(fechaInicio?: string, fechaFin?: string): Promise<DashboardData> {
    const params = new URLSearchParams();
    if (fechaInicio) params.append('fecha_inicio', fechaInicio);
    if (fechaFin) params.append('fecha_fin', fechaFin);
    
    const response = await api.get(`/analytics/dashboard?${params.toString()}`);
    return response.data;
  }

  async getEstadisticasGenerales(fechaInicio?: string, fechaFin?: string): Promise<EstadisticasGenerales> {
    const params = new URLSearchParams();
    if (fechaInicio) params.append('fecha_inicio', fechaInicio);
    if (fechaFin) params.append('fecha_fin', fechaFin);
    
    const response = await api.get(`/analytics/estadisticas-generales?${params.toString()}`);
    return response.data;
  }

  async getEstadisticasConsultas(fechaInicio?: string, fechaFin?: string): Promise<EstadisticasConsultas> {
    const params = new URLSearchParams();
    if (fechaInicio) params.append('fecha_inicio', fechaInicio);
    if (fechaFin) params.append('fecha_fin', fechaFin);
    
    const response = await api.get(`/analytics/estadisticas-consultas?${params.toString()}`);
    return response.data;
  }

  async getIndicadoresCalidad(fechaInicio?: string, fechaFin?: string): Promise<IndicadoresCalidad> {
    const params = new URLSearchParams();
    if (fechaInicio) params.append('fecha_inicio', fechaInicio);
    if (fechaFin) params.append('fecha_fin', fechaFin);
    
    const response = await api.get(`/analytics/indicadores-calidad?${params.toString()}`);
    return response.data;
  }

  async getTiemposAtencion(fechaInicio?: string, fechaFin?: string): Promise<TiemposAtencion> {
    const params = new URLSearchParams();
    if (fechaInicio) params.append('fecha_inicio', fechaInicio);
    if (fechaFin) params.append('fecha_fin', fechaFin);
    
    const response = await api.get(`/analytics/tiempos-atencion?${params.toString()}`);
    return response.data;
  }

  async exportarCSV(fechaInicio?: string, fechaFin?: string): Promise<Blob> {
    const params = new URLSearchParams();
    if (fechaInicio) params.append('fecha_inicio', fechaInicio);
    if (fechaFin) params.append('fecha_fin', fechaFin);
    
    const response = await api.post(`/analytics/exportar/csv?${params.toString()}`, {}, {
      responseType: 'blob'
    });
    return response.data;
  }

  async exportarExcel(fechaInicio?: string, fechaFin?: string, incluirGraficos: boolean = true): Promise<Blob> {
    const params = new URLSearchParams();
    if (fechaInicio) params.append('fecha_inicio', fechaInicio);
    if (fechaFin) params.append('fecha_fin', fechaFin);
    params.append('incluir_graficos', incluirGraficos.toString());
    
    const response = await api.post(`/analytics/exportar/excel?${params.toString()}`, {}, {
      responseType: 'blob'
    });
    return response.data;
  }

  async exportarPDF(fechaInicio?: string, fechaFin?: string, orientacion: string = 'portrait'): Promise<Blob> {
    const params = new URLSearchParams();
    if (fechaInicio) params.append('fecha_inicio', fechaInicio);
    if (fechaFin) params.append('fecha_fin', fechaFin);
    params.append('orientacion', orientacion);
    
    const response = await api.post(`/analytics/exportar/pdf?${params.toString()}`, {}, {
      responseType: 'blob'
    });
    return response.data;
  }

  downloadFile(blob: Blob, filename: string) {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }
}

export default new AnalyticsService();
