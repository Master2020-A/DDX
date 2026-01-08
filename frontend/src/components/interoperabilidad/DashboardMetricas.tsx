import React, { useState, useEffect } from "react";
import {
  Activity,
  AlertTriangle,
  Clock,
  Server,
  Shield,
  Database,
  Building2,
  BarChart3,
  Zap,
  WifiOff,
} from "lucide-react";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface MetricasTiempoReal {
  timestamp: string;
  periodo_dias: number;
  solicitudes: {
    total: number;
    por_estado: Record<string, number>;
    por_prioridad: Record<string, number>;
    tiempo_promedio_procesamiento_horas: number;
    tasa_exito_porcentaje: number;
    pendientes: number;
    en_proceso: number;
    completadas: number;
    rechazadas: number;
    con_error: number;
  };
  instituciones: {
    total: number;
    activas: number;
    inactivas: number;
    por_nivel_atencion: Record<string, number>;
    por_tipo: Record<string, number>;
    top_instituciones: Array<{ nombre: string; solicitudes: number }>;
  };
  rendimiento: {
    solicitudes_por_dia: Array<{ fecha: string; total: number }>;
    promedio_diario: number;
    pico_carga: { fecha: string; total: number } | null;
    disponibilidad_porcentaje: number;
    total_eventos_auditoria: number;
    total_errores: number;
  };
  seguridad: {
    total_consentimientos: number;
    consentimientos_activos: number;
    consentimientos_expirados: number;
    eventos_auditoria_por_tipo: Record<string, number>;
    accesos_denegados: number;
    tasa_cumplimiento_porcentaje: number;
  };
  volumen: {
    total_historias_unificadas: number;
    historias_nuevas_periodo: number;
    bundles_fhir_generados: number;
    datos_transferidos_mb: number;
    promedio_bundle_kb: number;
  };
}

interface Alerta {
  tipo: string;
  severidad: "baja" | "media" | "alta";
  mensaje: string;
  count: number;
}

const COLORS = {
  primary: "#3b82f6",
  success: "#10b981",
  warning: "#f59e0b",
  danger: "#ef4444",
  info: "#06b6d4",
  purple: "#8b5cf6",
};

const CHART_COLORS = [
  "#3b82f6",
  "#10b981",
  "#f59e0b",
  "#ef4444",
  "#8b5cf6",
  "#06b6d4",
];

// ✅ DATOS MOCK PARA DESARROLLO
const METRICAS_MOCK: MetricasTiempoReal = {
  timestamp: new Date().toISOString(),
  periodo_dias: 7,
  solicitudes: {
    total: 156,
    por_estado: {
      pendiente: 12,
      aprobada: 45,
      en_proceso: 23,
      completada: 67,
      rechazada: 5,
      error: 4,
    },
    por_prioridad: {
      baja: 30,
      normal: 80,
      alta: 35,
      urgente: 11,
    },
    tiempo_promedio_procesamiento_horas: 4.5,
    tasa_exito_porcentaje: 89.5,
    pendientes: 12,
    en_proceso: 23,
    completadas: 67,
    rechazadas: 5,
    con_error: 4,
  },
  instituciones: {
    total: 25,
    activas: 20,
    inactivas: 5,
    por_nivel_atencion: {
      primario: 10,
      secundario: 8,
      terciario: 5,
      especializado: 2,
    },
    por_tipo: {
      publico: 15,
      privado: 8,
      mixto: 2,
    },
    top_instituciones: [
      { nombre: "Hospital General de México", solicitudes: 45 },
      { nombre: "IMSS Clínica 20", solicitudes: 32 },
      { nombre: "Hospital Ángeles", solicitudes: 28 },
      { nombre: "Centro Médico Nacional", solicitudes: 25 },
      { nombre: "Hospital ABC", solicitudes: 18 },
    ],
  },
  rendimiento: {
    solicitudes_por_dia: [
      { fecha: "2024-01-15", total: 20 },
      { fecha: "2024-01-16", total: 25 },
      { fecha: "2024-01-17", total: 18 },
      { fecha: "2024-01-18", total: 30 },
      { fecha: "2024-01-19", total: 22 },
      { fecha: "2024-01-20", total: 28 },
      { fecha: "2024-01-21", total: 13 },
    ],
    promedio_diario: 22.3,
    pico_carga: { fecha: "2024-01-18", total: 30 },
    disponibilidad_porcentaje: 99.8,
    total_eventos_auditoria: 1250,
    total_errores: 4,
  },
  seguridad: {
    total_consentimientos: 350,
    consentimientos_activos: 320,
    consentimientos_expirados: 30,
    eventos_auditoria_por_tipo: {
      acceso: 800,
      modificacion: 300,
      exportacion: 150,
    },
    accesos_denegados: 12,
    tasa_cumplimiento_porcentaje: 98.5,
  },
  volumen: {
    total_historias_unificadas: 1500,
    historias_nuevas_periodo: 45,
    bundles_fhir_generados: 890,
    datos_transferidos_mb: 256.5,
    promedio_bundle_kb: 288,
  },
};

const DashboardMetricas: React.FC = () => {
  const [metricas, setMetricas] = useState<MetricasTiempoReal | null>(null);
  const [alertas, setAlertas] = useState<Alerta[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [usandoMock, setUsandoMock] = useState(false);
  const [periodoDias, setPeriodoDias] = useState(7);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const cargarMetricas = async () => {
    try {
      const response = await fetch(
        `http://localhost:8612/api/interoperabilidad/metricas/tiempo-real?periodo_dias=${periodoDias}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      setMetricas(data);
      setUsandoMock(false);
      setError(null);
    } catch (err) {
      console.warn("API no disponible, usando datos de demostración:", err);
      // ✅ Usar datos mock cuando la API no está disponible
      setMetricas({ ...METRICAS_MOCK, periodo_dias: periodoDias });
      setUsandoMock(true);
      setError("API no disponible - Mostrando datos de demostración");
    }
  };

  const cargarAlertas = async () => {
    try {
      const response = await fetch(
        "http://localhost:8612/api/interoperabilidad/metricas/alertas",
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      setAlertas(data.alertas || []);
    } catch (err) {
      console.warn("Error cargando alertas:", err);
      // Alertas mock para demostración
      setAlertas([
        { tipo: "info", severidad: "baja", mensaje: "Sistema funcionando en modo demostración", count: 1 },
      ]);
    }
  };

  const cargarDatos = async () => {
    setLoading(true);
    await Promise.all([cargarMetricas(), cargarAlertas()]);
    setLoading(false);
  };

  useEffect(() => {
    cargarDatos();
  }, [periodoDias]);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(cargarDatos, 30000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, periodoDias]);

  // ✅ Loading state
  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
      </div>
    );
  }

  // ✅ Verificación de seguridad para metricas
  if (!metricas) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-500">
        <WifiOff className="w-16 h-16 mb-4" />
        <p className="text-lg font-medium">No se pudieron cargar las métricas</p>
        <button
          onClick={cargarDatos}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Reintentar
        </button>
      </div>
    );
  }

  const getSeveridadColor = (severidad: string) => {
    switch (severidad) {
      case "alta":
        return "bg-red-100 text-red-800 border-red-200";
      case "media":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "baja":
        return "bg-blue-100 text-blue-800 border-blue-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  // ✅ Verificación segura de datos para gráficas
  const datosEstados = Object.entries(metricas?.solicitudes?.por_estado || {}).map(
    ([estado, count]) => ({
      name: estado.replace("_", " "),
      value: count,
    })
  );

  const datosPrioridad = Object.entries(metricas?.solicitudes?.por_prioridad || {}).map(
    ([prioridad, count]) => ({
      name: prioridad,
      value: count,
    })
  );

  return (
    <div className="space-y-6">
      {/* ✅ Banner de modo demostración */}
      {usandoMock && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 flex items-center gap-3">
          <WifiOff className="w-5 h-5 text-amber-600" />
          <div>
            <p className="font-medium text-amber-800">Modo Demostración</p>
            <p className="text-sm text-amber-600">
              La API de interoperabilidad no está disponible. Se muestran datos de ejemplo.
            </p>
          </div>
        </div>
      )}

      {/* Header con controles */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Activity className="w-7 h-7 text-blue-600" />
            Dashboard de Métricas en Tiempo Real
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Última actualización:{" "}
            {new Date(metricas.timestamp).toLocaleString("es-MX")}
          </p>
        </div>

        <div className="flex items-center gap-4">
          <select
            value={periodoDias}
            onChange={(e) => setPeriodoDias(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
          >
            <option value={1}>Últimas 24 horas</option>
            <option value={7}>Últimos 7 días</option>
            <option value={30}>Últimos 30 días</option>
            <option value={90}>Últimos 90 días</option>
          </select>

          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-4 py-2 rounded-md flex items-center gap-2 ${
              autoRefresh
                ? "bg-green-100 text-green-700 border border-green-300"
                : "bg-gray-100 text-gray-700 border border-gray-300"
            }`}
          >
            <Zap className={`w-4 h-4 ${autoRefresh ? "animate-pulse" : ""}`} />
            {autoRefresh ? "Auto ON" : "Auto OFF"}
          </button>

          <button
            onClick={cargarDatos}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center gap-2"
          >
            <Activity className="w-4 h-4" />
            Actualizar
          </button>
        </div>
      </div>

      {/* Alertas */}
      {alertas.length > 0 && (
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-orange-500" />
            Alertas del Sistema ({alertas.length})
          </h3>
          <div className="space-y-2">
            {alertas.map((alerta, index) => (
              <div
                key={index}
                className={`p-3 rounded-md border ${getSeveridadColor(alerta.severidad)}`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">{alerta.mensaje}</span>
                  <span className="text-xs uppercase font-semibold">
                    {alerta.severidad}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tarjetas de métricas principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Solicitudes</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">
                {metricas.solicitudes?.total ?? 0}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Tasa éxito: {metricas.solicitudes?.tasa_exito_porcentaje ?? 0}%
              </p>
            </div>
            <BarChart3 className="w-12 h-12 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Instituciones Activas</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">
                {metricas.instituciones?.activas ?? 0}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                de {metricas.instituciones?.total ?? 0} totales
              </p>
            </div>
            <Building2 className="w-12 h-12 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Disponibilidad</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">
                {metricas.rendimiento?.disponibilidad_porcentaje ?? 0}%
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {metricas.rendimiento?.total_errores ?? 0} errores
              </p>
            </div>
            <Server className="w-12 h-12 text-purple-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Datos Transferidos</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">
                {metricas.volumen?.datos_transferidos_mb ?? 0} MB
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {metricas.volumen?.bundles_fhir_generados ?? 0} bundles FHIR
              </p>
            </div>
            <Database className="w-12 h-12 text-cyan-500" />
          </div>
        </div>
      </div>

      {/* Gráficas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Solicitudes por Estado</h3>
          {datosEstados.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <RechartsPieChart>
                <Pie
                  data={datosEstados}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) =>
                    `${name}: ${(percent * 100).toFixed(0)}%`
                  }
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {datosEstados.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={CHART_COLORS[index % CHART_COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip />
              </RechartsPieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center text-gray-400">
              No hay datos disponibles
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Solicitudes por Prioridad</h3>
          {datosPrioridad.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={datosPrioridad}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill={COLORS.primary} name="Solicitudes" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center text-gray-400">
              No hay datos disponibles
            </div>
          )}
        </div>
      </div>

      {/* Tendencia temporal */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">
          Solicitudes por Día (Últimos {periodoDias} días)
        </h3>
        {(metricas.rendimiento?.solicitudes_por_dia?.length ?? 0) > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={metricas.rendimiento.solicitudes_por_dia}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="fecha" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area
                type="monotone"
                dataKey="total"
                stroke={COLORS.primary}
                fill={COLORS.primary}
                fillOpacity={0.3}
                name="Solicitudes"
              />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-[300px] flex items-center justify-center text-gray-400">
            No hay datos de tendencia disponibles
          </div>
        )}
      </div>

      {/* Métricas detalladas */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-blue-600" />
            Rendimiento
          </h3>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-600">Tiempo Promedio</p>
              <p className="text-2xl font-bold text-gray-900">
                {(metricas.solicitudes?.tiempo_promedio_procesamiento_horas ?? 0).toFixed(1)} hrs
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Promedio Diario</p>
              <p className="text-2xl font-bold text-gray-900">
                {(metricas.rendimiento?.promedio_diario ?? 0).toFixed(0)} solicitudes
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Shield className="w-5 h-5 text-green-600" />
            Seguridad
          </h3>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-600">Consentimientos Activos</p>
              <p className="text-2xl font-bold text-gray-900">
                {metricas.seguridad?.consentimientos_activos ?? 0}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Tasa Cumplimiento</p>
              <p className="text-2xl font-bold text-gray-900">
                {metricas.seguridad?.tasa_cumplimiento_porcentaje ?? 0}%
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Database className="w-5 h-5 text-purple-600" />
            Volumen
          </h3>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-600">Historias Unificadas</p>
              <p className="text-2xl font-bold text-gray-900">
                {metricas.volumen?.total_historias_unificadas ?? 0}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Bundles Generados</p>
              <p className="text-2xl font-bold text-gray-900">
                {metricas.volumen?.bundles_fhir_generados ?? 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Top Instituciones */}
      {(metricas.instituciones?.top_instituciones?.length ?? 0) > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">
            Top 5 Instituciones por Volumen
          </h3>
          <div className="space-y-3">
            {metricas.instituciones.top_instituciones.map((inst, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl font-bold text-gray-400">#{index + 1}</span>
                  <span className="font-medium text-gray-900">{inst.nombre}</span>
                </div>
                <span className="text-lg font-semibold text-blue-600">
                  {inst.solicitudes} solicitudes
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardMetricas;