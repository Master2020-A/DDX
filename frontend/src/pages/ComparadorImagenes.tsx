import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { 
  ArrowLeft, ZoomIn, ZoomOut, RotateCw, Maximize2, Link as LinkIcon,
  Sparkles, Calendar, Activity, ArrowLeftRight, Eye, EyeOff
} from 'lucide-react'
import api from '@/lib/api'

interface ImagenMedica {
  id: string
  titulo: string
  descripcion?: string
  tipo_imagen: string
  region_anatomica?: string
  analisis_ia_completado: boolean
  hallazgos?: string[]
  confianza_ia?: number
  created_at: string
  url_archivo?: string
}

const ComparadorImagenes = () => {
  const { imagen1Id, imagen2Id } = useParams<{ imagen1Id: string; imagen2Id: string }>()
  const navigate = useNavigate()

  const [imagen1, setImagen1] = useState<ImagenMedica | null>(null)
  const [imagen2, setImagen2] = useState<ImagenMedica | null>(null)
  const [url1, setUrl1] = useState('')
  const [url2, setUrl2] = useState('')
  const [loading, setLoading] = useState(true)

  // Controles de visualización
  const [zoom, setZoom] = useState(1)
  const [rotacion1, setRotacion1] = useState(0)
  const [rotacion2, setRotacion2] = useState(0)
  const [sincronizado, setSincronizado] = useState(true)
  const [mostrarInfoIA, setMostrarInfoIA] = useState(true)
  const [vistaVertical, setVistaVertical] = useState(false)

  useEffect(() => {
    if (imagen1Id && imagen2Id) {
      cargarImagenes()
    }
  }, [imagen1Id, imagen2Id])

  const cargarImagenes = async () => {
    try {
      setLoading(true)
      
      // Cargar metadatos de ambas imágenes
      const [res1, res2] = await Promise.all([
        api.get(`/imagenes/${imagen1Id}`),
        api.get(`/imagenes/${imagen2Id}`)
      ])
      
      setImagen1(res1.data)
      setImagen2(res2.data)
      
      // URLs de imágenes - usar url_archivo si está disponible
      const url1 = res1.data.url_archivo 
        ? `http://localhost:8612${res1.data.url_archivo}`
        : `${api.defaults.baseURL}/imagenes/${imagen1Id}/download`
      const url2 = res2.data.url_archivo 
        ? `http://localhost:8612${res2.data.url_archivo}`
        : `${api.defaults.baseURL}/imagenes/${imagen2Id}/download`
      
      setUrl1(url1)
      setUrl2(url2)
      
    } catch (error) {
      console.error('Error cargando imágenes:', error)
      alert('Error al cargar las imágenes')
    } finally {
      setLoading(false)
    }
  }

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 0.25, 5))
  }

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 0.25, 0.25))
  }

  const handleRotar1 = () => {
    if (sincronizado) {
      setRotacion1(prev => (prev + 90) % 360)
      setRotacion2(prev => (prev + 90) % 360)
    } else {
      setRotacion1(prev => (prev + 90) % 360)
    }
  }

  const handleRotar2 = () => {
    if (sincronizado) {
      setRotacion1(prev => (prev + 90) % 360)
      setRotacion2(prev => (prev + 90) % 360)
    } else {
      setRotacion2(prev => (prev + 90) % 360)
    }
  }

  const handleResetear = () => {
    setZoom(1)
    setRotacion1(0)
    setRotacion2(0)
  }

  const handleIntercambiar = () => {
    // Intercambiar imágenes
    const tempImagen = imagen1
    const tempUrl = url1
    const tempRotacion = rotacion1
    
    setImagen1(imagen2)
    setUrl1(url2)
    setRotacion1(rotacion2)
    
    setImagen2(tempImagen)
    setUrl2(tempUrl)
    setRotacion2(tempRotacion)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-white">Cargando imágenes...</p>
        </div>
      </div>
    )
  }

  if (!imagen1 || !imagen2) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-center text-white">
          <p>No se pudieron cargar las imágenes</p>
          <button onClick={() => navigate(-1)} className="btn-primary mt-4">
            Volver
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800 text-white px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate(-1)}
              className="flex items-center gap-2 hover:text-primary-400 transition-colors"
            >
              <ArrowLeft size={20} />
              Volver
            </button>
            <h1 className="font-medium text-lg">Comparación de Imágenes</h1>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setSincronizado(!sincronizado)}
              className={`px-3 py-2 rounded-lg flex items-center gap-2 ${
                sincronizado ? 'bg-primary-600' : 'bg-gray-700'
              }`}
              title={sincronizado ? 'Controles sincronizados' : 'Controles independientes'}
            >
              <LinkIcon size={18} />
              {sincronizado ? 'Sincronizado' : 'Independiente'}
            </button>

            <button
              onClick={() => setVistaVertical(!vistaVertical)}
              className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg"
              title="Cambiar orientación"
            >
              <ArrowLeftRight size={18} className={vistaVertical ? 'rotate-90' : ''} />
            </button>

            <button
              onClick={() => setMostrarInfoIA(!mostrarInfoIA)}
              className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg flex items-center gap-2"
            >
              {mostrarInfoIA ? <EyeOff size={18} /> : <Eye size={18} />}
              Info IA
            </button>

            <button
              onClick={handleIntercambiar}
              className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg"
              title="Intercambiar imágenes"
            >
              <ArrowLeftRight size={18} />
            </button>
          </div>
        </div>

        {/* Controles de zoom y rotación */}
        <div className="flex items-center gap-4 mt-3 pt-3 border-t border-gray-700">
          <div className="flex items-center gap-2 bg-gray-700 rounded-lg px-3 py-2">
            <button onClick={handleZoomOut} className="p-1 hover:bg-gray-600 rounded">
              <ZoomOut size={18} />
            </button>
            <span className="text-sm w-16 text-center">{Math.round(zoom * 100)}%</span>
            <button onClick={handleZoomIn} className="p-1 hover:bg-gray-600 rounded">
              <ZoomIn size={18} />
            </button>
          </div>

          <button
            onClick={handleResetear}
            className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg flex items-center gap-2"
          >
            <Maximize2 size={18} />
            Resetear
          </button>

          <div className="flex-1" />

          <div className="text-sm text-gray-400">
            Usa la rueda del mouse para hacer zoom
          </div>
        </div>
      </div>

      {/* Contenedor de imágenes */}
      <div className={`flex-1 flex ${vistaVertical ? 'flex-col' : 'flex-row'} overflow-hidden`}>
        {/* Imagen 1 */}
        <div className="flex-1 relative bg-gray-900 border-r border-gray-800">
          <div className="absolute inset-0 flex flex-col">
            {/* Header de imagen 1 */}
            <div className="bg-gray-800 bg-opacity-90 px-4 py-2 flex items-center justify-between">
              <div className="flex-1 min-w-0">
                <h3 className="text-white font-medium truncate">{imagen1.titulo}</h3>
                <p className="text-gray-400 text-sm">
                  {imagen1.tipo_imagen} • {new Date(imagen1.created_at).toLocaleDateString()}
                </p>
              </div>
              {!sincronizado && (
                <button
                  onClick={handleRotar1}
                  className="ml-2 p-2 bg-gray-700 hover:bg-gray-600 rounded-lg"
                >
                  <RotateCw size={18} className="text-white" />
                </button>
              )}
            </div>

            {/* Visor de imagen 1 */}
            <div className="flex-1 flex items-center justify-center overflow-hidden p-4">
              <div
                style={{
                  transform: `scale(${zoom}) rotate(${rotacion1}deg)`,
                  transition: 'transform 0.2s',
                }}
              >
                <img
                  src={url1}
                  alt={imagen1.titulo}
                  className="max-w-full max-h-full object-contain"
                  draggable={false}
                />
              </div>
            </div>

            {/* Info IA de imagen 1 */}
            {mostrarInfoIA && imagen1.analisis_ia_completado && (
              <div className="bg-gray-800 bg-opacity-95 px-4 py-3 max-h-48 overflow-y-auto">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles size={16} className="text-purple-400" />
                  <span className="text-white text-sm font-medium">Análisis IA</span>
                  {imagen1.confianza_ia && (
                    <span className="ml-auto text-purple-400 text-sm">
                      {(imagen1.confianza_ia * 100).toFixed(1)}%
                    </span>
                  )}
                </div>
                {imagen1.hallazgos && imagen1.hallazgos.length > 0 && (
                  <ul className="space-y-1">
                    {imagen1.hallazgos.map((hallazgo, i) => (
                      <li key={i} className="text-gray-300 text-xs flex items-start gap-2">
                        <span className="text-purple-400">•</span>
                        <span>{hallazgo}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Imagen 2 */}
        <div className="flex-1 relative bg-gray-900">
          <div className="absolute inset-0 flex flex-col">
            {/* Header de imagen 2 */}
            <div className="bg-gray-800 bg-opacity-90 px-4 py-2 flex items-center justify-between">
              <div className="flex-1 min-w-0">
                <h3 className="text-white font-medium truncate">{imagen2.titulo}</h3>
                <p className="text-gray-400 text-sm">
                  {imagen2.tipo_imagen} • {new Date(imagen2.created_at).toLocaleDateString()}
                </p>
              </div>
              {!sincronizado && (
                <button
                  onClick={handleRotar2}
                  className="ml-2 p-2 bg-gray-700 hover:bg-gray-600 rounded-lg"
                >
                  <RotateCw size={18} className="text-white" />
                </button>
              )}
            </div>

            {/* Visor de imagen 2 */}
            <div className="flex-1 flex items-center justify-center overflow-hidden p-4">
              <div
                style={{
                  transform: `scale(${zoom}) rotate(${rotacion2}deg)`,
                  transition: 'transform 0.2s',
                }}
              >
                <img
                  src={url2}
                  alt={imagen2.titulo}
                  className="max-w-full max-h-full object-contain"
                  draggable={false}
                />
              </div>
            </div>

            {/* Info IA de imagen 2 */}
            {mostrarInfoIA && imagen2.analisis_ia_completado && (
              <div className="bg-gray-800 bg-opacity-95 px-4 py-3 max-h-48 overflow-y-auto">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles size={16} className="text-purple-400" />
                  <span className="text-white text-sm font-medium">Análisis IA</span>
                  {imagen2.confianza_ia && (
                    <span className="ml-auto text-purple-400 text-sm">
                      {(imagen2.confianza_ia * 100).toFixed(1)}%
                    </span>
                  )}
                </div>
                {imagen2.hallazgos && imagen2.hallazgos.length > 0 && (
                  <ul className="space-y-1">
                    {imagen2.hallazgos.map((hallazgo, i) => (
                      <li key={i} className="text-gray-300 text-xs flex items-start gap-2">
                        <span className="text-purple-400">•</span>
                        <span>{hallazgo}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Panel de comparación */}
      {mostrarInfoIA && imagen1.analisis_ia_completado && imagen2.analisis_ia_completado && (
        <div className="bg-gray-800 border-t border-gray-700 px-4 py-3">
          <div className="flex items-center justify-between">
            <h3 className="text-white font-medium flex items-center gap-2">
              <Activity size={18} />
              Comparación de Resultados
            </h3>
            
            <div className="flex gap-4">
              <div className="text-sm">
                <span className="text-gray-400">Imagen 1: </span>
                <span className="text-purple-400 font-medium">
                  {imagen1.confianza_ia ? `${(imagen1.confianza_ia * 100).toFixed(1)}%` : 'N/A'}
                </span>
              </div>
              <div className="text-sm">
                <span className="text-gray-400">Imagen 2: </span>
                <span className="text-purple-400 font-medium">
                  {imagen2.confianza_ia ? `${(imagen2.confianza_ia * 100).toFixed(1)}%` : 'N/A'}
                </span>
              </div>
              <div className="text-sm">
                <span className="text-gray-400">Diferencia: </span>
                <span className="text-white font-medium">
                  {imagen1.confianza_ia && imagen2.confianza_ia
                    ? `${Math.abs((imagen1.confianza_ia - imagen2.confianza_ia) * 100).toFixed(1)}%`
                    : 'N/A'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ComparadorImagenes
