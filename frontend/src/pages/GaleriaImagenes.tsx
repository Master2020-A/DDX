import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { 
  Upload, Image as ImageIcon, Filter, Grid3x3, List, 
  Download, Trash2, Eye, Sparkles, ZoomIn, Copy, FileText,
  Calendar, User, Activity, AlertCircle, FileImage, MapPin, 
  Navigation, AlignLeft, X, Check, Stethoscope, Scan
} from 'lucide-react'
import api from '@/lib/api'
import PatientWorkspaceLayout, { WorkspaceMetric } from '@/components/patient/PatientWorkspaceLayout'

interface ImagenMedica {
  id: string
  paciente_id: string
  titulo: string
  descripcion?: string
  tipo_imagen: string
  region_anatomica?: string
  tipo_archivo: string
  tamanio_bytes: number
  ancho?: number
  alto?: number
  analisis_ia_completado: boolean
  hallazgos?: string[]
  confianza_ia?: number
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

interface Paciente {
  id: string
  nombre_completo: string
  numero_expediente: string
}

interface GaleriaData {
  total: number
  imagenes: ImagenMedica[]
  por_tipo: Record<string, number>
  por_region: Record<string, number>
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

const GaleriaImagenes = () => {
  const { pacienteId } = useParams<{ pacienteId: string }>()
  const navigate = useNavigate()

  const [paciente, setPaciente] = useState<Paciente | null>(null)
  const [galeria, setGaleria] = useState<GaleriaData | null>(null)
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [vistaGrid, setVistaGrid] = useState(true)
  
  // Filtros
  const [filtroTipo, setFiltroTipo] = useState<string>('')
  const [filtroRegion, setFiltroRegion] = useState<string>('')
  
  // Modal de subir imagen
  const [modalSubir, setModalSubir] = useState(false)
  const [archivoSeleccionado, setArchivoSeleccionado] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    titulo: '',
    descripcion: '',
    tipo_imagen: 'rayos_x',
    region_anatomica: '',
    lateralidad: ''
  })

  // Estado de análisis IA en progreso
  const [analisisEnProgreso, setAnalisisEnProgreso] = useState<Set<string>>(new Set())
  
  // Estado de selección para comparar
  const [modoComparar, setModoComparar] = useState(false)
  const [imagenesSeleccionadas, setImagenesSeleccionadas] = useState<string[]>([])

  useEffect(() => {
    if (pacienteId) {
      cargarDatos()
    }
  }, [pacienteId, filtroTipo, filtroRegion])

  const cargarDatos = async () => {
    try {
      setLoading(true)
      
      // Cargar datos del paciente
      const resPaciente = await api.get(`/pacientes/${pacienteId}`)
      setPaciente(resPaciente.data)
      
      // Cargar galería de imágenes
      const params: any = {}
      if (filtroTipo) params.tipo_imagen = filtroTipo
      if (filtroRegion) params.region_anatomica = filtroRegion
      
      const resGaleria = await api.get(`/imagenes/paciente/${pacienteId}`, { params })
      setGaleria(resGaleria.data)
    } catch (error) {
      console.error('Error cargando datos:', error)
      alert('Error al cargar los datos')
    } finally {
      setLoading(false)
    }
  }

  const handleSubirImagen = async () => {
    if (!archivoSeleccionado) {
      alert('Selecciona una imagen')
      return
    }

    if (!formData.titulo) {
      alert('Ingresa un título para la imagen')
      return
    }

    try {
      setUploading(true)

      const formDataUpload = new FormData()
      formDataUpload.append('archivo', archivoSeleccionado)
      formDataUpload.append('paciente_id', pacienteId || '')
      formDataUpload.append('titulo', formData.titulo)
      formDataUpload.append('tipo_imagen', formData.tipo_imagen)
      if (formData.descripcion) formDataUpload.append('descripcion', formData.descripcion)
      if (formData.region_anatomica) formDataUpload.append('region_anatomica', formData.region_anatomica)
      if (formData.lateralidad) formDataUpload.append('lateralidad', formData.lateralidad)

      await api.post('/imagenes/upload', formDataUpload, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      alert('Imagen subida exitosamente')
      setModalSubir(false)
      resetFormulario()
      cargarDatos()
    } catch (error) {
      console.error('Error subiendo imagen:', error)
      alert('Error al subir la imagen')
    } finally {
      setUploading(false)
    }
  }

  const resetFormulario = () => {
    setArchivoSeleccionado(null)
    setFormData({
      titulo: '',
      descripcion: '',
      tipo_imagen: 'rayos_x',
      region_anatomica: '',
      lateralidad: ''
    })
  }

  const handleEliminarImagen = async (imagenId: string) => {
    if (!confirm('¿Estás seguro de eliminar esta imagen?')) return

    try {
      await api.delete(`/imagenes/${imagenId}`)
      alert('Imagen eliminada')
      cargarDatos()
    } catch (error) {
      console.error('Error eliminando imagen:', error)
      alert('Error al eliminar la imagen')
    }
  }

  const handleAnalisisIA = async (imagenId: string) => {
    // Agregar imagen al conjunto de análisis en progreso
    setAnalisisEnProgreso(prev => new Set([...prev, imagenId]))

    try {
      await api.post(`/imagenes/${imagenId}/analizar-ia`)
      alert('Análisis de IA completado')
      cargarDatos()
    } catch (error) {
      console.error('Error en análisis IA:', error)
      alert('Error al analizar la imagen')
    } finally {
      // Remover imagen del conjunto de análisis en progreso
      setAnalisisEnProgreso(prev => {
        const nuevoSet = new Set(prev)
        nuevoSet.delete(imagenId)
        return nuevoSet
      })
    }
  }

  const handleToggleSeleccion = (imagenId: string) => {
    setImagenesSeleccionadas(prev => {
      if (prev.includes(imagenId)) {
        return prev.filter(id => id !== imagenId)
      } else {
        if (prev.length >= 2) {
          // Solo permitir 2 imágenes seleccionadas
          return [prev[1], imagenId]
        }
        return [...prev, imagenId]
      }
    })
  }

  const handleComparar = () => {
    if (imagenesSeleccionadas.length === 2) {
      navigate(`/comparador/${imagenesSeleccionadas[0]}/${imagenesSeleccionadas[1]}`)
    } else {
      alert('Selecciona exactamente 2 imágenes para comparar')
    }
  }

  const handleCancelarComparacion = () => {
    setModoComparar(false)
    setImagenesSeleccionadas([])
  }

  const handleDescargarPDF = async (imagenId: string) => {
    try {
      const response = await api.get(`/imagenes/${imagenId}/reporte-pdf`, {
        responseType: 'blob',
        headers: {
          'Accept': 'application/pdf'
        }
      })

      // Verificar que la respuesta es válida
      if (!response.data || response.data.size === 0) {
        throw new Error('El PDF generado está vacío')
      }

      // Obtener nombre del archivo de los headers si está disponible
      let filename = `reporte_ia_${imagenId}.pdf`
      const contentDisposition = response.headers['content-disposition']
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '')
        }
      }

      // Crear URL para descarga
      const blob = new Blob([response.data], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      
      // Limpiar después de un pequeño delay para asegurar que la descarga comenzó
      setTimeout(() => {
        link.remove()
        window.URL.revokeObjectURL(url)
      }, 100)

      // Notificar éxito
      console.log('✅ PDF descargado exitosamente:', filename)

    } catch (error: any) {
      console.error('❌ Error descargando PDF:', error)
      
      // Solo mostrar alert si realmente hubo un error (no si la descarga fue exitosa)
      if (error.response?.status !== 200) {
        const mensaje = error.response?.data?.detail || error.message || 'Error al descargar el reporte PDF'
        alert(mensaje)
      }
    }
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  const getTipoImagenLabel = (tipo: string) => {
    const tipos: Record<string, string> = {
      'rayos_x': 'Rayos X',
      'tomografia': 'Tomografía',
      'resonancia': 'Resonancia Magnética',
      'ecografia': 'Ecografía',
      'fotografia': 'Fotografía Médica',
      'endoscopia': 'Endoscopia',
      'mamografia': 'Mamografía'
    }
    return tipos[tipo] || tipo
  }

  const cerrarModal = () => {
    setModalSubir(false)
    setArchivoSeleccionado(null)
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
      setPreviewUrl(null)
    }
    setFormData({
      titulo: '',
      descripcion: '',
      tipo_imagen: 'rayos_x',
      region_anatomica: '',
      lateralidad: ''
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando galería...</p>
        </div>
      </div>
    )
  }

  const totalImagenes = galeria?.total || 0
  const conIA = galeria?.imagenes.filter((img) => img.analisis_ia_completado).length || 0
  const tipos = Object.keys(galeria?.por_tipo || {}).length
  const regiones = Object.keys(galeria?.por_region || {}).length

  const metrics: WorkspaceMetric[] = [
    { label: 'Total activos', value: `${totalImagenes}`, tone: 'cyan' },
    { label: 'Analizados con IA', value: `${conIA}`, helper: `${Math.round((conIA / (totalImagenes || 1)) * 100)}%`, tone: 'violet' },
    { label: 'Tipos de estudios', value: `${tipos}`, tone: 'emerald' },
    { label: 'Regiones anatómicas', value: `${regiones}`, tone: 'amber' },
  ]

  const sidebar = paciente ? (
    <div className="space-y-4">
      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Información del paciente</h3>
        <p className="mt-2 text-base font-semibold text-slate-900">{paciente.nombre_completo}</p>
        <p className="text-sm text-slate-500">Expediente: {paciente.numero_expediente}</p>
        <div className="mt-4 space-y-2 text-sm text-slate-600">
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-slate-400" />
            Última captura {galeria?.imagenes?.[0]?.created_at ? new Date(galeria.imagenes[0].created_at).toLocaleDateString('es-MX') : '—'}
          </div>
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-slate-400" />
            {conIA} estudios con IA
          </div>
        </div>
      </div>
      <div className="rounded-3xl border border-slate-200 bg-slate-900 text-white p-6 shadow-lg">
        <p className="text-sm text-white/70">Modo actual</p>
        <p className="text-2xl font-semibold mt-1">{modoComparar ? 'Comparar imágenes' : 'Explorar galería'}</p>
        <p className="text-sm text-white/70 mt-2">
          {modoComparar
            ? 'Selecciona exactamente dos estudios para analizar diferencias con IA.'
            : 'Sube estudios, filtra resultados o activa el modo comparador.'}
        </p>
      </div>
    </div>
  ) : null

  const actions = (
    <div className="flex flex-col gap-3 sm:flex-row">
      {modoComparar ? (
        <>
          <button
            onClick={handleCancelarComparacion}
            className="inline-flex items-center gap-2 rounded-2xl bg-white/10 px-5 py-3 text-sm font-semibold text-white hover:bg-white/20"
          >
            <X className="h-4 w-4" /> Cancelar
          </button>
          <button
            onClick={handleComparar}
            disabled={imagenesSeleccionadas.length !== 2}
            className={`inline-flex items-center gap-2 rounded-2xl px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-emerald-500/30 transition ${
              imagenesSeleccionadas.length === 2
                ? 'bg-gradient-to-r from-emerald-500 to-green-500'
                : 'bg-white/10 text-white/60 cursor-not-allowed'
            }`}
          >
            <Copy className="h-4 w-4" /> Comparar ({imagenesSeleccionadas.length}/2)
          </button>
        </>
      ) : (
        <>
          <button
            onClick={() => setModoComparar(true)}
            className="inline-flex items-center gap-2 rounded-2xl bg-white/10 px-5 py-3 text-sm font-semibold text-white hover:bg-white/20"
          >
            <Copy className="h-4 w-4" /> Modo comparar
          </button>
          <button
            onClick={() => setModalSubir(true)}
            className="inline-flex items-center gap-2 rounded-2xl bg-white/10 px-5 py-3 text-sm font-semibold text-white hover:bg-white/20"
          >
            <Upload className="h-4 w-4" /> Subir imagen
          </button>
        </>
      )}
    </div>
  )

  return (
    <PatientWorkspaceLayout
      title="Galería de Imágenes"
      subtitle="Administra estudios diagnósticos, activa análisis IA y crea comparativas clínicas."
      breadcrumbs={[
        { label: 'Pacientes', to: '/pacientes' },
        { label: paciente?.nombre_completo || 'Galería' },
      ]}
      patient={{
        name: paciente?.nombre_completo,
        expediente: paciente?.numero_expediente,
        tags: [galeria?.total ? `${galeria.total} archivos` : undefined].filter(Boolean) as string[],
      }}
      metrics={metrics}
      actions={actions}
      sidebar={sidebar}
      heroAccent="cyan"
    >
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {[
          { label: 'Total de imágenes', value: totalImagenes, icon: ImageIcon },
          { label: 'Con análisis IA', value: conIA, icon: Sparkles },
          { label: 'Tipos de estudio', value: tipos, icon: Activity },
          { label: 'Regiones anatómicas', value: regiones, icon: Filter },
        ].map((stat) => (
          <div key={stat.label} className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500">{stat.label}</p>
                <p className="text-2xl font-semibold text-slate-900">{stat.value}</p>
              </div>
              <stat.icon className="h-8 w-8 text-indigo-500" />
            </div>
          </div>
        ))}
      </div>

      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-end gap-4">
          <div className="flex-1 min-w-[200px]">
            <label className="text-sm font-medium text-slate-600">Tipo de imagen</label>
            <select
              value={filtroTipo}
              onChange={(e) => setFiltroTipo(e.target.value)}
              className="mt-1 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
            >
              <option value="">Todos</option>
              {Object.keys(galeria?.por_tipo || {}).map((tipo) => (
                <option key={tipo} value={tipo}>
                  {getTipoImagenLabel(tipo)} ({galeria?.por_tipo[tipo]})
                </option>
              ))}
            </select>
          </div>

          <div className="flex-1 min-w-[200px]">
            <label className="text-sm font-medium text-slate-600">Región anatómica</label>
            <select
              value={filtroRegion}
              onChange={(e) => setFiltroRegion(e.target.value)}
              className="mt-1 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
            >
              <option value="">Todas</option>
              {Object.keys(galeria?.por_region || {}).map((region) => (
                <option key={region} value={region}>
                  {region.charAt(0).toUpperCase() + region.slice(1)} ({galeria?.por_region[region]})
                </option>
              ))}
            </select>
          </div>

          <div className="flex gap-2 rounded-2xl border border-slate-200 p-2">
            <button
              onClick={() => setVistaGrid(true)}
              className={`rounded-2xl px-4 py-3 text-sm font-semibold ${
                vistaGrid ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/30' : 'text-slate-500'
              }`}
            >
              <Grid3x3 size={18} />
            </button>
            <button
              onClick={() => setVistaGrid(false)}
              className={`rounded-2xl px-4 py-3 text-sm font-semibold ${
                !vistaGrid ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/30' : 'text-slate-500'
              }`}
            >
              <List size={18} />
            </button>
          </div>
        </div>
      </div>

      {galeria && galeria.imagenes.length > 0 ? (
        vistaGrid ? (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            {galeria.imagenes.map((imagen) => (
              <TarjetaImagen
                key={imagen.id}
                imagen={imagen}
                onVer={() => navigate(`/imagenes/${imagen.id}/visor`)}
                onEliminar={() => handleEliminarImagen(imagen.id)}
                onAnalisisIA={() => handleAnalisisIA(imagen.id)}
                onDescargarPDF={() => handleDescargarPDF(imagen.id)}
                formatBytes={formatBytes}
                getTipoImagenLabel={getTipoImagenLabel}
                estaAnalizando={analisisEnProgreso.has(imagen.id)}
                modoComparar={modoComparar}
                seleccionada={imagenesSeleccionadas.includes(imagen.id)}
                onToggleSeleccion={() => handleToggleSeleccion(imagen.id)}
              />
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {galeria.imagenes.map((imagen) => (
              <TarjetaImagenLista
                key={imagen.id}
                imagen={imagen}
                onVer={() => navigate(`/imagenes/${imagen.id}/visor`)}
                onEliminar={() => handleEliminarImagen(imagen.id)}
                onAnalisisIA={() => handleAnalisisIA(imagen.id)}
                onDescargarPDF={() => handleDescargarPDF(imagen.id)}
                formatBytes={formatBytes}
                getTipoImagenLabel={getTipoImagenLabel}
                estaAnalizando={analisisEnProgreso.has(imagen.id)}
              />
            ))}
          </div>
        )
      ) : (
        <div className="rounded-3xl border border-dashed border-slate-200 bg-white text-center py-16">
          <ImageIcon size={48} className="mx-auto text-slate-300 mb-4" />
          <h3 className="text-lg font-semibold text-slate-900 mb-2">No hay imágenes registradas</h3>
          <p className="text-slate-500 mb-6">
            {filtroTipo || filtroRegion
              ? 'No hay estudios con los filtros seleccionados'
              : 'Sube la primera imagen médica para este paciente'}
          </p>
          <button
            onClick={() => setModalSubir(true)}
            className="inline-flex items-center gap-3 rounded-2xl bg-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30 transition hover:bg-indigo-700"
          >
            <Upload className="h-4 w-4" /> Subir imagen
          </button>
        </div>
      )}

      {modalSubir && (
        <ModalSubirImagen
          formData={formData}
          setFormData={setFormData}
          archivoSeleccionado={archivoSeleccionado}
          setArchivoSeleccionado={setArchivoSeleccionado}
          previewUrl={previewUrl}
          setPreviewUrl={setPreviewUrl}
          uploading={uploading}
          onCerrar={cerrarModal}
          onSubir={handleSubirImagen}
        />
      )}
    </PatientWorkspaceLayout>
  )
}

// Componente Tarjeta de Imagen (Grid)
const TarjetaImagen: React.FC<{
  imagen: ImagenMedica
  onVer: () => void
  onEliminar: () => void
  onAnalisisIA: () => void
  onDescargarPDF: () => void
  formatBytes: (bytes: number) => string
  getTipoImagenLabel: (tipo: string) => string
  estaAnalizando: boolean
  modoComparar?: boolean
  seleccionada?: boolean
  onToggleSeleccion?: () => void
}> = ({
  imagen,
  onVer,
  onEliminar,
  onAnalisisIA,
  onDescargarPDF,
  formatBytes,
  getTipoImagenLabel,
  estaAnalizando,
  modoComparar,
  seleccionada,
  onToggleSeleccion,
}) => {
  const urlVisualizacion = obtenerUrlVisualizacion(imagen);
  
  const handleClick = () => {
    if (modoComparar && onToggleSeleccion) {
      onToggleSeleccion()
    } else {
      onVer()
    }
  }
  
  return (
    <div className={`card hover:shadow-lg transition-all cursor-pointer group ${
      seleccionada ? 'ring-4 ring-green-500 shadow-xl' : ''
    }`}>
      <div className="relative aspect-square bg-gray-100 rounded-lg mb-3 overflow-hidden" onClick={handleClick}>
        {seleccionada && (
          <div className="absolute top-2 right-2 z-10 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center shadow-lg">
            <Check size={20} className="text-white" />
          </div>
        )}
        {urlVisualizacion ? (
          <img 
            src={`http://localhost:8612${urlVisualizacion}`}
            alt={imagen.titulo}
            className="w-full h-full object-cover"
            onError={(e) => {
              // Si falla la carga, mostrar placeholder
              e.currentTarget.style.display = 'none';
              const parent = e.currentTarget.parentElement;
              if (parent) {
                const placeholder = document.createElement('div');
                placeholder.className = 'absolute inset-0 flex items-center justify-center';
                placeholder.innerHTML = '<svg class="text-gray-400" width="48" height="48"><use href="#image-icon"/></svg>';
                parent.appendChild(placeholder);
              }
            }}
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center">
            <ImageIcon size={48} className="text-gray-400" />
          </div>
        )}
        <div className="absolute top-2 right-2 flex gap-1">
          {imagen.analisis_ia_completado && (
            <span className="bg-purple-500 text-white px-2 py-1 rounded-full text-xs flex items-center gap-1">
              <Sparkles size={12} />
              IA
            </span>
          )}
        </div>
        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all flex items-center justify-center opacity-0 group-hover:opacity-100">
          <ZoomIn size={32} className="text-white" />
        </div>
      </div>
      
      <h3 className="font-medium text-gray-900 mb-1 truncate">{imagen.titulo}</h3>
      <p className="text-sm text-gray-600 mb-2">{getTipoImagenLabel(imagen.tipo_imagen)}</p>
      
      {imagen.region_anatomica && (
        <p className="text-xs text-gray-500 mb-2 capitalize">{imagen.region_anatomica}</p>
      )}
      
      {imagen.analisis_ia_completado && imagen.hallazgos && imagen.hallazgos.length > 0 && (
        <div className="mb-3 p-2 bg-purple-50 rounded-lg">
          <p className="text-xs font-medium text-purple-900 mb-1">Hallazgos IA:</p>
          <ul className="text-xs text-purple-700 space-y-0.5">
            {imagen.hallazgos.slice(0, 2).map((h, i) => (
              <li key={i} className="truncate">• {h}</li>
            ))}
            {imagen.hallazgos.length > 2 && (
              <li className="text-purple-600 font-medium">+{imagen.hallazgos.length - 2} más</li>
            )}
          </ul>
        </div>
      )}
      
      <div className="flex gap-2">
        <button onClick={onVer} className="flex-1 btn-secondary text-sm py-1.5">
          <Eye size={14} />
        </button>
        {!imagen.analisis_ia_completado ? (
          estaAnalizando ? (
            // Barra de progreso mientras analiza
            <div className="flex-1 bg-gray-100 rounded-lg p-2">
              <div className="flex items-center justify-center gap-1 text-xs text-purple-600">
                <div className="animate-spin rounded-full h-3 w-3 border border-purple-500 border-t-transparent"></div>
                <span>Analizando...</span>
              </div>
              <div className="mt-1 w-full bg-purple-200 rounded-full h-1">
                <div className="bg-purple-600 h-1 rounded-full animate-pulse w-3/4"></div>
              </div>
            </div>
          ) : (
            <button 
              onClick={onAnalisisIA} 
              className="flex-1 btn-primary text-sm py-2 px-3 bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 text-white font-medium shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-1"
              title="Analizar con IA"
            >
              <Sparkles size={16} />
              <span className="hidden sm:inline">IA</span>
            </button>
          )
        ) : (
          // Botón PDF cuando ya está analizado
          <button 
            onClick={onDescargarPDF}
            className="flex-1 btn-secondary text-sm py-2 px-3 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-medium shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-1"
            title="Descargar reporte PDF"
          >
            <FileText size={16} />
            <span className="hidden sm:inline">PDF</span>
          </button>
        )}
        <button onClick={onEliminar} className="btn-secondary text-sm py-1.5 text-red-600 hover:bg-red-50">
          <Trash2 size={14} />
        </button>
      </div>
      
      <div className="mt-2 pt-2 border-t border-gray-200 text-xs text-gray-500">
        {formatBytes(imagen.tamanio_bytes)} • {new Date(imagen.created_at).toLocaleDateString()}
      </div>
    </div>
  )
}

// Componente Tarjeta de Imagen (Lista)
const TarjetaImagenLista: React.FC<{
  imagen: ImagenMedica
  onVer: () => void
  onEliminar: () => void
  onAnalisisIA: () => void
  onDescargarPDF: () => void
  formatBytes: (bytes: number) => string
  getTipoImagenLabel: (tipo: string) => string
  estaAnalizando: boolean
}> = ({ imagen, onVer, onEliminar, onAnalisisIA, onDescargarPDF, formatBytes, getTipoImagenLabel, estaAnalizando }) => {
  const urlVisualizacion = obtenerUrlVisualizacion(imagen);
  
  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="flex gap-4">
        <div className="w-24 h-24 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0 cursor-pointer overflow-hidden" onClick={onVer}>
          {urlVisualizacion ? (
            <img 
              src={`http://localhost:8612${urlVisualizacion}`}
              alt={imagen.titulo}
              className="w-full h-full object-cover"
            />
          ) : (
            <ImageIcon size={32} className="text-gray-400" />
          )}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between mb-2">
            <div className="flex-1 min-w-0">
              <h3 className="font-medium text-gray-900 truncate">{imagen.titulo}</h3>
              <p className="text-sm text-gray-600">{getTipoImagenLabel(imagen.tipo_imagen)}</p>
            </div>
            {imagen.analisis_ia_completado && (
              <span className="bg-purple-500 text-white px-2 py-1 rounded-full text-xs flex items-center gap-1 ml-2">
                <Sparkles size={12} />
                IA
              </span>
            )}
          </div>
          
          {imagen.descripcion && (
            <p className="text-sm text-gray-600 mb-2 line-clamp-2">{imagen.descripcion}</p>
          )}
          
          <div className="flex flex-wrap gap-2 text-xs text-gray-500 mb-2">
            {imagen.region_anatomica && (
              <span className="bg-gray-100 px-2 py-1 rounded capitalize">{imagen.region_anatomica}</span>
            )}
            <span>{formatBytes(imagen.tamanio_bytes)}</span>
            <span>{new Date(imagen.created_at).toLocaleDateString()}</span>
          </div>
          
          {imagen.analisis_ia_completado && imagen.hallazgos && imagen.hallazgos.length > 0 && (
            <div className="mb-2 p-2 bg-purple-50 rounded-lg">
              <p className="text-xs font-medium text-purple-900 mb-1">Hallazgos IA:</p>
              <p className="text-xs text-purple-700">{imagen.hallazgos.join(', ')}</p>
            </div>
          )}
        </div>
        
        <div className="flex flex-col gap-2">
          <button onClick={onVer} className="btn-secondary text-sm py-1.5 px-3">
            <Eye size={14} className="mr-1" />
            Ver
          </button>
          {!imagen.analisis_ia_completado ? (
            estaAnalizando ? (
              // Barra de progreso mientras analiza
              <div className="bg-gray-100 rounded-lg p-2">
                <div className="flex items-center justify-center gap-1 text-xs text-purple-600 mb-1">
                  <div className="animate-spin rounded-full h-3 w-3 border border-purple-500 border-t-transparent"></div>
                  <span>Analizando...</span>
                </div>
                <div className="w-full bg-purple-200 rounded-full h-1">
                  <div className="bg-purple-600 h-1 rounded-full animate-pulse w-3/4"></div>
                </div>
              </div>
            ) : (
              <button 
                onClick={onAnalisisIA} 
                className="btn-primary text-sm py-2 px-4 bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 text-white font-medium shadow-md hover:shadow-lg transition-all"
                title="Analizar con IA"
              >
                <Sparkles size={16} className="mr-1" />
                Analizar IA
              </button>
            )
          ) : (
            // Botón PDF cuando ya está analizado
            <button 
              onClick={onDescargarPDF}
              className="btn-secondary text-sm py-2 px-4 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-medium shadow-md hover:shadow-lg transition-all"
              title="Descargar reporte PDF"
            >
              <FileText size={16} className="mr-1" />
              Reporte PDF
            </button>
          )}
          <button onClick={onEliminar} className="btn-secondary text-sm py-1.5 px-3 text-red-600 hover:bg-red-50">
            <Trash2 size={14} />
          </button>
        </div>
      </div>
    </div>
  )
}

// Modal Subir Imagen
const ModalSubirImagen: React.FC<{
  formData: any
  setFormData: (data: any) => void
  archivoSeleccionado: File | null
  setArchivoSeleccionado: (file: File | null) => void
  previewUrl: string | null
  setPreviewUrl: (url: string | null) => void
  uploading: boolean
  onCerrar: () => void
  onSubir: () => void
}> = ({ formData, setFormData, archivoSeleccionado, setArchivoSeleccionado, previewUrl, setPreviewUrl, uploading, onCerrar, onSubir }) => {
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      setArchivoSeleccionado(file)
      
      // Limpiar URL anterior si existe
      if (previewUrl && previewUrl !== 'nifti-placeholder') {
        URL.revokeObjectURL(previewUrl)
      }
      
      // Detectar si es archivo NIfTI
      const esNifti = file.name.toLowerCase().endsWith('.nii') || 
                      file.name.toLowerCase().endsWith('.nii.gz')
      
      if (esNifti) {
        // Para archivos NIfTI, usar placeholder
        setPreviewUrl('nifti-placeholder')
      } else {
        // Para imágenes normales, crear URL de vista previa
        const newPreviewUrl = URL.createObjectURL(file)
        setPreviewUrl(newPreviewUrl)
      }
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal-content max-w-3xl">
        <div className="flex items-center justify-between mb-8 pb-4 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
              <Upload className="text-white" size={24} />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Subir Imagen Médica</h2>
              <p className="text-sm text-gray-500">Complete los datos de la imagen</p>
            </div>
          </div>
          <button 
            onClick={onCerrar} 
            className="w-10 h-10 rounded-lg hover:bg-gray-100 flex items-center justify-center text-gray-400 hover:text-gray-600 transition-colors"
            title="Cerrar"
          >
            <X size={20} />
          </button>
        </div>

        <div className="space-y-6">
          {/* Selección de archivo con vista previa */}
          <div>
            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-3">
              <FileImage size={18} className="text-blue-600" />
              Archivo de Imagen *
            </label>
            
            {previewUrl ? (
              /* Vista previa de la imagen */
              <div className="relative">
                <div className="relative w-full rounded-xl overflow-hidden bg-gray-900 shadow-xl">
                  {previewUrl === 'nifti-placeholder' ? (
                    /* Placeholder para archivos NIfTI */
                    <div className="w-full h-80 flex flex-col items-center justify-center bg-gradient-to-br from-blue-900 via-indigo-900 to-purple-900">
                      <svg className="w-32 h-32 mb-4 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <div className="text-center px-6">
                        <p className="text-2xl font-bold text-white mb-2">🧠 Archivo NIfTI 3D</p>
                        <p className="text-sm text-blue-200 mb-1">{archivoSeleccionado?.name}</p>
                        <p className="text-xs text-blue-300">
                          {archivoSeleccionado && `${(archivoSeleccionado.size / 1024 / 1024).toFixed(2)} MB`}
                        </p>
                        <p className="text-xs text-blue-400 mt-3 italic">El preview se generará al subir</p>
                      </div>
                    </div>
                  ) : (
                    /* Preview normal para imágenes */
                    <>
                      <img 
                        src={previewUrl} 
                        alt="Vista previa" 
                        className="w-full h-80 object-contain"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
                      <div className="absolute bottom-0 left-0 right-0 p-4 text-white">
                        <p className="font-medium text-sm truncate">{archivoSeleccionado?.name}</p>
                        <p className="text-xs text-gray-300">
                          {archivoSeleccionado && `${(archivoSeleccionado.size / 1024 / 1024).toFixed(2)} MB`}
                        </p>
                      </div>
                    </>
                  )}
                  <button
                    type="button"
                    onClick={() => {
                      setArchivoSeleccionado(null)
                      if (previewUrl && previewUrl !== 'nifti-placeholder') {
                        URL.revokeObjectURL(previewUrl)
                      }
                      setPreviewUrl(null)
                    }}
                    className="absolute top-3 right-3 w-8 h-8 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center transition-colors shadow-lg"
                    title="Eliminar imagen"
                  >
                    <X size={18} />
                  </button>
                </div>
                <div className="flex items-center gap-2 mt-3 text-sm text-green-600 bg-green-50 px-4 py-2.5 rounded-lg">
                  <Check size={16} />
                  <span className="font-medium">Archivo cargado correctamente</span>
                </div>
              </div>
            ) : (
              /* Área de selección de archivo */
              <div className="relative">
                <label className="flex items-center justify-center w-full h-32 px-4 transition bg-white border-2 border-gray-300 border-dashed rounded-xl appearance-none cursor-pointer hover:border-blue-400 hover:bg-blue-50 focus:outline-none group">
                  <div className="flex flex-col items-center space-y-2">
                    <Upload className="w-10 h-10 text-gray-400 group-hover:text-blue-500 transition-colors" />
                    <span className="font-medium text-gray-600 group-hover:text-blue-600">
                      Examinar archivo...
                    </span>
                    <span className="text-xs text-gray-500">
                      JPG, PNG, DICOM, NIfTI (.nii, .nii.gz) - máx. 200MB
                    </span>
                  </div>
                  <input
                    type="file"
                    accept="image/*,.dcm,.nii,.nii.gz,.gz,application/x-nifti,application/gzip,application/octet-stream"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </label>
              </div>
            )}
          </div>

          {/* Título */}
          <div>
            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-3">
              <AlignLeft size={18} className="text-blue-600" />
              Título *
            </label>
            <input
              type="text"
              value={formData.titulo}
              onChange={(e) => setFormData({ ...formData, titulo: e.target.value })}
              className="input-field text-lg py-3 px-4 border-2 focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              placeholder="Ej: Radiografía de tórax AP"
            />
          </div>

          {/* Tipo de imagen */}
          <div>
            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-3">
              <Scan size={18} className="text-blue-600" />
              Tipo de Imagen *
            </label>
            <select
              value={formData.tipo_imagen}
              onChange={(e) => setFormData({ ...formData, tipo_imagen: e.target.value })}
              className="input-field text-lg py-3 px-4 border-2 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 cursor-pointer"
            >
              <option value="rayos_x">🔬 Rayos X</option>
              <option value="tomografia">💿 Tomografía (CT)</option>
              <option value="resonancia">🧲 Resonancia Magnética (MRI)</option>
              <option value="ecografia">📡 Ecografía (US)</option>
              <option value="fotografia">📸 Fotografía Médica</option>
              <option value="endoscopia">🔍 Endoscopia</option>
              <option value="mamografia">🩺 Mamografía</option>
            </select>
          </div>

          {/* Región anatómica */}
          <div>
            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-3">
              <MapPin size={18} className="text-blue-600" />
              Región Anatómica
            </label>
            <select
              value={formData.region_anatomica}
              onChange={(e) => setFormData({ ...formData, region_anatomica: e.target.value })}
              className="input-field text-lg py-3 px-4 border-2 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 cursor-pointer"
            >
              <option value="">📍 Seleccionar región...</option>
              <option value="torax">🫁 Tórax</option>
              <option value="abdomen">🔴 Abdomen</option>
              <option value="craneo">🧠 Cráneo</option>
              <option value="columna">🦴 Columna Vertebral</option>
              <option value="pelvis">⚫ Pelvis</option>
              <option value="extremidad_superior">💪 Extremidad Superior</option>
              <option value="extremidad_inferior">🦵 Extremidad Inferior</option>
              <option value="cuello">👔 Cuello</option>
              <option value="cara">👤 Cara</option>
              <option value="mano">✋ Mano</option>
              <option value="pie">👣 Pie</option>
              <option value="rodilla">🦴 Rodilla</option>
              <option value="hombro">💪 Hombro</option>
              <option value="cadera">⚫ Cadera</option>
              <option value="toraco_abdominal">🫁 Tóraco-Abdominal</option>
              <option value="otro">📌 Otro</option>
            </select>
          </div>

          {/* Lateralidad */}
          <div>
            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-3">
              <Navigation size={18} className="text-blue-600" />
              Lateralidad
            </label>
            <select
              value={formData.lateralidad}
              onChange={(e) => setFormData({ ...formData, lateralidad: e.target.value })}
              className="input-field text-lg py-3 px-4 border-2 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 cursor-pointer"
            >
              <option value="">➖ No aplica</option>
              <option value="izquierda">← Izquierda</option>
              <option value="derecha">→ Derecha</option>
              <option value="bilateral">↔️ Bilateral</option>
            </select>
          </div>

          {/* Descripción */}
          <div>
            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-3">
              <FileText size={18} className="text-blue-600" />
              Descripción
            </label>
            <textarea
              value={formData.descripcion}
              onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
              className="input-field text-base py-3 px-4 border-2 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 resize-none"
              rows={4}
              placeholder="Notas adicionales sobre la imagen..."
            />
          </div>
        </div>

        <div className="flex gap-4 mt-8 pt-6 border-t border-gray-200">
          <button 
            onClick={onCerrar} 
            className="flex-1 px-6 py-3.5 text-base font-medium text-gray-700 bg-white border-2 border-gray-300 rounded-xl hover:bg-gray-50 hover:border-gray-400 transition-all flex items-center justify-center gap-2" 
            disabled={uploading}
          >
            <X size={20} />
            Cancelar
          </button>
          <button 
            onClick={onSubir} 
            className="flex-1 px-6 py-3.5 text-base font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transition-all flex items-center justify-center gap-2" 
            disabled={uploading || !archivoSeleccionado}
          >
            {uploading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
                <span>Subiendo...</span>
              </>
            ) : (
              <>
                <Upload size={20} />
                <span>Subir Imagen</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

export default GaleriaImagenes
