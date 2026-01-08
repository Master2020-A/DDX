import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { 
  ArrowLeft, FileText, User, Users, Baby, Home, 
  Stethoscope, Heart, Syringe, TrendingUp, Calendar,
  Download, Edit, Printer, ClipboardList
} from 'lucide-react'
import api from '@/lib/api'

const VerHistoriaClinica = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [historia, setHistoria] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (id) {
      cargarHistoria()
    }
  }, [id])

  const cargarHistoria = async () => {
    try {
      const response = await api.get(`/historias-clinicas/${id}`)
      setHistoria(response.data)
    } catch (error) {
      console.error('Error al cargar historia:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatearFecha = (fecha: string) => {
    if (!fecha) return 'N/A'
    return new Date(fecha).toLocaleDateString('es-MX', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 p-6 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando historia clínica...</p>
        </div>
      </div>
    )
  }

  if (!historia) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 p-6">
        <div className="max-w-7xl mx-auto text-center py-12">
          <p className="text-gray-600">Historia clínica no encontrada</p>
          <button
            onClick={() => navigate(-1)}
            className="mt-4 px-6 py-3 rounded-2xl font-medium text-white bg-gradient-to-r from-purple-500 to-pink-500"
          >
            Volver
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-purple-600 hover:text-purple-700 mb-4 transition-colors"
          >
            <ArrowLeft className="h-5 w-5" />
            <span className="font-medium">Volver</span>
          </button>
          
          <div className="bg-white rounded-3xl shadow-xl p-8 border border-purple-100">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-4 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl">
                  <FileText className="h-8 w-8 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                    Historia Clínica Pediátrica
                  </h1>
                  <p className="text-gray-600 mt-1">
                    Fecha: <span className="font-semibold text-gray-800">{formatearFecha(historia.fecha)}</span>
                  </p>
                </div>
              </div>
              
              <div className="flex gap-3">
                <button
                  onClick={() => window.print()}
                  className="px-4 py-3 rounded-xl font-medium text-purple-600 bg-purple-50 hover:bg-purple-100 transition-colors flex items-center gap-2"
                >
                  <Printer className="h-5 w-5" />
                  Imprimir
                </button>
                <button
                  className="px-4 py-3 rounded-xl font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 transition-colors flex items-center gap-2"
                >
                  <Download className="h-5 w-5" />
                  PDF
                </button>
                <button
                  onClick={() => navigate(`/historia-clinica/${historia.paciente_id}`)}
                  className="px-4 py-3 rounded-xl font-medium text-white bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 transition-all flex items-center gap-2"
                >
                  <Edit className="h-5 w-5" />
                  Editar
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="space-y-6">
          {/* Datos Generales */}
          <SeccionCard
            icon={User}
            titulo="Datos Generales"
            color="from-purple-500 to-purple-400"
          >
            <CampoInfo label="Número de Afiliación" valor={historia.numero_afiliacion} />
            <CampoInfo label="Informante" valor={historia.informante_parentesco} />
            <CampoInfo label="Edad del Informante" valor={historia.informante_edad} />
            <CampoInfo label="Escolaridad del Paciente" valor={historia.escolaridad_paciente} />
          </SeccionCard>

          {/* Padecimiento Actual */}
          {historia.padecimiento_actual && (
            <SeccionCard
              icon={ClipboardList}
              titulo="Padecimiento Actual"
              color="from-amber-500 to-amber-400"
            >
              <CampoTexto label="Síntomas" valor={historia.padecimiento_actual} />
              <CampoTexto label="Diagnósticos Previos" valor={historia.diagnosticos_previos} />
              <CampoTexto label="Exámenes Previos" valor={historia.examenes_previos} />
              <CampoTexto label="Terapéutica Previa" valor={historia.terapeutica_previa} />
            </SeccionCard>
          )}

          {/* Antecedentes Familiares */}
          <SeccionCard
            icon={Users}
            titulo="Antecedentes Familiares"
            color="from-blue-500 to-blue-400"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-rose-50 rounded-xl p-4">
                <h4 className="font-semibold text-rose-900 mb-3">Madre</h4>
                <CampoInfo label="Vive" valor={historia.madre_vive ? 'Sí' : 'No'} />
                <CampoInfo label="Edad" valor={historia.madre_edad} />
                <CampoInfo label="Ocupación" valor={historia.madre_ocupacion} />
                <CampoInfo label="Gesta" valor={historia.madre_gesta} />
                <CampoInfo label="Partos" valor={historia.madre_parto} />
              </div>
              
              <div className="bg-blue-50 rounded-xl p-4">
                <h4 className="font-semibold text-blue-900 mb-3">Padre</h4>
                <CampoInfo label="Vive" valor={historia.padre_vive ? 'Sí' : 'No'} />
                <CampoInfo label="Edad" valor={historia.padre_edad} />
                <CampoInfo label="Ocupación" valor={historia.padre_ocupacion} />
              </div>
            </div>
          </SeccionCard>

          {/* Antecedentes Perinatales */}
          <SeccionCard
            icon={Baby}
            titulo="Antecedentes Perinatales"
            color="from-rose-500 to-pink-400"
          >
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <CampoInfo label="Gestación (sem)" valor={historia.gestacion_semanas} />
              <CampoInfo label="Peso Nacimiento (kg)" valor={historia.peso_nacimiento} />
              <CampoInfo label="Talla Nacimiento (cm)" valor={historia.talla_nacimiento} />
              <CampoInfo label="Sitio de Parto" valor={historia.sitio_atencion_parto} />
            </div>
            {(historia.apnea_neonatal || historia.ictericia_neonatal || historia.convulsiones_neonatales) && (
              <div className="mt-4 p-4 bg-red-50 rounded-xl">
                <h5 className="font-semibold text-red-900 mb-2">Complicaciones Neonatales</h5>
                <div className="flex flex-wrap gap-2">
                  {historia.apnea_neonatal && <Badge>Apnea</Badge>}
                  {historia.ictericia_neonatal && <Badge>Ictericia</Badge>}
                  {historia.convulsiones_neonatales && <Badge>Convulsiones</Badge>}
                  {historia.hemorragias_neonatales && <Badge>Hemorragias</Badge>}
                  {historia.cianosis_neonatal && <Badge>Cianosis</Badge>}
                </div>
              </div>
            )}
          </SeccionCard>

          {/* Exploración Física */}
          {historia.exploracion_fisica && (
            <SeccionCard
              icon={Stethoscope}
              titulo="Exploración Física"
              color="from-green-500 to-emerald-400"
            >
              <div className="bg-green-50 rounded-xl p-4 mb-4">
                <h5 className="font-semibold text-green-900 mb-3">Signos Vitales</h5>
                <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
                  <CampoInfo label="Peso (kg)" valor={historia.exploracion_fisica.peso} />
                  <CampoInfo label="Talla (cm)" valor={historia.exploracion_fisica.talla} />
                  <CampoInfo label="FC (lpm)" valor={historia.exploracion_fisica.frecuencia_cardiaca} />
                  <CampoInfo label="FR (rpm)" valor={historia.exploracion_fisica.frecuencia_respiratoria} />
                  <CampoInfo label="Temp (°C)" valor={historia.exploracion_fisica.temperatura} />
                  <CampoInfo label="TA" valor={historia.exploracion_fisica.tension_arterial} />
                </div>
              </div>
              <CampoTexto label="Piel y Faneras" valor={historia.exploracion_fisica.piel_faneras} />
              <CampoTexto label="Cabeza" valor={historia.exploracion_fisica.cabeza} />
              <CampoTexto label="Tórax" valor={historia.exploracion_fisica.torax_ap_respiratorio} />
              <CampoTexto label="Abdomen" valor={historia.exploracion_fisica.abdomen} />
            </SeccionCard>
          )}

          {/* Antecedentes No Patológicos */}
          {historia.antecedentes_no_patologicos && (
            <SeccionCard
              icon={Heart}
              titulo="Alimentación y Desarrollo"
              color="from-orange-500 to-yellow-400"
            >
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <CampoInfo 
                  label="Lactancia Materna (meses)" 
                  valor={historia.antecedentes_no_patologicos.pecho_materno_duracion_meses} 
                />
                <CampoInfo 
                  label="Ablactación (meses)" 
                  valor={historia.antecedentes_no_patologicos.ablactacion_meses} 
                />
                <CampoInfo 
                  label="Destete (meses)" 
                  valor={historia.antecedentes_no_patologicos.destete_meses} 
                />
              </div>
              
              <div className="mt-4">
                <h5 className="font-semibold text-gray-800 mb-2">Desarrollo Psicomotor</h5>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  <CampoInfo 
                    label="Sonrió" 
                    valor={`${historia.antecedentes_no_patologicos.desarrollo_sonrio_meses || 'N/A'} m`} 
                  />
                  <CampoInfo 
                    label="Sostuvo Cabeza" 
                    valor={`${historia.antecedentes_no_patologicos.desarrollo_sostuvo_cabeza_meses || 'N/A'} m`} 
                  />
                  <CampoInfo 
                    label="Se Sentó" 
                    valor={`${historia.antecedentes_no_patologicos.desarrollo_se_sento_meses || 'N/A'} m`} 
                  />
                  <CampoInfo 
                    label="Caminó" 
                    valor={`${historia.antecedentes_no_patologicos.desarrollo_camino_meses || 'N/A'} m`} 
                  />
                </div>
              </div>
            </SeccionCard>
          )}
        </div>
      </div>
    </div>
  )
}

// Componentes auxiliares
const SeccionCard = ({ icon: Icon, titulo, color, children }: any) => (
  <div className="bg-white rounded-2xl shadow-lg border-2 border-gray-100 overflow-hidden animate-fadeIn">
    <div className={`bg-gradient-to-r ${color} p-4 flex items-center gap-3`}>
      <Icon className="h-6 w-6 text-white" />
      <h2 className="text-xl font-bold text-white">{titulo}</h2>
    </div>
    <div className="p-6 space-y-4">
      {children}
    </div>
  </div>
)

const CampoInfo = ({ label, valor }: any) => (
  <div>
    <p className="text-sm text-gray-600 mb-1">{label}</p>
    <p className="font-medium text-gray-900">{valor || 'No especificado'}</p>
  </div>
)

const CampoTexto = ({ label, valor }: any) => {
  if (!valor) return null
  return (
    <div>
      <p className="text-sm font-semibold text-gray-700 mb-2">{label}</p>
      <p className="text-gray-800 whitespace-pre-wrap bg-gray-50 rounded-xl p-4">{valor}</p>
    </div>
  )
}

const Badge = ({ children }: any) => (
  <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">
    {children}
  </span>
)

export default VerHistoriaClinica
