import { useEffect, useMemo, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import api from '@/lib/api'
import { Paciente } from '@/types'
import TranscripcionConsultaVoz from '@/components/TranscripcionConsultaVoz'
import PatientWorkspaceLayout, { WorkspaceMetric } from '@/components/patient/PatientWorkspaceLayout'
import { calculateAge } from '@/lib/utils'

const NuevaConsulta = () => {
  const { pacienteId } = useParams()
  const navigate = useNavigate()
  const [paciente, setPaciente] = useState<Paciente | null>(null)
  const [loading, setLoading] = useState(false)
  const [loadingPaciente, setLoadingPaciente] = useState(true)
  const [error, setError] = useState('')
  const [formData, setFormData] = useState({
    tipo_consulta: 'primera_vez',
    motivo_consulta: '',
    sintomas: '',
  })

  useEffect(() => {
    if (!pacienteId) return
    const fetchPaciente = async () => {
      try {
        const { data } = await api.get(`/pacientes/${pacienteId}`)
        setPaciente(data)
      } catch (err) {
        console.error('Error cargando paciente', err)
      } finally {
        setLoadingPaciente(false)
      }
    }
    fetchPaciente()
  }, [pacienteId])

  const handleDatosExtraidos = (datos: any) => {
    if (datos.sintomas?.length) {
      const sintomasTexto = datos.sintomas.map((s: any) => s.nombre || s).join(', ')
      setFormData((prev) => ({
        ...prev,
        sintomas: prev.sintomas ? `${prev.sintomas}, ${sintomasTexto}` : sintomasTexto,
      }))
    }
    if (!formData.motivo_consulta && datos.motivo_consulta) {
      setFormData((prev) => ({ ...prev, motivo_consulta: datos.motivo_consulta }))
    }
  }

  const handleTranscripcionCompleta = (texto: string) => {
    if (!formData.motivo_consulta && texto) {
      setFormData((prev) => ({ ...prev, motivo_consulta: texto.substring(0, 500) }))
    }
  }

  const metrics: WorkspaceMetric[] = useMemo(
    () => [
      { label: 'Tipo de consulta', value: formData.tipo_consulta.replace('_', ' '), tone: 'cyan' },
      { label: 'Motivo capturado', value: formData.motivo_consulta ? `${formData.motivo_consulta.length}/500` : 'Pendiente', tone: 'violet' },
      {
        label: 'Síntomas listados',
        value: formData.sintomas ? formData.sintomas.split(',').filter(Boolean).length.toString() : '0',
        tone: 'emerald',
      },
      { label: 'Captura por voz', value: 'Disponible', tone: 'slate' },
    ],
    [formData]
  )

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!pacienteId) return

    setLoading(true)
    setError('')

    try {
      const payload = {
        paciente_id: pacienteId,
        tipo_consulta: formData.tipo_consulta,
        motivo_consulta: formData.motivo_consulta,
        sintomas: formData.sintomas.split(',').map((s) => s.trim()).filter(Boolean),
      }
      const { data } = await api.post('/consultas/', payload)
      navigate(`/consultas/${data.id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al crear consulta')
    } finally {
      setLoading(false)
    }
  }

  if (!pacienteId) {
    return <div className="p-8 text-center text-rose-600 font-semibold">Error: falta identificar al paciente.</div>
  }

  if (loadingPaciente) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="text-center text-slate-500">Cargando ficha del paciente…</div>
      </div>
    )
  }

  if (!paciente) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="text-center text-rose-500">No encontramos la información del paciente.</div>
      </div>
    )
  }

  const sidebar = (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
      <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Paciente</h3>
      <p className="text-base font-semibold text-slate-900">{paciente.nombre_completo}</p>
      <p className="text-sm text-slate-500">Expediente {paciente.numero_expediente}</p>
      <div className="space-y-2 text-sm text-slate-600">
        {paciente.fecha_nacimiento && <p>Edad: {calculateAge(paciente.fecha_nacimiento)} años</p>}
        {paciente.tipo_sangre && <p>Tipo de sangre: {paciente.tipo_sangre}</p>}
      </div>
      <Link
        to={`/pacientes/${pacienteId}`}
        className="inline-flex items-center justify-center rounded-2xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:border-indigo-200 hover:text-indigo-600"
      >
        <ArrowLeft className="mr-2 h-4 w-4" /> Volver al paciente
      </Link>
    </div>
  )

  return (
    <PatientWorkspaceLayout
      title="Nueva Consulta"
      subtitle="Registra el motivo, síntomas y conclusiones principales."
      breadcrumbs={[
        { label: 'Pacientes', to: '/pacientes' },
        { label: paciente.nombre_completo },
      ]}
      patient={{
        name: paciente.nombre_completo,
        expediente: paciente.numero_expediente,
        tags: [paciente.tipo_sangre].filter(Boolean) as string[],
      }}
      metrics={metrics}
      sidebar={sidebar}
      heroAccent="indigo"
    >
      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-6">
          <TranscripcionConsultaVoz
            pacienteId={pacienteId}
            onDatosExtraidos={handleDatosExtraidos}
            onTranscripcionCompleta={handleTranscripcionCompleta}
          />
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div>
          )}

          <div>
            <label className="label">Tipo de consulta *</label>
            <select
              value={formData.tipo_consulta}
              onChange={(e) => setFormData({ ...formData, tipo_consulta: e.target.value })}
              className="input"
              required
            >
              <option value="primera_vez">Primera vez</option>
              <option value="seguimiento">Seguimiento</option>
              <option value="urgencia">Urgencia</option>
              <option value="interconsulta">Interconsulta</option>
            </select>
          </div>

          <div>
            <label className="label">Motivo de consulta *</label>
            <textarea
              value={formData.motivo_consulta}
              onChange={(e) => setFormData({ ...formData, motivo_consulta: e.target.value })}
              className="input"
              rows={3}
              placeholder="Describa el motivo principal de la consulta..."
              required
              maxLength={500}
            />
            <p className="text-xs text-slate-400 text-right">{formData.motivo_consulta.length}/500</p>
          </div>

          <div>
            <label className="label">Síntomas (separados por coma) *</label>
            <textarea
              value={formData.sintomas}
              onChange={(e) => setFormData({ ...formData, sintomas: e.target.value })}
              className="input"
              rows={4}
              placeholder="Fiebre, dolor de cabeza, tos seca, etc."
              required
            />
            <p className="text-sm text-slate-500 mt-1">Ingrese los síntomas separados por comas.</p>
          </div>

          <div className="flex flex-wrap justify-end gap-3 pt-4">
            <Link
              to={`/pacientes/${pacienteId}`}
              className="rounded-2xl border border-slate-200 px-6 py-2.5 text-sm font-semibold text-slate-600 hover:bg-slate-50"
            >
              Cancelar
            </Link>
            <button
              type="submit"
              disabled={loading}
              className="rounded-2xl bg-gradient-to-r from-indigo-500 to-purple-500 px-6 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30 transition hover:shadow-2xl disabled:opacity-60"
            >
              {loading ? 'Creando…' : 'Crear consulta'}
            </button>
          </div>
        </form>
      </div>
    </PatientWorkspaceLayout>
  )
}

export default NuevaConsulta
