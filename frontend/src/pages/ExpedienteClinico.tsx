import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import {
  FileText, Heart, Stethoscope, Pill, Activity,
  Save, User, Users,
  AlertCircle, CheckCircle, Edit, Trash2, Plus
} from 'lucide-react'
import api from '@/lib/api'
import PatientWorkspaceLayout, { WorkspaceMetric } from '@/components/patient/PatientWorkspaceLayout'
import { calculateAge, formatDateTime } from '@/lib/utils'

// ============================================================================
// INTERFACES
// ============================================================================

interface Paciente {
  id: string
  numero_expediente: string
  nombre_completo: string
  fecha_nacimiento: string
  genero: string
  tipo_sangre?: string
  telefono?: string
  email?: string
  alergias?: string[]
}

interface Expediente {
  id?: string
  paciente_id: string
  consulta_id?: string
  antecedentes_personales?: string
  antecedentes_familiares?: string
  padecimientos_cronicos?: string[]
  cirugias_previas?: string[]
  medicamentos_actuales?: string[]
  habitos?: string
  signos_vitales?: any
  exploracion_fisica?: string
  notas?: string
  created_at?: string
  updated_at?: string
}

// ============================================================================
// COMPONENTES
// ============================================================================

const InputField = ({ label, value, onChange, ...props }: any) => (
  <div>
    <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
    <input
      value={value || ''}
      onChange={(e) => onChange(e.target.value)}
      className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-400 focus:ring-4 focus:ring-purple-100 transition-all outline-none"
      {...props}
    />
  </div>
)

const TextArea = ({ label, value, onChange, rows = 4, ...props }: any) => (
  <div>
    <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
    <textarea
      value={value || ''}
      onChange={(e) => onChange(e.target.value)}
      rows={rows}
      className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-400 focus:ring-4 focus:ring-purple-100 transition-all outline-none resize-none"
      {...props}
    />
  </div>
)

// ============================================================================
// COMPONENTE PRINCIPAL
// ============================================================================

const ExpedienteClinico = () => {
  const { pacienteId } = useParams<{ pacienteId: string }>()
  
  const [paciente, setPaciente] = useState<Paciente | null>(null)
  const [expediente, setExpediente] = useState<Expediente>({
    paciente_id: pacienteId || '',
    antecedentes_personales: '',
    antecedentes_familiares: '',
    padecimientos_cronicos: [],
    cirugias_previas: [],
    medicamentos_actuales: [],
    habitos: '',
    signos_vitales: {},
    exploracion_fisica: '',
    notas: ''
  })
  
  const [activeTab, setActiveTab] = useState('antecedentes')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  useEffect(() => {
    if (pacienteId) {
      fetchPaciente()
      fetchExpediente()
    }
  }, [pacienteId])

  const fetchPaciente = async () => {
    try {
      const response = await api.get(`/pacientes/${pacienteId}`)
      setPaciente(response.data)
    } catch (error) {
      console.error('Error fetching paciente:', error)
      showMessage('error', 'Error al cargar datos del paciente')
    }
  }

  const fetchExpediente = async () => {
    try {
      setLoading(true)
      const response = await api.get(`/expedientes/paciente/${pacienteId}`)
      
      if (response.data && response.data.length > 0) {
        // Si existe un expediente, usar el más reciente
        setExpediente(response.data[0])
      }
    } catch (error) {
      console.error('Error fetching expediente:', error)
    } finally {
      setLoading(false)
    }
  }

  const updateField = (field: string, value: any) => {
    setExpediente(prev => ({ ...prev, [field]: value }))
  }

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text })
    setTimeout(() => setMessage(null), 5000)
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      
      if (expediente.id) {
        // Actualizar expediente existente
        await api.put(`/expedientes/${expediente.id}`, expediente)
        showMessage('success', 'Expediente actualizado correctamente')
      } else {
        // Crear nuevo expediente
        const response = await api.post('/expedientes/', expediente)
        setExpediente(response.data)
        showMessage('success', 'Expediente creado correctamente')
      }
    } catch (error) {
      console.error('Error saving expediente:', error)
      showMessage('error', 'Error al guardar el expediente')
    } finally {
      setSaving(false)
    }
  }

  const tabs = [
    { id: 'antecedentes', label: 'Antecedentes', icon: Users },
    { id: 'padecimientos', label: 'Padecimientos/Cirugías/Medicamentos', icon: Heart },
    { id: 'signos', label: 'Signos Vitales', icon: Activity },
    { id: 'exploracion', label: 'Exploración Física', icon: Stethoscope },
    { id: 'notas', label: 'Notas de Evolución', icon: FileText }
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    )
  }

  const patientTags = [paciente?.genero, paciente?.tipo_sangre].filter(Boolean) as string[]

  const metrics: WorkspaceMetric[] = [
    {
      label: 'Edad',
      value: paciente?.fecha_nacimiento ? `${calculateAge(paciente.fecha_nacimiento)} años` : 'Sin registro',
      tone: 'cyan',
    },
    {
      label: 'Tipo de sangre',
      value: paciente?.tipo_sangre || 'Pendiente',
      tone: 'violet',
    },
    {
      label: 'Última actualización',
      value: expediente.updated_at ? formatDateTime(expediente.updated_at) : 'Sin registro',
      helper: expediente.created_at ? `Creado ${formatDateTime(expediente.created_at)}` : undefined,
      tone: 'emerald',
    },
    {
      label: 'Alergias registradas',
      value:
        paciente?.alergias && paciente.alergias.length > 0
          ? `${paciente.alergias.length} registro${paciente.alergias.length === 1 ? '' : 's'}`
          : 'Sin alergias',
      tone: 'amber',
    },
  ]

  const sidebar = paciente ? (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
      <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Información del paciente</h3>
      <div className="space-y-3 text-sm text-slate-600">
        <div>
          <p className="text-xs text-slate-400">Teléfono</p>
          <p className="font-semibold">{paciente.telefono || 'No registrado'}</p>
        </div>
        <div>
          <p className="text-xs text-slate-400">Correo</p>
          <p className="font-semibold break-all">{paciente.email || 'No registrado'}</p>
        </div>
        {paciente.alergias && paciente.alergias.length > 0 && (
          <div>
            <p className="text-xs text-slate-400 mb-1">Alergias</p>
            <div className="flex flex-wrap gap-2">
              {paciente.alergias.map((alergia) => (
                <span key={alergia} className="rounded-full bg-rose-50 px-3 py-1 text-xs font-medium text-rose-600">
                  {alergia}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  ) : null

  return (
    <PatientWorkspaceLayout
      title="Expediente Clínico"
      subtitle="Gestiona la información médica longitudinal, antecedentes y notas de evolución del paciente."
      breadcrumbs={[
        { label: 'Pacientes', to: '/pacientes' },
        { label: paciente?.nombre_completo || 'Expediente clínico' },
      ]}
      patient={{
        name: paciente?.nombre_completo,
        expediente: paciente?.numero_expediente,
        tags: patientTags,
      }}
      metrics={metrics}
      actions={
        <button
          onClick={handleSave}
          disabled={saving}
          className="inline-flex items-center gap-2 rounded-2xl bg-white/10 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-black/20 transition hover:bg-white/20 disabled:opacity-60"
        >
          <Save className="h-4 w-4" />
          {saving ? 'Guardando…' : 'Guardar expediente'}
        </button>
      }
      sidebar={sidebar}
    >
      {message && (
        <div
          className={`rounded-2xl border px-4 py-3 text-sm font-medium shadow-sm ${
            message.type === 'success'
              ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
              : 'border-rose-200 bg-rose-50 text-rose-700'
          }`}
        >
          <div className="flex items-center gap-2">
            {message.type === 'success' ? <CheckCircle className="h-4 w-4" /> : <AlertCircle className="h-4 w-4" />}
            {message.text}
          </div>
        </div>
      )}

      <div className="rounded-3xl border border-slate-200 bg-white shadow-sm">
        <div className="flex flex-wrap overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex flex-1 min-w-[180px] items-center gap-2 px-5 py-4 text-sm font-semibold transition ${
                  activeTab === tab.id
                    ? 'bg-slate-900/5 text-indigo-600'
                    : 'text-slate-500 hover:text-slate-900'
                }`}
              >
                <Icon className="h-4 w-4" />
                {tab.label}
              </button>
            )
          })}
        </div>
      </div>

      <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
        {activeTab === 'antecedentes' && (
          <SeccionAntecedentes expediente={expediente} updateField={updateField} />
        )}

        {activeTab === 'padecimientos' && (
          <SeccionPadecimientos expediente={expediente} updateField={updateField} />
        )}

        {activeTab === 'signos' && <SeccionSignosVitales expediente={expediente} updateField={updateField} />}

        {activeTab === 'exploracion' && <SeccionExploracion expediente={expediente} updateField={updateField} />}

        {activeTab === 'notas' && <SeccionNotas pacienteId={pacienteId || ''} />}
      </div>
    </PatientWorkspaceLayout>
  )
}

// ============================================================================
// SECCIÓN: ANTECEDENTES
// ============================================================================

const SeccionAntecedentes = ({ expediente, updateField }: any) => {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
          <Users className="h-7 w-7 text-purple-600" />
          Antecedentes Médicos
        </h2>
      </div>

      {/* Antecedentes Personales */}
      <div className="bg-blue-50 rounded-2xl p-6 border-2 border-blue-100">
        <h3 className="text-xl font-semibold text-blue-900 mb-4 flex items-center gap-2">
          <User className="h-5 w-5" />
          Antecedentes Personales Patológicos
        </h3>
        <TextArea
          label="Enfermedades previas, hospitalizaciones, traumatismos, transfusiones, etc."
          value={expediente.antecedentes_personales}
          onChange={(v: string) => updateField('antecedentes_personales', v)}
          rows={8}
          placeholder="Ej: Diabetes Mellitus tipo 2 diagnosticada en 2015, Hipertensión arterial en tratamiento desde 2018, Apendicectomía en 2010..."
        />
      </div>

      {/* Antecedentes Familiares */}
      <div className="bg-rose-50 rounded-2xl p-6 border-2 border-rose-100">
        <h3 className="text-xl font-semibold text-rose-900 mb-4 flex items-center gap-2">
          <Users className="h-5 w-5" />
          Antecedentes Heredo-Familiares
        </h3>
        <TextArea
          label="Enfermedades de padres, hermanos, abuelos (Diabetes, Hipertensión, Cáncer, etc.)"
          value={expediente.antecedentes_familiares}
          onChange={(v: string) => updateField('antecedentes_familiares', v)}
          rows={8}
          placeholder="Ej: Padre con Diabetes Mellitus tipo 2, Madre con Hipertensión arterial, Abuela paterna falleció por cáncer de mama..."
        />
      </div>

      {/* Hábitos */}
      <div className="bg-amber-50 rounded-2xl p-6 border-2 border-amber-100">
        <h3 className="text-xl font-semibold text-amber-900 mb-4 flex items-center gap-2">
          <Activity className="h-5 w-5" />
          Hábitos y Estilo de Vida
        </h3>
        <TextArea
          label="Tabaquismo, alcoholismo, drogas, actividad física, dieta, etc."
          value={expediente.habitos}
          onChange={(v: string) => updateField('habitos', v)}
          rows={6}
          placeholder="Ej: Tabaquismo: 10 cigarrillos/día desde hace 15 años. Alcoholismo: Consumo social ocasional. Ejercicio: 30 minutos de caminata 3 veces por semana. Dieta: Rica en carbohidratos..."
        />
      </div>

      {/* Notas Adicionales */}
      <div className="bg-gray-50 rounded-2xl p-6 border-2 border-gray-200">
        <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Notas Generales
        </h3>
        <TextArea
          label="Información adicional relevante del expediente"
          value={expediente.notas}
          onChange={(v: string) => updateField('notas', v)}
          rows={4}
          placeholder="Cualquier información adicional que considere relevante para el expediente..."
        />
      </div>
    </div>
  )
}

// ============================================================================
// SECCIÓN: PADECIMIENTOS / CIRUGÍAS / MEDICAMENTOS
// ============================================================================

const SeccionPadecimientos = ({ expediente, updateField }: any) => {
  const [showPadecimientoModal, setShowPadecimientoModal] = useState(false)
  const [showCirugiaModal, setShowCirugiaModal] = useState(false)
  const [showMedicamentoModal, setShowMedicamentoModal] = useState(false)
  
  const [editingPadecimiento, setEditingPadecimiento] = useState<string | null>(null)
  const [editingCirugia, setEditingCirugia] = useState<string | null>(null)
  const [editingMedicamento, setEditingMedicamento] = useState<string | null>(null)

  // Padecimientos Crónicos
  const handleAddPadecimiento = (padecimiento: string) => {
    const padecimientos = expediente.padecimientos_cronicos || []
    updateField('padecimientos_cronicos', [...padecimientos, padecimiento])
    setShowPadecimientoModal(false)
  }

  const handleEditPadecimiento = (oldValue: string, newValue: string) => {
    const padecimientos = expediente.padecimientos_cronicos || []
    const updated = padecimientos.map((p: string) => p === oldValue ? newValue : p)
    updateField('padecimientos_cronicos', updated)
    setEditingPadecimiento(null)
  }

  const handleDeletePadecimiento = (padecimiento: string) => {
    const padecimientos = expediente.padecimientos_cronicos || []
    updateField('padecimientos_cronicos', padecimientos.filter((p: string) => p !== padecimiento))
  }

  // Cirugías Previas
  const handleAddCirugia = (cirugia: string) => {
    const cirugias = expediente.cirugias_previas || []
    updateField('cirugias_previas', [...cirugias, cirugia])
    setShowCirugiaModal(false)
  }

  const handleEditCirugia = (oldValue: string, newValue: string) => {
    const cirugias = expediente.cirugias_previas || []
    const updated = cirugias.map((c: string) => c === oldValue ? newValue : c)
    updateField('cirugias_previas', updated)
    setEditingCirugia(null)
  }

  const handleDeleteCirugia = (cirugia: string) => {
    const cirugias = expediente.cirugias_previas || []
    updateField('cirugias_previas', cirugias.filter((c: string) => c !== cirugia))
  }

  // Medicamentos Actuales
  const handleAddMedicamento = (medicamento: string) => {
    const medicamentos = expediente.medicamentos_actuales || []
    updateField('medicamentos_actuales', [...medicamentos, medicamento])
    setShowMedicamentoModal(false)
  }

  const handleEditMedicamento = (oldValue: string, newValue: string) => {
    const medicamentos = expediente.medicamentos_actuales || []
    const updated = medicamentos.map((m: string) => m === oldValue ? newValue : m)
    updateField('medicamentos_actuales', updated)
    setEditingMedicamento(null)
  }

  const handleDeleteMedicamento = (medicamento: string) => {
    const medicamentos = expediente.medicamentos_actuales || []
    updateField('medicamentos_actuales', medicamentos.filter((m: string) => m !== medicamento))
  }

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
          <Heart className="h-7 w-7 text-red-600" />
          Padecimientos, Cirugías y Medicamentos
        </h2>
      </div>

      {/* Padecimientos Crónicos */}
      <div className="bg-red-50 rounded-2xl p-6 border-2 border-red-100">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold text-red-900 flex items-center gap-2">
            <AlertCircle className="h-5 w-5" />
            Padecimientos Crónicos
          </h3>
          <button
            onClick={() => setShowPadecimientoModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            <Plus className="h-4 w-4" />
            Agregar Padecimiento
          </button>
        </div>

        {expediente.padecimientos_cronicos && expediente.padecimientos_cronicos.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {expediente.padecimientos_cronicos.map((padecimiento: string, index: number) => (
              <div key={index} className="bg-white rounded-lg p-4 border border-red-200 flex items-start justify-between gap-3">
                <div className="flex-1">
                  <p className="text-gray-800 font-medium">{padecimiento}</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setEditingPadecimiento(padecimiento)}
                    className="text-blue-600 hover:text-blue-800 transition-colors"
                    title="Editar"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDeletePadecimiento(padecimiento)}
                    className="text-red-600 hover:text-red-800 transition-colors"
                    title="Eliminar"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">No hay padecimientos crónicos registrados</p>
        )}
      </div>

      {/* Cirugías Previas */}
      <div className="bg-orange-50 rounded-2xl p-6 border-2 border-orange-100">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold text-orange-900 flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Cirugías Previas
          </h3>
          <button
            onClick={() => setShowCirugiaModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
          >
            <Plus className="h-4 w-4" />
            Agregar Cirugía
          </button>
        </div>

        {expediente.cirugias_previas && expediente.cirugias_previas.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {expediente.cirugias_previas.map((cirugia: string, index: number) => (
              <div key={index} className="bg-white rounded-lg p-4 border border-orange-200 flex items-start justify-between gap-3">
                <div className="flex-1">
                  <p className="text-gray-800 font-medium">{cirugia}</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setEditingCirugia(cirugia)}
                    className="text-blue-600 hover:text-blue-800 transition-colors"
                    title="Editar"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteCirugia(cirugia)}
                    className="text-red-600 hover:text-red-800 transition-colors"
                    title="Eliminar"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">No hay cirugías registradas</p>
        )}
      </div>

      {/* Medicamentos Actuales */}
      <div className="bg-green-50 rounded-2xl p-6 border-2 border-green-100">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold text-green-900 flex items-center gap-2">
            <Pill className="h-5 w-5" />
            Medicamentos Actuales
          </h3>
          <button
            onClick={() => setShowMedicamentoModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Plus className="h-4 w-4" />
            Agregar Medicamento
          </button>
        </div>

        {expediente.medicamentos_actuales && expediente.medicamentos_actuales.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {expediente.medicamentos_actuales.map((medicamento: string, index: number) => (
              <div key={index} className="bg-white rounded-lg p-4 border border-green-200 flex items-start justify-between gap-3">
                <div className="flex-1">
                  <p className="text-gray-800 font-medium">{medicamento}</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setEditingMedicamento(medicamento)}
                    className="text-blue-600 hover:text-blue-800 transition-colors"
                    title="Editar"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteMedicamento(medicamento)}
                    className="text-red-600 hover:text-red-800 transition-colors"
                    title="Eliminar"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">No hay medicamentos registrados</p>
        )}
      </div>

      {/* Modales */}
      {showPadecimientoModal && (
        <ModalPadecimiento
          onClose={() => setShowPadecimientoModal(false)}
          onSave={handleAddPadecimiento}
        />
      )}

      {editingPadecimiento && (
        <ModalPadecimiento
          onClose={() => setEditingPadecimiento(null)}
          onSave={(newValue: string) => handleEditPadecimiento(editingPadecimiento, newValue)}
          initialValue={editingPadecimiento}
          isEditing
        />
      )}

      {showCirugiaModal && (
        <ModalCirugia
          onClose={() => setShowCirugiaModal(false)}
          onSave={handleAddCirugia}
        />
      )}

      {editingCirugia && (
        <ModalCirugia
          onClose={() => setEditingCirugia(null)}
          onSave={(newValue: string) => handleEditCirugia(editingCirugia, newValue)}
          initialValue={editingCirugia}
          isEditing
        />
      )}

      {showMedicamentoModal && (
        <ModalMedicamento
          onClose={() => setShowMedicamentoModal(false)}
          onSave={handleAddMedicamento}
        />
      )}

      {editingMedicamento && (
        <ModalMedicamento
          onClose={() => setEditingMedicamento(null)}
          onSave={(newValue: string) => handleEditMedicamento(editingMedicamento, newValue)}
          initialValue={editingMedicamento}
          isEditing
        />
      )}
    </div>
  )
}

// ============================================================================
// MODALES
// ============================================================================

const ModalPadecimiento = ({ onClose, onSave, initialValue = '', isEditing = false }: any) => {
  const [formData, setFormData] = useState({
    nombre: '',
    fecha_diagnostico: '',
    tratamiento: '',
    observaciones: ''
  })

  useEffect(() => {
    if (initialValue) {
      // Parsear el string guardado (formato: "Nombre | Fecha | Tratamiento | Observaciones")
      const parts = initialValue.split(' | ')
      setFormData({
        nombre: parts[0] || '',
        fecha_diagnostico: parts[1] || '',
        tratamiento: parts[2] || '',
        observaciones: parts[3] || ''
      })
    }
  }, [initialValue])

  const handleSubmit = () => {
    if (!formData.nombre.trim()) return
    
    const padecimiento = [
      formData.nombre,
      formData.fecha_diagnostico,
      formData.tratamiento,
      formData.observaciones
    ].filter(Boolean).join(' | ')
    
    onSave(padecimiento)
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-2xl font-bold text-gray-900">
            {isEditing ? 'Editar Padecimiento Crónico' : 'Agregar Padecimiento Crónico'}
          </h3>
        </div>

        <div className="p-6 space-y-4">
          <InputField
            label="Nombre del Padecimiento *"
            value={formData.nombre}
            onChange={(v: string) => setFormData({ ...formData, nombre: v })}
            placeholder="Ej: Diabetes Mellitus Tipo 2"
          />

          <InputField
            label="Fecha de Diagnóstico"
            type="date"
            value={formData.fecha_diagnostico}
            onChange={(v: string) => setFormData({ ...formData, fecha_diagnostico: v })}
          />

          <TextArea
            label="Tratamiento Actual"
            value={formData.tratamiento}
            onChange={(v: string) => setFormData({ ...formData, tratamiento: v })}
            rows={3}
            placeholder="Ej: Metformina 850mg cada 12 horas..."
          />

          <TextArea
            label="Observaciones"
            value={formData.observaciones}
            onChange={(v: string) => setFormData({ ...formData, observaciones: v })}
            rows={2}
            placeholder="Información adicional..."
          />
        </div>

        <div className="p-6 border-t border-gray-200 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-6 py-2 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
          >
            Cancelar
          </button>
          <button
            onClick={handleSubmit}
            disabled={!formData.nombre.trim()}
            className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isEditing ? 'Actualizar' : 'Agregar'}
          </button>
        </div>
      </div>
    </div>
  )
}

const ModalCirugia = ({ onClose, onSave, initialValue = '', isEditing = false }: any) => {
  const [formData, setFormData] = useState({
    nombre: '',
    fecha: '',
    hospital: '',
    observaciones: ''
  })

  useEffect(() => {
    if (initialValue) {
      const parts = initialValue.split(' | ')
      setFormData({
        nombre: parts[0] || '',
        fecha: parts[1] || '',
        hospital: parts[2] || '',
        observaciones: parts[3] || ''
      })
    }
  }, [initialValue])

  const handleSubmit = () => {
    if (!formData.nombre.trim()) return
    
    const cirugia = [
      formData.nombre,
      formData.fecha,
      formData.hospital,
      formData.observaciones
    ].filter(Boolean).join(' | ')
    
    onSave(cirugia)
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-2xl font-bold text-gray-900">
            {isEditing ? 'Editar Cirugía' : 'Agregar Cirugía Previa'}
          </h3>
        </div>

        <div className="p-6 space-y-4">
          <InputField
            label="Nombre de la Cirugía *"
            value={formData.nombre}
            onChange={(v: string) => setFormData({ ...formData, nombre: v })}
            placeholder="Ej: Apendicectomía"
          />

          <InputField
            label="Fecha de la Cirugía"
            type="date"
            value={formData.fecha}
            onChange={(v: string) => setFormData({ ...formData, fecha: v })}
          />

          <InputField
            label="Hospital/Clínica"
            value={formData.hospital}
            onChange={(v: string) => setFormData({ ...formData, hospital: v })}
            placeholder="Ej: Hospital General"
          />

          <TextArea
            label="Observaciones"
            value={formData.observaciones}
            onChange={(v: string) => setFormData({ ...formData, observaciones: v })}
            rows={2}
            placeholder="Complicaciones, tipo de anestesia, etc..."
          />
        </div>

        <div className="p-6 border-t border-gray-200 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-6 py-2 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
          >
            Cancelar
          </button>
          <button
            onClick={handleSubmit}
            disabled={!formData.nombre.trim()}
            className="px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isEditing ? 'Actualizar' : 'Agregar'}
          </button>
        </div>
      </div>
    </div>
  )
}

const ModalMedicamento = ({ onClose, onSave, initialValue = '', isEditing = false }: any) => {
  const [formData, setFormData] = useState({
    nombre: '',
    dosis: '',
    frecuencia: '',
    via: '',
    fecha_inicio: '',
    observaciones: ''
  })

  useEffect(() => {
    if (initialValue) {
      const parts = initialValue.split(' | ')
      setFormData({
        nombre: parts[0] || '',
        dosis: parts[1] || '',
        frecuencia: parts[2] || '',
        via: parts[3] || '',
        fecha_inicio: parts[4] || '',
        observaciones: parts[5] || ''
      })
    }
  }, [initialValue])

  const handleSubmit = () => {
    if (!formData.nombre.trim()) return
    
    const medicamento = [
      formData.nombre,
      formData.dosis,
      formData.frecuencia,
      formData.via,
      formData.fecha_inicio,
      formData.observaciones
    ].filter(Boolean).join(' | ')
    
    onSave(medicamento)
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-2xl font-bold text-gray-900">
            {isEditing ? 'Editar Medicamento' : 'Agregar Medicamento Actual'}
          </h3>
        </div>

        <div className="p-6 space-y-4">
          <InputField
            label="Nombre del Medicamento *"
            value={formData.nombre}
            onChange={(v: string) => setFormData({ ...formData, nombre: v })}
            placeholder="Ej: Metformina"
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <InputField
              label="Dosis"
              value={formData.dosis}
              onChange={(v: string) => setFormData({ ...formData, dosis: v })}
              placeholder="Ej: 850mg"
            />

            <InputField
              label="Frecuencia"
              value={formData.frecuencia}
              onChange={(v: string) => setFormData({ ...formData, frecuencia: v })}
              placeholder="Ej: Cada 12 horas"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <InputField
              label="Vía de Administración"
              value={formData.via}
              onChange={(v: string) => setFormData({ ...formData, via: v })}
              placeholder="Ej: Oral"
            />

            <InputField
              label="Fecha de Inicio"
              type="date"
              value={formData.fecha_inicio}
              onChange={(v: string) => setFormData({ ...formData, fecha_inicio: v })}
            />
          </div>

          <TextArea
            label="Observaciones"
            value={formData.observaciones}
            onChange={(v: string) => setFormData({ ...formData, observaciones: v })}
            rows={2}
            placeholder="Indicaciones especiales, reacciones adversas, etc..."
          />
        </div>

        <div className="p-6 border-t border-gray-200 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-6 py-2 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
          >
            Cancelar
          </button>
          <button
            onClick={handleSubmit}
            disabled={!formData.nombre.trim()}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isEditing ? 'Actualizar' : 'Agregar'}
          </button>
        </div>
      </div>
    </div>
  )
}

// ============================================================================
// SECCIÓN: SIGNOS VITALES
// ============================================================================

const SeccionSignosVitales = ({ expediente, updateField }: any) => {
  const signosVitales = expediente.signos_vitales || {}

  const updateSigno = (field: string, value: any) => {
    updateField('signos_vitales', {
      ...signosVitales,
      [field]: value
    })
  }

  // Calcular IMC automáticamente
  useEffect(() => {
    if (signosVitales.peso && signosVitales.talla) {
      const peso = parseFloat(signosVitales.peso)
      const tallaMts = parseFloat(signosVitales.talla) / 100
      if (peso > 0 && tallaMts > 0) {
        const imc = (peso / (tallaMts * tallaMts)).toFixed(2)
        updateSigno('imc', imc)
      }
    }
  }, [signosVitales.peso, signosVitales.talla])

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
          <Activity className="h-7 w-7 text-blue-600" />
          Signos Vitales
        </h2>
      </div>

      {/* Signos Vitales Principales */}
      <div className="bg-blue-50 rounded-2xl p-6 border-2 border-blue-100">
        <h3 className="text-xl font-semibold text-blue-900 mb-4">Mediciones Actuales</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Temperatura */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              🌡️ Temperatura (°C)
            </label>
            <input
              type="number"
              step="0.1"
              value={signosVitales.temperatura || ''}
              onChange={(e) => updateSigno('temperatura', parseFloat(e.target.value) || null)}
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-blue-400 focus:ring-4 focus:ring-blue-100 transition-all outline-none"
              placeholder="36.5"
            />
          </div>

          {/* Presión Arterial Sistólica */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              💓 Presión Sistólica (mmHg)
            </label>
            <input
              type="number"
              value={signosVitales.presion_arterial_sistolica || ''}
              onChange={(e) => updateSigno('presion_arterial_sistolica', parseInt(e.target.value) || null)}
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-blue-400 focus:ring-4 focus:ring-blue-100 transition-all outline-none"
              placeholder="120"
            />
          </div>

          {/* Presión Arterial Diastólica */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              💓 Presión Diastólica (mmHg)
            </label>
            <input
              type="number"
              value={signosVitales.presion_arterial_diastolica || ''}
              onChange={(e) => updateSigno('presion_arterial_diastolica', parseInt(e.target.value) || null)}
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-blue-400 focus:ring-4 focus:ring-blue-100 transition-all outline-none"
              placeholder="80"
            />
          </div>

          {/* Frecuencia Cardíaca */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              ❤️ Frecuencia Cardíaca (lpm)
            </label>
            <input
              type="number"
              value={signosVitales.frecuencia_cardiaca || ''}
              onChange={(e) => updateSigno('frecuencia_cardiaca', parseInt(e.target.value) || null)}
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-blue-400 focus:ring-4 focus:ring-blue-100 transition-all outline-none"
              placeholder="70"
            />
          </div>

          {/* Frecuencia Respiratoria */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              🫁 Frecuencia Respiratoria (rpm)
            </label>
            <input
              type="number"
              value={signosVitales.frecuencia_respiratoria || ''}
              onChange={(e) => updateSigno('frecuencia_respiratoria', parseInt(e.target.value) || null)}
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-blue-400 focus:ring-4 focus:ring-blue-100 transition-all outline-none"
              placeholder="18"
            />
          </div>

          {/* Saturación de Oxígeno */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              🩺 Saturación O₂ (%)
            </label>
            <input
              type="number"
              step="0.1"
              value={signosVitales.saturacion_oxigeno || ''}
              onChange={(e) => updateSigno('saturacion_oxigeno', parseFloat(e.target.value) || null)}
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-blue-400 focus:ring-4 focus:ring-blue-100 transition-all outline-none"
              placeholder="98"
            />
          </div>
        </div>
      </div>

      {/* Antropometría */}
      <div className="bg-purple-50 rounded-2xl p-6 border-2 border-purple-100">
        <h3 className="text-xl font-semibold text-purple-900 mb-4">Antropometría</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {/* Peso */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              ⚖️ Peso (kg)
            </label>
            <input
              type="number"
              step="0.1"
              value={signosVitales.peso || ''}
              onChange={(e) => updateSigno('peso', parseFloat(e.target.value) || null)}
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-400 focus:ring-4 focus:ring-purple-100 transition-all outline-none"
              placeholder="70.5"
            />
          </div>

          {/* Talla */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              📏 Talla (cm)
            </label>
            <input
              type="number"
              step="0.1"
              value={signosVitales.talla || ''}
              onChange={(e) => updateSigno('talla', parseFloat(e.target.value) || null)}
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-400 focus:ring-4 focus:ring-purple-100 transition-all outline-none"
              placeholder="170"
            />
          </div>

          {/* IMC (Calculado) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              📊 IMC (kg/m²)
            </label>
            <input
              type="number"
              step="0.01"
              value={signosVitales.imc || ''}
              readOnly
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 bg-gray-50 text-gray-600 outline-none"
              placeholder="Auto"
            />
          </div>

          {/* Perímetro Abdominal */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              📐 Perímetro Abdominal (cm)
            </label>
            <input
              type="number"
              step="0.1"
              value={signosVitales.perimetro_abdominal || ''}
              onChange={(e) => updateSigno('perimetro_abdominal', parseFloat(e.target.value) || null)}
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-400 focus:ring-4 focus:ring-purple-100 transition-all outline-none"
              placeholder="85"
            />
          </div>
        </div>
      </div>

      {/* Glucosa */}
      <div className="bg-yellow-50 rounded-2xl p-6 border-2 border-yellow-100">
        <h3 className="text-xl font-semibold text-yellow-900 mb-4">Mediciones Adicionales</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              🩸 Glucosa (mg/dL)
            </label>
            <input
              type="number"
              step="0.1"
              value={signosVitales.glucosa || ''}
              onChange={(e) => updateSigno('glucosa', parseFloat(e.target.value) || null)}
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-yellow-400 focus:ring-4 focus:ring-yellow-100 transition-all outline-none"
              placeholder="100"
            />
          </div>
        </div>
      </div>

      {/* Resumen Visual */}
      {(signosVitales.presion_arterial_sistolica || signosVitales.frecuencia_cardiaca || signosVitales.temperatura) && (
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-6 border-2 border-blue-200">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">📈 Resumen Rápido</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {signosVitales.temperatura && (
              <div className="bg-white rounded-lg p-4 text-center">
                <p className="text-3xl font-bold text-blue-600">{signosVitales.temperatura}°C</p>
                <p className="text-sm text-gray-600 mt-1">Temperatura</p>
              </div>
            )}
            {(signosVitales.presion_arterial_sistolica && signosVitales.presion_arterial_diastolica) && (
              <div className="bg-white rounded-lg p-4 text-center">
                <p className="text-3xl font-bold text-red-600">
                  {signosVitales.presion_arterial_sistolica}/{signosVitales.presion_arterial_diastolica}
                </p>
                <p className="text-sm text-gray-600 mt-1">Presión Arterial</p>
              </div>
            )}
            {signosVitales.frecuencia_cardiaca && (
              <div className="bg-white rounded-lg p-4 text-center">
                <p className="text-3xl font-bold text-pink-600">{signosVitales.frecuencia_cardiaca}</p>
                <p className="text-sm text-gray-600 mt-1">FC (lpm)</p>
              </div>
            )}
            {signosVitales.saturacion_oxigeno && (
              <div className="bg-white rounded-lg p-4 text-center">
                <p className="text-3xl font-bold text-teal-600">{signosVitales.saturacion_oxigeno}%</p>
                <p className="text-sm text-gray-600 mt-1">SpO₂</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// ============================================================================
// SECCIÓN: EXPLORACIÓN FÍSICA
// ============================================================================

const SeccionExploracion = ({ expediente, updateField }: any) => {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
          <Stethoscope className="h-7 w-7 text-teal-600" />
          Exploración Física
        </h2>
      </div>

      <div className="bg-teal-50 rounded-2xl p-6 border-2 border-teal-100">
        <h3 className="text-xl font-semibold text-teal-900 mb-4">Exploración Física Completa</h3>
        <TextArea
          label="Descripción detallada de la exploración física por sistemas"
          value={expediente.exploracion_fisica}
          onChange={(v: string) => updateField('exploracion_fisica', v)}
          rows={20}
          placeholder="EXPLORACIÓN FÍSICA POR SISTEMAS:

ASPECTO GENERAL:
- Estado general, estado de conciencia, actitud

CABEZA:
- Cráneo, cabello, cuero cabelludo

OJOS:
- Conjuntivas, pupilas, movimientos oculares

OÍDOS:
- Conducto auditivo externo, membrana timpánica

NARIZ:
- Fosas nasales, tabique, mucosa

BOCA Y FARINGE:
- Mucosa oral, dentadura, faringe, amígdalas

CUELLO:
- Movilidad, tiroides, ganglios

TÓRAX:
- Inspección, forma, simetría

PULMONES:
- Auscultación, ruidos respiratorios

CORAZÓN:
- Ruidos cardíacos, soplos

ABDOMEN:
- Inspección, palpación, auscultación, percusión
- Dolor, masas, visceromegalias

EXTREMIDADES:
- Fuerza muscular, sensibilidad, reflejos
- Edema, pulsos periféricos

PIEL Y FANERAS:
- Lesiones, coloración, hidratación

NEUROLÓGICO:
- Estado mental, pares craneales, reflejos, sensibilidad, coordinación"
        />
      </div>
    </div>
  )
}

// ============================================================================
// SECCIÓN: NOTAS DE EVOLUCIÓN
// ============================================================================

const SeccionNotas = ({ pacienteId }: any) => {
  const [notas, setNotas] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)

  useEffect(() => {
    fetchNotas()
  }, [pacienteId])

  const fetchNotas = async () => {
    try {
      setLoading(true)
      const response = await api.get(`/notas-medicas/paciente/${pacienteId}`)
      setNotas(response.data)
    } catch (error) {
      console.error('Error fetching notas:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleNotaCreated = () => {
    setShowModal(false)
    fetchNotas()
  }

  const handleDeleteNota = async (notaId: string) => {
    if (!confirm('¿Está seguro de eliminar esta nota médica?')) return

    try {
      await api.delete(`/notas-medicas/${notaId}`)
      fetchNotas()
    } catch (error) {
      console.error('Error deleting nota:', error)
      alert('Error al eliminar la nota')
    }
  }

  const getTipoColor = (tipo: string) => {
    const colors: any = {
      evolucion: 'bg-blue-100 text-blue-800',
      ingreso: 'bg-green-100 text-green-800',
      alta: 'bg-purple-100 text-purple-800',
      interconsulta: 'bg-orange-100 text-orange-800',
      procedimiento: 'bg-pink-100 text-pink-800',
      defuncion: 'bg-gray-100 text-gray-800'
    }
    return colors[tipo] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
          <FileText className="h-7 w-7 text-indigo-600" />
          Notas de Evolución
        </h2>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Nueva Nota
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="text-gray-500 mt-4">Cargando notas...</p>
        </div>
      ) : notas.length === 0 ? (
        <div className="bg-gray-50 rounded-2xl p-12 text-center border-2 border-gray-200">
          <FileText className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <p className="text-lg font-medium text-gray-600">No hay notas médicas registradas</p>
          <p className="text-sm text-gray-500 mt-2">Comience agregando una nota de evolución</p>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Timeline */}
          <div className="relative">
            {/* Línea vertical del timeline */}
            <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200"></div>

            {notas.map((nota) => (
              <div key={nota.id} className="relative pl-20 pb-8">
                {/* Punto del timeline */}
                <div className="absolute left-6 w-5 h-5 rounded-full bg-indigo-600 border-4 border-white shadow"></div>

                {/* Card de la nota */}
                <div className="bg-white rounded-2xl border-2 border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                  <div className="p-6">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getTipoColor(nota.tipo_nota)}`}>
                            {nota.tipo_nota.toUpperCase()}
                          </span>
                          {nota.firmada && (
                            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800">
                              ✓ FIRMADA
                            </span>
                          )}
                        </div>
                        <h3 className="text-xl font-bold text-gray-900">{nota.titulo}</h3>
                        <p className="text-sm text-gray-500 mt-1">
                          {new Date(nota.fecha_nota).toLocaleDateString('es-MX', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </p>
                      </div>
                      {!nota.firmada && (
                        <button
                          onClick={() => handleDeleteNota(nota.id)}
                          className="text-red-600 hover:text-red-800 transition-colors"
                          title="Eliminar nota"
                        >
                          <Trash2 className="h-5 w-5" />
                        </button>
                      )}
                    </div>
                    <div className="prose max-w-none">
                      <p className="text-gray-700 whitespace-pre-wrap">{nota.contenido}</p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Modal Nueva Nota */}
      {showModal && (
        <ModalNuevaNota
          onClose={() => setShowModal(false)}
          onSave={handleNotaCreated}
          pacienteId={pacienteId}
        />
      )}
    </div>
  )
}

// ============================================================================
// MODAL: NUEVA NOTA MÉDICA
// ============================================================================

const ModalNuevaNota = ({ onClose, onSave, pacienteId }: any) => {
  const [formData, setFormData] = useState({
    tipo_nota: 'evolucion',
    titulo: '',
    contenido: ''
  })
  const [saving, setSaving] = useState(false)

  const tiposNota = [
    { value: 'evolucion', label: 'Nota de Evolución' },
    { value: 'ingreso', label: 'Nota de Ingreso' },
    { value: 'alta', label: 'Nota de Alta' },
    { value: 'interconsulta', label: 'Nota de Interconsulta' },
    { value: 'procedimiento', label: 'Nota de Procedimiento' },
    { value: 'defuncion', label: 'Nota de Defunción' }
  ]

  const handleSubmit = async () => {
    if (!formData.titulo.trim() || !formData.contenido.trim()) {
      alert('Título y contenido son obligatorios')
      return
    }

    try {
      setSaving(true)
      await api.post('/notas-medicas/', {
        paciente_id: pacienteId,
        ...formData
      })
      onSave()
    } catch (error) {
      console.error('Error saving nota:', error)
      alert('Error al guardar la nota médica')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-2xl font-bold text-gray-900">Nueva Nota Médica</h3>
        </div>

        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo de Nota *
            </label>
            <select
              value={formData.tipo_nota}
              onChange={(e) => setFormData({ ...formData, tipo_nota: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-indigo-400 focus:ring-4 focus:ring-indigo-100 transition-all outline-none"
            >
              {tiposNota.map((tipo) => (
                <option key={tipo.value} value={tipo.value}>
                  {tipo.label}
                </option>
              ))}
            </select>
          </div>

          <InputField
            label="Título *"
            value={formData.titulo}
            onChange={(v: string) => setFormData({ ...formData, titulo: v })}
            placeholder="Ej: Evolución del paciente - Día 3"
          />

          <TextArea
            label="Contenido de la Nota *"
            value={formData.contenido}
            onChange={(v: string) => setFormData({ ...formData, contenido: v })}
            rows={15}
            placeholder="Escriba aquí la nota médica completa...

Ejemplo:

SUBJETIVO:
- Paciente refiere mejoría del dolor abdominal
- Tolera vía oral sin náuseas

OBJETIVO:
- T: 36.8°C, FC: 72 lpm, TA: 120/80 mmHg
- Abdomen blando, depresible, no doloroso

ANÁLISIS:
- Evolución favorable post-operatoria

PLAN:
- Continuar antibiótico
- Dieta blanda
- Alta probable mañana"
          />
        </div>

        <div className="p-6 border-t border-gray-200 flex justify-end gap-3">
          <button
            onClick={onClose}
            disabled={saving}
            className="px-6 py-2 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            onClick={handleSubmit}
            disabled={saving || !formData.titulo.trim() || !formData.contenido.trim()}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? 'Guardando...' : 'Guardar Nota'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ExpedienteClinico
