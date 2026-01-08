/**
 * Tipos TypeScript para el módulo de Interconsultas
 */

export interface Interconsulta {
  id: string;
  paciente_id: string;
  consulta_id?: string;
  hospitalizacion_id?: string;
  medico_solicitante_id: string;
  especialista_id?: string;
  especialidad_requerida: string;
  motivo_solicitud: string;
  antecedentes_relevantes?: string;
  estudios_adjuntos?: string[];
  urgencia: string;
  estado: string;
  fecha_solicitud: string;
  fecha_aceptacion?: string;
  fecha_programada?: string;
  fecha_realizada?: string;
  fecha_completada?: string;
  diagnostico_especialista?: string;
  hallazgos?: string;
  recomendaciones?: string;
  plan_tratamiento?: string;
  requiere_seguimiento: boolean;
  fecha_seguimiento?: string;
  motivo_rechazo?: string;
  prioridad_clinica: number;
  notas_internas?: string;
  created_at: string;
  updated_at: string;
}

export interface InterconsultaCreate {
  paciente_id: string;
  consulta_id?: string;
  hospitalizacion_id?: string;
  especialista_id?: string;
  especialidad_requerida: string;
  motivo_solicitud: string;
  antecedentes_relevantes?: string;
  estudios_adjuntos?: string[];
  urgencia?: string;
  fecha_programada?: string;
  prioridad_clinica?: number;
}

export interface NotificacionInterconsulta {
  id: string;
  interconsulta_id: string;
  medico_destinatario_id: string;
  tipo: string;
  titulo: string;
  mensaje: string;
  leida: boolean;
  fecha_lectura?: string;
  created_at: string;
}

export interface MensajeInterconsulta {
  id: string;
  interconsulta_id: string;
  medico_emisor_id: string;
  mensaje: string;
  archivos_adjuntos?: string[];
  leido: boolean;
  fecha_lectura?: string;
  created_at: string;
}

export interface MensajeCreate {
  interconsulta_id: string;
  mensaje: string;
  archivos_adjuntos?: string[];
}

export interface SeguimientoInterconsulta {
  id: string;
  interconsulta_id: string;
  medico_id: string;
  tipo_seguimiento: string;
  observaciones: string;
  estado_paciente?: string;
  cambios_tratamiento?: string;
  proxima_revision?: string;
  created_at: string;
  updated_at: string;
}

export interface SeguimientoCreate {
  interconsulta_id: string;
  tipo_seguimiento: string;
  observaciones: string;
  estado_paciente?: string;
  cambios_tratamiento?: string;
  proxima_revision?: string;
}

export interface AceptarInterconsultaRequest {
  fecha_programada?: string;
  notas?: string;
}

export interface RechazarInterconsultaRequest {
  motivo_rechazo: string;
}

export interface ResponderInterconsultaRequest {
  diagnostico_especialista: string;
  hallazgos?: string;
  recomendaciones?: string;
  plan_tratamiento?: string;
  requiere_seguimiento?: boolean;
  fecha_seguimiento?: string;
}

export interface EstadisticasInterconsultas {
  total_solicitadas: number;
  pendientes: number;
  aceptadas: number;
  completadas: number;
  rechazadas: number;
  por_especialidad: Record<string, number>;
  por_urgencia: Record<string, number>;
  tiempo_promedio_respuesta?: number;
}

// Constantes
export const ESPECIALIDADES = [
  'Cardiología',
  'Neurología',
  'Gastroenterología',
  'Neumología',
  'Nefrología',
  'Endocrinología',
  'Hematología',
  'Oncología',
  'Reumatología',
  'Dermatología',
  'Oftalmología',
  'Otorrinolaringología',
  'Urología',
  'Ginecología',
  'Pediatría',
  'Psiquiatría',
  'Traumatología',
  'Cirugía General',
  'Anestesiología',
  'Radiología',
  'Patología',
  'Medicina Interna',
  'Medicina Familiar',
  'Geriatría',
  'Infectología'
];

export const URGENCIAS = {
  normal: { label: 'Normal', color: 'default' },
  urgente: { label: 'Urgente', color: 'warning' },
  emergencia: { label: 'Emergencia', color: 'error' }
};

export const ESTADOS = {
  solicitada: { label: 'Solicitada', color: 'info' },
  aceptada: { label: 'Aceptada', color: 'primary' },
  en_proceso: { label: 'En Proceso', color: 'warning' },
  completada: { label: 'Completada', color: 'success' },
  rechazada: { label: 'Rechazada', color: 'error' },
  cancelada: { label: 'Cancelada', color: 'default' }
};

export const TIPOS_SEGUIMIENTO = [
  'Evolución',
  'Control',
  'Revisión',
  'Ajuste de tratamiento',
  'Evaluación de respuesta'
];
