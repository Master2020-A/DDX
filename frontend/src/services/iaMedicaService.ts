/**
 * Servicio para Inteligencia Artificial Médica
 */

import api from './api';

// ==================== INTERFACES ====================

export interface AsistenteConsultaRequest {
  pregunta: string;
  paciente_id?: string;
  incluir_historial?: boolean;
  incluir_estudios?: boolean;
  tipo_consulta?: string;
}

export interface AsistenteConsultaResponse {
  id: string;
  pregunta: string;
  respuesta: string;
  contexto_utilizado: any;
  tipo_consulta: string;
  referencias: string[];
  created_at: string;
}

export interface PrediccionRiesgoRequest {
  paciente_id: string;
  tipo_riesgo: string;
  incluir_recomendaciones?: boolean;
}

export interface FactorRiesgo {
  nombre: string;
  valor: any;
  impacto: string;
  modificable: boolean;
}

export interface PrediccionRiesgoResponse {
  id: string;
  paciente_id: string;
  tipo_riesgo: string;
  nivel_riesgo: string;
  porcentaje_riesgo: number;
  factores_riesgo: FactorRiesgo[];
  factores_protectores: string[];
  recomendaciones: string[];
  estudios_sugeridos: string[];
  algoritmo: string;
  valido_hasta: string;
  created_at: string;
}

export interface RecomendacionTratamientoRequest {
  paciente_id: string;
  diagnostico_principal: string;
  codigo_cie10?: string;
  sintomas?: string[];
  comorbilidades?: string[];
}

export interface MedicamentoSugerido {
  nombre: string;
  dosis: string;
  frecuencia: string;
  duracion: string;
  via_administracion: string;
  razon: string;
  nivel_evidencia: string;
}

export interface RecomendacionTratamientoResponse {
  id: string;
  paciente_id: string;
  diagnostico_principal: string;
  codigo_cie10?: string;
  medicamentos_sugeridos: MedicamentoSugerido[];
  terapias_no_farmacologicas: string[];
  cambios_estilo_vida: string[];
  contraindicaciones: string[];
  precauciones: string[];
  guias_clinicas: string[];
  prioridad: string;
  created_at: string;
}

export interface InteraccionMedicamentosaRequest {
  paciente_id: string;
  medicamentos: string[];
  incluir_alergias?: boolean;
  incluir_condiciones?: boolean;
}

export interface Interaccion {
  medicamento1: string;
  medicamento2: string;
  severidad: string;
  descripcion: string;
  mecanismo: string;
  efectos: string[];
  manejo: string;
}

export interface InteraccionMedicamentosaResponse {
  id: string;
  paciente_id: string;
  medicamentos_analizados: string[];
  interacciones_encontradas: Interaccion[];
  severidad_maxima: string;
  alertas_criticas: string[];
  recomendaciones_ajuste: string[];
  alergias_consideradas: string[];
  condiciones_consideradas: string[];
  created_at: string;
}

export interface DeteccionAnomaliasRequest {
  paciente_id: string;
  tipo_estudio: string;
  estudio_id?: string;
  datos_estudio?: any;
}

export interface AnomaliaDetectadaResponse {
  id: string;
  paciente_id: string;
  tipo_estudio: string;
  estudio_id?: string;
  tipo_anomalia: string;
  severidad: string;
  descripcion: string;
  localizacion?: string;
  valores_anormales: any;
  patron_detectado?: string;
  confianza_deteccion: number;
  requiere_atencion_inmediata: boolean;
  recomendaciones: string[];
  estudios_adicionales: string[];
  created_at: string;
}

export interface EstadisticasIA {
  total_analisis: number;
  analisis_por_tipo: { [key: string]: number };
  predicciones_riesgo_activas: number;
  anomalias_pendientes_revision: number;
  interacciones_criticas: number;
  tiempo_promedio_respuesta: number;
  tasa_validacion_medico: number;
  consultas_asistente_hoy: number;
  consultas_asistente_mes: number;
}

export interface AnalisisReciente {
  id: string;
  tipo: string;
  paciente_nombre: string;
  resultado_resumen: string;
  severidad?: string;
  created_at: string;
}

export interface DashboardIAResponse {
  estadisticas: EstadisticasIA;
  analisis_recientes: AnalisisReciente[];
  alertas_criticas: any[];
  recomendaciones_pendientes: number;
}

// ==================== SERVICIOS ====================

const iaMedicaService = {
  // Asistente de IA
  consultarAsistente: async (request: AsistenteConsultaRequest): Promise<AsistenteConsultaResponse> => {
    const response = await api.post('/ia-medica/asistente/consultar', request);
    return response.data;
  },

  obtenerHistorialAsistente: async (pacienteId?: string, limit: number = 20): Promise<AsistenteConsultaResponse[]> => {
    const params = new URLSearchParams();
    if (pacienteId) params.append('paciente_id', pacienteId);
    params.append('limit', limit.toString());
    
    const response = await api.get(`/ia-medica/asistente/historial?${params.toString()}`);
    return response.data;
  },

  // Predicción de Riesgos
  predecirRiesgo: async (request: PrediccionRiesgoRequest): Promise<PrediccionRiesgoResponse> => {
    const response = await api.post('/ia-medica/prediccion-riesgo', request);
    return response.data;
  },

  obtenerPrediccionesPaciente: async (pacienteId: string): Promise<PrediccionRiesgoResponse[]> => {
    const response = await api.get(`/ia-medica/prediccion-riesgo/paciente/${pacienteId}`);
    return response.data;
  },

  // Recomendaciones de Tratamiento
  generarRecomendacionTratamiento: async (request: RecomendacionTratamientoRequest): Promise<RecomendacionTratamientoResponse> => {
    const response = await api.post('/ia-medica/recomendacion-tratamiento', request);
    return response.data;
  },

  // Interacciones Medicamentosas
  analizarInteracciones: async (request: InteraccionMedicamentosaRequest): Promise<InteraccionMedicamentosaResponse> => {
    const response = await api.post('/ia-medica/interacciones-medicamentosas', request);
    return response.data;
  },

  // Detección de Anomalías
  detectarAnomalias: async (request: DeteccionAnomaliasRequest): Promise<AnomaliaDetectadaResponse[]> => {
    const response = await api.post('/ia-medica/detectar-anomalias', request);
    return response.data;
  },

  obtenerAnomaliasPendientes: async (): Promise<AnomaliaDetectadaResponse[]> => {
    const response = await api.get('/ia-medica/anomalias/pendientes');
    return response.data;
  },

  // Dashboard
  obtenerDashboard: async (): Promise<DashboardIAResponse> => {
    const response = await api.get('/ia-medica/dashboard');
    return response.data;
  },
};

export default iaMedicaService;
