/**
 * Servicio para Pre-diagnóstico Inteligente
 */
import api from '@/lib/api';

export interface SintomaInput {
  descripcion: string;
  intensidad?: 'leve' | 'moderado' | 'severo';
  duracion?: string;
  frecuencia?: string;
}

export interface PreDiagnosticoRequest {
  paciente_id: string;
  sintomas: SintomaInput[];
  antecedentes?: string;
  medicamentos_actuales?: string[];
  alergias?: string[];
}

export interface DiagnosticoDiferencial {
  nombre: string;
  codigo_cie10?: string;
  probabilidad: number;
  evidencias: string[];
  sintomas_coincidentes: string[];
  sintomas_faltantes?: string[];
  urgencia: 'bajo' | 'medio' | 'alto' | 'critico';
  recomendaciones: string[];
}

export interface PreDiagnosticoResponse {
  diagnosticos_diferenciales: DiagnosticoDiferencial[];
  sintomas_analizados: string[];
  factores_riesgo: string[];
  examenes_sugeridos: string[];
  signos_alarma: string[];
  recomendaciones_generales: string[];
  nivel_urgencia: string;
  timestamp: string;
}

export interface AlgoritmoDecisionRequest {
  sintomas: string[];
  signos_vitales?: Record<string, any>;
  antecedentes?: string[];
  edad?: number;
  sexo?: string;
}

export interface AlgoritmoDecisionResponse {
  decision: string;
  nivel_urgencia: string;
  acciones_inmediatas: string[];
  examenes_prioritarios: string[];
  diagnosticos_probables: string[];
  justificacion: string;
  score_gravedad: number;
}

export interface CIE10SearchResult {
  id: string;
  codigo: string;
  descripcion: string;
  categoria?: string;
  relevancia: number;
}

export const prediagnosticoService = {
  /**
   * Genera pre-diagnóstico basado en síntomas
   */
  async generarPrediagnostico(request: PreDiagnosticoRequest): Promise<PreDiagnosticoResponse> {
    const response = await api.post<PreDiagnosticoResponse>('/prediagnostico/generar', request);
    return response.data;
  },

  /**
   * Ejecuta algoritmo de decisión clínica
   */
  async ejecutarAlgoritmoDecision(request: AlgoritmoDecisionRequest): Promise<AlgoritmoDecisionResponse> {
    const response = await api.post<AlgoritmoDecisionResponse>('/prediagnostico/algoritmo-decision', request);
    return response.data;
  },

  /**
   * Busca códigos CIE-10 con autocompletado
   */
  async buscarCIE10(query: string, limit: number = 10): Promise<CIE10SearchResult[]> {
    const response = await api.get<CIE10SearchResult[]>('/prediagnostico/cie10/buscar', {
      params: { q: query, limit }
    });
    return response.data;
  },

  /**
   * Obtiene información de un código CIE-10 específico
   */
  async obtenerCIE10(codigo: string): Promise<any> {
    const response = await api.get(`/prediagnostico/cie10/${codigo}`);
    return response.data;
  }
};
