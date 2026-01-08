/**
 * Servicio para gestión de API Pública, Webhooks y Marketplace
 */

import api from './api';

// ============================================================================
// Tipos
// ============================================================================

export interface APIKey {
  id: string;
  nombre: string;
  descripcion?: string;
  key: string;
  secret?: string;
  permisos: string[];
  scopes: string[];
  rate_limit_por_minuto: number;
  rate_limit_por_dia: number;
  webhook_url?: string;
  eventos_suscritos: string[];
  activa: boolean;
  expira_en?: string;
  entorno: string;
  created_at: string;
  updated_at: string;
  ultimo_uso?: string;
  total_requests: number;
}

export interface APIKeyCreate {
  nombre: string;
  descripcion?: string;
  permisos?: string[];
  scopes?: string[];
  rate_limit_por_minuto?: number;
  rate_limit_por_dia?: number;
  webhook_url?: string;
  eventos_suscritos?: string[];
  expira_en?: string;
  ip_whitelist?: string[];
  entorno?: string;
}

export interface Webhook {
  id: string;
  nombre: string;
  url: string;
  secret: string;
  eventos: string[];
  max_reintentos: number;
  timeout_segundos: number;
  activo: boolean;
  headers_personalizados?: Record<string, string>;
  created_at: string;
  ultimo_envio?: string;
  total_envios: number;
  total_errores: number;
}

export interface WebhookCreate {
  nombre: string;
  url: string;
  eventos: string[];
  max_reintentos?: number;
  timeout_segundos?: number;
  headers_personalizados?: Record<string, string>;
}

export interface Plugin {
  id: string;
  nombre: string;
  slug: string;
  descripcion: string;
  descripcion_larga?: string;
  autor: string;
  email_autor?: string;
  url_autor?: string;
  version: string;
  version_minima_ddx?: string;
  categoria?: string;
  tags: string[];
  url_repositorio?: string;
  url_documentacion?: string;
  url_demo?: string;
  url_icono?: string;
  screenshots: string[];
  url_descarga?: string;
  requiere_api_key: boolean;
  permisos_requeridos: string[];
  configuracion_schema?: Record<string, any>;
  estado: string;
  verificado: boolean;
  descargas: number;
  instalaciones_activas: number;
  calificacion_promedio: number;
  total_calificaciones: number;
  es_gratuito: boolean;
  precio_usd: number;
  created_at: string;
  updated_at: string;
  fecha_aprobacion?: string;
}

export interface EstadisticasAPI {
  total_requests: number;
  requests_exitosos: number;
  requests_fallidos: number;
  tiempo_respuesta_promedio_ms: number;
  endpoints_mas_usados: Array<{ endpoint: string; total: number }>;
  errores_comunes: Array<{ error: string; total: number }>;
  uso_por_dia: Array<{ fecha: string; total: number }>;
}

export interface LogAPI {
  id: string;
  metodo: string;
  endpoint: string;
  ip_origen?: string;
  status_code?: number;
  tiempo_respuesta_ms?: number;
  error?: string;
  timestamp: string;
}

// ============================================================================
// API Keys
// ============================================================================

export const crearAPIKey = async (data: APIKeyCreate): Promise<APIKey> => {
  const response = await api.post('/api-publica/keys', data);
  return response.data;
};

export const listarAPIKeys = async (params?: {
  activa?: boolean;
  entorno?: string;
}): Promise<APIKey[]> => {
  const response = await api.get('/api-publica/keys', { params });
  return response.data;
};

export const obtenerAPIKey = async (keyId: string): Promise<APIKey> => {
  const response = await api.get(`/api-publica/keys/${keyId}`);
  return response.data;
};

export const actualizarAPIKey = async (
  keyId: string,
  data: Partial<APIKeyCreate>
): Promise<APIKey> => {
  const response = await api.put(`/api-publica/keys/${keyId}`, data);
  return response.data;
};

export const eliminarAPIKey = async (keyId: string): Promise<void> => {
  await api.delete(`/api-publica/keys/${keyId}`);
};

export const regenerarSecret = async (keyId: string): Promise<APIKey> => {
  const response = await api.post(`/api-publica/keys/${keyId}/regenerar-secret`);
  return response.data;
};

// ============================================================================
// Webhooks
// ============================================================================

export const crearWebhook = async (data: WebhookCreate): Promise<Webhook> => {
  const response = await api.post('/api-publica/webhooks', data);
  return response.data;
};

export const listarWebhooks = async (params?: {
  activo?: boolean;
}): Promise<Webhook[]> => {
  const response = await api.get('/api-publica/webhooks', { params });
  return response.data;
};

export const actualizarWebhook = async (
  webhookId: string,
  data: Partial<WebhookCreate>
): Promise<Webhook> => {
  const response = await api.put(`/api-publica/webhooks/${webhookId}`, data);
  return response.data;
};

export const eliminarWebhook = async (webhookId: string): Promise<void> => {
  await api.delete(`/api-publica/webhooks/${webhookId}`);
};

export const listarEntregasWebhook = async (
  webhookId: string,
  limite: number = 50
): Promise<any[]> => {
  const response = await api.get(`/api-publica/webhooks/${webhookId}/entregas`, {
    params: { limite },
  });
  return response.data;
};

// ============================================================================
// Marketplace
// ============================================================================

export const publicarPlugin = async (data: any): Promise<Plugin> => {
  const response = await api.post('/api-publica/marketplace/plugins', data);
  return response.data;
};

export const listarPlugins = async (params?: {
  categoria?: string;
  tag?: string;
  verificado?: boolean;
  busqueda?: string;
  skip?: number;
  limit?: number;
}): Promise<Plugin[]> => {
  const response = await api.get('/api-publica/marketplace/plugins', { params });
  return response.data;
};

export const obtenerPlugin = async (slug: string): Promise<Plugin> => {
  const response = await api.get(`/api-publica/marketplace/plugins/${slug}`);
  return response.data;
};

export const instalarPlugin = async (
  pluginId: string,
  data: {
    configuracion?: Record<string, any>;
    api_key_id?: string;
  }
): Promise<any> => {
  const response = await api.post(
    `/api-publica/marketplace/plugins/${pluginId}/instalar`,
    { plugin_id: pluginId, ...data }
  );
  return response.data;
};

export const crearResenaPlugin = async (
  pluginId: string,
  data: {
    calificacion: number;
    titulo?: string;
    comentario?: string;
    autor_nombre: string;
    autor_email?: string;
    version_plugin: string;
  }
): Promise<any> => {
  const response = await api.post(
    `/api-publica/marketplace/plugins/${pluginId}/resenas`,
    { plugin_id: pluginId, ...data }
  );
  return response.data;
};

export const obtenerEstadisticasMarketplace = async (): Promise<any> => {
  const response = await api.get('/api-publica/marketplace/estadisticas');
  return response.data;
};

// ============================================================================
// Logs y Estadísticas
// ============================================================================

export const listarLogs = async (params?: {
  fecha_desde?: string;
  fecha_hasta?: string;
  limite?: number;
}): Promise<LogAPI[]> => {
  const response = await api.get('/api-publica/logs', { params });
  return response.data;
};

export const obtenerEstadisticas = async (
  dias: number = 7
): Promise<EstadisticasAPI> => {
  const response = await api.get('/api-publica/estadisticas', {
    params: { dias },
  });
  return response.data;
};

// ============================================================================
// Constantes
// ============================================================================

export const EVENTOS_DISPONIBLES = [
  { id: 'paciente.creado', nombre: 'Paciente Creado' },
  { id: 'paciente.actualizado', nombre: 'Paciente Actualizado' },
  { id: 'consulta.creada', nombre: 'Consulta Creada' },
  { id: 'consulta.finalizada', nombre: 'Consulta Finalizada' },
  { id: 'laboratorio.creado', nombre: 'Laboratorio Creado' },
  { id: 'laboratorio.completado', nombre: 'Laboratorio Completado' },
  { id: 'imagen.subida', nombre: 'Imagen Subida' },
  { id: 'imagen.analizada', nombre: 'Imagen Analizada' },
  { id: 'factura.generada', nombre: 'Factura Generada' },
  { id: 'factura.timbrada', nombre: 'Factura Timbrada' },
  { id: 'receta.generada', nombre: 'Receta Generada' },
  { id: 'receta.surtida', nombre: 'Receta Surtida' },
];

export const SCOPES_DISPONIBLES = [
  { id: 'pacientes:read', nombre: 'Leer Pacientes', descripcion: 'Consultar información de pacientes' },
  { id: 'pacientes:write', nombre: 'Escribir Pacientes', descripcion: 'Crear y actualizar pacientes' },
  { id: 'consultas:read', nombre: 'Leer Consultas', descripcion: 'Consultar información de consultas' },
  { id: 'consultas:write', nombre: 'Escribir Consultas', descripcion: 'Crear y actualizar consultas' },
  { id: 'laboratorio:read', nombre: 'Leer Laboratorios', descripcion: 'Consultar resultados de laboratorio' },
  { id: 'laboratorio:write', nombre: 'Escribir Laboratorios', descripcion: 'Crear resultados de laboratorio' },
  { id: 'imagenes:read', nombre: 'Leer Imágenes', descripcion: 'Consultar imágenes médicas' },
  { id: 'imagenes:write', nombre: 'Escribir Imágenes', descripcion: 'Subir imágenes médicas' },
  { id: 'facturacion:read', nombre: 'Leer Facturas', descripcion: 'Consultar facturas' },
  { id: 'facturacion:write', nombre: 'Escribir Facturas', descripcion: 'Generar facturas' },
  { id: 'recetas:read', nombre: 'Leer Recetas', descripcion: 'Consultar recetas electrónicas' },
  { id: 'recetas:write', nombre: 'Escribir Recetas', descripcion: 'Generar recetas electrónicas' },
  { id: 'admin', nombre: 'Administrador', descripcion: 'Acceso completo a todos los recursos' },
];

export const CATEGORIAS_PLUGINS = [
  'integracion',
  'comunicacion',
  'analisis',
  'reportes',
  'facturacion',
  'laboratorio',
  'imagenes',
  'seguridad',
  'productividad',
  'otros',
];

export default {
  // API Keys
  crearAPIKey,
  listarAPIKeys,
  obtenerAPIKey,
  actualizarAPIKey,
  eliminarAPIKey,
  regenerarSecret,
  
  // Webhooks
  crearWebhook,
  listarWebhooks,
  actualizarWebhook,
  eliminarWebhook,
  listarEntregasWebhook,
  
  // Marketplace
  publicarPlugin,
  listarPlugins,
  obtenerPlugin,
  instalarPlugin,
  crearResenaPlugin,
  obtenerEstadisticasMarketplace,
  
  // Logs y Estadísticas
  listarLogs,
  obtenerEstadisticas,
  
  // Constantes
  EVENTOS_DISPONIBLES,
  SCOPES_DISPONIBLES,
  CATEGORIAS_PLUGINS,
};
