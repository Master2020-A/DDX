import React, { useState, useEffect } from 'react';
import {
  Building2,
  ArrowLeftRight,
  Shield,
  Activity,
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle,
  Download,
  Users,
  FileText,
  Plus,
  Edit,
  Trash2,
  Eye,
  Search,
} from 'lucide-react';
import {
  listarInstitucionesExternas,
  listarSolicitudesIntercambio,
  obtenerEstadisticasIntercambio,
  aprobarSolicitudIntercambio,
  rechazarSolicitudIntercambio,
  generarExpedienteFHIR,
  crearInstitucionExterna,
  actualizarInstitucionExterna,
  eliminarInstitucionExterna,
  crearSolicitudIntercambio,
  InstitucionExterna,
  SolicitudIntercambio,
  EstadisticasIntercambio,
} from '../services/interoperabilidadService';
import FormularioInstitucion from '../components/interoperabilidad/FormularioInstitucion';
import FormularioSolicitud from '../components/interoperabilidad/FormularioSolicitud';

const Interoperabilidad: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'instituciones' | 'solicitudes' | 'consentimientos'>('dashboard');
  const [instituciones, setInstituciones] = useState<InstitucionExterna[]>([]);
  const [solicitudes, setSolicitudes] = useState<SolicitudIntercambio[]>([]);
  const [estadisticas, setEstadisticas] = useState<EstadisticasIntercambio | null>(null);
  const [loading, setLoading] = useState(false);
  const [mostrarFormInstitucion, setMostrarFormInstitucion] = useState(false);
  const [mostrarFormSolicitud, setMostrarFormSolicitud] = useState(false);
  const [institucionEditar, setInstitucionEditar] = useState<InstitucionExterna | undefined>();
  const [busqueda, setBusqueda] = useState('');

  useEffect(() => {
    cargarDatos();
  }, [activeTab]);

  const cargarDatos = async () => {
    setLoading(true);
    try {
      if (activeTab === 'dashboard') {
        const stats = await obtenerEstadisticasIntercambio(30);
        setEstadisticas(stats);
      } else if (activeTab === 'instituciones') {
        const data = await listarInstitucionesExternas({ limit: 100 });
        setInstituciones(data);
      } else if (activeTab === 'solicitudes') {
        const data = await listarSolicitudesIntercambio({ limit: 100 });
        setSolicitudes(data);
      }
    } catch (error) {
      console.error('Error cargando datos:', error);
    } finally {
      setLoading(false);
    }
  };

  // Funciones CRUD para Instituciones
  const handleCrearInstitucion = async (data: Partial<InstitucionExterna>) => {
    await crearInstitucionExterna(data);
    setMostrarFormInstitucion(false);
    cargarDatos();
  };

  const handleEditarInstitucion = (institucion: InstitucionExterna) => {
    setInstitucionEditar(institucion);
    setMostrarFormInstitucion(true);
  };

  const handleActualizarInstitucion = async (data: Partial<InstitucionExterna>) => {
    if (institucionEditar?.id) {
      await actualizarInstitucionExterna(institucionEditar.id, data);
      setMostrarFormInstitucion(false);
      setInstitucionEditar(undefined);
      cargarDatos();
    }
  };

  const handleEliminarInstitucion = async (id: string) => {
    if (window.confirm('¿Está seguro de eliminar esta institución?')) {
      try {
        await eliminarInstitucionExterna(id);
        cargarDatos();
      } catch (error) {
        alert('Error al eliminar la institución');
      }
    }
  };

  // Funciones para Solicitudes
  const handleCrearSolicitud = async (data: any) => {
    await crearSolicitudIntercambio(data);
    setMostrarFormSolicitud(false);
    cargarDatos();
  };

  const handleAprobarSolicitud = async (id: string) => {
    try {
      await aprobarSolicitudIntercambio(id);
      alert('Solicitud aprobada exitosamente');
      cargarDatos();
    } catch (error) {
      alert('Error al aprobar solicitud');
    }
  };

  const handleRechazarSolicitud = async (id: string) => {
    const motivo = prompt('Ingrese el motivo del rechazo:');
    if (!motivo) return;

    try {
      await rechazarSolicitudIntercambio(id, motivo);
      alert('Solicitud rechazada');
      cargarDatos();
    } catch (error) {
      alert('Error al rechazar solicitud');
    }
  };

  const handleGenerarExpediente = async (id: string) => {
    try {
      const expediente = await generarExpedienteFHIR(id);
      const blob = new Blob([JSON.stringify(expediente.bundle, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `expediente-fhir-${id}.json`;
      a.click();
      alert('Expediente FHIR generado y descargado');
      cargarDatos();
    } catch (error) {
      alert('Error al generar expediente FHIR');
    }
  };

  const getEstadoBadge = (estado: string) => {
    const badges: Record<string, { color: string; icon: React.ReactNode; text: string }> = {
      pendiente: { color: 'bg-yellow-100 text-yellow-800', icon: <Clock className="w-4 h-4" />, text: 'Pendiente' },
      aprobada: { color: 'bg-green-100 text-green-800', icon: <CheckCircle className="w-4 h-4" />, text: 'Aprobada' },
      rechazada: { color: 'bg-red-100 text-red-800', icon: <XCircle className="w-4 h-4" />, text: 'Rechazada' },
      en_proceso: { color: 'bg-blue-100 text-blue-800', icon: <Activity className="w-4 h-4" />, text: 'En Proceso' },
      completada: { color: 'bg-green-100 text-green-800', icon: <CheckCircle className="w-4 h-4" />, text: 'Completada' },
      error: { color: 'bg-red-100 text-red-800', icon: <AlertCircle className="w-4 h-4" />, text: 'Error' },
    };

    const badge = badges[estado] || badges.pendiente;

    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${badge.color}`}>
        {badge.icon}
        {badge.text}
      </span>
    );
  };

  const institucionesFiltradas = instituciones.filter((inst) =>
    inst.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
    inst.codigo_institucional.toLowerCase().includes(busqueda.toLowerCase()) ||
    inst.ciudad.toLowerCase().includes(busqueda.toLowerCase())
  );

  const renderDashboard = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Solicitudes</p>
              <p className="text-2xl font-bold text-gray-900">{estadisticas?.total_solicitudes || 0}</p>
            </div>
            <ArrowLeftRight className="w-10 h-10 text-blue-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Instituciones Activas</p>
              <p className="text-2xl font-bold text-gray-900">{estadisticas?.instituciones_activas || 0}</p>
            </div>
            <Building2 className="w-10 h-10 text-green-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Pacientes con Consentimiento</p>
              <p className="text-2xl font-bold text-gray-900">{estadisticas?.pacientes_con_consentimiento || 0}</p>
            </div>
            <Shield className="w-10 h-10 text-purple-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Completadas</p>
              <p className="text-2xl font-bold text-gray-900">{estadisticas?.solicitudes_completadas || 0}</p>
            </div>
            <CheckCircle className="w-10 h-10 text-green-500" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Solicitudes por Estado</h3>
          <div className="space-y-2">
            {estadisticas?.solicitudes_por_estado && Object.entries(estadisticas.solicitudes_por_estado).map(([estado, count]) => (
              <div key={estado} className="flex items-center justify-between">
                <span className="capitalize">{estado.replace('_', ' ')}</span>
                <span className="font-semibold">{count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Solicitudes por Tipo</h3>
          <div className="space-y-2">
            {estadisticas?.solicitudes_por_tipo && Object.entries(estadisticas.solicitudes_por_tipo).map(([tipo, count]) => (
              <div key={tipo} className="flex items-center justify-between">
                <span className="capitalize">{tipo.replace('_', ' ')}</span>
                <span className="font-semibold">{count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderInstituciones = () => (
    <div className="space-y-4">
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Buscar instituciones..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button
            onClick={() => {
              setInstitucionEditar(undefined);
              setMostrarFormInstitucion(true);
            }}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            <Plus className="w-5 h-5" />
            Nueva Institución
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nombre</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Código</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nivel</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ubicación</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Protocolos</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {institucionesFiltradas.map((inst) => (
                <tr key={inst.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      <Building2 className="w-5 h-5 text-gray-400 mr-2" />
                      <div>
                        <div className="text-sm font-medium text-gray-900">{inst.nombre}</div>
                        <div className="text-xs text-gray-500">{inst.tipo_institucion}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">{inst.codigo_institucional}</td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded capitalize">
                      {inst.nivel_atencion}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {inst.ciudad}, {inst.estado}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-1">
                      {inst.protocolos_soportados?.slice(0, 2).map((protocolo) => (
                        <span key={protocolo} className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                          {protocolo}
                        </span>
                      ))}
                      {inst.protocolos_soportados && inst.protocolos_soportados.length > 2 && (
                        <span className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                          +{inst.protocolos_soportados.length - 2}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded ${inst.activa ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {inst.activa ? 'Activa' : 'Inactiva'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => handleEditarInstitucion(inst)}
                        className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                        title="Editar"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleEliminarInstitucion(inst.id)}
                        className="p-1 text-red-600 hover:bg-red-50 rounded"
                        title="Eliminar"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderSolicitudes = () => (
    <div className="space-y-4">
      <div className="bg-white rounded-lg shadow p-4 flex justify-end">
        <button
          onClick={() => {
            const pacienteId = prompt('Ingrese el ID del paciente:');
            if (pacienteId) {
              setMostrarFormSolicitud(true);
            }
          }}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          <Plus className="w-5 h-5" />
          Nueva Solicitud
        </button>
      </div>

      <div className="space-y-4">
        {solicitudes.map((solicitud) => (
          <div key={solicitud.id} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h4 className="text-lg font-semibold text-gray-900 capitalize">
                    {solicitud.tipo_intercambio.replace('_', ' ')}
                  </h4>
                  {getEstadoBadge(solicitud.estado)}
                  <span className={`px-2 py-1 text-xs font-medium rounded ${
                    solicitud.prioridad === 'urgente' ? 'bg-red-100 text-red-800' :
                    solicitud.prioridad === 'alta' ? 'bg-orange-100 text-orange-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {solicitud.prioridad}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-2">{solicitud.motivo_solicitud}</p>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span>Protocolo: {solicitud.protocolo}</span>
                  <span>Creada: {new Date(solicitud.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            </div>

            {solicitud.estado === 'pendiente' && (
              <div className="flex gap-2 pt-4 border-t border-gray-200">
                <button
                  onClick={() => handleAprobarSolicitud(solicitud.id)}
                  className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm"
                >
                  <CheckCircle className="w-4 h-4" />
                  Aprobar
                </button>
                <button
                  onClick={() => handleRechazarSolicitud(solicitud.id)}
                  className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 text-sm"
                >
                  <XCircle className="w-4 h-4" />
                  Rechazar
                </button>
              </div>
            )}

            {(solicitud.estado === 'aprobada' || solicitud.estado === 'en_proceso') && (
              <div className="flex gap-2 pt-4 border-t border-gray-200">
                <button
                  onClick={() => handleGenerarExpediente(solicitud.id)}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
                >
                  <Download className="w-4 h-4" />
                  Generar Expediente FHIR
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );

  const renderConsentimientos = () => (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="text-center py-12">
        <Shield className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Gestión de Consentimientos</h3>
        <p className="text-gray-600">
          Aquí se gestionarán los consentimientos de pacientes para compartir información.
        </p>
      </div>
    </div>
  );

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <ArrowLeftRight className="w-8 h-8" />
          Interoperabilidad HL7 FHIR
        </h1>
        <p className="text-gray-600 mt-2">Red Nacional de Salud e Intercambio de Expedientes</p>
      </div>

      <div className="mb-6 border-b border-gray-200">
        <nav className="flex space-x-8">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'dashboard'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Activity className="w-5 h-5 inline mr-2" />
            Dashboard
          </button>
          <button
            onClick={() => setActiveTab('instituciones')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'instituciones'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Building2 className="w-5 h-5 inline mr-2" />
            Instituciones
          </button>
          <button
            onClick={() => setActiveTab('solicitudes')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'solicitudes'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <ArrowLeftRight className="w-5 h-5 inline mr-2" />
            Solicitudes
          </button>
          <button
            onClick={() => setActiveTab('consentimientos')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'consentimientos'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Shield className="w-5 h-5 inline mr-2" />
            Consentimientos
          </button>
        </nav>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="text-gray-600">Cargando...</div>
        </div>
      ) : (
        <>
          {activeTab === 'dashboard' && renderDashboard()}
          {activeTab === 'instituciones' && renderInstituciones()}
          {activeTab === 'solicitudes' && renderSolicitudes()}
          {activeTab === 'consentimientos' && renderConsentimientos()}
        </>
      )}

      {mostrarFormInstitucion && (
        <FormularioInstitucion
          institucion={institucionEditar}
          onClose={() => {
            setMostrarFormInstitucion(false);
            setInstitucionEditar(undefined);
          }}
          onSave={institucionEditar ? handleActualizarInstitucion : handleCrearInstitucion}
        />
      )}

      {mostrarFormSolicitud && (
        <FormularioSolicitud
          pacienteId={prompt('ID del paciente') || ''}
          instituciones={instituciones}
          onClose={() => setMostrarFormSolicitud(false)}
          onSave={handleCrearSolicitud}
        />
      )}
    </div>
  );
};

export default Interoperabilidad;
