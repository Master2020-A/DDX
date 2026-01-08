import { useState, useEffect } from 'react';
import { Clock, Plus, Power, PowerOff, Calendar } from 'lucide-react';
import backupsService, { ProgramacionBackup, TipoBackup } from '../../services/backupsService';

const ProgramacionBackups = () => {
  const [programaciones, setProgramaciones] = useState<ProgramacionBackup[]>([]);
  const [loading, setLoading] = useState(true);
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [nuevaProgramacion, setNuevaProgramacion] = useState({
    nombre: '',
    descripcion: '',
    tipo_backup: TipoBackup.COMPLETO,
    cron_expresion: '0 2 * * *',
    retencion_dias: 30,
    notificar_fallo: true,
  });

  useEffect(() => {
    cargarProgramaciones();
  }, []);

  const cargarProgramaciones = async () => {
    try {
      setLoading(true);
      const data = await backupsService.listarProgramaciones();
      setProgramaciones(data);
    } catch (error) {
      console.error('Error al cargar programaciones:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCrearProgramacion = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await backupsService.crearProgramacion(nuevaProgramacion);
      setMostrarFormulario(false);
      setNuevaProgramacion({
        nombre: '',
        descripcion: '',
        tipo_backup: TipoBackup.COMPLETO,
        cron_expresion: '0 2 * * *',
        retencion_dias: 30,
        notificar_fallo: true,
      });
      cargarProgramaciones();
    } catch (error) {
      console.error('Error al crear programación:', error);
      alert('Error al crear programación');
    }
  };

  const handleToggleActivo = async (id: string, activo: boolean) => {
    try {
      await backupsService.actualizarProgramacion(id, { activo: !activo });
      cargarProgramaciones();
    } catch (error) {
      console.error('Error al actualizar programación:', error);
      alert('Error al actualizar programación');
    }
  };

  const expresionesCron = [
    { valor: '0 2 * * *', texto: 'Diario a las 2:00 AM' },
    { valor: '0 0 * * 0', texto: 'Semanal (Domingos a medianoche)' },
    { valor: '0 0 1 * *', texto: 'Mensual (Día 1 a medianoche)' },
    { valor: '*/15 * * * *', texto: 'Cada 15 minutos' },
    { valor: '0 */6 * * *', texto: 'Cada 6 horas' },
    { valor: '0 0 * * 1-5', texto: 'Días laborales a medianoche' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-50">
            Programación de Backups
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Configure backups automáticos programados
          </p>
        </div>
        <button
          onClick={() => setMostrarFormulario(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
        >
          <Plus size={16} className="mr-2" />
          Nueva Programación
        </button>
      </div>

      {/* Formulario */}
      {mostrarFormulario && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-4">
              Nueva Programación de Backup
            </h3>
            <form onSubmit={handleCrearProgramacion} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Nombre *
                  </label>
                  <input
                    type="text"
                    required
                    value={nuevaProgramacion.nombre}
                    onChange={(e) => setNuevaProgramacion({ ...nuevaProgramacion, nombre: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    placeholder="Ej: Backup Diario"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Tipo de Backup
                  </label>
                  <select
                    value={nuevaProgramacion.tipo_backup}
                    onChange={(e) => setNuevaProgramacion({ ...nuevaProgramacion, tipo_backup: e.target.value as TipoBackup })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  >
                    <option value={TipoBackup.COMPLETO}>Completo</option>
                    <option value={TipoBackup.INCREMENTAL}>Incremental</option>
                    <option value={TipoBackup.DIFERENCIAL}>Diferencial</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Descripción
                </label>
                <textarea
                  value={nuevaProgramacion.descripcion}
                  onChange={(e) => setNuevaProgramacion({ ...nuevaProgramacion, descripcion: e.target.value })}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Frecuencia (Expresión Cron)
                </label>
                <select
                  value={nuevaProgramacion.cron_expresion}
                  onChange={(e) => setNuevaProgramacion({ ...nuevaProgramacion, cron_expresion: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                >
                  {expresionesCron.map((exp) => (
                    <option key={exp.valor} value={exp.valor}>
                      {exp.texto} ({exp.valor})
                    </option>
                  ))}
                </select>
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  Formato: minuto hora día mes día_semana
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Retención (días)
                </label>
                <input
                  type="number"
                  min="1"
                  max="365"
                  value={nuevaProgramacion.retencion_dias}
                  onChange={(e) => setNuevaProgramacion({ ...nuevaProgramacion, retencion_dias: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                />
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  Los backups se eliminarán automáticamente después de este período
                </p>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="notificar_fallo"
                  checked={nuevaProgramacion.notificar_fallo}
                  onChange={(e) => setNuevaProgramacion({ ...nuevaProgramacion, notificar_fallo: e.target.checked })}
                  className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                />
                <label htmlFor="notificar_fallo" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                  Notificar si el backup falla
                </label>
              </div>

              <div className="flex justify-end gap-2 pt-4 border-t border-gray-200 dark:border-gray-700">
                <button
                  type="button"
                  onClick={() => setMostrarFormulario(false)}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                >
                  Crear Programación
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Lista de programaciones */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : programaciones.length === 0 ? (
          <div className="text-center py-12">
            <Clock className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-50">
              No hay programaciones
            </h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Comience creando una nueva programación de backup
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {programaciones.map((prog) => (
              <div key={prog.id} className="p-6 hover:bg-gray-50 dark:hover:bg-gray-700">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-medium text-gray-900 dark:text-gray-50">
                        {prog.nombre}
                      </h3>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        prog.activo
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                      }`}>
                        {prog.activo ? 'Activo' : 'Inactivo'}
                      </span>
                    </div>
                    
                    {prog.descripcion && (
                      <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                        {prog.descripcion}
                      </p>
                    )}

                    <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Tipo</p>
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-50 mt-1">
                          {prog.tipo_backup.charAt(0).toUpperCase() + prog.tipo_backup.slice(1)}
                        </p>
                      </div>

                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Frecuencia</p>
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-50 mt-1">
                          {backupsService.parsearExpresionCron(prog.cron_expresion)}
                        </p>
                      </div>

                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Retención</p>
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-50 mt-1">
                          {prog.retencion_dias} días
                        </p>
                      </div>

                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Última Ejecución</p>
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-50 mt-1">
                          {prog.ultima_ejecucion
                            ? new Date(prog.ultima_ejecucion).toLocaleString('es-MX')
                            : 'Nunca'}
                        </p>
                      </div>
                    </div>

                    {prog.proximo_ejecucion && (
                      <div className="mt-3 flex items-center text-sm text-gray-600 dark:text-gray-400">
                        <Calendar size={16} className="mr-2" />
                        Próxima ejecución: {new Date(prog.proximo_ejecucion).toLocaleString('es-MX')}
                      </div>
                    )}
                  </div>

                  <button
                    onClick={() => handleToggleActivo(prog.id, prog.activo)}
                    className={`ml-4 p-2 rounded-md ${
                      prog.activo
                        ? 'text-green-600 hover:bg-green-50 dark:text-green-400 dark:hover:bg-green-900/20'
                        : 'text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                    title={prog.activo ? 'Desactivar' : 'Activar'}
                  >
                    {prog.activo ? <Power size={20} /> : <PowerOff size={20} />}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProgramacionBackups;
