import { useEffect, useMemo, useState } from 'react'
import { useLocation, useParams } from 'react-router-dom'
import { Shield, FileText, Activity, Settings } from 'lucide-react'
import PatientWorkspaceLayout, { WorkspaceMetric } from '@/components/patient/PatientWorkspaceLayout'
import DashboardCumplimiento from '@/components/cumplimiento/DashboardCumplimiento'
import GestionConsentimientos from '@/components/cumplimiento/GestionConsentimientos'
import api from '@/lib/api'
import { calculateAge } from '@/lib/utils'

const TABS = [
  { id: 'dashboard', name: 'Dashboard', icon: Shield },
  { id: 'consentimientos', name: 'Consentimientos', icon: FileText },
  { id: 'logs', name: 'Logs de Acceso', icon: Activity },
  { id: 'configuracion', name: 'Configuración', icon: Settings },
] as const

type TabId = (typeof TABS)[number]['id']

type Paciente = {
  id: string
  nombre_completo: string
  numero_expediente: string
  fecha_nacimiento?: string
  tipo_sangre?: string
}

const CumplimientoNormativo = () => {
  const params = useParams<{ pacienteId: string }>()
  const location = useLocation()
  const pacienteId = params.pacienteId || location.state?.pacienteId
  const [paciente, setPaciente] = useState<Paciente | null>(null)
  const [loadingPaciente, setLoadingPaciente] = useState(true)
  const [activeTab, setActiveTab] = useState<TabId>('dashboard')

  useEffect(() => {
    if (!pacienteId) return
    const fetchPaciente = async () => {
      try {
        const response = await api.get(`/pacientes/${pacienteId}`)
        setPaciente(response.data)
      } catch (error) {
        console.error('Error al cargar paciente', error)
      } finally {
        setLoadingPaciente(false)
      }
    }
    fetchPaciente()
  }, [pacienteId])

  const metrics: WorkspaceMetric[] = useMemo(
    () => [
      { label: 'Normas aplicables', value: '6', tone: 'cyan' },
      { label: 'Hallazgos abiertos', value: '2', tone: 'amber', helper: 'Última auditoría 12/12/2025' },
      { label: 'Correctivos en curso', value: '3', tone: 'violet' },
      { label: 'Cumplimiento promedio', value: '92%', tone: 'emerald' },
    ],
    []
  )

  if (!pacienteId) {
    return <div className="p-8 text-center text-rose-600 font-semibold">Error: falta identificar al paciente.</div>
  }

  if (loadingPaciente) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="text-center text-slate-500">Cargando cumplimiento normativo…</div>
      </div>
    )
  }

  const sidebar = paciente ? (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
      <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Paciente</h3>
      <p className="text-base font-semibold text-slate-900">{paciente.nombre_completo}</p>
      <p className="text-sm text-slate-500">Expediente {paciente.numero_expediente}</p>
      <div className="space-y-2 text-sm text-slate-600">
        {paciente.fecha_nacimiento && <p>Edad: {calculateAge(paciente.fecha_nacimiento)} años</p>}
        {paciente.tipo_sangre && <p>Tipo de sangre: {paciente.tipo_sangre}</p>}
      </div>
    </div>
  ) : null

  return (
    <PatientWorkspaceLayout
      title="Cumplimiento Normativo"
      subtitle="Gestión de HIPAA, GDPR y NOM-004-SSA3-2012 para este paciente."
      breadcrumbs={[
        { label: 'Pacientes', to: '/pacientes' },
        { label: paciente?.nombre_completo || 'Cumplimiento' },
      ]}
      patient={{
        name: paciente?.nombre_completo,
        expediente: paciente?.numero_expediente,
        tags: [paciente?.tipo_sangre].filter(Boolean) as string[],
      }}
      metrics={metrics}
      sidebar={sidebar}
      heroAccent="slate"
    >
      <div className="flex flex-wrap gap-3 border-b border-slate-200 pb-4 text-sm font-semibold text-slate-500">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`rounded-2xl px-4 py-2 ${
              activeTab === tab.id ? 'bg-slate-900 text-white' : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            {tab.name}
          </button>
        ))}
      </div>

      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        {activeTab === 'dashboard' && <DashboardCumplimiento />}
        {activeTab === 'consentimientos' && <GestionConsentimientos pacienteId={pacienteId} />}
        {activeTab === 'logs' && (
          <div className="rounded-3xl border border-slate-100 bg-white p-6 text-center shadow-sm">
            <Activity className="mx-auto h-12 w-12 text-slate-300" />
            <h3 className="mt-2 text-base font-semibold text-slate-900">Logs de acceso sensible</h3>
            <p className="mt-1 text-sm text-slate-500">Registro de accesos a información sensible (HIPAA compliance)</p>
            <p className="mt-4 text-xs text-slate-400">Esta funcionalidad se activará cuando se acceda a información de pacientes.</p>
          </div>
        )}
        {activeTab === 'configuracion' && (
          <div className="space-y-3">
            {[
              { title: 'HIPAA', region: 'Estados Unidos' },
              { title: 'GDPR', region: 'Unión Europea' },
              { title: 'NOM-004-SSA3-2012', region: 'México' },
            ].map((norma) => (
              <div key={norma.title} className="flex items-center justify-between rounded-2xl border border-slate-100 bg-slate-50 px-4 py-3">
                <div>
                  <p className="text-sm font-semibold text-slate-900">{norma.title}</p>
                  <p className="text-xs text-slate-500">{norma.region}</p>
                </div>
                <span className="rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-semibold text-emerald-700">Activo</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </PatientWorkspaceLayout>
  )
}

export default CumplimientoNormativo
