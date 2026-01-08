import React, { useState, useEffect } from 'react';
import {
  FileText,
  Plus,
  Search,
  CheckCircle,
  XCircle,
  Clock,
  Eye,
  Printer,
  AlertCircle,
  Trash2,
} from 'lucide-react';
import {
  listarRecetas,
  generarRecetaElectronica,
  validarRecetaElectronica,
  RecetaElectronica,
  MedicamentoReceta,
} from '../../services/integracionesService';
import { pacienteService } from '../../services/pacienteService';
import { useAuthStore } from '../../store/authStore';

const RecetaElectronicaComponent: React.FC = () => {
  const { user } = useAuthStore();
  const [recetas, setRecetas] = useState<RecetaElectronica[]>([]);
  const [loading, setLoading] = useState(true);
  const [filtroEstado, setFiltroEstado] = useState<string>('');
  const [busqueda, setBusqueda] = useState('');
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [recetaSeleccionada, setRecetaSeleccionada] = useState<RecetaElectronica | null>(null);
  const [pacientes, setPacientes] = useState<any[]>([]);
  const [guardando, setGuardando] = useState(false);
  
  const [formData, setFormData] = useState({
    paciente_id: '',
    consulta_id: null as string | null,
    diagnostico_cie10: '',
    indicaciones_generales: '',
    medicamentos: [] as MedicamentoReceta[]
  });
  
  const [nuevoMedicamento, setNuevoMedicamento] = useState<MedicamentoReceta>({
    nombre_generico: '',
    nombre_comercial: '',
    presentacion: '',
    dosis: '',
    frecuencia: '',
    via: 'ORAL',
    duracion_dias: 7,
    cantidad: 1,
    indicaciones: ''
  });

  useEffect(() => {
    cargarRecetas();
    cargarPacientes();
  }, [filtroEstado]);

  const cargarRecetas = async () => {
    try {
      setLoading(true);
      const data = await listarRecetas(undefined, undefined, filtroEstado || undefined);
      setRecetas(data);
    } catch (error) {
      console.error('Error al cargar recetas:', error);
    } finally {
      setLoading(false);
    }
  };

  const cargarPacientes = async () => {
    try {
      const data = await pacienteService.listar();
      setPacientes(data);
    } catch (error) {
      console.error('Error al cargar pacientes:', error);
    }
  };

  const agregarMedicamento = () => {
    if (!nuevoMedicamento.nombre_generico || !nuevoMedicamento.dosis || !nuevoMedicamento.frecuencia) {
      alert('Complete los campos obligatorios del medicamento');
      return;
    }
    setFormData({
      ...formData,
      medicamentos: [...formData.medicamentos, nuevoMedicamento]
    });
    setNuevoMedicamento({
      nombre_generico: '',
      nombre_comercial: '',
      presentacion: '',
      dosis: '',
      frecuencia: '',
      via: 'ORAL',
      duracion_dias: 7,
      cantidad: 1,
      indicaciones: ''
    });
  };

  const eliminarMedicamento = (index: number) => {
    setFormData({
      ...formData,
      medicamentos: formData.medicamentos.filter((_, i) => i !== index)
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.medicamentos.length === 0) {
      alert('Debe agregar al menos un medicamento');
      return;
    }
    try {
      setGuardando(true);
      
      if (!user?.id) {
        alert('Error: No se pudo obtener el ID del médico');
        return;
      }
      
      // Agregar medico_id al formData
      const recetaData = {
        ...formData,
        medico_id: user.id
      };
      
      console.log('📤 Enviando receta:', recetaData);
      await generarRecetaElectronica(recetaData);
      setMostrarFormulario(false);
      cargarRecetas();
      alert('Receta electrónica generada exitosamente');
      // Resetear formulario
      setFormData({
        paciente_id: '',
        consulta_id: null,
        diagnostico_cie10: '',
        indicaciones_generales: '',
        medicamentos: []
      });
    } catch (error: any) {
      console.error('❌ Error completo al generar receta:', error);
      console.error('📝 Response data:', error.response?.data);
      console.error('📝 Error message:', error.message);
      
      let mensajeError = 'Error desconocido';
      if (error.response?.data) {
        if (typeof error.response.data === 'string') {
          mensajeError = error.response.data;
        } else if (error.response.data.detail) {
          if (typeof error.response.data.detail === 'string') {
            mensajeError = error.response.data.detail;
          } else if (Array.isArray(error.response.data.detail)) {
            mensajeError = error.response.data.detail.map((e: any) => 
              `${e.loc?.join('.')}: ${e.msg}`
            ).join('\n');
          } else {
            mensajeError = JSON.stringify(error.response.data.detail);
          }
        } else {
          mensajeError = JSON.stringify(error.response.data);
        }
      } else if (error.message) {
        mensajeError = error.message;
      }
      
      alert(`Error al generar receta:\n${mensajeError}`);
    } finally {
      setGuardando(false);
    }
  };

  const getEstadoBadge = (estado: string) => {
    const badges: Record<string, { bg: string; text: string; icon: React.ReactNode }> = {
      ACTIVA: {
        bg: 'bg-green-100 text-green-800',
        text: 'Activa',
        icon: <CheckCircle className="h-4 w-4" />,
      },
      SURTIDA: {
        bg: 'bg-blue-100 text-blue-800',
        text: 'Surtida',
        icon: <CheckCircle className="h-4 w-4" />,
      },
      VENCIDA: {
        bg: 'bg-red-100 text-red-800',
        text: 'Vencida',
        icon: <XCircle className="h-4 w-4" />,
      },
      CANCELADA: {
        bg: 'bg-gray-100 text-gray-800',
        text: 'Cancelada',
        icon: <XCircle className="h-4 w-4" />,
      },
    };
    return badges[estado] || badges.ACTIVA;
  };

  const recetasFiltradas = recetas.filter((receta) =>
    receta.folio.toLowerCase().includes(busqueda.toLowerCase()) ||
    receta.codigo_verificacion.toLowerCase().includes(busqueda.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-50">
            Receta Electrónica
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Gestión de recetas electrónicas con firma digital
          </p>
        </div>
        <button
          onClick={() => setMostrarFormulario(true)}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2"
        >
          <Plus className="h-4 w-4" />
          Nueva Receta
        </button>
      </div>

      {/* Filtros */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Búsqueda */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por folio o código..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-gray-100"
            />
          </div>

          {/* Filtro Estado */}
          <select
            value={filtroEstado}
            onChange={(e) => setFiltroEstado(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-gray-100"
          >
            <option value="">Todos los estados</option>
            <option value="ACTIVA">Activa</option>
            <option value="SURTIDA">Surtida</option>
            <option value="VENCIDA">Vencida</option>
            <option value="CANCELADA">Cancelada</option>
          </select>
        </div>
      </div>

      {/* Lista de Recetas */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
          </div>
        ) : recetasFiltradas.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-50">
              No hay recetas
            </h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {busqueda || filtroEstado
                ? 'No se encontraron recetas con los filtros aplicados'
                : 'Comienza generando tu primera receta electrónica'}
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {recetasFiltradas.map((receta) => {
              const badge = getEstadoBadge(receta.estado);
              return (
                <div
                  key={receta.id}
                  className="p-6 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      {/* Header */}
                      <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                          <FileText className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                            {receta.folio}
                          </h3>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            Código: {receta.codigo_verificacion}
                          </p>
                        </div>
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1 ${badge.bg}`}
                        >
                          {badge.icon}
                          {badge.text}
                        </span>
                      </div>

                      {/* Información */}
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Fecha emisión:</span>
                          <p className="font-medium text-gray-900 dark:text-gray-50">
                            {new Date(receta.fecha_emision).toLocaleDateString('es-MX')}
                          </p>
                        </div>
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Vencimiento:</span>
                          <p className="font-medium text-gray-900 dark:text-gray-50">
                            {receta.fecha_vencimiento
                              ? new Date(receta.fecha_vencimiento).toLocaleDateString('es-MX')
                              : 'N/A'}
                          </p>
                        </div>
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Medicamentos:</span>
                          <p className="font-medium text-gray-900 dark:text-gray-50">
                            {receta.medicamentos.length}
                          </p>
                        </div>
                      </div>

                      {/* Medicamentos */}
                      {receta.medicamentos.length > 0 && (
                        <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                          <p className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Medicamentos:
                          </p>
                          <div className="space-y-1">
                            {receta.medicamentos.slice(0, 3).map((med: any, idx: number) => (
                              <p key={idx} className="text-sm text-gray-600 dark:text-gray-400">
                                • {med.nombre_generico} - {med.presentacion} ({med.cantidad})
                              </p>
                            ))}
                            {receta.medicamentos.length > 3 && (
                              <p className="text-sm text-gray-500 dark:text-gray-400">
                                + {receta.medicamentos.length - 3} más...
                              </p>
                            )}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Acciones */}
                    <div className="flex gap-2 ml-4">
                      <button
                        onClick={() => setRecetaSeleccionada(receta)}
                        className="p-2 text-gray-600 hover:text-purple-600 hover:bg-purple-50 dark:hover:bg-purple-900/30 rounded-lg transition-colors"
                        title="Ver detalle"
                      >
                        <Eye className="h-5 w-5" />
                      </button>
                      <button
                        onClick={() => {
                          /* TODO: Imprimir receta */
                        }}
                        className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition-colors"
                        title="Imprimir"
                      >
                        <Printer className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
              <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-50">
                {recetas.filter((r) => r.estado === 'ACTIVA').length}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">Activas</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <CheckCircle className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-50">
                {recetas.filter((r) => r.estado === 'SURTIDA').length}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">Surtidas</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg">
              <XCircle className="h-6 w-6 text-red-600 dark:text-red-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-50">
                {recetas.filter((r) => r.estado === 'VENCIDA').length}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">Vencidas</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
              <FileText className="h-6 w-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-50">
                {recetas.length}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">Total</p>
            </div>
          </div>
        </div>
      </div>

      {/* Modal de Visualización de Detalles */}
      {recetaSeleccionada && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-50">
                Detalle de Receta {recetaSeleccionada.folio}
              </h3>
              <button
                onClick={() => setRecetaSeleccionada(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-6">
              {/* Información General */}
              <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Estado</p>
                  <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getEstadoBadge(recetaSeleccionada.estado).bg}`}>
                    {getEstadoBadge(recetaSeleccionada.estado).icon}
                    {recetaSeleccionada.estado}
                  </span>
                </div>
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Fecha de Emisión</p>
                  <p className="font-medium">{new Date(recetaSeleccionada.fecha_emision).toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Código de Verificación</p>
                  <p className="font-mono text-sm">{recetaSeleccionada.codigo_verificacion}</p>
                </div>
                {recetaSeleccionada.fecha_vencimiento && (
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Fecha de Vencimiento</p>
                    <p className="font-medium">{new Date(recetaSeleccionada.fecha_vencimiento).toLocaleDateString()}</p>
                  </div>
                )}
              </div>

              {/* Medicamentos */}
              <div>
                <h4 className="font-semibold mb-3">Medicamentos Prescritos</h4>
                <div className="space-y-2">
                  {recetaSeleccionada.medicamentos.map((med: any, idx: number) => (
                    <div key={idx} className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <p className="font-medium text-gray-900 dark:text-gray-50">{med.nombre_generico}</p>
                          {med.nombre_comercial && (
                            <p className="text-sm text-gray-500 dark:text-gray-400">({med.nombre_comercial})</p>
                          )}
                          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                            {med.presentacion} - {med.dosis}
                          </p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            Frecuencia: {med.frecuencia} | Vía: {med.via} | Duración: {med.duracion_dias} días
                          </p>
                          {med.indicaciones && (
                            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 italic">
                              {med.indicaciones}
                            </p>
                          )}
                        </div>
                        <div className="text-right">
                          <p className="font-semibold text-gray-900 dark:text-gray-50">Cantidad: {med.cantidad}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex justify-end">
                <button
                  onClick={() => setRecetaSeleccionada(null)}
                  className="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600"
                >
                  Cerrar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Formulario Nueva Receta */}
      {mostrarFormulario && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-4xl w-full my-8">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-50">Nueva Receta Electrónica</h3>
              <button
                onClick={() => setMostrarFormulario(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle className="w-6 h-6" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Datos del Paciente */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Paciente *</label>
                  <select
                    required
                    value={formData.paciente_id}
                    onChange={(e) => setFormData({...formData, paciente_id: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700"
                  >
                    <option value="">Seleccionar paciente...</option>
                    {pacientes.map(p => (
                      <option key={p.id} value={p.id}>{p.nombre_completo}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Diagnóstico CIE-10</label>
                  <input
                    type="text"
                    value={formData.diagnostico_cie10}
                    onChange={(e) => setFormData({...formData, diagnostico_cie10: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700"
                    placeholder="Ej: J00 (Rinofaringitis aguda)"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Indicaciones Generales</label>
                <textarea
                  value={formData.indicaciones_generales}
                  onChange={(e) => setFormData({...formData, indicaciones_generales: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700"
                  rows={3}
                  placeholder="Indicaciones generales para el paciente..."
                />
              </div>

              {/* Agregar Medicamento */}
              <div className="border-t pt-4">
                <h4 className="text-lg font-semibold mb-4">Agregar Medicamento</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">
                  <input
                    type="text"
                    placeholder="Nombre Genérico *"
                    value={nuevoMedicamento.nombre_generico}
                    onChange={(e) => setNuevoMedicamento({...nuevoMedicamento, nombre_generico: e.target.value})}
                    className="px-3 py-2 border rounded-lg bg-white dark:bg-gray-700"
                  />
                  <input
                    type="text"
                    placeholder="Nombre Comercial"
                    value={nuevoMedicamento.nombre_comercial}
                    onChange={(e) => setNuevoMedicamento({...nuevoMedicamento, nombre_comercial: e.target.value})}
                    className="px-3 py-2 border rounded-lg bg-white dark:bg-gray-700"
                  />
                  <input
                    type="text"
                    placeholder="Presentación (ej: Tabletas 500mg)"
                    value={nuevoMedicamento.presentacion}
                    onChange={(e) => setNuevoMedicamento({...nuevoMedicamento, presentacion: e.target.value})}
                    className="px-3 py-2 border rounded-lg bg-white dark:bg-gray-700"
                  />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-3">
                  <input
                    type="text"
                    placeholder="Dosis *"
                    value={nuevoMedicamento.dosis}
                    onChange={(e) => setNuevoMedicamento({...nuevoMedicamento, dosis: e.target.value})}
                    className="px-3 py-2 border rounded-lg bg-white dark:bg-gray-700"
                  />
                  <input
                    type="text"
                    placeholder="Frecuencia * (ej: Cada 8 hrs)"
                    value={nuevoMedicamento.frecuencia}
                    onChange={(e) => setNuevoMedicamento({...nuevoMedicamento, frecuencia: e.target.value})}
                    className="px-3 py-2 border rounded-lg bg-white dark:bg-gray-700"
                  />
                  <select
                    value={nuevoMedicamento.via}
                    onChange={(e) => setNuevoMedicamento({...nuevoMedicamento, via: e.target.value})}
                    className="px-3 py-2 border rounded-lg bg-white dark:bg-gray-700"
                  >
                    <option value="ORAL">Oral</option>
                    <option value="INTRAVENOSA">Intravenosa</option>
                    <option value="INTRAMUSCULAR">Intramuscular</option>
                    <option value="SUBCUTANEA">Subcutánea</option>
                    <option value="TOPICA">Tópica</option>
                    <option value="OFTALMICA">Oftálmica</option>
                    <option value="OTICA">Ótica</option>
                    <option value="NASAL">Nasal</option>
                    <option value="RECTAL">Rectal</option>
                  </select>
                  <input
                    type="number"
                    placeholder="Duración (días)"
                    value={nuevoMedicamento.duracion_dias}
                    onChange={(e) => setNuevoMedicamento({...nuevoMedicamento, duracion_dias: parseInt(e.target.value)})}
                    className="px-3 py-2 border rounded-lg bg-white dark:bg-gray-700"
                  />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                  <input
                    type="number"
                    placeholder="Cantidad"
                    value={nuevoMedicamento.cantidad}
                    onChange={(e) => setNuevoMedicamento({...nuevoMedicamento, cantidad: parseInt(e.target.value)})}
                    className="px-3 py-2 border rounded-lg bg-white dark:bg-gray-700"
                  />
                  <input
                    type="text"
                    placeholder="Indicaciones específicas"
                    value={nuevoMedicamento.indicaciones}
                    onChange={(e) => setNuevoMedicamento({...nuevoMedicamento, indicaciones: e.target.value})}
                    className="px-3 py-2 border rounded-lg bg-white dark:bg-gray-700"
                  />
                </div>
                <button
                  type="button"
                  onClick={agregarMedicamento}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                >
                  <Plus className="w-4 h-4 inline mr-2" />
                  Agregar Medicamento
                </button>
              </div>

              {/* Lista de Medicamentos Agregados */}
              {formData.medicamentos.length > 0 && (
                <div className="border-t pt-4">
                  <h4 className="text-lg font-semibold mb-4">Medicamentos en la Receta ({formData.medicamentos.length})</h4>
                  <div className="space-y-2">
                    {formData.medicamentos.map((med, idx) => (
                      <div key={idx} className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg flex justify-between items-start">
                        <div className="flex-1">
                          <p className="font-medium">{med.nombre_generico}</p>
                          {med.nombre_comercial && <p className="text-sm text-gray-500">({med.nombre_comercial})</p>}
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {med.presentacion} - {med.dosis} - {med.frecuencia} - Vía: {med.via} - {med.duracion_dias} días
                          </p>
                          <p className="text-sm">Cantidad: {med.cantidad}</p>
                          {med.indicaciones && <p className="text-sm text-gray-500 italic">{med.indicaciones}</p>}
                        </div>
                        <button
                          type="button"
                          onClick={() => eliminarMedicamento(idx)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Botones */}
              <div className="flex justify-end gap-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={() => setMostrarFormulario(false)}
                  className="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={guardando}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
                >
                  {guardando ? 'Generando...' : 'Generar Receta Electrónica'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default RecetaElectronicaComponent;
