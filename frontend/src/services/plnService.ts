import api from './api';

export interface TranscripcionResponse {
  id: string;
  texto: string;
  idioma: string;
  duracion_segundos: number;
  confianza: number;
  modelo: string;
  informacion_extraida?: any;
}

export interface ExtraccionResponse {
  id: string;
  sintomas: any[];
  medicamentos: any[];
  signos_vitales: any;
  diagnosticos: any[];
  antecedentes: any[];
}

export interface ResumenResponse {
  id: string;
  resumen_texto: string;
  diagnosticos_actuales: string[];
  tratamiento_actual: string[];
  estudios_pendientes: string[];
  alertas_clinicas: string[];
  plan_seguimiento: string;
}

export interface TraduccionResponse {
  id: string;
  texto_traducido: string;
  alternativas: string[];
  sinonimos: any;
  definicion: string;
  confianza: number;
}

class PLNService {
  /**
   * Transcribir audio a texto usando Whisper
   */
  async transcribirAudio(
    archivo: File,
    pacienteId: string,
    idioma: string = 'es',
    extraerInformacion: boolean = true
  ): Promise<TranscripcionResponse> {
    const formData = new FormData();
    formData.append('archivo', archivo);
    formData.append('paciente_id', pacienteId);
    formData.append('idioma', idioma);
    formData.append('extraer_informacion', String(extraerInformacion));

    const response = await api.post('/pln/transcribir-audio', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  }

  /**
   * Extraer información estructurada de texto médico
   */
  async extraerInformacion(
    texto: string,
    pacienteId: string,
    tipoDocumento: string = 'nota_evolucion'
  ): Promise<ExtraccionResponse> {
    const response = await api.post('/pln/extraer-informacion', {
      texto,
      tipo_documento: tipoDocumento,
      paciente_id: pacienteId
    });
    return response.data;
  }

  /**
   * Generar resumen clínico automático
   */
  async generarResumen(
    pacienteId: string,
    tipoResumen: string = 'completo',
    periodoDias: number = 90
  ): Promise<ResumenResponse> {
    const response = await api.post('/pln/generar-resumen', {
      paciente_id: pacienteId,
      tipo_resumen: tipoResumen,
      periodo_dias: periodoDias,
      incluir_consultas: true,
      incluir_laboratorios: true,
      incluir_imagenes: true,
      incluir_medicamentos: true
    });
    return response.data;
  }

  /**
   * Traducir terminología médica
   */
  async traducir(
    texto: string,
    idiomaOrigen: string = 'es',
    idiomaDestino: string = 'en',
    tipoContenido: string = 'termino_medico'
  ): Promise<TraduccionResponse> {
    const response = await api.post('/pln/traducir', {
      texto,
      idioma_origen: idiomaOrigen,
      idioma_destino: idiomaDestino,
      tipo_contenido: tipoContenido
    });
    return response.data;
  }

  /**
   * Obtener transcripciones de un paciente
   */
  async obtenerTranscripciones(pacienteId: string): Promise<TranscripcionResponse[]> {
    const response = await api.get(`/pln/transcripciones/paciente/${pacienteId}`);
    return response.data;
  }

  /**
   * Obtener extracciones de un paciente
   */
  async obtenerExtracciones(pacienteId: string): Promise<ExtraccionResponse[]> {
    const response = await api.get(`/pln/extracciones/paciente/${pacienteId}`);
    return response.data;
  }

  /**
   * Obtener resúmenes de un paciente
   */
  async obtenerResumenes(pacienteId: string): Promise<ResumenResponse[]> {
    const response = await api.get(`/pln/resumenes/paciente/${pacienteId}`);
    return response.data;
  }

  /**
   * Obtener traducciones de un paciente
   */
  async obtenerTraducciones(pacienteId: string): Promise<TraduccionResponse[]> {
    const response = await api.get(`/pln/traducciones/paciente/${pacienteId}`);
    return response.data;
  }
}

export default new PLNService();
