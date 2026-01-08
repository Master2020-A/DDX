import { useState, useEffect } from 'react'
import { Brain, BarChart3, AlertTriangle, Pill, Activity, Bug } from 'lucide-react'
import iaMedicaService, { DashboardIAResponse } from '../services/iaMedicaService'
import AsistenteIA from '../components/ia-medica/AsistenteIA'
import PrediccionRiesgos from '../components/ia-medica/PrediccionRiesgos'
import RecomendacionesTratamiento from '../components/ia-medica/RecomendacionesTratamiento'
import InteraccionesMedicamentosas from '../components/ia-medica/InteraccionesMedicamentosas'
import DeteccionAnomalias from '../components/ia-medica/DeteccionAnomalias'
import DashboardIA from '../components/ia-medica/DashboardIA'

export default function InteligenciaArtificial() {
  const [tabActual, setTabActual] = useState(0)
  const [dashboard, setDashboard] = useState<DashboardIAResponse | null>(null)
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (tabActual === 0) {
      cargarDashboard()
    }
  }, [tabActual])

  const cargarDashboard = async () => {
    try {
      setCargando(true)
      setError(null)
      const data = await iaMedicaService.obtenerDashboard()
      setDashboard(data)
    } catch (err: any) {
      console.error('Error al cargar dashboard de IA:', err)
      setError(err.response?.data?.detail || 'Error al cargar dashboard')
    } finally {
      setCargando(false)
    }
  }

  const tabs = [
    { id: 0, name: 'Dashboard', icon: BarChart3 },
    { id: 1, name: 'Asistente de Diagnóstico', icon: Brain },
    { id: 2, name: 'Predicción de Riesgos', icon: AlertTriangle },
    { id: 3, name: 'Recomendaciones', icon: Activity },
    { id: 4, name: 'Interacciones', icon: Pill },
    { id: 5, name: 'Detección de Anomalías', icon: Bug },
  ]

  // Métricas de ejemplo
  const heroMetrics = [
    { label: 'Diagnósticos IA', value: 0 },
    { label: 'Predicciones', value: 0 },
    { label: 'Alertas Activas', value: dashboard?.alertas_criticas?.length || 0 },
    { label: 'Precisión', value: '95%' },
  ]

  return (
    <div className="space-y-8">
      {/* Hero Section - Idéntico a Interconsultas */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-[#4EAAC8] via-[#5BB5D3] to-[#68C0DE] p-8 shadow-2xl">
        <div className="relative z-10 flex flex-col gap-8 lg:flex-row lg:items-center">
          <div className="flex-1 text-white">
            <p className="uppercase text-xs tracking-[0.35em] text-white/70">Panel clínico</p>
            <h1 className="mt-3 text-4xl font-extrabold leading-tight">
              Inteligencia Artificial Médica
            </h1>
            <p className="mt-2 max-w-2xl text-base text-white/85">
              Herramientas avanzadas de IA para diagnóstico, predicción de riesgos y recomendaciones de tratamiento
            </p>
            <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {heroMetrics.map((metric) => (
                <div
                  key={metric.label}
                  className="rounded-2xl bg-white/10 p-4 backdrop-blur ring-1 ring-white/20"
                >
                  <span className="text-xs uppercase tracking-wide text-white/60">
                    {metric.label}
                  </span>
                  <p className="mt-2 text-2xl font-semibold">{metric.value}</p>
                </div>
              ))}
            </div>
          </div>
          <div className="flex flex-shrink-0 items-start gap-3 lg:flex-col">
            <button
              onClick={() => setTabActual(0)}
              className="inline-flex items-center justify-center rounded-2xl border border-white/30 bg-white/10 px-6 py-3 text-white shadow-lg shadow-black/10 backdrop-blur transition hover:bg-white/15"
            >
              <BarChart3 className="mr-2 h-5 w-5" />
              Ver dashboard
            </button>
          </div>
        </div>
        <div className="absolute inset-y-0 right-0 hidden w-1/3 translate-x-12 overflow-hidden opacity-40 lg:block">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.4),_transparent_60%)]" />
          <div className="absolute -bottom-10 right-10 h-48 w-48 rounded-full bg-white/20 blur-3xl" />
        </div>
      </section>

      {/* Error Alert */}
      {error && (
        <div className="rounded-2xl bg-red-50 border border-red-200 p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            <p className="text-red-800">{error}</p>
          </div>
          <button
            onClick={() => setError(null)}
            className="text-red-600 hover:text-red-800 transition-colors"
          >
            ✕
          </button>
        </div>
      )}

      {/* Tabs - Idéntico a Interconsultas */}
      <div className="overflow-x-auto">
        <div className="flex flex-wrap gap-2 pb-4">
          {tabs.map((tab) => {
            const Icon = tab.icon
            const isActive = tabActual === tab.id

            return (
              <button
                key={tab.id}
                onClick={() => setTabActual(tab.id)}
                className={`flex items-center gap-2 rounded-xl border px-4 py-3 text-sm font-medium transition-all duration-300 whitespace-nowrap ${
                  isActive
                    ? 'border-[#4EAAC8] bg-[#4EAAC8]/10 text-[#4EAAC8] shadow-lg'
                    : 'border-slate-200 bg-white text-slate-500 hover:text-slate-900 hover:border-slate-300'
                }`}
              >
                <Icon className={`h-4 w-4 ${isActive ? 'text-[#4EAAC8]' : 'text-slate-400'}`} />
                {tab.name}
              </button>
            )
          })}
        </div>
      </div>

      {/* Tab Content */}
      <div>
        {tabActual === 0 && (
          <div>
            {cargando ? (
              <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
                <p className="text-gray-600 mt-4">Cargando dashboard...</p>
              </div>
            ) : dashboard ? (
              <DashboardIA dashboard={dashboard} onRecargar={cargarDashboard} />
            ) : (
              <div className="bg-blue-50 border border-blue-200 rounded-2xl p-6 text-center">
                <p className="text-blue-800">No hay datos disponibles</p>
              </div>
            )}
          </div>
        )}

        {tabActual === 1 && <AsistenteIA />}
        {tabActual === 2 && <PrediccionRiesgos />}
        {tabActual === 3 && <RecomendacionesTratamiento />}
        {tabActual === 4 && <InteraccionesMedicamentosas />}
        {tabActual === 5 && <DeteccionAnomalias onActualizarDashboard={cargarDashboard} />}
      </div>
    </div>
  )
}
