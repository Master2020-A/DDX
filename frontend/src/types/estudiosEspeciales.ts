/**
 * Tipos para Estudios Especiales: EKG, EEG, Ecografías
 */

// ==================== TIPOS BASE ====================

export interface InterpretacionIA {
  interpretacion: string;
  confianza: number;
  hallazgos: string[];
  alteraciones?: string[];
  categorias_detectadas?: string[];
  estructuras_identificadas?: string[];
  clasificacion: 'normal' | 'anormal_leve' | 'anormal_moderado' | 'anormal_severo' | 'hallazgos_benignos' | 'sospechoso' | 'patologico';
  requiere_atencion: boolean;
  es_critico?: boolean;
  requiere_seguimiento?: boolean;
  recomendaciones: string;
}

// ==================== EKG ====================

export interface EstudioEKG {
  id: string;
  paciente_id: string;
  consulta_id?: string;
  medico_id: string;
  
  // Información del estudio
  fecha_estudio: string;
  motivo?: string;
  indicacion_clinica?: string;
  
  // Datos del paciente
  edad_paciente?: number;
  peso_kg?: number;
  altura_cm?: number;
  presion_arterial?: string;
  
  // Parámetros medidos
  frecuencia_cardiaca?: number;
  intervalo_pr?: number;
  duracion_qrs?: number;
  intervalo_qt?: number;
  intervalo_qtc?: number;
  eje_qrs?: number;
  
  // Ritmo
  ritmo?: string;
  ritmo_regular?: boolean;
  
  // Ondas y segmentos
  onda_p?: string;
  complejo_qrs?: string;
  segmento_st?: string;
  onda_t?: string;
  onda_u?: string;
  
  // Interpretación
  interpretacion_ia?: string;
  confianza_ia?: number;
  hallazgos?: string[];
  alteraciones?: string[];
  categorias_detectadas?: string[];
  interpretacion_medica?: string;
  recomendaciones?: string;
  clasificacion?: string;
  requiere_atencion?: boolean;
  es_critico?: boolean;
  
  // Archivos
  archivo_ekg?: string;
  
  // Metadata
  estado: 'pendiente' | 'en_proceso' | 'interpretado' | 'revisado';
  notas?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CrearEstudioEKG {
  paciente_id: string;
  consulta_id?: string;
  fecha_estudio: string;
  motivo?: string;
  indicacion_clinica?: string;
  edad_paciente?: number;
  peso_kg?: number;
  altura_cm?: number;
  presion_arterial?: string;
  frecuencia_cardiaca?: number;
  intervalo_pr?: number;
  duracion_qrs?: number;
  intervalo_qt?: number;
  intervalo_qtc?: number;
  eje_qrs?: number;
  ritmo?: string;
  ritmo_regular?: boolean;
  onda_p?: string;
  complejo_qrs?: string;
  segmento_st?: string;
  onda_t?: string;
  onda_u?: string;
}

// ==================== EEG ====================

export interface EstudioEEG {
  id: string;
  paciente_id: string;
  consulta_id?: string;
  medico_id: string;
  
  // Información del estudio
  fecha_estudio: string;
  motivo?: string;
  indicacion_clinica?: string;
  
  // Datos del paciente
  edad_paciente?: number;
  medicamentos_actuales?: string;
  horas_ayuno?: number;
  horas_sueno_previo?: number;
  
  // Tipo de estudio
  tipo_estudio: 'basal' | 'sueno' | 'vigilia' | 'prolongado';
  duracion_minutos?: number;
  
  // Condiciones del estudio
  estado_conciencia?: string;
  cooperacion_paciente?: string;
  artefactos?: string[];
  
  // Actividad de fondo
  actividad_fondo?: string;
  frecuencia_dominante?: number;
  amplitud_promedio?: number;
  simetria?: string;
  reactividad?: string;
  
  // Ritmos cerebrales
  ritmo_alfa?: string;
  ritmo_beta?: string;
  ritmo_theta?: string;
  ritmo_delta?: string;
  
  // Hallazgos anormales
  ondas_agudas?: boolean;
  espigas?: boolean;
  complejos_punta_onda?: boolean;
  actividad_paroxistica?: boolean;
  enlentecimiento?: string;
  
  // Localización
  localizacion_hallazgos?: string[];
  lateralidad?: string;
  
  // Pruebas de activación
  fotoestimulacion?: string;
  hiperventilacion?: string;
  privacion_sueno?: string;
  
  // Interpretación
  interpretacion_ia?: string;
  confianza_ia?: number;
  hallazgos?: string[];
  alteraciones?: string[];
  categorias_detectadas?: string[];
  interpretacion_medica?: string;
  recomendaciones?: string;
  clasificacion?: string;
  requiere_atencion?: boolean;
  es_critico?: boolean;
  
  // Archivos
  archivo_eeg?: string;
  
  // Metadata
  estado: 'pendiente' | 'en_proceso' | 'interpretado' | 'revisado';
  notas?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CrearEstudioEEG {
  paciente_id: string;
  consulta_id?: string;
  fecha_estudio: string;
  motivo?: string;
  indicacion_clinica?: string;
  edad_paciente?: number;
  medicamentos_actuales?: string;
  horas_ayuno?: number;
  horas_sueno_previo?: number;
  tipo_estudio: 'basal' | 'sueno' | 'vigilia' | 'prolongado';
  duracion_minutos?: number;
  estado_conciencia?: string;
  cooperacion_paciente?: string;
  artefactos?: string[];
  actividad_fondo?: string;
  frecuencia_dominante?: number;
  amplitud_promedio?: number;
  simetria?: string;
  reactividad?: string;
  ritmo_alfa?: string;
  ritmo_beta?: string;
  ritmo_theta?: string;
  ritmo_delta?: string;
  ondas_agudas?: boolean;
  espigas?: boolean;
  complejos_punta_onda?: boolean;
  actividad_paroxistica?: boolean;
  enlentecimiento?: string;
  localizacion_hallazgos?: string[];
  lateralidad?: string;
  fotoestimulacion?: string;
  hiperventilacion?: string;
  privacion_sueno?: string;
}

// ==================== ECOGRAFÍA ====================

export interface Ecografia {
  id: string;
  paciente_id: string;
  consulta_id?: string;
  medico_id: string;
  
  // Información del estudio
  fecha_estudio: string;
  motivo?: string;
  indicacion_clinica?: string;
  
  // Tipo de ecografía
  tipo_ecografia: string;
  region_anatomica: string;
  via_acceso?: string;
  
  // Datos obstétricos
  es_obstetrica?: boolean;
  edad_gestacional_semanas?: number;
  numero_fetos?: number;
  
  // Equipo
  equipo_utilizado?: string;
  transductor?: string;
  modo?: string;
  
  // Mediciones
  mediciones?: Array<{
    parametro: string;
    valor: number;
    unidad: string;
  }>;
  
  // Hallazgos
  hallazgos_organos?: Record<string, string>;
  masas_detectadas?: Array<{
    ubicacion: string;
    tamano_cm: number;
    caracteristicas: string;
  }>;
  liquido_libre?: boolean;
  cantidad_liquido?: string;
  
  // Doppler
  estudio_doppler?: boolean;
  flujo_vascular?: string;
  resistencia_vascular?: string;
  
  // Calidad
  calidad_estudio?: string;
  limitaciones?: string;
  
  // BI-RADS (mamarias)
  birads?: string;
  
  // Interpretación
  interpretacion_ia?: string;
  confianza_ia?: number;
  hallazgos?: string[];
  categorias_detectadas?: string[];
  estructuras_identificadas?: string[];
  interpretacion_medica?: string;
  recomendaciones?: string;
  clasificacion?: string;
  requiere_atencion?: boolean;
  requiere_seguimiento?: boolean;
  
  // Archivos
  imagenes?: string[];
  
  // Metadata
  estado: 'pendiente' | 'en_proceso' | 'interpretado' | 'revisado';
  notas?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CrearEcografia {
  paciente_id: string;
  consulta_id?: string;
  fecha_estudio: string;
  motivo?: string;
  indicacion_clinica?: string;
  tipo_ecografia: string;
  region_anatomica: string;
  via_acceso?: string;
  es_obstetrica?: boolean;
  edad_gestacional_semanas?: number;
  numero_fetos?: number;
  equipo_utilizado?: string;
  transductor?: string;
  modo?: string;
  mediciones?: Array<{
    parametro: string;
    valor: number;
    unidad: string;
  }>;
  hallazgos_organos?: Record<string, string>;
  masas_detectadas?: Array<{
    ubicacion: string;
    tamano_cm: number;
    caracteristicas: string;
  }>;
  liquido_libre?: boolean;
  cantidad_liquido?: string;
  estudio_doppler?: boolean;
  flujo_vascular?: string;
  resistencia_vascular?: string;
  calidad_estudio?: string;
  limitaciones?: string;
  birads?: string;
}

// ==================== RESUMEN ====================

export interface ResumenEstudiosEspeciales {
  paciente_id: string;
  ekg: {
    total: number;
    criticos: number;
    requieren_atencion: number;
    estudios: EstudioEKG[];
  };
  eeg: {
    total: number;
    criticos: number;
    requieren_atencion: number;
    estudios: EstudioEEG[];
  };
  ecografias: {
    total: number;
    requieren_atencion: number;
    requieren_seguimiento: number;
    estudios: Ecografia[];
  };
}

// ==================== CONSTANTES ====================

export const TIPOS_ECOGRAFIA = [
  'abdominal',
  'pelvica',
  'obstetrica',
  'cardiaca',
  'renal',
  'hepatica',
  'vesicula_biliar',
  'tiroides',
  'mamaria',
  'escrotal',
  'musculoesqueletica',
  'vascular'
] as const;

export const TIPOS_ESTUDIO_EEG = [
  'basal',
  'sueno',
  'vigilia',
  'prolongado'
] as const;

export const ESTADOS_ESTUDIO = [
  'pendiente',
  'en_proceso',
  'interpretado',
  'revisado'
] as const;

export const CLASIFICACIONES = {
  normal: { label: 'Normal', color: 'success' },
  anormal_leve: { label: 'Anormal Leve', color: 'warning' },
  anormal_moderado: { label: 'Anormal Moderado', color: 'warning' },
  anormal_severo: { label: 'Anormal Severo', color: 'error' },
  hallazgos_benignos: { label: 'Hallazgos Benignos', color: 'info' },
  sospechoso: { label: 'Sospechoso', color: 'warning' },
  patologico: { label: 'Patológico', color: 'error' }
} as const;
