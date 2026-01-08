import api from '@/lib/api';

export interface N8NConfig {
  id: string;
  nombre: string;
  descripcion?: string;
  n8n_webhook_url: string;
  n8n_api_url?: string;
  activo: boolean;
  webhooks_habilitados: boolean;
  timeout_segundos: number;
  eventos_habilitados?: string[];
  api_key: string;
  total_eventos_enviados: number;
  total_eventos_exitosos: number;
  total_eventos_fallidos: number;
  ultimo_evento_enviado?: string;
  created_by: string;
  created_at: string;
  updated_at?: string;
}

export interface N8NConfigCreate {
  nombre: string;
  descripcion?: string;
  n8n_webhook_url: string;
  n8n_api_url?: string;
  activo?: boolean;
  webhooks_habilitados?: boolean;
  timeout_segundos?: number;
  eventos_habilitados?: string[];
}

export interface N8NConfigStats {
  total_eventos_enviados: number;
  total_eventos_exitosos: number;
  total_eventos_fallidos: number;
  tasa_exito: number;
  ultimo_evento_enviado?: string;
}

export interface N8NEventLog {
  id: string;
  evento_tipo: string;
  evento_data: any;
  prioridad: string;
  webhook_url: string;
  exitoso: boolean;
  codigo_http?: number;
  tiempo_respuesta_ms?: number;
  error?: string;
  created_at: string;
}

export interface EventoDisponible {
  nombre: string;
  descripcion: string;
  categoria: string;
  prioridad_default: string;
  ejemplo_payload: any;
}

export interface N8NWorkflow {
  id: string;
  name: string;
  active: boolean;
  createdAt?: string;
  updatedAt?: string;
}

export interface N8NExecution {
  id: string;
  workflowId: string;
  finished: boolean;
  mode: string;
  startedAt: string;
  stoppedAt?: string;
  status: string;
}

const n8nService = {
  // ========== Configuración ==========
  
  async getConfig(): Promise<N8NConfig> {
    const response = await api.get('/n8n/config');
    return response.data;
  },

  async createConfig(data: N8NConfigCreate): Promise<N8NConfig> {
    const response = await api.post('/n8n/config', data);
    return response.data;
  },

  async updateConfig(id: string, data: Partial<N8NConfigCreate>): Promise<N8NConfig> {
    const response = await api.put(`/n8n/config/${id}`, data);
    return response.data;
  },

  async deleteConfig(id: string): Promise<void> {
    await api.delete(`/n8n/config/${id}`);
  },

  async getStats(): Promise<N8NConfigStats> {
    const response = await api.get('/n8n/config/stats');
    return response.data;
  },

  // ========== API Keys ==========

  async generateApiKey(nombre: string, descripcion?: string): Promise<{ api_key: string; mensaje: string; usage: string }> {
    const response = await api.post('/n8n/api-key/generate', { nombre, descripcion });
    return response.data;
  },

  async regenerateApiKey(): Promise<{ api_key: string; mensaje: string; usage: string }> {
    const response = await api.post('/n8n/api-key/regenerate');
    return response.data;
  },

  // ========== Event Logs ==========

  async getEvents(params?: {
    evento_tipo?: string;
    exitoso?: boolean;
    limit?: number;
    offset?: number;
  }): Promise<N8NEventLog[]> {
    const response = await api.get('/n8n/events', { params });
    return response.data;
  },

  async getEvent(id: string): Promise<N8NEventLog> {
    const response = await api.get(`/n8n/events/${id}`);
    return response.data;
  },

  // ========== Webhooks ==========

  async testWebhook(url: string, event_type: string, test_data?: any): Promise<{
    exitoso: boolean;
    mensaje: string;
    codigo_http?: number;
    tiempo_respuesta_ms?: number;
    error?: string;
  }> {
    const response = await api.post('/n8n/webhook/test', {
      url,
      event_type,
      test_data
    });
    return response.data;
  },

  async getEventosDisponibles(): Promise<{
    total: number;
    categorias: string[];
    eventos: EventoDisponible[];
  }> {
    const response = await api.get('/n8n/eventos-disponibles');
    return response.data;
  },

  // ========== Workflows Management ==========

  async getWorkflowsStatus(): Promise<{
    total: number;
    active: number;
    inactive: number;
    workflows: N8NWorkflow[];
  }> {
    const response = await api.get('/n8n/workflows/status');
    return response.data;
  },

  async getExecutionsStatus(): Promise<{
    total: number;
    success: number;
    failed: number;
    running: number;
    executions: N8NExecution[];
  }> {
    const response = await api.get('/n8n/executions/recent');
    return response.data;
  },

  // Gestión de workflows
  async getWorkflowTemplates(): Promise<{ templates: Array<{ id: string; name: string; description: string; category: string; nodes: number; trigger: string; }> }> {
    const response = await api.get('/n8n/workflows/templates');
    return response.data;
  },

  async createWorkflowFromTemplate(templateName: string, workflowName: string): Promise<{ success: boolean; workflow_id: string; workflow_name: string; message: string; edit_url: string; }> {
    const response = await api.post('/n8n/workflows/create-from-template', null, {
      params: { template_name: templateName, workflow_name: workflowName }
    });
    return response.data;
  },

  async deleteWorkflow(workflowId: string): Promise<{ success: boolean; message: string; }> {
    const response = await api.delete(`/n8n/workflows/${workflowId}`);
    return response.data;
  },
};

export default n8nService;
