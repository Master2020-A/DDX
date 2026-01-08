import { useState, useEffect, useRef } from 'react'
import { Send, Paperclip } from 'lucide-react'
import api from '@/lib/api'


interface Mensaje {
  id: string
  emisor_tipo: 'medico' | 'paciente'
  contenido: string
  tipo_mensaje: 'texto' | 'imagen' | 'archivo' | 'sistema'
  archivo_url?: string
  created_at: string
  leido: boolean
}

interface ChatConsultaProps {
  consultaRemotaId: string
  userId: string
  userRole: 'medico' | 'paciente'
  salaId: string
  token: string
}

const ChatConsulta: React.FC<ChatConsultaProps> = ({
  consultaRemotaId,
  userId,
  userRole,
  salaId,
  token,
}) => {
  const [mensajes, setMensajes] = useState<Mensaje[]>([])
  const [nuevoMensaje, setNuevoMensaje] = useState('')
  const [enviando, setEnviando] = useState(false)
  const [conectado, setConectado] = useState(false)

  const mensajesEndRef = useRef<HTMLDivElement>(null)
  const socketRef = useRef<WebSocket | null>(null)

  const buildWsUrl = () => {
    const rawBase = api.defaults.baseURL?.replace(/\/api$/, '') ?? 'http://localhost:8612'
    const parsed = new URL(rawBase)
    const wsProtocol = parsed.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsBase = `${wsProtocol}//${parsed.host}${parsed.pathname.replace(/\/$/, '')}`
    const params = new URLSearchParams({
      sala_id: salaId,
      user_id: userId,
      role: userRole,
      token,
    })
    return `${wsBase}/ws/telemedicina?${params.toString()}`
  }

  const sendSocketMessage = (payload: Record<string, any>) => {
    const socket = socketRef.current
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(
        JSON.stringify({
          sala_id: salaId,
          user_id: userId,
          ...payload,
        })
      )
    }
  }

  const handleSocketMessage = (event: MessageEvent) => {
    try {
      const data = JSON.parse(event.data)
      if (data.type !== 'chat_message') {
        return
      }
      const mensaje: Mensaje = {
        id: data.mensaje?.id || Date.now().toString(),
        emisor_tipo:
          data.user_id === userId
            ? userRole
            : userRole === 'medico'
            ? 'paciente'
            : 'medico',
        contenido: data.mensaje?.contenido || '',
        tipo_mensaje: data.mensaje?.tipo_mensaje || 'texto',
        archivo_url: data.mensaje?.archivo_url,
        created_at: data.timestamp || new Date().toISOString(),
        leido: false,
      }

      setMensajes((prev) => [...prev, mensaje])
    } catch (error) {
      console.error('Error procesando mensaje de chat:', error)
    }
  }

  useEffect(() => {
    const socket = new WebSocket(buildWsUrl())
    socketRef.current = socket

    socket.onopen = () => {
      console.log('Chat WebSocket conectado')
      setConectado(true)
    }

    socket.onclose = () => {
      console.log('Chat WebSocket desconectado')
      setConectado(false)
    }

    socket.onerror = () => {
      setConectado(false)
    }

    socket.onmessage = handleSocketMessage

    // Cargar mensajes anteriores
    cargarMensajes()

    return () => {
      socket.close()
    }
  }, [consultaRemotaId, userId, userRole, salaId, token])


  useEffect(() => {
    // Scroll automático al último mensaje
    scrollToBottom()
  }, [mensajes])

  const cargarMensajes = async () => {
    try {
      const { data } = await api.get(`/telemedicina/chat/${consultaRemotaId}/mensajes`)
      setMensajes(data)
    } catch (error) {
      console.error('Error cargando mensajes:', error)
    }
  }


  const enviarMensaje = async () => {
    if (!nuevoMensaje.trim() || enviando) return

    setEnviando(true)

    try {
      // Enviar mensaje a través del WebSocket
      sendSocketMessage({
        type: 'chat_message',
        mensaje: {
          consulta_remota_id: consultaRemotaId,
          contenido: nuevoMensaje,
          tipo_mensaje: 'texto',
        },
      })

      // También guardar en BD a través de la API
      await api.post('/telemedicina/chat/mensaje', {
        consulta_remota_id: consultaRemotaId,
        contenido: nuevoMensaje,
        tipo_mensaje: 'texto',
      })

      setNuevoMensaje('')

    } catch (error) {
      console.error('Error enviando mensaje:', error)
    } finally {
      setEnviando(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      enviarMensaje()
    }
  }

  const scrollToBottom = () => {
    mensajesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const formatearHora = (fecha: string) => {
    const date = new Date(fecha)
    return date.toLocaleTimeString('es-MX', {
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      <div className="bg-indigo-600 text-white p-4 flex items-center justify-between">
        <div>
          <h3 className="font-semibold">Chat de Consulta</h3>
          <p className="text-sm text-indigo-200">
            {conectado ? 'Conectado' : 'Desconectado'}
          </p>
        </div>
      </div>

      {/* Mensajes */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {mensajes.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <p>No hay mensajes aún</p>
            <p className="text-sm">Inicia la conversación</p>
          </div>
        ) : (
          mensajes.map((mensaje) => {
            const esMio = mensaje.emisor_tipo === userRole

            return (
              <div
                key={mensaje.id}
                className={`flex ${esMio ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[70%] rounded-lg px-4 py-2 ${
                    esMio
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-200 text-gray-900'
                  }`}
                >
                  {/* Etiqueta de emisor */}
                  {!esMio && (
                    <p className="text-xs font-semibold mb-1 text-gray-600">
                      {mensaje.emisor_tipo === 'medico' ? 'Médico' : 'Paciente'}
                    </p>
                  )}

                  {/* Contenido */}
                  <p className="text-sm whitespace-pre-wrap break-words">
                    {mensaje.contenido}
                  </p>

                  {/* Archivo adjunto */}
                  {mensaje.archivo_url && (
                    <div className="mt-2">
                      <a
                        href={mensaje.archivo_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs underline flex items-center gap-1"
                      >
                        <Paperclip className="w-3 h-3" />
                        Ver archivo
                      </a>
                    </div>
                  )}

                  {/* Hora */}
                  <p
                    className={`text-xs mt-1 ${
                      esMio ? 'text-indigo-200' : 'text-gray-500'
                    }`}
                  >
                    {formatearHora(mensaje.created_at)}
                  </p>
                </div>
              </div>
            )
          })
        )}
        <div ref={mensajesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t p-4">
        <div className="flex items-end gap-2">
          <div className="flex-1">
            <textarea
              value={nuevoMensaje}
              onChange={(e) => setNuevoMensaje(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Escribe un mensaje..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500"
              rows={2}
              disabled={!conectado || enviando}
            />
          </div>

          <button
            onClick={enviarMensaje}
            disabled={!nuevoMensaje.trim() || !conectado || enviando}
            className="p-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            title="Enviar mensaje"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>

        <p className="text-xs text-gray-500 mt-2">
          Presiona Enter para enviar, Shift+Enter para nueva línea
        </p>
      </div>
    </div>
  )
}

export default ChatConsulta
