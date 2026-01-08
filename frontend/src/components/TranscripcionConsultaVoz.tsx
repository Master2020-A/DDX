import { useState, useRef } from 'react'
import { Mic, Square, Sparkles, X, CheckCircle, Loader2 } from 'lucide-react'
import api from '@/lib/api'

interface TranscripcionConsultaVozProps {
  pacienteId: string
  onDatosExtraidos?: (datos: any) => void
  onTranscripcionCompleta?: (texto: string) => void
}

const TranscripcionConsultaVoz = ({
  pacienteId,
  onDatosExtraidos,
  onTranscripcionCompleta,
}: TranscripcionConsultaVozProps) => {
  const [grabando, setGrabando] = useState(false)
  const [procesando, setProcesando] = useState(false)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const [transcripcion, setTranscripcion] = useState<string>('')
  const [datosExtraidos, setDatosExtraidos] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [tiempoGrabacion, setTiempoGrabacion] = useState(0)
  const [mostrarResultados, setMostrarResultados] = useState(false)
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const timerRef = useRef<NodeJS.Timeout | null>(null)

  const iniciarGrabacion = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data)
        }
      }

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        setAudioBlob(blob)
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setGrabando(true)
      setTiempoGrabacion(0)
      setError(null)

      timerRef.current = setInterval(() => {
        setTiempoGrabacion(prev => prev + 1)
      }, 1000)

    } catch (err) {
      console.error('Error al acceder al micrófono:', err)
      setError('No se pudo acceder al micrófono. Verifica los permisos.')
    }
  }

  const detenerGrabacion = () => {
    if (mediaRecorderRef.current && grabando) {
      mediaRecorderRef.current.stop()
      setGrabando(false)
      
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
    }
  }

  const procesarAudio = async () => {
    if (!audioBlob) return

    try {
      setProcesando(true)
      setError(null)

      const formData = new FormData()
      const archivo = new File([audioBlob], 'consulta.webm', { type: 'audio/webm' })
      formData.append('archivo', archivo)
      formData.append('paciente_id', pacienteId)
      formData.append('idioma', 'es')
      formData.append('extraer_informacion', 'true')

      const response = await api.post('/pln/transcribir-audio', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      const resultado = response.data
      setTranscripcion(resultado.texto)
      
      if (resultado.informacion_extraida) {
        setDatosExtraidos(resultado.informacion_extraida)
        
        if (onDatosExtraidos) {
          onDatosExtraidos(resultado.informacion_extraida)
        }
      }

      if (onTranscripcionCompleta) {
        onTranscripcionCompleta(resultado.texto)
      }

      setMostrarResultados(true)

    } catch (err: any) {
      console.error('Error al procesar audio:', err)
      setError(err.response?.data?.detail || 'Error al transcribir el audio')
    } finally {
      setProcesando(false)
    }
  }

  const formatearTiempo = (segundos: number) => {
    const mins = Math.floor(segundos / 60)
    const secs = segundos % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const limpiar = () => {
    setAudioBlob(null)
    setTranscripcion('')
    setDatosExtraidos(null)
    setTiempoGrabacion(0)
    setMostrarResultados(false)
    setError(null)
  }

  const aplicarDatos = () => {
    setMostrarResultados(false)
    limpiar()
  }

  return (
    <>
      <div className="card bg-gradient-to-br from-purple-50 to-indigo-50 border-purple-200">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Mic className="w-6 h-6 text-purple-600" />
            <h3 className="text-lg font-semibold text-gray-900">Captura de Consulta por Voz</h3>
          </div>
          {audioBlob && (
            <span className="inline-flex items-center gap-1 px-3 py-1 bg-green-100 text-green-800 text-sm font-medium rounded-full">
              <CheckCircle className="w-4 h-4" />
              Audio grabado
            </span>
          )}
        </div>

        <p className="text-sm text-gray-600 mb-4">
          Graba la consulta médica y el sistema transcribirá automáticamente el audio,
          extrayendo síntomas, signos vitales, diagnósticos y más para pre-llenar el expediente.
        </p>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
            <X className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm text-red-800">{error}</p>
            </div>
            <button 
              onClick={() => setError(null)} 
              className="text-red-600 hover:text-red-800"
              aria-label="Cerrar alerta"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        <div className="flex items-center gap-3 flex-wrap">
          {!grabando && !audioBlob && (
            <button
              onClick={iniciarGrabacion}
              className="btn-primary flex items-center gap-2"
            >
              <Mic className="w-5 h-5" />
              Iniciar Grabación
            </button>
          )}

          {grabando && (
            <>
              <button
                onClick={detenerGrabacion}
                className="btn-danger flex items-center gap-2"
              >
                <Square className="w-5 h-5" />
                Detener Grabación
              </button>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                <span className="text-lg font-semibold text-red-600">
                  {formatearTiempo(tiempoGrabacion)}
                </span>
              </div>
            </>
          )}

          {audioBlob && !procesando && (
            <>
              <button
                onClick={procesarAudio}
                className="btn-primary flex items-center gap-2 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700"
              >
                <Sparkles className="w-5 h-5" />
                Transcribir y Extraer Datos
              </button>
              <button
                onClick={limpiar}
                className="btn-secondary"
              >
                Nueva Grabación
              </button>
            </>
          )}

          {procesando && (
            <div className="flex items-center gap-3 w-full">
              <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
              <div className="flex-1">
                <p className="text-sm text-gray-600 mb-1">Procesando audio con IA...</p>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full animate-pulse w-[70%]"></div>
                </div>
              </div>
            </div>
          )}
        </div>

        {audioBlob && (
          <p className="text-xs text-gray-500 mt-3">
            Duración: {formatearTiempo(tiempoGrabacion)}
          </p>
        )}
      </div>

      {/* Modal de Resultados */}
      {mostrarResultados && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between p-6 border-b">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-6 h-6 text-green-600" />
                <h2 className="text-xl font-bold text-gray-900">Transcripción Completada</h2>
              </div>
              <button
                onClick={() => setMostrarResultados(false)}
                className="text-gray-400 hover:text-gray-600"
                aria-label="Cerrar modal"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
              {/* Transcripción */}
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-gray-900 mb-2">📝 Texto Transcrito:</h3>
                <div className="card bg-gray-50">
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">{transcripcion}</p>
                </div>
              </div>

              {/* Datos Extraídos */}
              {datosExtraidos && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-900 mb-3">🔍 Información Extraída Automáticamente:</h3>

                  {/* Síntomas */}
                  {datosExtraidos.sintomas && datosExtraidos.sintomas.length > 0 && (
                    <div className="mb-4">
                      <p className="text-sm font-medium text-purple-700 mb-2">Síntomas:</p>
                      <div className="flex flex-wrap gap-2">
                        {datosExtraidos.sintomas.map((sintoma: any, idx: number) => (
                          <span
                            key={idx}
                            className="px-3 py-1 bg-purple-100 text-purple-800 text-sm rounded-full border border-purple-200"
                          >
                            {sintoma.nombre || sintoma}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Signos Vitales */}
                  {datosExtraidos.signos_vitales && (
                    <div className="mb-4">
                      <p className="text-sm font-medium text-purple-700 mb-2">Signos Vitales:</p>
                      <div className="grid grid-cols-2 gap-3">
                        {Object.entries(datosExtraidos.signos_vitales).map(([key, value]: [string, any]) => (
                          <div key={key} className="bg-gray-50 p-3 rounded-lg">
                            <p className="text-xs text-gray-500 uppercase">{key.replace(/_/g, ' ')}</p>
                            <p className="text-sm font-semibold text-gray-900">{value}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Medicamentos */}
                  {datosExtraidos.medicamentos && datosExtraidos.medicamentos.length > 0 && (
                    <div className="mb-4">
                      <p className="text-sm font-medium text-purple-700 mb-2">Medicamentos Mencionados:</p>
                      <div className="flex flex-wrap gap-2">
                        {datosExtraidos.medicamentos.map((med: any, idx: number) => (
                          <span
                            key={idx}
                            className="px-3 py-1 bg-pink-100 text-pink-800 text-sm rounded-full border border-pink-200"
                          >
                            {med.nombre || med}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Diagnósticos */}
                  {datosExtraidos.diagnosticos && datosExtraidos.diagnosticos.length > 0 && (
                    <div className="mb-4">
                      <p className="text-sm font-medium text-purple-700 mb-2">Diagnósticos Sugeridos:</p>
                      <div className="space-y-2">
                        {datosExtraidos.diagnosticos.map((diag: any, idx: number) => (
                          <div key={idx} className="bg-gray-50 p-3 rounded-lg">
                            <p className="text-sm font-semibold text-gray-900">{diag.nombre || diag}</p>
                            {diag.codigo_cie10 && (
                              <p className="text-xs text-gray-500">CIE-10: {diag.codigo_cie10}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Antecedentes */}
                  {datosExtraidos.antecedentes && datosExtraidos.antecedentes.length > 0 && (
                    <div className="mb-4">
                      <p className="text-sm font-medium text-purple-700 mb-2">Antecedentes:</p>
                      <ul className="space-y-1">
                        {datosExtraidos.antecedentes.map((ant: any, idx: number) => (
                          <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                            <span className="text-purple-600">•</span>
                            <span>{ant}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>

            <div className="flex items-center justify-end gap-3 p-6 border-t bg-gray-50">
              <button
                onClick={() => setMostrarResultados(false)}
                className="btn-secondary"
              >
                Cerrar
              </button>
              <button
                onClick={aplicarDatos}
                className="btn-primary"
              >
                Aceptar y Continuar
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default TranscripcionConsultaVoz
