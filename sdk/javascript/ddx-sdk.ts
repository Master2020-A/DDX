/**
 * DDX SDK - JavaScript/TypeScript
 * SDK oficial para integración con la API de DDX
 * @version 1.0.0
 */

export interface DDXConfig {
  apiKey: string;
  apiSecret: string;
  baseUrl?: string;
  timeout?: number;
}

export interface Paciente {
  id: string;
  nombre_completo: string;
  fecha_nacimiento: string;
  sexo: string;
  email?: string;
  telefono?: string;
  rfc?: string;
  curp?: string;
}

export interface Consulta {
  id: string;
  paciente_id: string;
  fecha: string;
  motivo: string;
  diagnostico?: string;
  tratamiento?: string;
}

export interface Laboratorio {
  id: string;
  paciente_id: string;
  area: string;
  tipo_prueba: string;
  resultados: Record<string, any>;
  estado: string;
}

export interface Factura {
  id: string;
  paciente_id: string;
  folio: string;
  total: number;
  estado: string;
  uuid_sat?: string;
}

export interface WebhookEvent {
  evento: string;
  timestamp: string;
  data: Record<string, any>;
}

export class DDXClient {
  private config: DDXConfig;
  private baseUrl: string;

  constructor(config: DDXConfig) {
    this.config = config;
    this.baseUrl = config.baseUrl || 'https://api.ddx.com';
  }

  /**
   * Realiza una petición HTTP a la API
   */
  private async request<T>(
    method: string,
    endpoint: string,
    data?: any
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'X-API-Key': this.config.apiKey,
      'X-API-Secret': this.config.apiSecret,
    };

    const options: RequestInit = {
      method,
      headers,
      signal: AbortSignal.timeout(this.config.timeout || 30000),
    };

    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, options);

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new DDXError(
          response.status,
          error.detail || response.statusText,
          error
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof DDXError) {
        throw error;
      }
      throw new DDXError(0, 'Error de red', { originalError: error });
    }
  }

  // ============================================================================
  // Pacientes
  // ============================================================================

  /**
   * Listar pacientes
   */
  async listarPacientes(params?: {
    skip?: number;
    limit?: number;
    busqueda?: string;
  }): Promise<Paciente[]> {
    const queryParams = new URLSearchParams();
    if (params?.skip) queryParams.append('skip', params.skip.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.busqueda) queryParams.append('busqueda', params.busqueda);

    const query = queryParams.toString();
    return this.request<Paciente[]>(
      'GET',
      `/api/pacientes${query ? `?${query}` : ''}`
    );
  }

  /**
   * Obtener un paciente por ID
   */
  async obtenerPaciente(id: string): Promise<Paciente> {
    return this.request<Paciente>('GET', `/api/pacientes/${id}`);
  }

  /**
   * Crear un nuevo paciente
   */
  async crearPaciente(data: Partial<Paciente>): Promise<Paciente> {
    return this.request<Paciente>('POST', '/api/pacientes', data);
  }

  /**
   * Actualizar un paciente
   */
  async actualizarPaciente(
    id: string,
    data: Partial<Paciente>
  ): Promise<Paciente> {
    return this.request<Paciente>('PUT', `/api/pacientes/${id}`, data);
  }

  // ============================================================================
  // Consultas
  // ============================================================================

  /**
   * Listar consultas de un paciente
   */
  async listarConsultas(pacienteId: string): Promise<Consulta[]> {
    return this.request<Consulta[]>(
      'GET',
      `/api/consultas?paciente_id=${pacienteId}`
    );
  }

  /**
   * Crear una nueva consulta
   */
  async crearConsulta(data: Partial<Consulta>): Promise<Consulta> {
    return this.request<Consulta>('POST', '/api/consultas', data);
  }

  // ============================================================================
  // Laboratorio
  // ============================================================================

  /**
   * Listar pruebas de laboratorio de un paciente
   */
  async listarLaboratorios(pacienteId: string): Promise<Laboratorio[]> {
    return this.request<Laboratorio[]>(
      'GET',
      `/api/laboratorio?paciente_id=${pacienteId}`
    );
  }

  /**
   * Crear una nueva prueba de laboratorio
   */
  async crearLaboratorio(data: Partial<Laboratorio>): Promise<Laboratorio> {
    return this.request<Laboratorio>('POST', '/api/laboratorio', data);
  }

  // ============================================================================
  // Facturación
  // ============================================================================

  /**
   * Listar facturas
   */
  async listarFacturas(params?: {
    paciente_id?: string;
    estado?: string;
  }): Promise<Factura[]> {
    const queryParams = new URLSearchParams();
    if (params?.paciente_id)
      queryParams.append('paciente_id', params.paciente_id);
    if (params?.estado) queryParams.append('estado', params.estado);

    const query = queryParams.toString();
    return this.request<Factura[]>(
      'GET',
      `/api/integraciones/facturacion${query ? `?${query}` : ''}`
    );
  }

  /**
   * Generar una nueva factura
   */
  async generarFactura(data: any): Promise<Factura> {
    return this.request<Factura>(
      'POST',
      '/api/integraciones/facturacion/generar',
      data
    );
  }

  // ============================================================================
  // Webhooks
  // ============================================================================

  /**
   * Verificar firma de webhook
   */
  static verificarWebhook(
    payload: string,
    signature: string,
    secret: string
  ): boolean {
    const crypto = require('crypto');
    const hmac = crypto.createHmac('sha256', secret);
    hmac.update(payload);
    const expectedSignature = hmac.digest('hex');
    return signature === expectedSignature;
  }

  /**
   * Parsear evento de webhook
   */
  static parsearWebhook(body: string): WebhookEvent {
    return JSON.parse(body);
  }
}

/**
 * Error personalizado de DDX
 */
export class DDXError extends Error {
  constructor(
    public statusCode: number,
    message: string,
    public details?: any
  ) {
    super(message);
    this.name = 'DDXError';
  }
}

/**
 * Ejemplo de uso:
 * 
 * const ddx = new DDXClient({
 *   apiKey: 'ddx_tu_api_key',
 *   apiSecret: 'tu_secret',
 *   baseUrl: 'https://api.ddx.com'
 * });
 * 
 * // Listar pacientes
 * const pacientes = await ddx.listarPacientes({ limit: 10 });
 * 
 * // Crear paciente
 * const nuevoPaciente = await ddx.crearPaciente({
 *   nombre_completo: 'Juan Pérez',
 *   fecha_nacimiento: '1990-01-01',
 *   sexo: 'M'
 * });
 * 
 * // Webhook
 * app.post('/webhook', (req, res) => {
 *   const signature = req.headers['x-ddx-signature'];
 *   const isValid = DDXClient.verificarWebhook(
 *     JSON.stringify(req.body),
 *     signature,
 *     'tu_webhook_secret'
 *   );
 *   
 *   if (isValid) {
 *     const evento = DDXClient.parsearWebhook(JSON.stringify(req.body));
 *     console.log('Evento recibido:', evento.evento);
 *   }
 * });
 */

export default DDXClient;
