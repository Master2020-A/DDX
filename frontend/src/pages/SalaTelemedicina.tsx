import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { MessageSquare, FileText } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import VideoLlamada from '@/components/telemedicina/VideoLlamada'
import ChatConsulta from '@/components/telemedicina/ChatConsulta'

interface ConsultaRemota {
  id: string
  sala_id: string
  paciente: {
    id: string
    nombre: string
  }
  medico: {
    id: string
    nombre: string
  }
  estado: string
  fecha_programada: string
  motivo_consulta: string
}

const SalaTelemedicina = () => {
  const { consultaId } = useParams()
  const navigate = useNavigate()
  
  const [consulta, setConsulta] = useState<ConsultaRemota | null>(null)
  const [mostrarChat, setMostrarChat] = useState(false)
  const [mostrarNotas, setMostrarNotas] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Obtener datos del usuario actual desde el store
  const { user, token } = useAuthStore()
  const userId = user?.id || ''
  const userRole = (user?.rol as 'medico' | 'paciente') || 'paciente'

  useEffect(() => {
    cargarConsulta()
  }, [consultaId])

  const cargarConsulta = async () => {
    if (!token) {
      setError('No hay token de autenticación')
      setLoading(false)
      return
    }

    try {
      const response = await fetch(
        `http://localhost:8612/api/telemedicina/consultas/${consultaId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      if (!response.ok) {
        throw new Error('Error al cargar consulta')
      }

      const data = await response.json()
      setConsulta(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const finalizarConsulta = async () => {
    if (!confirm('¿Está seguro de finalizar la consulta?')) return

    try {
      await fetch(
        `http://localhost:8612/api/telemedicina/consultas/${consultaId}/finalizar`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            notas_medico: '',
            requiere_seguimiento: false,
          }),
        }
      )

      navigate('/telemedicina')
    } catch (err) {
      console.error('Error finalizando consulta:', err)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando sala...</p>
        </div>
      </div>
    )
  }

  if (error || !consulta) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || 'Consulta no encontrada'}</p>
          <button
            onClick={() => navigate('/telemedicina')}
            className="btn btn-primary"
          >
            Volver
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col bg-gray-100">
      {/* Header */}
      <div className="bg-white shadow-sm p-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">
            Consulta Remota
          </h1>
          <p className="text-sm text-gray-600">
            {userRole === 'medico' 
              ? `Paciente: ${consulta.paciente.nombre}`
              : `Médico: ${consulta.medico.nombre}`
            }
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Toggle Chat */}
          <button
            onClick={() => setMostrarChat(!mostrarChat)}
            className={`p-2 rounded-lg transition-colors ${
              mostrarChat
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
            title="Chat"
          >
            <MessageSquare className="w-5 h-5" />
          </button>

          {/* Toggle Notas (solo médico) */}
          {userRole === 'medico' && (
            <button
              onClick={() => setMostrarNotas(!mostrarNotas)}
              className={`p-2 rounded-lg transition-colors ${
                mostrarNotas
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
              title="Notas"
            >
              <FileText className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>

      {/* Contenido Principal */}
      <div className="flex-1 flex overflow-hidden">
        {/* Video */}
        <div className={`${mostrarChat || mostrarNotas ? 'w-2/3' : 'w-full'} transition-all`}>
          <VideoLlamada
            salaId={consulta.sala_id}
            userId={userId}
            role={userRole}
            token={token || ''}
            onFinalizar={finalizarConsulta}
          />
        </div>

        {/* Panel Lateral (Chat o Notas) */}
        {(mostrarChat || mostrarNotas) && (
          <div className="w-1/3 border-l border-gray-300 bg-white flex flex-col">
            {/* Tabs */}
            <div className="flex border-b">
              {mostrarChat && (
                <button
                  onClick={() => {
                    setMostrarChat(true)
                    setMostrarNotas(false)
                  }}
                  className={`flex-1 px-4 py-3 text-sm font-medium ${
                    mostrarChat && !mostrarNotas
                      ? 'text-indigo-600 border-b-2 border-indigo-600'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Chat
                </button>
              )}
              {mostrarNotas && userRole === 'medico' && (
                <button
                  onClick={() => {
                    setMostrarChat(false)
                    setMostrarNotas(true)
                  }}
                  className={`flex-1 px-4 py-3 text-sm font-medium ${
                    mostrarNotas && !mostrarChat
                      ? 'text-indigo-600 border-b-2 border-indigo-600'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Notas
                </button>
              )}
            </div>

            {/* Contenido */}
            <div className="flex-1 overflow-hidden">
              {mostrarChat && !mostrarNotas && (
                <ChatConsulta
                  consultaRemotaId={consulta.id}
                  userId={userId}
                  userRole={userRole}
                  salaId={consulta.sala_id}
                  token={token || ''}
                />
              )}

              {mostrarNotas && !mostrarChat && userRole === 'medico' && (
                <div className="p-4 h-full flex flex-col">
                  <h3 className="font-semibold mb-4">Notas de la Consulta</h3>
                  <textarea
                    className="flex-1 w-full p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    placeholder="Escribe tus notas aquí..."
                  />
                  <button className="mt-4 btn btn-primary w-full">
                    Guardar Notas
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default SalaTelemedicina
