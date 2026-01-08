import { useEffect, useState } from 'react';
import { Shield, FileText, Activity, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import cumplimientoService, { EstadisticasCumplimiento } from '../../services/cumplimientoService';

const DashboardCumplimiento = () => {
  const [estadisticas, setEstadisticas] = useState<EstadisticasCumplimiento | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    cargarEstadisticas();
  }, []);

  const cargarEstadisticas = async () => {
    try {
      setLoading(true);
      const data = await cumplimientoService.getEstadisticas();
      setEstadisticas(data);
    } catch (error) {
      console.error('Error al cargar estadísticas:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!estadisticas) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No se pudieron cargar las estadísticas</p>
      </div>
    );
  }

  const tarjetas = [
    {
      titulo: 'Consentimientos Activos',
      valor: estadisticas.consentimientos_activos,
      total: estadisticas.total_consentimientos,
      icono: FileText,
      color: 'bg-blue-500',
      colorClaro: 'bg-blue-50',
      colorTexto: 'text-blue-600',
    },
    {
      titulo: 'Firmas Válidas',
      valor: estadisticas.firmas_validas,
      total: estadisticas.total_firmas,
      icono: CheckCircle,
      color: 'bg-green-500',
      colorClaro: 'bg-green-50',
      colorTexto: 'text-green-600',
    },
    {
      titulo: 'Accesos Último Mes',
      valor: estadisticas.logs_acceso_ultimo_mes,
      total: null,
      icono: Activity,
      color: 'bg-purple-500',
      colorClaro: 'bg-purple-50',
      colorTexto: 'text-purple-600',
    },
    {
      titulo: 'Solicitudes GDPR Pendientes',
      valor: estadisticas.solicitudes_gdpr_pendientes,
      total: null,
      icono: estadisticas.solicitudes_gdpr_pendientes > 0 ? AlertTriangle : Clock,
      color: estadisticas.solicitudes_gdpr_pendientes > 0 ? 'bg-red-500' : 'bg-gray-500',
      colorClaro: estadisticas.solicitudes_gdpr_pendientes > 0 ? 'bg-red-50' : 'bg-gray-50',
      colorTexto: estadisticas.solicitudes_gdpr_pendientes > 0 ? 'text-red-600' : 'text-gray-600',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-50">
          Dashboard de Cumplimiento Normativo
        </h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Resumen del estado de cumplimiento HIPAA, GDPR y NOM-004-SSA3-2012
        </p>
      </div>

      {/* Tarjetas de Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {tarjetas.map((tarjeta, index) => {
          const Icon = tarjeta.icono;
          const porcentaje = tarjeta.total
            ? Math.round((tarjeta.valor / tarjeta.total) * 100)
            : null;

          return (
            <div
              key={index}
              className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    {tarjeta.titulo}
                  </p>
                  <div className="mt-2 flex items-baseline">
                    <p className="text-3xl font-semibold text-gray-900 dark:text-gray-50">
                      {tarjeta.valor}
                    </p>
                    {tarjeta.total && (
                      <p className="ml-2 text-sm text-gray-500 dark:text-gray-400">
                        / {tarjeta.total}
                      </p>
                    )}
                  </div>
                  {porcentaje !== null && (
                    <div className="mt-2">
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div
                          className={`${tarjeta.color} h-2 rounded-full transition-all`}
                          style={{ width: `${porcentaje}%` }}
                        ></div>
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {porcentaje}% del total
                      </p>
                    </div>
                  )}
                </div>
                <div className={`${tarjeta.colorClaro} p-3 rounded-lg ml-4`}>
                  <Icon className={`h-6 w-6 ${tarjeta.colorTexto}`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Información de Normativas */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* HIPAA */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="bg-blue-100 dark:bg-blue-900 p-2 rounded-lg">
              <Shield className="h-6 w-6 text-blue-600 dark:text-blue-300" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50">HIPAA</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">Estados Unidos</p>
            </div>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">
            Health Insurance Portability and Accountability Act
          </p>
          <div className="space-y-2">
            <div className="flex items-center text-sm">
              <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
              <span className="text-gray-700 dark:text-gray-300">Logs de acceso activos</span>
            </div>
            <div className="flex items-center text-sm">
              <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
              <span className="text-gray-700 dark:text-gray-300">Retención: 7 años</span>
            </div>
            <div className="flex items-center text-sm">
              <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
              <span className="text-gray-700 dark:text-gray-300">Auditorías habilitadas</span>
            </div>
          </div>
        </div>

        {/* GDPR */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="bg-purple-100 dark:bg-purple-900 p-2 rounded-lg">
              <Shield className="h-6 w-6 text-purple-600 dark:text-purple-300" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50">GDPR</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">Unión Europea</p>
            </div>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">
            General Data Protection Regulation
          </p>
          <div className="space-y-2">
            <div className="flex items-center text-sm">
              <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
              <span className="text-gray-700 dark:text-gray-300">Consentimiento explícito</span>
            </div>
            <div className="flex items-center text-sm">
              <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
              <span className="text-gray-700 dark:text-gray-300">Portabilidad de datos</span>
            </div>
            <div className="flex items-center text-sm">
              <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
              <span className="text-gray-700 dark:text-gray-300">Derecho al olvido</span>
            </div>
          </div>
        </div>

        {/* NOM-004 */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="bg-green-100 dark:bg-green-900 p-2 rounded-lg">
              <Shield className="h-6 w-6 text-green-600 dark:text-green-300" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50">NOM-004</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">México</p>
            </div>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">
            Expediente Clínico Electrónico
          </p>
          <div className="space-y-2">
            <div className="flex items-center text-sm">
              <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
              <span className="text-gray-700 dark:text-gray-300">Firma electrónica</span>
            </div>
            <div className="flex items-center text-sm">
              <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
              <span className="text-gray-700 dark:text-gray-300">Expediente electrónico</span>
            </div>
            <div className="flex items-center text-sm">
              <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
              <span className="text-gray-700 dark:text-gray-300">Respaldo automático</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardCumplimiento;
