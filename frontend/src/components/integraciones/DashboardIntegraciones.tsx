import React, { useEffect, useState } from 'react';
import {
  Activity,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  Server,
  FileText,
  Pill,
  Receipt,
  Building2,
  Microscope,
  AlertCircle,
} from 'lucide-react';
import { obtenerDashboard, DashboardIntegraciones, EstadisticasIntegracion } from '../../services/integracionesService';

interface TarjetaEstadisticas {
  titulo: string;
  icono: React.ReactNode;
  color: string;
  stats?: EstadisticasIntegracion;
}

const DashboardIntegracionesComponent: React.FC = () => {
  const [dashboard, setDashboard] = useState<DashboardIntegraciones | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    cargarDashboard();
    // Actualizar cada 30 segundos
    const interval = setInterval(cargarDashboard, 30000);
    return () => clearInterval(interval);
  }, []);

  const cargarDashboard = async () => {
    try {
      setLoading(true);
      const data = await obtenerDashboard();
      setDashboard(data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar dashboard');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const tarjetas: TarjetaEstadisticas[] = [
    {
      titulo: 'PACS',
      icono: <Server className="h-8 w-8" />,
      color: 'blue',
      stats: dashboard?.pacs,
    },
    {
      titulo: 'LIS',
      icono: <Microscope className="h-8 w-8" />,
      color: 'green',
      stats: dashboard?.lis,
    },
    {
      titulo: 'Receta Electrónica',
      icono: <FileText className="h-8 w-8" />,
      color: 'purple',
      stats: dashboard?.receta_electronica,
    },
    {
      titulo: 'Farmacia',
      icono: <Pill className="h-8 w-8" />,
      color: 'pink',
      stats: dashboard?.farmacia,
    },
    {
      titulo: 'Facturación',
      icono: <Receipt className="h-8 w-8" />,
      color: 'yellow',
      stats: dashboard?.facturacion,
    },
    {
      titulo: 'ERP',
      icono: <Building2 className="h-8 w-8" />,
      color: 'indigo',
      stats: dashboard?.erp,
    },
  ];

  const getColorClasses = (color: string) => {
    const colors: Record<string, { bg: string; text: string; border: string }> = {
      blue: { bg: 'bg-blue-50', text: 'text-blue-600', border: 'border-blue-200' },
      green: { bg: 'bg-green-50', text: 'text-green-600', border: 'border-green-200' },
      purple: { bg: 'bg-purple-50', text: 'text-purple-600', border: 'border-purple-200' },
      pink: { bg: 'bg-pink-50', text: 'text-pink-600', border: 'border-pink-200' },
      yellow: { bg: 'bg-yellow-50', text: 'text-yellow-600', border: 'border-yellow-200' },
      indigo: { bg: 'bg-indigo-50', text: 'text-indigo-600', border: 'border-indigo-200' },
    };
    return colors[color] || colors.blue;
  };

  if (loading && !dashboard) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-50">
            Dashboard de Integraciones
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Monitoreo en tiempo real de sistemas externos
          </p>
        </div>
        <button
          onClick={cargarDashboard}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <Activity className="h-4 w-4" />
          Actualizar
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-medium text-red-900">Error</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Grid de Tarjetas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {tarjetas.map((tarjeta) => {
          const colors = getColorClasses(tarjeta.color);
          const stats = tarjeta.stats;

          return (
            <div
              key={tarjeta.titulo}
              className={`bg-white dark:bg-gray-800 rounded-lg border-2 ${colors.border} p-6 hover:shadow-lg transition-shadow`}
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-lg ${colors.bg}`}>
                  <div className={colors.text}>{tarjeta.icono}</div>
                </div>
                <div className="flex items-center gap-2">
                  {stats?.activo ? (
                    <div className="flex items-center gap-1 text-green-600">
                      <CheckCircle className="h-5 w-5" />
                      <span className="text-sm font-medium">Activo</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-1 text-gray-400">
                      <XCircle className="h-5 w-5" />
                      <span className="text-sm font-medium">Inactivo</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Título */}
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-4">
                {tarjeta.titulo}
              </h3>

              {/* Estadísticas */}
              {stats ? (
                <div className="space-y-3">
                  {/* Operaciones Hoy */}
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      Operaciones hoy
                    </span>
                    <span className="text-lg font-bold text-gray-900 dark:text-gray-50">
                      {stats.operaciones_hoy}
                    </span>
                  </div>

                  {/* Exitosas */}
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-1">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      Exitosas
                    </span>
                    <span className="text-sm font-semibold text-green-600">
                      {stats.operaciones_exitosas_hoy}
                    </span>
                  </div>

                  {/* Fallidas */}
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-1">
                      <XCircle className="h-4 w-4 text-red-500" />
                      Fallidas
                    </span>
                    <span className="text-sm font-semibold text-red-600">
                      {stats.operaciones_fallidas_hoy}
                    </span>
                  </div>

                  {/* Pendientes */}
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-1">
                      <Clock className="h-4 w-4 text-yellow-500" />
                      Pendientes
                    </span>
                    <span className="text-sm font-semibold text-yellow-600">
                      {stats.operaciones_pendientes}
                    </span>
                  </div>

                  {/* Tasa de Éxito */}
                  <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-1">
                        <TrendingUp className="h-4 w-4" />
                        Tasa de éxito
                      </span>
                      <span className="text-lg font-bold text-gray-900 dark:text-gray-50">
                        {stats.tasa_exito.toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          stats.tasa_exito >= 95
                            ? 'bg-green-500'
                            : stats.tasa_exito >= 80
                            ? 'bg-yellow-500'
                            : 'bg-red-500'
                        }`}
                        style={{ width: `${stats.tasa_exito}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Última Sincronización */}
                  {stats.ultima_sincronizacion && (
                    <div className="text-xs text-gray-500 dark:text-gray-400 pt-2">
                      Última sync:{' '}
                      {new Date(stats.ultima_sincronizacion).toLocaleString('es-MX', {
                        day: '2-digit',
                        month: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <p className="text-sm">No configurado</p>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Resumen Global */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-4">
          Resumen Global
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">
              {Object.values(dashboard || {}).reduce(
                (sum, stats) => sum + (stats?.operaciones_hoy || 0),
                0
              )}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Total Operaciones
            </div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">
              {Object.values(dashboard || {}).reduce(
                (sum, stats) => sum + (stats?.operaciones_exitosas_hoy || 0),
                0
              )}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Exitosas
            </div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-red-600">
              {Object.values(dashboard || {}).reduce(
                (sum, stats) => sum + (stats?.operaciones_fallidas_hoy || 0),
                0
              )}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Fallidas
            </div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-yellow-600">
              {Object.values(dashboard || {}).reduce(
                (sum, stats) => sum + (stats?.operaciones_pendientes || 0),
                0
              )}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Pendientes
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardIntegracionesComponent;
