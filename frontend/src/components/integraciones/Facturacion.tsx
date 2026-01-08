import { useState, useEffect } from 'react'
import { FileText, DollarSign, CheckCircle, Clock, XCircle, Search, Plus, X, Trash2, Eye } from 'lucide-react'
import * as integracionesService from '@/services/integracionesService'
import { pacienteService } from '@/services/pacienteService'

interface FacturaElectronica {
  id: string
  uuid_sat?: string
  serie?: string
  folio: string
  paciente_nombre?: string
  tipo_comprobante: string
  uso_cfdi: string
  metodo_pago: string
  forma_pago?: string
  receptor_rfc: string
  receptor_nombre: string
  receptor_cp?: string
  receptor_municipio?: string
  receptor_ciudad?: string
  receptor_estado?: string
  receptor_colonia?: string
  conceptos: Array<{
    clave_prod_serv: string
    cantidad: number
    unidad: string
    descripcion: string
    valor_unitario: number
    importe: number
  }>
  subtotal: number
  total: number
  fecha_emision: string
  estado: string
  fecha_timbrado?: string
  pac_proveedor?: string
}

export default function Facturacion() {
  const [facturas, setFacturas] = useState<FacturaElectronica[]>([])
  const [filtroEstado, setFiltroEstado] = useState<string>('TODOS')
  const [cargando, setCargando] = useState(true)
  const [mostrarFormulario, setMostrarFormulario] = useState(false)
  const [guardando, setGuardando] = useState(false)
  const [pacientes, setPacientes] = useState<any[]>([])
  const [facturaSeleccionada, setFacturaSeleccionada] = useState<FacturaElectronica | null>(null)
  const [buscandoCP, setBuscandoCP] = useState(false)
  
  const [formData, setFormData] = useState({
    paciente_id: '',
    receptor_rfc: 'XAXX010101000',
    receptor_nombre: 'Público General',
    receptor_cp: '01000',
    receptor_calle: '',
    receptor_numero_exterior: '',
    receptor_numero_interior: '',
    receptor_colonia: '',
    receptor_municipio: '',
    receptor_ciudad: '',
    receptor_estado: '',
    uso_cfdi: 'G03',
    metodo_pago: 'PUE',
    forma_pago: '01',
    conceptos: [] as Array<{
      clave_prod_serv: string
      cantidad: number
      unidad: string
      descripcion: string
      valor_unitario: number
      importe: number
    }>
  })
  
  const [colonias, setColonias] = useState<string[]>([])
  
  const [nuevoConcepto, setNuevoConcepto] = useState({
    clave_prod_serv: '85121800',
    cantidad: 1,
    unidad: 'E48',
    descripcion: '',
    valor_unitario: 0,
    importe: 0
  })

  useEffect(() => {
    cargarFacturas()
    cargarPacientes()
  }, [])

  const cargarPacientes = async () => {
    try {
      console.log('🔄 Iniciando carga de pacientes...')
      const data = await pacienteService.listar()
      console.log('✅ Pacientes cargados en Facturación:', data)
      console.log('📊 Cantidad de pacientes:', data?.length || 0)
      if (Array.isArray(data)) {
        setPacientes(data)
        if (data.length === 0) {
          console.warn('⚠️ El array de pacientes está vacío - Necesitas crear pacientes primero')
        }
      } else {
        console.error('❌ La respuesta no es un array:', data)
      }
    } catch (error: any) {
      console.error('❌ Error al cargar pacientes:', error)
      console.error('📝 Detalles del error:', error.response?.data || error.message)
      console.error('🔑 Status:', error.response?.status)
      if (error.response?.status === 401) {
        alert('Sesión expirada. Por favor, inicia sesión nuevamente.')
      } else if (error.response?.status === 403) {
        alert('No tienes permisos para ver los pacientes.')
      }
    }
  }

  const buscarDireccionPorCP = async (cp: string) => {
    if (cp.length !== 5) return
    
    try {
      setBuscandoCP(true)
      console.log(' Buscando CP:', cp)
      let resultado: any = null
      
      // Mapeo manual de CPs conocidos de Hermosillo, Sonora
      const cpsHermosillo: { [key: string]: { municipio: string, estado: string, colonias: string[] } } = {
        '83288': {
          municipio: 'Hermosillo',
          estado: 'Sonora',
          colonias: ['Jardines de Monaco', 'La Verbena', 'Peñasco', 'Marsella', 'Fovissste', 'Villa Bonita', 'Praderas Del Valle', 'Monaco Privada Residencial', 'Rosales', 'Rio Grande', 'Jardines Del Valle', 'Villas Del Palmar']
        },
        '83000': { municipio: 'Hermosillo', estado: 'Sonora', colonias: ['Centro'] },
        '83010': { municipio: 'Hermosillo', estado: 'Sonora', colonias: ['Villa de Seris'] },
        '83100': { municipio: 'Hermosillo', estado: 'Sonora', colonias: ['Modelo'] },
        '83200': { municipio: 'Hermosillo', estado: 'Sonora', colonias: ['San Benito'] }
      }
      
      // Verificar si tenemos el CP en el mapeo manual
      if (cpsHermosillo[cp]) {
        const info = cpsHermosillo[cp]
        resultado = {
          municipio: info.municipio,
          estado: info.estado,
          ciudad: info.municipio,
          colonias: info.colonias
        }
        console.log(' CP encontrado en base local:', resultado)
      }
      
      // Si no está en el mapeo, intentar con API
      if (!resultado) {
        try {
          console.log(' Consultando API Zippopotam...')
          const response = await fetch(`https://api.zippopotam.us/mx/${cp}`)
          const data = await response.json()
          console.log(' Respuesta Zippopotam:', data)
          
          if (data.places && data.places.length > 0) {
            // Zippopotam: "place name" es la colonia, "state" es el estado
            // Necesitamos inferir el municipio del nombre del lugar
            const estado = data.places[0]['state']
            const colonias = data.places.map((p: any) => p['place name'])
            
            // Inferir municipio: para Sonora, muchos CPs son de Hermosillo
            let municipio = colonias[0] // Por defecto usar la primera colonia
            
            // Lógica para inferir municipio basado en el estado
            if (estado === 'Sonora' && cp.startsWith('83')) {
              municipio = 'Hermosillo' // La mayoría de CPs 83xxx son de Hermosillo
            }
            
            resultado = {
              municipio: municipio,
              estado: estado,
              ciudad: municipio,
              colonias: colonias
            }
            console.log(' Datos inferidos de API:', resultado)
          }
        } catch (e) {
          console.warn(' API Zippopotam falló:', e)
        }
      }
      
      if (resultado) {
        console.log(' Información encontrada:', resultado)
        
        setColonias(resultado.colonias)
        
        setFormData(prev => ({
          ...prev,
          receptor_cp: cp,
          receptor_ciudad: resultado.ciudad || '',
          receptor_estado: resultado.estado || '',
          receptor_colonia: resultado.colonias.length > 0 ? resultado.colonias[0] : ''
        }))
        
        console.log(' Ciudad actualizada:', resultado.ciudad)
      } else {
        console.error(' No se encontró información')
        alert(`No se encontró información para el código postal: ${cp}`)
      }
    } catch (error) {
      console.error(' Error general al buscar CP:', error)
      alert('Error al buscar código postal. Verifique su conexión.')
    } finally {
      setBuscandoCP(false)
    }
  }

  const cargarFacturas = async () => {
    try {
      setCargando(true)
      const data = await integracionesService.listarFacturas()
      setFacturas(data)
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setCargando(false)
    }
  }

  const facturasFiltradas = facturas.filter(factura => 
    filtroEstado === 'TODOS' || factura.estado === filtroEstado
  )

  const estadisticas = {
    total: facturas.length,
    timbradas: facturas.filter(f => f.estado === 'TIMBRADA').length,
    pendientes: facturas.filter(f => f.estado === 'PENDIENTE').length,
    canceladas: facturas.filter(f => f.estado === 'CANCELADA').length,
    totalMonto: facturas.reduce((sum, f) => sum + f.total, 0),
  }

  const getEstadoBadge = (estado: string) => {
    const badges = {
      PENDIENTE: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      TIMBRADA: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      CANCELADA: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      ERROR: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    }
    return badges[estado as keyof typeof badges] || 'bg-gray-100 text-gray-800'
  }

  const getEstadoIcon = (estado: string) => {
    switch (estado) {
      case 'PENDIENTE':
        return <Clock className="w-4 h-4" />
      case 'TIMBRADA':
        return <CheckCircle className="w-4 h-4" />
      case 'CANCELADA':
      case 'ERROR':
        return <XCircle className="w-4 h-4" />
      default:
        return <FileText className="w-4 h-4" />
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN',
    }).format(amount)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-50">
            Facturación Electrónica CFDI 4.0
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Generación y timbrado de facturas electrónicas
          </p>
        </div>
        <button
          onClick={() => setMostrarFormulario(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus className="w-4 h-4" />
          Nueva Factura
        </button>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Total Facturas</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-50">{estadisticas.total}</p>
            </div>
            <FileText className="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Timbradas</p>
              <p className="text-2xl font-bold text-green-600">{estadisticas.timbradas}</p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-500" />
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
              <p className="text-sm text-gray-500 dark:text-gray-400">Canceladas</p>
              <p className="text-2xl font-bold text-red-600">{estadisticas.canceladas}</p>
            </div>
            <XCircle className="w-8 h-8 text-red-500" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Monto Total</p>
              <p className="text-xl font-bold text-blue-600">{formatCurrency(estadisticas.totalMonto)}</p>
            </div>
            <DollarSign className="w-8 h-8 text-blue-500" />
          </div>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-4">
          <Search className="w-5 h-5 text-gray-400" />
          <div className="flex gap-2">
            {['TODOS', 'PENDIENTE', 'TIMBRADA', 'CANCELADA'].map(estado => (
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

      {/* Lista de Facturas */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        {cargando ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-500">Cargando facturas...</p>
          </div>
        ) : facturasFiltradas.length === 0 ? (
          <div className="p-8 text-center">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No hay facturas</p>
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
                    Receptor
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    RFC
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Conceptos
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Total
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
                {facturasFiltradas.map(factura => (
                  <tr key={factura.id} className="hover:bg-gray-50 dark:hover:bg-gray-900">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm">
                        <div className="font-medium text-gray-900 dark:text-gray-50">
                          {factura.serie}-{factura.folio}
                        </div>
                        {factura.uuid_sat && (
                          <div className="text-xs text-gray-500 dark:text-gray-400">
                            UUID: {factura.uuid_sat.substring(0, 8)}...
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm text-gray-900 dark:text-gray-50">
                        {factura.receptor_nombre}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900 dark:text-gray-50">
                        {factura.receptor_rfc}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm text-gray-900 dark:text-gray-50">
                        {factura.conceptos.length} concepto(s)
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm font-semibold text-gray-900 dark:text-gray-50">
                        {formatCurrency(factura.total)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {new Date(factura.fecha_emision).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getEstadoBadge(factura.estado)}`}>
                        {getEstadoIcon(factura.estado)}
                        {factura.estado}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <div className="flex gap-2">
                        <button
                          onClick={() => setFacturaSeleccionada(factura)}
                          className="text-blue-600 hover:text-blue-800 dark:text-blue-400"
                          title="Ver detalles"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        {factura.estado === 'TIMBRADA' && (
                          <>
                            <button className="text-green-600 hover:text-green-800 dark:text-green-400">
                              Descargar
                            </button>
                            <button className="text-red-600 hover:text-red-800 dark:text-red-400">
                              Cancelar
                            </button>
                          </>
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

      {/* Formulario Nueva Factura */}
      {mostrarFormulario && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-50">Nueva Factura Electrónica CFDI 4.0</h3>
              <button onClick={() => setMostrarFormulario(false)} className="text-gray-400 hover:text-gray-600">
                <X className="w-6 h-6" />
              </button>
            </div>

            <form onSubmit={async (e) => {
              e.preventDefault()
              if (formData.conceptos.length === 0) {
                alert('Debe agregar al menos un concepto')
                return
              }
              try {
                setGuardando(true)
                const subtotal = formData.conceptos.reduce((sum, c) => sum + c.importe, 0)
                const total = subtotal * 1.16
                
                // Estructurar datos según schema del backend
                const facturaData = {
                  paciente_id: formData.paciente_id || null,
                  consulta_id: null,
                  hospitalizacion_id: null,
                  tipo_comprobante: 'I',
                  uso_cfdi: formData.uso_cfdi,
                  metodo_pago: formData.metodo_pago,
                  forma_pago: formData.forma_pago,
                  receptor: {
                    rfc: formData.receptor_rfc,
                    nombre: formData.receptor_nombre,
                    codigo_postal: formData.receptor_cp,
                    regimen_fiscal: '605'
                  },
                  conceptos: formData.conceptos.map(c => ({
                    ...c,
                    objeto_imp: '02'
                  })),
                  subtotal,
                  total
                }
                
                console.log('📤 Enviando factura:', facturaData)
                await integracionesService.generarFactura(facturaData)
                setMostrarFormulario(false)
                cargarFacturas()
                alert('Factura creada exitosamente')
              } catch (error: any) {
                console.error('❌ Error al crear factura:', error)
                console.error('📝 Detalles:', error.response?.data)
                alert(`Error al crear factura: ${error.response?.data?.detail || error.message}`)
              } finally {
                setGuardando(false)
              }
            }} className="space-y-6">
              
              {/* Datos del Paciente */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Paciente *</label>
                  <select
                    required
                    value={formData.paciente_id}
                    onChange={(e) => {
                      const paciente = pacientes.find(p => p.id === e.target.value)
                      setFormData({
                        ...formData,
                        paciente_id: e.target.value,
                        receptor_nombre: paciente?.nombre_completo || '',
                        receptor_rfc: paciente?.rfc || 'XAXX010101000'
                      })
                    }}
                    className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700"
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
                  <label className="block text-sm font-medium mb-2">RFC Receptor *</label>
                  <input type="text" required value={formData.receptor_rfc}
                    onChange={(e) => setFormData({...formData, receptor_rfc: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700" />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium mb-2">Nombre Receptor *</label>
                  <input type="text" required value={formData.receptor_nombre}
                    onChange={(e) => setFormData({...formData, receptor_nombre: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700" />
                </div>
              </div>

              {/* Dirección Fiscal */}
              <div className="border-t pt-4">
                <h4 className="text-lg font-semibold mb-4">Dirección Fiscal</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Código Postal *</label>
                    <input
                      type="text"
                      required
                      maxLength={5}
                      value={formData.receptor_cp}
                      onChange={(e) => {
                        const cp = e.target.value
                        setFormData({...formData, receptor_cp: cp})
                        if (cp.length === 5) {
                          buscarDireccionPorCP(cp)
                        }
                      }}
                      className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700"
                      placeholder="12345"
                    />
                    {buscandoCP && <p className="text-xs text-blue-500 mt-1">Buscando...</p>}
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Calle *</label>
                    <input
                      type="text"
                      required
                      value={formData.receptor_calle}
                      onChange={(e) => setFormData({...formData, receptor_calle: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700"
                      placeholder="Nombre de la calle"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">No. Exterior *</label>
                    <input
                      type="text"
                      required
                      value={formData.receptor_numero_exterior}
                      onChange={(e) => setFormData({...formData, receptor_numero_exterior: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700"
                      placeholder="123"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">No. Interior</label>
                    <input
                      type="text"
                      value={formData.receptor_numero_interior}
                      onChange={(e) => setFormData({...formData, receptor_numero_interior: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700"
                      placeholder="A"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Colonia *</label>
                    <select
                      required
                      value={formData.receptor_colonia}
                      onChange={(e) => setFormData({...formData, receptor_colonia: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700"
                      aria-label="Seleccionar colonia"
                      disabled={colonias.length === 0}
                    >
                      <option value="">Seleccionar colonia...</option>
                      {colonias.map((col, idx) => (
                        <option key={idx} value={col}>{col}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Ciudad</label>
                    <input
                      type="text"
                      readOnly
                      value={formData.receptor_ciudad}
                      className="w-full px-3 py-2 border rounded-lg bg-gray-100 dark:bg-gray-800"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Estado</label>
                    <input
                      type="text"
                      readOnly
                      value={formData.receptor_estado}
                      className="w-full px-3 py-2 border rounded-lg bg-gray-100 dark:bg-gray-800"
                    />
                  </div>
                </div>
              </div>

              <div className="border-t pt-4">
                <h4 className="text-lg font-semibold mb-4">Conceptos</h4>
                <div className="grid grid-cols-6 gap-2 mb-3">
                  <input type="text" placeholder="Descripción" value={nuevoConcepto.descripcion}
                    onChange={(e) => setNuevoConcepto({...nuevoConcepto, descripcion: e.target.value})}
                    className="col-span-2 px-3 py-2 border rounded-lg bg-white dark:bg-gray-700" />
                  <input type="number" placeholder="Cantidad" value={nuevoConcepto.cantidad}
                    onChange={(e) => {
                      const cantidad = parseFloat(e.target.value)
                      setNuevoConcepto({...nuevoConcepto, cantidad, importe: cantidad * nuevoConcepto.valor_unitario})
                    }}
                    className="px-3 py-2 border rounded-lg bg-white dark:bg-gray-700" />
                  <input type="number" placeholder="Precio" value={nuevoConcepto.valor_unitario}
                    onChange={(e) => {
                      const valor = parseFloat(e.target.value)
                      setNuevoConcepto({...nuevoConcepto, valor_unitario: valor, importe: nuevoConcepto.cantidad * valor})
                    }}
                    className="px-3 py-2 border rounded-lg bg-white dark:bg-gray-700" />
                  <input type="text" disabled value={formatCurrency(nuevoConcepto.importe)}
                    className="px-3 py-2 border rounded-lg bg-gray-100 dark:bg-gray-800" />
                  <button type="button"
                    onClick={() => {
                      if (nuevoConcepto.descripcion && nuevoConcepto.valor_unitario > 0) {
                        setFormData({...formData, conceptos: [...formData.conceptos, nuevoConcepto]})
                        setNuevoConcepto({clave_prod_serv: '85121800', cantidad: 1, unidad: 'E48', descripcion: '', valor_unitario: 0, importe: 0})
                      }
                    }}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                    <Plus className="w-4 h-4" />
                  </button>
                </div>

                {formData.conceptos.length > 0 && (
                  <div className="space-y-2">
                    {formData.conceptos.map((concepto, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
                        <div className="flex-1">
                          <span className="font-medium">{concepto.descripcion}</span>
                          <span className="text-sm text-gray-500 ml-2">
                            {concepto.cantidad} x {formatCurrency(concepto.valor_unitario)} = {formatCurrency(concepto.importe)}
                          </span>
                        </div>
                        <button type="button"
                          onClick={() => setFormData({...formData, conceptos: formData.conceptos.filter((_, i) => i !== index)})}
                          className="text-red-600 hover:text-red-800">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                    <div className="text-right pt-3 border-t">
                      <p className="text-sm text-gray-500">Subtotal: {formatCurrency(formData.conceptos.reduce((sum, c) => sum + c.importe, 0))}</p>
                      <p className="text-sm text-gray-500">IVA (16%): {formatCurrency(formData.conceptos.reduce((sum, c) => sum + c.importe, 0) * 0.16)}</p>
                      <p className="text-lg font-bold">Total: {formatCurrency(formData.conceptos.reduce((sum, c) => sum + c.importe, 0) * 1.16)}</p>
                    </div>
                  </div>
                )}
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t">
                <button type="button" onClick={() => setMostrarFormulario(false)}
                  className="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg">Cancelar</button>
                <button type="submit" disabled={guardando || formData.conceptos.length === 0}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
                  {guardando ? 'Guardando...' : 'Crear Factura'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal de Visualización de Detalles */}
      {facturaSeleccionada && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-50">
                Detalle de Factura {facturaSeleccionada.serie}-{facturaSeleccionada.folio}
              </h3>
              <button
                onClick={() => setFacturaSeleccionada(null)}
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
                  <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getEstadoBadge(facturaSeleccionada.estado)}`}>
                    {getEstadoIcon(facturaSeleccionada.estado)}
                    {facturaSeleccionada.estado}
                  </span>
                </div>
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Fecha de Emisión</p>
                  <p className="font-medium">{new Date(facturaSeleccionada.fecha_emision).toLocaleString()}</p>
                </div>
                {facturaSeleccionada.uuid_sat && (
                  <div className="col-span-2">
                    <p className="text-sm text-gray-500 dark:text-gray-400">UUID SAT</p>
                    <p className="font-mono text-sm">{facturaSeleccionada.uuid_sat}</p>
                  </div>
                )}
              </div>

              {/* Datos del Receptor */}
              <div>
                <h4 className="font-semibold mb-3">Datos del Receptor</h4>
                <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Nombre</p>
                    <p className="font-medium">{facturaSeleccionada.receptor_nombre}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">RFC</p>
                    <p className="font-medium">{facturaSeleccionada.receptor_rfc}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Uso CFDI</p>
                    <p className="font-medium">{facturaSeleccionada.uso_cfdi}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Método de Pago</p>
                    <p className="font-medium">{facturaSeleccionada.metodo_pago}</p>
                  </div>
                </div>
              </div>

              {/* Conceptos */}
              <div>
                <h4 className="font-semibold mb-3">Conceptos</h4>
                <div className="space-y-2">
                  {facturaSeleccionada.conceptos.map((concepto, idx) => (
                    <div key={idx} className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                      <p className="font-medium">{concepto.descripcion}</p>
                      <div className="grid grid-cols-4 gap-2 mt-2 text-sm text-gray-600 dark:text-gray-400">
                        <div>
                          <span className="text-gray-500">Cantidad:</span> {concepto.cantidad}
                        </div>
                        <div>
                          <span className="text-gray-500">Precio:</span> {formatCurrency(concepto.valor_unitario)}
                        </div>
                        <div>
                          <span className="text-gray-500">Importe:</span> {formatCurrency(concepto.importe)}
                        </div>
                        <div>
                          <span className="text-gray-500">Clave:</span> {concepto.clave_prod_serv}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Totales */}
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div className="flex justify-between mb-2">
                  <span className="text-gray-600 dark:text-gray-400">Subtotal:</span>
                  <span className="font-medium">{formatCurrency(facturaSeleccionada.subtotal)}</span>
                </div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-600 dark:text-gray-400">IVA (16%):</span>
                  <span className="font-medium">{formatCurrency(facturaSeleccionada.total - facturaSeleccionada.subtotal)}</span>
                </div>
                <div className="flex justify-between pt-2 border-t border-blue-200 dark:border-blue-800">
                  <span className="text-lg font-bold">Total:</span>
                  <span className="text-lg font-bold text-blue-600">{formatCurrency(facturaSeleccionada.total)}</span>
                </div>
              </div>

              <div className="flex justify-end">
                <button
                  onClick={() => setFacturaSeleccionada(null)}
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
