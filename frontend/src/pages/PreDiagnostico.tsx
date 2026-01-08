/**
 * Página principal de Pre-diagnóstico Inteligente
 */
import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { AlertCircle } from 'lucide-react'
import FormularioSintomas from '@/components/prediagnostico/FormularioSintomas'
import ResultadosPrediagnostico from '@/components/prediagnostico/ResultadosPrediagnostico'
import PatientWorkspaceLayout, { WorkspaceMetric } from '@/components/patient/PatientWorkspaceLayout'
import { prediagnosticoService, type PreDiagnosticoRequest, type PreDiagnosticoResponse } from '@/services/prediagnosticoService'
import api from '@/lib/api'
import { calculateAge } from '@/lib/utils'

export default function PreDiagnostico() {

  const { pacienteId } = useParams<{ pacienteId: string }>()
  const [tabActual, setTabActual] = useState(0)
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [resultado, setResultado] = useState<PreDiagnosticoResponse | null>(null)
  const [paciente, setPaciente] = useState<any>(null)
  const [loadingPaciente, setLoadingPaciente] = useState(true)

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

  const handleGenerarPrediagnostico = async (request: PreDiagnosticoRequest) => {
    setCargando(true)
    setError(null)

    try {
      const respuesta = await prediagnosticoService.generarPrediagnostico(request)
      setResultado(respuesta)
      setTabActual(1)
    } catch (err: any) {
      let errorMsg = 'Error al generar pre-diagnóstico. '
      if (err.response?.data?.detail) {
        if (Array.isArray(err.response.data.detail)) {
          errorMsg += err.response.data.detail
            .map((d: any) => `${d.loc?.join('.')}: ${d.msg}`)
            .join(', ')
        } else {
          errorMsg += err.response.data.detail
        }
      } else {
        errorMsg += 'Intente nuevamente.'
      }
      setError(errorMsg)
    } finally {
      setCargando(false)
    }
  }

  if (!pacienteId) {
    return <div className="p-8 text-center text-rose-600 font-semibold">Error: falta identificar al paciente.</div>
  }

  if (loadingPaciente) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="text-center text-slate-500">Cargando pre-diagnóstico…</div>
      </div>
    )
  }

  const metrics: WorkspaceMetric[] = [
    {
      label: 'Nivel de urgencia',
      value: resultado?.nivel_urgencia ? resultado.nivel_urgencia.toUpperCase() : '—',
      tone: resultado?.nivel_urgencia === 'critico' ? 'amber' : 'cyan',
    },
    {
      label: 'Diagnósticos sugeridos',
      value: resultado?.diagnosticos_diferenciales?.length
        ? resultado.diagnosticos_diferenciales.length.toString()
        : '—',
      tone: 'violet',
    },
    {
      label: 'Signos de alarma',
      value: resultado?.signos_alarma?.length ? resultado.signos_alarma.length.toString() : '0',
      tone: 'emerald',
    },
    {
      label: 'Último análisis',
      value: resultado?.timestamp ? new Date(resultado.timestamp).toLocaleString('es-MX') : 'Pendiente',
      tone: 'slate',
    },
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
      title="Pre-diagnóstico Inteligente"
      subtitle="Sugerencias clínicas generadas con IA según los síntomas capturados."
      breadcrumbs={[
        { label: 'Pacientes', to: '/pacientes' },
        { label: paciente?.nombre_completo || 'Pre-diagnóstico' },
      ]}
      patient={{
        name: paciente?.nombre_completo,
        expediente: paciente?.numero_expediente,
        tags: [paciente?.tipo_sangre].filter(Boolean) as string[],
      }}
      metrics={metrics}
      actions={null}
      sidebar={sidebar}
      heroAccent="indigo"
    >
      {error && (
        <div className="rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700 shadow-sm">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4" /> {error}
          </div>
        </div>
      )}

      <div className="rounded-3xl border border-dashed border-indigo-200 bg-indigo-50/70 px-6 py-4 text-sm text-indigo-800">
        <strong>Nota:</strong> Este pre-diagnóstico es una herramienta de apoyo clínico generada por IA. No reemplaza el juicio
        médico profesional.
      </div>

      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-center gap-4 border-b border-slate-100 pb-4 text-sm font-semibold text-slate-500">
          <button
            onClick={() => setTabActual(0)}
            className={`rounded-2xl px-4 py-2 ${
              tabActual === 0 ? 'bg-slate-900 text-white' : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            Ingresar síntomas
          </button>
          <button
            onClick={() => resultado && setTabActual(1)}
            disabled={!resultado}
            className={`rounded-2xl px-4 py-2 ${
              tabActual === 1
                ? 'bg-slate-900 text-white'
                : resultado
                ? 'text-slate-500 hover:text-slate-900'
                : 'text-slate-400 cursor-not-allowed'
            }`}
          >
            Resultados
          </button>
        </div>

        <div className="mt-6">
          {tabActual === 0 && (
            <FormularioSintomas
              pacienteId={pacienteId}
              onGenerarPrediagnostico={handleGenerarPrediagnostico}
              cargando={cargando}
            />
          )}

          {tabActual === 1 && resultado && (
            <ResultadosPrediagnostico resultado={resultado} />
          )}
        </div>
      </div>
    </PatientWorkspaceLayout>
  )
}

