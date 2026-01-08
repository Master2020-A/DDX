import { useState } from 'react'
import { Send, Inbox, CheckCircle, TrendingUp, ArrowRightLeft, Plus } from 'lucide-react'
import MisSolicitudes from '@/components/interconsultas/MisSolicitudes'
import MisInterconsultas from '@/components/interconsultas/MisInterconsultas'
import NuevaSolicitud from '@/components/interconsultas/NuevaSolicitud'
import Estadisticas from '@/components/interconsultas/Estadisticas'

const Interconsultas = () => {
  const [tabActual, setTabActual] = useState(0)
  const [actualizarKey, setActualizarKey] = useState(0)

  const handleActualizar = () => {
    setActualizarKey(prev => prev + 1)
  }

  const tabs = [
    { id: 0, name: 'Mis Solicitudes', icon: Send },
    { id: 1, name: 'Mis Interconsultas', icon: Inbox },
    { id: 2, name: 'Nueva Solicitud', icon: CheckCircle },
    { id: 3, name: 'Estadísticas', icon: TrendingUp },
  ]

  // Métricas de ejemplo - deberían venir de una API
  const heroMetrics = [
    { label: 'Solicitudes Enviadas', value: 0 },
    { label: 'Interconsultas Recibidas', value: 0 },
    { label: 'Pendientes', value: 0 },
    { label: 'Completadas', value: 0 },
  ]

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-[#4EAAC8] via-[#5BB5D3] to-[#68C0DE] p-8 shadow-2xl">
        <div className="relative z-10 flex flex-col gap-8 lg:flex-row lg:items-center">
          <div className="flex-1 text-white">
            <p className="uppercase text-xs tracking-[0.35em] text-white/70">Panel clínico</p>
            <h1 className="mt-3 text-4xl font-extrabold leading-tight">
              Interconsultas
            </h1>
            <p className="mt-2 max-w-2xl text-base text-white/85">
              Gestión de solicitudes de interconsulta y comunicación entre especialistas
              con seguimiento en tiempo real.
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
              onClick={() => setTabActual(2)}
              className="inline-flex items-center justify-center rounded-2xl border border-white/30 bg-white/10 px-6 py-3 text-white shadow-lg shadow-black/10 backdrop-blur transition hover:bg-white/15"
            >
              <Plus className="mr-2" size={20} />
              Nueva Solicitud
            </button>
          </div>
        </div>
        <div className="absolute inset-y-0 right-0 hidden w-1/3 translate-x-12 overflow-hidden opacity-40 lg:block">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.4),_transparent_60%)]" />
          <div className="absolute -bottom-10 right-10 h-48 w-48 rounded-full bg-white/20 blur-3xl" />
        </div>
      </section>

      {/* Tabs */}
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
      <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-xl min-h-[600px]">
        {tabActual === 0 && <MisSolicitudes key={actualizarKey} onActualizar={handleActualizar} />}
        {tabActual === 1 && <MisInterconsultas key={actualizarKey} onActualizar={handleActualizar} />}
        {tabActual === 2 && <NuevaSolicitud onSuccess={handleActualizar} />}
        {tabActual === 3 && <Estadisticas key={actualizarKey} />}
      </div>
    </div>
  )
}

export default Interconsultas
