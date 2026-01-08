/**
 * Servicio para gestión de Estudios Especiales: EKG, EEG, Ecografías
 */
import api from '@/lib/api';
import {
  EstudioEKG,
  EstudioEEG,
  Ecografia,
  CrearEstudioEKG,
  CrearEstudioEEG,
  CrearEcografia,
  ResumenEstudiosEspeciales
} from '../types/estudiosEspeciales';

// ==================== EKG ====================

export const estudiosEspecialesService = {
  // EKG
  async crearEstudioEKG(data: CrearEstudioEKG): Promise<{ mensaje: string; id: string; interpretacion: any }> {
    const response = await api.post('/estudios-especiales/ekg', data);
    return response.data;
  },

  async listarEstudiosEKGPaciente(pacienteId: string): Promise<{ total: number; estudios: EstudioEKG[] }> {
    const response = await api.get(`/estudios-especiales/ekg/paciente/${pacienteId}`);
    return response.data;
  },

  async obtenerEstudioEKG(estudioId: string): Promise<EstudioEKG> {
    const response = await api.get(`/estudios-especiales/ekg/${estudioId}`);
    return response.data;
  },

  // EEG
  async crearEstudioEEG(data: CrearEstudioEEG): Promise<{ mensaje: string; id: string; interpretacion: any }> {
    const response = await api.post('/estudios-especiales/eeg', data);
    return response.data;
  },

  async listarEstudiosEEGPaciente(pacienteId: string): Promise<{ total: number; estudios: EstudioEEG[] }> {
    const response = await api.get(`/estudios-especiales/eeg/paciente/${pacienteId}`);
    return response.data;
  },

  async obtenerEstudioEEG(estudioId: string): Promise<EstudioEEG> {
    const response = await api.get(`/estudios-especiales/eeg/${estudioId}`);
    return response.data;
  },

  // Ecografías
  async crearEcografia(data: CrearEcografia): Promise<{ mensaje: string; id: string; interpretacion: any }> {
    const response = await api.post('/estudios-especiales/ecografia', data);
    return response.data;
  },

  async listarEcografiasPaciente(pacienteId: string): Promise<{ total: number; ecografias: Ecografia[] }> {
    const response = await api.get(`/estudios-especiales/ecografia/paciente/${pacienteId}`);
    return response.data;
  },

  async obtenerEcografia(ecografiaId: string): Promise<Ecografia> {
    const response = await api.get(`/estudios-especiales/ecografia/${ecografiaId}`);
    return response.data;
  },

  // Resumen
  async obtenerResumenEstudios(pacienteId: string): Promise<ResumenEstudiosEspeciales> {
    const response = await api.get(`/estudios-especiales/paciente/${pacienteId}/resumen`);
    return response.data;
  },

  // Extracción desde archivo
  async extraerDesdeArchivo(
    archivo: File, 
    metodoAnalisis: 'auto' | 'ocr' | 'ia' = 'ia'
  ): Promise<{
    mensaje: string;
    tipo_estudio: string;
    datos: any;
    anomalias?: string[];
    confianza: number;
    texto_muestra: string;
    metodo?: string;
    interpretacion_ia?: string;
    conversion_csv_disponible?: boolean;
    mensaje_conversion?: string;
  }> {
    const formData = new FormData();
    formData.append('archivo', archivo);
    formData.append('metodo_analisis', metodoAnalisis);
    
    const response = await api.post('/estudios-especiales/extraer-desde-archivo', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },

  // Convertir CSV a imagen y analizar con IA
  async convertirCsvAImagen(
    archivo: File,
    num_derivaciones: number = 12,
    usar_ia: boolean = true
  ): Promise<{
    mensaje: string;
    tipo_estudio: string;
    datos: any;
    anomalias?: string[];
    interpretacion_ia?: string;
    confianza: number;
    metodo: string;
  }> {
    const formData = new FormData();
    formData.append('archivo', archivo);
    formData.append('num_derivaciones', num_derivaciones.toString());
    formData.append('usar_ia', usar_ia.toString());
    
    const response = await api.post('/estudios-especiales/convertir-csv-a-imagen', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },

  // ==================== INTERPRETACIÓN CON IA ====================
  
  async interpretarEKGConIA(ekgId: string): Promise<any> {
    const response = await api.post(`/estudios-especiales/ekg/${ekgId}/interpretar-ia`);
    return response.data;
  },

  async interpretarEEGConIA(eegId: string): Promise<any> {
    const response = await api.post(`/estudios-especiales/eeg/${eegId}/interpretar-ia`);
    return response.data;
  },

  async interpretarEcografiaConIA(ecografiaId: string): Promise<any> {
    const response = await api.post(`/estudios-especiales/ecografia/${ecografiaId}/interpretar-ia`);
    return response.data;
  },

  // ==================== ANÁLISIS AVANZADO EKG ====================

  async analizarEKGDesdeImagen(archivo: File, pacienteId?: string): Promise<any> {
    const formData = new FormData();
    formData.append('archivo', archivo);
    if (pacienteId) formData.append('paciente_id', pacienteId);
    
    const response = await api.post('/estudios-especiales/ekg/analizar-imagen', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  async extraerParametrosEKG(archivo: File): Promise<any> {
    const formData = new FormData();
    formData.append('archivo', archivo);
    
    const response = await api.post('/estudios-especiales/ekg/extraer-parametros', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  async generarGraficaAnotadaEKG(ekgId: string): Promise<Blob> {
    const response = await api.post(`/estudios-especiales/ekg/${ekgId}/generar-grafica-anotada`, {}, {
      responseType: 'blob'
    });
    return response.data;
  },

  async obtenerInterpretacionNarrativa(ekgId: string): Promise<any> {
    const response = await api.get(`/estudios-especiales/ekg/${ekgId}/interpretacion-narrativa`);
    return response.data;
  },

  // ==================== EXTRACCIÓN AUTOMÁTICA ====================

  async extraerParametrosEEG(archivo: File): Promise<any> {
    const formData = new FormData();
    formData.append('archivo', archivo);
    
    const response = await api.post('/estudios-especiales/eeg/extraer-parametros', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  async extraerParametrosEcografia(archivo: File): Promise<any> {
    const formData = new FormData();
    formData.append('archivo', archivo);
    
    const response = await api.post('/estudios-especiales/ecografia/extraer-parametros', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  // ==================== GENERACIÓN DE PDFs ====================

  async generarPDFAnalisisEKG(ekgId: string): Promise<Blob> {
    const response = await api.get(`/estudios-especiales/ekg/${ekgId}/pdf-analisis`, {
      responseType: 'blob'
    });
    return response.data;
  },

  async generarPDFInterpretacionEKG(ekgId: string): Promise<Blob> {
    const response = await api.get(`/estudios-especiales/ekg/${ekgId}/pdf-interpretacion`, {
      responseType: 'blob'
    });
    return response.data;
  },

  async generarPDFAnalisisEEG(eegId: string): Promise<Blob> {
    const response = await api.get(`/estudios-especiales/eeg/${eegId}/pdf-analisis`, {
      responseType: 'blob'
    });
    return response.data;
  },

  async generarPDFInterpretacionEEG(eegId: string): Promise<Blob> {
    const response = await api.get(`/estudios-especiales/eeg/${eegId}/pdf-interpretacion`, {
      responseType: 'blob'
    });
    return response.data;
  },

  async generarPDFAnalisisEcografia(ecografiaId: string): Promise<Blob> {
    const response = await api.get(`/estudios-especiales/ecografia/${ecografiaId}/pdf-analisis`, {
      responseType: 'blob'
    });
    return response.data;
  },

  async generarPDFInterpretacionEcografia(ecografiaId: string): Promise<Blob> {
    const response = await api.get(`/estudios-especiales/ecografia/${ecografiaId}/pdf-interpretacion`, {
      responseType: 'blob'
    });
    return response.data;
  }
};

export default estudiosEspecialesService;
