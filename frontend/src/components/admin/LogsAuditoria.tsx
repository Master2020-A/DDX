import React, { useEffect, useState } from 'react';
import { Activity, Filter, Download, Eye, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import securityService, { AuditLog } from '../../services/securityService';

const LogsAuditoria: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [limit] = useState(50);
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);
  const [showDetailDialog, setShowDetailDialog] = useState(false);
  const [filterExitoso, setFilterExitoso] = useState<'all' | 'success' | 'failed'>('all');

  useEffect(() => {
    cargarLogs();
  }, [page]);

  const cargarLogs = async () => {
    try {
      setLoading(true);
      const response = await securityService.getRecentAuditLogs(limit, page * limit);
      setLogs(response.logs);
      setTotal(response.total);
    } catch (error) {
      console.error('Error al cargar logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleVerDetalle = (log: AuditLog) => {
    setSelectedLog(log);
    setShowDetailDialog(true);
  };

  const logsFiltrados = logs.filter(log => {
    if (filterExitoso === 'success') return log.exitoso;
    if (filterExitoso === 'failed') return !log.exitoso;
    return true;
  });

  const getAccionColor = (accion: string) => {
    switch (accion.toLowerCase()) {
      case 'crear':
      case 'create':
        return 'bg-green-100 text-green-800';
      case 'editar':
      case 'edit':
      case 'actualizar':
        return 'bg-blue-100 text-blue-800';
      case 'eliminar':
      case 'delete':
        return 'bg-red-100 text-red-800';
      case 'ver':
      case 'view':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-purple-100 text-purple-800';
    }
  };

  if (loading && logs.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Logs de Auditoría</h2>
          <p className="text-sm text-gray-500 mt-1">
            {total} registros totales
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={filterExitoso}
            onChange={(e) => setFilterExitoso(e.target.value as any)}
            className="block pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
          >
            <option value="all">Todos</option>
            <option value="success">Exitosos</option>
            <option value="failed">Fallidos</option>
          </select>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total</p>
              <p className="text-2xl font-bold text-gray-900">{logs.length}</p>
            </div>
            <Activity className="h-8 w-8 text-gray-400" />
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Exitosos</p>
              <p className="text-2xl font-bold text-green-600">
                {logs.filter(l => l.exitoso).length}
              </p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-400" />
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Fallidos</p>
              <p className="text-2xl font-bold text-red-600">
                {logs.filter(l => !l.exitoso).length}
              </p>
            </div>
            <XCircle className="h-8 w-8 text-red-400" />
          </div>
        </div>
      </div>

      {/* Logs Table */}
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Estado
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Acción
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Recurso
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Descripción
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                IP / Método
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Fecha
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {logsFiltrados.map((log) => (
              <tr key={log.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  {log.exitoso ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-500" />
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getAccionColor(log.accion)}`}>
                    {log.accion}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{log.recurso}</div>
                  {log.recurso_id && (
                    <div className="text-xs text-gray-500 truncate max-w-xs">
                      ID: {log.recurso_id.substring(0, 8)}...
                    </div>
                  )}
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-900 max-w-md truncate">
                    {log.descripcion || '-'}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{log.ip_address || '-'}</div>
                  <div className="text-xs text-gray-500">{log.metodo_http || '-'}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(log.created_at).toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => handleVerDetalle(log)}
                    className="text-indigo-600 hover:text-indigo-900"
                  >
                    <Eye className="h-4 w-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between bg-white px-4 py-3 sm:px-6 rounded-lg shadow">
        <div className="flex-1 flex justify-between sm:hidden">
          <button
            onClick={() => setPage(Math.max(0, page - 1))}
            disabled={page === 0}
            className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
          >
            Anterior
          </button>
          <button
            onClick={() => setPage(page + 1)}
            disabled={(page + 1) * limit >= total}
            className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
          >
            Siguiente
          </button>
        </div>
        <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
          <div>
            <p className="text-sm text-gray-700">
              Mostrando <span className="font-medium">{page * limit + 1}</span> a{' '}
              <span className="font-medium">{Math.min((page + 1) * limit, total)}</span> de{' '}
              <span className="font-medium">{total}</span> resultados
            </p>
          </div>
          <div>
            <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
              <button
                onClick={() => setPage(Math.max(0, page - 1))}
                disabled={page === 0}
                className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
              >
                Anterior
              </button>
              <button
                onClick={() => setPage(page + 1)}
                disabled={(page + 1) * limit >= total}
                className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
              >
                Siguiente
              </button>
            </nav>
          </div>
        </div>
      </div>

      {/* Detail Dialog */}
      {showDetailDialog && selectedLog && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">
                  Detalle del Log de Auditoría
                </h3>
                <button
                  onClick={() => setShowDetailDialog(false)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  ✕
                </button>
              </div>
            </div>

            <div className="px-6 py-4 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Estado</label>
                  <div className="mt-1 flex items-center">
                    {selectedLog.exitoso ? (
                      <>
                        <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                        <span className="text-green-700">Exitoso</span>
                      </>
                    ) : (
                      <>
                        <XCircle className="h-5 w-5 text-red-500 mr-2" />
                        <span className="text-red-700">Fallido</span>
                      </>
                    )}
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Código Estado</label>
                  <div className="mt-1 text-sm text-gray-900">{selectedLog.codigo_estado || '-'}</div>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-500">Acción</label>
                <div className="mt-1">
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getAccionColor(selectedLog.accion)}`}>
                    {selectedLog.accion}
                  </span>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-500">Recurso</label>
                <div className="mt-1 text-sm text-gray-900">{selectedLog.recurso}</div>
                {selectedLog.recurso_id && (
                  <div className="text-xs text-gray-500 mt-1">ID: {selectedLog.recurso_id}</div>
                )}
              </div>

              <div>
                <label className="text-sm font-medium text-gray-500">Descripción</label>
                <div className="mt-1 text-sm text-gray-900">{selectedLog.descripcion || '-'}</div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">IP Address</label>
                  <div className="mt-1 text-sm text-gray-900">{selectedLog.ip_address || '-'}</div>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Método HTTP</label>
                  <div className="mt-1 text-sm text-gray-900">{selectedLog.metodo_http || '-'}</div>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-500">Endpoint</label>
                <div className="mt-1 text-sm text-gray-900 font-mono bg-gray-50 p-2 rounded">
                  {selectedLog.endpoint || '-'}
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-500">User Agent</label>
                <div className="mt-1 text-xs text-gray-900 bg-gray-50 p-2 rounded break-all">
                  {selectedLog.user_agent || '-'}
                </div>
              </div>

              {selectedLog.mensaje_error && (
                <div>
                  <label className="text-sm font-medium text-red-500">Mensaje de Error</label>
                  <div className="mt-1 text-sm text-red-700 bg-red-50 p-3 rounded">
                    {selectedLog.mensaje_error}
                  </div>
                </div>
              )}

              {selectedLog.datos_anteriores && (
                <div>
                  <label className="text-sm font-medium text-gray-500">Datos Anteriores</label>
                  <pre className="mt-1 text-xs text-gray-900 bg-gray-50 p-3 rounded overflow-x-auto">
                    {JSON.stringify(selectedLog.datos_anteriores, null, 2)}
                  </pre>
                </div>
              )}

              {selectedLog.datos_nuevos && (
                <div>
                  <label className="text-sm font-medium text-gray-500">Datos Nuevos</label>
                  <pre className="mt-1 text-xs text-gray-900 bg-gray-50 p-3 rounded overflow-x-auto">
                    {JSON.stringify(selectedLog.datos_nuevos, null, 2)}
                  </pre>
                </div>
              )}

              <div>
                <label className="text-sm font-medium text-gray-500">Fecha y Hora</label>
                <div className="mt-1 text-sm text-gray-900">
                  {new Date(selectedLog.created_at).toLocaleString()}
                </div>
              </div>
            </div>

            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
              <button
                onClick={() => setShowDetailDialog(false)}
                className="w-full inline-flex justify-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LogsAuditoria;
