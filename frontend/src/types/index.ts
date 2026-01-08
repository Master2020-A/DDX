export interface Usuario {
  id: string
  email: string
  nombre_completo: string
  rol: 'medico' | 'enfermero' | 'administrativo' | 'especialista' | 'admin'
  especialidad?: string
  cedula_profesional?: string
  activo: boolean
  created_at: string
  updated_at: string
}

export interface Paciente {
  id: string
  numero_expediente: string
  nombre_completo: string
  fecha_nacimiento: string
  genero?: 'masculino' | 'femenino' | 'otro' | 'no_especifica'
  tipo_sangre?: string
  telefono?: string
  email?: string
  direccion?: string
  contacto_emergencia_nombre?: string
  contacto_emergencia_telefono?: string
  alergias?: string[]
  created_at: string
  updated_at: string
}

export interface Consulta {
  id: string
  paciente_id: string
  medico_id: string
  fecha_hora: string
  tipo_consulta: 'primera_vez' | 'seguimiento' | 'urgencia' | 'interconsulta'
  motivo_consulta: string
  sintomas: string[]
  estado: 'en_proceso' | 'completada' | 'hospitalizado' | 'alta'
  created_at: string
  updated_at: string
}

export interface Diagnostico {
  id: string
  consulta_id: string
  medico_id: string
  tipo: 'pre_diagnostico' | 'diagnostico_presuntivo' | 'diagnostico_confirmado' | 'diagnostico_diferencial'
  codigo_cie10?: string
  descripcion: string
  confianza_nivel?: 'bajo' | 'medio' | 'alto' | 'confirmado'
  justificacion?: string
  evidencias?: string[]
  estado: 'activo' | 'descartado' | 'confirmado'
  created_at: string
  updated_at: string
}

export interface PruebaMedica {
  id: string
  consulta_id: string
  diagnostico_id?: string
  tipo_prueba: 'laboratorio' | 'imagen' | 'biopsia' | 'electrocardiograma' | 'otro'
  nombre_prueba: string
  descripcion?: string
  urgencia: 'normal' | 'urgente' | 'emergencia'
  estado: 'solicitada' | 'en_proceso' | 'completada' | 'cancelada'
  fecha_solicitud: string
  fecha_programada?: string
  fecha_realizada?: string
  solicitado_por: string
  laboratorio_externo?: string
  created_at: string
  updated_at: string
}

export interface Tratamiento {
  id: string
  consulta_id: string
  diagnostico_id?: string
  tipo_tratamiento: 'farmacologico' | 'fisico' | 'paliativo' | 'quirurgico' | 'psicologico' | 'otro'
  descripcion: string
  objetivo?: string
  duracion_dias?: number
  fecha_inicio?: string
  fecha_fin?: string
  estado: 'activo' | 'completado' | 'suspendido' | 'modificado'
  prescrito_por: string
  notas?: string
  created_at: string
  updated_at: string
}
