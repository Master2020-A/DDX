import { useState, useEffect } from 'react';
import { Database, Download, Trash2, Plus, RefreshCw, AlertCircle } from 'lucide-react';
import backupsService, { Backup, TipoBackup, EstadoBackup } from '../../services/backupsService';

const GestionBackups = () => {
  const [backups, setBackups] = useState<Backup[]>([]);
  const [loading, setLoading] = useState(true);
  const [filtroTipo, setFiltroTipo] = useState<TipoBackup | ''>('');
  const [filtroEstado, setFiltroEstado] = useState<EstadoBackup | ''>('');
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [nuevoBackup, setNuevoBackup] = useState({
    nombre: '',
    descripcion: '',
    tipo: TipoBackup.COMPLETO,
  });

  useEffect(() => {
    cargarBackups();
  }, [filtroTipo, filtroEstado]);

  const cargarBackups = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (filtroTipo) params.tipo = filtroTipo;
      if (filtroEstado) params.estado = filtroEstado;
      
      const data = await backupsService.listarBackups(params);
      setBackups(data);
    } catch (error) {
      console.error('Error al cargar backups:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCrearBackup = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await backupsService.crearBackup(nuevoBackup);
      setMostrarFormulario(false);
      setNuevoBackup({ nombre: '', descripcion: '', tipo: TipoBackup.COMPLETO });
      cargarBackups();
    } catch (error) {
      console.error('Error al crear backup:', error);
      alert('Error al crear backup');
    }
  };

  const handleEliminarBackup = async (id: string) => {
    if (!confirm('¿Está seguro de eliminar este backup? Esta acción no se puede deshacer.')) {
      return;
    }

    try {
      await backupsService.eliminarBackup(id);
      cargarBackups();
    } catch (error) {
      console.error('Error al eliminar backup:', error);
      alert('Error al eliminar backup');
    }
  };

  const obtenerColorEstado = (estado: EstadoBackup) => {
    const colores = {
      completado: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      en_progreso: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      pendiente: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      fallido: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      cancelado: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200',
    };
    return colores[estado] || colores.pendiente;
  };

  const obtenerTextoEstado = (estado: EstadoBackup) => {
    const textos = {
      completado: 'Completado',
      en_progreso: 'En Progreso',
      pendiente: 'Pendiente',
      fallido: 'Fallido',
      cancelado: 'Cancelado',
    };
    return textos[estado] || estado;
  };

  const obtenerTextoTipo = (tipo: TipoBackup) => {
    const textos = {
      completo: 'Completo',
      incremental: 'Incremental',
      diferencial: 'Diferencial',
      transaccional: 'Transaccional',
    };
    return textos[tipo] || tipo;
  };

  return (
    <div className="space-y-6">
      {/* Header con acciones */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-50">
            Gestión de Backups
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Administre los backups de la base de datos
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={cargarBackups}
            className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            <RefreshCw size={16} className="mr-2" />
            Actualizar
          </button>
          <button
            onClick={() => setMostrarFormulario(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
          >
            <Plus size={16} className="mr-2" />
            Nuevo Backup
          </button>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Filtrar por Tipo
            </label>
            <select
              value={filtroTipo}
              onChange={(e) => setFiltroTipo(e.target.value as TipoBackup | '')}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            >
              <option value="">Todos los tipos</option>
              <option value={TipoBackup.COMPLETO}>Completo</option>
              <option value={TipoBackup.INCREMENTAL}>Incremental</option>
              <option value={TipoBackup.DIFERENCIAL}>Diferencial</option>
              <option value={TipoBackup.TRANSACCIONAL}>Transaccional</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Filtrar por Estado
            </label>
            <select
              value={filtroEstado}
              onChange={(e) => setFiltroEstado(e.target.value as EstadoBackup | '')}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            >
              <option value="">Todos los estados</option>
              <option value={EstadoBackup.COMPLETADO}>Completado</option>
              <option value={EstadoBackup.EN_PROGRESO}>En Progreso</option>
              <option value={EstadoBackup.PENDIENTE}>Pendiente</option>
              <option value={EstadoBackup.FALLIDO}>Fallido</option>
            </select>
          </div>
        </div>
      </div>

      {/* Formulario de nuevo backup */}
      {mostrarFormulario && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-4">
              Crear Nuevo Backup
            </h3>
            <form onSubmit={handleCrearBackup} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Nombre *
                </label>
                <input
                  type="text"
                  required
                  value={nuevoBackup.nombre}
                  onChange={(e) => setNuevoBackup({ ...nuevoBackup, nombre: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  placeholder="Ej: backup_produccion"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Tipo
                </label>
                <select
                  value={nuevoBackup.tipo}
                  onChange={(e) => setNuevoBackup({ ...nuevoBackup, tipo: e.target.value as TipoBackup })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                >
                  <option value={TipoBackup.COMPLETO}>Completo</option>
                  <option value={TipoBackup.INCREMENTAL}>Incremental</option>
                  <option value={TipoBackup.DIFERENCIAL}>Diferencial</option>
                  <option value={TipoBackup.TRANSACCIONAL}>Transaccional</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Descripción
                </label>
                <textarea
                  value={nuevoBackup.descripcion}
                  onChange={(e) => setNuevoBackup({ ...nuevoBackup, descripcion: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  placeholder="Descripción opcional del backup"
                />
              </div>

              <div className="flex justify-end gap-2 pt-4">
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
                  Crear Backup
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Lista de backups */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : backups.length === 0 ? (
          <div className="text-center py-12">
            <Database className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-50">
              No hay backups
            </h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Comience creando un nuevo backup
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-900">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Nombre
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Tipo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Tamaño
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Fecha
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Duración
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {backups.map((backup) => (
                  <tr key={backup.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Database className="h-5 w-5 text-gray-400 mr-3" />
                        <div>
                          <div className="text-sm font-medium text-gray-900 dark:text-gray-50">
                            {backup.nombre}
                          </div>
                          {backup.descripcion && (
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                              {backup.descripcion}
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900 dark:text-gray-50">
                        {obtenerTextoTipo(backup.tipo)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${obtenerColorEstado(backup.estado)}`}>
                        {obtenerTextoEstado(backup.estado)}
                      </span>
                      {backup.estado === EstadoBackup.FALLIDO && backup.mensaje_error && (
                        <div className="mt-1 text-xs text-red-600 dark:text-red-400">
                          <AlertCircle size={12} className="inline mr-1" />
                          {backup.mensaje_error.substring(0, 50)}...
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-50">
                      {backup.tamano_bytes ? backupsService.formatearTamano(backup.tamano_bytes) : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {new Date(backup.fecha_inicio).toLocaleString('es-MX')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {backup.duracion_segundos ? backupsService.formatearDuracion(backup.duracion_segundos) : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => handleEliminarBackup(backup.id)}
                        className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                        title="Eliminar backup"
                      >
                        <Trash2 size={18} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default GestionBackups;
