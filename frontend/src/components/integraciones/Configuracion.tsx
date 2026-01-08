import { useState, useEffect } from 'react'
import { Settings, Server, CheckCircle, XCircle, Plus, Edit, Trash2, X } from 'lucide-react'
import * as integracionesService from '@/services/integracionesService'

interface ConfiguracionIntegracion {
  id: string
  nombre: string
  tipo_sistema: string
  descripcion?: string
  url_base: string
  puerto?: number
  protocolo?: string
  tipo_auth?: string
  usuario?: string
  activo: boolean
  fecha_creacion: string
  ultima_sincronizacion?: string
}

export default function Configuracion() {
  const [configuraciones, setConfiguraciones] = useState<ConfiguracionIntegracion[]>([])
  const [cargando, setCargando] = useState(true)
  const [mostrarFormulario, setMostrarFormulario] = useState(false)
  const [configSeleccionada, setConfigSeleccionada] = useState<ConfiguracionIntegracion | null>(null)
  const [guardando, setGuardando] = useState(false)
  
  const [formData, setFormData] = useState({
    nombre: '',
    tipo_sistema: 'PACS',
    descripcion: '',
    url_base: '',
    puerto: 0,
    protocolo: 'HTTPS',
    tipo_auth: 'BASIC',
    usuario: '',
    password: '',
    activo: true
  })

  useEffect(() => {
    cargarConfiguraciones()
  }, [])

  const cargarConfiguraciones = async () => {
    try {
      setCargando(true)
      const data = await integracionesService.listarConfiguraciones()
      setConfiguraciones(data)
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setCargando(false)
    }
  }

  const estadisticas = {
    total: configuraciones.length,
    activas: configuraciones.filter(c => c.activo).length,
    inactivas: configuraciones.filter(c => !c.activo).length,
  }

  const getTipoSistemaBadge = (tipo: string) => {
    const badges: { [key: string]: { color: string; label: string } } = {
      PACS: { color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200', label: 'PACS' },
      LIS: { color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200', label: 'LIS' },
      CFDI: { color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200', label: 'CFDI' },
      ERP: { color: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200', label: 'ERP' },
      RECETA: { color: 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200', label: 'Receta' },
      FARMACIA: { color: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200', label: 'Farmacia' },
    }
    return badges[tipo] || { color: 'bg-gray-100 text-gray-800', label: tipo }
  }

  const handleToggleActivo = async (id: string, activo: boolean) => {
    try {
      await integracionesService.actualizarConfiguracion(id, { activo: !activo })
      cargarConfiguraciones()
    } catch (error) {
      console.error('Error:', error)
    }
  }

  const handleEliminar = async (id: string) => {
    if (!confirm('¿Está seguro de eliminar esta configuración?')) return
    
    try {
      await integracionesService.eliminarConfiguracion(id)
      cargarConfiguraciones()
    } catch (error) {
      console.error('Error:', error)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-50">
            Configuración de Integraciones
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Gestión de conexiones con sistemas externos
          </p>
        </div>
        <button
          onClick={() => {
            setConfigSeleccionada(null)
            setMostrarFormulario(true)
          }}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus className="w-4 h-4" />
          Nueva Configuración
        </button>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Total Configuraciones</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-50">{estadisticas.total}</p>
            </div>
            <Server className="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Activas</p>
              <p className="text-2xl font-bold text-green-600">{estadisticas.activas}</p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Inactivas</p>
              <p className="text-2xl font-bold text-red-600">{estadisticas.inactivas}</p>
            </div>
            <XCircle className="w-8 h-8 text-red-500" />
          </div>
        </div>
      </div>

      {/* Lista de Configuraciones */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        {cargando ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-500">Cargando configuraciones...</p>
          </div>
        ) : configuraciones.length === 0 ? (
          <div className="p-8 text-center">
            <Settings className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No hay configuraciones</p>
            <button
              onClick={() => setMostrarFormulario(true)}
              className="mt-4 text-blue-600 hover:text-blue-800"
            >
              Crear primera configuración
            </button>
          </div>
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {configuraciones.map(config => (
              <div key={config.id} className="p-6 hover:bg-gray-50 dark:hover:bg-gray-900">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                        {config.nombre}
                      </h3>
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${getTipoSistemaBadge(config.tipo_sistema).color}`}>
                        {getTipoSistemaBadge(config.tipo_sistema).label}
                      </span>
                      {config.activo ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                          <CheckCircle className="w-3 h-3" />
                          Activo
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
                          <XCircle className="w-3 h-3" />
                          Inactivo
                        </span>
                      )}
                    </div>
                    
                    {config.descripcion && (
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                        {config.descripcion}
                      </p>
                    )}

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">URL:</span>
                        <span className="ml-2 text-gray-900 dark:text-gray-50 font-mono">
                          {config.url_base}{config.puerto ? `:${config.puerto}` : ''}
                        </span>
                      </div>
                      {config.protocolo && (
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Protocolo:</span>
                          <span className="ml-2 text-gray-900 dark:text-gray-50">
                            {config.protocolo}
                          </span>
                        </div>
                      )}
                      {config.tipo_auth && (
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Autenticación:</span>
                          <span className="ml-2 text-gray-900 dark:text-gray-50">
                            {config.tipo_auth}
                          </span>
                        </div>
                      )}
                      {config.usuario && (
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Usuario:</span>
                          <span className="ml-2 text-gray-900 dark:text-gray-50">
                            {config.usuario}
                          </span>
                        </div>
                      )}
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Creado:</span>
                        <span className="ml-2 text-gray-900 dark:text-gray-50">
                          {new Date(config.fecha_creacion).toLocaleDateString()}
                        </span>
                      </div>
                      {config.ultima_sincronizacion && (
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Última sincronización:</span>
                          <span className="ml-2 text-gray-900 dark:text-gray-50">
                            {new Date(config.ultima_sincronizacion).toLocaleString()}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2 ml-4">
                    <button
                      onClick={() => handleToggleActivo(config.id, config.activo)}
                      className={`p-2 rounded-lg ${
                        config.activo
                          ? 'bg-green-100 text-green-600 hover:bg-green-200 dark:bg-green-900 dark:text-green-200'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300'
                      }`}
                      title={config.activo ? 'Desactivar' : 'Activar'}
                    >
                      {config.activo ? <CheckCircle className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                    </button>
                    <button
                      onClick={() => {
                        setConfigSeleccionada(config)
                        setMostrarFormulario(true)
                      }}
                      className="p-2 rounded-lg bg-blue-100 text-blue-600 hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-200"
                      title="Editar"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleEliminar(config.id)}
                      className="p-2 rounded-lg bg-red-100 text-red-600 hover:bg-red-200 dark:bg-red-900 dark:text-red-200"
                      title="Eliminar"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Formulario */}
      {mostrarFormulario && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-50">
                {configSeleccionada ? 'Editar Configuración' : 'Nueva Configuración'}
              </h3>
              <button
                onClick={() => {
                  setMostrarFormulario(false)
                  setConfigSeleccionada(null)
                  setFormData({
                    nombre: '',
                    tipo_sistema: 'PACS',
                    descripcion: '',
                    url_base: '',
                    puerto: 0,
                    protocolo: 'HTTPS',
                    tipo_auth: 'BASIC',
                    usuario: '',
                    password: '',
                    activo: true
                  })
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <form onSubmit={async (e) => {
              e.preventDefault()
              try {
                setGuardando(true)
                if (configSeleccionada) {
                  await integracionesService.actualizarConfiguracion(configSeleccionada.id, formData)
                } else {
                  await integracionesService.crearConfiguracion(formData)
                }
                setMostrarFormulario(false)
                setConfigSeleccionada(null)
                setFormData({
                  nombre: '',
                  tipo_sistema: 'PACS',
                  descripcion: '',
                  url_base: '',
                  puerto: 0,
                  protocolo: 'HTTPS',
                  tipo_auth: 'BASIC',
                  usuario: '',
                  password: '',
                  activo: true
                })
                cargarConfiguraciones()
              } catch (error) {
                console.error('Error:', error)
                alert('Error al guardar configuración')
              } finally {
                setGuardando(false)
              }
            }} className="space-y-6">
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Nombre *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.nombre}
                    onChange={(e) => setFormData({...formData, nombre: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-50"
                    placeholder="Ej: PACS Principal"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Tipo de Sistema *
                  </label>
                  <select
                    required
                    value={formData.tipo_sistema}
                    onChange={(e) => setFormData({...formData, tipo_sistema: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-50"
                    aria-label="Tipo de sistema"
                  >
                    <option value="PACS">PACS</option>
                    <option value="LIS">LIS</option>
                    <option value="RECETA">Receta Electrónica</option>
                    <option value="FARMACIA">Farmacia</option>
                    <option value="CFDI">CFDI</option>
                    <option value="ERP">ERP</option>
                  </select>
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Descripción
                  </label>
                  <textarea
                    value={formData.descripcion}
                    onChange={(e) => setFormData({...formData, descripcion: e.target.value})}
                    rows={2}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-50"
                    placeholder="Descripción del sistema"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    URL Base *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.url_base}
                    onChange={(e) => setFormData({...formData, url_base: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-50"
                    placeholder="https://api.ejemplo.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Puerto
                  </label>
                  <input
                    type="number"
                    value={formData.puerto}
                    onChange={(e) => setFormData({...formData, puerto: parseInt(e.target.value) || 0})}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-50"
                    placeholder="443"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Protocolo *
                  </label>
                  <select
                    required
                    value={formData.protocolo}
                    onChange={(e) => setFormData({...formData, protocolo: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-50"
                    aria-label="Protocolo"
                  >
                    <option value="HTTPS">HTTPS</option>
                    <option value="HTTP">HTTP</option>
                    <option value="DICOM">DICOM</option>
                    <option value="HL7">HL7</option>
                    <option value="FHIR">FHIR</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Tipo de Autenticación
                  </label>
                  <select
                    value={formData.tipo_auth}
                    onChange={(e) => setFormData({...formData, tipo_auth: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-50"
                    aria-label="Tipo de autenticación"
                  >
                    <option value="BASIC">Basic</option>
                    <option value="BEARER">Bearer Token</option>
                    <option value="OAUTH2">OAuth 2.0</option>
                    <option value="API_KEY">API Key</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Usuario
                  </label>
                  <input
                    type="text"
                    value={formData.usuario}
                    onChange={(e) => setFormData({...formData, usuario: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-50"
                    placeholder="Usuario de acceso"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Contraseña / Token
                  </label>
                  <input
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({...formData, password: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-50"
                    placeholder="Contraseña o token de acceso"
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="activo"
                    checked={formData.activo}
                    onChange={(e) => setFormData({...formData, activo: e.target.checked})}
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                  <label htmlFor="activo" className="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                    Configuración Activa
                  </label>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                <button
                  type="button"
                  onClick={() => {
                    setMostrarFormulario(false)
                    setConfigSeleccionada(null)
                    setFormData({
                      nombre: '',
                      tipo_sistema: 'PACS',
                      descripcion: '',
                      url_base: '',
                      puerto: 0,
                      protocolo: 'HTTPS',
                      tipo_auth: 'BASIC',
                      usuario: '',
                      password: '',
                      activo: true
                    })
                  }}
                  className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={guardando}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {guardando ? 'Guardando...' : (configSeleccionada ? 'Actualizar' : 'Crear Configuración')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
