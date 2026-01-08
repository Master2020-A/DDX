/**
 * Servicio para interactuar con la API de Aplicación Móvil
 */

import api from './api';

// ==================== TIPOS ====================

export enum PlataformaMovil {
  IOS = 'ios',
  ANDROID = 'android',
}

export enum EstadoDispositivo {
  ACTIVO = 'activo',
  INACTIVO = 'inactivo',
  BLOQUEADO = 'bloqueado',
  REVOCADO = 'revocado',
}

export enum TipoNotificacion {
  CITA = 'cita',
  RECORDATORIO = 'recordatorio',
  RESULTADO = 'resultado',
  MENSAJE = 'mensaje',
  ALERTA = 'alerta',
  SISTEMA = 'sistema',
}

export enum EstadoNotificacion {
  PENDIENTE = 'pendiente',
  ENVIADA = 'enviada',
  ENTREGADA = 'entregada',
  LEIDA = 'leida',
  FALLIDA = 'fallida',
}

export enum TipoDocumento {
  IDENTIFICACION = 'identificacion',
  RECETA = 'receta',
  LABORATORIO = 'laboratorio',
  ESTUDIO = 'estudio',
  CONSENTIMIENTO = 'consentimiento',
  OTRO = 'otro',
}

export interface DispositivoMovil {
  id: string;
  usuario_id: string;
  plataforma: PlataformaMovil;
  modelo?: string;
  version_os?: string;
  version_app?: string;
  device_id: string;
  estado: EstadoDispositivo;
  notificaciones_habilitadas: boolean;
  biometria_habilitada: boolean;
  sincronizacion_automatica: boolean;
  ultimo_acceso?: string;
  fecha_registro: string;
  created_at: string;
}

export interface NotificacionPush {
  id: string;
  dispositivo_id?: string;
  usuario_id: string;
  tipo: TipoNotificacion;
  titulo: string;
  mensaje: string;
  datos?: any;
  accion_url?: string;
  estado: EstadoNotificacion;
  prioridad: string;
  programada_para?: string;
  fecha_envio?: string;
  fecha_entrega?: string;
  fecha_lectura?: string;
  mensaje_error?: string;
  created_at: string;
}

export interface DocumentoEscaneado {
  id: string;
  dispositivo_id: string;
  usuario_id: string;
  paciente_id?: string;
  tipo: TipoDocumento;
  nombre: string;
  descripcion?: string;
  ruta_archivo: string;
  ruta_thumbnail?: string;
  tamano_bytes?: number;
  mime_type?: string;
  texto_extraido?: string;
  ocr_procesado: boolean;
  confianza_ocr?: number;
  firmado: boolean;
  fecha_firma?: string;
  sincronizado: boolean;
  fecha_sincronizacion?: string;
  created_at: string;
}

export interface CitaMovil {
  id: string;
  paciente_id: string;
  medico_id: string;
  dispositivo_id?: string;
  fecha_hora: string;
  duracion_minutos: number;
  motivo?: string;
  notas?: string;
  confirmada: boolean;
  fecha_confirmacion?: string;
  cancelada: boolean;
  fecha_cancelacion?: string;
  motivo_cancelacion?: string;
  recordatorio_enviado: boolean;
  fecha_recordatorio?: string;
  es_telemedicina: boolean;
  url_videollamada?: string;
  created_at: string;
}

export interface ConfiguracionAppMovil {
  id: string;
  usuario_id: string;
  notificaciones_citas: boolean;
  notificaciones_resultados: boolean;
  notificaciones_mensajes: boolean;
  notificaciones_recordatorios: boolean;
  recordatorio_citas_minutos: number;
  sincronizar_solo_wifi: boolean;
  sincronizar_automaticamente: boolean;
  intervalo_sincronizacion_minutos: number;
  requerir_biometria: boolean;
  timeout_sesion_minutos: number;
  tema: string;
  idioma: string;
  limpiar_cache_automaticamente: boolean;
  dias_retener_datos_offline: number;
  created_at: string;
}

export interface EstadisticasAppMovil {
  total_dispositivos: number;
  dispositivos_activos: number;
  dispositivos_ios: number;
  dispositivos_android: number;
  notificaciones_enviadas_hoy: number;
  notificaciones_pendientes: number;
  documentos_escaneados_mes: number;
  citas_programadas: number;
  sincronizaciones_pendientes: number;
}

export interface EstadoSincronizacion {
  ultima_sincronizacion?: string;
  operaciones_pendientes: number;
  operaciones_en_progreso: number;
  operaciones_fallidas: number;
  conflictos_sin_resolver: number;
}

// ==================== SERVICIO ====================

class AppMovilService {
  // ==================== DISPOSITIVOS ====================

  async listarDispositivos(): Promise<DispositivoMovil[]> {
    const response = await api.get('/app-movil/dispositivos');
    return response.data;
  }

  async actualizarDispositivo(id: string, data: Partial<DispositivoMovil>): Promise<DispositivoMovil> {
    const response = await api.patch(`/app-movil/dispositivos/${id}`, data);
    return response.data;
  }

  async revocarDispositivo(id: string): Promise<void> {
    await api.delete(`/app-movil/dispositivos/${id}`);
  }

  // ==================== NOTIFICACIONES ====================

  async listarNotificaciones(limite: number = 50): Promise<NotificacionPush[]> {
    const response = await api.get('/app-movil/notificaciones', {
      params: { limite },
    });
    return response.data;
  }

  async crearNotificacion(data: {
    usuario_id: string;
    tipo: TipoNotificacion;
    titulo: string;
    mensaje: string;
    datos?: any;
    accion_url?: string;
    prioridad?: string;
  }): Promise<NotificacionPush> {
    const response = await api.post('/app-movil/notificaciones', data);
    return response.data;
  }

  async enviarNotificacionMasiva(data: {
    titulo: string;
    mensaje: string;
    tipo?: TipoNotificacion;
    usuarios_ids?: string[];
    dispositivos_ids?: string[];
    datos?: any;
    accion_url?: string;
    prioridad?: string;
  }): Promise<{ mensaje: string; total: number }> {
    const response = await api.post('/app-movil/notificaciones/enviar', data);
    return response.data;
  }

  async marcarNotificacionLeida(id: string): Promise<NotificacionPush> {
    const response = await api.patch(`/app-movil/notificaciones/${id}/leer`);
    return response.data;
  }

  // ==================== DOCUMENTOS ====================

  async listarDocumentos(params?: {
    paciente_id?: string;
    tipo?: TipoDocumento;
    limite?: number;
  }): Promise<DocumentoEscaneado[]> {
    const response = await api.get('/app-movil/documentos', { params });
    return response.data;
  }

  async subirDocumento(data: {
    tipo: TipoDocumento;
    nombre: string;
    archivo: File;
    descripcion?: string;
    paciente_id?: string;
    dispositivo_id?: string;
  }): Promise<DocumentoEscaneado> {
    const formData = new FormData();
    formData.append('archivo', data.archivo);
    formData.append('tipo', data.tipo);
    formData.append('nombre', data.nombre);
    if (data.descripcion) formData.append('descripcion', data.descripcion);
    if (data.paciente_id) formData.append('paciente_id', data.paciente_id);
    if (data.dispositivo_id) formData.append('dispositivo_id', data.dispositivo_id);

    const response = await api.post('/app-movil/documentos', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async firmarDocumento(id: string, firmaData: any): Promise<DocumentoEscaneado> {
    const response = await api.post(`/app-movil/documentos/${id}/firmar`, {
      firma_biometrica: firmaData,
    });
    return response.data;
  }

  // ==================== CITAS ====================

  async listarCitas(params?: {
    fecha_desde?: string;
    fecha_hasta?: string;
  }): Promise<CitaMovil[]> {
    const response = await api.get('/app-movil/citas', { params });
    return response.data;
  }

  async crearCita(data: {
    paciente_id: string;
    medico_id: string;
    fecha_hora: string;
    duracion_minutos?: number;
    motivo?: string;
    notas?: string;
    es_telemedicina?: boolean;
  }): Promise<CitaMovil> {
    const response = await api.post('/app-movil/citas', data);
    return response.data;
  }

  async actualizarCita(id: string, data: Partial<CitaMovil>): Promise<CitaMovil> {
    const response = await api.patch(`/app-movil/citas/${id}`, data);
    return response.data;
  }

  // ==================== CONFIGURACIÓN ====================

  async obtenerConfiguracion(): Promise<ConfiguracionAppMovil> {
    const response = await api.get('/app-movil/configuracion');
    return response.data;
  }

  async actualizarConfiguracion(data: Partial<ConfiguracionAppMovil>): Promise<ConfiguracionAppMovil> {
    const response = await api.patch('/app-movil/configuracion', data);
    return response.data;
  }

  // ==================== SINCRONIZACIÓN ====================

  async obtenerEstadoSincronizacion(dispositivo_id: string): Promise<EstadoSincronizacion> {
    const response = await api.get('/app-movil/sincronizacion/estado', {
      params: { dispositivo_id },
    });
    return response.data;
  }

  // ==================== ESTADÍSTICAS ====================

  async obtenerEstadisticas(): Promise<EstadisticasAppMovil> {
    const response = await api.get('/app-movil/estadisticas');
    return response.data;
  }

  // ==================== UTILIDADES ====================

  formatearTamano(bytes?: number): string {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
  }

  obtenerColorEstado(estado: EstadoDispositivo): string {
    switch (estado) {
      case EstadoDispositivo.ACTIVO:
        return 'green';
      case EstadoDispositivo.INACTIVO:
        return 'gray';
      case EstadoDispositivo.BLOQUEADO:
        return 'orange';
      case EstadoDispositivo.REVOCADO:
        return 'red';
      default:
        return 'gray';
    }
  }

  obtenerTextoEstado(estado: EstadoDispositivo): string {
    switch (estado) {
      case EstadoDispositivo.ACTIVO:
        return 'Activo';
      case EstadoDispositivo.INACTIVO:
        return 'Inactivo';
      case EstadoDispositivo.BLOQUEADO:
        return 'Bloqueado';
      case EstadoDispositivo.REVOCADO:
        return 'Revocado';
      default:
        return estado;
    }
  }

  obtenerIconoPlataforma(plataforma: PlataformaMovil): string {
    switch (plataforma) {
      case PlataformaMovil.IOS:
        return '🍎';
      case PlataformaMovil.ANDROID:
        return '🤖';
      default:
        return '📱';
    }
  }

  obtenerColorNotificacion(estado: EstadoNotificacion): string {
    switch (estado) {
      case EstadoNotificacion.LEIDA:
        return 'gray';
      case EstadoNotificacion.ENTREGADA:
        return 'blue';
      case EstadoNotificacion.ENVIADA:
        return 'green';
      case EstadoNotificacion.PENDIENTE:
        return 'yellow';
      case EstadoNotificacion.FALLIDA:
        return 'red';
      default:
        return 'gray';
    }
  }

  obtenerTextoTipoNotificacion(tipo: TipoNotificacion): string {
    switch (tipo) {
      case TipoNotificacion.CITA:
        return 'Cita';
      case TipoNotificacion.RECORDATORIO:
        return 'Recordatorio';
      case TipoNotificacion.RESULTADO:
        return 'Resultado';
      case TipoNotificacion.MENSAJE:
        return 'Mensaje';
      case TipoNotificacion.ALERTA:
        return 'Alerta';
      case TipoNotificacion.SISTEMA:
        return 'Sistema';
      default:
        return tipo;
    }
  }

  obtenerIconoTipoDocumento(tipo: TipoDocumento): string {
    switch (tipo) {
      case TipoDocumento.IDENTIFICACION:
        return '🪪';
      case TipoDocumento.RECETA:
        return '💊';
      case TipoDocumento.LABORATORIO:
        return '🧪';
      case TipoDocumento.ESTUDIO:
        return '📋';
      case TipoDocumento.CONSENTIMIENTO:
        return '✍️';
      case TipoDocumento.OTRO:
        return '📄';
      default:
        return '📄';
    }
  }

  calcularTiempoTranscurrido(fecha: string): string {
    const ahora = new Date();
    const fechaObj = new Date(fecha);
    const diff = ahora.getTime() - fechaObj.getTime();

    const minutos = Math.floor(diff / 60000);
    const horas = Math.floor(diff / 3600000);
    const dias = Math.floor(diff / 86400000);

    if (minutos < 1) return 'Ahora';
    if (minutos < 60) return `Hace ${minutos} min`;
    if (horas < 24) return `Hace ${horas}h`;
    if (dias < 30) return `Hace ${dias}d`;
    return fechaObj.toLocaleDateString('es-MX');
  }
}

export default new AppMovilService();
