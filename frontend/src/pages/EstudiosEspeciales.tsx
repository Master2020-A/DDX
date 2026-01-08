/**
 * Página principal de Estudios Especiales
 * Integra EKG, EEG y Ecografías
 */
import React, { useEffect, useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Brain, HeartPulse, Waves, Plus, X } from 'lucide-react'
import DashboardEstudiosEspeciales from '../components/estudios-especiales/DashboardEstudiosEspeciales';
import FormularioEKG from '../components/estudios-especiales/FormularioEKG';
import FormularioEEG from '../components/estudios-especiales/FormularioEEG';
import FormularioEcografia from '../components/estudios-especiales/FormularioEcografia';
import PatientWorkspaceLayout, { WorkspaceMetric } from '@/components/patient/PatientWorkspaceLayout';
import { calculateAge } from '@/lib/utils'
import api from '@/lib/api'
import estudiosEspecialesService from '@/services/estudiosEspecialesService'

const EstudiosEspeciales: React.FC = () => {
  const { pacienteId } = useParams<{ pacienteId: string }>()
  const [formularioAbierto, setFormularioAbierto] = useState<'ekg' | 'eeg' | 'ecografia' | null>(null)
  const [actualizarKey, setActualizarKey] = useState(0)
  const [paciente, setPaciente] = useState<any>(null)
  const [loadingPaciente, setLoadingPaciente] = useState(true)
  const [resumen, setResumen] = useState({
    ekg: 0,
    eeg: 0,
    ecografia: 0,
    alertas: 0,
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
    const fetchResumen = async () => {
      try {
        const data = await estudiosEspecialesService.obtenerResumenEstudios(pacienteId)
        const alertas =
          (data?.ekg?.alertas || 0) +
          (data?.eeg?.alertas || 0) +
          (data?.ecografias?.alertas || 0)
        setResumen({
          ekg: data?.ekg?.total || 0,
          eeg: data?.eeg?.total || 0,
          ecografia: data?.ecografias?.total || 0,
          alertas,
        })
      } catch (error) {
        console.error('Error al cargar resumen', error)
      }
    }
    fetchResumen()
  }, [pacienteId, actualizarKey])

  const handleNuevoEstudio = (tipo: 'ekg' | 'eeg' | 'ecografia') => {
    setFormularioAbierto(tipo)
  }

  const handleCerrarFormulario = () => {
    setFormularioAbierto(null)
  }

  const handleExito = () => {
    setActualizarKey((prev) => prev + 1)
    handleCerrarFormulario()
  }

  if (!pacienteId) {
    return <div className="p-8 text-center text-rose-600 font-semibold">Error: falta identificar al paciente.</div>
  }

  if (loadingPaciente) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="text-center text-slate-500">Cargando estudios especiales…</div>
      </div>
    )
  }

  const metrics: WorkspaceMetric[] = [
    { label: 'EKG realizados', value: resumen.ekg.toString(), tone: 'cyan' },
    { label: 'EEG realizados', value: resumen.eeg.toString(), tone: 'violet' },
    { label: 'Ecografías', value: resumen.ecografia.toString(), tone: 'emerald' },
    { label: 'Alertas activas', value: resumen.alertas.toString(), tone: 'amber' },
  ]

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
      title="Estudios Especiales"
      subtitle="EKG, EEG y ecografías con interpretación asistida."
      breadcrumbs={[
        { label: 'Pacientes', to: '/pacientes' },
        { label: paciente?.nombre_completo || 'Estudios especiales' },
      ]}
      patient={{
        name: paciente?.nombre_completo,
        expediente: paciente?.numero_expediente,
        tags: [paciente?.tipo_sangre].filter(Boolean) as string[],
      }}
      metrics={metrics}
      actions={
        <button
          onClick={() => setFormularioAbierto('ekg')}
          className="inline-flex items-center gap-2 rounded-2xl bg-white/10 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30 transition hover:bg-white/20"
        >
          <Plus className="h-4 w-4" /> Registrar estudio
        </button>
      }
      sidebar={sidebar}
      heroAccent="slate"
    >
      <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm">
        <DashboardEstudiosEspeciales
          key={actualizarKey}
          pacienteId={pacienteId}
          onNuevoEstudio={handleNuevoEstudio}
        />
      </div>

      <ModalEstudio
        tipo={formularioAbierto}
        pacienteId={pacienteId}
        onClose={handleCerrarFormulario}
        onSuccess={handleExito}
      />

    </PatientWorkspaceLayout>
  )
}

const ModalEstudio = ({
  tipo,
  pacienteId,
  onClose,
  onSuccess,
}: {
  tipo: 'ekg' | 'eeg' | 'ecografia' | null
  pacienteId: string
  onClose: () => void
  onSuccess: () => void
}) => {
  if (!tipo) return null

  const renderContent = () => {
    if (tipo === 'ekg') return <FormularioEKG open pacienteId={pacienteId} onClose={onClose} onSuccess={onSuccess} />
    if (tipo === 'eeg') return <FormularioEEG open pacienteId={pacienteId} onClose={onClose} onSuccess={onSuccess} />
    return <FormularioEcografia open pacienteId={pacienteId} onClose={onClose} onSuccess={onSuccess} />
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
        <div className="max-h-[75vh] overflow-y-auto">{renderContent()}</div>
      </div>
    </div>
  )
}

export default EstudiosEspeciales;
