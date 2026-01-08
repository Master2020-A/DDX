import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Search, User, X } from 'lucide-react'
import api from '@/lib/api'
import { Paciente } from '@/types'
import { calculateAge } from '@/lib/utils'
import CodigoPostalInput from '@/components/CodigoPostalInput'

const COUNTRY_DIAL_PRESETS: Record<string, { dial: string; defaultArea?: string }> = {
  MX: { dial: '+52' },
  US: { dial: '+1' },
  CA: { dial: '+1' },
  CO: { dial: '+57' },
  AR: { dial: '+54' },
  ES: { dial: '+34' },
  CL: { dial: '+56' },
  PE: { dial: '+51' },
}
const DEFAULT_DIAL_PRESET = { dial: '+52' }

const detectUserDialPreset = () => {
  if (typeof window === 'undefined') return DEFAULT_DIAL_PRESET
  const resolved = Intl.DateTimeFormat().resolvedOptions().locale
  const fallback = typeof navigator !== 'undefined' ? navigator.language : 'es-MX'
  const locale = resolved || fallback || 'es-MX'
  const region = locale.split('-')[1]?.toUpperCase()
  return (region && COUNTRY_DIAL_PRESETS[region]) || DEFAULT_DIAL_PRESET
}

const formatISOToMask = (iso: string) => {
  if (!iso) return ''
  const [year, month, day] = iso.split('-')
  if (!year || !month || !day) return ''
  return `${day}/${month}/${year}`
}

const formatMaskToISO = (digits: string) => {
  if (digits.length !== 8) return ''
  const day = digits.slice(0, 2)
  const month = digits.slice(2, 4)
  const year = digits.slice(4)
  return `${year}-${month}-${day}`
}

const Pacientes = () => {
  const [pacientes, setPacientes] = useState<Paciente[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [showModal, setShowModal] = useState(false)

  useEffect(() => {
    fetchPacientes()
  }, [])

  const fetchPacientes = async () => {
    try {
      const response = await api.get('/pacientes/')
      setPacientes(response.data)
    } catch (error) {
      console.error('Error fetching pacientes:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredPacientes = pacientes.filter((p) =>
    p.nombre_completo.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.numero_expediente.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const totalPacientes = pacientes.length
  const pacientesConTelefono = pacientes.filter((p) => Boolean(p.telefono)).length
  const pacientesMenores = pacientes.filter((p) =>
    p.fecha_nacimiento ? calculateAge(p.fecha_nacimiento) < 18 : false
  ).length
  const gruposSanguineos = new Set(
    pacientes.map((p) => p.tipo_sangre).filter(Boolean) as string[]
  ).size

  const heroMetrics = [
    { label: 'Pacientes activos', value: totalPacientes },
    { label: 'Contacto directo', value: pacientesConTelefono },
    { label: 'Menores de edad', value: pacientesMenores },
    { label: 'Grupos sanguíneos', value: gruposSanguineos },
  ]

  const getInitials = (fullName: string) => {
    if (!fullName) return 'P'
    return fullName
      .split(' ')
      .filter(Boolean)
      .slice(0, 2)
      .map((word) => word[0])
      .join('')
      .toUpperCase()
  }

  const renderPatientBadge = (text?: string | null) => (
    <span className="inline-flex items-center rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-600">
      {text || '—'}
    </span>
  )

  return (
    <div className="space-y-8">
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-indigo-600 via-sky-500 to-cyan-400 p-8 shadow-2xl">
        <div className="relative z-10 flex flex-col gap-8 lg:flex-row lg:items-center">
          <div className="flex-1 text-white">
            <p className="uppercase text-xs tracking-[0.35em] text-white/70">Panel clínico</p>
            <h1 className="mt-3 text-4xl font-extrabold leading-tight">
              Pacientes
            </h1>
            <p className="mt-2 max-w-2xl text-base text-white/85">
              Monitorea tu base de pacientes con un resumen ejecutivo, accesos directos
              y fichas enriquecidas para priorizar la atención.
            </p>
            <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {heroMetrics.map((metric) => (
                <div
                  key={metric.label}
                  className="rounded-2xl bg-white/10 p-4 backdrop-blur ring-1 ring-white/20"
                >
                  <span className="text-xs uppercase tracking-wide text-white/60">
                    {metric.label}
                  </span>
                  <p className="mt-2 text-2xl font-semibold">{metric.value}</p>
                </div>
              ))}
            </div>
          </div>
          <div className="flex flex-shrink-0 items-start gap-3 lg:flex-col">
            <button
              onClick={() => setShowModal(true)}
              className="inline-flex items-center justify-center rounded-2xl border border-white/30 bg-white/10 px-6 py-3 text-white shadow-lg shadow-black/10 backdrop-blur transition hover:bg-white/15"
            >
              <Plus className="mr-2" size={20} />
              Nuevo Paciente
            </button>
          </div>
        </div>
        <div className="absolute inset-y-0 right-0 hidden w-1/3 translate-x-12 overflow-hidden opacity-40 lg:block">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.4),_transparent_60%)]" />
          <div className="absolute -bottom-10 right-10 h-48 w-48 rounded-full bg-white/20 blur-3xl" />
        </div>
      </section>

      <div className="rounded-2xl border border-slate-100 bg-white/70 p-1 shadow-sm">
        <div className="flex flex-col gap-4 rounded-2xl bg-white/80 p-6 lg:flex-row lg:items-center">
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Busca por nombre, expediente o contacto"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full rounded-2xl border border-slate-200 bg-slate-50/70 py-3 pl-12 pr-4 text-sm text-slate-700 placeholder:text-slate-400 focus:border-indigo-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
            />
          </div>
          <div className="flex gap-2 text-xs text-slate-500">
            <span className="rounded-full border border-slate-200 px-4 py-2">
              {filteredPacientes.length} resultados
            </span>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="rounded-2xl border border-slate-100 bg-white p-12 text-center shadow-sm">
          <p className="text-slate-500">Cargando pacientes...</p>
        </div>
      ) : filteredPacientes.length === 0 ? (
        <div className="rounded-3xl border border-dashed border-slate-200 bg-white/70 p-12 text-center shadow-sm">
          <User className="mx-auto mb-4 text-slate-300" size={48} />
          <p className="text-lg font-semibold text-slate-700">No hay pacientes registrados</p>
          <p className="mt-2 text-sm text-slate-500">
            Registra el primer paciente para comenzar a construir el expediente digital.
          </p>
          <button
            onClick={() => setShowModal(true)}
            className="btn btn-primary mt-6"
          >
            Registrar paciente
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
          {filteredPacientes.map((paciente) => {
            const edad = paciente.fecha_nacimiento
              ? `${calculateAge(paciente.fecha_nacimiento)} años`
              : 'Edad n/d'

            return (
              <Link
                key={paciente.id}
                to={`/pacientes/${paciente.id}`}
                className="group relative overflow-hidden rounded-3xl border border-slate-100 bg-white/90 p-6 shadow-sm ring-1 ring-transparent transition hover:-translate-y-1 hover:border-indigo-100 hover:shadow-2xl hover:ring-indigo-100"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500/15 to-cyan-400/20 text-lg font-semibold text-indigo-700">
                      {getInitials(paciente.nombre_completo)}
                    </div>
                    <div>
                      <p className="font-semibold text-slate-900 group-hover:text-indigo-600">
                        {paciente.nombre_completo}
                      </p>
                      <p className="text-xs uppercase tracking-wide text-slate-400">
                        {paciente.numero_expediente}
                      </p>
                    </div>
                  </div>
                  {paciente.tipo_sangre && renderPatientBadge(paciente.tipo_sangre)}
                </div>

                <div className="mt-6 grid gap-3 text-sm text-slate-600">
                  <div className="flex items-center justify-between border-b border-dashed border-slate-200 pb-2">
                    <span className="text-slate-400">Edad</span>
                    <span className="font-medium text-slate-900">{edad}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Tipo de sangre</span>
                    <span className="font-medium">
                      {paciente.tipo_sangre || 'Sin registro'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Contacto</span>
                    <span className="font-medium">
                      {paciente.telefono || 'No disponible'}
                    </span>
                  </div>
                </div>

                <div className="mt-6 flex items-center justify-between text-xs text-slate-400">
                  <span>Ver expediente</span>
                  <span className="text-indigo-500">Detalles →</span>
                </div>
              </Link>
            )
          })}
        </div>
      )}

      {showModal && (
        <NuevoPacienteModal
          onClose={() => setShowModal(false)}
          onSuccess={() => {
            setShowModal(false)
            fetchPacientes()
          }}
        />
      )}
    </div>
  )
}

const NuevoPacienteModal = ({ onClose, onSuccess }: { onClose: () => void; onSuccess: () => void }) => {
  const [formData, setFormData] = useState({
    nombre_completo: '',
    fecha_nacimiento: '',
    genero: '',
    tipo_sangre: '',
    codigo_pais: '+52',
    lada: '',
    telefono: '',
    email: '',
    codigo_postal: '',
    estado: '',
    municipio: '',
    ciudad: '',
    colonia: '',
    calle: '',
    numero_exterior: '',
    numero_interior: '',
    contacto_emergencia_nombre: '',
    contacto_codigo_pais: '+52',
    contacto_lada: '',
    contacto_numero: '',
    alergias: '',
  })
  const [fechaInput, setFechaInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [errors, setErrors] = useState<{[key: string]: string}>({})
  const [coloniasDisponibles, setColoniasDisponibles] = useState<string[]>([])

  useEffect(() => {
    const preset = detectUserDialPreset()
    setFormData(prev => ({
      ...prev,
      codigo_pais: prev.codigo_pais || preset.dial,
      lada: prev.lada || preset.defaultArea || '',
      contacto_codigo_pais: prev.contacto_codigo_pais || preset.dial,
      contacto_lada: prev.contacto_lada || preset.defaultArea || '',
    }))
  }, [])

  useEffect(() => {
    if (formData.fecha_nacimiento) {
      setFechaInput(formatISOToMask(formData.fecha_nacimiento))
    }
  }, [formData.fecha_nacimiento])

  const handleFechaInputChange = (value: string) => {
    const digits = value.replace(/\D/g, '').slice(0, 8)
    let formatted = digits
    if (digits.length >= 5) {
      formatted = `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4)}`
    } else if (digits.length >= 3) {
      formatted = `${digits.slice(0, 2)}/${digits.slice(2)}`
    }
    setFechaInput(formatted)
    const iso = formatMaskToISO(digits)
    setFormData(prev => ({ ...prev, fecha_nacimiento: iso }))
  }

  const validateForm = () => {
    const newErrors: {[key: string]: string} = {}
    
    // Validar nombre
    if (!formData.nombre_completo.trim()) {
      newErrors.nombre_completo = 'El nombre es requerido'
    } else if (formData.nombre_completo.trim().length < 3) {
      newErrors.nombre_completo = 'El nombre debe tener al menos 3 caracteres'
    }
    
    // Validar fecha de nacimiento
    if (!formData.fecha_nacimiento) {
      newErrors.fecha_nacimiento = 'La fecha de nacimiento es requerida'
    } else {
      const fechaNac = new Date(formData.fecha_nacimiento)
      const hoy = new Date()
      if (fechaNac > hoy) {
        newErrors.fecha_nacimiento = 'La fecha no puede ser futura'
      }
    }
    
    // Validar email si está presente
    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Email inválido'
    }
    
    // Validar teléfono si está presente
    if (formData.telefono && formData.telefono.length < 10) {
      newErrors.telefono = 'El teléfono debe tener al menos 10 dígitos'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }
    
    setLoading(true)
    setError('')

    try {
      // Construir teléfono completo
      const telefonoCompleto = formData.telefono 
        ? `${formData.codigo_pais} (${formData.lada}) ${formData.telefono}`
        : ''

      const telefonoEmergencia = formData.contacto_numero
        ? `${formData.contacto_codigo_pais} (${formData.contacto_lada}) ${formData.contacto_numero}`
        : ''
      
      // Construir dirección completa
      const direccionCompleta = [
        formData.calle,
        formData.numero_exterior && `#${formData.numero_exterior}`,
        formData.numero_interior && `Int. ${formData.numero_interior}`,
        formData.colonia,
        formData.ciudad,
        formData.municipio,
        formData.estado,
        formData.codigo_postal && `C.P. ${formData.codigo_postal}`
      ].filter(Boolean).join(', ')
      
      const data = {
        nombre_completo: formData.nombre_completo.trim(),
        fecha_nacimiento: formData.fecha_nacimiento,
        genero: formData.genero || undefined,
        tipo_sangre: formData.tipo_sangre || undefined,
        telefono: telefonoCompleto || undefined,
        email: formData.email || undefined,
        direccion: direccionCompleta || undefined,
        contacto_emergencia_nombre: formData.contacto_emergencia_nombre || undefined,
        contacto_emergencia_telefono: telefonoEmergencia || undefined,
        alergias: formData.alergias ? formData.alergias.split(',').map(a => a.trim()) : [],
      }
      
      await api.post('/pacientes/', data)
      onSuccess()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al crear paciente')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">Nuevo Paciente</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600" title="Cerrar" aria-label="Cerrar modal">
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Nombre completo *</label>
              <input
                type="text"
                value={formData.nombre_completo}
                onChange={(e) => setFormData({ ...formData, nombre_completo: e.target.value })}
                className={`input ${errors.nombre_completo ? 'border-red-500' : ''}`}
                placeholder="Nombre completo del paciente"
                required
              />
              {errors.nombre_completo && <p className="text-red-500 text-sm mt-1">{errors.nombre_completo}</p>}
            </div>

            <div>
              <label className="label">Fecha de nacimiento *</label>
              <input
                type="text"
                inputMode="numeric"
                placeholder="dd/mm/aaaa"
                value={fechaInput}
                onChange={(e) => handleFechaInputChange(e.target.value)}
                className={`input ${errors.fecha_nacimiento ? 'border-red-500' : ''}`}
                maxLength={10}
                required
              />
              {errors.fecha_nacimiento && <p className="text-red-500 text-sm mt-1">{errors.fecha_nacimiento}</p>}
            </div>

            <div>
              <label className="label">Género</label>
              <select
                value={formData.genero}
                onChange={(e) => setFormData({ ...formData, genero: e.target.value })}
                className="input"
              >
                <option value="">Seleccionar</option>
                <option value="masculino">Masculino</option>
                <option value="femenino">Femenino</option>
                <option value="otro">Otro</option>
                <option value="no_especifica">Prefiero no especificar</option>
              </select>
            </div>

            <div>
              <label className="label">Tipo de sangre</label>
              <select
                value={formData.tipo_sangre}
                onChange={(e) => setFormData({ ...formData, tipo_sangre: e.target.value })}
                className="input"
              >
                <option value="">Seleccionar</option>
                <option value="A+">A+</option>
                <option value="A-">A-</option>
                <option value="B+">B+</option>
                <option value="B-">B-</option>
                <option value="AB+">AB+</option>
                <option value="AB-">AB-</option>
                <option value="O+">O+</option>
                <option value="O-">O-</option>
              </select>
            </div>

            <div>
              <label className="label">Teléfono</label>
              <div className="grid grid-cols-12 gap-2">
                <input
                  type="text"
                  value={formData.codigo_pais}
                  onChange={(e) => setFormData({ ...formData, codigo_pais: e.target.value })}
                  className="input col-span-2"
                  placeholder="+52"
                />
                <input
                  type="tel"
                  value={formData.lada}
                  onChange={(e) => setFormData({ ...formData, lada: e.target.value.replace(/\D/g, '').slice(0, 3) })}
                  className="input col-span-3"
                  placeholder="LADA"
                  maxLength={3}
                />
                <input
                  type="tel"
                  value={formData.telefono}
                  onChange={(e) => setFormData({ ...formData, telefono: e.target.value.replace(/\D/g, '').slice(0, 10) })}
                  className={`input col-span-7 ${errors.telefono ? 'border-red-500' : ''}`}
                  placeholder="Número telefónico"
                  maxLength={10}
                />
              </div>
              {errors.telefono && <p className="text-red-500 text-sm mt-1">{errors.telefono}</p>}
              <p className="text-xs text-gray-500 mt-1">Formato: +52 (LADA) Número</p>
            </div>

            <div>
              <label className="label">Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className={`input ${errors.email ? 'border-red-500' : ''}`}
                placeholder="correo@ejemplo.com"
              />
              {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
            </div>
          </div>

          {/* Sección de Dirección */}
          <div className="border-t pt-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Dirección</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Código Postal</label>
                <CodigoPostalInput
                  value={formData.codigo_postal}
                  onChange={(cp) => {
                    setColoniasDisponibles([])
                    setFormData(prev => ({
                      ...prev,
                      codigo_postal: cp,
                      estado: '',
                      municipio: '',
                      ciudad: '',
                      colonia: '',
                    }))
                  }}
                  onDataLoaded={(data) => {
                    const colonias = data.colonias && data.colonias.length > 0 ? data.colonias : [data.colonia || ''];
                    setColoniasDisponibles(colonias);

                    const primaryColonia = (colonias[0] || '').trim().toLowerCase();
                    const normalized = (value?: string | null) => value?.trim().toLowerCase() || '';

                    const fallbackMunicipio = data.estado || data.ciudad || '';
                    const calculatedMunicipio = !data.municipio || normalized(data.municipio) === primaryColonia
                      ? fallbackMunicipio
                      : data.municipio;

                    const fallbackCiudad = calculatedMunicipio || data.estado;
                    const calculatedCiudad = !data.ciudad || normalized(data.ciudad) === primaryColonia
                      ? fallbackCiudad
                      : data.ciudad;
                    
                    setFormData(prev => ({
                      ...prev,
                      codigo_postal: data.codigo_postal,
                      estado: data.estado,
                      municipio: calculatedMunicipio,
                      ciudad: calculatedCiudad,
                      colonia: colonias[0] || '',
                      codigo_pais: data.pais === 'México' ? '+52' : prev.codigo_pais,
                      contacto_codigo_pais:
                        data.pais === 'México' ? '+52' : prev.contacto_codigo_pais,
                    }))
                  }}
                />
              </div>
              
              <div>
                <label className="label">Estado</label>
                <input
                  type="text"
                  value={formData.estado}
                  onChange={(e) => setFormData({ ...formData, estado: e.target.value })}
                  className="input"
                  placeholder="Estado"
                  readOnly
                />
              </div>
              
              <div>
                <label className="label">Municipio</label>
                <input
                  type="text"
                  value={formData.municipio}
                  onChange={(e) => setFormData({ ...formData, municipio: e.target.value })}
                  className="input"
                  placeholder="Municipio"
                  readOnly
                />
              </div>
              
              <div>
                <label className="label">Ciudad</label>
                <input
                  type="text"
                  value={formData.ciudad}
                  onChange={(e) => setFormData({ ...formData, ciudad: e.target.value })}
                  className="input"
                  placeholder="Ciudad"
                />
              </div>
              
              <div>
                <label className="label">Colonia</label>
                {coloniasDisponibles.length > 0 ? (
                  <select
                    value={formData.colonia}
                    onChange={(e) => setFormData(prev => ({ ...prev, colonia: e.target.value }))}
                    className="input"
                  >
                    {coloniasDisponibles.map((colonia, index) => (
                      <option key={index} value={colonia}>
                        {colonia}
                      </option>
                    ))}
                  </select>
                ) : (
                  <input
                    type="text"
                    value={formData.colonia}
                    onChange={(e) => setFormData(prev => ({ ...prev, colonia: e.target.value }))}
                    className="input"
                    placeholder="Colonia"
                  />
                )}
              </div>
              
              <div>
                <label className="label">Calle</label>
                <input
                  type="text"
                  value={formData.calle}
                  onChange={(e) => setFormData({ ...formData, calle: e.target.value })}
                  className="input"
                  placeholder="Nombre de la calle"
                />
              </div>
              
              <div>
                <label className="label">Número exterior</label>
                <input
                  type="text"
                  value={formData.numero_exterior}
                  onChange={(e) => setFormData({ ...formData, numero_exterior: e.target.value })}
                  className="input"
                  placeholder="Núm. exterior"
                />
              </div>
              
              <div>
                <label className="label">Número interior</label>
                <input
                  type="text"
                  value={formData.numero_interior}
                  onChange={(e) => setFormData({ ...formData, numero_interior: e.target.value })}
                  className="input"
                  placeholder="Núm. interior (opcional)"
                />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Contacto de emergencia</label>
              <input
                type="text"
                value={formData.contacto_emergencia_nombre}
                onChange={(e) => setFormData({ ...formData, contacto_emergencia_nombre: e.target.value })}
                className="input"
                placeholder="Nombre"
              />
            </div>

            <div>
              <label className="label">Teléfono de emergencia</label>
              <div className="grid grid-cols-12 gap-2">
                <input
                  type="text"
                  value={formData.contacto_codigo_pais}
                  onChange={(e) => setFormData({ ...formData, contacto_codigo_pais: e.target.value })}
                  className="input col-span-2"
                  placeholder="+52"
                />
                <input
                  type="tel"
                  value={formData.contacto_lada}
                  onChange={(e) => setFormData({ ...formData, contacto_lada: e.target.value.replace(/\D/g, '').slice(0, 3) })}
                  className="input col-span-3"
                  placeholder="LADA"
                  maxLength={3}
                />
                <input
                  type="tel"
                  value={formData.contacto_numero}
                  onChange={(e) => setFormData({ ...formData, contacto_numero: e.target.value.replace(/\D/g, '').slice(0, 10) })}
                  className="input col-span-7"
                  placeholder="Número telefónico"
                  maxLength={10}
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">Formato: +52 (LADA) Número</p>
            </div>
          </div>

          <div>
            <label className="label">Alergias (separadas por coma)</label>
            <input
              type="text"
              value={formData.alergias}
              onChange={(e) => setFormData({ ...formData, alergias: e.target.value })}
              className="input"
              placeholder="Penicilina, Polen, etc."
            />
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button type="button" onClick={onClose} className="btn btn-secondary">
              Cancelar
            </button>
            <button type="submit" disabled={loading} className="btn btn-primary">
              {loading ? 'Guardando...' : 'Guardar Paciente'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default Pacientes
