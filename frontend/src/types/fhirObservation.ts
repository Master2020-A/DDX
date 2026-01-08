// Tipos para FHIR Observation Resource
// Basado en HL7 FHIR R4

export type ObservationStatus = 
  | 'registered'
  | 'preliminary'
  | 'final'
  | 'amended'
  | 'corrected'
  | 'cancelled'
  | 'entered-in-error'
  | 'unknown';

export type ObservationCategory = 
  | 'vital-signs'
  | 'laboratory'
  | 'imaging'
  | 'procedure'
  | 'survey'
  | 'exam'
  | 'therapy'
  | 'activity';

export interface Coding {
  system?: string;
  code: string;
  display?: string;
  version?: string;
}

export interface CodeableConcept {
  coding?: Coding[];
  text?: string;
}

export interface Quantity {
  value: number;
  unit?: string;
  system?: string;
  code?: string;
  comparator?: '<' | '<=' | '>=' | '>';
}

export interface Range {
  low?: Quantity;
  high?: Quantity;
}

export interface Reference {
  reference?: string;
  type?: string;
  display?: string;
}

export interface Period {
  start?: string;
  end?: string;
}

export interface Annotation {
  text: string;
  time?: string;
  authorReference?: Reference;
}

export interface ReferenceRange {
  low?: Quantity;
  high?: Quantity;
  type?: CodeableConcept;
  appliesTo?: CodeableConcept[];
  age?: Range;
  text?: string;
}

export interface ObservationComponent {
  code: CodeableConcept;
  valueQuantity?: Quantity;
  valueCodeableConcept?: CodeableConcept;
  valueString?: string;
  valueBoolean?: boolean;
  valueInteger?: number;
  valueRange?: Range;
  dataAbsentReason?: CodeableConcept;
  interpretation?: CodeableConcept[];
  referenceRange?: ReferenceRange[];
}

export interface FHIRObservation {
  id: string;
  identifier?: any;
  status: ObservationStatus;
  category: ObservationCategory[];
  code: CodeableConcept;
  subject_type: string;
  subject_id: string;
  encounter_id?: string;
  effective_datetime?: string;
  effective_period_start?: string;
  effective_period_end?: string;
  issued?: string;
  performer?: any;
  
  // Valores (solo uno debe estar presente)
  value_quantity?: Quantity;
  value_codeable_concept?: CodeableConcept;
  value_string?: string;
  value_boolean?: boolean;
  value_integer?: number;
  value_range?: Range;
  value_ratio?: any;
  value_sampled_data?: any;
  value_time?: string;
  value_datetime?: string;
  value_period?: Period;
  
  // Interpretación y notas
  interpretation?: CodeableConcept[];
  note?: Annotation[];
  
  // Método y sitio
  method?: CodeableConcept;
  body_site?: CodeableConcept;
  
  // Rango de referencia
  reference_range?: ReferenceRange[];
  
  // Componentes (para observaciones multi-valor)
  component?: ObservationComponent[];
  
  // Metadatos
  meta?: any;
  source_type?: string;
  source_id?: string;
  
  // Auditoría
  created_at: string;
  updated_at: string;
  created_by?: string;
}

export interface ObservationCreate {
  status: ObservationStatus;
  category: ObservationCategory[];
  code: CodeableConcept;
  subject_id: string;
  encounter_id?: string;
  effective_datetime?: string;
  effective_period_start?: string;
  effective_period_end?: string;
  value_quantity?: Quantity;
  value_codeable_concept?: CodeableConcept;
  value_string?: string;
  value_boolean?: boolean;
  value_integer?: number;
  interpretation?: CodeableConcept[];
  note?: Annotation[];
  reference_range?: ReferenceRange[];
  component?: ObservationComponent[];
  source_type?: string;
  source_id?: string;
}

export interface ObservationFromVitalSign {
  nombre_parametro: string;
  valor: number;
  unidad: string;
  paciente_id: string;
  consulta_id?: string;
  fecha: string;
}

export interface ObservationFromBloodPressure {
  sistolica: number;
  diastolica: number;
  paciente_id: string;
  consulta_id?: string;
  fecha: string;
}

export interface ObservationFromLabParameter {
  nombre_parametro: string;
  valor: number;
  unidad: string;
  paciente_id: string;
  prueba_id: string;
  fecha: string;
  interpretacion?: string;
  estado_anormal?: string;
}

export interface ObservationBundle {
  resourceType: 'Bundle';
  type: 'searchset';
  total: number;
  entry: Array<{
    fullUrl: string;
    resource: any;
  }>;
}

export interface ObservationStatistics {
  total: number;
  por_categoria: Record<string, number>;
  por_estado: Record<string, number>;
  ultima_actualizacion: string;
}

export interface ObservationFilters {
  patient?: string;
  category?: ObservationCategory;
  code?: string;
  date?: string;
  status?: ObservationStatus;
  skip?: number;
  limit?: number;
}

// Constantes útiles
export const OBSERVATION_STATUS_LABELS: Record<ObservationStatus, string> = {
  'registered': 'Registrada',
  'preliminary': 'Preliminar',
  'final': 'Final',
  'amended': 'Enmendada',
  'corrected': 'Corregida',
  'cancelled': 'Cancelada',
  'entered-in-error': 'Error de Entrada',
  'unknown': 'Desconocido'
};

export const OBSERVATION_CATEGORY_LABELS: Record<ObservationCategory, string> = {
  'vital-signs': 'Signos Vitales',
  'laboratory': 'Laboratorio',
  'imaging': 'Imagen',
  'procedure': 'Procedimiento',
  'survey': 'Encuesta',
  'exam': 'Examen',
  'therapy': 'Terapia',
  'activity': 'Actividad'
};

export const INTERPRETATION_CODES: Record<string, { label: string; color: string }> = {
  'N': { label: 'Normal', color: 'green' },
  'L': { label: 'Bajo', color: 'blue' },
  'H': { label: 'Alto', color: 'orange' },
  'LL': { label: 'Muy Bajo', color: 'red' },
  'HH': { label: 'Muy Alto', color: 'red' },
  'AA': { label: 'Crítico Anormal', color: 'red' },
  '<': { label: 'Por Debajo', color: 'blue' },
  '>': { label: 'Por Encima', color: 'orange' },
  'A': { label: 'Anormal', color: 'yellow' }
};

export const LOINC_COMMON_CODES: Record<string, string> = {
  '8867-4': 'Frecuencia Cardíaca',
  '9279-1': 'Frecuencia Respiratoria',
  '8310-5': 'Temperatura Corporal',
  '2708-6': 'Saturación de Oxígeno',
  '8480-6': 'Presión Arterial Sistólica',
  '8462-4': 'Presión Arterial Diastólica',
  '85354-9': 'Panel de Presión Arterial',
  '29463-7': 'Peso Corporal',
  '8302-2': 'Altura Corporal',
  '39156-5': 'Índice de Masa Corporal',
  '718-7': 'Hemoglobina',
  '4544-3': 'Hematocrito',
  '6690-2': 'Leucocitos',
  '777-3': 'Plaquetas',
  '2345-7': 'Glucosa',
  '2160-0': 'Creatinina',
  '3094-0': 'Urea',
  '2093-3': 'Colesterol Total',
  '2571-8': 'Triglicéridos',
  '2085-9': 'Colesterol HDL',
  '2089-1': 'Colesterol LDL'
};
