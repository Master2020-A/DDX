/**
 * Servicio para interactuar con la API de Interconsultas
 */
import api from '@/lib/api';
import type {
  Interconsulta,
  InterconsultaCreate,
  NotificacionInterconsulta,
  MensajeInterconsulta,
  MensajeCreate,
  SeguimientoInterconsulta,
  SeguimientoCreate,
  AceptarInterconsultaRequest,
  RechazarInterconsultaRequest,
  ResponderInterconsultaRequest,
  EstadisticasInterconsultas
} from '@/types/interconsulta';

const BASE_URL = '/interconsultas';

// ==================== INTERCONSULTAS ====================

export const interconsultaService = {
  // Crear solicitud de interconsulta
  async crear(data: InterconsultaCreate): Promise<Interconsulta> {
    const response = await api.post(`${BASE_URL}/`, data);
    return response.data;
  },

  // Listar interconsultas
  async listar(params?: {
    skip?: number;
    limit?: number;
    estado?: string;
    especialidad?: string;
    urgencia?: string;
    paciente_id?: string;
    mis_solicitudes?: boolean;
    mis_interconsultas?: boolean;
  }): Promise<Interconsulta[]> {
    const response = await api.get(`${BASE_URL}/`, { params });
    return response.data;
  },

  // Obtener detalles de una interconsulta
  async obtener(id: string): Promise<Interconsulta> {
    const response = await api.get(`${BASE_URL}/${id}`);
    return response.data;
  },

  // Actualizar interconsulta
  async actualizar(id: string, data: Partial<InterconsultaCreate>): Promise<Interconsulta> {
    const response = await api.put(`${BASE_URL}/${id}`, data);
    return response.data;
  },

  // Aceptar interconsulta
  async aceptar(id: string, data: AceptarInterconsultaRequest): Promise<Interconsulta> {
    const response = await api.post(`${BASE_URL}/${id}/aceptar`, data);
    return response.data;
  },

  // Rechazar interconsulta
  async rechazar(id: string, data: RechazarInterconsultaRequest): Promise<Interconsulta> {
    const response = await api.post(`${BASE_URL}/${id}/rechazar`, data);
    return response.data;
  },

  // Responder interconsulta
  async responder(id: string, data: ResponderInterconsultaRequest): Promise<Interconsulta> {
    const response = await api.post(`${BASE_URL}/${id}/responder`, data);
    return response.data;
  },
};

// ==================== NOTIFICACIONES ====================

export const notificacionService = {
  // Obtener mis notificaciones
  async obtenerMisNotificaciones(params?: {
    skip?: number;
    limit?: number;
    solo_no_leidas?: boolean;
  }): Promise<NotificacionInterconsulta[]> {
    const response = await api.get(`${BASE_URL}/notificaciones/mis-notificaciones`, { params });
    return response.data;
  },

  // Marcar como leída
  async marcarLeida(id: string): Promise<void> {
    await api.put(`${BASE_URL}/notificaciones/${id}/marcar-leida`);
  },
};

// ==================== MENSAJES (CHAT) ====================

export const mensajeService = {
  // Enviar mensaje
  async enviar(data: MensajeCreate): Promise<MensajeInterconsulta> {
    const response = await api.post(`${BASE_URL}/mensajes`, data);
    return response.data;
  },

  // Obtener mensajes de una interconsulta
  async obtener(interconsultaId: string, params?: {
    skip?: number;
    limit?: number;
  }): Promise<MensajeInterconsulta[]> {
    const response = await api.get(`${BASE_URL}/mensajes/${interconsultaId}`, { params });
    return response.data;
  },
};

// ==================== SEGUIMIENTOS ====================

export const seguimientoService = {
  // Crear seguimiento
  async crear(data: SeguimientoCreate): Promise<SeguimientoInterconsulta> {
    const response = await api.post(`${BASE_URL}/seguimientos`, data);
    return response.data;
  },

  // Obtener seguimientos de una interconsulta
  async obtener(interconsultaId: string): Promise<SeguimientoInterconsulta[]> {
    const response = await api.get(`${BASE_URL}/seguimientos/${interconsultaId}`);
    return response.data;
  },
};

// ==================== ESTADÍSTICAS ====================

export const estadisticasService = {
  // Obtener estadísticas generales
  async obtenerGeneral(): Promise<EstadisticasInterconsultas> {
    const response = await api.get(`${BASE_URL}/estadisticas/general`);
    return response.data;
  },
};

// Exportar todo como default también
export default {
  interconsulta: interconsultaService,
  notificacion: notificacionService,
  mensaje: mensajeService,
  seguimiento: seguimientoService,
  estadisticas: estadisticasService,
};
