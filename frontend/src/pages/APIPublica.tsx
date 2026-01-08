import React, { useState, useEffect } from 'react';
import {
  Key,
  Webhook,
  Package,
  BarChart3,
  FileText,
  Copy,
  Eye,
  EyeOff,
  Plus,
  Trash2,
  RefreshCw,
  CheckCircle,
  XCircle,
  Download,
  ExternalLink,
  Code,
} from 'lucide-react';
import * as apiPublicaService from '../services/apiPublicaService';

interface APIKey {
  id: string;
  nombre: string;
  descripcion?: string;
  key: string;
  secret?: string;
  permisos: string[];
  scopes: string[];
  rate_limit_por_minuto: number;
  rate_limit_por_dia: number;
  activa: boolean;
  created_at: string;
  ultimo_uso?: string;
  total_requests: number;
}

interface Webhook {
  id: string;
  nombre: string;
  url: string;
  secret: string;
  eventos: string[];
  activo: boolean;
  total_envios: number;
  total_errores: number;
}

interface Plugin {
  id: string;
  nombre: string;
  slug: string;
  descripcion: string;
  autor: string;
  version: string;
  categoria: string;
  descargas: number;
  calificacion_promedio: number;
  verificado: boolean;
  url_icono?: string;
}

export default function APIPublica() {
  const [tabActiva, setTabActiva] = useState<'keys' | 'webhooks' | 'marketplace' | 'docs'>('keys');
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [webhooks, setWebhooks] = useState<Webhook[]>([]);
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [mostrarSecret, setMostrarSecret] = useState<{ [key: string]: boolean }>({});
  const [mostrarFormularioKey, setMostrarFormularioKey] = useState(false);
  const [mostrarFormularioWebhook, setMostrarFormularioWebhook] = useState(false);

  const [formKey, setFormKey] = useState({
    nombre: '',
    descripcion: '',
    scopes: [] as string[],
    rate_limit_por_minuto: 60,
    rate_limit_por_dia: 10000,
  });

  const [formWebhook, setFormWebhook] = useState({
    nombre: '',
    url: '',
    eventos: [] as string[],
  });

  const eventosDisponibles = [
    'paciente.creado',
    'paciente.actualizado',
    'consulta.creada',
    'consulta.finalizada',
    'laboratorio.creado',
    'laboratorio.completado',
    'factura.generada',
    'factura.timbrada',
  ];

  const scopesDisponibles = [
    { id: 'pacientes:read', nombre: 'Leer Pacientes' },
    { id: 'pacientes:write', nombre: 'Escribir Pacientes' },
    { id: 'consultas:read', nombre: 'Leer Consultas' },
    { id: 'consultas:write', nombre: 'Escribir Consultas' },
    { id: 'laboratorio:read', nombre: 'Leer Laboratorios' },
    { id: 'laboratorio:write', nombre: 'Escribir Laboratorios' },
    { id: 'facturacion:read', nombre: 'Leer Facturas' },
    { id: 'facturacion:write', nombre: 'Escribir Facturas' },
  ];

  useEffect(() => {
    cargarDatos();
  }, [tabActiva]);

  const cargarDatos = async () => {
    try {
      if (tabActiva === 'keys') {
        const keys = await apiPublicaService.listarAPIKeys();
        setApiKeys(keys);
      } else if (tabActiva === 'webhooks') {
        const hooks = await apiPublicaService.listarWebhooks();
        setWebhooks(hooks);
      } else if (tabActiva === 'marketplace') {
        const pluginsList = await apiPublicaService.listarPlugins();
        setPlugins(pluginsList);
      }
    } catch (error: any) {
      console.error('Error al cargar datos:', error);
      // No mostrar alerta si es solo que no hay datos
      if (error.response?.status !== 404) {
        console.warn('Error al cargar datos de API Pública:', error.message);
      }
    }
  };

  const crearAPIKey = async () => {
    try {
      const nuevaKey = await apiPublicaService.crearAPIKey(formKey);
      alert(`API Key creada exitosamente!\n\nKey: ${nuevaKey.key}\nSecret: ${nuevaKey.secret}\n\n⚠️ Guarda el secret ahora, no se mostrará de nuevo.`);
      setMostrarFormularioKey(false);
      setFormKey({
        nombre: '',
        descripcion: '',
        scopes: [],
        rate_limit_por_minuto: 60,
        rate_limit_por_dia: 10000,
      });
      cargarDatos();
    } catch (error: any) {
      console.error('Error al crear API Key:', error);
      let errorMessage = 'Error desconocido';
      
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        } else if (Array.isArray(error.response.data.detail)) {
          errorMessage = error.response.data.detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
        } else {
          errorMessage = JSON.stringify(error.response.data.detail);
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      alert(`Error al crear API Key:\n${errorMessage}`);
    }
  };

  const regenerarSecret = async (keyId: string) => {
    if (confirm('¿Estás seguro? Esto invalidará el secret actual.')) {
      try {
        const keyActualizada = await apiPublicaService.regenerarSecret(keyId);
        alert(`Secret regenerado exitosamente!\n\nNuevo Secret: ${keyActualizada.secret}\n\n⚠️ Guarda el secret ahora, no se mostrará de nuevo.`);
        cargarDatos();
      } catch (error: any) {
        console.error('Error al regenerar secret:', error);
        let errorMessage = 'Error desconocido';
        
        if (error.response?.data?.detail) {
          if (typeof error.response.data.detail === 'string') {
            errorMessage = error.response.data.detail;
          } else if (Array.isArray(error.response.data.detail)) {
            errorMessage = error.response.data.detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
          } else {
            errorMessage = JSON.stringify(error.response.data.detail);
          }
        } else if (error.message) {
          errorMessage = error.message;
        }
        
        alert(`Error al regenerar secret:\n${errorMessage}`);
      }
    }
  };

  const eliminarAPIKey = async (keyId: string) => {
    if (confirm('¿Estás seguro de eliminar esta API Key?')) {
      try {
        await apiPublicaService.eliminarAPIKey(keyId);
        alert('API Key eliminada exitosamente');
        cargarDatos();
      } catch (error: any) {
        console.error('Error al eliminar API Key:', error);
        let errorMessage = 'Error desconocido';
        
        if (error.response?.data?.detail) {
          if (typeof error.response.data.detail === 'string') {
            errorMessage = error.response.data.detail;
          } else if (Array.isArray(error.response.data.detail)) {
            errorMessage = error.response.data.detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
          } else {
            errorMessage = JSON.stringify(error.response.data.detail);
          }
        } else if (error.message) {
          errorMessage = error.message;
        }
        
        alert(`Error al eliminar API Key:\n${errorMessage}`);
      }
    }
  };

  const toggleSecret = (keyId: string) => {
    setMostrarSecret(prev => ({ ...prev, [keyId]: !prev[keyId] }));
  };

  const copiarAlPortapapeles = (texto: string) => {
    navigator.clipboard.writeText(texto);
    alert('Copiado al portapapeles');
  };

  const crearWebhook = async () => {
    try {
      const nuevoWebhook = await apiPublicaService.crearWebhook(formWebhook);
      alert(`Webhook creado exitosamente!\n\nSecret: ${nuevoWebhook.secret}\n\n⚠️ Guarda el secret para verificar las firmas.`);
      setMostrarFormularioWebhook(false);
      setFormWebhook({
        nombre: '',
        url: '',
        eventos: [],
      });
      cargarDatos();
    } catch (error: any) {
      console.error('Error al crear webhook:', error);
      let errorMessage = 'Error desconocido';
      
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        } else if (Array.isArray(error.response.data.detail)) {
          errorMessage = error.response.data.detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
        } else {
          errorMessage = JSON.stringify(error.response.data.detail);
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      alert(`Error al crear webhook:\n${errorMessage}`);
    }
  };

  const eliminarWebhook = async (webhookId: string) => {
    if (confirm('¿Estás seguro de eliminar este webhook?')) {
      try {
        await apiPublicaService.eliminarWebhook(webhookId);
        alert('Webhook eliminado exitosamente');
        cargarDatos();
      } catch (error: any) {
        console.error('Error al eliminar webhook:', error);
        let errorMessage = 'Error desconocido';
        
        if (error.response?.data?.detail) {
          if (typeof error.response.data.detail === 'string') {
            errorMessage = error.response.data.detail;
          } else if (Array.isArray(error.response.data.detail)) {
            errorMessage = error.response.data.detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
          } else {
            errorMessage = JSON.stringify(error.response.data.detail);
          }
        } else if (error.message) {
          errorMessage = error.message;
        }
        
        alert(`Error al eliminar webhook:\n${errorMessage}`);
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-50">
          API Pública
        </h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Gestiona API Keys, Webhooks y Plugins del Marketplace
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'keys', nombre: 'API Keys', icono: Key },
            { id: 'webhooks', nombre: 'Webhooks', icono: Webhook },
            { id: 'marketplace', nombre: 'Marketplace', icono: Package },
            { id: 'docs', nombre: 'Documentación', icono: FileText },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setTabActiva(tab.id as any)}
              className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm ${
                tabActiva === tab.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icono className="w-5 h-5" />
              {tab.nombre}
            </button>
          ))}
        </nav>
      </div>

      {/* Contenido de API Keys */}
      {tabActiva === 'keys' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Tus API Keys</h3>
            <button
              onClick={() => setMostrarFormularioKey(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Plus className="w-4 h-4" />
              Nueva API Key
            </button>
          </div>

          {/* Lista de API Keys */}
          <div className="space-y-4">
            {apiKeys.map(key => (
              <div
                key={key.id}
                className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                      {key.nombre}
                    </h4>
                    {key.descripcion && (
                      <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        {key.descripcion}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        key.activa
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                      }`}
                    >
                      {key.activa ? 'Activa' : 'Inactiva'}
                    </span>
                  </div>
                </div>

                {/* API Key */}
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      API Key
                    </label>
                    <div className="flex items-center gap-2">
                      <code className="flex-1 px-3 py-2 bg-gray-100 dark:bg-gray-900 rounded font-mono text-sm">
                        {key.key}
                      </code>
                      <button
                        onClick={() => copiarAlPortapapeles(key.key)}
                        className="p-2 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {key.secret && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Secret (solo se muestra una vez)
                      </label>
                      <div className="flex items-center gap-2">
                        <code className="flex-1 px-3 py-2 bg-gray-100 dark:bg-gray-900 rounded font-mono text-sm">
                          {mostrarSecret[key.id] ? key.secret : '••••••••••••••••'}
                        </code>
                        <button
                          onClick={() => toggleSecret(key.id)}
                          className="p-2 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100"
                        >
                          {mostrarSecret[key.id] ? (
                            <EyeOff className="w-4 h-4" />
                          ) : (
                            <Eye className="w-4 h-4" />
                          )}
                        </button>
                        <button
                          onClick={() => copiarAlPortapapeles(key.secret!)}
                          className="p-2 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Scopes */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Permisos
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {key.scopes.map(scope => (
                        <span
                          key={scope}
                          className="px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded text-xs"
                        >
                          {scope}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Estadísticas */}
                  <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Total Requests</p>
                      <p className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                        {key.total_requests.toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Rate Limit/min</p>
                      <p className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                        {key.rate_limit_por_minuto}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Rate Limit/día</p>
                      <p className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                        {key.rate_limit_por_dia.toLocaleString()}
                      </p>
                    </div>
                  </div>

                  {/* Acciones */}
                  <div className="flex gap-2 pt-4">
                    <button
                      onClick={() => regenerarSecret(key.id)}
                      className="flex items-center gap-2 px-3 py-2 text-sm bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 rounded hover:bg-yellow-200 dark:hover:bg-yellow-800"
                    >
                      <RefreshCw className="w-4 h-4" />
                      Regenerar Secret
                    </button>
                    <button
                      onClick={() => eliminarAPIKey(key.id)}
                      className="flex items-center gap-2 px-3 py-2 text-sm bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 rounded hover:bg-red-200 dark:hover:bg-red-800"
                    >
                      <Trash2 className="w-4 h-4" />
                      Eliminar
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Formulario Nueva API Key */}
          {mostrarFormularioKey && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
              <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full">
                <h3 className="text-xl font-semibold mb-4">Nueva API Key</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Nombre *</label>
                    <input
                      type="text"
                      value={formKey.nombre}
                      onChange={e => setFormKey({ ...formKey, nombre: e.target.value })}
                      className="w-full px-3 py-2 border rounded-lg"
                      placeholder="Mi API Key"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Descripción</label>
                    <textarea
                      value={formKey.descripcion}
                      onChange={e => setFormKey({ ...formKey, descripcion: e.target.value })}
                      className="w-full px-3 py-2 border rounded-lg"
                      rows={3}
                      placeholder="Para qué se usará esta API Key"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Permisos</label>
                    <div className="grid grid-cols-2 gap-2">
                      {scopesDisponibles.map(scope => (
                        <label key={scope.id} className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={formKey.scopes.includes(scope.id)}
                            onChange={e => {
                              if (e.target.checked) {
                                setFormKey({
                                  ...formKey,
                                  scopes: [...formKey.scopes, scope.id],
                                });
                              } else {
                                setFormKey({
                                  ...formKey,
                                  scopes: formKey.scopes.filter(s => s !== scope.id),
                                });
                              }
                            }}
                            className="rounded"
                          />
                          <span className="text-sm">{scope.nombre}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                  <div className="flex justify-end gap-2 pt-4">
                    <button
                      onClick={() => setMostrarFormularioKey(false)}
                      className="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg"
                    >
                      Cancelar
                    </button>
                    <button
                      onClick={crearAPIKey}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      Crear API Key
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Contenido de Webhooks */}
      {tabActiva === 'webhooks' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Tus Webhooks</h3>
            <button
              onClick={() => setMostrarFormularioWebhook(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Plus className="w-4 h-4" />
              Nuevo Webhook
            </button>
          </div>

          {/* Lista de Webhooks */}
          <div className="space-y-4">
            {webhooks.map(webhook => (
              <div
                key={webhook.id}
                className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                      {webhook.nombre}
                    </h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                      {webhook.url}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        webhook.activo
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                      }`}
                    >
                      {webhook.activo ? 'Activo' : 'Inactivo'}
                    </span>
                  </div>
                </div>

                <div className="space-y-2 text-sm">
                  <div>
                    <span className="font-medium">Eventos:</span>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {webhook.eventos.map(evento => (
                        <span
                          key={evento}
                          className="px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded text-xs"
                        >
                          {evento}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 pt-2">
                    <div>
                      <span className="text-gray-500">Total Envíos:</span>
                      <span className="ml-2 font-medium">{webhook.total_envios}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Errores:</span>
                      <span className="ml-2 font-medium text-red-600">{webhook.total_errores}</span>
                    </div>
                  </div>
                </div>

                <div className="flex gap-2 pt-4">
                  <button
                    onClick={() => eliminarWebhook(webhook.id)}
                    className="flex items-center gap-2 px-3 py-2 text-sm bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 rounded hover:bg-red-200 dark:hover:bg-red-800"
                  >
                    <Trash2 className="w-4 h-4" />
                    Eliminar
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Formulario Nuevo Webhook */}
          {mostrarFormularioWebhook && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
              <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full">
                <h3 className="text-xl font-semibold mb-4">Nuevo Webhook</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Nombre *</label>
                    <input
                      type="text"
                      value={formWebhook.nombre}
                      onChange={e => setFormWebhook({ ...formWebhook, nombre: e.target.value })}
                      className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                      placeholder="Mi Webhook"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">URL *</label>
                    <input
                      type="url"
                      value={formWebhook.url}
                      onChange={e => setFormWebhook({ ...formWebhook, url: e.target.value })}
                      className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                      placeholder="https://tu-servidor.com/webhook"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Eventos</label>
                    <div className="grid grid-cols-2 gap-2">
                      {eventosDisponibles.map(evento => (
                        <label key={evento} className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={formWebhook.eventos.includes(evento)}
                            onChange={e => {
                              if (e.target.checked) {
                                setFormWebhook({
                                  ...formWebhook,
                                  eventos: [...formWebhook.eventos, evento],
                                });
                              } else {
                                setFormWebhook({
                                  ...formWebhook,
                                  eventos: formWebhook.eventos.filter(ev => ev !== evento),
                                });
                              }
                            }}
                            className="rounded"
                          />
                          <span className="text-sm">{evento}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                  <div className="flex justify-end gap-2 pt-4">
                    <button
                      onClick={() => setMostrarFormularioWebhook(false)}
                      className="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg"
                    >
                      Cancelar
                    </button>
                    <button
                      onClick={crearWebhook}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      Crear Webhook
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Contenido de Marketplace */}
      {tabActiva === 'marketplace' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {plugins.map(plugin => (
              <div
                key={plugin.id}
                className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
              >
                <div className="flex items-start gap-4 mb-4">
                  {plugin.url_icono ? (
                    <img src={plugin.url_icono} alt={plugin.nombre} className="w-12 h-12 rounded" />
                  ) : (
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded flex items-center justify-center">
                      <Package className="w-6 h-6 text-white" />
                    </div>
                  )}
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900 dark:text-gray-50">
                      {plugin.nombre}
                    </h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      por {plugin.autor}
                    </p>
                  </div>
                  {plugin.verificado && (
                    <CheckCircle className="w-5 h-5 text-blue-500" />
                  )}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  {plugin.descripcion}
                </p>
                <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 mb-4">
                  <span>⭐ {plugin.calificacion_promedio}/5</span>
                  <span>📥 {plugin.descargas.toLocaleString()}</span>
                  <span>v{plugin.version}</span>
                </div>
                <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                  Instalar
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Contenido de Documentación */}
      {tabActiva === 'docs' && (
        <div className="space-y-6">
          {/* Introducción */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-xl font-semibold mb-4">📚 Documentación de la API de DDX</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              La API de DDX te permite integrar tu sistema médico con aplicaciones externas, 
              automatizar procesos y crear extensiones personalizadas.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <a
                href="http://localhost:8612/docs"
                target="_blank"
                className="flex items-center gap-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <Code className="w-5 h-5" />
                <div className="flex-1">
                  <div className="font-semibold">Swagger UI</div>
                  <div className="text-xs opacity-90">Documentación interactiva</div>
                </div>
                <ExternalLink className="w-4 h-4" />
              </a>
              <a
                href="http://localhost:8612/redoc"
                target="_blank"
                className="flex items-center gap-2 px-4 py-3 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600"
              >
                <FileText className="w-5 h-5" />
                <div className="flex-1">
                  <div className="font-semibold">ReDoc</div>
                  <div className="text-xs opacity-90">Documentación detallada</div>
                </div>
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>
          </div>

          {/* Autenticación */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h4 className="text-lg font-semibold mb-3">🔐 Autenticación</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Todas las peticiones a la API requieren una API Key y Secret en los headers:
            </p>
            <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
              <pre className="text-green-400 text-sm">
{`curl -X GET "http://localhost:8612/api/pacientes" \\
  -H "X-API-Key: ddx_tu_api_key_aqui" \\
  -H "X-API-Secret: tu_secret_aqui"`}
              </pre>
            </div>
          </div>

          {/* Endpoints Principales */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h4 className="text-lg font-semibold mb-4">🎯 Endpoints Principales</h4>
            <div className="space-y-4">
              {[
                {
                  metodo: 'GET',
                  endpoint: '/api/pacientes',
                  descripcion: 'Listar todos los pacientes',
                  color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                },
                {
                  metodo: 'POST',
                  endpoint: '/api/pacientes',
                  descripcion: 'Crear un nuevo paciente',
                  color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                },
                {
                  metodo: 'GET',
                  endpoint: '/api/consultas',
                  descripcion: 'Listar consultas',
                  color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                },
                {
                  metodo: 'POST',
                  endpoint: '/api/consultas',
                  descripcion: 'Crear una consulta',
                  color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                },
                {
                  metodo: 'GET',
                  endpoint: '/api/laboratorio/{paciente_id}',
                  descripcion: 'Obtener resultados de laboratorio',
                  color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                },
                {
                  metodo: 'POST',
                  endpoint: '/api/integraciones/factura',
                  descripcion: 'Generar factura electrónica',
                  color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                },
              ].map((item, idx) => (
                <div key={idx} className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-900 rounded">
                  <span className={`px-2 py-1 rounded text-xs font-mono ${item.color}`}>
                    {item.metodo}
                  </span>
                  <code className="text-sm font-mono flex-1">{item.endpoint}</code>
                  <span className="text-xs text-gray-500">{item.descripcion}</span>
                </div>
              ))}
            </div>
          </div>

          {/* SDK JavaScript/TypeScript */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h4 className="text-lg font-semibold mb-3">📦 SDK de JavaScript/TypeScript</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Instala el SDK oficial para integrar DDX en tus aplicaciones JavaScript o TypeScript:
            </p>
            <div className="bg-gray-900 rounded-lg p-4 mb-4">
              <code className="text-green-400 text-sm">npm install @ddx/sdk</code>
            </div>
            
            <h5 className="font-semibold mb-2 text-sm">Ejemplo Básico:</h5>
            <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto mb-4">
              <pre className="text-green-400 text-sm">
{`import DDXClient from '@ddx/sdk';

const ddx = new DDXClient({
  apiKey: 'ddx_tu_api_key',
  apiSecret: 'tu_secret',
  baseURL: 'http://localhost:8612'
});

// Listar pacientes
const pacientes = await ddx.pacientes.listar();
console.log(pacientes);

// Crear paciente
const nuevoPaciente = await ddx.pacientes.crear({
  nombre: 'Juan',
  apellido_paterno: 'Pérez',
  fecha_nacimiento: '1990-05-15',
  genero: 'M'
});`}
              </pre>
            </div>

            <h5 className="font-semibold mb-2 text-sm">Ejemplo con Consultas:</h5>
            <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto mb-4">
              <pre className="text-green-400 text-sm">
{`// Crear consulta
const consulta = await ddx.consultas.crear({
  paciente_id: 'uuid-del-paciente',
  motivo: 'Chequeo general',
  sintomas: 'Dolor de cabeza',
  diagnostico: 'Cefalea tensional'
});

// Listar consultas de un paciente
const consultas = await ddx.consultas.listar({
  paciente_id: 'uuid-del-paciente'
});`}
              </pre>
            </div>

            <h5 className="font-semibold mb-2 text-sm">Ejemplo con Webhooks:</h5>
            <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
              <pre className="text-green-400 text-sm">
{`// Verificar firma de webhook
const crypto = require('crypto');

function verificarWebhook(payload, signature, secret) {
  const hash = crypto
    .createHmac('sha256', secret)
    .update(JSON.stringify(payload))
    .digest('hex');
  
  return hash === signature;
}

// En tu servidor Express
app.post('/webhook', (req, res) => {
  const signature = req.headers['x-webhook-signature'];
  const isValid = verificarWebhook(
    req.body, 
    signature, 
    'tu_webhook_secret'
  );
  
  if (isValid) {
    console.log('Evento:', req.body.evento);
    console.log('Datos:', req.body.datos);
    res.status(200).send('OK');
  } else {
    res.status(401).send('Invalid signature');
  }
});`}
              </pre>
            </div>
          </div>

          {/* Rate Limits y Mejores Prácticas */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h4 className="text-lg font-semibold mb-3">⚡ Rate Limits y Mejores Prácticas</h4>
            <div className="space-y-3 text-sm">
              <div className="flex items-start gap-2">
                <span className="text-blue-500">•</span>
                <div>
                  <strong>Rate Limits:</strong> Por defecto 60 requests/minuto y 10,000/día
                </div>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-blue-500">•</span>
                <div>
                  <strong>Caché:</strong> Implementa caché local para reducir llamadas repetitivas
                </div>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-blue-500">•</span>
                <div>
                  <strong>Webhooks:</strong> Usa webhooks en lugar de polling para eventos en tiempo real
                </div>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-blue-500">•</span>
                <div>
                  <strong>Seguridad:</strong> Nunca expongas tu API Secret en el frontend
                </div>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-blue-500">•</span>
                <div>
                  <strong>Scopes:</strong> Solicita solo los permisos que necesitas
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
