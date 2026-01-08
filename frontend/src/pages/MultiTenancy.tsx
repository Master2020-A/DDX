import React, { useState, useEffect } from 'react';
import {
  Building2,
  Users,
  Database,
  DollarSign,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock,
  Settings,
  FileText,
  BarChart3,
  Plus,
} from 'lucide-react';
import axios from 'axios';

const API_URL = 'http://localhost:8612/api';

interface DashboardData {
  total_instituciones: number;
  instituciones_activas: number;
  instituciones_prueba: number;
  instituciones_suspendidas: number;
  total_usuarios: number;
  total_pacientes: number;
  total_almacenamiento_gb: number;
  mrr_total: number;
  arr_total: number;
  ingresos_mes_actual: number;
  ingresos_mes_anterior: number;
  crecimiento_ingresos_pct: number;
  instituciones_limite_usuarios: string[];
  instituciones_limite_almacenamiento: string[];
  facturas_vencidas: number;
  renovaciones_proximas: number;
}

interface Institucion {
  id: string;
  codigo: string;
  nombre: string;
  tipo: string;
  plan: string;
  estado: string;
  usuarios_activos: number;
  pacientes_registrados: number;
  activa: boolean;
}

export default function MultiTenancy() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'instituciones' | 'facturacion'>('dashboard');
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [instituciones, setInstituciones] = useState<Institucion[]>([]);
  const [loading, setLoading] = useState(true);
  const [showNuevaInstitucion, setShowNuevaInstitucion] = useState(false);

  useEffect(() => {
    cargarDatos();
  }, [activeTab]);

  const cargarDatos = async () => {
    setLoading(true);
    try {
      if (activeTab === 'dashboard') {
        const response = await axios.get(`${API_URL}/instituciones/dashboard/estadisticas`);
        setDashboard(response.data);
      } else if (activeTab === 'instituciones') {
        const response = await axios.get(`${API_URL}/instituciones/`);
        setInstituciones(response.data);
      }
    } catch (error) {
      console.error('Error al cargar datos:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN',
    }).format(amount);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('es-MX').format(num);
  };

  const getPlanBadgeColor = (plan: string) => {
    const colors: Record<string, string> = {
      basico: 'bg-gray-100 text-gray-800',
      profesional: 'bg-blue-100 text-blue-800',
      empresarial: 'bg-purple-100 text-purple-800',
      personalizado: 'bg-green-100 text-green-800',
    };
    return colors[plan] || 'bg-gray-100 text-gray-800';
  };

  const getEstadoBadgeColor = (estado: string) => {
    const colors: Record<string, string> = {
      activa: 'bg-green-100 text-green-800',
      prueba: 'bg-yellow-100 text-yellow-800',
      suspendida: 'bg-red-100 text-red-800',
      cancelada: 'bg-gray-100 text-gray-800',
    };
    return colors[estado] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Multi-Tenancy</h1>
              <p className="mt-1 text-sm text-gray-500">
                Administración de instituciones y facturación
              </p>
            </div>
            <button
              onClick={() => setShowNuevaInstitucion(true)}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Plus size={20} className="mr-2" />
              Nueva Institución
            </button>
          </div>

          {/* Tabs */}
          <div className="mt-6 border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`pb-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'dashboard'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <BarChart3 size={18} className="inline mr-2" />
                Dashboard
              </button>
              <button
                onClick={() => setActiveTab('instituciones')}
                className={`pb-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'instituciones'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Building2 size={18} className="inline mr-2" />
                Instituciones
              </button>
              <button
                onClick={() => setActiveTab('facturacion')}
                className={`pb-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'facturacion'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <FileText size={18} className="inline mr-2" />
                Facturación
              </button>
            </nav>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <>
            {/* Dashboard Tab */}
            {activeTab === 'dashboard' && dashboard && (
              <div className="space-y-6">
                {/* Métricas principales */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Total Instituciones</p>
                        <p className="text-3xl font-bold text-gray-900 mt-2">
                          {dashboard.total_instituciones}
                        </p>
                      </div>
                      <div className="p-3 bg-blue-100 rounded-full">
                        <Building2 size={24} className="text-blue-600" />
                      </div>
                    </div>
                    <div className="mt-4 flex items-center text-sm">
                      <CheckCircle size={16} className="text-green-500 mr-1" />
                      <span className="text-green-600 font-medium">{dashboard.instituciones_activas}</span>
                      <span className="text-gray-500 ml-1">activas</span>
                    </div>
                  </div>

                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Total Usuarios</p>
                        <p className="text-3xl font-bold text-gray-900 mt-2">
                          {formatNumber(dashboard.total_usuarios)}
                        </p>
                      </div>
                      <div className="p-3 bg-green-100 rounded-full">
                        <Users size={24} className="text-green-600" />
                      </div>
                    </div>
                    <div className="mt-4 flex items-center text-sm">
                      <span className="text-gray-500">
                        {formatNumber(dashboard.total_pacientes)} pacientes
                      </span>
                    </div>
                  </div>

                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">MRR</p>
                        <p className="text-3xl font-bold text-gray-900 mt-2">
                          {formatCurrency(dashboard.mrr_total)}
                        </p>
                      </div>
                      <div className="p-3 bg-purple-100 rounded-full">
                        <DollarSign size={24} className="text-purple-600" />
                      </div>
                    </div>
                    <div className="mt-4 flex items-center text-sm">
                      <TrendingUp size={16} className="text-green-500 mr-1" />
                      <span className="text-green-600 font-medium">
                        {dashboard.crecimiento_ingresos_pct.toFixed(1)}%
                      </span>
                      <span className="text-gray-500 ml-1">vs mes anterior</span>
                    </div>
                  </div>

                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Almacenamiento</p>
                        <p className="text-3xl font-bold text-gray-900 mt-2">
                          {dashboard.total_almacenamiento_gb.toFixed(1)} GB
                        </p>
                      </div>
                      <div className="p-3 bg-orange-100 rounded-full">
                        <Database size={24} className="text-orange-600" />
                      </div>
                    </div>
                    <div className="mt-4 flex items-center text-sm">
                      <span className="text-gray-500">Uso total del sistema</span>
                    </div>
                  </div>
                </div>

                {/* Ingresos */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Ingresos Mensuales</h3>
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm text-gray-600">Mes Actual</span>
                          <span className="text-lg font-bold text-gray-900">
                            {formatCurrency(dashboard.ingresos_mes_actual)}
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-blue-600 h-2 rounded-full w-full"></div>
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm text-gray-600">Mes Anterior</span>
                          <span className="text-lg font-bold text-gray-900">
                            {formatCurrency(dashboard.ingresos_mes_anterior)}
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-gray-400 h-2 rounded-full transition-all"
                            style={{
                              width: `${
                                dashboard.ingresos_mes_actual > 0
                                  ? Math.min((dashboard.ingresos_mes_anterior / dashboard.ingresos_mes_actual) * 100, 100)
                                  : 0
                              }%`,
                            }}
                          ></div>
                        </div>
                      </div>
                      <div className="pt-4 border-t border-gray-200">
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium text-gray-600">ARR (Anual)</span>
                          <span className="text-xl font-bold text-gray-900">
                            {formatCurrency(dashboard.arr_total)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Alertas */}
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Alertas</h3>
                    <div className="space-y-3">
                      {dashboard.facturas_vencidas > 0 && (
                        <div className="flex items-start p-3 bg-red-50 rounded-lg">
                          <AlertTriangle size={20} className="text-red-600 mr-3 mt-0.5" />
                          <div>
                            <p className="text-sm font-medium text-red-900">
                              {dashboard.facturas_vencidas} facturas vencidas
                            </p>
                            <p className="text-xs text-red-700 mt-1">Requieren atención inmediata</p>
                          </div>
                        </div>
                      )}

                      {dashboard.renovaciones_proximas > 0 && (
                        <div className="flex items-start p-3 bg-yellow-50 rounded-lg">
                          <Clock size={20} className="text-yellow-600 mr-3 mt-0.5" />
                          <div>
                            <p className="text-sm font-medium text-yellow-900">
                              {dashboard.renovaciones_proximas} renovaciones próximas
                            </p>
                            <p className="text-xs text-yellow-700 mt-1">En los próximos 30 días</p>
                          </div>
                        </div>
                      )}

                      {dashboard.instituciones_limite_usuarios.length > 0 && (
                        <div className="flex items-start p-3 bg-orange-50 rounded-lg">
                          <Users size={20} className="text-orange-600 mr-3 mt-0.5" />
                          <div>
                            <p className="text-sm font-medium text-orange-900">
                              {dashboard.instituciones_limite_usuarios.length} instituciones cerca del límite de usuarios
                            </p>
                            <p className="text-xs text-orange-700 mt-1">Considerar upgrade de plan</p>
                          </div>
                        </div>
                      )}

                      {dashboard.instituciones_limite_almacenamiento.length > 0 && (
                        <div className="flex items-start p-3 bg-orange-50 rounded-lg">
                          <Database size={20} className="text-orange-600 mr-3 mt-0.5" />
                          <div>
                            <p className="text-sm font-medium text-orange-900">
                              {dashboard.instituciones_limite_almacenamiento.length} instituciones cerca del límite de almacenamiento
                            </p>
                            <p className="text-xs text-orange-700 mt-1">Revisar uso de espacio</p>
                          </div>
                        </div>
                      )}

                      {dashboard.facturas_vencidas === 0 &&
                        dashboard.renovaciones_proximas === 0 &&
                        dashboard.instituciones_limite_usuarios.length === 0 &&
                        dashboard.instituciones_limite_almacenamiento.length === 0 && (
                          <div className="flex items-center justify-center p-8 text-gray-500">
                            <CheckCircle size={24} className="mr-2 text-green-500" />
                            <span>No hay alertas pendientes</span>
                          </div>
                        )}
                    </div>
                  </div>
                </div>

                {/* Estados de instituciones */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Estado de Instituciones</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 border border-green-200 rounded-lg bg-green-50">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-green-900">Activas</span>
                        <span className="text-2xl font-bold text-green-600">
                          {dashboard.instituciones_activas}
                        </span>
                      </div>
                    </div>
                    <div className="p-4 border border-yellow-200 rounded-lg bg-yellow-50">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-yellow-900">En Prueba</span>
                        <span className="text-2xl font-bold text-yellow-600">
                          {dashboard.instituciones_prueba}
                        </span>
                      </div>
                    </div>
                    <div className="p-4 border border-red-200 rounded-lg bg-red-50">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-red-900">Suspendidas</span>
                        <span className="text-2xl font-bold text-red-600">
                          {dashboard.instituciones_suspendidas}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Instituciones Tab */}
            {activeTab === 'instituciones' && (
              <div className="bg-white rounded-lg shadow">
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Institución
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Tipo
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Plan
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Estado
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Usuarios
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Pacientes
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Acciones
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {instituciones.map((inst) => (
                        <tr key={inst.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div>
                              <div className="text-sm font-medium text-gray-900">{inst.nombre}</div>
                              <div className="text-sm text-gray-500">{inst.codigo}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="text-sm text-gray-900 capitalize">
                              {inst.tipo.replace('_', ' ')}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span
                              className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getPlanBadgeColor(
                                inst.plan
                              )}`}
                            >
                              {inst.plan.charAt(0).toUpperCase() + inst.plan.slice(1)}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span
                              className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getEstadoBadgeColor(
                                inst.estado
                              )}`}
                            >
                              {inst.estado.charAt(0).toUpperCase() + inst.estado.slice(1)}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {inst.usuarios_activos}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatNumber(inst.pacientes_registrados)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <button 
                              className="text-blue-600 hover:text-blue-900 mr-3"
                              title="Configurar institución"
                              aria-label="Configurar institución"
                            >
                              <Settings size={18} />
                            </button>
                            <button 
                              className="text-gray-600 hover:text-gray-900"
                              title="Ver facturas"
                              aria-label="Ver facturas"
                            >
                              <FileText size={18} />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Facturación Tab */}
            {activeTab === 'facturacion' && (
              <div className="bg-white rounded-lg shadow p-6">
                <p className="text-gray-500 text-center py-12">
                  Módulo de facturación en desarrollo
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
