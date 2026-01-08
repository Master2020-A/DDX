/**
 * Página principal de laboratorios clínicos
 */
import React, { useEffect, useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  ClipboardList,
  Plus,
  X,
  Upload,
  Library,
} from 'lucide-react';
import FormularioLaboratorio from '@/components/laboratorio/FormularioLaboratorio';
import SubirArchivoLaboratorio from '@/components/laboratorio/SubirArchivoLaboratorio';
import DashboardLaboratorio from '@/components/laboratorio/DashboardLaboratorio';
import CatalogoLaboratorio from '@/components/laboratorio/CatalogoLaboratorio';
import PatientWorkspaceLayout, { WorkspaceMetric } from '@/components/patient/PatientWorkspaceLayout';
import laboratorioService from '@/services/laboratorioService';
import api from '@/lib/api';
import { calculateAge, formatDateTime } from '@/lib/utils';

const tabsModal = [
  { id: 'manual', label: 'Captura manual', icon: ClipboardList },
  { id: 'archivo', label: 'Subir archivo', icon: Upload },
  { id: 'catalogo', label: 'Ver catálogo', icon: Library },
] as const

type TabModal = typeof tabsModal[number]['id']

interface Paciente {
  id: string
  nombre_completo: string
  numero_expediente: string
  fecha_nacimiento?: string
  genero?: string
  tipo_sangre?: string
}

const LaboratorioModal = ({
  open,
  activeTab,
  onTabChange,
  onClose,
  pacienteId,
  onSuccess,
}: {
  open: boolean
  activeTab: TabModal
  onTabChange: (tab: TabModal) => void
  onClose: () => void
  pacienteId: string
  onSuccess: () => void
}) => {
  if (!open) return null

  const renderContent = () => {
    if (activeTab === 'manual') {
      return (
        <FormularioLaboratorio pacienteId={pacienteId} onSuccess={onSuccess} onCancel={onClose} />
      )
    }
    if (activeTab === 'archivo') {
      return (
        <SubirArchivoLaboratorio pacienteId={pacienteId} onSuccess={onSuccess} onCancel={onClose} />
      )
    }
    return <CatalogoLaboratorio />
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/70 px-4">
      <div className="relative w-full max-w-4xl rounded-3xl bg-white p-6 shadow-2xl">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-full border border-slate-200 p-1 text-slate-500 hover:text-slate-900"
        >
          <X className="h-4 w-4" />
        </button>
        <h3 className="text-xl font-semibold text-slate-900">Registrar nuevo resultado</h3>
        <p className="text-sm text-slate-500">Captura manual, adjunta archivos o consulta el catálogo de pruebas.</p>

        <div className="mt-6 flex flex-wrap gap-3">
          {tabsModal.map((tab) => {
            const Icon = tab.icon
            const isActive = tab.id === activeTab
            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`flex items-center gap-2 rounded-2xl border px-4 py-2 text-sm font-semibold transition ${
                  isActive
                    ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
                    : 'border-slate-200 bg-white text-slate-500'
                }`}
              >
                <Icon className="h-4 w-4" /> {tab.label}
              </button>
            )
          })}
        </div>

        <div className="mt-6 max-h-[70vh] overflow-y-auto rounded-2xl border border-slate-100 bg-white p-4">
          {renderContent()}
        </div>
      </div>
    </div>
  )
}

const Laboratorios: React.FC = () => {
  const { pacienteId } = useParams<{ pacienteId: string }>()
  const [dialogoAbierto, setDialogoAbierto] = useState(false)
  const [tabDialogo, setTabDialogo] = useState<TabModal>('manual')
  const [recargar, setRecargar] = useState(0)
  const [paciente, setPaciente] = useState<Paciente | null>(null)
  const [loadingPaciente, setLoadingPaciente] = useState(true)
  const [stats, setStats] = useState({
    total: 0,
    alertas: 0,
    areas: 0,
    ultimaActualizacion: '',
  })

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

  useEffect(() => {
    if (!pacienteId) return
    const fetchStats = async () => {
      try {
        const pruebas = await laboratorioService.listarPruebasPaciente(pacienteId)
        const total = pruebas.length
        const alertas = pruebas.filter((p) => p.requiere_atencion || p.valores_criticos_count > 0).length
        const areas = new Set(pruebas.map((p) => p.area)).size
        const fechas = pruebas
          .map((p) => p.fecha_resultado)
          .filter((fecha): fecha is string => Boolean(fecha))
          .sort((a, b) => new Date(b).getTime() - new Date(a).getTime())
        setStats({
          total,
          alertas,
          areas,
          ultimaActualizacion: fechas[0] || '',
        })
      } catch (error) {
        console.error('Error al cargar estadísticas de laboratorio', error)
      }
    }
    fetchStats()
  }, [pacienteId, recargar])

  const handlePruebaCreada = () => {
    setRecargar((prev) => prev + 1)
    setDialogoAbierto(false)
  }

  const metrics: WorkspaceMetric[] = useMemo(() => {
    return [
      {
        label: 'Pruebas registradas',
        value: stats.total.toString(),
        tone: 'cyan',
      },
      {
        label: 'Alertas activas',
        value: stats.alertas.toString(),
        tone: stats.alertas > 0 ? 'amber' : 'emerald',
        helper: stats.alertas > 0 ? 'Requieren atención' : 'Sin valores críticos',
      },
      {
        label: 'Áreas evaluadas',
        value: stats.areas.toString(),
        tone: 'violet',
      },
      {
        label: 'Último resultado',
        value: stats.ultimaActualizacion ? formatDateTime(stats.ultimaActualizacion) : 'Sin registro',
        tone: 'slate',
      },
    ]
  }, [stats])

  if (!pacienteId) {
    return <div className="p-8 text-center text-rose-600 font-semibold">Error: falta identificar al paciente.</div>
  }

  if (loadingPaciente) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="text-center text-slate-500">Cargando información del laboratorio…</div>
      </div>
    )
  }

  const sidebar = paciente ? (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
      <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Paciente</h3>
      <p className="text-base font-semibold text-slate-900">{paciente.nombre_completo}</p>
      <p className="text-sm text-slate-500">Expediente {paciente.numero_expediente}</p>
      <div className="space-y-2 text-sm text-slate-600">
        {paciente.fecha_nacimiento && (
          <p>Edad: {calculateAge(paciente.fecha_nacimiento)} años</p>
        )}
        {paciente.tipo_sangre && <p>Tipo de sangre: {paciente.tipo_sangre}</p>}
      </div>
    </div>
  ) : null

  return (
    <PatientWorkspaceLayout
      title="Laboratorio Clínico"
      subtitle="Consulta paneles, tendencias y alertas críticas de las pruebas diagnósticas del paciente."
      breadcrumbs={[
        { label: 'Pacientes', to: '/pacientes' },
        { label: paciente?.nombre_completo || 'Laboratorio' },
      ]}
      patient={{
        name: paciente?.nombre_completo,
        expediente: paciente?.numero_expediente,
        tags: [paciente?.tipo_sangre].filter(Boolean) as string[],
      }}
      metrics={metrics}
      actions={
        <button
          onClick={() => setDialogoAbierto(true)}
          className="inline-flex items-center gap-2 rounded-2xl bg-white/10 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-emerald-500/30 transition hover:bg-white/20"
        >
          <Plus className="h-4 w-4" /> Nuevo resultado
        </button>
      }
      sidebar={sidebar}
      heroAccent="cyan"
    >
      <div className="rounded-3xl border border-slate-200 bg-white p-2 shadow-sm">
        <DashboardLaboratorio key={recargar} pacienteId={pacienteId} />
      </div>

      <LaboratorioModal
        open={dialogoAbierto}
        activeTab={tabDialogo}
        onTabChange={setTabDialogo}
        onClose={() => setDialogoAbierto(false)}
        pacienteId={pacienteId}
        onSuccess={handlePruebaCreada}
      />
    </PatientWorkspaceLayout>
  )
}

export default Laboratorios;
