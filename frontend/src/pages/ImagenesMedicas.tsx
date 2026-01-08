import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, Image, Calendar, User, FileImage, Eye } from 'lucide-react'

interface ImagenMedica {
  id: string
  paciente_id: string
  paciente_nombre: string
  tipo_estudio: string
  descripcion: string
  fecha_estudio: string
  url_imagen: string
  created_at: string
}

export default function ImagenesMedicas() {
  const [imagenes] = useState<ImagenMedica[]>([])
  const [loading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [tipoFiltro, setTipoFiltro] = useState('')

  const imagenesFiltradas = imagenes.filter(img => {
    const matchSearch = img.paciente_nombre?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                       img.tipo_estudio?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                       img.descripcion?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchTipo = !tipoFiltro || img.tipo_estudio === tipoFiltro
    return matchSearch && matchTipo
  })

  const tiposEstudio = [...new Set(imagenes.map(img => img.tipo_estudio).filter(Boolean))]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-12 px-6 mb-8 rounded-3xl shadow-xl mx-6 mt-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 bg-white/20 rounded-2xl backdrop-blur-sm">
              <FileImage className="h-8 w-8" />
            </div>
            <div>
              <h1 className="text-4xl font-bold">Imágenes Médicas</h1>
              <p className="text-blue-100 mt-2">Gestión y visualización de estudios de imagen</p>
            </div>
          </div>

          {/* Métricas */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-100 text-sm">Total Imágenes</p>
                  <p className="text-3xl font-bold mt-1">{imagenes.length}</p>
                </div>
                <Image className="h-8 w-8 text-blue-200" />
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-100 text-sm">Tipos de Estudio</p>
                  <p className="text-3xl font-bold mt-1">{tiposEstudio.length}</p>
                </div>
                <FileImage className="h-8 w-8 text-blue-200" />
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-100 text-sm">Este Mes</p>
                  <p className="text-3xl font-bold mt-1">
                    {imagenes.filter(img => {
                      const fecha = new Date(img.created_at)
                      const ahora = new Date()
                      return fecha.getMonth() === ahora.getMonth() && fecha.getFullYear() === ahora.getFullYear()
                    }).length}
                  </p>
                </div>
                <Calendar className="h-8 w-8 text-blue-200" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filtros */}
      <div className="max-w-7xl mx-auto px-6 mb-6">
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
              <input
                type="text"
                placeholder="Buscar por paciente, tipo de estudio o descripción..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <select
              value={tipoFiltro}
              onChange={(e) => setTipoFiltro(e.target.value)}
              className="px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Todos los tipos de estudio</option>
              {tiposEstudio.map(tipo => (
                <option key={tipo} value={tipo}>{tipo}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Lista de Imágenes */}
      <div className="max-w-7xl mx-auto px-6 pb-8">
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Cargando imágenes...</p>
          </div>
        ) : imagenesFiltradas.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
            <FileImage className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No hay imágenes</h3>
            <p className="text-gray-600">
              {searchTerm || tipoFiltro ? 'No se encontraron imágenes con los filtros aplicados' : 'Aún no hay imágenes médicas registradas'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {imagenesFiltradas.map((imagen) => (
              <div
                key={imagen.id}
                className="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
              >
                {/* Imagen Preview */}
                <div className="relative h-48 bg-gradient-to-br from-gray-100 to-gray-200">
                  {imagen.url_imagen ? (
                    <img
                      src={imagen.url_imagen}
                      alt={imagen.descripcion}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full">
                      <FileImage className="h-16 w-16 text-gray-400" />
                    </div>
                  )}
                </div>

                {/* Contenido */}
                <div className="p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <User className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-medium text-gray-900">{imagen.paciente_nombre}</span>
                  </div>

                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{imagen.tipo_estudio}</h3>
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">{imagen.descripcion}</p>

                  <div className="flex items-center gap-2 text-sm text-gray-500 mb-4">
                    <Calendar className="h-4 w-4" />
                    <span>{new Date(imagen.fecha_estudio).toLocaleDateString('es-ES')}</span>
                  </div>

                  <Link
                    to={`/imagenes/${imagen.paciente_id}`}
                    className="flex items-center justify-center gap-2 w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-2.5 rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 font-medium"
                  >
                    <Eye className="h-4 w-4" />
                    Ver Galería del Paciente
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
