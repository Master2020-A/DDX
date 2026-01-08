import { useState, useEffect } from 'react';
import { Database, HardDrive, AlertTriangle, CheckCircle, Clock, TrendingUp } from 'lucide-react';
import backupsService, { EstadisticasBackups, EstadoSistema } from '../../services/backupsService';

const DashboardBackups = () => {
  const [estadisticas, setEstadisticas] = useState<EstadisticasBackups | null>(null);
  const [estadoSistema, setEstadoSistema] = useState<EstadoSistema | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    cargarDatos();
  }, []);

  const cargarDatos = async () => {
    try {
      setLoading(true);
      const [stats, estado] = await Promise.all([
        backupsService.obtenerEstadisticas(),
        backupsService.obtenerEstadoSistema(),
      ]);
      setEstadisticas(stats);
      setEstadoSistema(estado);
    } catch (error) {
      console.error('Error al cargar datos:', error);
    } finally {
      setLoading(false);
    }
  };

  const obtenerColorEstado = (estado: string) => {
    switch (estado) {
      case 'healthy':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'degraded':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'critical':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const obtenerTextoEstado = (estado: string) => {
    switch (estado) {
      case 'healthy':
        return 'Saludable';
      case 'degraded':
        return 'Degradado';
      case 'critical':
        return 'Crítico';
      default:
        return 'Desconocido';
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
      {/* Estado del Sistema */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-50">
            Estado del Sistema
          </h2>
          <button
            onClick={cargarDatos}
            className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400"
          >
            🔄 Actualizar
          </button>
        </div>

        {estadoSistema && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Estado General */}
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Estado</p>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mt-1 ${obtenerColorEstado(estadoSistema.estado)}`}>
                    {obtenerTextoEstado(estadoSistema.estado)}
                  </span>
                </div>
                <CheckCircle className={`h-8 w-8 ${estadoSistema.estado === 'healthy' ? 'text-green-500' : 'text-yellow-500'}`} />
              </div>
            </div>

            {/* Disponibilidad */}
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Disponibilidad</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-gray-50 mt-1">
                    {estadoSistema.disponibilidad_porcentaje.toFixed(2)}%
                  </p>
                </div>
                <TrendingUp className="h-8 w-8 text-blue-500" />
              </div>
            </div>

            {/* Uptime */}
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Uptime</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-gray-50 mt-1">
                    {estadoSistema.uptime_dias} días
                  </p>
                </div>
                <Clock className="h-8 w-8 text-purple-500" />
              </div>
            </div>

            {/* Alertas Activas */}
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Alertas Activas</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-gray-50 mt-1">
                    {estadoSistema.alertas_activas}
                  </p>
                </div>
                <AlertTriangle className={`h-8 w-8 ${estadoSistema.alertas_activas > 0 ? 'text-red-500' : 'text-gray-400'}`} />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Estadísticas de Backups */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-50 mb-4">
          Estadísticas de Backups
        </h2>

        {estadisticas && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Total de Backups */}
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Total de Backups</p>
                  <p className="text-3xl font-bold text-gray-900 dark:text-gray-50 mt-1">
                    {estadisticas.total_backups}
                  </p>
                </div>
                <Database className="h-10 w-10 text-blue-500" />
              </div>
            </div>

            {/* Backups Completados */}
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Completados</p>
                  <p className="text-3xl font-bold text-green-600 dark:text-green-400 mt-1">
                    {estadisticas.backups_completados}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {estadisticas.total_backups > 0
                      ? `${((estadisticas.backups_completados / estadisticas.total_backups) * 100).toFixed(1)}%`
                      : '0%'}
                  </p>
                </div>
                <CheckCircle className="h-10 w-10 text-green-500" />
              </div>
            </div>

            {/* Backups Fallidos */}
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Fallidos</p>
                  <p className="text-3xl font-bold text-red-600 dark:text-red-400 mt-1">
                    {estadisticas.backups_fallidos}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {estadisticas.total_backups > 0
                      ? `${((estadisticas.backups_fallidos / estadisticas.total_backups) * 100).toFixed(1)}%`
                      : '0%'}
                  </p>
                </div>
                <AlertTriangle className="h-10 w-10 text-red-500" />
              </div>
            </div>

            {/* Tamaño Total */}
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Tamaño Total</p>
                  <p className="text-3xl font-bold text-gray-900 dark:text-gray-50 mt-1">
                    {estadisticas.tamano_total_gb.toFixed(2)} GB
                  </p>
                </div>
                <HardDrive className="h-10 w-10 text-purple-500" />
              </div>
            </div>

            {/* Programaciones Activas */}
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Programaciones Activas</p>
                  <p className="text-3xl font-bold text-gray-900 dark:text-gray-50 mt-1">
                    {estadisticas.programaciones_activas}
                  </p>
                </div>
                <Clock className="h-10 w-10 text-indigo-500" />
              </div>
            </div>

            {/* Último Backup */}
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Último Backup</p>
                {estadisticas.ultimo_backup.fecha ? (
                  <>
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-50 mt-1">
                      {estadisticas.ultimo_backup.nombre}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(estadisticas.ultimo_backup.fecha).toLocaleString('es-MX')}
                    </p>
                    <p className="text-xs text-gray-500">
                      {estadisticas.ultimo_backup.tamano_mb.toFixed(2)} MB
                    </p>
                  </>
                ) : (
                  <p className="text-sm text-gray-500 mt-1">Sin backups recientes</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Información Adicional */}
      {estadoSistema && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Espacio en Disco */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-4">
              Espacio en Disco
            </h3>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-3xl font-bold text-gray-900 dark:text-gray-50">
                  {estadoSistema.espacio_disco_libre_gb} GB
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Espacio libre disponible
                </p>
              </div>
              <HardDrive className="h-12 w-12 text-blue-500" />
            </div>
            {estadoSistema.espacio_disco_libre_gb < 50 && (
              <div className="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                <p className="text-sm text-yellow-800 dark:text-yellow-200">
                  ⚠️ Espacio en disco bajo. Considere limpiar backups antiguos.
                </p>
              </div>
            )}
          </div>

          {/* Último Backup Exitoso */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-4">
              Último Backup Exitoso
            </h3>
            {estadoSistema.ultimo_backup_exitoso ? (
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Fecha</p>
                  <p className="text-lg font-medium text-gray-900 dark:text-gray-50 mt-1">
                    {new Date(estadoSistema.ultimo_backup_exitoso).toLocaleString('es-MX')}
                  </p>
                  <p className="text-sm text-gray-500 mt-2">
                    Hace {Math.floor((Date.now() - new Date(estadoSistema.ultimo_backup_exitoso).getTime()) / (1000 * 60 * 60))} horas
                  </p>
                </div>
                <CheckCircle className="h-12 w-12 text-green-500" />
              </div>
            ) : (
              <p className="text-sm text-gray-500">No hay backups exitosos registrados</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardBackups;
