import { useState, useEffect } from 'react';
import { Bell, Send, Clock, CheckCircle, XCircle, AlertCircle, RefreshCw } from 'lucide-react';
import appMovilService, { NotificacionPush, TipoNotificacion, EstadoNotificacion } from '../../services/appMovilService';

const GestionNotificaciones = () => {
  const [notificaciones, setNotificaciones] = useState<NotificacionPush[]>([]);
  const [loading, setLoading] = useState(true);
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formulario, setFormulario] = useState({
    titulo: '',
    mensaje: '',
    tipo: TipoNotificacion.SISTEMA,
    prioridad: 'normal',
  });

  useEffect(() => {
    cargarNotificaciones();
  }, []);

  const cargarNotificaciones = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Cargando notificaciones...');
      const data = await appMovilService.listarNotificaciones(50);
      console.log('Notificaciones cargadas:', data);
      setNotificaciones(data);
    } catch (error: any) {
      console.error('Error al cargar notificaciones:', error);
      setError(error.response?.data?.detail || error.message || 'Error al cargar notificaciones');
    } finally {
      setLoading(false);
    }
  };

  const handleEnviarNotificacion = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setEnviando(true);
      await appMovilService.enviarNotificacionMasiva({
        titulo: formulario.titulo,
        mensaje: formulario.mensaje,
        tipo: formulario.tipo,
        prioridad: formulario.prioridad,
      });

      alert('Notificación enviada exitosamente');
      setFormulario({
        titulo: '',
        mensaje: '',
        tipo: TipoNotificacion.SISTEMA,
        prioridad: 'normal',
      });
      setMostrarFormulario(false);
      cargarNotificaciones();
    } catch (error) {
      console.error('Error al enviar notificación:', error);
      alert('Error al enviar notificación');
    } finally {
      setEnviando(false);
    }
  };

  const obtenerIconoEstado = (estado: EstadoNotificacion) => {
    switch (estado) {
      case EstadoNotificacion.LEIDA:
        return <CheckCircle className="h-5 w-5 text-gray-500" />;
      case EstadoNotificacion.ENTREGADA:
        return <CheckCircle className="h-5 w-5 text-blue-500" />;
      case EstadoNotificacion.ENVIADA:
        return <Send className="h-5 w-5 text-green-500" />;
      case EstadoNotificacion.PENDIENTE:
        return <Clock className="h-5 w-5 text-yellow-500" />;
      case EstadoNotificacion.FALLIDA:
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-500" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-50">
            Gestión de Notificaciones Push
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Envía y gestiona notificaciones push a dispositivos móviles
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={cargarNotificaciones}
            disabled={loading}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Actualizar
          </button>
          <button
            onClick={() => setMostrarFormulario(!mostrarFormulario)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
          >
            <Send className="h-4 w-4 mr-2" />
            Nueva Notificación
          </button>
        </div>
      </div>

      {/* Mensaje de Error */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div className="flex items-start">
            <XCircle className="h-5 w-5 text-red-600 dark:text-red-400 mt-0.5 mr-3" />
            <div className="flex-1">
              <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                Error al cargar notificaciones
              </h3>
              <p className="text-sm text-red-700 dark:text-red-300 mt-1">
                {error}
              </p>
              <p className="text-xs text-red-600 dark:text-red-400 mt-2">
                Verifica la consola del navegador (F12) para más detalles.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Formulario de Nueva Notificación */}
      {mostrarFormulario && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-4">
            Enviar Notificación Masiva
          </h3>
          <form onSubmit={handleEnviarNotificacion} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Título
              </label>
              <input
                type="text"
                value={formulario.titulo}
                onChange={(e) => setFormulario({ ...formulario, titulo: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-50"
                required
                maxLength={200}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Mensaje
              </label>
              <textarea
                value={formulario.mensaje}
                onChange={(e) => setFormulario({ ...formulario, mensaje: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-50"
                rows={3}
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Tipo
                </label>
                <select
                  value={formulario.tipo}
                  onChange={(e) => setFormulario({ ...formulario, tipo: e.target.value as TipoNotificacion })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-50"
                >
                  <option value={TipoNotificacion.SISTEMA}>Sistema</option>
                  <option value={TipoNotificacion.CITA}>Cita</option>
                  <option value={TipoNotificacion.RECORDATORIO}>Recordatorio</option>
                  <option value={TipoNotificacion.RESULTADO}>Resultado</option>
                  <option value={TipoNotificacion.MENSAJE}>Mensaje</option>
                  <option value={TipoNotificacion.ALERTA}>Alerta</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Prioridad
                </label>
                <select
                  value={formulario.prioridad}
                  onChange={(e) => setFormulario({ ...formulario, prioridad: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-50"
                >
                  <option value="baja">Baja</option>
                  <option value="normal">Normal</option>
                  <option value="alta">Alta</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => setMostrarFormulario(false)}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={enviando}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center"
              >
                {enviando ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Enviando...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4 mr-2" />
                    Enviar a Todos
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Lista de Notificaciones */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
              Historial de Notificaciones
            </h3>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              Total: {notificaciones.length}
            </span>
          </div>
        </div>
        <div className="divide-y divide-gray-200 dark:divide-gray-700">
          {notificaciones.length === 0 ? (
            <div className="px-6 py-12 text-center">
              <Bell className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-50">
                No hay notificaciones
              </h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                {error ? 'Hubo un error al cargar las notificaciones. Verifica la consola.' : 'Envía tu primera notificación push'}
              </p>
              <button
                onClick={cargarNotificaciones}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 inline-flex items-center"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Intentar de nuevo
              </button>
            </div>
          ) : (
            notificaciones.map((notificacion) => (
              <div key={notificacion.id} className="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-700">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 flex-1">
                    {obtenerIconoEstado(notificacion.estado)}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-50">
                          {notificacion.titulo}
                        </p>
                        <span className={`
                          px-2 py-0.5 text-xs rounded-full
                          ${notificacion.tipo === TipoNotificacion.ALERTA ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' : ''}
                          ${notificacion.tipo === TipoNotificacion.CITA ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' : ''}
                          ${notificacion.tipo === TipoNotificacion.RESULTADO ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : ''}
                          ${notificacion.tipo === TipoNotificacion.SISTEMA ? 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200' : ''}
                          ${notificacion.tipo === TipoNotificacion.RECORDATORIO ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' : ''}
                          ${notificacion.tipo === TipoNotificacion.MENSAJE ? 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200' : ''}
                        `}>
                          {appMovilService.obtenerTextoTipoNotificacion(notificacion.tipo)}
                        </span>
                      </div>
                      <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                        {notificacion.mensaje}
                      </p>
                      <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                        <span>
                          {appMovilService.calcularTiempoTranscurrido(notificacion.created_at)}
                        </span>
                        <span className="capitalize">{notificacion.estado}</span>
                        {notificacion.prioridad !== 'normal' && (
                          <span className="capitalize">Prioridad: {notificacion.prioridad}</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default GestionNotificaciones;
