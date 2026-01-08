import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Plus, TestTube, Pill, Stethoscope } from 'lucide-react'
import api from '@/lib/api'
import { Consulta, Paciente, Diagnostico, PruebaMedica, Tratamiento } from '@/types'
import { formatDateTime } from '@/lib/utils'
import NuevoDiagnosticoModal from '@/components/modals/NuevoDiagnosticoModal'

const ConsultaDetalle = () => {
  const { id } = useParams()
  const [consulta, setConsulta] = useState<Consulta | null>(null)
  const [paciente, setPaciente] = useState<Paciente | null>(null)
  const [diagnosticos, setDiagnosticos] = useState<Diagnostico[]>([])
  const [pruebas, setPruebas] = useState<PruebaMedica[]>([])
  const [tratamientos, setTratamientos] = useState<Tratamiento[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'diagnostico' | 'pruebas' | 'tratamiento'>('diagnostico')
  const [showDiagnosticoModal, setShowDiagnosticoModal] = useState(false)
  const [currentUser, setCurrentUser] = useState<any>(null)

  useEffect(() => {
    if (id) {
      fetchConsultaData(id)
    }
    
    // Obtener usuario actual
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    setCurrentUser(user)
  }, [id])

  const fetchConsultaData = async (consultaId: string) => {
    try {
      const consultaRes = await api.get(`/consultas/${consultaId}`)
      const consulta = consultaRes.data
      setConsulta(consulta)

      const [pacienteRes, diagnosticosRes, pruebasRes, tratamientosRes] = await Promise.all([
        api.get(`/pacientes/${consulta.paciente_id}`),
        api.get(`/diagnosticos/consulta/${consultaId}`),
        api.get(`/pruebas/consulta/${consultaId}`),
        api.get(`/tratamientos/consulta/${consultaId}`),
      ])

      setPaciente(pacienteRes.data)
      setDiagnosticos(diagnosticosRes.data)
      setPruebas(pruebasRes.data)
      setTratamientos(tratamientosRes.data)
    } catch (error) {
      console.error('Error fetching consulta:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Cargando consulta...</p>
      </div>
    )
  }

  if (!consulta || !paciente) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Consulta no encontrada</p>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-6">
        <Link to={`/pacientes/${paciente.id}`} className="inline-flex items-center text-primary-600 hover:text-primary-700">
          <ArrowLeft size={20} className="mr-2" />
          Volver al paciente
        </Link>
      </div>

      {/* Header */}
      <div className="card mb-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Consulta Médica</h1>
            <p className="text-gray-600">
              Paciente: <Link to={`/pacientes/${paciente.id}`} className="text-primary-600 hover:underline font-medium">
                {paciente.nombre_completo}
              </Link>
            </p>
            <p className="text-gray-600">{formatDateTime(consulta.fecha_hora)}</p>
          </div>
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${
              consulta.estado === 'completada'
                ? 'bg-green-100 text-green-700'
                : consulta.estado === 'en_proceso'
                ? 'bg-yellow-100 text-yellow-700'
                : 'bg-blue-100 text-blue-700'
            }`}
          >
            {consulta.estado.replace('_', ' ')}
          </span>
        </div>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm font-medium text-gray-500 mb-1">Motivo de consulta</p>
            <p className="text-gray-900">{consulta.motivo_consulta}</p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500 mb-1">Síntomas</p>
            <div className="flex flex-wrap gap-1">
              {consulta.sintomas.map((sintoma, idx) => (
                <span key={idx} className="px-2 py-1 bg-primary-50 text-primary-700 rounded text-sm">
                  {sintoma}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('diagnostico')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'diagnostico'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Stethoscope className="inline mr-2" size={18} />
              Diagnóstico
            </button>
            <button
              onClick={() => setActiveTab('pruebas')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'pruebas'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <TestTube className="inline mr-2" size={18} />
              Pruebas ({pruebas.length})
            </button>
            <button
              onClick={() => setActiveTab('tratamiento')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'tratamiento'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Pill className="inline mr-2" size={18} />
              Tratamiento ({tratamientos.length})
            </button>
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'diagnostico' && (
        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-900">Diagnósticos</h2>
            <button 
              onClick={() => setShowDiagnosticoModal(true)}
              className="btn btn-primary btn-sm flex items-center"
            >
              <Plus size={16} className="mr-1" />
              Nuevo Diagnóstico
            </button>
          </div>

          {diagnosticos.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No hay diagnósticos registrados</p>
          ) : (
            <div className="space-y-4">
              {diagnosticos.map((diagnostico) => (
                <div key={diagnostico.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium ${
                          diagnostico.tipo === 'diagnostico_confirmado'
                            ? 'bg-green-100 text-green-700'
                            : 'bg-yellow-100 text-yellow-700'
                        }`}
                      >
                        {diagnostico.tipo.replace('_', ' ')}
                      </span>
                      {diagnostico.codigo_cie10 && (
                        <span className="ml-2 text-sm text-gray-500">CIE-10: {diagnostico.codigo_cie10}</span>
                      )}
                    </div>
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${
                        diagnostico.estado === 'confirmado'
                          ? 'bg-green-100 text-green-700'
                          : diagnostico.estado === 'descartado'
                          ? 'bg-red-100 text-red-700'
                          : 'bg-blue-100 text-blue-700'
                      }`}
                    >
                      {diagnostico.estado}
                    </span>
                  </div>
                  <p className="font-semibold text-gray-900 mb-2">{diagnostico.descripcion}</p>
                  {diagnostico.justificacion && (
                    <p className="text-sm text-gray-600">{diagnostico.justificacion}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'pruebas' && (
        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-900">Pruebas Médicas</h2>
            <button className="btn btn-primary btn-sm flex items-center">
              <Plus size={16} className="mr-1" />
              Solicitar Prueba
            </button>
          </div>

          {pruebas.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No hay pruebas solicitadas</p>
          ) : (
            <div className="space-y-4">
              {pruebas.map((prueba) => (
                <div key={prueba.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="font-semibold text-gray-900">{prueba.nombre_prueba}</p>
                      <p className="text-sm text-gray-500 capitalize">{prueba.tipo_prueba}</p>
                    </div>
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${
                        prueba.estado === 'completada'
                          ? 'bg-green-100 text-green-700'
                          : prueba.estado === 'en_proceso'
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {prueba.estado}
                    </span>
                  </div>
                  {prueba.descripcion && <p className="text-sm text-gray-600">{prueba.descripcion}</p>}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'tratamiento' && (
        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-900">Tratamientos</h2>
            <button className="btn btn-primary btn-sm flex items-center">
              <Plus size={16} className="mr-1" />
              Nuevo Tratamiento
            </button>
          </div>

          {tratamientos.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No hay tratamientos prescritos</p>
          ) : (
            <div className="space-y-4">
              {tratamientos.map((tratamiento) => (
                <div key={tratamiento.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium capitalize ${
                          tratamiento.tipo_tratamiento === 'farmacologico'
                            ? 'bg-blue-100 text-blue-700'
                            : 'bg-purple-100 text-purple-700'
                        }`}
                      >
                        {tratamiento.tipo_tratamiento}
                      </span>
                    </div>
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${
                        tratamiento.estado === 'activo'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {tratamiento.estado}
                    </span>
                  </div>
                  <p className="font-semibold text-gray-900 mb-2">{tratamiento.descripcion}</p>
                  {tratamiento.objetivo && (
                    <p className="text-sm text-gray-600">Objetivo: {tratamiento.objetivo}</p>
                  )}
                  {tratamiento.duracion_dias && (
                    <p className="text-sm text-gray-500 mt-1">Duración: {tratamiento.duracion_dias} días</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Modales */}
      {currentUser && consulta && (
        <NuevoDiagnosticoModal
          consultaId={consulta.id}
          isOpen={showDiagnosticoModal}
          onClose={() => setShowDiagnosticoModal(false)}
          onSuccess={() => {
            if (id) fetchConsultaData(id)
          }}
        />
      )}
    </div>
  )
}

export default ConsultaDetalle
