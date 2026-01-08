import { useState, useEffect, useMemo } from 'react'
import { prediagnosticoService, CIE10SearchResult } from '@/services/prediagnosticoService'
import { useNavigate, useParams } from 'react-router-dom'
import { 
  FileText, User, Users, Baby, Home, Activity, 
  Heart, Syringe, TrendingUp, Calendar, Save, 
  Stethoscope, ClipboardList
} from 'lucide-react'
import api from '@/lib/api'
import PatientWorkspaceLayout, { WorkspaceMetric } from '@/components/patient/PatientWorkspaceLayout'
import { calculateAge } from '@/lib/utils'

// ============================================================================
// CATÁLOGOS DE DATOS
// ============================================================================

const SERVICIOS_MEDICOS_MEXICO = [
  // Proveedores Públicos
  'IMSS - Instituto Mexicano del Seguro Social',
  'ISSSTE - Instituto de Seguridad y Servicios Sociales de los Trabajadores del Estado',
  'INSABI (antes Seguro Popular)',
  'PEMEX - Servicios de Salud',
  'SEDENA - Servicios Médicos Militares',
  'SEMAR - Servicios Médicos Navales',
  'SSA - Secretaría de Salud',
  
  // Institutos Nacionales de Salud
  'Hospital Infantil de México Federico Gómez',
  'Instituto Nacional de Cancerología',
  'Instituto Nacional de Nutrición Salvador Zubirán',
  'Instituto Nacional de Cardiología Ignacio Chávez',
  'Instituto Nacional de Pediatría',
  'Instituto Nacional de Perinatología',
  'Instituto Nacional de Enfermedades Respiratorias',
  
  // Hospitales Privados
  'Hospital Ángeles',
  'Star Médica',
  'Christus Muguerza',
  'Hospital Español',
  'ABC Medical Center',
  'Médica Sur',
  'Hospital Privado (Otro)',
  
  // Clínicas Privadas
  'Jack Nathan Health (Walmart)',
  'Bupa México',
  'Clínica Particular',
  'Consultorio Médico Privado',
  
  // Telemedicina
  '1DOC3 (Telemedicina)',
  'Más Salud (Telemedicina + Estudios)',
  'Telemedicina (Otra)',
  
  // Seguros Médicos Privados
  'Cigna Global',
  'GeoBlue Xplorer',
  'AXA Seguros',
  'Allianz',
  'Metlife',
  'GNP Seguros',
  'Seguro Privado (Otro)',
  
  // Servicios Integrales
  'Care U (Sistema Integral)',
  'Más Salud (Sistema Integral)',
  
  // Sin Servicio
  'Sin Servicio Médico',
  'Pago de Bolsillo'
]

const EXAMENES_LABORATORIO = [
  'Biometría Hemática',
  'Química Sanguínea',
  'Perfil de Lípidos',
  'Examen General de Orina (EGO)',
  'Urocultivo',
  'Coproparasitoscópico',
  'Coprocultivo',
  'Pruebas de Función Hepática',
  'Pruebas de Función Renal',
  'Electrolitos Séricos',
  'Perfil Tiroideo (TSH, T3, T4)',
  'Hemoglobina Glucosilada (HbA1c)',
  'Proteína C Reactiva (PCR)',
  'Velocidad de Sedimentación Globular (VSG)',
  'Tiempos de Coagulación',
  'Grupo Sanguíneo y Factor RH',
  'Radiografía de Tórax',
  'Electrocardiograma',
  'Ultrasonido Abdominal'
]

const NIVELES_EDUCATIVOS_MEXICO = [
  'Sin Escolaridad',
  'Preescolar',
  'Primaria Incompleta',
  'Primaria Completa',
  'Secundaria Incompleta',
  'Secundaria Completa',
  'Preparatoria/Bachillerato Incompleto',
  'Preparatoria/Bachillerato Completo',
  'Universidad Incompleta',
  'Universidad Completa',
  'Posgrado'
]

const SUSTANCIAS_TOXICAS = [
  'Plomo',
  'Asbesto/Amianto',
  'Mercurio',
  'Arsénico',
  'Plaguicidas/Pesticidas',
  'Solventes Industriales',
  'Hidrocarburos',
  'Monóxido de Carbono',
  'Alcohol (Consumo Familiar)',
  'Tabaco (Fumador Pasivo)',
  'Cannabis/Marihuana',
  'Cocaína',
  'LSD/Alucinógenos',
  'Metanfetaminas',
  'Inhalantes (Thinner, Pegamento)'
]

const VACUNAS_IMSS = [
  { nombre: 'BCG', edades: ['Recién nacido'], dosis: 1 },
  { nombre: 'Hepatitis B', edades: ['Recién nacido', '2 meses', '6 meses'], dosis: 3 },
  { nombre: 'Pentavalente (DPT+Hib+HepB)', edades: ['2 meses', '4 meses', '6 meses', '18 meses'], dosis: 4 },
  { nombre: 'Rotavirus', edades: ['2 meses', '4 meses'], dosis: 2 },
  { nombre: 'Neumococo', edades: ['2 meses', '4 meses', '12 meses'], dosis: 3 },
  { nombre: 'Influenza', edades: ['6 meses', '7 meses', 'Anual'], dosis: 2 },
  { nombre: 'SRP (Sarampión, Rubéola, Parotiditis)', edades: ['12 meses', '6 años'], dosis: 2 },
  { nombre: 'Varicela', edades: ['12 meses'], dosis: 1 },
  { nombre: 'Hepatitis A', edades: ['12 meses'], dosis: 1 },
  { nombre: 'DPT (Refuerzo)', edades: ['4 años'], dosis: 1 },
  { nombre: 'VPH (Virus del Papiloma Humano)', edades: ['11 años (niñas)'], dosis: 2 },
  { nombre: 'Td/Tdap (Tétanos, Difteria)', edades: ['Refuerzos cada 10 años'], dosis: 1 }
]

// Paleta de colores pasteles moderna
const colors = {
  primary: 'bg-gradient-to-br from-purple-100 to-purple-50',
  secondary: 'bg-gradient-to-br from-blue-100 to-blue-50',
  success: 'bg-gradient-to-br from-green-100 to-green-50',
  warning: 'bg-gradient-to-br from-amber-100 to-amber-50',
  info: 'bg-gradient-to-br from-cyan-100 to-cyan-50',
  rose: 'bg-gradient-to-br from-rose-100 to-rose-50',
}

interface Tab {
  id: string
  name: string
  icon: any
  color: string
}

const tabs: Tab[] = [
  { id: 'general', name: 'Datos Generales', icon: User, color: colors.primary },
  { id: 'padecimiento', name: 'Padecimiento Actual', icon: ClipboardList, color: colors.warning },
  { id: 'familiares', name: 'Ant. Familiares', icon: Users, color: colors.secondary },
  { id: 'perinatales', name: 'Ant. Perinatales', icon: Baby, color: colors.rose },
  { id: 'vivienda', name: 'Vivienda', icon: Home, color: colors.info },
  { id: 'exploracion', name: 'Exploración Física', icon: Stethoscope, color: colors.success },
  { id: 'alimentacion', name: 'Alimentación', icon: Heart, color: colors.warning },
  { id: 'vacunacion', name: 'Vacunación', icon: Syringe, color: colors.rose },
  { id: 'desarrollo', name: 'Desarrollo', icon: TrendingUp, color: colors.info },
  { id: 'consultas', name: 'Consultas y Reportes', icon: Activity, color: colors.primary },
]

const HistoriaClinica = () => {
  const { pacienteId } = useParams()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('general')
  const [loading, setLoading] = useState(false)
  const [paciente, setPaciente] = useState<any>(null)
  const [formData, setFormData] = useState<any>({})

  useEffect(() => {
    if (pacienteId) {
      cargarPaciente()
    }
  }, [pacienteId])

  const cargarPaciente = async () => {
    try {
      const response = await api.get(`/pacientes/${pacienteId}`)
      setPaciente(response.data)
    } catch (error) {
      console.error('Error al cargar paciente:', error)
    }
  }

  const handleSubmit = async () => {
    setLoading(true)
    try {
      const historiaData = {
        paciente_id: pacienteId,
        ...formData
      }
      await api.post('/historias-clinicas/', historiaData)
      alert('Historia clínica guardada exitosamente')
      navigate(`/pacientes/${pacienteId}`)
    } catch (error: any) {
      console.error('Error:', error)
      alert(error.response?.data?.detail || 'Error al guardar')
    } finally {
      setLoading(false)
    }
  }

  const updateField = (field: string, value: any) => {
    setFormData((prev: any) => ({ ...prev, [field]: value }))
  }

  const currentTab = tabs.find((tab) => tab.id === activeTab)
  const currentIndex = Math.max(tabs.findIndex((tab) => tab.id === activeTab), 0)
  const progress = Math.round(((currentIndex + 1) / tabs.length) * 100)

  const metrics: WorkspaceMetric[] = [
    {
      label: 'Edad',
      value: paciente?.fecha_nacimiento ? `${calculateAge(paciente.fecha_nacimiento)} años` : 'Sin registro',
      tone: 'cyan',
    },
    {
      label: 'Servicio médico',
      value: formData.servicio_medico || 'No capturado',
      tone: 'violet',
    },
    {
      label: 'Progreso',
      value: `${progress}%`,
      helper: currentTab?.name ? `Sección actual: ${currentTab.name}` : undefined,
      tone: 'emerald',
    },
    {
      label: 'Consultas registradas',
      value: formData?.consultas?.length ? `${formData.consultas.length}` : '0',
      tone: 'amber',
    },
  ]

  const sidebar = (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Progreso de captura</h3>
      <p className="mt-2 text-4xl font-semibold text-slate-900">{progress}%</p>
      <p className="text-sm text-slate-500">{currentTab?.name || 'Inicia el registro'}</p>
      <div className="mt-4 space-y-2">
        {tabs.map((tab) => (
          <div
            key={tab.id}
            className={`flex items-center justify-between rounded-2xl border px-3 py-2 text-sm ${
              tab.id === activeTab
                ? 'border-indigo-200 bg-indigo-50 text-indigo-700'
                : 'border-slate-100 bg-slate-50 text-slate-500'
            }`}
          >
            <span>{tab.name}</span>
            {tab.id === activeTab && <span className="text-xs font-semibold">Activo</span>}
          </div>
        ))}
      </div>
    </div>
  )

  return (
    <PatientWorkspaceLayout
      title="Historia Clínica Pediátrica"
      subtitle="Documenta antecedentes, exploraciones y evolución con una experiencia guiada y asistida por IA."
      breadcrumbs={[
        { label: 'Pacientes', to: '/pacientes' },
        { label: paciente?.nombre_completo || 'Historia clínica' },
      ]}
      patient={{
        name: paciente?.nombre_completo,
        expediente: paciente?.numero_expediente,
        tags: [paciente?.genero, paciente?.tipo_sangre].filter(Boolean) as string[],
      }}
      metrics={metrics}
      actions={
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-2xl bg-white/10 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-black/20 transition hover:bg-white/20 disabled:opacity-60"
        >
          <Save className="h-4 w-4" />
          {loading ? 'Guardando…' : 'Guardar historia'}
        </button>
      }
      sidebar={sidebar}
    >
      <div className="overflow-x-auto">
        <div className="flex flex-wrap gap-2 pb-4">
          {tabs.map((tab) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id

            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 rounded-xl border px-3 py-2 text-sm font-medium transition-all duration-300 whitespace-nowrap ${
                  isActive
                    ? 'border-indigo-200 bg-indigo-50 text-indigo-700 shadow-lg'
                    : 'border-slate-200 bg-white text-slate-500 hover:text-slate-900'
                }`}
              >
                <Icon className={`h-4 w-4 ${isActive ? 'text-indigo-600' : 'text-slate-400'}`} />
                {tab.name}
              </button>
            )
          })}
        </div>
      </div>

      <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-xl min-h-[600px]">
        {activeTab === 'general' && <SeccionGeneral formData={formData} updateField={updateField} />}
        {activeTab === 'padecimiento' && <SeccionPadecimiento formData={formData} updateField={updateField} />}
        {activeTab === 'familiares' && <SeccionFamiliares formData={formData} updateField={updateField} />}
        {activeTab === 'perinatales' && <SeccionPerinatales formData={formData} updateField={updateField} />}
        {activeTab === 'vivienda' && <SeccionVivienda formData={formData} updateField={updateField} />}
        {activeTab === 'exploracion' && <SeccionExploracion formData={formData} updateField={updateField} />}
        {activeTab === 'alimentacion' && <SeccionAlimentacion formData={formData} updateField={updateField} />}
        {activeTab === 'vacunacion' && <SeccionVacunacion formData={formData} updateField={updateField} />}
        {activeTab === 'desarrollo' && <SeccionDesarrollo formData={formData} updateField={updateField} />}
        {activeTab === 'consultas' && <SeccionConsultasReportes formData={formData} updateField={updateField} />}
      </div>

      <div className="flex flex-wrap gap-4 justify-end">
        <button
          onClick={() => navigate(-1)}
          className="rounded-2xl border border-slate-200 px-6 py-3 text-sm font-semibold text-slate-600 hover:bg-slate-50"
        >
          Cancelar
        </button>
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="rounded-2xl bg-gradient-to-r from-indigo-500 to-purple-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30 transition hover:shadow-2xl disabled:opacity-60"
        >
          <Save className="h-4 w-4" />
          {loading ? 'Guardando…' : 'Guardar historia clínica'}
        </button>
      </div>
    </PatientWorkspaceLayout>
  )
}

// ============================================================================
// COMPONENTES DE SECCIONES
// ============================================================================

const InputField = ({ label, value, onChange, type = 'text', ...props }: any) => (
  <div>
    <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
    <input
      type={type}
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

const CheckboxField = ({ label, checked, onChange }: any) => (
  <label className="flex items-center gap-3 cursor-pointer group">
    <div className="relative">
      <input
        type="checkbox"
        checked={checked || false}
        onChange={(e) => onChange(e.target.checked)}
        className="w-5 h-5 rounded border-2 border-gray-300 text-purple-500 focus:ring-4 focus:ring-purple-100 transition-all cursor-pointer"
      />
    </div>
    <span className="text-gray-700 group-hover:text-gray-900 transition-colors">{label}</span>
  </label>
)

const SelectField = ({ label, value, onChange, options, ...props }: any) => (
  <div>
    <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
    <select
      value={value || ''}
      onChange={(e) => onChange(e.target.value)}
      className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-400 focus:ring-4 focus:ring-purple-100 transition-all outline-none bg-white"
      {...props}
    >
      <option value="">Seleccionar...</option>
      {options.map((option: string) => (
        <option key={option} value={option}>{option}</option>
      ))}
    </select>
  </div>
)

const SeccionGeneral = ({ formData, updateField }: any) => (
  <div className="space-y-6 animate-fadeIn">
    <h2 className="text-2xl font-bold text-gray-800 mb-6">Datos Generales</h2>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <SelectField
        label="Servicio de Atención Médica"
        value={formData.servicio_medico}
        onChange={(v: string) => updateField('servicio_medico', v)}
        options={SERVICIOS_MEDICOS_MEXICO}
      />
      <InputField
        label="Número de Afiliación"
        value={formData.numero_afiliacion}
        onChange={(v: string) => updateField('numero_afiliacion', v)}
        placeholder="Ej: 123456789"
      />
      <InputField
        label="Informante (Parentesco)"
        value={formData.informante_parentesco}
        onChange={(v: string) => updateField('informante_parentesco', v)}
        placeholder="Ej: Madre, Padre, Tutor"
      />
      <InputField
        label="Edad del Informante"
        type="number"
        value={formData.informante_edad}
        onChange={(v: string) => updateField('informante_edad', parseInt(v) || null)}
      />
      <SelectField
        label="Escolaridad del Paciente"
        value={formData.escolaridad_paciente}
        onChange={(v: string) => updateField('escolaridad_paciente', v)}
        options={NIVELES_EDUCATIVOS_MEXICO}
      />
    </div>
  </div>
)

const SeccionPadecimiento = ({ formData, updateField }: any) => {
  const handleExamenToggle = (examen: string) => {
    const examenes = formData.examenes_laboratorio || []
    const nuevosExamenes = examenes.includes(examen)
      ? examenes.filter((e: string) => e !== examen)
      : [...examenes, examen]
    updateField('examenes_laboratorio', nuevosExamenes)
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Padecimiento Actual</h2>
      <TextArea
        label="Síntomas en orden cronológico"
        value={formData.padecimiento_actual}
        onChange={(v: string) => updateField('padecimiento_actual', v)}
        rows={8}
        placeholder="Describa por separado cada uno de los síntomas, con la evolución de sus características, desde el inicio hasta el momento actual..."
      />
      <TextArea
        label="Diagnósticos Previos"
        value={formData.diagnosticos_previos}
        onChange={(v: string) => updateField('diagnosticos_previos', v)}
        rows={3}
      />
      
      {/* Exámenes de Laboratorio - Checkboxes */}
      <div className="bg-blue-50 rounded-2xl p-6 border-2 border-blue-100">
        <h3 className="text-lg font-semibold text-blue-900 mb-4">Exámenes de Laboratorio y Gabinetes Previos</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mb-4">
          {EXAMENES_LABORATORIO.map((examen) => (
            <CheckboxField
              key={examen}
              label={examen}
              checked={formData.examenes_laboratorio?.includes(examen) || false}
              onChange={() => handleExamenToggle(examen)}
            />
          ))}
        </div>
        <TextArea
          label="Otros exámenes o resultados específicos"
          value={formData.examenes_previos}
          onChange={(v: string) => updateField('examenes_previos', v)}
          rows={3}
          placeholder="Escriba otros exámenes no listados o resultados específicos..."
        />
      </div>

      <TextArea
        label="Terapéutica Previa"
        value={formData.terapeutica_previa}
        onChange={(v: string) => updateField('terapeutica_previa', v)}
        rows={3}
      />
    </div>
  )
}

const SeccionFamiliares = ({ formData, updateField }: any) => (
  <div className="space-y-8 animate-fadeIn">
    <h2 className="text-2xl font-bold text-gray-800 mb-6">Antecedentes Familiares</h2>
    
    {/* Madre */}
    <div className="bg-rose-50 rounded-2xl p-6 border-2 border-rose-100">
      <h3 className="text-xl font-semibold text-rose-900 mb-4 flex items-center gap-2">
        <Users className="h-5 w-5" />
        Madre
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <CheckboxField
          label="Vive"
          checked={formData.madre_vive}
          onChange={(v: boolean) => updateField('madre_vive', v)}
        />
        <InputField
          label="Edad"
          type="number"
          value={formData.madre_edad}
          onChange={(v: string) => updateField('madre_edad', parseInt(v) || null)}
        />
        <SelectField
          label="Escolaridad"
          value={formData.madre_escolaridad}
          onChange={(v: string) => updateField('madre_escolaridad', v)}
          options={NIVELES_EDUCATIVOS_MEXICO}
        />
        <InputField
          label="Ocupación"
          value={formData.madre_ocupacion}
          onChange={(v: string) => updateField('madre_ocupacion', v)}
        />
        <InputField
          label="Gesta"
          type="number"
          value={formData.madre_gesta}
          onChange={(v: string) => updateField('madre_gesta', parseInt(v) || null)}
        />
        <InputField
          label="Partos"
          type="number"
          value={formData.madre_parto}
          onChange={(v: string) => updateField('madre_parto', parseInt(v) || null)}
        />
        <InputField
          label="Abortos"
          type="number"
          value={formData.madre_abortos}
          onChange={(v: string) => updateField('madre_abortos', parseInt(v) || null)}
        />
        <InputField
          label="Cesáreas"
          type="number"
          value={formData.madre_cesareas}
          onChange={(v: string) => updateField('madre_cesareas', parseInt(v) || null)}
        />
      </div>
    </div>

    {/* Padre */}
    <div className="bg-blue-50 rounded-2xl p-6 border-2 border-blue-100">
      <h3 className="text-xl font-semibold text-blue-900 mb-4 flex items-center gap-2">
        <User className="h-5 w-5" />
        Padre
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <CheckboxField
          label="Vive"
          checked={formData.padre_vive}
          onChange={(v: boolean) => updateField('padre_vive', v)}
        />
        <InputField
          label="Edad"
          type="number"
          value={formData.padre_edad}
          onChange={(v: string) => updateField('padre_edad', parseInt(v) || null)}
        />
        <SelectField
          label="Escolaridad"
          value={formData.padre_escolaridad}
          onChange={(v: string) => updateField('padre_escolaridad', v)}
          options={NIVELES_EDUCATIVOS_MEXICO}
        />
        <InputField
          label="Ocupación"
          value={formData.padre_ocupacion}
          onChange={(v: string) => updateField('padre_ocupacion', v)}
        />
      </div>
    </div>

    {/* Hermanos */}
    <div className="bg-purple-50 rounded-2xl p-6 border-2 border-purple-100">
      <h3 className="text-xl font-semibold text-purple-900 mb-4">Hermanos</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <InputField
          label="Número de Hermanos"
          type="number"
          value={formData.hermanos_numero}
          onChange={(v: string) => updateField('hermanos_numero', parseInt(v) || null)}
        />
        <InputField
          label="Vivos"
          type="number"
          value={formData.hermanos_vivos}
          onChange={(v: string) => updateField('hermanos_vivos', parseInt(v) || null)}
        />
        <InputField
          label="Muertos"
          type="number"
          value={formData.hermanos_muertos}
          onChange={(v: string) => updateField('hermanos_muertos', parseInt(v) || null)}
        />
      </div>
    </div>
  </div>
)

const SeccionPerinatales = ({ formData, updateField }: any) => (
  <div className="space-y-6 animate-fadeIn">
    <h2 className="text-2xl font-bold text-gray-800 mb-6">Antecedentes Perinatales</h2>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <InputField
        label="Número de Embarazo"
        type="number"
        value={formData.embarazo_numero}
        onChange={(v: string) => updateField('embarazo_numero', parseInt(v) || null)}
      />
      <InputField
        label="Gestación (semanas)"
        type="number"
        value={formData.gestacion_semanas}
        onChange={(v: string) => updateField('gestacion_semanas', parseInt(v) || null)}
      />
      <InputField
        label="Peso al Nacer (kg)"
        type="number"
        step="0.01"
        value={formData.peso_nacimiento}
        onChange={(v: string) => updateField('peso_nacimiento', parseFloat(v) || null)}
      />
      <InputField
        label="Talla al Nacer (cm)"
        type="number"
        step="0.1"
        value={formData.talla_nacimiento}
        onChange={(v: string) => updateField('talla_nacimiento', parseFloat(v) || null)}
      />
      <SelectField
        label="Sitio de Atención del Parto"
        value={formData.sitio_atencion_parto}
        onChange={(v: string) => updateField('sitio_atencion_parto', v)}
        options={SERVICIOS_MEDICOS_MEXICO}
      />
    </div>
    <div className="mt-6 grid grid-cols-2 md:grid-cols-3 gap-4">
      <CheckboxField
        label="Apnea Neonatal"
        checked={formData.apnea_neonatal}
        onChange={(v: boolean) => updateField('apnea_neonatal', v)}
      />
      <CheckboxField
        label="Convulsiones"
        checked={formData.convulsiones_neonatales}
        onChange={(v: boolean) => updateField('convulsiones_neonatales', v)}
      />
      <CheckboxField
        label="Hemorragias"
        checked={formData.hemorragias_neonatales}
        onChange={(v: boolean) => updateField('hemorragias_neonatales', v)}
      />
      <CheckboxField
        label="Ictericia"
        checked={formData.ictericia_neonatal}
        onChange={(v: boolean) => updateField('ictericia_neonatal', v)}
      />
      <CheckboxField
        label="Cianosis"
        checked={formData.cianosis_neonatal}
        onChange={(v: boolean) => updateField('cianosis_neonatal', v)}
      />
    </div>
  </div>
)

const SeccionVivienda = ({ formData, updateField }: any) => {
  const handleSustanciaToggle = (sustancia: string) => {
    const sustancias = formData.sustancias_toxicas || []
    const nuevasSustancias = sustancias.includes(sustancia)
      ? sustancias.filter((s: string) => s !== sustancia)
      : [...sustancias, sustancia]
    updateField('sustancias_toxicas', nuevasSustancias)
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Condiciones de Vivienda</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <InputField
          label="Número de Cuartos"
          type="number"
          value={formData.num_cuartos_casa}
          onChange={(v: string) => updateField('num_cuartos_casa', parseInt(v) || null)}
        />
        <InputField
          label="Personas que Duermen en la Casa"
          type="number"
          value={formData.num_personas_duermen_casa}
          onChange={(v: string) => updateField('num_personas_duermen_casa', parseInt(v) || null)}
        />
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-6">
        <CheckboxField
          label="Refrigerador"
          checked={formData.tiene_refrigerador}
          onChange={(v: boolean) => updateField('tiene_refrigerador', v)}
        />
        <CheckboxField
          label="Teléfono"
          checked={formData.tiene_telefono}
          onChange={(v: boolean) => updateField('tiene_telefono', v)}
        />
        <CheckboxField
          label="Automóvil"
          checked={formData.tiene_automovil}
          onChange={(v: boolean) => updateField('tiene_automovil', v)}
        />
      </div>

      {/* Sustancias Tóxicas - Checkboxes */}
      <div className="bg-orange-50 rounded-2xl p-6 border-2 border-orange-100">
        <h3 className="text-lg font-semibold text-orange-900 mb-4">Exposición a Sustancias Tóxicas</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mb-4">
          {SUSTANCIAS_TOXICAS.map((sustancia) => (
            <CheckboxField
              key={sustancia}
              label={sustancia}
              checked={formData.sustancias_toxicas?.includes(sustancia) || false}
              onChange={() => handleSustanciaToggle(sustancia)}
            />
          ))}
        </div>
        <TextArea
          label="Otras sustancias o detalles adicionales"
          value={formData.exposicion_sustancias_toxicas}
          onChange={(v: string) => updateField('exposicion_sustancias_toxicas', v)}
          rows={3}
          placeholder="Describa otras sustancias no listadas o detalles adicionales de la exposición..."
        />
      </div>
    </div>
  )
}

const SeccionExploracion = ({ formData, updateField }: any) => (
  <div className="space-y-6 animate-fadeIn">
    <h2 className="text-2xl font-bold text-gray-800 mb-6">Exploración Física</h2>
    <div className="bg-green-50 rounded-2xl p-6 border-2 border-green-100 mb-6">
      <h3 className="text-lg font-semibold text-green-900 mb-4">Signos Vitales y Medidas</h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <InputField
          label="Peso (kg)"
          type="number"
          step="0.1"
          value={formData.peso}
          onChange={(v: string) => updateField('peso', parseFloat(v) || null)}
        />
        <InputField
          label="Talla (cm)"
          type="number"
          step="0.1"
          value={formData.talla}
          onChange={(v: string) => updateField('talla', parseFloat(v) || null)}
        />
        <InputField
          label="FC (lpm)"
          type="number"
          value={formData.frecuencia_cardiaca}
          onChange={(v: string) => updateField('frecuencia_cardiaca', parseInt(v) || null)}
        />
        <InputField
          label="FR (rpm)"
          type="number"
          value={formData.frecuencia_respiratoria}
          onChange={(v: string) => updateField('frecuencia_respiratoria', parseInt(v) || null)}
        />
        <InputField
          label="Temp (°C)"
          type="number"
          step="0.1"
          value={formData.temperatura}
          onChange={(v: string) => updateField('temperatura', parseFloat(v) || null)}
        />
        <InputField
          label="TA"
          placeholder="120/80"
          value={formData.tension_arterial}
          onChange={(v: string) => updateField('tension_arterial', v)}
        />
      </div>
    </div>
  </div>
)

const SeccionAlimentacion = ({ formData, updateField }: any) => (
  <div className="space-y-6 animate-fadeIn">
    <h2 className="text-2xl font-bold text-gray-800 mb-6">Alimentación</h2>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <InputField
        label="Pecho Materno (meses)"
        type="number"
        value={formData.pecho_materno_duracion_meses}
        onChange={(v: string) => updateField('pecho_materno_duracion_meses', parseInt(v) || null)}
      />
      <InputField
        label="Ablactación (meses)"
        type="number"
        value={formData.ablactacion_meses}
        onChange={(v: string) => updateField('ablactacion_meses', parseInt(v) || null)}
      />
      <InputField
        label="Destete (meses)"
        type="number"
        value={formData.destete_meses}
        onChange={(v: string) => updateField('destete_meses', parseInt(v) || null)}
      />
    </div>
  </div>
)

const SeccionVacunacion = ({ formData, updateField }: any) => {
  const handleVacunaToggle = (nombreVacuna: string, dosis: number) => {
    const vacunas = formData.vacunas || []
    const key = `${nombreVacuna}_${dosis}`
    
    const nuevasVacunas = vacunas.includes(key)
      ? vacunas.filter((v: string) => v !== key)
      : [...vacunas, key]
    
    updateField('vacunas', nuevasVacunas)
  }

  const isVacunaAplicada = (nombreVacuna: string, dosis: number) => {
    const vacunas = formData.vacunas || []
    return vacunas.includes(`${nombreVacuna}_${dosis}`)
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Esquema de Vacunación</h2>
      
      <div className="bg-gradient-to-br from-pink-50 to-purple-50 rounded-2xl p-6 border-2 border-purple-100 mb-6">
        <h3 className="text-lg font-semibold text-purple-900 mb-2 flex items-center gap-2">
          <Syringe className="h-5 w-5" />
          Esquema Nacional de Vacunación (México - IMSS)
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          Seleccione las vacunas aplicadas según el esquema oficial del IMSS
        </p>
      </div>

      {VACUNAS_IMSS.map((vacuna, index) => {
        const colorClasses = [
          'bg-blue-50 border-blue-100',
          'bg-green-50 border-green-100',
          'bg-yellow-50 border-yellow-100',
          'bg-pink-50 border-pink-100',
          'bg-purple-50 border-purple-100',
          'bg-indigo-50 border-indigo-100'
        ]
        const colorClass = colorClasses[index % colorClasses.length]

        return (
          <div key={vacuna.nombre} className={`rounded-2xl p-6 border-2 ${colorClass}`}>
            <h4 className="text-lg font-bold text-gray-800 mb-3">{vacuna.nombre}</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {vacuna.edades.map((edad, dosisIndex) => {
                const dosisNumero = dosisIndex + 1
                return (
                  <div key={`${vacuna.nombre}_${dosisNumero}`} className="bg-white rounded-xl p-4 border border-gray-200">
                    <CheckboxField
                      label={`Dosis ${dosisNumero}: ${edad}`}
                      checked={isVacunaAplicada(vacuna.nombre, dosisNumero)}
                      onChange={() => handleVacunaToggle(vacuna.nombre, dosisNumero)}
                    />
                  </div>
                )
              })}
            </div>
          </div>
        )
      })}

      {/* Vacunas Adicionales */}
      <div className="bg-gray-50 rounded-2xl p-6 border-2 border-gray-200">
        <h4 className="text-lg font-bold text-gray-800 mb-4">Vacunas Adicionales o No Incluidas en el Esquema</h4>
        <TextArea
          label="Otras vacunas aplicadas"
          value={formData.vacunas_adicionales}
          onChange={(v: string) => updateField('vacunas_adicionales', v)}
          rows={4}
          placeholder="Ej: COVID-19 (Pfizer, 2 dosis), Fiebre Amarilla, etc..."
        />
      </div>

      {/* Observaciones Generales */}
      <div className="bg-amber-50 rounded-2xl p-6 border-2 border-amber-100">
        <h4 className="text-lg font-bold text-amber-900 mb-4">Observaciones sobre Vacunación</h4>
        <TextArea
          label="Notas adicionales"
          value={formData.observaciones_vacunacion}
          onChange={(v: string) => updateField('observaciones_vacunacion', v)}
          rows={3}
          placeholder="Reacciones adversas, contraindicaciones, esquema incompleto, etc..."
        />
      </div>
    </div>
  )
}

const SeccionDesarrollo = ({ formData, updateField }: any) => (
  <div className="space-y-6 animate-fadeIn">
    <h2 className="text-2xl font-bold text-gray-800 mb-6">Desarrollo Psicomotor</h2>
    <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
      <InputField
        label="Siguió Objetos (meses)"
        type="number"
        value={formData.desarrollo_siguio_objetos_meses}
        onChange={(v: string) => updateField('desarrollo_siguio_objetos_meses', parseInt(v) || null)}
      />
      <InputField
        label="Sonrió (meses)"
        type="number"
        value={formData.desarrollo_sonrio_meses}
        onChange={(v: string) => updateField('desarrollo_sonrio_meses', parseInt(v) || null)}
      />
      <InputField
        label="Sostuvo Cabeza (meses)"
        type="number"
        value={formData.desarrollo_sostuvo_cabeza_meses}
        onChange={(v: string) => updateField('desarrollo_sostuvo_cabeza_meses', parseInt(v) || null)}
      />
      <InputField
        label="Se Sentó (meses)"
        type="number"
        value={formData.desarrollo_se_sento_meses}
        onChange={(v: string) => updateField('desarrollo_se_sento_meses', parseInt(v) || null)}
      />
      <InputField
        label="Caminó (meses)"
        type="number"
        value={formData.desarrollo_camino_meses}
        onChange={(v: string) => updateField('desarrollo_camino_meses', parseInt(v) || null)}
      />
    </div>
  </div>
)

const SeccionConsultasReportes = ({ formData, updateField }: any) => (
  <div className="space-y-6 animate-fadeIn">
    <h2 className="text-2xl font-bold text-gray-800 mb-6">Consultas y Reportes</h2>
    
    {/* Impresión Diagnóstica */}
    <div className="bg-purple-50 rounded-2xl p-6 border-2 border-purple-100">
      <h3 className="text-xl font-semibold text-purple-900 mb-4 flex items-center gap-2">
        <Activity className="h-5 w-5" />
        Impresión Diagnóstica
      </h3>
      <TextArea
        label="Diagnóstico Principal"
        value={formData.diagnostico_principal}
        onChange={(v: string) => updateField('diagnostico_principal', v)}
        rows={4}
        placeholder="Escriba el diagnóstico principal basado en la historia clínica..."
      />
      <div className="mt-4">
        <TextArea
          label="Diagnósticos Secundarios"
          value={formData.diagnosticos_secundarios}
          onChange={(v: string) => updateField('diagnosticos_secundarios', v)}
          rows={3}
          placeholder="Diagnósticos adicionales o comorbilidades..."
        />
      </div>
    </div>

    {/* Plan de Tratamiento */}
    <div className="bg-blue-50 rounded-2xl p-6 border-2 border-blue-100">
      <h3 className="text-xl font-semibold text-blue-900 mb-4">Plan de Tratamiento</h3>
      <TextArea
        label="Indicaciones Terapéuticas"
        value={formData.plan_tratamiento}
        onChange={(v: string) => updateField('plan_tratamiento', v)}
        rows={5}
        placeholder="Medicamentos, dosis, frecuencia y duración del tratamiento..."
      />
    </div>

    {/* Estudios y Laboratorios */}
    <div className="bg-green-50 rounded-2xl p-6 border-2 border-green-100">
      <h3 className="text-xl font-semibold text-green-900 mb-4">Estudios Solicitados</h3>
      <TextArea
        label="Laboratorios y Estudios de Gabinete"
        value={formData.estudios_solicitados}
        onChange={(v: string) => updateField('estudios_solicitados', v)}
        rows={4}
        placeholder="Estudios de laboratorio, radiografías, ultrasonidos, etc..."
      />
    </div>

    {/* Recomendaciones */}
    <div className="bg-amber-50 rounded-2xl p-6 border-2 border-amber-100">
      <h3 className="text-xl font-semibold text-amber-900 mb-4">Recomendaciones y Seguimiento</h3>
      <TextArea
        label="Indicaciones al Paciente/Familia"
        value={formData.recomendaciones}
        onChange={(v: string) => updateField('recomendaciones', v)}
        rows={4}
        placeholder="Signos de alarma, cuidados en casa, alimentación, restricciones..."
      />
      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
        <InputField
          label="Próxima Consulta"
          type="date"
          value={formData.proxima_consulta}
          onChange={(v: string) => updateField('proxima_consulta', v)}
        />
        <InputField
          label="Días de Incapacidad"
          type="number"
          value={formData.dias_incapacidad}
          onChange={(v: string) => updateField('dias_incapacidad', parseInt(v) || null)}
          placeholder="0"
        />
      </div>
    </div>

    {/* Pronóstico */}
    <div className="bg-rose-50 rounded-2xl p-6 border-2 border-rose-100">
      <h3 className="text-xl font-semibold text-rose-900 mb-4">Pronóstico</h3>
      <div className="grid grid-cols-3 gap-4">
        <label className="flex items-center justify-center gap-2 cursor-pointer p-4 rounded-xl border-2 border-gray-200 hover:border-green-400 hover:bg-green-50 transition-all">
          <input
            type="radio"
            name="pronostico"
            value="bueno"
            checked={formData.pronostico === 'bueno'}
            onChange={(e) => updateField('pronostico', e.target.value)}
            className="w-4 h-4 text-green-500"
          />
          <span className="font-medium text-gray-700">Bueno</span>
        </label>
        <label className="flex items-center justify-center gap-2 cursor-pointer p-4 rounded-xl border-2 border-gray-200 hover:border-yellow-400 hover:bg-yellow-50 transition-all">
          <input
            type="radio"
            name="pronostico"
            value="reservado"
            checked={formData.pronostico === 'reservado'}
            onChange={(e) => updateField('pronostico', e.target.value)}
            className="w-4 h-4 text-yellow-500"
          />
          <span className="font-medium text-gray-700">Reservado</span>
        </label>
        <label className="flex items-center justify-center gap-2 cursor-pointer p-4 rounded-xl border-2 border-gray-200 hover:border-red-400 hover:bg-red-50 transition-all">
          <input
            type="radio"
            name="pronostico"
            value="grave"
            checked={formData.pronostico === 'grave'}
            onChange={(e) => updateField('pronostico', e.target.value)}
            className="w-4 h-4 text-red-500"
          />
          <span className="font-medium text-gray-700">Grave</span>
        </label>
      </div>
    </div>

    {/* Médico Responsable */}
    <div className="bg-indigo-50 rounded-2xl p-6 border-2 border-indigo-100">
      <h3 className="text-xl font-semibold text-indigo-900 mb-4">Médico Responsable</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <InputField
          label="Nombre del Médico"
          value={formData.nombre_medico}
          onChange={(v: string) => updateField('nombre_medico', v)}
          placeholder="Dr(a). Nombre completo"
        />
        <InputField
          label="Cédula Profesional"
          value={formData.cedula_medico}
          onChange={(v: string) => updateField('cedula_medico', v)}
          placeholder="Número de cédula"
        />
        <InputField
          label="Especialidad"
          value={formData.especialidad_medico}
          onChange={(v: string) => updateField('especialidad_medico', v)}
          placeholder="Pediatría, Medicina General, etc."
        />
        <InputField
          label="Firma Digital"
          value={formData.firma_medico}
          onChange={(v: string) => updateField('firma_medico', v)}
          placeholder="Código de firma electrónica"
        />
      </div>
    </div>

    {/* Notas Adicionales */}
    <div className="bg-gray-50 rounded-2xl p-6 border-2 border-gray-200">
      <h3 className="text-xl font-semibold text-gray-900 mb-4">Notas Adicionales</h3>
      <TextArea
        label="Observaciones Generales"
        value={formData.notas_adicionales}
        onChange={(v: string) => updateField('notas_adicionales', v)}
        rows={4}
        placeholder="Información adicional relevante que no se haya incluido en otras secciones..."
      />
    </div>
  </div>
)

export default HistoriaClinica
