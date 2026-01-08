/**
 * Tipos para el sistema de laboratorio clínico
 */

export interface ResultadoLaboratorio {
  parametro: string;
  valor: number;
}

export interface ValorAnormal {
  parametro: string;
  valor: number;
  unidad: string;
  rango_min: number | null;
  rango_max: number | null;
  estado: 'bajo' | 'alto' | 'critico_bajo' | 'critico_alto' | 'normal';
  critico: boolean;
  interpretacion: string;
}

export interface PruebaLaboratorio {
  id: string;
  paciente_id: string;
  consulta_id?: string;
  medico_id: string;
  area: string;
  tipo_prueba: string;
  resultados: Record<string, number>;
  interpretacion: string;
  valores_anormales: ValorAnormal[];
  valores_criticos: ValorAnormal[];
  estado: 'pendiente' | 'completado' | 'validado';
  requiere_atencion: boolean;
  laboratorio_externo?: string;
  numero_orden?: string;
  fecha_solicitud: string;
  fecha_resultado?: string;
  notas_medico?: string;
  created_at: string;
  updated_at: string;
}

export interface PruebaLaboratorioResumen {
  id: string;
  area: string;
  tipo_prueba: string;
  fecha_resultado?: string;
  estado: string;
  requiere_atencion: boolean;
  valores_criticos_count: number;
  valores_anormales_count: number;
  laboratorio_externo?: string;
  numero_orden?: string;
}

export interface RangoReferencia {
  parametro: string;
  area?: string;
  tipo_prueba: string;
  nombre_completo?: string;
  sexo?: string;
  grupo_etario?: string;
  edad_min?: number;
  edad_max?: number;
  valor_min?: number;
  valor_max?: number;
  critico_bajo?: number;
  critico_alto?: number;
  unidad?: string;
  descripcion?: string;
  interpretacion_bajo?: string;
  interpretacion_alto?: string;
}

export interface CrearPruebaLaboratorio {
  paciente_id: string;
  consulta_id?: string;
  area: string;
  tipo_prueba: string;
  resultados: ResultadoLaboratorio[];
  laboratorio_externo?: string;
  numero_orden?: string;
  fecha_resultado?: string;
  notas_medico?: string;
}

// Áreas de laboratorio
export const AREAS_LABORATORIO = [
  { value: 'hematologia', label: 'Hematología' },
  { value: 'quimica_clinica', label: 'Química Clínica' },
  { value: 'bacteriologia', label: 'Bacteriología' },
  { value: 'inmunologia', label: 'Inmunología' },
  { value: 'parasitologia', label: 'Parasitología' },
  { value: 'urinalisis', label: 'Examen General de Orina' }
] as const;

// Tipos de pruebas por área
export const TIPOS_PRUEBAS: Record<string, Array<{ value: string; label: string; parametros: string[] }>> = {
  hematologia: [
    {
      value: 'biometria_hematica',
      label: 'Biometría Hemática Completa',
      parametros: [
        'hemoglobina',
        'hematocrito',
        'eritrocitos',
        'leucocitos',
        'plaquetas',
        'neutrofilos',
        'linfocitos',
        'monocitos',
        'eosinofilos',
        'basofilos'
      ]
    },
    {
      value: 'vsg',
      label: 'Velocidad de Sedimentación Globular',
      parametros: ['vsg']
    }
  ],
  quimica_clinica: [
    {
      value: 'glucosa',
      label: 'Glucosa en Ayunas',
      parametros: ['glucosa']
    },
    {
      value: 'funcion_renal',
      label: 'Función Renal',
      parametros: ['creatinina', 'urea', 'acido_urico']
    },
    {
      value: 'perfil_lipidico',
      label: 'Perfil Lipídico',
      parametros: ['colesterol_total', 'trigliceridos', 'hdl', 'ldl']
    },
    {
      value: 'funcion_hepatica',
      label: 'Función Hepática',
      parametros: ['tgo', 'tgp', 'bilirrubina_total', 'fosfatasa_alcalina', 'albumina', 'proteinas_totales']
    }
  ],
  inmunologia: [
    {
      value: 'marcadores_inflamatorios',
      label: 'Marcadores Inflamatorios',
      parametros: ['proteina_c_reactiva']
    }
  ]
};

// Labels amigables para parámetros
export const PARAMETROS_LABELS: Record<string, string> = {
  hemoglobina: 'Hemoglobina',
  hematocrito: 'Hematocrito',
  eritrocitos: 'Eritrocitos',
  leucocitos: 'Leucocitos',
  plaquetas: 'Plaquetas',
  neutrofilos: 'Neutrófilos',
  linfocitos: 'Linfocitos',
  monocitos: 'Monocitos',
  eosinofilos: 'Eosinófilos',
  basofilos: 'Basófilos',
  vsg: 'VSG',
  glucosa: 'Glucosa',
  creatinina: 'Creatinina',
  urea: 'Urea',
  acido_urico: 'Ácido Úrico',
  colesterol_total: 'Colesterol Total',
  trigliceridos: 'Triglicéridos',
  hdl: 'HDL (Colesterol Bueno)',
  ldl: 'LDL (Colesterol Malo)',
  tgo: 'TGO (AST)',
  tgp: 'TGP (ALT)',
  bilirrubina_total: 'Bilirrubina Total',
  fosfatasa_alcalina: 'Fosfatasa Alcalina',
  albumina: 'Albúmina',
  proteinas_totales: 'Proteínas Totales',
  proteina_c_reactiva: 'Proteína C Reactiva (PCR)'
};
