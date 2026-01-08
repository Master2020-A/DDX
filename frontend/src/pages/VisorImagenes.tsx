import React, { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { 
  ArrowLeft, ZoomIn, ZoomOut, RotateCw, Move, Maximize2, 
  Download, Edit3, Trash2, Sparkles, FileText, Copy,
  Circle, Square, ArrowRight, Type, Minus, Plus, Save
} from 'lucide-react'
import api from '@/lib/api'
import DashboardNIfTI from '@/components/DashboardNIfTI'

interface ImagenMedica {
  id: string
  paciente_id: string
  titulo: string
  descripcion?: string
  tipo_imagen: string
  region_anatomica?: string
  lateralidad?: string
  tipo_archivo: string
  tamanio_bytes: number
  ancho?: number
  alto?: number
  analisis_ia_completado: boolean
  hallazgos?: string[]
  confianza_ia?: number
  anotaciones?: Anotacion[]
  created_at: string
  url_archivo?: string
  url_preview?: string
  nombre_archivo?: string
  resultados_ia?: {
    nifti_previews?: {
      axial?: string
      sagital?: string
      coronal?: string
    }
    nifti_metadatos?: any
    [key: string]: any
  }
}

interface Anotacion {
  tipo: 'rectangulo' | 'circulo' | 'flecha' | 'texto' | 'linea'
  coordenadas: any
  color?: string
  texto?: string
  grosor?: number
  autor?: string
  fecha?: string
}

// Función helper para obtener URL de visualización de imagen
const obtenerUrlVisualizacion = (imagen: ImagenMedica): string | null => {
  // Si tiene previews NIfTI, usar el preview axial
  if (imagen.resultados_ia?.nifti_previews?.axial) {
    return imagen.resultados_ia.nifti_previews.axial;
  }
  
  // Usar URL normal para otros archivos
  return imagen.url_archivo || null;
};

const VisorImagenes = () => {
  const { imagenId } = useParams<{ imagenId: string }>()
  const navigate = useNavigate()
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  const [imagen, setImagen] = useState<ImagenMedica | null>(null)
  const [imagenUrl, setImagenUrl] = useState<string>('')
  const [loading, setLoading] = useState(true)
  
  // Estado del visor
  const [zoom, setZoom] = useState(1)
  const [rotacion, setRotacion] = useState(0)
  const [posicion, setPosicion] = useState({ x: 0, y: 0 })
  const [arrastrando, setArrastrando] = useState(false)
  const [ultimaPosicion, setUltimaPosicion] = useState({ x: 0, y: 0 })
  
  // Estado de anotaciones
  const [modoAnotacion, setModoAnotacion] = useState<'ver' | 'rectangulo' | 'circulo' | 'flecha' | 'texto' | 'linea'>('ver')
  const [anotaciones, setAnotaciones] = useState<Anotacion[]>([])
  const [anotacionActual, setAnotacionActual] = useState<any>(null)
  const [colorAnotacion, setColorAnotacion] = useState('#FF0000')
  const [grosorAnotacion, setGrosorAnotacion] = useState(2)
  
  // Panel de resultados IA
  const [mostrarResultadosIA, setMostrarResultadosIA] = useState(true)

  useEffect(() => {
    if (imagenId) {
      cargarImagen()
    }
  }, [imagenId])

  // Dibujar anotaciones en el canvas
  useEffect(() => {
    const canvas = canvasRef.current
    const container = containerRef.current
    if (!canvas || !container) return

    // Ajustar tamaño del canvas al contenedor
    const rect = container.getBoundingClientRect()
    canvas.width = rect.width
    canvas.height = rect.height

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Limpiar canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Aplicar transformaciones
    ctx.save()
    ctx.translate(canvas.width / 2 + posicion.x, canvas.height / 2 + posicion.y)
    ctx.scale(zoom, zoom)
    ctx.rotate((rotacion * Math.PI) / 180)

    // Dibujar anotaciones guardadas
    anotaciones.forEach(anotacion => {
      ctx.strokeStyle = anotacion.color || colorAnotacion
      ctx.lineWidth = anotacion.grosor || grosorAnotacion
      ctx.fillStyle = anotacion.color || colorAnotacion

      const { inicio, fin } = anotacion.coordenadas

      switch (anotacion.tipo) {
        case 'rectangulo':
          ctx.strokeRect(
            inicio.x - canvas.width / 2,
            inicio.y - canvas.height / 2,
            fin.x - inicio.x,
            fin.y - inicio.y
          )
          break
        case 'circulo':
          const radio = Math.sqrt(
            Math.pow(fin.x - inicio.x, 2) + Math.pow(fin.y - inicio.y, 2)
          )
          ctx.beginPath()
          ctx.arc(
            inicio.x - canvas.width / 2,
            inicio.y - canvas.height / 2,
            radio,
            0,
            2 * Math.PI
          )
          ctx.stroke()
          break
        case 'linea':
          ctx.beginPath()
          ctx.moveTo(inicio.x - canvas.width / 2, inicio.y - canvas.height / 2)
          ctx.lineTo(fin.x - canvas.width / 2, fin.y - canvas.height / 2)
          ctx.stroke()
          break
        case 'flecha':
          // Dibujar línea
          ctx.beginPath()
          ctx.moveTo(inicio.x - canvas.width / 2, inicio.y - canvas.height / 2)
          ctx.lineTo(fin.x - canvas.width / 2, fin.y - canvas.height / 2)
          ctx.stroke()
          
          // Dibujar punta de flecha
          const angle = Math.atan2(fin.y - inicio.y, fin.x - inicio.x)
          const headlen = 15
          ctx.beginPath()
          ctx.moveTo(fin.x - canvas.width / 2, fin.y - canvas.height / 2)
          ctx.lineTo(
            fin.x - canvas.width / 2 - headlen * Math.cos(angle - Math.PI / 6),
            fin.y - canvas.height / 2 - headlen * Math.sin(angle - Math.PI / 6)
          )
          ctx.moveTo(fin.x - canvas.width / 2, fin.y - canvas.height / 2)
          ctx.lineTo(
            fin.x - canvas.width / 2 - headlen * Math.cos(angle + Math.PI / 6),
            fin.y - canvas.height / 2 - headlen * Math.sin(angle + Math.PI / 6)
          )
          ctx.stroke()
          break
        case 'texto':
          ctx.font = '16px Arial'
          ctx.fillText(
            anotacion.texto || '',
            inicio.x - canvas.width / 2,
            inicio.y - canvas.height / 2
          )
          break
      }
    })

    // Dibujar anotación actual (mientras se dibuja)
    if (anotacionActual && modoAnotacion !== 'ver') {
      ctx.strokeStyle = colorAnotacion
      ctx.lineWidth = grosorAnotacion
      ctx.fillStyle = colorAnotacion

      const { inicio, fin } = anotacionActual

      switch (modoAnotacion) {
        case 'rectangulo':
          ctx.strokeRect(
            inicio.x - canvas.width / 2,
            inicio.y - canvas.height / 2,
            fin.x - inicio.x,
            fin.y - inicio.y
          )
          break
        case 'circulo':
          const radio = Math.sqrt(
            Math.pow(fin.x - inicio.x, 2) + Math.pow(fin.y - inicio.y, 2)
          )
          ctx.beginPath()
          ctx.arc(
            inicio.x - canvas.width / 2,
            inicio.y - canvas.height / 2,
            radio,
            0,
            2 * Math.PI
          )
          ctx.stroke()
          break
        case 'linea':
          ctx.beginPath()
          ctx.moveTo(inicio.x - canvas.width / 2, inicio.y - canvas.height / 2)
          ctx.lineTo(fin.x - canvas.width / 2, fin.y - canvas.height / 2)
          ctx.stroke()
          break
        case 'flecha':
          ctx.beginPath()
          ctx.moveTo(inicio.x - canvas.width / 2, inicio.y - canvas.height / 2)
          ctx.lineTo(fin.x - canvas.width / 2, fin.y - canvas.height / 2)
          ctx.stroke()
          break
      }
    }

    ctx.restore()
  }, [anotaciones, anotacionActual, zoom, rotacion, posicion, modoAnotacion, colorAnotacion, grosorAnotacion])

  const cargarImagen = async () => {
    try {
      setLoading(true)
      
      // Cargar metadatos
      const res = await api.get(`/imagenes/${imagenId}`)
      setImagen(res.data)
      
      if (res.data.anotaciones) {
        setAnotaciones(res.data.anotaciones)
      }
      
      // Cargar imagen usando la URL directa si está disponible
      const urlVisualizacion = obtenerUrlVisualizacion(res.data);
      const urlImagen = urlVisualizacion
        ? `http://localhost:8612${urlVisualizacion}`
        : `${api.defaults.baseURL}/imagenes/${imagenId}/download`
      setImagenUrl(urlImagen)
      
    } catch (error) {
      console.error('Error cargando imagen:', error)
      alert('Error al cargar la imagen')
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

  const handleRotar = () => {
    setRotacion(prev => (prev + 90) % 360)
  }

  const handleResetear = () => {
    setZoom(1)
    setRotacion(0)
    setPosicion({ x: 0, y: 0 })
  }

  const handleMouseDown = (e: React.MouseEvent) => {
    if (modoAnotacion === 'ver') {
      setArrastrando(true)
      setUltimaPosicion({ x: e.clientX, y: e.clientY })
    } else {
      // Iniciar anotación
      const rect = canvasRef.current?.getBoundingClientRect()
      if (rect) {
        const x = e.clientX - rect.left
        const y = e.clientY - rect.top
        setAnotacionActual({ inicio: { x, y }, fin: { x, y } })
      }
    }
  }

  const handleMouseMove = (e: React.MouseEvent) => {
    if (arrastrando && modoAnotacion === 'ver') {
      const deltaX = e.clientX - ultimaPosicion.x
      const deltaY = e.clientY - ultimaPosicion.y
      setPosicion(prev => ({ x: prev.x + deltaX, y: prev.y + deltaY }))
      setUltimaPosicion({ x: e.clientX, y: e.clientY })
    } else if (anotacionActual && modoAnotacion !== 'ver') {
      const rect = canvasRef.current?.getBoundingClientRect()
      if (rect) {
        const x = e.clientX - rect.left
        const y = e.clientY - rect.top
        setAnotacionActual({ ...anotacionActual, fin: { x, y } })
      }
    }
  }

  const handleMouseUp = () => {
    if (arrastrando) {
      setArrastrando(false)
    } else if (anotacionActual && modoAnotacion !== 'ver') {
      // Si es texto, pedir el texto al usuario
      if (modoAnotacion === 'texto') {
        const texto = prompt('Ingrese el texto de la anotación:')
        if (!texto) {
          setAnotacionActual(null)
          return
        }
        
        const nuevaAnotacion: Anotacion = {
          tipo: 'texto',
          coordenadas: anotacionActual,
          color: colorAnotacion,
          grosor: grosorAnotacion,
          texto: texto,
          fecha: new Date().toISOString()
        }
        setAnotaciones([...anotaciones, nuevaAnotacion])
        setAnotacionActual(null)
      } else {
        // Guardar anotación normal
        const nuevaAnotacion: Anotacion = {
          tipo: modoAnotacion as any,
          coordenadas: anotacionActual,
          color: colorAnotacion,
          grosor: grosorAnotacion,
          fecha: new Date().toISOString()
        }
        setAnotaciones([...anotaciones, nuevaAnotacion])
        setAnotacionActual(null)
      }
    }
  }

  const handleGuardarAnotaciones = async () => {
    try {
      await api.put(`/imagenes/${imagenId}`, { anotaciones })
      alert('Anotaciones guardadas')
    } catch (error) {
      console.error('Error guardando anotaciones:', error)
      alert('Error al guardar anotaciones')
    }
  }

  const handleAnalisisIA = async () => {
    try {
      const res = await api.post(`/imagenes/${imagenId}/analizar-ia`)
      setImagen(res.data)
      alert('Análisis completado')
    } catch (error) {
      console.error('Error en análisis:', error)
      alert('Error al analizar imagen')
    }
  }

  const handleDescargar = async () => {
    window.open(`${api.defaults.baseURL}/imagenes/${imagenId}/download`, '_blank')
  }

  const handleEliminar = async () => {
    if (!confirm('¿Eliminar esta imagen?')) return
    try {
      await api.delete(`/imagenes/${imagenId}`)
      alert('Imagen eliminada')
      navigate(-1)
    } catch (error) {
      console.error('Error eliminando:', error)
      alert('Error al eliminar')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando imagen...</p>
        </div>
      </div>
    )
  }

  if (!imagen) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-gray-600">Imagen no encontrada</p>
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
      <div className="bg-gray-800 text-white px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 hover:text-primary-400 transition-colors"
          >
            <ArrowLeft size={20} />
            Volver
          </button>
          <div>
            <h1 className="font-medium">{imagen.titulo}</h1>
            <p className="text-sm text-gray-400">
              {imagen.tipo_imagen} {imagen.region_anatomica && `• ${imagen.region_anatomica}`}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {!imagen.analisis_ia_completado && (
            <button
              onClick={handleAnalisisIA}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg flex items-center gap-2"
            >
              <Sparkles size={18} />
              Analizar con IA
            </button>
          )}
          <button
            onClick={handleDescargar}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg"
          >
            <Download size={18} />
          </button>
          <button
            onClick={handleEliminar}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg"
          >
            <Trash2 size={18} />
          </button>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Panel lateral izquierdo - Herramientas */}
        <div className="w-16 bg-gray-800 flex flex-col items-center py-4 gap-3">
          <button
            onClick={() => setModoAnotacion('ver')}
            className={`p-3 rounded-lg ${modoAnotacion === 'ver' ? 'bg-primary-600' : 'bg-gray-700 hover:bg-gray-600'}`}
            title="Mover"
          >
            <Move size={20} className="text-white" />
          </button>
          
          <div className="w-10 h-px bg-gray-700" />
          
          <button
            onClick={() => setModoAnotacion('rectangulo')}
            className={`p-3 rounded-lg ${modoAnotacion === 'rectangulo' ? 'bg-primary-600' : 'bg-gray-700 hover:bg-gray-600'}`}
            title="Rectángulo"
          >
            <Square size={20} className="text-white" />
          </button>
          
          <button
            onClick={() => setModoAnotacion('circulo')}
            className={`p-3 rounded-lg ${modoAnotacion === 'circulo' ? 'bg-primary-600' : 'bg-gray-700 hover:bg-gray-600'}`}
            title="Círculo"
          >
            <Circle size={20} className="text-white" />
          </button>
          
          <button
            onClick={() => setModoAnotacion('flecha')}
            className={`p-3 rounded-lg ${modoAnotacion === 'flecha' ? 'bg-primary-600' : 'bg-gray-700 hover:bg-gray-600'}`}
            title="Flecha"
          >
            <ArrowRight size={20} className="text-white" />
          </button>
          
          <button
            onClick={() => setModoAnotacion('texto')}
            className={`p-3 rounded-lg ${modoAnotacion === 'texto' ? 'bg-primary-600' : 'bg-gray-700 hover:bg-gray-600'}`}
            title="Texto"
          >
            <Type size={20} className="text-white" />
          </button>
          
          {anotaciones.length > 0 && (
            <>
              <div className="w-10 h-px bg-gray-700" />
              <button
                onClick={handleGuardarAnotaciones}
                className="p-3 rounded-lg bg-green-600 hover:bg-green-700"
                title="Guardar anotaciones"
              >
                <Save size={20} className="text-white" />
              </button>
            </>
          )}
        </div>

        {/* Visor central */}
        <div className="flex-1 relative bg-gray-900" ref={containerRef}>
          <div
            className="absolute inset-0 flex items-center justify-center overflow-hidden cursor-move"
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
          >
            <div
              style={{
                transform: `translate(${posicion.x}px, ${posicion.y}px) scale(${zoom}) rotate(${rotacion}deg)`,
                transition: arrastrando ? 'none' : 'transform 0.1s',
              }}
            >
              {imagenUrl && (
                <img
                  src={imagenUrl}
                  alt={imagen.titulo}
                  className="max-w-none"
                  draggable={false}
                />
              )}
              
              {/* Canvas para anotaciones */}
              <canvas
                ref={canvasRef}
                className="absolute top-0 left-0 w-full h-full"
                style={{ pointerEvents: modoAnotacion === 'ver' ? 'none' : 'auto' }}
              />
            </div>
          </div>

          {/* Controles de zoom flotantes */}
          <div className="absolute bottom-4 left-4 bg-gray-800 rounded-lg p-2 flex items-center gap-2">
            <button
              onClick={handleZoomOut}
              className="p-2 hover:bg-gray-700 rounded"
            >
              <ZoomOut size={20} className="text-white" />
            </button>
            
            <span className="text-white text-sm w-16 text-center">
              {Math.round(zoom * 100)}%
            </span>
            
            <button
              onClick={handleZoomIn}
              className="p-2 hover:bg-gray-700 rounded"
            >
              <ZoomIn size={20} className="text-white" />
            </button>
            
            <div className="w-px h-6 bg-gray-700 mx-1" />
            
            <button
              onClick={handleRotar}
              className="p-2 hover:bg-gray-700 rounded"
            >
              <RotateCw size={20} className="text-white" />
            </button>
            
            <button
              onClick={handleResetear}
              className="p-2 hover:bg-gray-700 rounded"
            >
              <Maximize2 size={20} className="text-white" />
            </button>
          </div>

          {/* Herramientas de anotación */}
          {modoAnotacion !== 'ver' && (
            <div className="absolute top-4 left-4 bg-gray-800 rounded-lg p-3 flex items-center gap-3">
              <div className="flex items-center gap-2">
                <label className="text-white text-sm">Color:</label>
                <input
                  type="color"
                  value={colorAnotacion}
                  onChange={(e) => setColorAnotacion(e.target.value)}
                  className="w-8 h-8 rounded cursor-pointer"
                />
              </div>
              
              <div className="w-px h-6 bg-gray-700" />
              
              <div className="flex items-center gap-2">
                <label className="text-white text-sm">Grosor:</label>
                <button
                  onClick={() => setGrosorAnotacion(Math.max(1, grosorAnotacion - 1))}
                  className="p-1 hover:bg-gray-700 rounded"
                >
                  <Minus size={16} className="text-white" />
                </button>
                <span className="text-white text-sm w-8 text-center">{grosorAnotacion}</span>
                <button
                  onClick={() => setGrosorAnotacion(Math.min(10, grosorAnotacion + 1))}
                  className="p-1 hover:bg-gray-700 rounded"
                >
                  <Plus size={16} className="text-white" />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Panel lateral derecho - Información */}
        {mostrarResultadosIA && imagen.analisis_ia_completado && (
          <div className="w-80 bg-gray-800 text-white p-4 overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold flex items-center gap-2">
                <Sparkles size={20} className="text-purple-400" />
                Análisis IA
              </h3>
              <button
                onClick={() => setMostrarResultadosIA(false)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            {imagen.resultados_ia && (
              <div className="space-y-4">
                <div className="bg-gray-700 rounded-lg p-3">
                  <p className="text-sm text-gray-400 mb-1">Modelo</p>
                  <p className="font-medium">{imagen.resultados_ia.modelo}</p>
                </div>

                <div className="bg-gray-700 rounded-lg p-3">
                  <p className="text-sm text-gray-400 mb-1">Confianza Global</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-600 rounded-full h-2">
                      <div
                        className="bg-purple-500 h-2 rounded-full"
                        style={{ width: `${(imagen.confianza_ia || 0) * 100}%` }}
                      />
                    </div>
                    <span className="font-medium">{((imagen.confianza_ia || 0) * 100).toFixed(1)}%</span>
                  </div>
                </div>

                {imagen.hallazgos && imagen.hallazgos.length > 0 && (
                  <div className="bg-gray-700 rounded-lg p-3">
                    <p className="text-sm text-gray-400 mb-2">Hallazgos Detectados</p>
                    <ul className="space-y-1">
                      {imagen.hallazgos.map((hallazgo, index) => (
                        <li key={index} className="text-sm flex items-start gap-2">
                          <span className="text-purple-400">•</span>
                          <span>{hallazgo}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {imagen.resultados_ia.predicciones && (
                  <div className="bg-gray-700 rounded-lg p-3">
                    <p className="text-sm text-gray-400 mb-2">Predicciones Detalladas</p>
                    <div className="space-y-2">
                      {Object.entries(imagen.resultados_ia.predicciones as Record<string, number>)
                        .sort(([, a], [, b]) => b - a)
                        .slice(0, 10)
                        .map(([clase, prob]) => (
                          <div key={clase}>
                            <div className="flex justify-between text-xs mb-1">
                              <span>{clase.replace(/_/g, ' ')}</span>
                              <span>{(prob * 100).toFixed(1)}%</span>
                            </div>
                            <div className="bg-gray-600 rounded-full h-1.5">
                              <div
                                className="bg-gradient-to-r from-purple-500 to-pink-500 h-1.5 rounded-full"
                                style={{ width: `${prob * 100}%` }}
                              />
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
        
        {/* Dashboard Avanzado NIfTI */}
        {imagen.resultados_ia?.nifti_analisis_avanzado && (
          <div className="absolute bottom-0 right-0 w-1/3 max-h-screen overflow-y-auto bg-white shadow-2xl">
            <DashboardNIfTI
              imagenId={imagen.id}
              analisisAvanzado={imagen.resultados_ia.nifti_analisis_avanzado}
            />
          </div>
        )}
      </div>
    </div>
  )
}

export default VisorImagenes
