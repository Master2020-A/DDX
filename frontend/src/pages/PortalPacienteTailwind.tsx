import { useEffect, useMemo, useState } from 'react'
import {
  Activity,
  AlertCircle,
  Calendar,
  CalendarClock,
  CheckCircle2,
  Clock,
  CreditCard,
  FileText,
  Loader2,
  MessageSquare,
  Pill,
  Plus,
  Settings,
  ShieldCheck,
} from 'lucide-react'
import portalPacienteService, {
  DashboardData,
  CitaPaciente,
  SolicitudEstudio,
  PagoServicio,
  MensajePacienteMedico,
  RecordatorioMedicamento,
  ConfiguracionPortal,
} from '@/services/portalPacienteService'

const TABS = [
  { id: 'dashboard', label: 'Dashboard', icon: Activity },
  { id: 'citas', label: 'Citas', icon: Calendar },
  { id: 'estudios', label: 'Estudios', icon: FileText },
  { id: 'pagos', label: 'Pagos', icon: CreditCard },
  { id: 'mensajes', label: 'Mensajes', icon: MessageSquare },
  { id: 'recordatorios', label: 'Medicamentos', icon: Pill },
  { id: 'configuracion', label: 'Configuración', icon: Settings },
] as const

type TabId = (typeof TABS)[number]['id']

const PACIENTE_ID = '49bfb1e1-699c-4161-90cd-9162c226259c'

type NuevaCitaForm = {
  tipo_cita: string
  especialidad_solicitada: string
  motivo_consulta: string
  fecha_solicitada: string
  hora_solicitada: string
  notas_paciente: string
}

type NuevoEstudioForm = {
  tipo_estudio: string
  nombre_estudio: string
  descripcion: string
  prioridad: string
}

type NuevoMensajeForm = {
  medico_id: string
  asunto: string
  mensaje: string
}

type NuevoRecordatorioForm = {
  nombre_medicamento: string
  dosis: string
  frecuencia: string
  horarios: string
  indicaciones: string
}

export default function PortalPaciente() {
  const [activeTab, setActiveTab] = useState<TabId>('dashboard')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [citas, setCitas] = useState<CitaPaciente[]>([])
  const [solicitudes, setSolicitudes] = useState<SolicitudEstudio[]>([])
  const [pagos, setPagos] = useState<PagoServicio[]>([])
  const [mensajes, setMensajes] = useState<MensajePacienteMedico[]>([])
  const [recordatorios, setRecordatorios] = useState<RecordatorioMedicamento[]>([])
  const [configuracion, setConfiguracion] = useState<ConfiguracionPortal | null>(null)

  const [showCitaModal, setShowCitaModal] = useState(false)
  const [showEstudioModal, setShowEstudioModal] = useState(false)
  const [showMensajeModal, setShowMensajeModal] = useState(false)
  const [showRecordatorioModal, setShowRecordatorioModal] = useState(false)
  const [saving, setSaving] = useState(false)

  const [citaForm, setCitaForm] = useState<NuevaCitaForm>({
    tipo_cita: 'consulta',
    especialidad_solicitada: '',
    motivo_consulta: '',
    fecha_solicitada: '',
    hora_solicitada: '',
    notas_paciente: '',
  })

  const [estudioForm, setEstudioForm] = useState<NuevoEstudioForm>({
    tipo_estudio: 'laboratorio',
    nombre_estudio: '',
    descripcion: '',
    prioridad: 'normal',
  })

  const [mensajeForm, setMensajeForm] = useState<NuevoMensajeForm>({
    medico_id: '',
    asunto: '',
    mensaje: '',
  })

  const [recordatorioForm, setRecordatorioForm] = useState<NuevoRecordatorioForm>({
    nombre_medicamento: '',
    dosis: '',
    frecuencia: 'Cada 8 horas',
    horarios: '',
    indicaciones: '',
  })

  const [configDraft, setConfigDraft] = useState<ConfiguracionPortal | null>(null)
  const [savingConfig, setSavingConfig] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)
      try {
        switch (activeTab) {
          case 'dashboard':
            setDashboardData(await portalPacienteService.getDashboard(PACIENTE_ID))
            break
          case 'citas':
            setCitas(await portalPacienteService.getCitas(PACIENTE_ID))
            break
          case 'estudios':
            setSolicitudes(await portalPacienteService.getSolicitudesEstudios(PACIENTE_ID))
            break
          case 'pagos':
            setPagos(await portalPacienteService.getPagos(PACIENTE_ID))
            break
          case 'mensajes':
            setMensajes(await portalPacienteService.getMensajes(PACIENTE_ID))
            break
          case 'recordatorios':
            setRecordatorios(await portalPacienteService.getRecordatorios(PACIENTE_ID, true))
            break
          case 'configuracion':
            const cfg = await portalPacienteService.getConfiguracion(PACIENTE_ID)
            setConfiguracion(cfg)
            setConfigDraft(cfg)
            break
        }
      } catch (err: any) {
        console.error(err)
        setError(err.response?.data?.detail || 'No pudimos cargar la información')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [activeTab])

  const refreshTab = () => {
    setActiveTab((prev) => prev)
  }

  const metrics = useMemo(() => {
    const dash = dashboardData
    const safe = (value?: number | null) => (typeof value === 'number' ? value.toString() : '0')

    if (!dash) {
      return [
        { label: 'Citas pendientes', value: '0' },
        { label: 'Estudios pendientes', value: '0' },
        { label: 'Mensajes sin leer', value: '0' },
        { label: 'Recordatorios activos', value: '0' },
      ]
    }

    return [
      { label: 'Citas pendientes', value: safe(dash.citas_pendientes) },
      { label: 'Estudios pendientes', value: safe(dash.solicitudes_pendientes) },
      { label: 'Mensajes sin leer', value: safe(dash.mensajes_no_leidos) },
      { label: 'Recordatorios activos', value: safe(dash.recordatorios_activos) },
    ]
  }, [dashboardData])

  const estadoPill = (estado: string) => {
    const map: Record<string, { text: string; className: string }> = {
      solicitada: { text: 'Solicitada', className: 'bg-amber-100 text-amber-800' },
      confirmada: { text: 'Confirmada', className: 'bg-emerald-100 text-emerald-700' },
      cancelada: { text: 'Cancelada', className: 'bg-rose-100 text-rose-700' },
      en_proceso: { text: 'En proceso', className: 'bg-indigo-100 text-indigo-700' },
      aprobada: { text: 'Aprobada', className: 'bg-emerald-100 text-emerald-700' },
      pendiente: { text: 'Pendiente', className: 'bg-slate-100 text-slate-600' },
      pagado: { text: 'Pagado', className: 'bg-emerald-100 text-emerald-700' },
    }
    const badge = map[estado] || { text: estado, className: 'bg-slate-100 text-slate-600' }
    return <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${badge.className}`}>{badge.text}</span>
  }

  const formatFecha = (fecha: string) =>
    new Date(fecha).toLocaleDateString('es-MX', { year: 'numeric', month: 'short', day: 'numeric' })

  const formatHora = (hora?: string | null) =>
    hora ? new Date(`2000-01-01T${hora}`).toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' }) : null

  const renderListState = <T,>(items: T[], renderItem: (item: T) => JSX.Element, emptyText: string) => {
    if (loading) {
      return <div className="py-12 text-center text-slate-500">Cargando…</div>
    }
    if (!items.length) {
      return (
        <div className="rounded-3xl border border-dashed border-slate-200 bg-white p-12 text-center text-slate-500">
          {emptyText}
        </div>
      )
    }
    return <div className="space-y-3">{items.map(renderItem)}</div>
  }

  const handleCrearCita = async () => {
    setSaving(true)
    try {
      await portalPacienteService.crearCita({
        ...citaForm,
        paciente_id: PACIENTE_ID,
      })
      setShowCitaModal(false)
      setCitaForm({
        tipo_cita: 'consulta',
        especialidad_solicitada: '',
        motivo_consulta: '',
        fecha_solicitada: '',
        hora_solicitada: '',
        notas_paciente: '',
      })
      refreshTab()
    } catch (err) {
      console.error(err)
      setError('No pudimos registrar la cita')
    } finally {
      setSaving(false)
    }
  }

  const handleCrearEstudio = async () => {
    setSaving(true)
    try {
      await portalPacienteService.crearSolicitudEstudio({
        ...estudioForm,
        paciente_id: PACIENTE_ID,
      })
      setShowEstudioModal(false)
      setEstudioForm({ tipo_estudio: 'laboratorio', nombre_estudio: '', descripcion: '', prioridad: 'normal' })
      refreshTab()
    } catch (err) {
      console.error(err)
      setError('No pudimos registrar la solicitud')
    } finally {
      setSaving(false)
    }
  }

  const handleEnviarMensaje = async () => {
    setSaving(true)
    try {
      await portalPacienteService.enviarMensaje({
        ...mensajeForm,
        paciente_id: PACIENTE_ID,
      })
      setShowMensajeModal(false)
      setMensajeForm({ medico_id: '', asunto: '', mensaje: '' })
      refreshTab()
    } catch (err) {
      console.error(err)
      setError('No pudimos enviar el mensaje')
    } finally {
      setSaving(false)
    }
  }

  const handleCrearRecordatorio = async () => {
    setSaving(true)
    try {
      await portalPacienteService.crearRecordatorio({
        paciente_id: PACIENTE_ID,
        nombre_medicamento: recordatorioForm.nombre_medicamento,
        dosis: recordatorioForm.dosis,
        frecuencia: recordatorioForm.frecuencia,
        horarios: recordatorioForm.horarios
          .split(',')
          .map((h) => h.trim())
          .filter(Boolean),
        indicaciones: recordatorioForm.indicaciones,
        activo: true,
      })
      setShowRecordatorioModal(false)
      setRecordatorioForm({ nombre_medicamento: '', dosis: '', frecuencia: 'Cada 8 horas', horarios: '', indicaciones: '' })
      refreshTab()
    } catch (err) {
      console.error(err)
      setError('No pudimos crear el recordatorio')
    } finally {
      setSaving(false)
    }
  }

  const handleCancelarCita = async (citaId: string) => {
    try {
      await portalPacienteService.cancelarCita(citaId, 'Cancelado desde portal del paciente')
      refreshTab()
    } catch (err) {
      console.error(err)
      setError('No pudimos cancelar la cita')
    }
  }

  const handleConfigSave = async () => {
    if (!configDraft) return
    setSavingConfig(true)
    try {
      await portalPacienteService.actualizarConfiguracion(PACIENTE_ID, configDraft)
      setConfiguracion(configDraft)
      setError(null)
    } catch (err) {
      console.error(err)
      setError('No pudimos guardar la configuración')
    } finally {
      setSavingConfig(false)
    }
  }

  const renderDashboard = () => (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {metrics.map((metric) => (
          <div key={metric.label} className="rounded-3xl border border-slate-100 bg-white/90 p-5 shadow-sm">
            <p className="text-xs uppercase tracking-wide text-slate-500">{metric.label}</p>
            <p className="mt-2 text-3xl font-semibold text-slate-900">{metric.value}</p>
          </div>
        ))}
      </div>

      {dashboardData?.proxima_cita && (
        <div className="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-500">Próxima cita</p>
              <p className="text-xl font-semibold text-slate-900">
                {dashboardData.proxima_cita.especialidad_solicitada || dashboardData.proxima_cita.tipo_cita}
              </p>
              <p className="text-sm text-slate-500">{dashboardData.proxima_cita.motivo_consulta}</p>
            </div>
            {estadoPill(dashboardData.proxima_cita.estado)}
          </div>
          <div className="mt-4 flex flex-wrap gap-4 text-sm text-slate-600">
            <span className="flex items-center gap-1"><CalendarClock className="h-4 w-4" />{formatFecha(dashboardData.proxima_cita.fecha_solicitada)}</span>
            {formatHora(dashboardData.proxima_cita.hora_solicitada) && (
              <span className="flex items-center gap-1"><Clock className="h-4 w-4" />{formatHora(dashboardData.proxima_cita.hora_solicitada)}</span>
            )}
          </div>
        </div>
      )}
    </div>
  )

  const renderCitas = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900">Mis citas</h2>
        <button
          className="inline-flex items-center gap-2 rounded-2xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30"
          onClick={() => setShowCitaModal(true)}
        >
          <Plus className="h-4 w-4" /> Nueva cita
        </button>
      </div>
      {renderListState(citas, (cita) => (
        <div key={cita.id} className="rounded-3xl border border-slate-100 bg-white p-5 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <p className="text-base font-semibold text-slate-900">{cita.especialidad_solicitada || cita.tipo_cita}</p>
              <p className="text-sm text-slate-500">{cita.motivo_consulta}</p>
            </div>
            <div className="flex items-center gap-2">
              {estadoPill(cita.estado)}
              {cita.estado !== 'cancelada' && (
                <button
                  onClick={() => handleCancelarCita(cita.id)}
                  className="text-xs font-semibold text-rose-600 hover:underline"
                >
                  Cancelar
                </button>
              )}
            </div>
          </div>
          <div className="mt-3 flex flex-wrap gap-4 text-sm text-slate-600">
            <span className="flex items-center gap-1"><Calendar className="h-4 w-4" />{formatFecha(cita.fecha_solicitada)}</span>
            {formatHora(cita.hora_solicitada) && (
              <span className="flex items-center gap-1"><Clock className="h-4 w-4" />{formatHora(cita.hora_solicitada)}</span>
            )}
          </div>
        </div>
      ), 'No tienes citas programadas')}
    </div>
  )

  const renderSolicitudes = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900">Solicitudes de estudios</h2>
        <button
          className="inline-flex items-center gap-2 rounded-2xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30"
          onClick={() => setShowEstudioModal(true)}
        >
          <Plus className="h-4 w-4" /> Nueva solicitud
        </button>
      </div>
      {renderListState(solicitudes, (solicitud) => (
        <div key={solicitud.id} className="rounded-3xl border border-slate-100 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-base font-semibold text-slate-900">{solicitud.nombre_estudio}</p>
              <p className="text-sm text-slate-500">{solicitud.descripcion || 'Sin descripción'}</p>
            </div>
            {estadoPill(solicitud.estado)}
          </div>
          <p className="mt-2 text-sm text-slate-500">Solicitado: {formatFecha(solicitud.fecha_solicitud)}</p>
          {solicitud.resultado_disponible && (
            <span className="mt-3 inline-flex items-center gap-1 rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700">
              ✓ Resultado disponible
            </span>
          )}
        </div>
      ), 'No hay solicitudes registradas')}
    </div>
  )

  const renderPagos = () => (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-slate-900">Pagos y facturación</h2>
      {renderListState(pagos, (pago) => (
        <div key={pago.id} className="rounded-3xl border border-slate-100 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-base font-semibold text-slate-900">{pago.concepto}</p>
              <p className="text-sm text-slate-500">Referencia: {pago.referencia_pago || 'N/D'}</p>
            </div>
            <ShieldCheck className={`h-5 w-5 ${pago.estado === 'pagado' ? 'text-emerald-500' : 'text-slate-300'}`} />
          </div>
          <div className="mt-2 text-sm text-slate-600">
            <p>Monto: ${pago.monto.toFixed(2)} {pago.moneda}</p>
            <p>Fecha: {pago.fecha_pago ? formatFecha(pago.fecha_pago) : 'Pendiente'}</p>
          </div>
        </div>
      ), 'No hay pagos registrados')}
    </div>
  )

  const renderMensajes = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900">Mensajes</h2>
        <button
          className="inline-flex items-center gap-2 rounded-2xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30"
          onClick={() => setShowMensajeModal(true)}
        >
          <Plus className="h-4 w-4" /> Nuevo mensaje
        </button>
      </div>
      {renderListState(mensajes, (mensaje) => (
        <div key={mensaje.id} className="rounded-3xl border border-slate-100 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-base font-semibold text-slate-900">{mensaje.asunto || 'Sin asunto'}</p>
              <p className="text-sm text-slate-500">Mensaje #{mensaje.id}</p>
            </div>
            {estadoPill(mensaje.estado)}
          </div>
          <p className="mt-3 text-sm text-slate-600 line-clamp-3">{mensaje.mensaje}</p>
        </div>
      ), 'No tienes mensajes nuevos')}
    </div>
  )

  const renderRecordatorios = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900">Recordatorios de medicamentos</h2>
        <button
          className="inline-flex items-center gap-2 rounded-2xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30"
          onClick={() => setShowRecordatorioModal(true)}
        >
          <Plus className="h-4 w-4" /> Nuevo recordatorio
        </button>
      </div>
      {renderListState(recordatorios, (rec) => (
        <div key={rec.id} className="rounded-3xl border border-slate-100 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-base font-semibold text-slate-900">{rec.nombre_medicamento}</p>
              <p className="text-sm text-slate-500">{rec.dosis} — {rec.frecuencia}</p>
            </div>
            <CheckCircle2 className={`h-5 w-5 ${rec.activo ? 'text-emerald-500' : 'text-slate-300'}`} />
          </div>
          <p className="mt-3 text-sm text-slate-500">Horarios: {rec.horarios.join(', ')}</p>
        </div>
      ), 'No hay recordatorios activos')}
    </div>
  )

  const renderConfiguracion = () => (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-slate-900">Preferencias del portal</h2>
      {loading ? (
        <div className="py-12 text-center text-slate-500">Cargando…</div>
      ) : configDraft ? (
        <div className="space-y-3">
          {[
            { label: 'Notificaciones por email', key: 'notificaciones_email' },
            { label: 'Notificaciones por SMS', key: 'notificaciones_sms' },
            { label: 'Notificaciones push', key: 'notificaciones_push' },
            { label: 'Recordatorios de citas', key: 'recordatorios_citas' },
            { label: 'Recordatorios de medicamentos', key: 'recordatorios_medicamentos' },
            { label: 'Recordatorios de estudios', key: 'recordatorios_estudios' },
            { label: 'Compartir datos para investigación', key: 'compartir_datos_investigacion' },
          ].map(({ label, key }) => (
            <label key={key} className="flex items-center justify-between rounded-3xl border border-slate-100 bg-white px-4 py-3 text-sm font-semibold text-slate-900 shadow-sm">
              <span>{label}</span>
              <input
                type="checkbox"
                className="h-4 w-4 accent-indigo-600"
                checked={(configDraft as any)[key] as boolean}
                onChange={(e) => setConfigDraft((prev) => prev ? { ...prev, [key]: e.target.checked } : prev)}
              />
            </label>
          ))}
          <button
            onClick={handleConfigSave}
            disabled={savingConfig}
            className="inline-flex items-center gap-2 rounded-2xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30 disabled:opacity-60"
          >
            {savingConfig ? 'Guardando…' : 'Guardar preferencias'}
          </button>
        </div>
      ) : (
        <div className="rounded-3xl border border-slate-100 bg-white p-6 text-center text-slate-500">
          No se pudo cargar la configuración
        </div>
      )}
    </div>
  )

  const heroMetrics = [
    { label: 'Citas pendientes', value: citas.filter(c => c.estado === 'solicitada').length },
    { label: 'Estudios pendientes', value: solicitudes.filter(s => s.estado === 'solicitado').length },
    { label: 'Mensajes sin leer', value: mensajes.filter(m => !m.leido).length },
    { label: 'Recordatorios activos', value: recordatorios.filter(r => r.activo).length },
  ]

  return (
    <div className="space-y-8">
      {/* Hero Section with Gradient */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-indigo-600 via-sky-500 to-cyan-400 p-8 shadow-2xl">
        <div className="relative z-10 flex flex-col gap-8 lg:flex-row lg:items-center">
          <div className="flex-1 text-white">
            <p className="uppercase text-xs tracking-[0.35em] text-white/70">Panel clínico</p>
            <h1 className="mt-3 text-4xl font-extrabold leading-tight">
              Portal del Paciente
            </h1>
            <p className="mt-2 max-w-2xl text-base text-white/85">
              Gestiona tu información médica, citas, estudios y comunicación con tu equipo de salud
              desde un solo lugar.
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

      {/* Tabs Navigation */}
      <div className="rounded-2xl border border-slate-100 bg-white/70 p-1 shadow-sm">
        <div className="flex gap-2 overflow-x-auto rounded-2xl bg-white/80 p-2">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 whitespace-nowrap rounded-xl px-4 py-2.5 text-sm font-semibold transition-all ${
                activeTab === tab.id
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/30'
                  : 'text-slate-700 hover:bg-slate-50'
              }`}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content Area */}
      <div className="rounded-3xl border border-slate-100 bg-white/90 p-6 shadow-xl">
          {error && (
            <div className="mb-4 rounded-2xl bg-red-50 p-4 text-sm text-red-700">
              {error}
            </div>
          )}
          {activeTab === 'dashboard' && renderDashboard()}
          {activeTab === 'citas' && renderCitas()}
          {activeTab === 'estudios' && renderSolicitudes()}
          {activeTab === 'pagos' && renderPagos()}
          {activeTab === 'mensajes' && renderMensajes()}
          {activeTab === 'recordatorios' && renderRecordatorios()}
          {activeTab === 'configuracion' && renderConfiguracion()}
      </div>

      {/* Modal: Nueva Cita */}
      {showCitaModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-lg rounded-3xl bg-white p-6 shadow-2xl">
            <h3 className="mb-4 text-xl font-bold text-slate-900">Solicitar nueva cita</h3>
            <div className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">Tipo de cita</label>
                <select
                  value={citaForm.tipo_cita}
                  onChange={(e) => setCitaForm({ ...citaForm, tipo_cita: e.target.value })}
                  className="w-full rounded-xl border border-slate-200 px-4 py-2 focus:border-indigo-500 focus:outline-none"
                >
                  <option value="consulta">Consulta</option>
                  <option value="seguimiento">Seguimiento</option>
                  <option value="urgencia">Urgencia</option>
                </select>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">Especialidad</label>
                <input
                  type="text"
                  value={citaForm.especialidad_solicitada}
                  onChange={(e) => setCitaForm({ ...citaForm, especialidad_solicitada: e.target.value })}
                  placeholder="Ej: Cardiología, Urología"
                  className="w-full rounded-xl border border-slate-200 px-4 py-2 focus:border-indigo-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">Motivo de consulta</label>
                <textarea
                  value={citaForm.motivo_consulta}
                  onChange={(e) => setCitaForm({ ...citaForm, motivo_consulta: e.target.value })}
                  placeholder="Describe brevemente el motivo"
                  rows={3}
                  className="w-full rounded-xl border border-slate-200 px-4 py-2 focus:border-indigo-500 focus:outline-none"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Fecha</label>
                  <input
                    type="date"
                    value={citaForm.fecha_solicitada}
                    onChange={(e) => setCitaForm({ ...citaForm, fecha_solicitada: e.target.value })}
                    className="w-full rounded-xl border border-slate-200 px-4 py-2 focus:border-indigo-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Hora</label>
                  <input
                    type="time"
                    value={citaForm.hora_solicitada}
                    onChange={(e) => setCitaForm({ ...citaForm, hora_solicitada: e.target.value })}
                    className="w-full rounded-xl border border-slate-200 px-4 py-2 focus:border-indigo-500 focus:outline-none"
                  />
                </div>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">Notas adicionales</label>
                <textarea
                  value={citaForm.notas_paciente}
                  onChange={(e) => setCitaForm({ ...citaForm, notas_paciente: e.target.value })}
                  placeholder="Información adicional (opcional)"
                  rows={2}
                  className="w-full rounded-xl border border-slate-200 px-4 py-2 focus:border-indigo-500 focus:outline-none"
                />
              </div>
            </div>
            <div className="mt-6 flex gap-3">
              <button
                onClick={() => setShowCitaModal(false)}
                className="flex-1 rounded-xl border border-slate-200 px-4 py-2 font-medium text-slate-700 hover:bg-slate-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleCrearCita}
                disabled={saving}
                className="flex-1 rounded-xl bg-indigo-600 px-4 py-2 font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
              >
                {saving ? 'Guardando...' : 'Solicitar cita'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Nueva Solicitud de Estudio */}
      {showEstudioModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-lg rounded-3xl bg-white p-6 shadow-2xl">
            <h3 className="mb-4 text-xl font-bold text-slate-900">Solicitar estudio</h3>
            <div className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">Tipo de estudio</label>
                <select
                  value={estudioForm.tipo_estudio}
                  onChange={(e) => setEstudioForm({ ...estudioForm, tipo_estudio: e.target.value })}
                  className="w-full rounded-xl border border-slate-200 px-4 py-2 focus:border-indigo-500 focus:outline-none"
                >
                  <option value="laboratorio">Laboratorio</option>
                  <option value="imagen">Imagen</option>
                  <option value="biopsia">Biopsia</option>
                  <option value="otro">Otro</option>
                </select>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">Nombre del estudio</label>
                <input
                  type="text"
                  value={estudioForm.nombre_estudio}
                  onChange={(e) => setEstudioForm({ ...estudioForm, nombre_estudio: e.target.value })}
                  placeholder="Ej: Hemograma completo, Radiografía de tórax"
                  className="w-full rounded-xl border border-slate-200 px-4 py-2 focus:border-indigo-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">Descripción</label>
                <textarea
                  value={estudioForm.descripcion}
                  onChange={(e) => setEstudioForm({ ...estudioForm, descripcion: e.target.value })}
                  placeholder="Describe el motivo de la solicitud"
                  rows={3}
                  className="w-full rounded-xl border border-slate-200 px-4 py-2 focus:border-indigo-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">Prioridad</label>
                <select
                  value={estudioForm.prioridad}
                  onChange={(e) => setEstudioForm({ ...estudioForm, prioridad: e.target.value })}
                  className="w-full rounded-xl border border-slate-200 px-4 py-2 focus:border-indigo-500 focus:outline-none"
                >
                  <option value="normal">Normal</option>
                  <option value="urgente">Urgente</option>
                  <option value="alta">Alta</option>
                </select>
              </div>
            </div>
            <div className="mt-6 flex gap-3">
              <button
                onClick={() => setShowEstudioModal(false)}
                className="flex-1 rounded-xl border border-slate-200 px-4 py-2 font-medium text-slate-700 hover:bg-slate-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleCrearEstudio}
                disabled={saving}
                className="flex-1 rounded-xl bg-indigo-600 px-4 py-2 font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
              >
                {saving ? 'Guardando...' : 'Solicitar estudio'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Nuevo Mensaje */}
      {showMensajeModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-lg rounded-3xl bg-white p-6 shadow-2xl">
            <h3 className="mb-4 text-xl font-bold text-slate-900">Enviar mensaje</h3>
            <div className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">Médico destinatario</label>
                <input
                  type="text"
                  value={mensajeForm.medico_id}
                  onChange={(e) => setMensajeForm({ ...mensajeForm, medico_id: e.target.value })}
                  placeholder="ID del médico"
                  className="w-full rounded-xl border border-slate-200 px-4 py-2 focus:border-indigo-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">Asunto</label>
                <input
                  type="text"
                  value={mensajeForm.asunto}
                  onChange={(e) => setMensajeForm({ ...mensajeForm, asunto: e.target.value })}
                  placeholder="Asunto del mensaje"
                  className="w-full rounded-xl border border-slate-200 px-4 py-2 focus:border-indigo-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">Mensaje</label>
                <textarea
                  value={mensajeForm.mensaje}
                  onChange={(e) => setMensajeForm({ ...mensajeForm, mensaje: e.target.value })}
                  placeholder="Escribe tu mensaje aquí"
                  rows={5}
                  className="w-full rounded-xl border border-slate-200 px-4 py-2 focus:border-indigo-500 focus:outline-none"
                />
              </div>
            </div>
            <div className="mt-6 flex gap-3">
              <button
                onClick={() => setShowMensajeModal(false)}
                className="flex-1 rounded-xl border border-slate-200 px-4 py-2 font-medium text-slate-700 hover:bg-slate-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleEnviarMensaje}
                disabled={saving}
                className="flex-1 rounded-xl bg-indigo-600 px-4 py-2 font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
              >
                {saving ? 'Enviando...' : 'Enviar mensaje'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Nuevo Recordatorio */}
      {showRecordatorioModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-lg rounded-3xl bg-white p-6 shadow-2xl">
            <h3 className="mb-4 text-xl font-bold text-slate-900">Crear recordatorio de medicamento</h3>
            <div className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">Nombre del medicamento</label>
                <input
                  type="text"
                  value={recordatorioForm.nombre_medicamento}
                  onChange={(e) => setRecordatorioForm({ ...recordatorioForm, nombre_medicamento: e.target.value })}
                  placeholder="Ej: Paracetamol"
                  className="w-full rounded-xl border border-slate-200 px-4 py-2 focus:border-indigo-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">Dosis</label>
                <input
                  type="text"
                  value={recordatorioForm.dosis}
                  onChange={(e) => setRecordatorioForm({ ...recordatorioForm, dosis: e.target.value })}
                  placeholder="Ej: 500mg"
                  className="w-full rounded-xl border border-slate-200 px-4 py-2 focus:border-indigo-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">Frecuencia</label>
                <select
                  value={recordatorioForm.frecuencia}
                  onChange={(e) => setRecordatorioForm({ ...recordatorioForm, frecuencia: e.target.value })}
                  className="w-full rounded-xl border border-slate-200 px-4 py-2 focus:border-indigo-500 focus:outline-none"
                >
                  <option value="Cada 4 horas">Cada 4 horas</option>
                  <option value="Cada 6 horas">Cada 6 horas</option>
                  <option value="Cada 8 horas">Cada 8 horas</option>
                  <option value="Cada 12 horas">Cada 12 horas</option>
                  <option value="Una vez al día">Una vez al día</option>
                  <option value="Dos veces al día">Dos veces al día</option>
                </select>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">Horarios (separados por comas)</label>
                <input
                  type="text"
                  value={recordatorioForm.horarios}
                  onChange={(e) => setRecordatorioForm({ ...recordatorioForm, horarios: e.target.value })}
                  placeholder="Ej: 08:00, 14:00, 20:00"
                  className="w-full rounded-xl border border-slate-200 px-4 py-2 focus:border-indigo-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">Indicaciones</label>
                <textarea
                  value={recordatorioForm.indicaciones}
                  onChange={(e) => setRecordatorioForm({ ...recordatorioForm, indicaciones: e.target.value })}
                  placeholder="Ej: Tomar con alimentos"
                  rows={2}
                  className="w-full rounded-xl border border-slate-200 px-4 py-2 focus:border-indigo-500 focus:outline-none"
                />
              </div>
            </div>
            <div className="mt-6 flex gap-3">
              <button
                onClick={() => setShowRecordatorioModal(false)}
                className="flex-1 rounded-xl border border-slate-200 px-4 py-2 font-medium text-slate-700 hover:bg-slate-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleCrearRecordatorio}
                disabled={saving}
                className="flex-1 rounded-xl bg-indigo-600 px-4 py-2 font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
              >
                {saving ? 'Guardando...' : 'Crear recordatorio'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}