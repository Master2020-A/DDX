import React, { useState, useEffect } from "react";
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
} from "lucide-react";
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
  InstitucionExterna,
  SolicitudIntercambio,
  EstadisticasIntercambio,
} from "../services/interoperabilidadService";
import FormularioInstitucion from "../components/interoperabilidad/FormularioInstitucion";
import FormularioSolicitud from "../components/interoperabilidad/FormularioSolicitud";
import DashboardMetricas from "../components/interoperabilidad/DashboardMetricas";
import NotificacionesPanel from "../components/interoperabilidad/NotificacionesPanel";

const Interoperabilidad: React.FC = () => {
  const [activeTab, setActiveTab] = useState<
    "dashboard" | "metricas" | "instituciones" | "solicitudes" | "consentimientos"
  >("dashboard");
  const [instituciones, setInstituciones] = useState<InstitucionExterna[]>([]);
  const [solicitudes, setSolicitudes] = useState<SolicitudIntercambio[]>([]);
  const [estadisticas, setEstadisticas] =
    useState<EstadisticasIntercambio | null>(null);
  const [loading, setLoading] = useState(false);
  const [mostrarFormInstitucion, setMostrarFormInstitucion] = useState(false);
  const [mostrarFormSolicitud, setMostrarFormSolicitud] = useState(false);
  const [institucionEditar, setInstitucionEditar] =
    useState<InstitucionExterna | undefined>();

  useEffect(() => {
    cargarDatos();
  }, [activeTab]);

  const cargarDatos = async () => {
    setLoading(true);
    try {
      if (activeTab === "dashboard") {
        const stats = await obtenerEstadisticasIntercambio(30);
        setEstadisticas(stats);
      } else if (activeTab === "instituciones") {
        const data = await listarInstitucionesExternas({ limit: 100 });
        setInstituciones(data);
      } else if (activeTab === "solicitudes") {
        const data = await listarSolicitudesIntercambio({ limit: 100 });
        setSolicitudes(data);
      }
    } catch (error) {
      console.error("Error cargando datos:", error);
    } finally {
      setLoading(false);
    }
  };

  // CRUD Instituciones
  const handleCrearInstitucion = async (data: Partial<InstitucionExterna>) => {
    await crearInstitucionExterna(data);
    setMostrarFormInstitucion(false);
    cargarDatos();
  };

  const handleEditarInstitucion = (institucion: InstitucionExterna) => {
    setInstitucionEditar(institucion);
    setMostrarFormInstitucion(true);
  };

  const handleActualizarInstitucion = async (
    data: Partial<InstitucionExterna>
  ) => {
    if (institucionEditar?.id) {
      await actualizarInstitucionExterna(institucionEditar.id, data);
      setMostrarFormInstitucion(false);
      setInstitucionEditar(undefined);
      cargarDatos();
    }
  };

  const handleEliminarInstitucion = async (id: string) => {
    if (window.confirm("¿Está seguro de eliminar esta institución?")) {
      try {
        await eliminarInstitucionExterna(id);
        cargarDatos();
      } catch (error) {
        alert("Error al eliminar la institución");
      }
    }
  };

  // Solicitudes
  const handleAprobarSolicitud = async (id: string) => {
    try {
      await aprobarSolicitudIntercambio(id);
      alert("Solicitud aprobada exitosamente");
      cargarDatos();
    } catch (error) {
      console.error("Error aprobando solicitud:", error);
      alert("Error al aprobar solicitud");
    }
  };

  const handleRechazarSolicitud = async (id: string) => {
    const motivo = prompt("Ingrese el motivo del rechazo:");
    if (!motivo) return;

    try {
      await rechazarSolicitudIntercambio(id, motivo);
      alert("Solicitud rechazada");
      cargarDatos();
    } catch (error) {
      console.error("Error rechazando solicitud:", error);
      alert("Error al rechazar solicitud");
    }
  };

  const handleGenerarExpediente = async (id: string) => {
    try {
      const expediente = await generarExpedienteFHIR(id);
      const blob = new Blob([JSON.stringify(expediente.bundle, null, 2)], {
        type: "application/json",
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `expediente-fhir-${id}.json`;
      a.click();
      alert("Expediente FHIR generado y descargado");
      cargarDatos();
    } catch (error) {
      console.error("Error generando expediente:", error);
      alert("Error al generar expediente FHIR");
    }
  };

  const getEstadoBadge = (estado: string) => {
    const badges: Record<
      string,
      { color: string; icon: React.ReactNode; text: string }
    > = {
      pendiente: {
        color: "bg-yellow-100 text-yellow-800",
        icon: <Clock className="w-4 h-4" />,
        text: "Pendiente",
      },
      aprobada: {
        color: "bg-green-100 text-green-800",
        icon: <CheckCircle className="w-4 h-4" />,
        text: "Aprobada",
      },
      rechazada: {
        color: "bg-red-100 text-red-800",
        icon: <XCircle className="w-4 h-4" />,
        text: "Rechazada",
      },
      en_proceso: {
        color: "bg-blue-100 text-blue-800",
        icon: <Activity className="w-4 h-4" />,
        text: "En Proceso",
      },
      completada: {
        color: "bg-green-100 text-green-800",
        icon: <CheckCircle className="w-4 h-4" />,
        text: "Completada",
      },
      error: {
        color: "bg-red-100 text-red-800",
        icon: <AlertCircle className="w-4 h-4" />,
        text: "Error",
      },
    };

    const badge = badges[estado] || badges.pendiente;

    return (
      <span
        className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${badge.color}`}
      >
        {badge.icon}
        {badge.text}
      </span>
    );
  };

  const renderDashboard = () => {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Solicitudes</p>
                <p className="text-2xl font-bold text-gray-900">
                  {estadisticas?.total_solicitudes || 0}
                </p>
              </div>
              <ArrowLeftRight className="w-10 h-10 text-blue-500" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Instituciones Activas</p>
                <p className="text-2xl font-bold text-gray-900">
                  {estadisticas?.instituciones_activas || 0}
                </p>
              </div>
              <Building2 className="w-10 h-10 text-green-500" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">
                  Pacientes con Consentimiento
                </p>
                <p className="text-2xl font-bold text-gray-900">
                  {estadisticas?.pacientes_con_consentimiento || 0}
                </p>
              </div>
              <Users className="w-10 h-10 text-purple-500" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Completadas</p>
                <p className="text-2xl font-bold text-gray-900">
                  {estadisticas?.solicitudes_por_estado?.completada || 0}
                </p>
              </div>
              <CheckCircle className="w-10 h-10 text-green-500" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Solicitudes por Estado</h3>
          <div className="space-y-2">
            {estadisticas?.solicitudes_por_estado &&
              Object.entries(estadisticas.solicitudes_por_estado).map(
                ([estado, count]) => (
                  <div
                    key={estado}
                    className="flex items-center justify-between"
                  >
                    <span className="capitalize">
                      {estado.replace("_", " ")}
                    </span>
                    <span className="font-semibold">{count}</span>
                  </div>
                )
              )}
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Solicitudes por Tipo</h3>
          <div className="space-y-2">
            {estadisticas?.solicitudes_por_tipo &&
              Object.entries(estadisticas.solicitudes_por_tipo).map(
                ([tipo, count]) => (
                  <div
                    key={tipo}
                    className="flex items-center justify-between"
                  >
                    <span className="capitalize">
                      {tipo.replace("_", " ")}
                    </span>
                    <span className="font-semibold">{count}</span>
                  </div>
                )
              )}
          </div>
        </div>
      </div>
    );
  };

  const renderInstituciones = () => {
    return (
      <div className="space-y-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <h3 className="text-lg font-semibold">
              Instituciones de la Red Nacional de Salud
            </h3>
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
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Nombre
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Código
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Nivel
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Tipo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Protocolos
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Estado
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {instituciones.map((inst) => (
                  <tr key={inst.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Building2 className="w-5 h-5 text-gray-400 mr-2" />
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {inst.nombre}
                          </div>
                          <div className="text-sm text-gray-500">
                            {inst.ciudad}, {inst.estado}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {inst.codigo_institucional}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800 capitalize">
                        {inst.nivel_atencion}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800 capitalize">
                        {inst.tipo_institucion}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {inst.protocolos_soportados.join(", ")}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {inst.activa ? (
                        <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                          Activa
                        </span>
                      ) : (
                        <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">
                          Inactiva
                        </span>
                      )}
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
  };

  const renderSolicitudes = () => {
    return (
      <div className="space-y-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <h3 className="text-lg font-semibold">Solicitudes de Intercambio</h3>
            <button
              onClick={() => setMostrarFormSolicitud(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              <Plus className="w-5 h-5" />
              Nueva Solicitud
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Tipo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Protocolo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Estado
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Prioridad
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Fecha
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {solicitudes.map((sol) => (
                  <tr key={sol.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <FileText className="w-5 h-5 text-gray-400 mr-2" />
                        <span className="text-sm text-gray-900 capitalize">
                          {sol.tipo_intercambio.replace("_", " ")}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-indigo-100 text-indigo-800">
                        {sol.protocolo}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getEstadoBadge(sol.estado)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded-full capitalize ${
                          sol.prioridad === "urgente"
                            ? "bg-red-100 text-red-800"
                            : sol.prioridad === "alta"
                            ? "bg-orange-100 text-orange-800"
                            : "bg-gray-100 text-gray-800"
                        }`}
                      >
                        {sol.prioridad}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(sol.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                      {sol.estado === "pendiente" && (
                        <>
                          <button
                            onClick={() => handleAprobarSolicitud(sol.id)}
                            className="text-green-600 hover:text-green-900"
                            title="Aprobar"
                          >
                            <CheckCircle className="w-5 h-5" />
                          </button>
                          <button
                            onClick={() => handleRechazarSolicitud(sol.id)}
                            className="text-red-600 hover:text-red-900"
                            title="Rechazar"
                          >
                            <XCircle className="w-5 h-5" />
                          </button>
                        </>
                      )}
                      {sol.estado === "aprobada" && (
                        <button
                          onClick={() => handleGenerarExpediente(sol.id)}
                          className="text-blue-600 hover:text-blue-900"
                          title="Generar Expediente FHIR"
                        >
                          <Download className="w-5 h-5" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  };

  const renderConsentimientos = () => {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">
          Gestión de Consentimientos
        </h3>
        <p className="text-gray-600">
          Aquí se gestionarán los consentimientos de pacientes para compartir
          información.
        </p>
      </div>
    );
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <ArrowLeftRight className="w-8 h-8" />
              Interoperabilidad HL7 FHIR
            </h1>
            <p className="text-gray-600 mt-2">
              Red Nacional de Salud e Intercambio de Expedientes
            </p>
          </div>
          <NotificacionesPanel />
        </div>
      </div>

      <div className="mb-6 border-b border-gray-200">
        <nav className="flex space-x-8">
          <button
            onClick={() => setActiveTab("dashboard")}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === "dashboard"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            <Activity className="w-5 h-5 inline mr-2" />
            Dashboard
          </button>
          <button
            onClick={() => setActiveTab("metricas")}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === "metricas"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            <Activity className="w-5 h-5 inline mr-2" />
            Métricas en Tiempo Real
          </button>
          <button
            onClick={() => setActiveTab("instituciones")}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === "instituciones"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            <Building2 className="w-5 h-5 inline mr-2" />
            Instituciones
          </button>
          <button
            onClick={() => setActiveTab("solicitudes")}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === "solicitudes"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            <ArrowLeftRight className="w-5 h-5 inline mr-2" />
            Solicitudes
          </button>
          <button
            onClick={() => setActiveTab("consentimientos")}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === "consentimientos"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            <Shield className="w-5 h-5 inline mr-2" />
            Consentimientos
          </button>
        </nav>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
        </div>
      ) : (
        <>
          {activeTab === "dashboard" && renderDashboard()}
          {activeTab === "metricas" && <DashboardMetricas />}
          {activeTab === "instituciones" && renderInstituciones()}
          {activeTab === "solicitudes" && renderSolicitudes()}
          {activeTab === "consentimientos" && renderConsentimientos()}
        </>
      )}

      {mostrarFormInstitucion && (
        <FormularioInstitucion
          institucion={institucionEditar}
          onClose={() => {
            setMostrarFormInstitucion(false);
            setInstitucionEditar(undefined);
          }}
          onSave={
            institucionEditar ? handleActualizarInstitucion : handleCrearInstitucion
          }
        />
      )}

      {mostrarFormSolicitud && (
        <FormularioSolicitud
          pacienteId=""
          instituciones={instituciones}
          onClose={() => setMostrarFormSolicitud(false)}
          onSave={async () => {}}
        />
      )}
    </div>
  );
};

export default Interoperabilidad;