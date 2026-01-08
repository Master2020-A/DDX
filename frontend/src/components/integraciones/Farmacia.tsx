import { useState, useEffect } from 'react'
import { Package, AlertCircle, CheckCircle, Clock, Search, Plus, X, Trash2, Eye } from 'lucide-react'
import * as integracionesService from '@/services/integracionesService'
import { pacienteService } from '@/services/pacienteService'

interface SolicitudFarmacia {
  id: string
  folio: string
  paciente_nombre?: string
  medico_nombre?: string
  medicamentos_solicitados: Array<{
    codigo: string
    nombre: string
    cantidad: number
    urgente: boolean
  }>
  urgente: boolean
  destino: string
  ubicacion?: string
  fecha_solicitud: string
  estado: string
  fecha_dispensacion?: string
  farmaceutico_nombre?: string
  costo_total?: number
  verificado: boolean
}

interface FormularioData {
  paciente_id: string
  medicamentos_solicitados: Array<{
    codigo: string
    nombre: string
    cantidad: number
    urgente: boolean
  }>
  urgente: boolean
  destino: string
  ubicacion?: string
  notas?: string
}

export default function Farmacia() {
  const [solicitudes, setSolicitudes] = useState<SolicitudFarmacia[]>([])
  const [filtroEstado, setFiltroEstado] = useState<string>('TODOS')
  const [cargando, setCargando] = useState(true)
  const [mostrarFormulario, setMostrarFormulario] = useState(false)
  const [guardando, setGuardando] = useState(false)
  const [pacientes, setPacientes] = useState<any[]>([])
  const [solicitudSeleccionada, setSolicitudSeleccionada] = useState<SolicitudFarmacia | null>(null)
  
  const [formData, setFormData] = useState<FormularioData>({
    paciente_id: '',
    medicamentos_solicitados: [],
    urgente: false,
    destino: 'AMBULATORIO',
    ubicacion: '',
    notas: '',
  })
  
  const [piso, setPiso] = useState('')
  const [cama, setCama] = useState('')
  
  const pisos = ['Planta Baja', 'Piso 1', 'Piso 2', 'Piso 3', 'Piso 4', 'Piso 5', 'UCI', 'Urgencias']
  const camas = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20']
  
  const [nuevoMedicamento, setNuevoMedicamento] = useState({
    codigo: '',
    nombre: '',
    cantidad: 1,
    urgente: false,
  })

  useEffect(() => {
    cargarSolicitudes()
    cargarPacientes()
  }, [])

  const cargarPacientes = async () => {
    try {
      console.log('🔄 Iniciando carga de pacientes...')
      const data = await pacienteService.listar()
      console.log('✅ Pacientes cargados en Farmacia:', data)
      console.log('📊 Cantidad de pacientes:', data?.length || 0)
      if (Array.isArray(data)) {
        setPacientes(data)
        if (data.length === 0) {
          console.warn('⚠️ El array de pacientes está vacío')
        }
      } else {
        console.error('❌ La respuesta no es un array:', data)
      }
    } catch (error: any) {
      console.error('❌ Error al cargar pacientes:', error)
      console.error('📝 Detalles del error:', error.response?.data || error.message)
      if (error.response?.status === 401) {
        alert('Sesión expirada. Por favor, inicia sesión nuevamente.')
      }
    }
  }

  useEffect(() => {
    if (piso && cama) {
      setFormData(prev => ({ ...prev, ubicacion: `${piso}, Cama ${cama}` }))
    }
  }, [piso, cama])

  const cargarSolicitudes = async () => {
    try {
      setCargando(true)
      const data = await integracionesService.listarSolicitudesFarmacia()
      setSolicitudes(data)
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setCargando(false)
    }
  }

  const solicitudesFiltradas = solicitudes.filter(sol => 
    filtroEstado === 'TODOS' || sol.estado === filtroEstado
  )

  const estadisticas = {
    total: solicitudes.length,
    pendientes: solicitudes.filter(s => s.estado === 'PENDIENTE').length,
    dispensadas: solicitudes.filter(s => s.estado === 'DISPENSADO').length,
    urgentes: solicitudes.filter(s => s.urgente && s.estado === 'PENDIENTE').length,
  }

  const getEstadoBadge = (estado: string) => {
    const badges = {
      PENDIENTE: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      DISPENSADO: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      CANCELADO: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    }
    return badges[estado as keyof typeof badges] || 'bg-gray-100 text-gray-800'
  }

  const getEstadoIcon = (estado: string) => {
    switch (estado) {
      case 'PENDIENTE':
        return <Clock className="w-4 h-4" />
      case 'DISPENSADO':
        return <CheckCircle className="w-4 h-4" />
      case 'CANCELADO':
        return <AlertCircle className="w-4 h-4" />
      default:
        return <Package className="w-4 h-4" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-50">
            Gestión de Farmacia
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Solicitudes y dispensación de medicamentos
          </p>
        </div>
        <button
          onClick={() => setMostrarFormulario(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus className="w-4 h-4" />
          Nueva Solicitud
        </button>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Total Solicitudes</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-50">{estadisticas.total}</p>
            </div>
            <Package className="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Pendientes</p>
              <p className="text-2xl font-bold text-yellow-600">{estadisticas.pendientes}</p>
            </div>
            <Clock className="w-8 h-8 text-yellow-500" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Dispensadas</p>
              <p className="text-2xl font-bold text-green-600">{estadisticas.dispensadas}</p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Urgentes</p>
              <p className="text-2xl font-bold text-red-600">{estadisticas.urgentes}</p>
            </div>
            <AlertCircle className="w-8 h-8 text-red-500" />
          </div>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-4">
          <Search className="w-5 h-5 text-gray-400" />
          <div className="flex gap-2">
            {['TODOS', 'PENDIENTE', 'DISPENSADO', 'CANCELADO'].map(estado => (
              <button
                key={estado}
                onClick={() => setFiltroEstado(estado)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  filtroEstado === estado
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300'
                }`}
              >
                {estado}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Lista de Solicitudes */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        {cargando ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-500">Cargando solicitudes...</p>
          </div>
        ) : solicitudesFiltradas.length === 0 ? (
          <div className="p-8 text-center">
            <Package className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No hay solicitudes</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-900">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Folio
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Paciente
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Medicamentos
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Destino
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Fecha
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Estado
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {solicitudesFiltradas.map(solicitud => (
                  <tr key={solicitud.id} className="hover:bg-gray-50 dark:hover:bg-gray-900">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        {solicitud.urgente && (
                          <AlertCircle className="w-4 h-4 text-red-500" />
                        )}
                        <span className="text-sm font-medium text-gray-900 dark:text-gray-50">
                          {solicitud.folio}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900 dark:text-gray-50">
                        {solicitud.paciente_nombre || 'N/A'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900 dark:text-gray-50">
                        {solicitud.medicamentos_solicitados.length} medicamento(s)
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm">
                        <div className="font-medium text-gray-900 dark:text-gray-50">
                          {solicitud.destino}
                        </div>
                        {solicitud.ubicacion && (
                          <div className="text-gray-500 dark:text-gray-400">
                            {solicitud.ubicacion}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {new Date(solicitud.fecha_solicitud).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getEstadoBadge(solicitud.estado)}`}>
                        {getEstadoIcon(solicitud.estado)}
                        {solicitud.estado}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex gap-2">
                        <button
                          onClick={() => setSolicitudSeleccionada(solicitud)}
                          className="text-blue-600 hover:text-blue-800 dark:text-blue-400"
                          title="Ver detalles"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        {solicitud.estado === 'PENDIENTE' && (
                          <button className="text-green-600 hover:text-green-800 dark:text-green-400">
                            Dispensar
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Formulario Nueva Solicitud */}
      {mostrarFormulario && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-50">
                Nueva Solicitud de Farmacia
              </h3>
              <button
                onClick={() => {
                  setMostrarFormulario(false)
                  setFormData({
                    paciente_id: '',
                    medicamentos_solicitados: [],
                    urgente: false,
                    destino: 'AMBULATORIO',
                    ubicacion: '',
                    notas: '',
                  })
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <form onSubmit={async (e) => {
              e.preventDefault()
              if (formData.medicamentos_solicitados.length === 0) {
                alert('Debe agregar al menos un medicamento')
                return
              }
              try {
                setGuardando(true)
                await integracionesService.crearSolicitudFarmacia(formData)
                setMostrarFormulario(false)
                setFormData({
                  paciente_id: '',
                  medicamentos_solicitados: [],
                  urgente: false,
                  destino: 'AMBULATORIO',
                  ubicacion: '',
                  notas: '',
                })
                cargarSolicitudes()
              } catch (error) {
                console.error('Error:', error)
                alert('Error al crear solicitud')
              } finally {
                setGuardando(false)
              }
            }} className="space-y-6">
              
              {/* Información General */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Paciente *
                  </label>
                  <select
                    required
                    value={formData.paciente_id}
                    onChange={(e) => setFormData({...formData, paciente_id: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-50"
                    aria-label="Seleccionar paciente"
                  >
                    <option value="">Seleccionar paciente...</option>
                    {pacientes.map(p => (
                      <option key={p.id} value={p.id}>
                        {p.nombre_completo}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Destino *
                  </label>
                  <select
                    required
                    value={formData.destino}
                    onChange={(e) => setFormData({...formData, destino: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-50"
                    aria-label="Destino de la solicitud"
                  >
                    <option value="AMBULATORIO">Ambulatorio</option>
                    <option value="HOSPITALIZACION">Hospitalización</option>
                    <option value="URGENCIAS">Urgencias</option>
                    <option value="CIRUGIA">Cirugía</option>
                  </select>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="urgente"
                    checked={formData.urgente}
                    onChange={(e) => setFormData({...formData, urgente: e.target.checked})}
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                  <label htmlFor="urgente" className="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                    Solicitud Urgente
                  </label>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Piso
                  </label>
                  <select
                    value={piso}
                    onChange={(e) => setPiso(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-50"
                    aria-label="Seleccionar piso"
                  >
                    <option value="">Seleccionar piso...</option>
                    {pisos.map(p => (
                      <option key={p} value={p}>{p}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Cama
                  </label>
                  <select
                    value={cama}
                    onChange={(e) => setCama(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-50"
                    aria-label="Seleccionar cama"
                  >
                    <option value="">Seleccionar cama...</option>
                    {camas.map(c => (
                      <option key={c} value={c}>Cama {c}</option>
                    ))}
                  </select>
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Ubicación (generada automáticamente)
                  </label>
                  <input
                    type="text"
                    value={formData.ubicacion}
                    onChange={(e) => setFormData({...formData, ubicacion: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-50"
                    placeholder="Ej: Piso 3, Cama 12"
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="urgente"
                    checked={formData.urgente}
                    onChange={(e) => setFormData({...formData, urgente: e.target.checked})}
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                  <label htmlFor="urgente" className="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                    Solicitud Urgente
                  </label>
                </div>
              </div>

              {/* Agregar Medicamentos */}
              <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
                <h4 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-4">
                  Medicamentos Solicitados
                </h4>
                
                <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-3">
                  <input
                    type="text"
                    value={nuevoMedicamento.codigo}
                    onChange={(e) => setNuevoMedicamento({...nuevoMedicamento, codigo: e.target.value})}
                    className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-50"
                    placeholder="Código"
                  />
                  <input
                    type="text"
                    value={nuevoMedicamento.nombre}
                    onChange={(e) => setNuevoMedicamento({...nuevoMedicamento, nombre: e.target.value})}
                    className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-50"
                    placeholder="Nombre del medicamento"
                  />
                  <input
                    type="number"
                    min="1"
                    value={nuevoMedicamento.cantidad}
                    onChange={(e) => setNuevoMedicamento({...nuevoMedicamento, cantidad: parseInt(e.target.value)})}
                    className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-50"
                    placeholder="Cantidad"
                  />
                  <button
                    type="button"
                    onClick={() => {
                      if (nuevoMedicamento.nombre && nuevoMedicamento.codigo) {
                        setFormData({
                          ...formData,
                          medicamentos_solicitados: [...formData.medicamentos_solicitados, nuevoMedicamento]
                        })
                        setNuevoMedicamento({ codigo: '', nombre: '', cantidad: 1, urgente: false })
                      }
                    }}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    <Plus className="w-4 h-4 inline mr-1" />
                    Agregar
                  </button>
                </div>

                {/* Lista de Medicamentos */}
                {formData.medicamentos_solicitados.length > 0 && (
                  <div className="space-y-2">
                    {formData.medicamentos_solicitados.map((med, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
                        <div className="flex-1">
                          <span className="font-medium text-gray-900 dark:text-gray-50">{med.nombre}</span>
                          <span className="text-sm text-gray-500 dark:text-gray-400 ml-2">
                            ({med.codigo}) - Cantidad: {med.cantidad}
                          </span>
                        </div>
                        <button
                          type="button"
                          onClick={() => {
                            setFormData({
                              ...formData,
                              medicamentos_solicitados: formData.medicamentos_solicitados.filter((_, i) => i !== index)
                            })
                          }}
                          className="text-red-600 hover:text-red-800"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Notas */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Notas Adicionales
                </label>
                <textarea
                  value={formData.notas}
                  onChange={(e) => setFormData({...formData, notas: e.target.value})}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-50"
                  placeholder="Observaciones o instrucciones especiales..."
                />
              </div>

              {/* Botones */}
              <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                <button
                  type="button"
                  onClick={() => {
                    setMostrarFormulario(false)
                    setFormData({
                      paciente_id: '',
                      medicamentos_solicitados: [],
                      urgente: false,
                      destino: 'AMBULATORIO',
                      ubicacion: '',
                      notas: '',
                    })
                  }}
                  className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={guardando || formData.medicamentos_solicitados.length === 0}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {guardando ? 'Guardando...' : 'Crear Solicitud'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal de Visualización de Detalles */}
      {solicitudSeleccionada && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-50">
                Detalle de Solicitud {solicitudSeleccionada.folio}
              </h3>
              <button
                onClick={() => setSolicitudSeleccionada(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-6">
              {/* Información General */}
              <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Estado</p>
                  <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getEstadoBadge(solicitudSeleccionada.estado)}`}>
                    {getEstadoIcon(solicitudSeleccionada.estado)}
                    {solicitudSeleccionada.estado}
                  </span>
                </div>
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Fecha de Solicitud</p>
                  <p className="font-medium">{new Date(solicitudSeleccionada.fecha_solicitud).toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Paciente</p>
                  <p className="font-medium">{solicitudSeleccionada.paciente_nombre || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Médico</p>
                  <p className="font-medium">{solicitudSeleccionada.medico_nombre || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Destino</p>
                  <p className="font-medium">{solicitudSeleccionada.destino}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Ubicación</p>
                  <p className="font-medium">{solicitudSeleccionada.ubicacion || 'N/A'}</p>
                </div>
                {solicitudSeleccionada.urgente && (
                  <div className="col-span-2">
                    <span className="inline-flex items-center gap-1 px-3 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-full text-sm font-medium">
                      <AlertCircle className="w-4 h-4" />
                      Solicitud Urgente
                    </span>
                  </div>
                )}
              </div>

              {/* Medicamentos Solicitados */}
              <div>
                <h4 className="font-semibold mb-3">Medicamentos Solicitados</h4>
                <div className="space-y-2">
                  {solicitudSeleccionada.medicamentos_solicitados.map((med, idx) => (
                    <div key={idx} className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <p className="font-medium text-gray-900 dark:text-gray-50">{med.nombre}</p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">Código: {med.codigo}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold text-gray-900 dark:text-gray-50">Cantidad: {med.cantidad}</p>
                          {med.urgente && (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded text-xs">
                              Urgente
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Información de Dispensación */}
              {solicitudSeleccionada.estado === 'DISPENSADA' && (
                <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                  <h4 className="font-semibold mb-3 text-green-800 dark:text-green-400">Información de Dispensación</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Fecha de Dispensación</p>
                      <p className="font-medium">{solicitudSeleccionada.fecha_dispensacion ? new Date(solicitudSeleccionada.fecha_dispensacion).toLocaleString() : 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Farmacéutico</p>
                      <p className="font-medium">{solicitudSeleccionada.farmaceutico_nombre || 'N/A'}</p>
                    </div>
                    {solicitudSeleccionada.costo_total && (
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Costo Total</p>
                        <p className="font-bold text-green-600">${solicitudSeleccionada.costo_total.toFixed(2)} MXN</p>
                      </div>
                    )}
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Verificado</p>
                      <p className="font-medium">{solicitudSeleccionada.verificado ? 'Sí' : 'No'}</p>
                    </div>
                  </div>
                </div>
              )}

              <div className="flex justify-end">
                <button
                  onClick={() => setSolicitudSeleccionada(null)}
                  className="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600"
                >
                  Cerrar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
