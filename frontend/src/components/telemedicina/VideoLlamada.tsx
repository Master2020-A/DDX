import { useEffect, useRef, useState } from 'react'
import { Video, VideoOff, Mic, MicOff, PhoneOff, Monitor, MonitorOff } from 'lucide-react'
import SimplePeer from 'simple-peer'
import api from '@/lib/api'


interface VideoLlamadaProps {
  salaId: string
  userId: string
  role: 'medico' | 'paciente'
  token: string
  onFinalizar?: () => void
}

const VideoLlamada: React.FC<VideoLlamadaProps> = ({
  salaId,
  userId,
  role,
  token,
  onFinalizar,
}) => {
  const [peer, setPeer] = useState<SimplePeer.Instance | null>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [remoteStream, setRemoteStream] = useState<MediaStream | null>(null)
  const [audioEnabled, setAudioEnabled] = useState(true)
  const [videoEnabled, setVideoEnabled] = useState(true)
  const [screenSharing, setScreenSharing] = useState(false)
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const localVideoRef = useRef<HTMLVideoElement>(null)
  const remoteVideoRef = useRef<HTMLVideoElement>(null)
  const socketRef = useRef<WebSocket | null>(null)
  const peerRef = useRef<SimplePeer.Instance | null>(null)
  const queuedSignalsRef = useRef<any[]>([])
  const screenStreamRef = useRef<MediaStream | null>(null)

  const buildWsUrl = () => {
    const rawBase = api.defaults.baseURL?.replace(/\/api$/, '') ?? 'http://localhost:8612'
    const parsed = new URL(rawBase)
    const wsProtocol = parsed.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsBase = `${wsProtocol}//${parsed.host}${parsed.pathname.replace(/\/$/, '')}`
    const params = new URLSearchParams({
      sala_id: salaId,
      user_id: userId,
      role,
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
      switch (data.type) {
        case 'webrtc_signal':
          if (data.from_user_id === userId) return
          if (peerRef.current) {
            peerRef.current.signal(data.signal)
          } else {
            queuedSignalsRef.current.push(data.signal)
          }
          break
        case 'ping':
          sendSocketMessage({ type: 'pong' })
          break
        default:
          break
      }
    } catch (err) {
      console.error('Error procesando mensaje WebSocket', err)
    }
  }

  useEffect(() => {
    iniciarLlamada()

    return () => {
      limpiarRecursos()
    }
  }, [salaId, userId, role, token])

  const iniciarLlamada = async () => {
    try {
      const localStream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      })

      setStream(localStream)

      if (localVideoRef.current) {
        localVideoRef.current.srcObject = localStream
      }

      const ws = new WebSocket(buildWsUrl())
      socketRef.current = ws

      ws.onopen = () => {
        console.log('WebSocket conectado')
        crearPeer(localStream)
      }

      ws.onclose = () => {
        console.log('WebSocket desconectado')
        setConnected(false)
      }

      ws.onerror = (event) => {
        console.error('Error WebSocket', event)
        setError('Error en la conexión WebSocket')
      }

      ws.onmessage = handleSocketMessage
    } catch (err: any) {
      console.error('Error iniciando llamada:', err)
      setError(err.message || 'Error al acceder a cámara/micrófono')
    }
  }

  const crearPeer = (localStream: MediaStream) => {

    const newPeer = new SimplePeer({
      initiator: role === 'medico',
      trickle: false,
      stream: localStream,
      config: {
        iceServers: [
          { urls: 'stun:stun.l.google.com:19302' },
          { urls: 'stun:stun1.l.google.com:19302' },
        ],
      },
    })

    newPeer.on('signal', (signal) => {
      console.log('Enviando señal WebRTC')
      sendSocketMessage({ type: 'webrtc_signal', signal })
    })

    newPeer.on('stream', (remoteStream) => {
      console.log('Stream remoto recibido')
      setRemoteStream(remoteStream)
      if (remoteVideoRef.current) {
        remoteVideoRef.current.srcObject = remoteStream
      }
      setConnected(true)
    })

    newPeer.on('error', (err) => {
      console.error('Error en peer:', err)
      setError('Error en la conexión de video')
    })

    peerRef.current = newPeer
    setPeer(newPeer)

    if (queuedSignalsRef.current.length) {
      queuedSignalsRef.current.forEach((signal) => newPeer.signal(signal))
      queuedSignalsRef.current = []
    }
  }

  const toggleAudio = () => {

    if (stream) {
      const audioTrack = stream.getAudioTracks()[0]
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled
        setAudioEnabled(audioTrack.enabled)

        // Notificar al otro usuario
        sendSocketMessage({ type: 'media_state', audio: audioTrack.enabled })

      }
    }
  }

  const toggleVideo = () => {
    if (stream) {
      const videoTrack = stream.getVideoTracks()[0]
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled
        setVideoEnabled(videoTrack.enabled)

        // Notificar al otro usuario
        sendSocketMessage({ type: 'media_state', video: videoTrack.enabled })

      }
    }
  }

  const toggleScreenShare = async () => {
    if (!screenSharing) {
      try {
        // Iniciar compartir pantalla
        const screenStream = await navigator.mediaDevices.getDisplayMedia({
          video: true,
        })

        screenStreamRef.current = screenStream

        // Reemplazar track de video con el de la pantalla
        const screenTrack = screenStream.getVideoTracks()[0]
        const sender = peer?.streams[0]?.getVideoTracks()[0]

        if (sender && peer) {
          // @ts-ignore
          const senders = peer._pc.getSenders()
          const videoSender = senders.find((s: any) => s.track?.kind === 'video')
          if (videoSender) {
            videoSender.replaceTrack(screenTrack)
          }
        }

        // Cuando se detiene compartir pantalla
        screenTrack.onended = () => {
          detenerCompartirPantalla()
        }

        setScreenSharing(true)

        // Notificar al otro usuario
        sendSocketMessage({ type: 'screen_share', estado: true })

      } catch (err) {
        console.error('Error compartiendo pantalla:', err)
      }
    } else {
      detenerCompartirPantalla()
    }
  }

  const detenerCompartirPantalla = () => {
    if (screenStreamRef.current) {
      screenStreamRef.current.getTracks().forEach((track) => track.stop())
      screenStreamRef.current = null
    }

    // Restaurar video de cámara
    if (stream && peer) {
      const videoTrack = stream.getVideoTracks()[0]
      // @ts-ignore
      const senders = peer._pc.getSenders()
      const videoSender = senders.find((s: any) => s.track?.kind === 'video')
      if (videoSender) {
        videoSender.replaceTrack(videoTrack)
      }
    }

    setScreenSharing(false)

    // Notificar al otro usuario
    sendSocketMessage({ type: 'screen_share', estado: false })

  }

  const finalizarLlamada = () => {
    limpiarRecursos()
    onFinalizar?.()
  }

  const limpiarRecursos = () => {
    // Detener todos los tracks
    stream?.getTracks().forEach((track) => track.stop())
    screenStreamRef.current?.getTracks().forEach((track) => track.stop())

    // Cerrar peer
    peer?.destroy()

    // Desconectar socket
    if (socketRef.current) {
      socketRef.current.close()
      socketRef.current = null
    }

    setStream(null)
    setRemoteStream(null)
    setPeer(null)
    queuedSignalsRef.current = []
    setConnected(false)
  }


  return (
    <div className="flex flex-col h-full bg-gray-900">
      {/* Videos */}
      <div className="flex-1 relative">
        {/* Video remoto (principal) */}
        <div className="w-full h-full bg-black flex items-center justify-center">
          {remoteStream ? (
            <video
              ref={remoteVideoRef}
              autoPlay
              playsInline
              className="w-full h-full object-contain"
            />
          ) : (
            <div className="text-white text-center">
              <div className="animate-pulse mb-4">
                <Video className="w-16 h-16 mx-auto" />
              </div>
              <p className="text-lg">Esperando conexión...</p>
            </div>
          )}
        </div>

        {/* Video local (miniatura) */}
        <div className="absolute bottom-4 right-4 w-48 h-36 bg-gray-800 rounded-lg overflow-hidden shadow-lg border-2 border-gray-700">
          <video
            ref={localVideoRef}
            autoPlay
            muted
            playsInline
            className="w-full h-full object-cover"
          />
          {!videoEnabled && (
            <div className="absolute inset-0 bg-gray-800 flex items-center justify-center">
              <VideoOff className="w-8 h-8 text-gray-400" />
            </div>
          )}
        </div>

        {/* Indicador de conexión */}
        {connected && (
          <div className="absolute top-4 left-4 bg-green-500 text-white px-3 py-1 rounded-full text-sm flex items-center gap-2">
            <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
            Conectado
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-red-500 text-white px-4 py-2 rounded-lg">
            {error}
          </div>
        )}
      </div>

      {/* Controles */}
      <div className="bg-gray-800 p-4">
        <div className="flex justify-center items-center gap-4">
          {/* Toggle Audio */}
          <button
            onClick={toggleAudio}
            className={`p-4 rounded-full transition-colors ${
              audioEnabled
                ? 'bg-gray-700 hover:bg-gray-600 text-white'
                : 'bg-red-500 hover:bg-red-600 text-white'
            }`}
            title={audioEnabled ? 'Silenciar' : 'Activar audio'}
          >
            {audioEnabled ? <Mic className="w-6 h-6" /> : <MicOff className="w-6 h-6" />}
          </button>

          {/* Toggle Video */}
          <button
            onClick={toggleVideo}
            className={`p-4 rounded-full transition-colors ${
              videoEnabled
                ? 'bg-gray-700 hover:bg-gray-600 text-white'
                : 'bg-red-500 hover:bg-red-600 text-white'
            }`}
            title={videoEnabled ? 'Desactivar video' : 'Activar video'}
          >
            {videoEnabled ? <Video className="w-6 h-6" /> : <VideoOff className="w-6 h-6" />}
          </button>

          {/* Compartir Pantalla */}
          <button
            onClick={toggleScreenShare}
            className={`p-4 rounded-full transition-colors ${
              screenSharing
                ? 'bg-blue-500 hover:bg-blue-600 text-white'
                : 'bg-gray-700 hover:bg-gray-600 text-white'
            }`}
            title={screenSharing ? 'Detener compartir' : 'Compartir pantalla'}
          >
            {screenSharing ? <MonitorOff className="w-6 h-6" /> : <Monitor className="w-6 h-6" />}
          </button>

          {/* Finalizar Llamada */}
          <button
            onClick={finalizarLlamada}
            className="p-4 rounded-full bg-red-500 hover:bg-red-600 text-white transition-colors"
            title="Finalizar llamada"
          >
            <PhoneOff className="w-6 h-6" />
          </button>
        </div>
      </div>
    </div>
  )
}

export default VideoLlamada
