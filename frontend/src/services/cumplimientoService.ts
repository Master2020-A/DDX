import api from './api';

// ==================== TIPOS ====================

export enum TipoNormativa {
  HIPAA = 'HIPAA',
  GDPR = 'GDPR',
  NOM_004 = 'NOM-004-SSA3-2012',
  OTRA = 'OTRA'
}

export enum TipoConsentimiento {
  TRATAMIENTO = 'TRATAMIENTO',
  CIRUGIA = 'CIRUGIA',
  ANESTESIA = 'ANESTESIA',
  INVESTIGACION = 'INVESTIGACION',
  DATOS_PERSONALES = 'DATOS_PERSONALES',
  IMAGEN = 'IMAGEN',
  OTRO = 'OTRO'
}

export enum EstadoConsentimiento {
  PENDIENTE = 'PENDIENTE',
  ACEPTADO = 'ACEPTADO',
  RECHAZADO = 'RECHAZADO',
  REVOCADO = 'REVOCADO'
}

export enum TipoAccesoSensible {
  LECTURA = 'LECTURA',
  MODIFICACION = 'MODIFICACION',
  ELIMINACION = 'ELIMINACION',
  EXPORTACION = 'EXPORTACION',
  IMPRESION = 'IMPRESION'
}

export interface ConfiguracionCumplimiento {
  id: string;
  normativa: TipoNormativa;
  habilitado: boolean;
  configuracion: any;
  requiere_autorizacion_acceso: boolean;
  requiere_log_acceso: boolean;
  dias_retencion_logs: number;
  requiere_consentimiento_explicito: boolean;
  permite_portabilidad_datos: boolean;
  permite_derecho_olvido: boolean;
  dias_respuesta_solicitud: number;
  requiere_firma_electronica: boolean;
  requiere_expediente_electronico: boolean;
  requiere_respaldo_informacion: boolean;
  notas?: string;
  created_at: string;
  updated_at: string;
}

export interface ConsentimientoInformado {
  id: string;
  paciente_id: string;
  tipo: TipoConsentimiento;
  estado: EstadoConsentimiento;
  titulo: string;
  descripcion: string;
  riesgos?: string[];
  beneficios?: string[];
  alternativas?: string[];
  fecha_firma_paciente?: string;
  fecha_firma_medico?: string;
  created_at: string;
}

export interface LogAccesoSensible {
  id: string;
  usuario_id: string;
  recurso_tipo: string;
  recurso_id: string;
  paciente_id?: string;
  tipo_acceso: TipoAccesoSensible;
  accion: string;
  descripcion?: string;
  justificacion?: string;
  autorizado: boolean;
  ip_address?: string;
  created_at: string;
}

export interface SolicitudDatosPersonales {
  id: string;
  paciente_id: string;
  tipo_solicitud: string;
  descripcion: string;
  estado: string;
  fecha_limite: string;
  fecha_respuesta?: string;
  respuesta?: string;
  created_at: string;
}

export interface AuditoriaHIPAA {
  id: string;
  fecha_inicio: string;
  fecha_fin: string;
  total_accesos: number;
  accesos_autorizados: number;
  accesos_no_autorizados: number;
  nivel_cumplimiento: number;
  cumple_normativa: boolean;
  created_at: string;
}

export interface EstadisticasCumplimiento {
  total_consentimientos: number;
  consentimientos_activos: number;
  total_firmas: number;
  firmas_validas: number;
  logs_acceso_ultimo_mes: number;
  solicitudes_gdpr_pendientes: number;
}

// ==================== SERVICIO ====================

const cumplimientoService = {
  // ==================== CONFIGURACIÓN ====================

  async getConfiguraciones(): Promise<ConfiguracionCumplimiento[]> {
    const response = await api.get('/cumplimiento/configuracion');
    return response.data;
  },

  async getConfiguracion(normativa: TipoNormativa): Promise<ConfiguracionCumplimiento> {
    const response = await api.get(`/cumplimiento/configuracion/${normativa}`);
    return response.data;
  },

  async createConfiguracion(data: Partial<ConfiguracionCumplimiento>): Promise<any> {
    const response = await api.post('/cumplimiento/configuracion', data);
    return response.data;
  },

  // ==================== CONSENTIMIENTOS INFORMADOS ====================

  async crearConsentimiento(data: {
    paciente_id: string;
    tipo: TipoConsentimiento;
    titulo: string;
    descripcion: string;
    riesgos?: string[];
    beneficios?: string[];
    alternativas?: string[];
    consulta_id?: string;
  }): Promise<any> {
    const response = await api.post('/cumplimiento/consentimientos', data);
    return response.data;
  },

  async firmarConsentimientoPaciente(
    consentimientoId: string,
    contenido: string
  ): Promise<any> {
    const response = await api.post(
      `/cumplimiento/consentimientos/${consentimientoId}/firmar-paciente`,
      { contenido }
    );
    return response.data;
  },

  async firmarConsentimientoMedico(
    consentimientoId: string,
    contenido: string
  ): Promise<any> {
    const response = await api.post(
      `/cumplimiento/consentimientos/${consentimientoId}/firmar-medico`,
      { contenido }
    );
    return response.data;
  },

  async revocarConsentimiento(
    consentimientoId: string,
    motivo: string
  ): Promise<any> {
    const response = await api.post(
      `/cumplimiento/consentimientos/${consentimientoId}/revocar`,
      { motivo }
    );
    return response.data;
  },

  async getConsentimientosPaciente(
    pacienteId: string,
    tipo?: TipoConsentimiento
  ): Promise<ConsentimientoInformado[]> {
    const params = tipo ? { tipo } : {};
    const response = await api.get(
      `/cumplimiento/consentimientos/paciente/${pacienteId}`,
      { params }
    );
    return response.data;
  },

  // ==================== LOGS DE ACCESO SENSIBLE ====================

  async registrarAccesoSensible(data: {
    recurso_tipo: string;
    recurso_id: string;
    tipo_acceso: TipoAccesoSensible;
    accion: string;
    paciente_id?: string;
    descripcion?: string;
    datos_accedidos?: any;
    justificacion?: string;
    normativa_aplicable?: TipoNormativa;
  }): Promise<any> {
    const response = await api.post('/cumplimiento/logs-acceso', data);
    return response.data;
  },

  async getLogsAccesoPaciente(
    pacienteId: string,
    fechaInicio?: string,
    fechaFin?: string,
    limit: number = 100
  ): Promise<LogAccesoSensible[]> {
    const params: any = { limit };
    if (fechaInicio) params.fecha_inicio = fechaInicio;
    if (fechaFin) params.fecha_fin = fechaFin;

    const response = await api.get(
      `/cumplimiento/logs-acceso/paciente/${pacienteId}`,
      { params }
    );
    return response.data;
  },

  async getLogsAccesoUsuario(
    usuarioId: string,
    limit: number = 100
  ): Promise<LogAccesoSensible[]> {
    const response = await api.get(
      `/cumplimiento/logs-acceso/usuario/${usuarioId}`,
      { params: { limit } }
    );
    return response.data;
  },

  // ==================== SOLICITUDES DATOS PERSONALES (GDPR) ====================

  async crearSolicitudDatos(data: {
    tipo_solicitud: string;
    descripcion: string;
    datos_solicitados?: string[];
  }): Promise<any> {
    const response = await api.post('/cumplimiento/solicitudes-datos', data);
    return response.data;
  },

  async procesarSolicitudDatos(
    solicitudId: string,
    respuesta: string,
    archivoRespuestaUrl?: string
  ): Promise<any> {
    const response = await api.post(
      `/cumplimiento/solicitudes-datos/${solicitudId}/procesar`,
      { respuesta, archivo_respuesta_url: archivoRespuestaUrl }
    );
    return response.data;
  },

  async getSolicitudesPendientes(): Promise<SolicitudDatosPersonales[]> {
    const response = await api.get('/cumplimiento/solicitudes-datos/pendientes');
    return response.data;
  },

  // ==================== AUDITORÍA HIPAA ====================

  async crearAuditoriaHIPAA(
    fechaInicio: string,
    fechaFin: string
  ): Promise<any> {
    const response = await api.post('/cumplimiento/auditoria-hipaa', {
      fecha_inicio: fechaInicio,
      fecha_fin: fechaFin
    });
    return response.data;
  },

  async getAuditoriasRecientes(limit: number = 10): Promise<AuditoriaHIPAA[]> {
    const response = await api.get('/cumplimiento/auditoria-hipaa', {
      params: { limit }
    });
    return response.data;
  },

  // ==================== ESTADÍSTICAS ====================

  async getEstadisticas(): Promise<EstadisticasCumplimiento> {
    const response = await api.get('/cumplimiento/estadisticas');
    return response.data;
  }
};

export default cumplimientoService;
