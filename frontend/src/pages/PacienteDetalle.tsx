import { useState, useEffect, useMemo, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeft,
  User,
  Calendar,
  Phone,
  Mail,
  AlertCircle,
  Plus,
  FileText,
  Image,
  FlaskConical,
  Heart,
  Brain,
  Shield,
  Camera,
  Upload,
  Activity,
} from 'lucide-react'
import api from '@/lib/api'
import { Paciente, Consulta } from '@/types'
import { calculateAge, formatDateTime } from '@/lib/utils'
import DiagnosticoSugerido from '@/components/DiagnosticoSugerido'

const PacienteDetalle = () => {
  const { id } = useParams()
  const [paciente, setPaciente] = useState<Paciente | null>(null)
  const [consultas, setConsultas] = useState<Consulta[]>([])
  const [loading, setLoading] = useState(true)
  const [diagnosticoSugeridoOpen, setDiagnosticoSugeridoOpen] = useState(false)
  const [photoPreview, setPhotoPreview] = useState<string | null>(null)
  const [isCameraActive, setIsCameraActive] = useState(false)
  const [cameraError, setCameraError] = useState<string | null>(null)

  const videoRef = useRef<HTMLVideoElement | null>(null)
  const streamRef = useRef<MediaStream | null>(null)

  useEffect(() => {
    if (id) {
      fetchPacienteData(id)
    }
  }, [id])

  useEffect(() => {
    return () => {
      stopCamera()
    }
  }, [])

  const fetchPacienteData = async (pacienteId: string) => {
    try {
      const [pacienteRes, consultasRes] = await Promise.all([
        api.get(`/pacientes/${pacienteId}`),
        api.get(`/consultas/paciente/${pacienteId}`),
      ])
      setPaciente(pacienteRes.data)
      setConsultas(consultasRes.data)
      if (pacienteRes.data?.foto_url) {
        setPhotoPreview(pacienteRes.data.foto_url)
      }
    } catch (error) {
      console.error('Error fetching paciente:', error)
    } finally {
      setLoading(false)
    }
  }

  const orderedConsultas = useMemo(() => {
    return [...consultas].sort(
      (a, b) => new Date(b.fecha_hora).getTime() - new Date(a.fecha_hora).getTime()
    )
  }, [consultas])

  const latestConsulta = orderedConsultas[0]

  const featuredStats = useMemo(
    () => [
      {
        label: 'Edad',
        value: paciente ? `${calculateAge(paciente.fecha_nacimiento)} años` : '—',
      },
      {
        label: 'Tipo de sangre',
        value: paciente?.tipo_sangre || 'Sin registro',
      },
      {
        label: 'Última consulta',
        value: latestConsulta ? formatDateTime(latestConsulta.fecha_hora) : 'Sin historial',
      },
      {
        label: 'Alergias registradas',
        value: paciente?.alergias?.length
          ? `${paciente.alergias.length} ${paciente.alergias.length === 1 ? 'registro' : 'registros'}`
          : 'Sin alergias',
      },
    ],
    [paciente, latestConsulta]
  )

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop())
      streamRef.current = null
    }
    setIsCameraActive(false)
  }

  const startCamera = async () => {
    if (isCameraActive) return
    if (!navigator.mediaDevices?.getUserMedia) {
      setCameraError('La cámara no está disponible en este dispositivo')
      return
    }

    try {
      setCameraError(null)
      const stream = await navigator.mediaDevices.getUserMedia({ video: true })
      streamRef.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }
      setIsCameraActive(true)
    } catch (error) {
      console.error(error)
      setCameraError('No pudimos acceder a la cámara. Verifica los permisos del navegador.')
    }
  }

  const capturePhoto = () => {
    const video = videoRef.current
    if (!video) return

    const canvas = document.createElement('canvas')
    canvas.width = video.videoWidth || 640
    canvas.height = video.videoHeight || 480
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
    const dataUrl = canvas.toDataURL('image/png')
    setPhotoPreview(dataUrl)
    stopCamera()
  }

  const handlePhotoUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      setPhotoPreview(reader.result as string)
    }
    reader.readAsDataURL(file)
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Cargando información del paciente...</p>
      </div>
    )
  }

  if (!paciente) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Paciente no encontrado</p>
        <Link to="/pacientes" className="btn btn-primary mt-4">
          Volver a pacientes
        </Link>
      </div>
    )
  }

  const displayPhoto = photoPreview
  const contactoEmergencia = paciente.contacto_emergencia_nombre
    ? `${paciente.contacto_emergencia_nombre} ${
        paciente.contacto_emergencia_telefono ? `· ${paciente.contacto_emergencia_telefono}` : ''
      }`
    : 'Sin registro'

  return (
    <div className="space-y-8">
      <Link
        to="/pacientes"
        className="inline-flex items-center text-sm font-semibold text-indigo-600 transition hover:text-indigo-500"
      >
        <ArrowLeft size={18} className="mr-2" /> Volver a pacientes
      </Link>

      <section className="relative overflow-hidden rounded-4xl bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-900 p-8 text-white shadow-2xl">
        <div className="absolute inset-y-0 right-0 w-1/2 translate-x-1/3 bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.15),_transparent_55%)]" />
        <div className="relative z-10 grid gap-10 lg:grid-cols-[auto,1fr] xl:grid-cols-[auto,1fr,1fr]">
          <div className="flex flex-col items-center gap-4">
            <div className="relative h-32 w-32 overflow-hidden rounded-3xl border border-white/20 bg-white/10 backdrop-blur">
              {displayPhoto ? (
                <img src={displayPhoto} alt={paciente.nombre_completo} className="h-full w-full object-cover" />
              ) : (
                <div className="flex h-full w-full items-center justify-center">
                  <User className="h-16 w-16 text-white/70" />
                </div>
              )}
            </div>
            <div className="flex flex-wrap justify-center gap-3 text-xs font-medium">
              <label className="inline-flex cursor-pointer items-center rounded-full border border-white/30 bg-white/10 px-4 py-2 backdrop-blur transition hover:bg-white/20">
                <Upload size={14} className="mr-2" /> Cargar foto
                <input type="file" className="hidden" accept="image/*" onChange={handlePhotoUpload} />
              </label>
              <button
                type="button"
                onClick={isCameraActive ? stopCamera : startCamera}
                className="inline-flex items-center rounded-full border border-white/30 bg-white/10 px-4 py-2 backdrop-blur transition hover:bg-white/20"
              >
                <Camera size={14} className="mr-2" /> {isCameraActive ? 'Cerrar cámara' : 'Tomar foto'}
              </button>
            </div>
            {isCameraActive && (
              <div className="w-full rounded-2xl border border-white/10 bg-black/40 p-4 backdrop-blur">
                <video ref={videoRef} autoPlay playsInline className="h-48 w-full rounded-xl object-cover" />
                <div className="mt-3 flex gap-3 text-sm">
                  <button
                    type="button"
                    onClick={capturePhoto}
                    className="flex-1 rounded-xl bg-emerald-500 px-4 py-2 font-semibold text-white shadow-lg shadow-emerald-500/30 transition hover:bg-emerald-400"
                  >
                    Capturar
                  </button>
                  <button
                    type="button"
                    onClick={stopCamera}
                    className="flex-1 rounded-xl bg-white/10 px-4 py-2 font-semibold text-white/90 backdrop-blur transition hover:bg-white/20"
                  >
                    Cancelar
                  </button>
                </div>
                {cameraError && <p className="mt-2 text-xs text-rose-200">{cameraError}</p>}
              </div>
            )}
          </div>

          <div className="space-y-4">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-white/60">Expediente #{paciente.numero_expediente}</p>
              <h1 className="mt-2 text-3xl font-bold tracking-tight">{paciente.nombre_completo}</h1>
              <p className="mt-2 text-sm text-white/80">
                Paciente registrado desde {new Date(paciente.created_at).toLocaleDateString('es-MX', { month: 'long', year: 'numeric' })}
              </p>
            </div>
            <div className="flex flex-wrap gap-2 text-xs">
              {paciente.genero && <span className="rounded-full bg-white/10 px-3 py-1 capitalize text-white/80">{paciente.genero}</span>}
              {paciente.tipo_sangre && <span className="rounded-full bg-white/10 px-3 py-1">{paciente.tipo_sangre}</span>}
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            {featuredStats.map((stat) => (
              <div key={stat.label} className="rounded-2xl border border-white/15 bg-white/5 p-4 backdrop-blur">
                <p className="text-xs uppercase tracking-wide text-white/60">{stat.label}</p>
                <p className="mt-2 text-xl font-semibold">{stat.value}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <div className="space-y-6">
        <div className="grid gap-6 xl:grid-cols-[320px,1fr]">
          <div className="rounded-3xl border border-slate-100 bg-white/90 p-6 shadow-lg">
            <h3 className="text-sm font-semibold text-slate-500">Información de contacto</h3>
            <div className="mt-4 space-y-4 text-sm">
              <div className="flex items-center gap-3">
                <div className="rounded-2xl bg-slate-100 p-2 text-slate-500">
                  <Phone size={16} />
                </div>
                <div>
                  <p className="text-xs uppercase text-slate-400">Teléfono</p>
                  <p className="font-medium text-slate-900">{paciente.telefono || 'Sin registro'}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="rounded-2xl bg-slate-100 p-2 text-slate-500">
                  <Mail size={16} />
                </div>
                <div>
                  <p className="text-xs uppercase text-slate-400">Correo electrónico</p>
                  <p className="font-medium text-slate-900">{paciente.email || 'Sin registro'}</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="rounded-2xl bg-rose-50 p-2 text-rose-500">
                  <AlertCircle size={16} />
                </div>
                <div>
                  <p className="text-xs uppercase text-slate-400">Alergias</p>
                  {paciente.alergias?.length ? (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {paciente.alergias.map((alergia) => (
                        <span key={alergia} className="rounded-full bg-rose-50 px-3 py-1 text-xs font-medium text-rose-600">
                          {alergia}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="font-medium text-slate-900">Sin alergias registradas</p>
                  )}
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="rounded-2xl bg-slate-100 p-2 text-slate-500">
                  <Activity size={16} />
                </div>
                <div>
                  <p className="text-xs uppercase text-slate-400">Contacto de emergencia</p>
                  <p className="font-medium text-slate-900">{contactoEmergencia}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-4xl border border-slate-100 bg-white/90 p-6 shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-slate-900">Acciones rápidas</h3>
                <p className="text-sm text-slate-500">Atajos operativos del expediente</p>
              </div>
              <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">Tablero</span>
            </div>
            <div className="mt-5 grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
              <LinkAction to={`/expediente/${paciente.id}`} icon={FileText} label="Expediente Clínico" gradient="from-sky-500 to-cyan-400" />
              <LinkAction
                to={`/historia-clinica/${paciente.id}`}
                icon={FileText}
                label="Historia Clínica Pediátrica"
                gradient="from-fuchsia-500 to-pink-500"
              />
              <LinkAction to={`/imagenes/${paciente.id}`} icon={Image} label="Galería de Imágenes" gradient="from-indigo-500 to-purple-500" />
              <LinkAction to={`/laboratorios/${paciente.id}`} icon={FlaskConical} label="Laboratorio Clínico" gradient="from-emerald-500 to-teal-500" />
              <LinkAction to={`/estudios-especiales/${paciente.id}`} icon={Heart} label="Estudios Especiales" gradient="from-rose-500 to-red-500" />
              <ActionTile onClick={() => setDiagnosticoSugeridoOpen(true)} gradient="from-purple-600 to-violet-600" label="Diagnóstico sugerido" icon={Brain} />
              <LinkAction
                to={`/cumplimiento`}
                state={{ pacienteId: paciente.id }}
                icon={Shield}
                label="Cumplimiento Normativo"
                gradient="from-blue-600 to-indigo-600"
              />
              <Link
                to={`/consultas/nueva/${paciente.id}`}
                className="flex h-36 items-center justify-center gap-2 rounded-3xl border border-dashed border-slate-300 px-4 py-3 font-semibold text-slate-600 transition hover:border-indigo-200 hover:bg-indigo-50"
              >
                <Plus size={18} /> Nueva consulta
              </Link>
            </div>
          </div>
        </div>

        <div className="rounded-4xl border border-slate-100 bg-white/95 p-6 shadow-xl">
...
        </div>
      </div>

      {paciente && diagnosticoSugeridoOpen && (
        <DiagnosticoSugerido
          pacienteId={paciente.id}
          onClose={() => setDiagnosticoSugeridoOpen(false)}
        />
      )}


    </div>
  )
}

const LinkAction = ({
  to,
  icon: Icon,
  label,
  gradient,
  state,
}: {
  to: string
  icon: typeof FileText
  label: string
  gradient: string
  state?: Record<string, unknown>
}) => (
  <Link
    to={to}
    state={state}
    className="flex h-36 items-center rounded-3xl border border-slate-100 bg-white px-5 shadow-sm transition hover:-translate-y-1 hover:border-indigo-200 hover:shadow-xl"
  >
    <div className="flex items-center gap-4">
      <span
        className={`inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-r ${gradient} text-white shadow-inner`}
      >
        <Icon size={18} />
      </span>
      <div>
        <p className="text-base font-semibold text-slate-900">{label}</p>
        <p className="text-xs text-slate-400">Acceder</p>
      </div>
    </div>
  </Link>
)

const ActionTile = ({
  onClick,
  icon: Icon,
  label,
  gradient,
}: {
  onClick: () => void
  icon: typeof FileText
  label: string
  gradient: string
}) => (
  <button
    onClick={onClick}
    className="flex h-36 w-full items-center rounded-3xl border border-slate-100 bg-white px-5 shadow-sm transition hover:-translate-y-1 hover:border-indigo-200 hover:shadow-xl"
  >
    <div className="flex items-center gap-4">
      <span
        className={`inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-r ${gradient} text-white shadow-inner`}
      >
        <Icon size={18} />
      </span>
      <div>
        <p className="text-base font-semibold text-slate-900">{label}</p>
        <p className="text-xs text-slate-400">Acceder</p>
      </div>
    </div>
  </button>
)

const statusBadgeClasses = (estado: Consulta['estado']) => {
  switch (estado) {
    case 'completada':
      return 'rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-600'
    case 'hospitalizado':
      return 'rounded-full bg-rose-50 px-3 py-1 text-xs font-semibold text-rose-600'
    case 'en_proceso':
      return 'rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-600'
    default:
      return 'rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-600'
  }
}

export default PacienteDetalle
