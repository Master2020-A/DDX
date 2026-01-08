/**
 * Servicio para interactuar con la API de Backups y Recuperación
 */

import api from './api';

// ==================== TIPOS ====================

export enum TipoBackup {
  COMPLETO = 'completo',
  INCREMENTAL = 'incremental',
  DIFERENCIAL = 'diferencial',
  TRANSACCIONAL = 'transaccional',
}

export enum EstadoBackup {
  PENDIENTE = 'pendiente',
  EN_PROGRESO = 'en_progreso',
  COMPLETADO = 'completado',
  FALLIDO = 'fallido',
  CANCELADO = 'cancelado',
}

export enum TipoRestauracion {
  COMPLETA = 'completa',
  POINT_IN_TIME = 'point_in_time',
  TABLA_ESPECIFICA = 'tabla_especifica',
  DATOS_ESPECIFICOS = 'datos_especificos',
}

export enum EstadoRestauracion {
  PENDIENTE = 'pendiente',
  EN_PROGRESO = 'en_progreso',
  COMPLETADO = 'completado',
  FALLIDO = 'fallido',
  CANCELADO = 'cancelado',
}

export enum NivelSeveridad {
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error',
  CRITICAL = 'critical',
}

export interface Backup {
  id: string;
  tipo: TipoBackup;
  estado: EstadoBackup;
  nombre: string;
  descripcion?: string;
  ruta_archivo: string;
  tamano_bytes?: number;
  base_datos: string;
  version_postgresql?: string;
  checksum_md5?: string;
  checksum_sha256?: string;
  comprimido: boolean;
  algoritmo_compresion?: string;
  encriptado: boolean;
  fecha_inicio: string;
  fecha_fin?: string;
  duracion_segundos?: number;
  fecha_expiracion?: string;
  retencion_dias: number;
  automatico: boolean;
  mensaje_error?: string;
  created_at: string;
  updated_at?: string;
}

export interface BackupCreate {
  tipo?: TipoBackup;
  nombre: string;
  descripcion?: string;
}

export interface ProgramacionBackup {
  id: string;
  nombre: string;
  descripcion?: string;
  activo: boolean;
  tipo_backup: TipoBackup;
  cron_expresion: string;
  zona_horaria: string;
  retencion_dias: number;
  max_backups_mantener: number;
  base_datos: string;
  ruta_destino: string;
  compresion: boolean;
  encriptacion: boolean;
  notificar_exito: boolean;
  notificar_fallo: boolean;
  emails_notificacion?: string[];
  ultima_ejecucion?: string;
  proximo_ejecucion?: string;
  created_at: string;
  updated_at?: string;
}

export interface ProgramacionBackupCreate {
  nombre: string;
  descripcion?: string;
  tipo_backup?: TipoBackup;
  cron_expresion: string;
  zona_horaria?: string;
  retencion_dias?: number;
  max_backups_mantener?: number;
  compresion?: boolean;
  encriptacion?: boolean;
  notificar_exito?: boolean;
  notificar_fallo?: boolean;
  emails_notificacion?: string[];
}

export interface ProgramacionBackupUpdate {
  activo?: boolean;
  cron_expresion?: string;
  retencion_dias?: number;
  notificar_exito?: boolean;
  notificar_fallo?: boolean;
  emails_notificacion?: string[];
}

export interface Restauracion {
  id: string;
  backup_id: string;
  tipo: TipoRestauracion;
  estado: EstadoRestauracion;
  nombre: string;
  descripcion?: string;
  motivo: string;
  punto_tiempo?: string;
  tablas_restaurar?: string[];
  base_datos_destino: string;
  sobrescribir: boolean;
  fecha_inicio: string;
  fecha_fin?: string;
  duracion_segundos?: number;
  mensaje_error?: string;
  validacion_exitosa?: boolean;
  resultado_validacion?: any;
  usuario_id: string;
  aprobado_por?: string;
  fecha_aprobacion?: string;
  created_at: string;
  updated_at?: string;
}

export interface RestauracionCreate {
  backup_id: string;
  tipo?: TipoRestauracion;
  nombre: string;
  descripcion?: string;
  motivo: string;
  punto_tiempo?: string;
  tablas_restaurar?: string[];
  sobrescribir?: boolean;
}

export interface MonitoreoSalud {
  id: string;
  timestamp: string;
  conexiones_activas?: number;
  conexiones_maximas?: number;
  tamano_bd_bytes?: number;
  transacciones_por_segundo?: number;
  uso_cpu_porcentaje?: number;
  uso_memoria_porcentaje?: number;
  uso_disco_porcentaje?: number;
  espacio_disco_libre_gb?: number;
  tiempo_respuesta_promedio_ms?: number;
  requests_por_minuto?: number;
  errores_por_minuto?: number;
  estado_sistema?: string;
  disponibilidad_porcentaje?: number;
  alertas_activas: number;
}

export interface AlertaBackup {
  id: string;
  severidad: NivelSeveridad;
  tipo: string;
  titulo: string;
  mensaje: string;
  backup_id?: string;
  restauracion_id?: string;
  replicacion_id?: string;
  activa: boolean;
  fecha_resolucion?: string;
  resuelto_por?: string;
  notas_resolucion?: string;
  notificado: boolean;
  fecha_notificacion?: string;
  created_at: string;
  updated_at?: string;
}

export interface PlanRecuperacion {
  id: string;
  nombre: string;
  descripcion?: string;
  activo: boolean;
  rto_minutos: number;
  rpo_minutos: number;
  procedimientos: any[];
  contactos_emergencia?: any[];
  recursos_requeridos?: string[];
  ultima_prueba?: string;
  proxima_prueba?: string;
  frecuencia_prueba_dias: number;
  resultado_ultima_prueba?: string;
  created_at: string;
  updated_at?: string;
}

export interface PlanRecuperacionCreate {
  nombre: string;
  descripcion?: string;
  rto_minutos: number;
  rpo_minutos: number;
  procedimientos: any[];
  contactos_emergencia?: any[];
  recursos_requeridos?: string[];
  frecuencia_prueba_dias?: number;
}

export interface EstadisticasBackups {
  total_backups: number;
  backups_completados: number;
  backups_fallidos: number;
  ultimo_backup: {
    fecha?: string;
    nombre?: string;
    tamano_mb: number;
  };
  tamano_total_gb: number;
  programaciones_activas: number;
}

export interface EstadoSistema {
  estado: string;
  disponibilidad_porcentaje: number;
  uptime_dias: number;
  ultimo_backup_exitoso?: string;
  alertas_activas: number;
  replicacion_activa: boolean;
  espacio_disco_libre_gb: number;
}

// ==================== SERVICIO ====================

class BackupsService {
  // ==================== BACKUPS ====================

  async crearBackup(data: BackupCreate): Promise<Backup> {
    const response = await api.post('/backups/', data);
    return response.data;
  }

  async listarBackups(params?: {
    tipo?: TipoBackup;
    estado?: EstadoBackup;
    limite?: number;
  }): Promise<Backup[]> {
    const response = await api.get('/backups/', { params });
    return response.data;
  }

  async obtenerBackup(id: string): Promise<Backup> {
    const response = await api.get(`/backups/${id}`);
    return response.data;
  }

  async eliminarBackup(id: string): Promise<void> {
    await api.delete(`/backups/${id}`);
  }

  async limpiarBackupsAntiguos(diasRetencion: number = 30): Promise<{ mensaje: string; eliminados: number }> {
    const response = await api.post('/backups/limpiar-antiguos', null, {
      params: { dias_retencion: diasRetencion },
    });
    return response.data;
  }

  // ==================== PROGRAMACIÓN ====================

  async crearProgramacion(data: ProgramacionBackupCreate): Promise<ProgramacionBackup> {
    const response = await api.post('/backups/programacion', data);
    return response.data;
  }

  async listarProgramaciones(activo?: boolean): Promise<ProgramacionBackup[]> {
    const response = await api.get('/backups/programacion', {
      params: activo !== undefined ? { activo } : {},
    });
    return response.data;
  }

  async actualizarProgramacion(id: string, data: ProgramacionBackupUpdate): Promise<ProgramacionBackup> {
    const response = await api.patch(`/backups/programacion/${id}`, data);
    return response.data;
  }

  // ==================== RESTAURACIÓN ====================

  async crearRestauracion(data: RestauracionCreate): Promise<Restauracion> {
    const response = await api.post('/backups/restauracion', data);
    return response.data;
  }

  async ejecutarRestauracion(id: string): Promise<Restauracion> {
    const response = await api.post(`/backups/restauracion/${id}/ejecutar`);
    return response.data;
  }

  async listarRestauraciones(limite: number = 50): Promise<Restauracion[]> {
    const response = await api.get('/backups/restauracion', {
      params: { limite },
    });
    return response.data;
  }

  // ==================== MONITOREO ====================

  async registrarSaludSistema(): Promise<MonitoreoSalud> {
    const response = await api.post('/backups/monitoreo/salud');
    return response.data;
  }

  async obtenerSaludReciente(horas: number = 24): Promise<MonitoreoSalud[]> {
    const response = await api.get('/backups/monitoreo/salud/reciente', {
      params: { horas },
    });
    return response.data;
  }

  // ==================== ALERTAS ====================

  async listarAlertas(activasSolo: boolean = true, limite: number = 50): Promise<AlertaBackup[]> {
    const response = await api.get('/backups/alertas', {
      params: { activas_solo: activasSolo, limite },
    });
    return response.data;
  }

  async resolverAlerta(id: string, notas: string): Promise<AlertaBackup> {
    const response = await api.post(`/backups/alertas/${id}/resolver`, { notas });
    return response.data;
  }

  // ==================== ESTADÍSTICAS ====================

  async obtenerEstadisticas(): Promise<EstadisticasBackups> {
    const response = await api.get('/backups/estadisticas');
    return response.data;
  }

  async obtenerEstadoSistema(): Promise<EstadoSistema> {
    const response = await api.get('/backups/estado-sistema');
    return response.data;
  }

  // ==================== PLANES DE RECUPERACIÓN ====================

  async crearPlanRecuperacion(data: PlanRecuperacionCreate): Promise<PlanRecuperacion> {
    const response = await api.post('/backups/planes-recuperacion', data);
    return response.data;
  }

  async listarPlanesRecuperacion(activo?: boolean): Promise<PlanRecuperacion[]> {
    const response = await api.get('/backups/planes-recuperacion', {
      params: activo !== undefined ? { activo } : {},
    });
    return response.data;
  }

  // ==================== UTILIDADES ====================

  formatearTamano(bytes?: number): string {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
  }

  formatearDuracion(segundos?: number): string {
    if (!segundos) return '0s';
    const horas = Math.floor(segundos / 3600);
    const minutos = Math.floor((segundos % 3600) / 60);
    const segs = segundos % 60;

    const partes = [];
    if (horas > 0) partes.push(`${horas}h`);
    if (minutos > 0) partes.push(`${minutos}m`);
    if (segs > 0 || partes.length === 0) partes.push(`${segs}s`);

    return partes.join(' ');
  }

  obtenerColorEstado(estado: EstadoBackup | EstadoRestauracion): string {
    switch (estado) {
      case 'completado':
        return 'green';
      case 'en_progreso':
        return 'blue';
      case 'pendiente':
        return 'yellow';
      case 'fallido':
        return 'red';
      case 'cancelado':
        return 'gray';
      default:
        return 'gray';
    }
  }

  obtenerColorSeveridad(severidad: NivelSeveridad): string {
    switch (severidad) {
      case NivelSeveridad.INFO:
        return 'blue';
      case NivelSeveridad.WARNING:
        return 'yellow';
      case NivelSeveridad.ERROR:
        return 'orange';
      case NivelSeveridad.CRITICAL:
        return 'red';
      default:
        return 'gray';
    }
  }

  obtenerIconoSeveridad(severidad: NivelSeveridad): string {
    switch (severidad) {
      case NivelSeveridad.INFO:
        return '💡';
      case NivelSeveridad.WARNING:
        return '⚠️';
      case NivelSeveridad.ERROR:
        return '❌';
      case NivelSeveridad.CRITICAL:
        return '🚨';
      default:
        return 'ℹ️';
    }
  }

  parsearExpresionCron(cron: string): string {
    // Parsear expresión cron a texto legible
    const partes = cron.split(' ');
    if (partes.length < 5) return cron;

    const [minuto, hora, dia, mes, diaSemana] = partes;

    if (cron === '0 2 * * *') return 'Diario a las 2:00 AM';
    if (cron === '0 0 * * 0') return 'Semanal (Domingos a medianoche)';
    if (cron === '0 0 1 * *') return 'Mensual (Día 1 a medianoche)';
    if (cron === '*/15 * * * *') return 'Cada 15 minutos';
    if (cron === '0 */6 * * *') return 'Cada 6 horas';

    return cron; // Retornar expresión original si no coincide
  }
}

export default new BackupsService();
