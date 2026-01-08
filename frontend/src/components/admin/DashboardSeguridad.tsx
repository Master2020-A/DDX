import React, { useEffect, useState } from 'react';
import { Users, Shield, Activity, AlertTriangle, TrendingUp, Clock } from 'lucide-react';
import securityService, { SecurityDashboard } from '../../services/securityService';

const DashboardSeguridad: React.FC = () => {
  const [dashboard, setDashboard] = useState<SecurityDashboard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    cargarDashboard();
  }, []);

  const cargarDashboard = async () => {
    try {
      setLoading(true);
      const data = await securityService.getDashboard();
      setDashboard(data);
    } catch (error) {
      console.error('Error al cargar dashboard:', error);
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

  if (!dashboard) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No se pudo cargar el dashboard</p>
      </div>
    );
  }

  const stats = [
    {
      name: 'Total Usuarios',
      value: dashboard.total_usuarios,
      icon: Users,
      color: 'bg-blue-500',
      change: '+12%',
      changeType: 'increase'
    },
    {
      name: 'Usuarios con 2FA',
      value: dashboard.usuarios_con_2fa,
      icon: Shield,
      color: 'bg-green-500',
      change: `${Math.round((dashboard.usuarios_con_2fa / dashboard.total_usuarios) * 100)}%`,
      changeType: 'neutral'
    },
    {
      name: 'Sesiones Activas',
      value: dashboard.sesiones_activas,
      icon: Activity,
      color: 'bg-purple-500',
      change: 'Ahora',
      changeType: 'neutral'
    },
    {
      name: 'Acciones Fallidas (24h)',
      value: dashboard.acciones_fallidas_ultimo_dia,
      icon: AlertTriangle,
      color: 'bg-red-500',
      change: dashboard.acciones_fallidas_ultimo_dia > 10 ? 'Alto' : 'Normal',
      changeType: dashboard.acciones_fallidas_ultimo_dia > 10 ? 'decrease' : 'neutral'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className={`flex-shrink-0 ${stat.color} rounded-md p-3`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        {stat.name}
                      </dt>
                      <dd className="flex items-baseline">
                        <div className="text-2xl font-semibold text-gray-900">
                          {stat.value}
                        </div>
                        <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                          stat.changeType === 'increase' ? 'text-green-600' :
                          stat.changeType === 'decrease' ? 'text-red-600' :
                          'text-gray-500'
                        }`}>
                          {stat.change}
                        </div>
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Distribución de Roles */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Distribución de Roles</h3>
          <TrendingUp className="h-5 w-5 text-gray-400" />
        </div>
        <div className="space-y-4">
          {Object.entries(dashboard.roles).map(([roleName, count]) => {
            const total = dashboard.total_usuarios;
            const percentage = Math.round((count / total) * 100);
            
            return (
              <div key={roleName}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700 capitalize">
                    {roleName}
                  </span>
                  <span className="text-sm text-gray-500">
                    {count} usuarios ({percentage}%)
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      roleName === 'admin' ? 'bg-red-500' :
                      roleName === 'medico' ? 'bg-blue-500' :
                      roleName === 'enfermero' ? 'bg-green-500' :
                      'bg-yellow-500'
                    }`}
                    style={{ width: `${percentage}%` }}
                  ></div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Actividad Reciente */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Actividad Reciente (24h)</h3>
          <Clock className="h-5 w-5 text-gray-400" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="border rounded-lg p-4">
            <div className="text-3xl font-bold text-indigo-600">
              {dashboard.acciones_ultimo_dia}
            </div>
            <div className="text-sm text-gray-500 mt-1">Acciones Totales</div>
          </div>
          <div className="border rounded-lg p-4">
            <div className="text-3xl font-bold text-green-600">
              {dashboard.acciones_ultimo_dia - dashboard.acciones_fallidas_ultimo_dia}
            </div>
            <div className="text-sm text-gray-500 mt-1">Acciones Exitosas</div>
          </div>
        </div>
      </div>

      {/* Recomendaciones de Seguridad */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <div className="flex items-start">
          <AlertTriangle className="h-6 w-6 text-yellow-600 mt-0.5" />
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">
              Recomendaciones de Seguridad
            </h3>
            <div className="mt-2 text-sm text-yellow-700">
              <ul className="list-disc list-inside space-y-1">
                {dashboard.usuarios_con_2fa < dashboard.total_usuarios * 0.5 && (
                  <li>Menos del 50% de usuarios tienen 2FA activado. Considera hacerlo obligatorio.</li>
                )}
                {dashboard.acciones_fallidas_ultimo_dia > 10 && (
                  <li>Se detectaron {dashboard.acciones_fallidas_ultimo_dia} acciones fallidas en las últimas 24h.</li>
                )}
                {dashboard.sesiones_activas > dashboard.total_usuarios * 2 && (
                  <li>Hay múltiples sesiones activas por usuario. Revisa sesiones sospechosas.</li>
                )}
                {dashboard.usuarios_con_2fa === dashboard.total_usuarios && (
                  <li className="text-green-700">✓ Todos los usuarios tienen 2FA activado. ¡Excelente!</li>
                )}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardSeguridad;
