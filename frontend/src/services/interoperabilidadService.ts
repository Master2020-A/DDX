/**
 * Servicio para Interoperabilidad HL7 FHIR
 * Gestión de intercambio de expedientes y red nacional de salud
 */

import axios from 'axios';

const API_URL = 'http://localhost:8612/api/interoperabilidad';

// ==================== INTERFACES ====================

export interface InstitucionExterna {
  id: string;
  nombre: string;
  codigo_institucional: string;
  nivel_atencion: 'primario' | 'secundario' | 'terciario' | 'especializado';
  tipo_institucion: 'publico' | 'privado' | 'mixto';
  pais: string;
  estado?: string;
  ciudad?: string;
  direccion?: string;
  telefono?: string;
  email?: string;
  url_endpoint_fhir?: string;
  url_endpoint_hl7v2?: string;
  certificado_ssl?: string;
  activa: boolean;
  protocolos_soportados: string[];
  versiones_fhir: string[];
  capacidades?: any;
  created_at: string;
  updated_at: string;
}

export interface SolicitudIntercambio {
  id: string;
  paciente_id: string;
  institucion_origen_id: string;
  institucion_destino_id: string;
  tipo_intercambio: 'expediente_completo' | 'consultas' | 'laboratorios' | 'imagenes' | 'recetas' | 'hospitalizacion';
  protocolo: 'FHIR_R4' | 'FHIR_R5' | 'HL7V2' | 'REST_API';
  estado: 'pendiente' | 'aprobada' | 'rechazada' | 'en_proceso' | 'completada' | 'error';
  prioridad: 'baja' | 'normal' | 'alta' | 'urgente';
  motivo_solicitud?: string;
  periodo_inicio?: string;
  periodo_fin?: string;
  solicitante_id: string;
  aprobador_id?: string;
  fecha_aprobacion?: string;
  fecha_completado?: string;
  datos_enviados?: any;
  datos_recibidos?: any;
  checksum_datos?: string;
  motivo_rechazo?: string;
  errores?: string[];
  created_at: string;
  updated_at: string;
}

export interface HistoriaClinicaUnificada {
  id: string;
  paciente_id: string;
  consultas_totales: number;
  hospitalizaciones_totales: number;
  diagnosticos_activos: any[];
  medicamentos_actuales: any[];
  alergias_consolidadas: any[];
  vacunas_consolidadas: any[];
  instituciones_contribuyentes: string[];
  ultima_actualizacion_externa?: string;
  created_at: string;
  updated_at: string;
}

export interface ConsentimientoIntercambio {
  id: string;
  paciente_id: string;
  activo: boolean;
  fecha_consentimiento: string;
  fecha_expiracion?: string;
  revocado: boolean;
  fecha_revocacion?: string;
  instituciones_autorizadas: string[];
  tipos_datos_autorizados: string[];
  puede_compartir_diagnosticos: boolean;
  puede_compartir_laboratorios: boolean;
  puede_compartir_imagenes: boolean;
  puede_compartir_recetas: boolean;
  proposito_uso: string[];
  documento_firmado_url?: string;
  created_at: string;
  updated_at: string;
}

export interface EstadisticasIntercambio {
  total_solicitudes: number;
  solicitudes_por_estado: Record<string, number>;
  solicitudes_por_tipo: Record<string, number>;
  instituciones_activas: number;
  pacientes_con_consentimiento: number;
  periodo_dias: number;
}

export interface ExpedienteCompletoFHIR {
  bundle: any;
  checksum: string;
  fecha_generacion: string;
  solicitud_id: string;
}

// ==================== INSTITUCIONES EXTERNAS ====================

export const crearInstitucionExterna = async (data: Partial<InstitucionExterna>) => {
  const response = await axios.post(`${API_URL}/instituciones-externas/`, data);
  return response.data;
};

export const listarInstitucionesExternas = async (params?: {
  skip?: number;
  limit?: number;
  activa?: boolean;
  nivel?: string;
}) => {
  const response = await axios.get(`${API_URL}/instituciones-externas/`, { params });
  return response.data;
};

export const obtenerInstitucionExterna = async (id: string) => {
  const response = await axios.get(`${API_URL}/instituciones-externas/${id}`);
  return response.data;
};

export const actualizarInstitucionExterna = async (id: string, data: Partial<InstitucionExterna>) => {
  const response = await axios.put(`${API_URL}/instituciones-externas/${id}`, data);
  return response.data;
};

export const eliminarInstitucionExterna = async (id: string) => {
  const response = await axios.delete(`${API_URL}/instituciones-externas/${id}`);
  return response.data;
};

// ==================== SOLICITUDES DE INTERCAMBIO ====================

export const crearSolicitudIntercambio = async (data: Partial<SolicitudIntercambio>) => {
  const response = await axios.post(`${API_URL}/solicitudes/`, data);
  return response.data;
};

export const listarSolicitudesIntercambio = async (params?: {
  skip?: number;
  limit?: number;
  estado?: string;
  tipo?: string;
  paciente_id?: string;
}) => {
  const response = await axios.get(`${API_URL}/solicitudes/`, { params });
  return response.data;
};

export const obtenerSolicitudIntercambio = async (id: string) => {
  const response = await axios.get(`${API_URL}/solicitudes/${id}`);
  return response.data;
};

export const aprobarSolicitudIntercambio = async (id: string) => {
  const response = await axios.put(`${API_URL}/solicitudes/${id}/aprobar`);
  return response.data;
};

export const rechazarSolicitudIntercambio = async (id: string, motivo: string) => {
  const response = await axios.put(`${API_URL}/solicitudes/${id}/rechazar`, null, {
    params: { motivo }
  });
  return response.data;
};

export const generarExpedienteFHIR = async (solicitudId: string): Promise<ExpedienteCompletoFHIR> => {
  const response = await axios.post(`${API_URL}/solicitudes/${solicitudId}/generar-expediente`);
  return response.data;
};

// ==================== HISTORIA CLÍNICA UNIFICADA ====================

export const obtenerHistoriaUnificada = async (pacienteId: string): Promise<HistoriaClinicaUnificada> => {
  const response = await axios.get(`${API_URL}/historia-unificada/${pacienteId}`);
  return response.data;
};

export const consolidarDatosExternos = async (
  pacienteId: string,
  datosExternos: any,
  institucionOrigen: string
) => {
  const response = await axios.post(`${API_URL}/historia-unificada/${pacienteId}/consolidar`, {
    datos_externos: datosExternos,
    institucion_origen: institucionOrigen,
  });
  return response.data;
};

// ==================== CONSENTIMIENTOS ====================

export const crearConsentimiento = async (data: Partial<ConsentimientoIntercambio>) => {
  const response = await axios.post(`${API_URL}/consentimientos/`, data);
  return response.data;
};

export const listarConsentimientosPaciente = async (pacienteId: string) => {
  const response = await axios.get(`${API_URL}/consentimientos/paciente/${pacienteId}`);
  return response.data;
};

export const revocarConsentimiento = async (id: string) => {
  const response = await axios.put(`${API_URL}/consentimientos/${id}/revocar`);
  return response.data;
};

// ==================== ESTADÍSTICAS ====================

export const obtenerEstadisticasIntercambio = async (dias: number = 30): Promise<EstadisticasIntercambio> => {
  const response = await axios.get(`${API_URL}/estadisticas/`, { params: { dias } });
  return response.data;
};

// ==================== LOGS ====================

export const obtenerLogsSolicitud = async (solicitudId: string) => {
  const response = await axios.get(`${API_URL}/logs/solicitud/${solicitudId}`);
  return response.data;
};
