import { useState, useEffect } from 'react'
import { FileText, CheckCircle, XCircle, AlertCircle, Search, Filter, Download } from 'lucide-react'
import * as integracionesService from '@/services/integracionesService'

interface LogIntegracion {
  id: string
  tipo_sistema: string
  operacion: string
  estado: string
  request_data?: any
  response_data?: any
  error_mensaje?: string
  duracion_ms?: number
  fecha_operacion: string
  usuario_nombre?: string
}

export default function Logs() {
  const [logs, setLogs] = useState<LogIntegracion[]>([])
  const [filtroTipo, setFiltroTipo] = useState<string>('TODOS')
  const [filtroEstado, setFiltroEstado] = useState<string>('TODOS')
  const [cargando, setCargando] = useState(true)
  const [logSeleccionado, setLogSeleccionado] = useState<LogIntegracion | null>(null)

  useEffect(() => {
    cargarLogs()
  }, [])

  const cargarLogs = async () => {
    try {
      setCargando(true)
      const data = await integracionesService.listarLogs()
      setLogs(data)
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setCargando(false)
    }
  }

  const logsFiltrados = logs.filter(log => {
    const cumpleTipo = filtroTipo === 'TODOS' || log.tipo_sistema === filtroTipo
    const cumpleEstado = filtroEstado === 'TODOS' || log.estado === filtroEstado
    return cumpleTipo && cumpleEstado
  })

  const estadisticas = {
    total: logs.length,
    exitosos: logs.filter(l => l.estado === 'EXITOSO').length,
    fallidos: logs.filter(l => l.estado === 'ERROR').length,
    advertencias: logs.filter(l => l.estado === 'ADVERTENCIA').length,
  }

  const getEstadoBadge = (estado: string) => {
    const badges = {
      EXITOSO: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      ERROR: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      ADVERTENCIA: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    }
    return badges[estado as keyof typeof badges] || 'bg-gray-100 text-gray-800'
  }

  const getEstadoIcon = (estado: string) => {
    switch (estado) {
      case 'EXITOSO':
        return <CheckCircle className="w-4 h-4" />
      case 'ERROR':
        return <XCircle className="w-4 h-4" />
      case 'ADVERTENCIA':
        return <AlertCircle className="w-4 h-4" />
      default:
        return <FileText className="w-4 h-4" />
    }
  }

  const getTipoSistemaBadge = (tipo: string) => {
    const badges: { [key: string]: string } = {
      PACS: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      LIS: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      RECETA: 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200',
      FARMACIA: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
      CFDI: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      ERP: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    }
    return badges[tipo] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-50">
            Logs de Integración
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Historial de operaciones y errores
          </p>
        </div>
        <button
          onClick={cargarLogs}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Download className="w-4 h-4" />
          Actualizar
        </button>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Total Operaciones</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-50">{estadisticas.total}</p>
            </div>
            <FileText className="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Exitosas</p>
              <p className="text-2xl font-bold text-green-600">{estadisticas.exitosos}</p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Fallidas</p>
              <p className="text-2xl font-bold text-red-600">{estadisticas.fallidos}</p>
            </div>
            <XCircle className="w-8 h-8 text-red-500" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Advertencias</p>
              <p className="text-2xl font-bold text-yellow-600">{estadisticas.advertencias}</p>
            </div>
            <AlertCircle className="w-8 h-8 text-yellow-500" />
          </div>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-4 flex-wrap">
          <Filter className="w-5 h-5 text-gray-400" />
          
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">Sistema:</span>
            <select
              value={filtroTipo}
              onChange={(e) => setFiltroTipo(e.target.value)}
              className="px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm"
              aria-label="Filtrar por tipo de sistema"
            >
              <option value="TODOS">Todos</option>
              <option value="PACS">PACS</option>
              <option value="LIS">LIS</option>
              <option value="RECETA">Receta</option>
              <option value="FARMACIA">Farmacia</option>
              <option value="CFDI">CFDI</option>
              <option value="ERP">ERP</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">Estado:</span>
            <select
              value={filtroEstado}
              onChange={(e) => setFiltroEstado(e.target.value)}
              className="px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm"
              aria-label="Filtrar por estado"
            >
              <option value="TODOS">Todos</option>
              <option value="EXITOSO">Exitoso</option>
              <option value="ERROR">Error</option>
              <option value="ADVERTENCIA">Advertencia</option>
            </select>
          </div>
        </div>
      </div>

      {/* Lista de Logs */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        {cargando ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-500">Cargando logs...</p>
          </div>
        ) : logsFiltrados.length === 0 ? (
          <div className="p-8 text-center">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No hay logs disponibles</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-900">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Fecha/Hora
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Sistema
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Operación
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Usuario
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Duración
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Estado
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {logsFiltrados.map(log => (
                  <tr key={log.id} className="hover:bg-gray-50 dark:hover:bg-gray-900">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-50">
                      {new Date(log.fecha_operacion).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${getTipoSistemaBadge(log.tipo_sistema)}`}>
                        {log.tipo_sistema}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900 dark:text-gray-50">
                      {log.operacion}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {log.usuario_nombre || 'Sistema'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {log.duracion_ms ? `${log.duracion_ms}ms` : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getEstadoBadge(log.estado)}`}>
                        {getEstadoIcon(log.estado)}
                        {log.estado}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <button
                        onClick={() => setLogSeleccionado(log)}
                        className="text-blue-600 hover:text-blue-800 dark:text-blue-400"
                      >
                        Ver detalles
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal de Detalles */}
      {logSeleccionado && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                  Detalles del Log
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {new Date(logSeleccionado.fecha_operacion).toLocaleString()}
                </p>
              </div>
              <button
                onClick={() => setLogSeleccionado(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Sistema</label>
                  <p className="text-gray-900 dark:text-gray-50">{logSeleccionado.tipo_sistema}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Operación</label>
                  <p className="text-gray-900 dark:text-gray-50">{logSeleccionado.operacion}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Estado</label>
                  <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getEstadoBadge(logSeleccionado.estado)}`}>
                    {getEstadoIcon(logSeleccionado.estado)}
                    {logSeleccionado.estado}
                  </span>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Duración</label>
                  <p className="text-gray-900 dark:text-gray-50">
                    {logSeleccionado.duracion_ms ? `${logSeleccionado.duracion_ms}ms` : 'N/A'}
                  </p>
                </div>
              </div>

              {logSeleccionado.error_mensaje && (
                <div>
                  <label className="text-sm font-medium text-red-600 dark:text-red-400">Error</label>
                  <div className="mt-1 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                    <p className="text-sm text-red-900 dark:text-red-200 font-mono">
                      {logSeleccionado.error_mensaje}
                    </p>
                  </div>
                </div>
              )}

              {logSeleccionado.request_data && (
                <div>
                  <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Request Data</label>
                  <pre className="mt-1 p-3 bg-gray-50 dark:bg-gray-900 rounded-lg text-xs overflow-x-auto">
                    {JSON.stringify(logSeleccionado.request_data, null, 2)}
                  </pre>
                </div>
              )}

              {logSeleccionado.response_data && (
                <div>
                  <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Response Data</label>
                  <pre className="mt-1 p-3 bg-gray-50 dark:bg-gray-900 rounded-lg text-xs overflow-x-auto">
                    {JSON.stringify(logSeleccionado.response_data, null, 2)}
                  </pre>
                </div>
              )}
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setLogSeleccionado(null)}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
