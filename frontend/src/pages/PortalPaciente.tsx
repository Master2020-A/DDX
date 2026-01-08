import { useEffect, useMemo, useState } from 'react'
import {
  Activity,
  Calendar,
  CalendarClock,
  CheckCircle2,
  Clock,
  CreditCard,
  FileText,
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

const PortalPaciente = () => {
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

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)
      try {
        switch (activeTab) {
          case 'dashboard': {
            const data = await portalPacienteService.getDashboard(PACIENTE_ID)
            setDashboardData(data)
            break
          }
          case 'citas': {
            const data = await portalPacienteService.getCitas(PACIENTE_ID)
            setCitas(data)
            break
          }
          case 'estudios': {
            const data = await portalPacienteService.getSolicitudesEstudios(PACIENTE_ID)
            setSolicitudes(data)
            break
          }
          case 'pagos': {
            const data = await portalPacienteService.getPagos(PACIENTE_ID)
            setPagos(data)
            break
          }
          case 'mensajes': {
            const data = await portalPacienteService.getMensajes(PACIENTE_ID)
            setMensajes(data)
            break
          }
          case 'recordatorios': {
            const data = await portalPacienteService.getRecordatorios(PACIENTE_ID, true)
            setRecordatorios(data)
            break
          }
          case 'configuracion': {
            const data = await portalPacienteService.getConfiguracion(PACIENTE_ID)
            setConfiguracion(data)
            break
          }
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

  const metrics = useMemo(() => {
    if (!dashboardData) {
      return [
        { label: 'Citas pendientes', value: '—' },
        { label: 'Estudios pendientes', value: '—' },
        { label: 'Mensajes sin leer', value: '—' },
        { label: 'Recordatorios activos', value: '—' },
      ]
    }

    return [
      { label: 'Citas pendientes', value: dashboardData.citas_pendientes.toString() },
      { label: 'Estudios pendientes', value: dashboardData.solicitudes_pendientes.toString() },
      { label: 'Mensajes sin leer', value: dashboardData.mensajes_no_leidos.toString() },
      { label: 'Recordatorios activos', value: dashboardData.recordatorios_activos.toString() },
    ]
  }, [dashboardData])

  const formatFecha = (fecha: string) =>
    new Date(fecha).toLocaleDateString('es-MX', { year: 'numeric', month: 'short', day: 'numeric' })

  const formatHora = (hora?: string | null) =>
    hora ? new Date(`2000-01-01T${hora}`).toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' }) : null

  const estadoPill = (estado: string) => {
    const map: Record<string, { text: string; className: string }> = {
      solicitada: { text: 'Solicitada', className: 'bg-amber-100 text-amber-800' },
      confirmada: { text: 'Confirmada', className: 'bg-emerald-100 text-emerald-700' },
      cancelada: { text: 'Cancelada', className: 'bg-rose-100 text-rose-700' },
      pendiente: { text: 'Pendiente', className: 'bg-slate-100 text-slate-600' },
    }
    const badge = map[estado] || { text: estado, className: 'bg-slate-100 text-slate-600' }
    return <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${badge.className}`}>{badge.text}</span>
  }

  const renderDashboard = () => (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {metrics.map((metric) => (
          <div key={metric.label} className="rounded-3xl border border-slate-100 bg-white p-5 shadow-sm">
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
              <p className="text-xl font-semibold text-slate-900">{dashboardData.proxima_cita.especialidad_solicitada}</p>
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
        <button className="inline-flex items-center gap-2 rounded-2xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30">
          <Plus className="h-4 w-4" /> Nueva cita
        </button>
      </div>
      {loading ? (
        <div className="py-12 text-center text-slate-500">Cargando…</div>
      ) : citas.length ? (
        citas.map((cita) => (
          <div key={cita.id} className="rounded-3xl border border-slate-100 bg-white p-5 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <p className="text-base font-semibold text-slate-900">{cita.especialidad_solicitada || cita.tipo_cita}</p>
                <p className="text-sm text-slate-500">{cita.motivo_consulta}</p>
              </div>
              {estadoPill(cita.estado)}
            </div>
            <div className="mt-3 flex flex-wrap gap-4 text-sm text-slate-600">
              <span className="flex items-center gap-1"><Calendar className="h-4 w-4" />{formatFecha(cita.fecha_solicitada)}</span>
              {formatHora(cita.hora_solicitada) && (
                <span className="flex items-center gap-1"><Clock className="h-4 w-4" />{formatHora(cita.hora_solicitada)}</span>
              )}
            </div>
          </div>
        ))
      ) : (
        <div className="rounded-3xl border border-dashed border-slate-200 bg-white p-12 text-center text-slate-500">
          No tienes citas programadas
        </div>
      )}
    </div>
  )

  const renderSolicitudes = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900">Solicitudes de estudios</h2>
        <button className="inline-flex items-center gap-2 rounded-2xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30">
          <Plus className="h-4 w-4" /> Nueva solicitud
        </button>
      </div>
      {loading ? (
        <div className="py-12 text-center text-slate-500">Cargando…</div>
      ) : solicitudes.length ? (
        solicitudes.map((solicitud) => (
          <div key={solicitud.id} className="rounded-3xl border border-slate-100 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-base font-semibold text-slate-900">{solicitud.nombre_estudio}</p>
                <p className="text-sm text-slate-500">{solicitud.descripcion || 'Sin descripción'}</p>
              </div>
              {estadoPill(solicitud.estado)}
            </div>
            <p className="mt-2 text-sm text-slate-500">Solicitado: {formatFecha(solicitud.fecha_solicitud)}</p>
          </div>
        ))
      ) : (
        <div className="rounded-3xl border border-dashed border-slate-200 bg-white p-12 text-center text-slate-500">
          No hay solicitudes registradas
        </div>
      )}
    </div>
  )

  const renderPagos = () => (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-slate-900">Pagos y facturación</h2>
      {loading ? (
        <div className="py-12 text-center text-slate-500">Cargando…</div>
      ) : pagos.length ? (
        pagos.map((pago) => (
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
        ))
      ) : (
        <div className="rounded-3xl border border-dashed border-slate-200 bg-white p-12 text-center text-slate-500">
          No hay pagos registrados
        </div>
      )}
    </div>
  )

  const renderMensajes = () => (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-slate-900">Mensajes con tu médico</h2>
      {loading ? (
        <div className="py-12 text-center text-slate-500">Cargando…</div>
      ) : mensajes.length ? (
        mensajes.map((mensaje) => (
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
        ))
      ) : (
        <div className="rounded-3xl border border-dashed border-slate-200 bg-white p-12 text-center text-slate-500">
          No tienes mensajes nuevos
        </div>
      )}
    </div>
  )

  const renderRecordatorios = () => (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-slate-900">Recordatorios de medicamentos</h2>
      {loading ? (
        <div className="py-12 text-center text-slate-500">Cargando…</div>
      ) : recordatorios.length ? (
        recordatorios.map((rec) => (
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
        ))
      ) : (
        <div className="rounded-3xl border border-dashed border-slate-200 bg-white p-12 text-center text-slate-500">
          No hay recordatorios activos
        </div>
      )}
    </div>
  )

  const renderConfiguracion = () => (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-slate-900">Preferencias del portal</h2>
      {loading ? (
        <div className="py-12 text-center text-slate-500">Cargando…</div>
      ) : configuracion ? (
        <div className="space-y-3">
          {[
            { label: 'Notificaciones por email', value: configuracion.notificaciones_email },
            { label: 'Notificaciones por SMS', value: configuracion.notificaciones_sms },
            { label: 'Recordatorios de citas', value: configuracion.recordatorios_citas },
            { label: 'Recordatorios de medicamentos', value: configuracion.recordatorios_medicamentos },
            { label: 'Recordatorios de estudios', value: configuracion.recordatorios_estudios },
            { label: 'Compartir datos para investigación', value: configuracion.compartir_datos_investigacion },
          ].map((pref) => (
            <div key={pref.label} className="flex items-center justify-between rounded-3xl border border-slate-100 bg-white px-4 py-3 shadow-sm">
              <div>
                <p className="text-sm font-semibold text-slate-900">{pref.label}</p>
                <p className="text-xs text-slate-500">Estado personalizado</p>
              </div>
              <span
                className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                  pref.value ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600'
                }`}
              >
                {pref.value ? 'Activo' : 'Inactivo'}
              </span>
            </div>
          ))}
        </div>
      ) : (
        <div className="rounded-3xl border border-dashed border-slate-200 bg-white p-12 text-center text-slate-500">
          No hay preferencias configuradas
        </div>
      )}
    </div>
  )

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return renderDashboard()
      case 'citas':
        return renderCitas()
      case 'estudios':
        return renderSolicitudes()
      case 'pagos':
        return renderPagos()
      case 'mensajes':
        return renderMensajes()
      case 'recordatorios':
        return renderRecordatorios()
      case 'configuracion':
        return renderConfiguracion()
      default:
        return null
    }
  }

  return (
    <div className="space-y-8">
      <section className="rounded-4xl bg-white p-8 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-6">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-slate-400">Portal del paciente</p>
            <h1 className="mt-2 text-3xl font-semibold text-slate-900">Gestiona tu salud desde un solo lugar</h1>
            <p className="mt-2 text-sm text-slate-500">Consulta citas, estudios, pagos y recordatorios personalizados.</p>
          </div>
        </div>
      </section>

      {error && (
        <div className="rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div>
      )}

      <div className="flex flex-wrap gap-3 border-b border-slate-200 pb-4 text-sm font-semibold text-slate-500">
        {TABS.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`inline-flex items-center gap-2 rounded-2xl px-4 py-2 ${
                activeTab === tab.id ? 'bg-slate-900 text-white' : 'text-slate-500 hover:text-slate-900'
              }`}
            >
              <Icon className="h-4 w-4" /> {tab.label}
            </button>
          )
        })}
      </div>

      <section className="rounded-4xl border border-slate-200 bg-white p-6 shadow-sm">
        {renderContent()}
      </section>
    </div>
  )
}

export default PortalPaciente
