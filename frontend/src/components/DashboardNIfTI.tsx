import React, { useState, useEffect } from 'react'
import { Activity, Brain, Layers, PieChart, BarChart3 } from 'lucide-react'
import api from '@/lib/api'

interface EstructuraAnatomica {
  nombre: string
  volumen: number
  color: { r: number; g: number; b: number }
  porcentaje: number
}

interface VisualizacionData {
  estructuras: EstructuraAnatomica[]
  total_volumen: number
}

interface AnalisisAvanzado {
  metricas_globales?: {
    volumen_total_cm3: number
    volumen_tejido_cm3: number
    dimensiones: number[]
  }
  calidad_imagen?: {
    calidad_estimada: string
    snr: number
    cnr: number
  }
  analisis_multiplanar?: {
    [key: string]: {
      intensidad_media: number
      porcentaje_ocupacion: number
    }
  }
}

interface DashboardNIfTIProps {
  imagenId: string
  analisisAvanzado?: AnalisisAvanzado
}

const DashboardNIfTI: React.FC<DashboardNIfTIProps> = ({ imagenId, analisisAvanzado }) => {
  const [visualizacion, setVisualizacion] = useState<VisualizacionData | null>(null)
  const [segmentando, setSegmentando] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [tabActiva, setTabActiva] = useState<'resumen' | 'anatomia' | 'calidad' | '3d'>('resumen')

  const cargarVisualizacion = async () => {
    try {
      const response = await api.get(`/imagenes/${imagenId}/visualizacion-3d`)
      setVisualizacion(response.data.visualizacion)
    } catch (err: any) {
      // Si no existe, no es error crítico
      console.log('No hay visualización 3D disponible')
    }
  }

  const ejecutarSegmentacion = async () => {
    setSegmentando(true)
    setError(null)
    
    try {
      const response = await api.post(
        `/imagenes/${imagenId}/segmentar-anatomico?fast=true`
      )
      
      setVisualizacion(response.data.visualizacion)
      alert('✅ Segmentación completada')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error en segmentación')
    } finally {
      setSegmentando(false)
    }
  }

  useEffect(() => {
    cargarVisualizacion()
  }, [imagenId])

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Brain className="w-8 h-8 text-purple-600" />
          <h2 className="text-2xl font-bold text-gray-800">Análisis Avanzado 3D</h2>
        </div>
        
        {!visualizacion && (
          <button
            onClick={ejecutarSegmentacion}
            disabled={segmentando}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center space-x-2"
          >
            <Layers className="w-5 h-5" />
            <span>{segmentando ? 'Segmentando...' : 'Segmentar Anatomía'}</span>
          </button>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex space-x-8">
          <button
            onClick={() => setTabActiva('resumen')}
            className={`pb-4 px-2 ${
              tabActiva === 'resumen'
                ? 'border-b-2 border-purple-600 text-purple-600 font-semibold'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Activity className="w-5 h-5" />
              <span>Resumen</span>
            </div>
          </button>
          
          <button
            onClick={() => setTabActiva('anatomia')}
            className={`pb-4 px-2 ${
              tabActiva === 'anatomia'
                ? 'border-b-2 border-purple-600 text-purple-600 font-semibold'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Layers className="w-5 h-5" />
              <span>Anatomía</span>
            </div>
          </button>
          
          <button
            onClick={() => setTabActiva('calidad')}
            className={`pb-4 px-2 ${
              tabActiva === 'calidad'
                ? 'border-b-2 border-purple-600 text-purple-600 font-semibold'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <div className="flex items-center space-x-2">
              <BarChart3 className="w-5 h-5" />
              <span>Calidad</span>
            </div>
          </button>
          
          {visualizacion && (
            <button
              onClick={() => setTabActiva('3d')}
              className={`pb-4 px-2 ${
                tabActiva === '3d'
                  ? 'border-b-2 border-purple-600 text-purple-600 font-semibold'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <div className="flex items-center space-x-2">
                <PieChart className="w-5 h-5" />
                <span>Visualización 3D</span>
              </div>
            </button>
          )}
        </div>
      </div>

      {/* Contenido de tabs */}
      <div className="mt-6">
        {/* TAB RESUMEN */}
        {tabActiva === 'resumen' && analisisAvanzado && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Métricas Globales */}
            {analisisAvanzado.metricas_globales && (
              <>
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
                  <div className="text-sm text-blue-600 font-semibold mb-1">Volumen Total</div>
                  <div className="text-3xl font-bold text-blue-900">
                    {analisisAvanzado.metricas_globales.volumen_total_cm3.toFixed(1)}
                    <span className="text-lg ml-1">cm³</span>
                  </div>
                </div>
                
                <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4">
                  <div className="text-sm text-green-600 font-semibold mb-1">Volumen Tejido</div>
                  <div className="text-3xl font-bold text-green-900">
                    {analisisAvanzado.metricas_globales.volumen_tejido_cm3.toFixed(1)}
                    <span className="text-lg ml-1">cm³</span>
                  </div>
                </div>
                
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4">
                  <div className="text-sm text-purple-600 font-semibold mb-1">Dimensiones</div>
                  <div className="text-2xl font-bold text-purple-900">
                    {analisisAvanzado.metricas_globales.dimensiones.join(' × ')}
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {/* TAB ANATOMÍA */}
        {tabActiva === 'anatomia' && !visualizacion && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
            <Layers className="w-12 h-12 text-blue-600 mx-auto mb-3" />
            <h4 className="font-semibold text-blue-900 mb-2">
              Segmentación anatómica no ejecutada
            </h4>
            <p className="text-sm text-blue-700 mb-4">
              Haz clic en el botón "Segmentar Anatomía" para analizar las estructuras anatómicas.
            </p>
            <button
              onClick={ejecutarSegmentacion}
              disabled={segmentando}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 inline-flex items-center space-x-2"
            >
              <Layers className="w-5 h-5" />
              <span>{segmentando ? 'Segmentando...' : 'Segmentar Ahora'}</span>
            </button>
          </div>
        )}
        
        {tabActiva === 'anatomia' && visualizacion && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              Estructuras Anatómicas ({visualizacion.estructuras?.length || 0})
            </h3>
            
            {(!visualizacion.estructuras || visualizacion.estructuras.length === 0) && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
                <Brain className="w-12 h-12 text-yellow-600 mx-auto mb-3" />
                <h4 className="font-semibold text-yellow-900 mb-2">
                  No hay estructuras anatómicas disponibles
                </h4>
                <p className="text-sm text-yellow-700 mb-4">
                  Para segmentación anatómica detallada (104 estructuras), necesitas instalar TotalSegmentator.
                </p>
                <div className="bg-white rounded-lg p-4 text-left">
                  <p className="text-xs font-mono text-gray-600 mb-2">Instalación:</p>
                  <code className="text-xs bg-gray-100 px-2 py-1 rounded block">
                    python instalar_segmentacion.py
                  </code>
                  <p className="text-xs text-gray-500 mt-2">
                    Requiere: GPU NVIDIA (8GB VRAM) o 16GB RAM
                  </p>
                </div>
              </div>
            )}
            
            <div className="space-y-2">
              {visualizacion.estructuras?.map((estructura, idx) => (
                <div key={idx} className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div
                        className="w-4 h-4 rounded"
                        style={{
                          backgroundColor: `rgb(${estructura.color.r}, ${estructura.color.g}, ${estructura.color.b})`
                        }}
                      />
                      <span className="font-medium text-gray-800">{estructura.nombre}</span>
                    </div>
                    
                    <div className="flex items-center space-x-4">
                      <span className="text-sm text-gray-600">
                        {estructura.volumen.toFixed(2)} cm³
                      </span>
                      <span className="text-sm font-semibold text-purple-600">
                        {estructura.porcentaje.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                  
                  {/* Barra de progreso */}
                  <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="h-2 rounded-full transition-all duration-300"
                      style={{
                        width: `${estructura.porcentaje}%`,
                        backgroundColor: `rgb(${estructura.color.r}, ${estructura.color.g}, ${estructura.color.b})`
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB CALIDAD */}
        {tabActiva === 'calidad' && analisisAvanzado?.calidad_imagen && (
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-indigo-900 mb-4">Evaluación de Calidad</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white rounded-lg p-4">
                  <div className="text-sm text-gray-600 mb-1">Calidad General</div>
                  <div className="text-2xl font-bold text-indigo-600 capitalize">
                    {analisisAvanzado.calidad_imagen.calidad_estimada}
                  </div>
                </div>
                
                <div className="bg-white rounded-lg p-4">
                  <div className="text-sm text-gray-600 mb-1">SNR</div>
                  <div className="text-2xl font-bold text-blue-600">
                    {analisisAvanzado.calidad_imagen.snr.toFixed(2)}
                  </div>
                </div>
                
                <div className="bg-white rounded-lg p-4">
                  <div className="text-sm text-gray-600 mb-1">CNR</div>
                  <div className="text-2xl font-bold text-green-600">
                    {analisisAvanzado.calidad_imagen.cnr.toFixed(2)}
                  </div>
                </div>
              </div>
            </div>
            
            {/* Análisis Multiplanar */}
            {analisisAvanzado.analisis_multiplanar && (
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Análisis Multiplanar</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {Object.entries(analisisAvanzado.analisis_multiplanar).map(([plano, datos]) => (
                    <div key={plano} className="bg-gray-50 rounded-lg p-4">
                      <h4 className="font-semibold text-gray-800 capitalize mb-2">{plano}</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Intensidad:</span>
                          <span className="font-medium">{datos.intensidad_media?.toFixed(1)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Ocupación:</span>
                          <span className="font-medium">{datos.porcentaje_ocupacion?.toFixed(1)}%</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB VISUALIZACIÓN 3D */}
        {tabActiva === '3d' && visualizacion && (
          <div className="space-y-6">
            {/* Gráfico de barras */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                Distribución de Volumen por Estructura
              </h3>
              <div className="space-y-3">
                {visualizacion.estructuras.map((estructura, idx) => (
                  <div key={idx} className="relative">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm font-medium text-gray-700">{estructura.nombre}</span>
                      <span className="text-sm text-gray-600">{estructura.volumen.toFixed(1)} cm³</span>
                    </div>
                    <div className="w-full h-8 bg-gray-200 rounded-lg overflow-hidden">
                      <div
                        className="h-full transition-all duration-500 flex items-center justify-end pr-2"
                        style={{
                          width: `${estructura.porcentaje}%`,
                          backgroundColor: `rgb(${estructura.color.r}, ${estructura.color.g}, ${estructura.color.b})`
                        }}
                      >
                        <span className="text-xs font-semibold text-white">
                          {estructura.porcentaje.toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Leyenda de colores */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-semibold text-gray-800 mb-3">Leyenda de Colores</h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {visualizacion.estructuras.slice(0, 6).map((estructura, idx) => (
                  <div key={idx} className="flex items-center space-x-2">
                    <div
                      className="w-6 h-6 rounded shadow-sm"
                      style={{
                        backgroundColor: `rgb(${estructura.color.r}, ${estructura.color.g}, ${estructura.color.b})`
                      }}
                    />
                    <span className="text-sm text-gray-700">{estructura.nombre}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default DashboardNIfTI
