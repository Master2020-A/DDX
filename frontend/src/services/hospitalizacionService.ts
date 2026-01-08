/**
 * Servicio para interactuar con la API de Hospitalización
 */
import api from '@/lib/api';
import type {
  Hospitalizacion,
  HospitalizacionCreate,
  HospitalizacionUpdate,
  Cama,
  CamaCreate,
  CamaUpdate,
  NotaEvolucion,
  NotaEvolucionCreate,
  IndicacionMedica,
  IndicacionMedicaCreate,
  NotaAlta,
  NotaAltaCreate,
  CensoHospitalario
} from '@/types/hospitalizacion';

const BASE_URL = '/hospitalizacion';

// ==================== HOSPITALIZACIÓN ====================

export const hospitalizacionService = {
  // Crear ingreso hospitalario
  async crear(data: HospitalizacionCreate): Promise<Hospitalizacion> {
    const response = await api.post(`${BASE_URL}/`, data);
    return response.data;
  },

  // Listar hospitalizaciones
  async listar(params?: {
    skip?: number;
    limit?: number;
    estado?: string;
    area?: string;
    paciente_id?: string;
  }): Promise<Hospitalizacion[]> {
    const response = await api.get(`${BASE_URL}/`, { params });
    return response.data;
  },

  // Obtener detalles de una hospitalización
  async obtener(id: string): Promise<Hospitalizacion> {
    const response = await api.get(`${BASE_URL}/${id}`);
    return response.data;
  },

  // Actualizar hospitalización
  async actualizar(id: string, data: HospitalizacionUpdate): Promise<Hospitalizacion> {
    const response = await api.put(`${BASE_URL}/${id}`, data);
    return response.data;
  },

  // Eliminar hospitalización
  async eliminar(id: string): Promise<void> {
    await api.delete(`${BASE_URL}/${id}`);
  },
};

// ==================== CAMAS ====================

export const camaService = {
  // Registrar nueva cama
  async crear(data: CamaCreate): Promise<Cama> {
    const response = await api.post(`${BASE_URL}/camas`, data);
    return response.data;
  },

  // Listar camas
  async listar(params?: {
    skip?: number;
    limit?: number;
    estado?: string;
    area?: string;
    disponibles?: boolean;
  }): Promise<Cama[]> {
    const response = await api.get<{ camas: Cama[]; total: number }>('/hospitalizacion/camas', { params });
    return response.data.camas;
  },

  // Actualizar cama
  async actualizar(id: string, data: CamaUpdate): Promise<Cama> {
    const response = await api.put(`${BASE_URL}/camas/${id}`, data);
    return response.data;
  },
};

// ==================== NOTAS DE EVOLUCIÓN ====================

export const notaEvolucionService = {
  // Crear nota de evolución
  async crear(data: NotaEvolucionCreate): Promise<NotaEvolucion> {
    const response = await api.post(`${BASE_URL}/notas-evolucion`, data);
    return response.data;
  },

  // Listar notas de evolución
  async listar(params?: {
    hospitalizacion_id?: string;
    skip?: number;
    limit?: number;
  }): Promise<NotaEvolucion[]> {
    const response = await api.get(`${BASE_URL}/notas-evolucion`, { params });
    return response.data;
  },
};

// ==================== INDICACIONES MÉDICAS ====================

export const indicacionMedicaService = {
  // Crear indicación médica
  async crear(data: IndicacionMedicaCreate): Promise<IndicacionMedica> {
    const response = await api.post(`${BASE_URL}/indicaciones`, data);
    return response.data;
  },

  // Listar indicaciones médicas
  async listar(params?: {
    hospitalizacion_id?: string;
    estado?: string;
    skip?: number;
    limit?: number;
  }): Promise<IndicacionMedica[]> {
    const response = await api.get(`${BASE_URL}/indicaciones`, { params });
    return response.data;
  },

  // Actualizar indicación médica
  async actualizar(id: string, data: Partial<IndicacionMedicaCreate>): Promise<IndicacionMedica> {
    const response = await api.put(`${BASE_URL}/indicaciones/${id}`, data);
    return response.data;
  },

  // Suspender indicación
  async suspender(id: string, motivo: string): Promise<IndicacionMedica> {
    const response = await api.put(`${BASE_URL}/indicaciones/${id}`, {
      estado: 'suspendida',
      fecha_suspension: new Date().toISOString(),
      motivo_suspension: motivo
    });
    return response.data;
  },
};

// ==================== NOTAS DE ALTA ====================

export const notaAltaService = {
  // Crear nota de alta
  async crear(data: NotaAltaCreate): Promise<NotaAlta> {
    const response = await api.post(`${BASE_URL}/notas-alta`, data);
    return response.data;
  },

  // Obtener nota de alta
  async obtener(hospitalizacionId: string): Promise<NotaAlta> {
    const response = await api.get(`${BASE_URL}/notas-alta/${hospitalizacionId}`);
    return response.data;
  },
};

// ==================== CENSO HOSPITALARIO ====================

export const censoService = {
  // Obtener censo actual
  async obtenerCenso(): Promise<CensoHospitalario> {
    const response = await api.get(`${BASE_URL}/censo/actual`);
    return response.data;
  },
};

// Exportar todo como default también
export default {
  hospitalizacion: hospitalizacionService,
  cama: camaService,
  notaEvolucion: notaEvolucionService,
  indicacionMedica: indicacionMedicaService,
  notaAlta: notaAltaService,
  censo: censoService,
};
