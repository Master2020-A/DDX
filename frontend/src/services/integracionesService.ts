/**
 * Servicio para el módulo de Integraciones
 */
import api from './api';

// ============================================================================
// Tipos e Interfaces
// ============================================================================

export interface ConfiguracionIntegracion {
  id: string;
  nombre: string;
  tipo_sistema: 'PACS' | 'LIS' | 'RECETA' | 'FARMACIA' | 'CFDI' | 'ERP';
  descripcion?: string;
  url_base?: string;
  puerto?: number;
  protocolo?: string;
  tipo_auth?: string;
  usuario?: string;
  configuracion_adicional?: any;
  webhook_url?: string;
  timeout_segundos: number;
  max_reintentos: number;
  intervalo_reintento_segundos: number;
  activo: boolean;
  log_requests: boolean;
  log_responses: boolean;
  fecha_ultima_sincronizacion?: string;
  created_at: string;
  updated_at: string;
}

export interface MedicamentoReceta {
  nombre_generico: string;
  nombre_comercial?: string;
  presentacion: string;
  dosis: string;
  frecuencia: string;
  via: string;
  duracion_dias: number;
  cantidad: number;
  indicaciones?: string;
}

export interface RecetaElectronica {
  id: string;
  folio: string;
  codigo_verificacion: string;
  paciente_id: string;
  medico_id: string;
  consulta_id?: string;
  fecha_emision: string;
  fecha_vencimiento?: string;
  diagnostico_cie10?: string;
  medicamentos: MedicamentoReceta[];
  estado: 'ACTIVA' | 'SURTIDA' | 'PARCIAL' | 'VENCIDA' | 'CANCELADA';
  fecha_surtido?: string;
  farmacia_id?: string;
  created_at: string;
}

export interface MedicamentoSolicitud {
  codigo: string;
  nombre: string;
  cantidad: number;
  urgente: boolean;
}

export interface SolicitudFarmacia {
  id: string;
  folio: string;
  paciente_id: string;
  medico_id?: string;
  receta_id?: string;
  fecha_solicitud: string;
  urgente: boolean;
  destino: string;
  ubicacion?: string;
  medicamentos_solicitados: MedicamentoSolicitud[];
  estado: 'PENDIENTE' | 'PROCESANDO' | 'DISPENSADO' | 'CANCELADO';
  fecha_dispensacion?: string;
  farmaceutico_id?: string;
  medicamentos_dispensados?: any[];
  costo_total?: number;
  verificado: boolean;
  notas?: string;
  created_at: string;
}

export interface FacturaElectronica {
  id: string;
  uuid_sat?: string;
  serie?: string;
  folio: string;
  paciente_id?: string;
  tipo_comprobante: string;
  uso_cfdi: string;
  metodo_pago: string;
  forma_pago?: string;
  receptor_rfc: string;
  receptor_nombre: string;
  receptor_cp: string;
  conceptos: any[];
  subtotal: number;
  descuento?: number;
  total: number;
  fecha_emision: string;
  fecha_timbrado?: string;
  estado: 'PENDIENTE' | 'TIMBRADA' | 'CANCELADA';
  pac_proveedor?: string;
  created_at: string;
}

export interface EstadisticasIntegracion {
  activo: boolean;
  operaciones_hoy: number;
  operaciones_exitosas_hoy: number;
  operaciones_fallidas_hoy: number;
  operaciones_pendientes: number;
  ultima_sincronizacion?: string;
  tasa_exito: number;
}

export interface DashboardIntegraciones {
  pacs?: EstadisticasIntegracion;
  lis?: EstadisticasIntegracion;
  receta_electronica?: EstadisticasIntegracion;
  farmacia?: EstadisticasIntegracion;
  facturacion?: EstadisticasIntegracion;
  erp?: EstadisticasIntegracion;
}

export interface LogIntegracion {
  id: string;
  configuracion_id?: string;
  operacion: string;
  direccion: 'SALIDA' | 'ENTRADA';
  tipo_sistema: string;
  url?: string;
  metodo?: string;
  response_status?: number;
  duracion_ms?: number;
  exitoso: boolean;
  mensaje_error?: string;
  fecha_hora: string;
  created_at: string;
}

// ============================================================================
// Configuración General
// ============================================================================

export const listarConfiguraciones = async (
  tipo_sistema?: string,
  activo?: boolean
): Promise<ConfiguracionIntegracion[]> => {
  const params = new URLSearchParams();
  if (tipo_sistema) params.append('tipo_sistema', tipo_sistema);
  if (activo !== undefined) params.append('activo', activo.toString());
  
  const response = await api.get(`/integraciones/configuraciones?${params}`);
  return response.data;
};

export const crearConfiguracion = async (
  data: Partial<ConfiguracionIntegracion>
): Promise<ConfiguracionIntegracion> => {
  const response = await api.post('/integraciones/configuraciones', data);
  return response.data;
};

export const obtenerConfiguracion = async (
  id: string
): Promise<ConfiguracionIntegracion> => {
  const response = await api.get(`/integraciones/configuraciones/${id}`);
  return response.data;
};

export const actualizarConfiguracion = async (
  id: string,
  data: Partial<ConfiguracionIntegracion>
): Promise<ConfiguracionIntegracion> => {
  const response = await api.put(`/integraciones/configuraciones/${id}`, data);
  return response.data;
};

export const eliminarConfiguracion = async (id: string): Promise<void> => {
  await api.delete(`/integraciones/configuraciones/${id}`);
};

// ============================================================================
// Receta Electrónica
// ============================================================================

export const generarRecetaElectronica = async (data: {
  paciente_id: string;
  medico_id: string;
  consulta_id?: string;
  diagnostico_cie10?: string;
  medicamentos: MedicamentoReceta[];
  vigencia_dias?: number;
}): Promise<RecetaElectronica> => {
  const response = await api.post('/integraciones/receta-electronica', data);
  return response.data;
};

export const validarRecetaElectronica = async (
  folio_receta: string,
  codigo_verificacion: string
): Promise<any> => {
  const response = await api.post('/integraciones/receta-electronica/validar', {
    folio_receta,
    codigo_verificacion
  });
  return response.data;
};

export const surtirRecetaElectronica = async (data: {
  folio_receta: string;
  farmacia_id: string;
  fecha_surtido: string;
  medicamentos_surtidos: any[];
}): Promise<void> => {
  await api.post('/integraciones/receta-electronica/surtir', data);
};

export const listarRecetas = async (
  paciente_id?: string,
  medico_id?: string,
  estado?: string,
  skip: number = 0,
  limit: number = 50
): Promise<RecetaElectronica[]> => {
  const params = new URLSearchParams();
  if (paciente_id) params.append('paciente_id', paciente_id);
  if (medico_id) params.append('medico_id', medico_id);
  if (estado) params.append('estado', estado);
  params.append('skip', skip.toString());
  params.append('limit', limit.toString());
  
  const response = await api.get(`/integraciones/receta-electronica?${params}`);
  return response.data;
};

// ============================================================================
// Farmacia
// ============================================================================

export const crearSolicitudFarmacia = async (data: {
  paciente_id: string;
  medico_id?: string;
  receta_id?: string;
  medicamentos_solicitados: MedicamentoSolicitud[];
  urgente?: boolean;
  destino: string;
  ubicacion?: string;
  notas?: string;
}): Promise<SolicitudFarmacia> => {
  const response = await api.post('/integraciones/farmacia/solicitud', data);
  return response.data;
};

export const dispensarMedicamentos = async (data: {
  solicitud_id: string;
  farmaceutico_id: string;
  medicamentos_dispensados: any[];
  costo_total: number;
  verificado_por?: string;
}): Promise<void> => {
  await api.post('/integraciones/farmacia/dispensar', data);
};

export const listarSolicitudesFarmacia = async (
  estado?: string,
  urgente?: boolean,
  skip: number = 0,
  limit: number = 50
): Promise<SolicitudFarmacia[]> => {
  const params = new URLSearchParams();
  if (estado) params.append('estado', estado);
  if (urgente !== undefined) params.append('urgente', urgente.toString());
  params.append('skip', skip.toString());
  params.append('limit', limit.toString());
  
  const response = await api.get(`/integraciones/farmacia/solicitudes?${params}`);
  return response.data;
};

export const consultarDisponibilidad = async (
  medicamento: string,
  cantidad_requerida: number
): Promise<any> => {
  const response = await api.post('/integraciones/farmacia/disponibilidad', {
    medicamento,
    cantidad_requerida
  });
  return response.data;
};

// ============================================================================
// Facturación Electrónica
// ============================================================================

export const generarFactura = async (data: any): Promise<FacturaElectronica> => {
  const response = await api.post('/integraciones/facturacion/generar', data);
  return response.data;
};

export const timbrarFactura = async (
  factura_id: string,
  pac_proveedor: string = 'FINKOK'
): Promise<any> => {
  const response = await api.post('/integraciones/facturacion/timbrar', {
    factura_id,
    pac_proveedor
  });
  return response.data;
};

export const listarFacturas = async (
  paciente_id?: string,
  estado?: string,
  skip: number = 0,
  limit: number = 50
): Promise<FacturaElectronica[]> => {
  const params = new URLSearchParams();
  if (paciente_id) params.append('paciente_id', paciente_id);
  if (estado) params.append('estado', estado);
  params.append('skip', skip.toString());
  params.append('limit', limit.toString());
  
  const response = await api.get(`/integraciones/facturacion?${params}`);
  return response.data;
};

// ============================================================================
// Dashboard
// ============================================================================

export const obtenerDashboard = async (): Promise<DashboardIntegraciones> => {
  const response = await api.get('/integraciones/dashboard');
  return response.data;
};

// ============================================================================
// Logs
// ============================================================================

export const listarLogs = async (
  tipo_sistema?: string,
  exitoso?: boolean,
  fecha_desde?: string,
  fecha_hasta?: string,
  skip: number = 0,
  limit: number = 100
): Promise<LogIntegracion[]> => {
  const params = new URLSearchParams();
  if (tipo_sistema) params.append('tipo_sistema', tipo_sistema);
  if (exitoso !== undefined) params.append('exitoso', exitoso.toString());
  if (fecha_desde) params.append('fecha_desde', fecha_desde);
  if (fecha_hasta) params.append('fecha_hasta', fecha_hasta);
  params.append('skip', skip.toString());
  params.append('limit', limit.toString());
  
  const response = await api.get(`/integraciones/logs?${params}`);
  return response.data;
};

export default {
  // Configuración
  listarConfiguraciones,
  crearConfiguracion,
  obtenerConfiguracion,
  actualizarConfiguracion,
  eliminarConfiguracion,
  
  // Receta Electrónica
  generarRecetaElectronica,
  validarRecetaElectronica,
  surtirRecetaElectronica,
  listarRecetas,
  
  // Farmacia
  crearSolicitudFarmacia,
  dispensarMedicamentos,
  listarSolicitudesFarmacia,
  consultarDisponibilidad,
  
  // Facturación
  generarFactura,
  timbrarFactura,
  listarFacturas,
  
  // Dashboard y Logs
  obtenerDashboard,
  listarLogs,
};
