import React, { useState, useEffect } from "react";
import {
  Bell,
  BellOff,
  Check,
  CheckCheck,
  Trash2,
  X,
  AlertCircle,
  Info,
  AlertTriangle,
  Zap,
  ExternalLink,
} from "lucide-react";

interface Notificacion {
  id: string;
  tipo: string;
  prioridad: "baja" | "media" | "alta" | "urgente";
  titulo: string;
  mensaje: string;
  datos_adicionales: string | null;
  usuario_id: string;
  solicitud_id: string | null;
  institucion_id: string | null;
  leida: boolean;
  fecha_lectura: string | null;
  accion_url: string | null;
  accion_texto: string | null;
  created_at: string;
  updated_at: string | null;
}

const NotificacionesPanel: React.FC = () => {
  const [notificaciones, setNotificaciones] = useState<Notificacion[]>([]);
  const [countNoLeidas, setCountNoLeidas] = useState(0);
  const [mostrarPanel, setMostrarPanel] = useState(false);
  const [soloNoLeidas, setSoloNoLeidas] = useState(false);
  const [loading, setLoading] = useState(false);

  const cargarNotificaciones = async () => {
    try {
      const response = await fetch(
        `http://localhost:8612/api/interoperabilidad/notificaciones/?solo_no_leidas=${soloNoLeidas}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );
      const data = await response.json();
      setNotificaciones(data);
    } catch (error) {
      console.error("Error cargando notificaciones:", error);
    }
  };

  const cargarCount = async () => {
    try {
      const response = await fetch(
        "http://localhost:8612/api/interoperabilidad/notificaciones/count",
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );
      const data = await response.json();
      setCountNoLeidas(data.count);
    } catch (error) {
      console.error("Error cargando count:", error);
    }
  };

  const marcarComoLeida = async (id: string) => {
    try {
      await fetch(
        `http://localhost:8612/api/interoperabilidad/notificaciones/${id}/marcar-leida`,
        {
          method: "PUT",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );
      cargarNotificaciones();
      cargarCount();
    } catch (error) {
      console.error("Error marcando como leída:", error);
    }
  };

  const marcarTodasComoLeidas = async () => {
    setLoading(true);
    try {
      await fetch(
        "http://localhost:8612/api/interoperabilidad/notificaciones/marcar-todas-leidas",
        {
          method: "PUT",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );
      cargarNotificaciones();
      cargarCount();
    } catch (error) {
      console.error("Error marcando todas como leídas:", error);
    } finally {
      setLoading(false);
    }
  };

  const eliminarNotificacion = async (id: string) => {
    try {
      await fetch(
        `http://localhost:8612/api/interoperabilidad/notificaciones/${id}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );
      cargarNotificaciones();
      cargarCount();
    } catch (error) {
      console.error("Error eliminando notificación:", error);
    }
  };

  useEffect(() => {
    cargarCount();
    const interval = setInterval(cargarCount, 30000); // Actualizar cada 30 segundos
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (mostrarPanel) {
      cargarNotificaciones();
    }
  }, [mostrarPanel, soloNoLeidas]);

  const getPrioridadColor = (prioridad: string) => {
    switch (prioridad) {
      case "urgente":
        return "border-l-4 border-red-500 bg-red-50";
      case "alta":
        return "border-l-4 border-orange-500 bg-orange-50";
      case "media":
        return "border-l-4 border-yellow-500 bg-yellow-50";
      case "baja":
        return "border-l-4 border-blue-500 bg-blue-50";
      default:
        return "border-l-4 border-gray-500 bg-gray-50";
    }
  };

  const getPrioridadIcon = (prioridad: string) => {
    switch (prioridad) {
      case "urgente":
        return <Zap className="w-5 h-5 text-red-600" />;
      case "alta":
        return <AlertTriangle className="w-5 h-5 text-orange-600" />;
      case "media":
        return <AlertCircle className="w-5 h-5 text-yellow-600" />;
      case "baja":
        return <Info className="w-5 h-5 text-blue-600" />;
      default:
        return <Bell className="w-5 h-5 text-gray-600" />;
    }
  };

  const formatearFecha = (fecha: string) => {
    const date = new Date(fecha);
    const ahora = new Date();
    const diff = ahora.getTime() - date.getTime();
    const minutos = Math.floor(diff / 60000);
    const horas = Math.floor(diff / 3600000);
    const dias = Math.floor(diff / 86400000);

    if (minutos < 1) return "Hace un momento";
    if (minutos < 60) return `Hace ${minutos} min`;
    if (horas < 24) return `Hace ${horas} h`;
    if (dias < 7) return `Hace ${dias} d`;
    return date.toLocaleDateString("es-MX");
  };

  return (
    <div className="relative">
      {/* Botón de notificaciones */}
      <button
        onClick={() => setMostrarPanel(!mostrarPanel)}
        className="relative p-2 text-gray-600 hover:bg-gray-100 rounded-full transition-colors"
      >
        <Bell className="w-6 h-6" />
        {countNoLeidas > 0 && (
          <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full">
            {countNoLeidas > 99 ? "99+" : countNoLeidas}
          </span>
        )}
      </button>

      {/* Panel de notificaciones */}
      {mostrarPanel && (
        <>
          {/* Overlay */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setMostrarPanel(false)}
          />

          {/* Panel */}
          <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-2xl z-50 max-h-[600px] flex flex-col">
            {/* Header */}
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <Bell className="w-5 h-5" />
                  Notificaciones
                  {countNoLeidas > 0 && (
                    <span className="px-2 py-1 text-xs font-bold bg-red-100 text-red-800 rounded-full">
                      {countNoLeidas}
                    </span>
                  )}
                </h3>
                <button
                  onClick={() => setMostrarPanel(false)}
                  className="p-1 hover:bg-gray-100 rounded"
                >
                  <X className="w-5 h-5 text-gray-500" />
                </button>
              </div>

              {/* Controles */}
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setSoloNoLeidas(!soloNoLeidas)}
                  className={`flex-1 px-3 py-1.5 text-sm rounded-md transition-colors ${
                    soloNoLeidas
                      ? "bg-blue-100 text-blue-700 border border-blue-300"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  {soloNoLeidas ? (
                    <>
                      <BellOff className="w-4 h-4 inline mr-1" />
                      Solo no leídas
                    </>
                  ) : (
                    <>
                      <Bell className="w-4 h-4 inline mr-1" />
                      Todas
                    </>
                  )}
                </button>
                {countNoLeidas > 0 && (
                  <button
                    onClick={marcarTodasComoLeidas}
                    disabled={loading}
                    className="flex-1 px-3 py-1.5 text-sm bg-green-100 text-green-700 rounded-md hover:bg-green-200 transition-colors disabled:opacity-50"
                  >
                    <CheckCheck className="w-4 h-4 inline mr-1" />
                    Marcar todas
                  </button>
                )}
              </div>
            </div>

            {/* Lista de notificaciones */}
            <div className="overflow-y-auto flex-1">
              {notificaciones.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  <Bell className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                  <p className="font-medium">No hay notificaciones</p>
                  <p className="text-sm mt-1">
                    {soloNoLeidas
                      ? "Todas tus notificaciones están leídas"
                      : "No tienes notificaciones aún"}
                  </p>
                </div>
              ) : (
                <div className="divide-y divide-gray-200">
                  {notificaciones.map((notif) => (
                    <div
                      key={notif.id}
                      className={`p-4 hover:bg-gray-50 transition-colors ${
                        !notif.leida ? getPrioridadColor(notif.prioridad) : ""
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        {/* Icono */}
                        <div className="flex-shrink-0 mt-1">
                          {getPrioridadIcon(notif.prioridad)}
                        </div>

                        {/* Contenido */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between gap-2">
                            <h4
                              className={`text-sm font-semibold ${
                                !notif.leida
                                  ? "text-gray-900"
                                  : "text-gray-600"
                              }`}
                            >
                              {notif.titulo}
                            </h4>
                            <span className="text-xs text-gray-500 whitespace-nowrap">
                              {formatearFecha(notif.created_at)}
                            </span>
                          </div>

                          <p className="text-sm text-gray-600 mt-1">
                            {notif.mensaje}
                          </p>

                          {/* Acciones */}
                          <div className="flex items-center gap-2 mt-3">
                            {notif.accion_url && notif.accion_texto && (
                              <a
                                href={notif.accion_url}
                                onClick={() => {
                                  if (!notif.leida) {
                                    marcarComoLeida(notif.id);
                                  }
                                  setMostrarPanel(false);
                                }}
                                className="text-xs text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1"
                              >
                                {notif.accion_texto}
                                <ExternalLink className="w-3 h-3" />
                              </a>
                            )}

                            <div className="flex-1" />

                            {!notif.leida && (
                              <button
                                onClick={() => marcarComoLeida(notif.id)}
                                className="p-1 text-green-600 hover:bg-green-50 rounded"
                                title="Marcar como leída"
                              >
                                <Check className="w-4 h-4" />
                              </button>
                            )}

                            <button
                              onClick={() => eliminarNotificacion(notif.id)}
                              className="p-1 text-red-600 hover:bg-red-50 rounded"
                              title="Eliminar"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Footer */}
            {notificaciones.length > 0 && (
              <div className="p-3 border-t border-gray-200 bg-gray-50">
                <p className="text-xs text-center text-gray-500">
                  Mostrando {notificaciones.length} notificación
                  {notificaciones.length !== 1 ? "es" : ""}
                </p>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default NotificacionesPanel;
