import api from './api';

export interface DashboardData {
  citas_pendientes: number;
  estudios_pendientes: number;
  mensajes_sin_leer: number;
  recordatorios_activos: number;
  proxima_cita?: any;
}

export interface CitaPaciente {
  id: string;
  tipo_cita: string;
  especialidad_solicitada?: string;
  motivo_consulta: string;
  fecha_solicitada: string;
  hora_solicitada?: string;
  estado: string;
  notas_paciente?: string;
}

export interface SolicitudEstudio {
  id: string;
  tipo_estudio: string;
  nombre_estudio: string;
  descripcion?: string;
  estado: string;
  fecha_solicitud: string;
  resultado_disponible: boolean;
}

export interface MensajePacienteMedico {
  id: string;
  asunto: string;
  mensaje: string;
  leido: boolean;
  fecha_envio: string;
  medico_id: string;
}

export interface RecordatorioMedicamento {
  id: string;
  nombre_medicamento: string;
  dosis: string;
  frecuencia: string;
  horarios: string[];
  indicaciones?: string;
  activo: boolean;
}

export interface ConfiguracionPortal {
  id: string;
  notificaciones_email: boolean;
  notificaciones_sms: boolean;
  notificaciones_push: boolean;
  recordatorios_citas: boolean;
  recordatorios_medicamentos: boolean;
  recordatorios_estudios: boolean;
  idioma: string;
  tema: string;
}

class PortalPacienteService {
  async getDashboard(pacienteId: string): Promise<DashboardData> {
    const response = await api.get(`/portal-paciente/dashboard/${pacienteId}`);
    return response.data;
  }

  async getCitas(pacienteId: string): Promise<CitaPaciente[]> {
    const response = await api.get(`/portal-paciente/citas/${pacienteId}`);
    return response.data;
  }

  async crearCita(data: any): Promise<CitaPaciente> {
    const response = await api.post('/portal-paciente/citas', data);
    return response.data;
  }

  async cancelarCita(citaId: string, motivo: string): Promise<void> {
    await api.post(`/portal-paciente/citas/${citaId}/cancelar`, { motivo_cancelacion: motivo });
  }

  async getSolicitudesEstudio(pacienteId: string): Promise<SolicitudEstudio[]> {
    const response = await api.get(`/portal-paciente/estudios/${pacienteId}`);
    return response.data;
  }

  async crearSolicitudEstudio(data: any): Promise<SolicitudEstudio> {
    const response = await api.post('/portal-paciente/estudios', data);
    return response.data;
  }

  async getMensajes(pacienteId: string): Promise<MensajePacienteMedico[]> {
    const response = await api.get(`/portal-paciente/mensajes/${pacienteId}`);
    return response.data;
  }

  async enviarMensaje(data: any): Promise<MensajePacienteMedico> {
    const response = await api.post('/portal-paciente/mensajes', data);
    return response.data;
  }

  async marcarMensajeLeido(mensajeId: string): Promise<void> {
    await api.patch(`/portal-paciente/mensajes/${mensajeId}/leer`);
  }

  async getRecordatorios(pacienteId: string): Promise<RecordatorioMedicamento[]> {
    const response = await api.get(`/portal-paciente/recordatorios/${pacienteId}`);
    return response.data;
  }

  async crearRecordatorio(data: any): Promise<RecordatorioMedicamento> {
    const response = await api.post('/portal-paciente/recordatorios', data);
    return response.data;
  }

  async eliminarRecordatorio(recordatorioId: string): Promise<void> {
    await api.delete(`/portal-paciente/recordatorios/${recordatorioId}`);
  }

  async getConfiguracion(pacienteId: string): Promise<ConfiguracionPortal> {
    const response = await api.get(`/portal-paciente/configuracion/${pacienteId}`);
    return response.data;
  }

  async actualizarConfiguracion(pacienteId: string, data: Partial<ConfiguracionPortal>): Promise<ConfiguracionPortal> {
    const response = await api.put(`/portal-paciente/configuracion/${pacienteId}`, data);
    return response.data;
  }
}

export default new PortalPacienteService();
