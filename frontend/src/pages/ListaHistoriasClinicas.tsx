import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { FileText, Calendar, Eye, Plus, ArrowLeft, Download, Search } from 'lucide-react'
import api from '@/lib/api'

interface HistoriaClinica {
  id: string
  fecha: string
  numero_afiliacion: string
  created_at: string
  updated_at: string
}

const ListaHistoriasClinicas = () => {
  const { pacienteId } = useParams()
  const navigate = useNavigate()
  const [historias, setHistorias] = useState<HistoriaClinica[]>([])
  const [paciente, setPaciente] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    if (pacienteId) {
      cargarDatos()
    }
  }, [pacienteId])

  const cargarDatos = async () => {
    try {
      const [pacienteRes, historiasRes] = await Promise.all([
        api.get(`/pacientes/${pacienteId}`),
        api.get(`/historias-clinicas/paciente/${pacienteId}`)
      ])
      setPaciente(pacienteRes.data)
      setHistorias(historiasRes.data)
    } catch (error) {
      console.error('Error al cargar datos:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatearFecha = (fecha: string) => {
    return new Date(fecha).toLocaleDateString('es-MX', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const historiasFiltradas = historias.filter(h => 
    h.numero_afiliacion?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    formatearFecha(h.fecha).toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto"></div>
            <p className="text-gray-600 mt-4">Cargando historias clínicas...</p>
          </div>
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
            onClick={() => navigate(`/pacientes/${pacienteId}`)}
            className="flex items-center gap-2 text-purple-600 hover:text-purple-700 mb-4 transition-colors"
          >
            <ArrowLeft className="h-5 w-5" />
            <span className="font-medium">Volver al paciente</span>
          </button>
          
          <div className="bg-white rounded-3xl shadow-xl p-8 border border-purple-100">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-4 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl">
                  <FileText className="h-8 w-8 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                    Historias Clínicas
                  </h1>
                  {paciente && (
                    <p className="text-gray-600 mt-1">
                      <span className="font-semibold text-gray-800">{paciente.nombre_completo}</span>
                    </p>
                  )}
                </div>
              </div>
              
              <Link
                to={`/historia-clinica/${pacienteId}`}
                className="px-6 py-3 rounded-2xl font-medium text-white bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 transition-all duration-300 shadow-lg hover:shadow-xl flex items-center gap-2"
              >
                <Plus className="h-5 w-5" />
                Nueva Historia
              </Link>
            </div>
          </div>
        </div>

        {/* Search Bar */}
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
            <input
              type="text"
              placeholder="Buscar por número de afiliación o fecha..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-4 py-4 rounded-2xl border-2 border-gray-200 focus:border-purple-400 focus:ring-4 focus:ring-purple-100 transition-all outline-none"
            />
          </div>
        </div>

        {/* Lista de Historias */}
        {historiasFiltradas.length === 0 ? (
          <div className="bg-white rounded-3xl shadow-xl p-12 border border-purple-100 text-center">
            <div className="p-6 bg-purple-50 rounded-2xl inline-block mb-4">
              <FileText className="h-16 w-16 text-purple-400" />
            </div>
            <h3 className="text-2xl font-bold text-gray-800 mb-2">
              {searchTerm ? 'No se encontraron resultados' : 'No hay historias clínicas'}
            </h3>
            <p className="text-gray-600 mb-6">
              {searchTerm 
                ? 'Intenta con otros términos de búsqueda'
                : 'Este paciente aún no tiene historias clínicas registradas'
              }
            </p>
            {!searchTerm && (
              <Link
                to={`/historia-clinica/${pacienteId}`}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-2xl font-medium text-white bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 transition-all duration-300 shadow-lg"
              >
                <Plus className="h-5 w-5" />
                Crear Primera Historia
              </Link>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {historiasFiltradas.map((historia) => (
              <div
                key={historia.id}
                className="bg-white rounded-2xl shadow-lg border-2 border-gray-100 hover:border-purple-300 transition-all duration-300 overflow-hidden group hover:shadow-xl"
              >
                <div className="bg-gradient-to-br from-purple-100 to-pink-100 p-6">
                  <div className="flex items-center justify-between mb-2">
                    <Calendar className="h-6 w-6 text-purple-600" />
                    <span className="text-xs font-medium text-purple-600 bg-white px-3 py-1 rounded-full">
                      Historia #{historia.numero_afiliacion || 'S/N'}
                    </span>
                  </div>
                  <h3 className="text-xl font-bold text-gray-800">
                    {formatearFecha(historia.fecha)}
                  </h3>
                </div>
                
                <div className="p-6">
                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Creada:</span>
                      <span className="font-medium text-gray-800">
                        {new Date(historia.created_at).toLocaleDateString('es-MX')}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Actualizada:</span>
                      <span className="font-medium text-gray-800">
                        {new Date(historia.updated_at).toLocaleDateString('es-MX')}
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    <Link
                      to={`/historia-clinica/ver/${historia.id}`}
                      className="flex-1 px-4 py-2 rounded-xl font-medium text-purple-600 bg-purple-50 hover:bg-purple-100 transition-colors flex items-center justify-center gap-2"
                    >
                      <Eye className="h-4 w-4" />
                      Ver
                    </Link>
                    <button
                      onClick={() => {/* Implementar descarga PDF */}}
                      className="px-4 py-2 rounded-xl font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 transition-colors"
                      title="Descargar PDF"
                    >
                      <Download className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default ListaHistoriasClinicas
