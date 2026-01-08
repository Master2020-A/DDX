/**
 * Tipos TypeScript para el módulo de Hospitalización
 */

export interface Hospitalizacion {
  id: string;
  paciente_id: string;
  consulta_id?: string;
  medico_responsable_id: string;
  fecha_ingreso: string;
  fecha_alta?: string;
  motivo_ingreso: string;
  diagnostico_ingreso: string;
  diagnostico_egreso?: string;
  resumen_clinico?: string;
  area_hospitalizacion?: string;
  numero_cama?: string;
  piso?: string;
  estado: string;
  prioridad: string;
  tipo_ingreso?: string;
  alergias_conocidas?: string[];
  antecedentes_relevantes?: string;
  tratamiento_actual?: string;
  tipo_seguro?: string;
  numero_poliza?: string;
  created_at: string;
  updated_at: string;
}

export interface HospitalizacionCreate {
  paciente_id: string;
  consulta_id?: string;
  motivo_ingreso: string;
  diagnostico_ingreso: string;
  area_hospitalizacion?: string;
  numero_cama?: string;
  piso?: string;
  prioridad?: string;
  tipo_ingreso?: string;
  alergias_conocidas?: string[];
  antecedentes_relevantes?: string;
  tratamiento_actual?: string;
  tipo_seguro?: string;
  numero_poliza?: string;
}

export interface HospitalizacionUpdate {
  motivo_ingreso?: string;
  diagnostico_ingreso?: string;
  diagnostico_egreso?: string;
  resumen_clinico?: string;
  area_hospitalizacion?: string;
  numero_cama?: string;
  piso?: string;
  estado?: string;
  prioridad?: string;
  alergias_conocidas?: string[];
  antecedentes_relevantes?: string;
  tratamiento_actual?: string;
}

export interface Cama {
  id: string;
  numero_cama: string;
  area: string;
  piso?: string;
  habitacion?: string;
  estado: string;
  tipo_cama?: string;
  tiene_oxigeno: boolean;
  tiene_monitor: boolean;
  tiene_ventilador: boolean;
  capacidad_peso?: number;
  hospitalizacion_actual_id?: string;
  fecha_ultima_limpieza?: string;
  fecha_ultimo_mantenimiento?: string;
  observaciones?: string;
  created_at: string;
  updated_at: string;
}

export interface CamaCreate {
  numero_cama: string;
  area: string;
  piso?: string;
  habitacion?: string;
  tipo_cama?: string;
  tiene_oxigeno?: boolean;
  tiene_monitor?: boolean;
  tiene_ventilador?: boolean;
  capacidad_peso?: number;
  observaciones?: string;
}

export interface CamaUpdate {
  numero_cama?: string;
  area?: string;
  piso?: string;
  habitacion?: string;
  estado?: string;
  tipo_cama?: string;
  tiene_oxigeno?: boolean;
  tiene_monitor?: boolean;
  tiene_ventilador?: boolean;
  capacidad_peso?: number;
  observaciones?: string;
}

export interface NotaEvolucion {
  id: string;
  hospitalizacion_id: string;
  medico_id: string;
  fecha_nota: string;
  tipo_nota: string;
  turno?: string;
  subjetivo?: string;
  objetivo?: string;
  temperatura?: number;
  presion_arterial_sistolica?: number;
  presion_arterial_diastolica?: number;
  frecuencia_cardiaca?: number;
  frecuencia_respiratoria?: number;
  saturacion_oxigeno?: number;
  evaluacion?: string;
  plan?: string;
  estudios_solicitados?: string[];
  procedimientos_realizados?: string[];
  estado_general?: string;
  nivel_conciencia?: string;
  observaciones?: string;
  created_at: string;
  updated_at: string;
}

export interface NotaEvolucionCreate {
  hospitalizacion_id: string;
  tipo_nota?: string;
  turno?: string;
  subjetivo?: string;
  objetivo?: string;
  temperatura?: number;
  presion_arterial_sistolica?: number;
  presion_arterial_diastolica?: number;
  frecuencia_cardiaca?: number;
  frecuencia_respiratoria?: number;
  saturacion_oxigeno?: number;
  evaluacion?: string;
  plan?: string;
  estudios_solicitados?: string[];
  procedimientos_realizados?: string[];
  estado_general?: string;
  nivel_conciencia?: string;
  observaciones?: string;
}

export interface IndicacionMedica {
  id: string;
  hospitalizacion_id: string;
  medico_id: string;
  fecha_indicacion: string;
  tipo_indicacion: string;
  descripcion: string;
  dosis?: string;
  via_administracion?: string;
  frecuencia?: string;
  duracion?: string;
  prioridad: string;
  estado: string;
  fecha_inicio?: string;
  fecha_fin?: string;
  fecha_suspension?: string;
  motivo_suspension?: string;
  observaciones?: string;
  created_at: string;
  updated_at: string;
}

export interface IndicacionMedicaCreate {
  hospitalizacion_id: string;
  tipo_indicacion: string;
  descripcion: string;
  dosis?: string;
  via_administracion?: string;
  frecuencia?: string;
  duracion?: string;
  prioridad?: string;
  fecha_inicio?: string;
  fecha_fin?: string;
  observaciones?: string;
}

export interface NotaAlta {
  id: string;
  hospitalizacion_id: string;
  medico_id: string;
  fecha_alta: string;
  tipo_alta: string;
  motivo_ingreso: string;
  resumen_evolucion: string;
  diagnostico_egreso: string;
  procedimientos_realizados?: string;
  complicaciones?: string;
  condicion_egreso?: string;
  estado_funcional?: string;
  medicamentos_egreso?: string;
  dieta_recomendada?: string;
  cuidados_domiciliarios?: string;
  restricciones?: string;
  fecha_control?: string;
  especialidad_control?: string;
  estudios_pendientes?: string[];
  pronostico?: string;
  observaciones?: string;
  created_at: string;
  updated_at: string;
}

export interface NotaAltaCreate {
  hospitalizacion_id: string;
  tipo_alta: string;
  motivo_ingreso: string;
  resumen_evolucion: string;
  diagnostico_egreso: string;
  procedimientos_realizados?: string;
  complicaciones?: string;
  condicion_egreso?: string;
  estado_funcional?: string;
  medicamentos_egreso?: string;
  dieta_recomendada?: string;
  cuidados_domiciliarios?: string;
  restricciones?: string;
  fecha_control?: string;
  especialidad_control?: string;
  estudios_pendientes?: string[];
  pronostico?: string;
  observaciones?: string;
}

export interface CensoHospitalario {
  total_hospitalizados: number;
  por_area: Record<string, number>;
  por_estado: Record<string, number>;
  camas_disponibles: number;
  camas_ocupadas: number;
  camas_totales: number;
  porcentaje_ocupacion: number;
  hospitalizaciones_recientes: Hospitalizacion[];
}
