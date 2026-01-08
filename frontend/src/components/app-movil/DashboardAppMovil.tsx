import { useState, useEffect } from 'react';
import { Smartphone, Bell, FileText, Calendar, TrendingUp, Wifi } from 'lucide-react';
import appMovilService, { EstadisticasAppMovil } from '../../services/appMovilService';

const DashboardAppMovil = () => {
  const [estadisticas, setEstadisticas] = useState<EstadisticasAppMovil | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    cargarEstadisticas();
  }, []);

  const cargarEstadisticas = async () => {
    try {
      setLoading(true);
      const data = await appMovilService.obtenerEstadisticas();
      setEstadisticas(data);
    } catch (error) {
      console.error('Error al cargar estadísticas:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
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
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-50">
          Dashboard de Aplicación Móvil
        </h2>
        <button
          onClick={cargarEstadisticas}
          className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400"
        >
          🔄 Actualizar
        </button>
      </div>

      {estadisticas && (
        <>
          {/* Estadísticas de Dispositivos */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-4">
              Dispositivos Móviles
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Total Dispositivos */}
              <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Total Dispositivos</p>
                    <p className="text-3xl font-bold text-gray-900 dark:text-gray-50 mt-1">
                      {estadisticas.total_dispositivos}
                    </p>
                  </div>
                  <Smartphone className="h-10 w-10 text-blue-500" />
                </div>
              </div>

              {/* Dispositivos Activos */}
              <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Activos</p>
                    <p className="text-3xl font-bold text-green-600 dark:text-green-400 mt-1">
                      {estadisticas.dispositivos_activos}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {estadisticas.total_dispositivos > 0
                        ? `${((estadisticas.dispositivos_activos / estadisticas.total_dispositivos) * 100).toFixed(1)}%`
                        : '0%'}
                    </p>
                  </div>
                  <TrendingUp className="h-10 w-10 text-green-500" />
                </div>
              </div>

              {/* iOS */}
              <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">iOS</p>
                    <p className="text-3xl font-bold text-gray-900 dark:text-gray-50 mt-1">
                      {estadisticas.dispositivos_ios}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {estadisticas.total_dispositivos > 0
                        ? `${((estadisticas.dispositivos_ios / estadisticas.total_dispositivos) * 100).toFixed(1)}%`
                        : '0%'}
                    </p>
                  </div>
                  <span className="text-4xl">🍎</span>
                </div>
              </div>

              {/* Android */}
              <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Android</p>
                    <p className="text-3xl font-bold text-gray-900 dark:text-gray-50 mt-1">
                      {estadisticas.dispositivos_android}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {estadisticas.total_dispositivos > 0
                        ? `${((estadisticas.dispositivos_android / estadisticas.total_dispositivos) * 100).toFixed(1)}%`
                        : '0%'}
                    </p>
                  </div>
                  <span className="text-4xl">🤖</span>
                </div>
              </div>
            </div>
          </div>

          {/* Estadísticas de Actividad */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-4">
              Actividad Reciente
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Notificaciones Hoy */}
              <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Notificaciones Hoy</p>
                    <p className="text-3xl font-bold text-gray-900 dark:text-gray-50 mt-1">
                      {estadisticas.notificaciones_enviadas_hoy}
                    </p>
                  </div>
                  <Bell className="h-10 w-10 text-purple-500" />
                </div>
              </div>

              {/* Notificaciones Pendientes */}
              <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Pendientes</p>
                    <p className="text-3xl font-bold text-yellow-600 dark:text-yellow-400 mt-1">
                      {estadisticas.notificaciones_pendientes}
                    </p>
                  </div>
                  <Bell className="h-10 w-10 text-yellow-500" />
                </div>
              </div>

              {/* Documentos Este Mes */}
              <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Documentos Este Mes</p>
                    <p className="text-3xl font-bold text-gray-900 dark:text-gray-50 mt-1">
                      {estadisticas.documentos_escaneados_mes}
                    </p>
                  </div>
                  <FileText className="h-10 w-10 text-indigo-500" />
                </div>
              </div>

              {/* Citas Programadas */}
              <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Citas Programadas</p>
                    <p className="text-3xl font-bold text-gray-900 dark:text-gray-50 mt-1">
                      {estadisticas.citas_programadas}
                    </p>
                  </div>
                  <Calendar className="h-10 w-10 text-pink-500" />
                </div>
              </div>

              {/* Sincronizaciones Pendientes */}
              <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Sync Pendientes</p>
                    <p className="text-3xl font-bold text-gray-900 dark:text-gray-50 mt-1">
                      {estadisticas.sincronizaciones_pendientes}
                    </p>
                  </div>
                  <Wifi className="h-10 w-10 text-cyan-500" />
                </div>
              </div>
            </div>
          </div>

          {/* Gráfica de Distribución iOS vs Android */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-4">
              Distribución de Plataformas
            </h3>
            <div className="space-y-4">
              {/* iOS */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center">
                    <span className="text-2xl mr-2">🍎</span>
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">iOS</span>
                  </div>
                  <span className="text-sm font-medium text-gray-900 dark:text-gray-50">
                    {estadisticas.dispositivos_ios} ({estadisticas.total_dispositivos > 0
                      ? `${((estadisticas.dispositivos_ios / estadisticas.total_dispositivos) * 100).toFixed(1)}%`
                      : '0%'})
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all duration-500"
                    style={{
                      width: estadisticas.total_dispositivos > 0
                        ? `${(estadisticas.dispositivos_ios / estadisticas.total_dispositivos) * 100}%`
                        : '0%'
                    }}
                  ></div>
                </div>
              </div>

              {/* Android */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center">
                    <span className="text-2xl mr-2">🤖</span>
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Android</span>
                  </div>
                  <span className="text-sm font-medium text-gray-900 dark:text-gray-50">
                    {estadisticas.dispositivos_android} ({estadisticas.total_dispositivos > 0
                      ? `${((estadisticas.dispositivos_android / estadisticas.total_dispositivos) * 100).toFixed(1)}%`
                      : '0%'})
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-green-500 to-green-600 h-3 rounded-full transition-all duration-500"
                    style={{
                      width: estadisticas.total_dispositivos > 0
                        ? `${(estadisticas.dispositivos_android / estadisticas.total_dispositivos) * 100}%`
                        : '0%'
                    }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          {/* Información Adicional */}
          {estadisticas.sincronizaciones_pendientes > 0 && (
            <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
              <div className="flex items-start">
                <Wifi className="h-5 w-5 text-yellow-600 dark:text-yellow-400 mt-0.5 mr-3" />
                <div>
                  <h4 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                    Sincronizaciones Pendientes
                  </h4>
                  <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                    Hay {estadisticas.sincronizaciones_pendientes} operaciones pendientes de sincronización.
                    Los dispositivos las procesarán cuando tengan conexión.
                  </p>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default DashboardAppMovil;
