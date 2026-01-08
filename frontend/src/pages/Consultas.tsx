import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Calendar, Search, Filter, User } from 'lucide-react'
import api from '@/lib/api'
import { Consulta, Paciente } from '@/types'
import { formatDateTime } from '@/lib/utils'

const Consultas = () => {
  const [consultas, setConsultas] = useState<Consulta[]>([])
  const [pacientes, setPacientes] = useState<{[key: string]: Paciente}>({})
  const [loading, setLoading] = useState(true)
  const [filtro, setFiltro] = useState('')
  const [estadoFiltro, setEstadoFiltro] = useState<string>('todas')

  useEffect(() => {
    fetchConsultas()
  }, [])

  const fetchConsultas = async () => {
    try {
      setLoading(true)
      const [consultasRes, pacientesRes] = await Promise.all([
        api.get('/consultas/'),
        api.get('/pacientes/')
      ])

      setConsultas(consultasRes.data || [])
      
      // Crear un mapa de pacientes por ID
      const pacientesMap: {[key: string]: Paciente} = {}
      pacientesRes.data.forEach((p: Paciente) => {
        pacientesMap[p.id] = p
      })
      setPacientes(pacientesMap)
    } catch (error) {
      console.error('Error fetching consultas:', error)
    } finally {
      setLoading(false)
    }
  }

  const consultasFiltradas = consultas.filter(consulta => {
    const paciente = pacientes[consulta.paciente_id]
    const matchFiltro = !filtro || 
      paciente?.nombre_completo?.toLowerCase().includes(filtro.toLowerCase()) ||
      consulta.motivo_consulta?.toLowerCase().includes(filtro.toLowerCase())
    
    const matchEstado = estadoFiltro === 'todas' || consulta.estado === estadoFiltro
    
    return matchFiltro && matchEstado
  })

  const getEstadoBadge = (estado: string) => {
    const badges: {[key: string]: string} = {
      'completada': 'bg-green-100 text-green-700',
      'en_proceso': 'bg-yellow-100 text-yellow-700',
      'cancelada': 'bg-red-100 text-red-700',
      'programada': 'bg-blue-100 text-blue-700'
    }
    return badges[estado] || 'bg-gray-100 text-gray-700'
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Cargando consultas...</p>
      </div>
    )
  }

  const totalConsultas = consultas.length
  const enProceso = consultas.filter(c => c.estado === 'en_proceso').length
  const completadas = consultas.filter(c => c.estado === 'completada').length
  const hoy = consultas.filter(c => 
    c.fecha_hora?.startsWith(new Date().toISOString().split('T')[0])
  ).length

  const heroMetrics = [
    { label: 'Total', value: totalConsultas },
    { label: 'En Proceso', value: enProceso },
    { label: 'Completadas', value: completadas },
    { label: 'Hoy', value: hoy },
  ]

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-indigo-600 via-sky-500 to-cyan-400 p-8 shadow-2xl">
        <div className="relative z-10 flex flex-col gap-8 lg:flex-row lg:items-center">
          <div className="flex-1 text-white">
            <p className="uppercase text-xs tracking-[0.35em] text-white/70">Panel clínico</p>
            <h1 className="mt-3 text-4xl font-extrabold leading-tight">
              Consultas
            </h1>
            <p className="mt-2 max-w-2xl text-base text-white/85">
              Gestiona y monitorea todas las consultas médicas con un resumen ejecutivo en tiempo real
              y acceso rápido a cada expediente.
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
        </div>
        <div className="absolute inset-y-0 right-0 hidden w-1/3 translate-x-12 overflow-hidden opacity-40 lg:block">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.4),_transparent_60%)]" />
          <div className="absolute -bottom-10 right-10 h-48 w-48 rounded-full bg-white/20 blur-3xl" />
        </div>
      </section>

      {/* Filtros */}
      <div className="rounded-2xl border border-slate-100 bg-white/70 p-1 shadow-sm">
        <div className="flex flex-col gap-4 rounded-2xl bg-white/80 p-6 lg:flex-row lg:items-center">
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Buscar por paciente o motivo..."
              value={filtro}
              onChange={(e) => setFiltro(e.target.value)}
              className="w-full rounded-2xl border border-slate-200 bg-slate-50/70 py-3 pl-12 pr-4 text-sm text-slate-700 placeholder:text-slate-400 focus:border-indigo-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
            />
          </div>
          <div className="relative lg:w-48">
            <Filter className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <select
              value={estadoFiltro}
              onChange={(e) => setEstadoFiltro(e.target.value)}
              className="w-full rounded-2xl border border-slate-200 bg-slate-50/70 py-3 pl-12 pr-4 text-sm text-slate-700 focus:border-indigo-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
            >
              <option value="todas">Todas</option>
              <option value="programada">Programadas</option>
              <option value="en_proceso">En proceso</option>
              <option value="completada">Completadas</option>
              <option value="cancelada">Canceladas</option>
            </select>
          </div>
          <div className="flex gap-2 text-xs text-slate-500">
            <span className="rounded-full border border-slate-200 px-4 py-2">
              {consultasFiltradas.length} resultados
            </span>
          </div>
        </div>
      </div>

      {/* Lista de consultas */}
      {consultasFiltradas.length === 0 ? (
        <div className="rounded-3xl border border-dashed border-slate-200 bg-white/70 p-12 text-center shadow-sm">
          <Calendar className="mx-auto mb-4 text-slate-300" size={48} />
          <p className="text-lg font-semibold text-slate-700">No hay consultas que coincidan con los filtros</p>
          <p className="mt-2 text-sm text-slate-500">
            Intenta ajustar los filtros de búsqueda o estado.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {consultasFiltradas.map((consulta) => {
            const paciente = pacientes[consulta.paciente_id]
            return (
              <Link
                key={consulta.id}
                to={`/consultas/${consulta.id}`}
                className="group relative overflow-hidden rounded-3xl border border-slate-100 bg-white p-6 shadow-sm ring-1 ring-transparent transition hover:-translate-y-1 hover:border-indigo-100 hover:shadow-2xl hover:ring-indigo-100"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex gap-4 flex-1">
                    <div className="flex-shrink-0">
                      <User size={24} className="text-indigo-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex flex-wrap items-center gap-2 mb-3">
                        <span className="font-semibold text-slate-900 group-hover:text-indigo-600">
                          {paciente?.nombre_completo || 'Paciente desconocido'}
                        </span>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getEstadoBadge(consulta.estado)}`}>
                          {consulta.estado.replace('_', ' ')}
                        </span>
                        {consulta.tipo_consulta && (
                          <span className="px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700 capitalize">
                            {consulta.tipo_consulta.replace('_', ' ')}
                          </span>
                        )}
                      </div>
                      <p className="text-slate-900 mb-2">
                        <span className="font-medium text-slate-500">Motivo:</span> {consulta.motivo_consulta}
                      </p>
                      {consulta.sintomas && consulta.sintomas.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-3">
                          {consulta.sintomas.slice(0, 3).map((sintoma, idx) => (
                            <span key={idx} className="px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-xs font-medium">
                              {sintoma}
                            </span>
                          ))}
                          {consulta.sintomas.length > 3 && (
                            <span className="px-3 py-1 bg-slate-100 text-slate-600 rounded-full text-xs font-medium">
                              +{consulta.sintomas.length - 3} más
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex-shrink-0 text-right">
                    <div className="flex items-center text-slate-500 text-sm mb-2">
                      <Calendar size={14} className="mr-1" />
                      {formatDateTime(consulta.fecha_hora)}
                    </div>
                    <span className="text-xs text-indigo-500">Ver detalles →</span>
                  </div>
                </div>
              </Link>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default Consultas
