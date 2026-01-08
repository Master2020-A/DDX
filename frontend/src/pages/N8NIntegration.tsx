import React, { useState, useEffect } from 'react';
import {
  Activity,
  Settings,
  Zap,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  AlertCircle,
  RefreshCw,
  Key,
  Play,
  Pause,
  BookOpen,
  Copy,
  ExternalLink,
} from 'lucide-react';
import n8nService, { N8NConfig, N8NConfigStats, N8NEventLog } from '@/services/n8nService';

const N8NIntegration: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'config' | 'events' | 'workflows' | 'examples'>('overview');
  const [config, setConfig] = useState<N8NConfig | null>(null);
  const [stats, setStats] = useState<N8NConfigStats | null>(null);
  const [events, setEvents] = useState<N8NEventLog[]>([]);
  const [workflows, setWorkflows] = useState<any>(null);
  const [executions, setExecutions] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedExample, setSelectedExample] = useState<number | null>(null);
  const [copiedCode, setCopiedCode] = useState<number | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [workflowName, setWorkflowName] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [configData, statsData, eventsData] = await Promise.all([
        n8nService.getConfig().catch(() => null),
        n8nService.getStats().catch(() => null),
        n8nService.getEvents({ limit: 50 }).catch(() => []),
      ]);

      setConfig(configData);
      setStats(statsData);
      setEvents(eventsData);

      if (configData?.activo) {
        const [workflowsData, executionsData] = await Promise.all([
          n8nService.getWorkflowsStatus().catch(() => null),
          n8nService.getExecutionsStatus().catch(() => null),
        ]);
        setWorkflows(workflowsData);
        setExecutions(executionsData);
      }
    } catch (err: any) {
      setError(err.message || 'Error al cargar datos de N8N');
    } finally {
      setLoading(false);
    }
  };

  const handleTestWebhook = async () => {
    if (!config) return;

    try {
      const result = await n8nService.testWebhook(
        config.n8n_webhook_url + '/test',
        'test.webhook',
        { mensaje: 'Prueba desde DDX' }
      );

      if (result.exitoso) {
        alert('✅ Webhook enviado exitosamente');
      } else {
        alert(`❌ Error: ${result.error || 'Error desconocido'}`);
      }
    } catch (err: any) {
      alert(`❌ Error: ${err.message}`);
    }
  };

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Estado General */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Estado</p>
              <p className="text-2xl font-bold mt-1">
                {config?.activo ? (
                  <span className="text-green-600">Activo</span>
                ) : (
                  <span className="text-gray-400">Inactivo</span>
                )}
              </p>
            </div>
            {config?.activo ? (
              <CheckCircle className="text-green-600" size={32} />
            ) : (
              <XCircle className="text-gray-400" size={32} />
            )}
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Eventos Enviados</p>
              <p className="text-2xl font-bold mt-1">{stats?.total_eventos_enviados || 0}</p>
            </div>
            <Zap className="text-blue-600" size={32} />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Tasa de Éxito</p>
              <p className="text-2xl font-bold mt-1">{stats?.tasa_exito.toFixed(1) || 0}%</p>
            </div>
            <TrendingUp className="text-green-600" size={32} />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Workflows Activos</p>
              <p className="text-2xl font-bold mt-1">{workflows?.active || 0}</p>
            </div>
            <Activity className="text-purple-600" size={32} />
          </div>
        </div>
      </div>

      {/* Workflows Status */}
      {workflows && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Workflows de N8N</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <p className="text-3xl font-bold text-blue-600">{workflows.total}</p>
              <p className="text-sm text-gray-600">Total</p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <p className="text-3xl font-bold text-green-600">{workflows.active}</p>
              <p className="text-sm text-gray-600">Activos</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-3xl font-bold text-gray-600">{workflows.inactive}</p>
              <p className="text-sm text-gray-600">Inactivos</p>
            </div>
          </div>

          <div className="space-y-2">
            {workflows.workflows?.slice(0, 5).map((workflow: any) => (
              <div key={workflow.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div className="flex items-center gap-3">
                  {workflow.active ? (
                    <Play className="text-green-600" size={20} />
                  ) : (
                    <Pause className="text-gray-400" size={20} />
                  )}
                  <div>
                    <p className="font-medium">{workflow.name}</p>
                    <p className="text-xs text-gray-500">ID: {workflow.id}</p>
                  </div>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-medium ${
                    workflow.active ? 'bg-green-100 text-green-800' : 'bg-gray-200 text-gray-600'
                  }`}
                >
                  {workflow.active ? 'Activo' : 'Inactivo'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Ejecuciones Recientes */}
      {executions && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Ejecuciones Recientes</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <p className="text-3xl font-bold text-blue-600">{executions.total}</p>
              <p className="text-sm text-gray-600">Total</p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <p className="text-3xl font-bold text-green-600">{executions.success}</p>
              <p className="text-sm text-gray-600">Exitosas</p>
            </div>
            <div className="text-center p-4 bg-red-50 rounded-lg">
              <p className="text-3xl font-bold text-red-600">{executions.failed}</p>
              <p className="text-sm text-gray-600">Fallidas</p>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <p className="text-3xl font-bold text-yellow-600">{executions.running}</p>
              <p className="text-sm text-gray-600">En Ejecución</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderConfig = () => (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold">Configuración de N8N</h3>
        <button
          onClick={handleTestWebhook}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <Zap size={16} />
          Probar Webhook
        </button>
      </div>

      {config ? (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
              <input
                type="text"
                value={config.nombre}
                readOnly
                className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Estado</label>
              <div className="flex items-center gap-2">
                <span
                  className={`px-3 py-2 rounded-md font-medium ${
                    config.activo ? 'bg-green-100 text-green-800' : 'bg-gray-200 text-gray-600'
                  }`}
                >
                  {config.activo ? 'Activo' : 'Inactivo'}
                </span>
              </div>
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">URL de Webhooks</label>
              <input
                type="text"
                value={config.n8n_webhook_url}
                readOnly
                className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50"
              />
            </div>

            {config.n8n_api_url && (
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">URL de API</label>
                <input
                  type="text"
                  value={config.n8n_api_url}
                  readOnly
                  className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50"
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Timeout (segundos)</label>
              <input
                type="number"
                value={config.timeout_segundos}
                readOnly
                className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Webhooks Habilitados</label>
              <span
                className={`inline-block px-3 py-2 rounded-md font-medium ${
                  config.webhooks_habilitados ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}
              >
                {config.webhooks_habilitados ? 'Sí' : 'No'}
              </span>
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <Key size={16} className="inline mr-1" />
                API Key
              </label>
              <div className="flex gap-2">
                <input
                  type="password"
                  value={config.api_key}
                  readOnly
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md bg-gray-50 font-mono text-sm"
                />
                <button
                  onClick={() => navigator.clipboard.writeText(config.api_key)}
                  className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
                >
                  Copiar
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Usar en N8N HTTP Request headers: Authorization: Bearer {'{api_key}'}
              </p>
            </div>
          </div>

          {config.descripcion && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
              <textarea
                value={config.descripcion}
                readOnly
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50"
              />
            </div>
          )}
        </div>
      ) : (
        <div className="text-center py-12">
          <AlertCircle className="mx-auto text-gray-400 mb-4" size={48} />
          <p className="text-gray-600">No hay configuración de N8N activa</p>
          <p className="text-sm text-gray-500 mt-2">
            Contacta al administrador para configurar la integración con N8N
          </p>
        </div>
      )}
    </div>
  );

  const renderEvents = () => (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold">Log de Eventos</h3>
        <button
          onClick={loadData}
          className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 flex items-center gap-2"
        >
          <RefreshCw size={16} />
          Actualizar
        </button>
      </div>

      {events.length > 0 ? (
        <div className="space-y-2">
          {events.map((event) => (
            <div
              key={event.id}
              className={`p-4 rounded-lg border-l-4 ${
                event.exitoso ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    {event.exitoso ? (
                      <CheckCircle className="text-green-600" size={20} />
                    ) : (
                      <XCircle className="text-red-600" size={20} />
                    )}
                    <span className="font-medium">{event.evento_tipo}</span>
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${
                        event.prioridad === 'critical'
                          ? 'bg-red-100 text-red-800'
                          : event.prioridad === 'high'
                          ? 'bg-orange-100 text-orange-800'
                          : 'bg-blue-100 text-blue-800'
                      }`}
                    >
                      {event.prioridad}
                    </span>
                  </div>

                  <div className="text-sm text-gray-600 space-y-1">
                    <p>
                      <Clock size={14} className="inline mr-1" />
                      {new Date(event.created_at).toLocaleString('es-MX')}
                    </p>
                    {event.codigo_http && (
                      <p>HTTP {event.codigo_http}</p>
                    )}
                    {event.tiempo_respuesta_ms && (
                      <p>{event.tiempo_respuesta_ms}ms</p>
                    )}
                    {event.error && (
                      <p className="text-red-600 text-xs mt-2">{event.error}</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Activity className="mx-auto text-gray-400 mb-4" size={48} />
          <p className="text-gray-600">No hay eventos registrados</p>
        </div>
      )}
    </div>
  );

  const handleCreateWorkflow = async (templateId: string) => {
    setSelectedTemplate(templateId);
    setWorkflowName('');
    setShowCreateModal(true);
  };

  const handleConfirmCreate = async () => {
    if (!selectedTemplate || !workflowName.trim()) {
      alert('Por favor ingrese un nombre para el workflow');
      return;
    }

    try {
      setCreating(true);
      const result = await n8nService.createWorkflowFromTemplate(selectedTemplate, workflowName);
      
      alert(`✅ ${result.message}\n\nAhora puedes editarlo en N8N.`);
      setShowCreateModal(false);
      setSelectedTemplate(null);
      setWorkflowName('');
      
      // Abrir N8N en nueva pestaña
      window.open(result.edit_url, '_blank');
      
      // Recargar workflows
      loadData();
    } catch (err: any) {
      alert(`❌ Error: ${err.response?.data?.detail || err.message}`);
    } finally {
      setCreating(false);
    }
  };

  const copyToClipboard = (text: string, id: number) => {
    navigator.clipboard.writeText(text);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const templateMapping: Record<number, string> = {
    1: 'alerta_critica',
    2: 'recordatorio_citas',
    3: 'notificacion_resultados'
  };

  const renderExamples = () => {

    const examples = [
      {
        id: 1,
        title: '🚨 Alertas Médicas Críticas',
        description: 'Envía alertas inmediatas por Email y SMS cuando hay resultados de laboratorio críticos (ej: Glucosa >400 mg/dL)',
        category: 'Laboratorio',
        difficulty: 'Intermedio',
        nodes: 4,
        workflow: {
          trigger: 'Webhook: laboratorio.resultado_critico',
          steps: [
            'Function: Formatear datos del resultado',
            'Send Email: Notificar al médico',
            'Send SMS (Twilio): Alerta por mensaje',
            'HTTP Request: Registrar notificación en DDX'
          ]
        },
        code: `// Nodo Function - Formatear Datos
const data = $input.item.json.data;

return {
  json: {
    paciente_nombre: data.paciente_nombre,
    parametro: data.parametro,
    valor: data.valor,
    nivel: data.nivel,
    medico_email: data.medico_email,
    urgencia: "CRÍTICO"
  }
};`
      },
      {
        id: 2,
        title: '📅 Recordatorios Automáticos de Citas',
        description: 'Envía recordatorios automáticos a pacientes 24 horas antes de su cita médica por Email y WhatsApp',
        category: 'Citas',
        difficulty: 'Básico',
        nodes: 5,
        workflow: {
          trigger: 'Schedule: Diario a las 8:00 AM',
          steps: [
            'HTTP Request: Obtener citas del día siguiente',
            'Split In Batches: Procesar cada cita',
            'Function: Formatear mensaje personalizado',
            'Send Email: Recordatorio por correo',
            'Send WhatsApp: Recordatorio por WhatsApp'
          ]
        },
        code: `// Nodo Function - Formatear Mensaje
const cita = $input.item.json;
const fecha = new Date(cita.fecha_hora);
const fechaFormateada = fecha.toLocaleDateString('es-MX', {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
  hour: '2-digit',
  minute: '2-digit'
});

return {
  json: {
    paciente_nombre: cita.paciente_nombre,
    paciente_email: cita.paciente_email,
    fecha_formateada: fechaFormateada,
    medico_nombre: cita.medico_nombre
  }
};`
      },
      {
        id: 3,
        title: '🧪 Notificación de Resultados de Laboratorio',
        description: 'Notifica al paciente cuando sus resultados están listos con un enlace seguro temporal para verlos',
        category: 'Laboratorio',
        difficulty: 'Intermedio',
        nodes: 4,
        workflow: {
          trigger: 'Webhook: laboratorio.completado',
          steps: [
            'HTTP Request: Generar token de acceso temporal',
            'Function: Crear enlace seguro',
            'Send Email: Email HTML con enlace',
            'HTTP Request: Registrar notificación enviada'
          ]
        },
        code: `// Nodo Function - Crear Enlace Seguro
const data = $input.item.json;
const token = data.token;
const prueba_id = data.prueba_id;

const enlace_seguro = \`http://localhost:3000/portal-paciente/resultados/\${prueba_id}?token=\${token}\`;

return {
  json: {
    paciente_nombre: data.paciente.nombre_completo,
    paciente_email: data.paciente.email,
    tipo_prueba: data.tipo_prueba,
    enlace_seguro: enlace_seguro,
    expiracion: "24 horas"
  }
};`
      },
      {
        id: 4,
        title: '🎥 Workflow de Telemedicina',
        description: 'Automatiza el proceso completo: notificación → consulta → encuesta de satisfacción → seguimiento',
        category: 'Telemedicina',
        difficulty: 'Avanzado',
        nodes: 8,
        workflow: {
          trigger: 'Webhook: telemedicina.consulta_iniciada',
          steps: [
            'Send Email: Enlace de sala al paciente',
            'Wait: 1 hora (duración promedio)',
            'HTTP Request: Verificar estado de consulta',
            'IF Node: ¿Consulta finalizada?',
            'Send Email: Encuesta de satisfacción',
            'Wait: 24 horas',
            'Send SMS: Recordatorio de seguimiento'
          ]
        },
        code: `// Nodo Send Email - Enlace de Sala
To: {{$json.paciente_email}}
Subject: 🎥 Su Consulta de Telemedicina está Lista

Estimado(a) {{$json.paciente_nombre}},

Su consulta está programada para:
📅 {{$json.fecha_hora}}

Acceda a la sala:
🔗 http://localhost:3000/telemedicina/sala/{{$json.consulta_id}}

Recomendaciones:
✅ Pruebe su cámara y micrófono
✅ Busque un lugar tranquilo
✅ Tenga a mano su identificación`
      },
      {
        id: 5,
        title: '💾 Backup Automático Diario',
        description: 'Realiza backup automático de la base de datos, lo sube a la nube y notifica al administrador',
        category: 'Sistema',
        difficulty: 'Avanzado',
        nodes: 8,
        workflow: {
          trigger: 'Schedule: Diario a las 2:00 AM',
          steps: [
            'HTTP Request: Iniciar backup en DDX',
            'Wait: 5 minutos (tiempo de backup)',
            'HTTP Request: Verificar estado del backup',
            'Function: Calcular métricas',
            'IF Node: ¿Backup exitoso?',
            'Upload to S3/Drive: Subir archivo',
            'Send Email: Notificar resultado'
          ]
        },
        code: `// Nodo Function - Calcular Métricas
const backup = $input.item.json;
const tamaño_mb = (backup.tamaño_bytes / 1024 / 1024).toFixed(2);
const duracion_min = Math.round(backup.duracion_segundos / 60);

return {
  json: {
    backup_id: backup.id,
    fecha: backup.fecha_creacion,
    tamaño_mb: tamaño_mb,
    duracion_min: duracion_min,
    exitoso: backup.estado === "completado",
    archivo: backup.ruta_archivo
  }
};`
      },
      {
        id: 6,
        title: '📊 Reporte Diario de Métricas',
        description: 'Envía un reporte diario con KPIs, estadísticas y gráficas al equipo directivo',
        category: 'Reportes',
        difficulty: 'Intermedio',
        nodes: 5,
        workflow: {
          trigger: 'Schedule: Lunes a Viernes 7:00 AM',
          steps: [
            'HTTP Request: Obtener métricas del día anterior',
            'Function: Calcular KPIs y tendencias',
            'QuickChart: Generar gráficas',
            'Send Email: Reporte con gráficas',
            'HTTP Request: Registrar envío'
          ]
        },
        code: `// Nodo Function - Calcular KPIs
const metricas = $input.item.json;

const tendencia_pacientes = metricas.pacientes_nuevos > metricas.pacientes_nuevos_ayer ? "📈" : "📉";
const tendencia_consultas = metricas.consultas_hoy > metricas.consultas_ayer ? "📈" : "📉";

return {
  json: {
    fecha: new Date().toLocaleDateString('es-MX'),
    pacientes_nuevos: metricas.pacientes_nuevos,
    tendencia_pacientes: tendencia_pacientes,
    consultas_hoy: metricas.consultas_hoy,
    tendencia_consultas: tendencia_consultas,
    satisfaccion_promedio: metricas.satisfaccion_promedio
  }
};`
      },
      {
        id: 7,
        title: '💬 Integración con WhatsApp Business',
        description: 'Envía confirmaciones de citas y recordatorios automáticos por WhatsApp',
        category: 'Citas',
        difficulty: 'Intermedio',
        nodes: 5,
        workflow: {
          trigger: 'Webhook: cita.agendada',
          steps: [
            'Function: Formatear mensaje WhatsApp',
            'WhatsApp Business API: Enviar confirmación',
            'Wait Until: 24 horas antes de la cita',
            'WhatsApp Business API: Enviar recordatorio',
            'HTTP Request: Registrar mensajes enviados'
          ]
        },
        code: `// Nodo Function - Formatear Mensaje WhatsApp
const cita = $input.item.json.data;
const fecha = new Date(cita.fecha_hora);
const fechaFormateada = fecha.toLocaleDateString('es-MX');

const mensaje = \`✅ *Cita Confirmada*\n\nHola \${cita.paciente_nombre} 👋\n\n📅 *Fecha:* \${fechaFormateada}\n👨‍⚕️ *Médico:* \${cita.medico_nombre}\n\nLe enviaremos un recordatorio 24 horas antes.\`;

return {
  json: {
    telefono: cita.paciente_telefono,
    mensaje: mensaje
  }
};`
      },
      {
        id: 8,
        title: '🔔 Seguimiento Post-Consulta',
        description: 'Seguimiento automatizado del paciente 3 días después de la consulta con detección de complicaciones',
        category: 'Consultas',
        difficulty: 'Avanzado',
        nodes: 7,
        workflow: {
          trigger: 'Webhook: consulta.completada',
          steps: [
            'Wait: 3 días',
            'Send Email: Encuesta de seguimiento',
            'Wait for Webhook: Respuesta del paciente',
            'IF Node: ¿Reporta síntomas?',
            'HTTP Request: Crear alerta médica',
            'Send Email: Notificar al médico'
          ]
        },
        code: `// Nodo IF - Verificar Síntomas
const respuesta = $input.item.json;

// Considerar alerta si:
// - Paciente se siente peor
// - Reporta nuevos síntomas
// - Solicita contacto urgente

return respuesta.estado === "peor" || 
       respuesta.nuevos_sintomas === true ||
       respuesta.contacto_urgente === true;`
      }
    ];

    return (
      <div className="space-y-6">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-start gap-3">
            <BookOpen className="text-blue-600 mt-1" size={24} />
            <div>
              <h3 className="font-semibold text-blue-900 mb-2">Workflows Listos para Usar</h3>
              <p className="text-blue-700 text-sm">
                Estos son ejemplos prácticos de workflows de N8N integrados con DDX. 
                Cada ejemplo incluye el diagrama de flujo, configuración de nodos y código listo para copiar.
              </p>
              <a 
                href="http://localhost:5678" 
                target="_blank" 
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 mt-3 text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                <ExternalLink size={16} />
                Abrir N8N Editor
              </a>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {examples.map((example) => (
            <div
              key={example.id}
              className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => setSelectedExample(selectedExample === example.id ? null : example.id)}
            >
              <div className="flex items-start justify-between mb-3">
                <h3 className="text-lg font-semibold text-gray-900">{example.title}</h3>
                <span className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded">
                  {example.nodes} nodos
                </span>
              </div>

              <p className="text-sm text-gray-600 mb-4">{example.description}</p>

              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">
                    {example.category}
                  </span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    example.difficulty === 'Básico' ? 'bg-green-100 text-green-700' :
                    example.difficulty === 'Intermedio' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-red-100 text-red-700'
                  }`}>
                    {example.difficulty}
                  </span>
                </div>
                {templateMapping[example.id] && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleCreateWorkflow(templateMapping[example.id]);
                    }}
                    className="flex items-center gap-1 px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 transition-colors"
                  >
                    <Zap size={12} />
                    Crear en N8N
                  </button>
                )}
              </div>

              {selectedExample === example.id && (
                <div className="mt-4 pt-4 border-t border-gray-200 space-y-4">
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">🎯 Trigger</h4>
                    <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded">
                      {example.workflow.trigger}
                    </p>
                  </div>

                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">📝 Pasos del Workflow</h4>
                    <ol className="text-sm text-gray-700 space-y-2">
                      {example.workflow.steps.map((step, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <span className="font-semibold text-blue-600">{idx + 1}.</span>
                          <span>{step}</span>
                        </li>
                      ))}
                    </ol>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-semibold text-gray-900">💻 Código de Ejemplo</h4>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          copyToClipboard(example.code, example.id);
                        }}
                        className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800"
                      >
                        <Copy size={14} />
                        {copiedCode === example.id ? '✓ Copiado' : 'Copiar'}
                      </button>
                    </div>
                    <pre className="text-xs bg-gray-900 text-gray-100 p-4 rounded overflow-x-auto">
                      <code>{example.code}</code>
                    </pre>
                  </div>

                  <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
                    <p className="text-xs text-yellow-800">
                      💡 <strong>Tip:</strong> Copia este código en un nodo Function de N8N y ajusta los nombres de variables según tu configuración.
                    </p>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
          <h3 className="font-semibold text-gray-900 mb-3">📚 Documentación Completa</h3>
          <p className="text-sm text-gray-600 mb-4">
            Para más detalles sobre cada workflow, consulta el archivo de documentación completo:
          </p>
          <code className="text-sm bg-white border border-gray-300 px-3 py-2 rounded block">
            C:\Users\Master\Documents\DDX\EJEMPLOS_N8N_DDX.md
          </code>
        </div>

        {/* Modal para crear workflow */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
              <h3 className="text-xl font-bold text-gray-900 mb-4">⚡ Crear Workflow en N8N</h3>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nombre del Workflow
                </label>
                <input
                  type="text"
                  value={workflowName}
                  onChange={(e) => setWorkflowName(e.target.value)}
                  placeholder="Ej: Alertas Críticas - Producción"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={creating}
                />
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded p-3 mb-4">
                <p className="text-xs text-blue-800">
                  💡 El workflow se creará en N8N y se abrirá automáticamente para que puedas editarlo y configurarlo.
                </p>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleConfirmCreate}
                  disabled={creating || !workflowName.trim()}
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                >
                  {creating ? 'Creando...' : 'Crear Workflow'}
                </button>
                <button
                  onClick={() => {
                    setShowCreateModal(false);
                    setSelectedTemplate(null);
                    setWorkflowName('');
                  }}
                  disabled={creating}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors"
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <RefreshCw className="animate-spin text-blue-600" size={48} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center gap-3">
          <AlertCircle className="text-red-600" size={24} />
          <div>
            <h3 className="font-semibold text-red-900">Error</h3>
            <p className="text-red-700">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Integración N8N</h1>
        <p className="text-gray-600">Automatización de workflows y eventos</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex gap-4">
          <button
            onClick={() => setActiveTab('overview')}
            className={`pb-3 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'overview'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Activity className="inline mr-2" size={16} />
            Resumen
          </button>
          <button
            onClick={() => setActiveTab('config')}
            className={`pb-3 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'config'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Settings className="inline mr-2" size={16} />
            Configuración
          </button>
          <button
            onClick={() => setActiveTab('events')}
            className={`pb-3 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'events'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Zap className="inline mr-2" size={16} />
            Eventos
          </button>
          <button
            onClick={() => setActiveTab('examples')}
            className={`pb-3 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'examples'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <BookOpen className="inline mr-2" size={16} />
            Ejemplos
          </button>
        </nav>
      </div>

      {/* Content */}
      {activeTab === 'overview' && renderOverview()}
      {activeTab === 'config' && renderConfig()}
      {activeTab === 'events' && renderEvents()}
      {activeTab === 'examples' && renderExamples()}
    </div>
  );
};

export default N8NIntegration;
