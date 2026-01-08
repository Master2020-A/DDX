import api from './api';

export interface DashboardData {
  proxima_cita: CitaPaciente | null;
  citas_pendientes: number;
  solicitudes_pendientes: number;
  mensajes_no_leidos: number;
  recordatorios_activos: number;
  pagos_pendientes: number;
  ultima_consulta: string | null;
  proximos_recordatorios: RecordatorioMedicamento[];
}

export interface CitaPaciente {
  id: string;
  paciente_id: string;
  medico_id?: string;
  tipo_cita: string;
  especialidad_solicitada?: string;
  motivo_consulta: string;
  fecha_solicitada: string;
  hora_solicitada?: string;
  fecha_confirmada?: string;
  duracion_minutos?: number;
  estado: string;
  notas_paciente?: string;
  notas_medico?: string;
  recordatorio_enviado?: boolean;
  fecha_recordatorio?: string;
  fecha_cancelacion?: string;
  motivo_cancelacion?: string;
  cancelado_por?: string;
  created_at: string;
  updated_at: string;
}

export interface SolicitudEstudio {
  id: string;
  paciente_id: string;
  medico_solicitante_id?: string;
  medico_autorizador_id?: string;
  tipo_estudio: string;
  nombre_estudio: string;
  descripcion?: string;
  indicaciones_especiales?: string;
  estado: string;
  prioridad?: string;
  fecha_solicitud: string;
  fecha_autorizacion?: string;
  fecha_programada?: string;
  fecha_realizacion?: string;
  resultado_disponible: boolean;
  resultado_id?: string;
  url_resultado?: string;
  notas_paciente?: string;
  notas_autorizacion?: string;
  motivo_rechazo?: string;
  created_at: string;
  updated_at: string;
}

export interface PagoServicio {
  id: string;
  paciente_id: string;
  cita_id?: string;
  solicitud_estudio_id?: string;
  concepto: string;
  descripcion?: string;
  monto: number;
  moneda: string;
  metodo_pago: string;
  referencia_pago?: string;
  estado: string;
  fecha_pago?: string;
  fecha_procesado?: string;
  fecha_completado?: string;
  datos_transaccion?: any;
  comprobante_url?: string;
  factura_id?: string;
  reembolsado: boolean;
  fecha_reembolso?: string;
  motivo_reembolso?: string;
  created_at: string;
  updated_at: string;
}

export interface MensajePacienteMedico {
  id: string;
  paciente_id: string;
  medico_id: string;
  remitente_tipo: string;
  asunto?: string;
  mensaje: string;
  archivos_adjuntos?: any;
  estado: string;
  leido: boolean;
  fecha_lectura?: string;
  mensaje_padre_id?: string;
  created_at: string;
  updated_at: string;
}

export interface RecordatorioMedicamento {
  id: string;
  paciente_id: string;
  receta_id?: string;
  nombre_medicamento: string;
  dosis: string;
  via_administracion?: string;
  indicaciones?: string;
  frecuencia: string;
  horarios: string[];
  fecha_inicio: string;
  fecha_fin?: string;
  duracion_dias?: number;
  activo: boolean;
  pausado: boolean;
  notificar_email: boolean;
  notificar_sms: boolean;
  notificar_push: boolean;
  ultima_toma_registrada?: string;
  tomas_registradas: number;
  tomas_omitidas: number;
  created_at: string;
  updated_at: string;
}

export interface RegistroTomaMedicamento {
  id: string;
  recordatorio_id: string;
  fecha_programada: string;
  fecha_real?: string;
  tomado: boolean;
  omitido: boolean;
  motivo_omision?: string;
  notas?: string;
  efectos_secundarios?: string;
  created_at: string;
}

export interface ConfiguracionPortal {
  id: string;
  paciente_id: string;
  notificaciones_email: boolean;
  notificaciones_sms: boolean;
  notificaciones_push: boolean;
  compartir_datos_investigacion: boolean;
  mostrar_perfil_publico: boolean;
  idioma: string;
  tema: string;
  zona_horaria: string;
  recordatorios_citas: boolean;
  recordatorios_medicamentos: boolean;
  recordatorios_estudios: boolean;
  created_at: string;
  updated_at: string;
}

const portalPacienteService = {
  // Dashboard
  getDashboard: async (pacienteId: string): Promise<DashboardData> => {
    const response = await api.get(`/portal-paciente/dashboard/${pacienteId}`);
    return response.data;
  },

  // Expediente
  getExpediente: async (pacienteId: string) => {
    const response = await api.get(`/portal-paciente/expediente/${pacienteId}`);
    return response.data;
  },

  // Citas
  getCitas: async (pacienteId: string, estado?: string): Promise<CitaPaciente[]> => {
    const params = new URLSearchParams();
    params.append('paciente_id', pacienteId);
    if (estado) params.append('estado', estado);
    const response = await api.get(`/portal-paciente/citas?${params.toString()}`);
    return response.data;
  },

  getCita: async (citaId: string): Promise<CitaPaciente> => {
    const response = await api.get(`/portal-paciente/citas/${citaId}`);
    return response.data;
  },

  crearCita: async (data: Partial<CitaPaciente>): Promise<CitaPaciente> => {
    const response = await api.post('/portal-paciente/citas', data);
    return response.data;
  },

  actualizarCita: async (citaId: string, data: Partial<CitaPaciente>): Promise<CitaPaciente> => {
    const response = await api.put(`/portal-paciente/citas/${citaId}`, data);
    return response.data;
  },

  cancelarCita: async (citaId: string, motivo: string): Promise<CitaPaciente> => {
    const response = await api.post(`/portal-paciente/citas/${citaId}/cancelar`, { motivo_cancelacion: motivo });
    return response.data;
  },

  // Solicitudes de Estudios
  getSolicitudesEstudios: async (pacienteId: string, estado?: string): Promise<SolicitudEstudio[]> => {
    const params = new URLSearchParams();
    params.append('paciente_id', pacienteId);
    if (estado) params.append('estado', estado);
    const response = await api.get(`/portal-paciente/solicitudes-estudios?${params.toString()}`);
    return response.data;
  },

  crearSolicitudEstudio: async (data: Partial<SolicitudEstudio>): Promise<SolicitudEstudio> => {
    const response = await api.post('/portal-paciente/solicitudes-estudios', data);
    return response.data;
  },

  // Pagos
  getPagos: async (pacienteId: string, estado?: string): Promise<PagoServicio[]> => {
    const params = new URLSearchParams();
    params.append('paciente_id', pacienteId);
    if (estado) params.append('estado', estado);
    const response = await api.get(`/portal-paciente/pagos?${params.toString()}`);
    return response.data;
  },

  crearPago: async (data: Partial<PagoServicio>): Promise<PagoServicio> => {
    const response = await api.post('/portal-paciente/pagos', data);
    return response.data;
  },

  // Mensajería
  getMensajes: async (pacienteId: string, medicoId?: string): Promise<MensajePacienteMedico[]> => {
    const params = new URLSearchParams();
    params.append('paciente_id', pacienteId);
    if (medicoId) params.append('medico_id', medicoId);
    const response = await api.get(`/portal-paciente/mensajes?${params.toString()}`);
    return response.data;
  },

  enviarMensaje: async (data: Partial<MensajePacienteMedico>): Promise<MensajePacienteMedico> => {
    const response = await api.post('/portal-paciente/mensajes', data);
    return response.data;
  },

  marcarMensajeLeido: async (mensajeId: string): Promise<MensajePacienteMedico> => {
    const response = await api.post(`/portal-paciente/mensajes/${mensajeId}/marcar-leido`);
    return response.data;
  },

  // Recordatorios de Medicamentos
  getRecordatorios: async (pacienteId: string, activo?: boolean): Promise<RecordatorioMedicamento[]> => {
    const params = new URLSearchParams();
    params.append('paciente_id', pacienteId);
    if (activo !== undefined) params.append('activo', activo.toString());
    const response = await api.get(`/portal-paciente/recordatorios?${params.toString()}`);
    return response.data;
  },

  crearRecordatorio: async (data: Partial<RecordatorioMedicamento>): Promise<RecordatorioMedicamento> => {
    const response = await api.post('/portal-paciente/recordatorios', data);
    return response.data;
  },

  actualizarRecordatorio: async (recordatorioId: string, data: Partial<RecordatorioMedicamento>): Promise<RecordatorioMedicamento> => {
    const response = await api.put(`/portal-paciente/recordatorios/${recordatorioId}`, data);
    return response.data;
  },

  pausarRecordatorio: async (recordatorioId: string): Promise<RecordatorioMedicamento> => {
    const response = await api.post(`/portal-paciente/recordatorios/${recordatorioId}/pausar`);
    return response.data;
  },

  reanudarRecordatorio: async (recordatorioId: string): Promise<RecordatorioMedicamento> => {
    const response = await api.post(`/portal-paciente/recordatorios/${recordatorioId}/reanudar`);
    return response.data;
  },

  registrarToma: async (recordatorioId: string, data: Partial<RegistroTomaMedicamento>): Promise<RegistroTomaMedicamento> => {
    const response = await api.post(`/portal-paciente/recordatorios/${recordatorioId}/registrar-toma`, data);
    return response.data;
  },

  // Configuración
  getConfiguracion: async (pacienteId: string): Promise<ConfiguracionPortal> => {
    const response = await api.get(`/portal-paciente/configuracion/${pacienteId}`);
    return response.data;
  },

  actualizarConfiguracion: async (pacienteId: string, data: Partial<ConfiguracionPortal>): Promise<ConfiguracionPortal> => {
    const response = await api.put(`/portal-paciente/configuracion/${pacienteId}`, data);
    return response.data;
  },

  // Accesos al Expediente
  getAccesosExpediente: async (pacienteId: string, limit: number = 50) => {
    const response = await api.get(`/portal-paciente/accesos-expediente/${pacienteId}?limit=${limit}`);
    return response.data;
  },
};

export default portalPacienteService;
