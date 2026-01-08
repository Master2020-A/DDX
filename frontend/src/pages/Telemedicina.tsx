import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Video, Calendar, Clock, User, Plus, Search } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'

interface ConsultaRemota {
  id: string
  sala_id: string
  paciente: {
    id: string
    nombre: string
  }
  medico: {
    id: string
    nombre: string
  }
  estado: 'programada' | 'en_curso' | 'finalizada' | 'cancelada'
  fecha_programada: string
  fecha_inicio?: string
  fecha_fin?: string
  motivo_consulta: string
  tipo: string
  duracion_minutos?: number
}

const Telemedicina = () => {
  const navigate = useNavigate()
  const { token, user } = useAuthStore()
  
  const [consultas, setConsultas] = useState<ConsultaRemota[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filtroEstado, setFiltroEstado] = useState<string>('todas')

  useEffect(() => {
    cargarConsultas()
  }, [])

  const cargarConsultas = async () => {
    if (!token) {
      setError('No hay token de autenticación')
      setLoading(false)
      return
    }

    try {
      const response = await fetch(
        'http://localhost:8612/api/telemedicina/consultas/programadas',
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      if (!response.ok) {
        throw new Error('Error al cargar consultas')
      }

      const data = await response.json()
      setConsultas(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const abrirSala = (consultaId: string) => {
    navigate(`/telemedicina/sala/${consultaId}`)
  }

  const getEstadoColor = (estado: string) => {
    switch (estado) {
      case 'programada':
        return 'bg-blue-100 text-blue-800'
      case 'en_curso':
        return 'bg-green-100 text-green-800'
      case 'finalizada':
        return 'bg-gray-100 text-gray-800'
      case 'cancelada':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getEstadoTexto = (estado: string) => {
    switch (estado) {
      case 'programada':
        return 'Programada'
      case 'en_curso':
        return 'En Curso'
      case 'finalizada':
        return 'Finalizada'
      case 'cancelada':
        return 'Cancelada'
      default:
        return estado
    }
  }

  const formatearFecha = (fecha: string) => {
    return new Date(fecha).toLocaleString('es-MX', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const consultasFiltradas = consultas.filter((c) => {
    if (filtroEstado === 'todas') return true
    return c.estado === filtroEstado
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando consultas...</p>
        </div>
      </div>
    )
  }

  const totalConsultas = consultas.length
  const programadas = consultas.filter(c => c.estado === 'programada').length
  const enCurso = consultas.filter(c => c.estado === 'en_curso').length
  const finalizadas = consultas.filter(c => c.estado === 'finalizada').length

  const heroMetrics = [
    { label: 'Total', value: totalConsultas },
    { label: 'Programadas', value: programadas },
    { label: 'En Curso', value: enCurso },
    { label: 'Finalizadas', value: finalizadas },
  ]

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-[#4EAAC8] via-[#5BB5D3] to-[#68C0DE] p-8 shadow-2xl">
        <div className="relative z-10 flex flex-col gap-8 lg:flex-row lg:items-center">
          <div className="flex-1 text-white">
            <p className="uppercase text-xs tracking-[0.35em] text-white/70">Panel clínico</p>
            <h1 className="mt-3 text-4xl font-extrabold leading-tight">
              Telemedicina
            </h1>
            <p className="mt-2 max-w-2xl text-base text-white/85">
              Gestiona tus consultas remotas y videollamadas con un resumen ejecutivo en tiempo real
              y acceso rápido a cada sala.
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
              onClick={() => navigate('/consultas')}
              className="inline-flex items-center justify-center rounded-2xl border border-white/30 bg-white/10 px-6 py-3 text-white shadow-lg shadow-black/10 backdrop-blur transition hover:bg-white/15"
            >
              <Plus className="mr-2" size={20} />
              Nueva Consulta
            </button>
          </div>
        </div>
        <div className="absolute inset-y-0 right-0 hidden w-1/3 translate-x-12 overflow-hidden opacity-40 lg:block">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.4),_transparent_60%)]" />
          <div className="absolute -bottom-10 right-10 h-48 w-48 rounded-full bg-white/20 blur-3xl" />
        </div>
      </section>

      {error && (
        <div className="rounded-2xl bg-red-50 border border-red-200 text-red-700 px-6 py-4">
          {error}
        </div>
      )}

      {/* Filtros */}
      <div className="rounded-2xl border border-slate-100 bg-white/70 p-1 shadow-sm">
        <div className="flex flex-col gap-4 rounded-2xl bg-white/80 p-6 lg:flex-row lg:items-center">
          <div className="flex items-center gap-2 text-slate-500">
            <Search className="w-5 h-5" />
            <span className="text-sm font-medium">Filtrar por estado:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setFiltroEstado('todas')}
              className={`px-4 py-2 rounded-2xl font-medium text-sm transition-colors ${
                filtroEstado === 'todas'
                  ? 'bg-[#4EAAC8] text-white shadow-lg'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              Todas
            </button>
            <button
              onClick={() => setFiltroEstado('programada')}
              className={`px-4 py-2 rounded-2xl font-medium text-sm transition-colors ${
                filtroEstado === 'programada'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              Programadas
            </button>
            <button
              onClick={() => setFiltroEstado('en_curso')}
              className={`px-4 py-2 rounded-2xl font-medium text-sm transition-colors ${
                filtroEstado === 'en_curso'
                  ? 'bg-green-600 text-white shadow-lg'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              En Curso
            </button>
            <button
              onClick={() => setFiltroEstado('finalizada')}
              className={`px-4 py-2 rounded-2xl font-medium text-sm transition-colors ${
                filtroEstado === 'finalizada'
                  ? 'bg-gray-600 text-white shadow-lg'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              Finalizadas
            </button>
          </div>
          <div className="flex gap-2 text-xs text-slate-500 lg:ml-auto">
            <span className="rounded-full border border-slate-200 px-4 py-2">
              {consultasFiltradas.length} resultados
            </span>
          </div>
        </div>
      </div>

      {/* Lista de Consultas */}
      {consultasFiltradas.length === 0 ? (
        <div className="rounded-3xl border border-dashed border-slate-200 bg-white/70 p-12 text-center shadow-sm">
          <Video className="mx-auto mb-4 text-slate-300" size={48} />
          <p className="text-lg font-semibold text-slate-700">
            No hay consultas {filtroEstado !== 'todas' ? getEstadoTexto(filtroEstado).toLowerCase() : ''}
          </p>
          <p className="mt-2 text-sm text-slate-500">
            Las consultas de telemedicina aparecerán aquí
          </p>
          <button
            onClick={() => navigate('/consultas')}
            className="mt-6 inline-flex items-center gap-2 rounded-2xl bg-[#4EAAC8] px-6 py-3 text-sm font-semibold text-white shadow-lg transition hover:bg-[#3d8aa3]"
          >
            <Plus className="w-5 h-5" />
            Crear Primera Consulta
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {consultasFiltradas.map((consulta) => (
            <div
              key={consulta.id}
              className="group relative overflow-hidden rounded-3xl border border-slate-100 bg-white p-6 shadow-sm ring-1 ring-transparent transition hover:-translate-y-1 hover:border-[#4EAAC8]/30 hover:shadow-2xl hover:ring-[#4EAAC8]/20 cursor-pointer"
              onClick={() => abrirSala(consulta.id)}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex flex-wrap items-center gap-2 mb-3">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${getEstadoColor(
                        consulta.estado
                      )}`}
                    >
                      {getEstadoTexto(consulta.estado)}
                    </span>
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700">
                      Sala: {consulta.sala_id}
                    </span>
                  </div>

                  <h3 className="text-lg font-semibold text-slate-900 mb-3 group-hover:text-[#4EAAC8]">
                    {consulta.motivo_consulta}
                  </h3>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                    <div className="flex items-center gap-2 text-slate-600">
                      <User className="w-4 h-4 text-slate-400" />
                      <span>
                        Paciente: <strong className="text-slate-900">{consulta.paciente.nombre}</strong>
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-slate-600">
                      <User className="w-4 h-4 text-slate-400" />
                      <span>
                        Médico: <strong className="text-slate-900">{consulta.medico.nombre}</strong>
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-slate-600">
                      <Calendar className="w-4 h-4 text-slate-400" />
                      <span>{formatearFecha(consulta.fecha_programada)}</span>
                    </div>
                    {consulta.duracion_minutos && (
                      <div className="flex items-center gap-2 text-slate-600">
                        <Clock className="w-4 h-4 text-slate-400" />
                        <span>Duración: {consulta.duracion_minutos} min</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex-shrink-0">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      abrirSala(consulta.id)
                    }}
                    className={`inline-flex items-center gap-2 rounded-2xl px-5 py-3 text-sm font-semibold shadow-lg transition ${
                      consulta.estado === 'programada' || consulta.estado === 'en_curso'
                        ? 'bg-[#4EAAC8] text-white hover:bg-[#3d8aa3]'
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                    }`}
                  >
                    <Video className="w-5 h-5" />
                    {consulta.estado === 'en_curso'
                      ? 'Iniciar'
                      : consulta.estado === 'programada'
                      ? 'Iniciar'
                      : 'Ver Detalles'}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Información adicional */}
      <div className="rounded-3xl border border-[#4EAAC8]/20 bg-[#4EAAC8]/5 p-6 shadow-sm">
        <div className="flex items-start gap-4">
          <Video className="w-6 h-6 text-[#4EAAC8] mt-1 flex-shrink-0" />
          <div>
            <h3 className="font-semibold text-[#3d8aa3] mb-2">
              ¿Cómo funciona la telemedicina?
            </h3>
            <ul className="text-sm text-slate-700 space-y-1">
              <li>• Las consultas se crean desde el módulo de Consultas</li>
              <li>• Puedes iniciar una videollamada haciendo clic en "Iniciar"</li>
              <li>• Durante la consulta tendrás acceso a video, audio y chat</li>
              <li>• Al finalizar, se guardará el registro completo de la consulta</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Telemedicina
