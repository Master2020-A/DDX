import { useEffect, useState } from 'react';
import { FileText, Plus, CheckCircle, XCircle, Clock, AlertCircle } from 'lucide-react';
import cumplimientoService, {
  ConsentimientoInformado,
  TipoConsentimiento,
  EstadoConsentimiento,
} from '../../services/cumplimientoService';

interface GestionConsentimientosProps {
  pacienteId?: string;
}

const GestionConsentimientos = ({ pacienteId }: GestionConsentimientosProps) => {
  const [consentimientos, setConsentimientos] = useState<ConsentimientoInformado[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [selectedConsentimiento, setSelectedConsentimiento] = useState<ConsentimientoInformado | null>(null);
  const [showDetailDialog, setShowDetailDialog] = useState(false);

  const [newConsentimiento, setNewConsentimiento] = useState({
    tipo: TipoConsentimiento.TRATAMIENTO,
    titulo: '',
    descripcion: '',
    riesgos: [''],
    beneficios: [''],
    alternativas: [''],
  });

  useEffect(() => {
    if (pacienteId) {
      cargarConsentimientos();
    } else {
      setLoading(false);
    }
  }, [pacienteId]);

  const cargarConsentimientos = async () => {
    if (!pacienteId) return;

    try {
      setLoading(true);
      const data = await cumplimientoService.getConsentimientosPaciente(pacienteId);
      setConsentimientos(data);
    } catch (error) {
      console.error('Error al cargar consentimientos:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCrearConsentimiento = async () => {
    if (!pacienteId || !newConsentimiento.titulo || !newConsentimiento.descripcion) {
      alert('Por favor completa todos los campos obligatorios');
      return;
    }

    try {
      await cumplimientoService.crearConsentimiento({
        paciente_id: pacienteId,
        tipo: newConsentimiento.tipo,
        titulo: newConsentimiento.titulo,
        descripcion: newConsentimiento.descripcion,
        riesgos: newConsentimiento.riesgos.filter(r => r.trim() !== ''),
        beneficios: newConsentimiento.beneficios.filter(b => b.trim() !== ''),
        alternativas: newConsentimiento.alternativas.filter(a => a.trim() !== ''),
      });

      await cargarConsentimientos();
      setShowCreateDialog(false);
      setNewConsentimiento({
        tipo: TipoConsentimiento.TRATAMIENTO,
        titulo: '',
        descripcion: '',
        riesgos: [''],
        beneficios: [''],
        alternativas: [''],
      });
      alert('Consentimiento creado exitosamente');
    } catch (error: any) {
      console.error('Error al crear consentimiento:', error);
      alert(error.response?.data?.detail || 'Error al crear consentimiento');
    }
  };

  const getEstadoBadge = (estado: EstadoConsentimiento) => {
    const badges = {
      [EstadoConsentimiento.PENDIENTE]: {
        icon: Clock,
        color: 'bg-yellow-100 text-yellow-800',
        text: 'Pendiente',
      },
      [EstadoConsentimiento.ACEPTADO]: {
        icon: CheckCircle,
        color: 'bg-green-100 text-green-800',
        text: 'Aceptado',
      },
      [EstadoConsentimiento.RECHAZADO]: {
        icon: XCircle,
        color: 'bg-red-100 text-red-800',
        text: 'Rechazado',
      },
      [EstadoConsentimiento.REVOCADO]: {
        icon: AlertCircle,
        color: 'bg-gray-100 text-gray-800',
        text: 'Revocado',
      },
    };

    const badge = badges[estado];
    const Icon = badge.icon;

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${badge.color}`}>
        <Icon className="h-3 w-3 mr-1" />
        {badge.text}
      </span>
    );
  };

  const getTipoLabel = (tipo: TipoConsentimiento) => {
    const labels = {
      [TipoConsentimiento.TRATAMIENTO]: 'Tratamiento',
      [TipoConsentimiento.CIRUGIA]: 'Cirugía',
      [TipoConsentimiento.ANESTESIA]: 'Anestesia',
      [TipoConsentimiento.INVESTIGACION]: 'Investigación',
      [TipoConsentimiento.DATOS_PERSONALES]: 'Datos Personales',
      [TipoConsentimiento.IMAGEN]: 'Uso de Imagen',
      [TipoConsentimiento.OTRO]: 'Otro',
    };
    return labels[tipo] || tipo;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!pacienteId) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="text-center py-12">
          <FileText className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-50">
            Gestión de Consentimientos Informados
          </h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Para gestionar consentimientos informados, primero debes seleccionar un paciente.
          </p>
          <p className="mt-4 text-xs text-gray-400 dark:text-gray-500">
            Ve a <strong>Pacientes</strong> → Selecciona un paciente → <strong>Cumplimiento</strong>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-50">Consentimientos Informados</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            {consentimientos.length} consentimientos registrados
          </p>
        </div>
        <button
          onClick={() => setShowCreateDialog(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
        >
          <Plus className="h-4 w-4 mr-2" />
          Nuevo Consentimiento
        </button>
      </div>

      {/* Lista de Consentimientos */}
      <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
        {consentimientos.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="mx-auto h-12 w-12 text-gray-400" />
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">No hay consentimientos registrados</p>
            <button
              onClick={() => setShowCreateDialog(true)}
              className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200"
            >
              Crear primer consentimiento
            </button>
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {consentimientos.map((consentimiento) => (
              <li
                key={consentimiento.id}
                className="px-6 py-4 hover:bg-gray-50 cursor-pointer"
                onClick={() => {
                  setSelectedConsentimiento(consentimiento);
                  setShowDetailDialog(true);
                }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <FileText className="h-5 w-5 text-indigo-600" />
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">
                          {consentimiento.titulo}
                        </h3>
                        <p className="text-sm text-gray-500">
                          {getTipoLabel(consentimiento.tipo)}
                        </p>
                      </div>
                    </div>
                    <p className="mt-2 text-sm text-gray-600 line-clamp-2">
                      {consentimiento.descripcion}
                    </p>
                  </div>
                  <div className="ml-4 flex flex-col items-end space-y-2">
                    {getEstadoBadge(consentimiento.estado)}
                    <p className="text-xs text-gray-500">
                      {new Date(consentimiento.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Diálogo Crear Consentimiento */}
      {showCreateDialog && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">
                Nuevo Consentimiento Informado
              </h3>
            </div>

            <div className="px-6 py-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Tipo de Consentimiento *
                </label>
                <select
                  value={newConsentimiento.tipo}
                  onChange={(e) => setNewConsentimiento({ ...newConsentimiento, tipo: e.target.value as TipoConsentimiento })}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                >
                  {Object.values(TipoConsentimiento).map((tipo) => (
                    <option key={tipo} value={tipo}>
                      {getTipoLabel(tipo)}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Título *
                </label>
                <input
                  type="text"
                  value={newConsentimiento.titulo}
                  onChange={(e) => setNewConsentimiento({ ...newConsentimiento, titulo: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  placeholder="Ej: Consentimiento para Cirugía de Apendicectomía"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Descripción *
                </label>
                <textarea
                  value={newConsentimiento.descripcion}
                  onChange={(e) => setNewConsentimiento({ ...newConsentimiento, descripcion: e.target.value })}
                  rows={4}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  placeholder="Descripción detallada del procedimiento o tratamiento..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Riesgos
                </label>
                {newConsentimiento.riesgos.map((riesgo, index) => (
                  <input
                    key={index}
                    type="text"
                    value={riesgo}
                    onChange={(e) => {
                      const nuevosRiesgos = [...newConsentimiento.riesgos];
                      nuevosRiesgos[index] = e.target.value;
                      setNewConsentimiento({ ...newConsentimiento, riesgos: nuevosRiesgos });
                    }}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="Riesgo del procedimiento"
                  />
                ))}
                <button
                  onClick={() => setNewConsentimiento({ ...newConsentimiento, riesgos: [...newConsentimiento.riesgos, ''] })}
                  className="mt-2 text-sm text-indigo-600 hover:text-indigo-800"
                >
                  + Agregar riesgo
                </button>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Beneficios
                </label>
                {newConsentimiento.beneficios.map((beneficio, index) => (
                  <input
                    key={index}
                    type="text"
                    value={beneficio}
                    onChange={(e) => {
                      const nuevosBeneficios = [...newConsentimiento.beneficios];
                      nuevosBeneficios[index] = e.target.value;
                      setNewConsentimiento({ ...newConsentimiento, beneficios: nuevosBeneficios });
                    }}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="Beneficio del procedimiento"
                  />
                ))}
                <button
                  onClick={() => setNewConsentimiento({ ...newConsentimiento, beneficios: [...newConsentimiento.beneficios, ''] })}
                  className="mt-2 text-sm text-indigo-600 hover:text-indigo-800"
                >
                  + Agregar beneficio
                </button>
              </div>
            </div>

            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={() => setShowCreateDialog(false)}
                className="px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleCrearConsentimiento}
                className="px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
              >
                Crear Consentimiento
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Diálogo Detalle Consentimiento */}
      {showDetailDialog && selectedConsentimiento && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">
                  {selectedConsentimiento.titulo}
                </h3>
                {getEstadoBadge(selectedConsentimiento.estado)}
              </div>
              <p className="text-sm text-gray-500 mt-1">
                {getTipoLabel(selectedConsentimiento.tipo)}
              </p>
            </div>

            <div className="px-6 py-4 space-y-4">
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-2">Descripción</h4>
                <p className="text-sm text-gray-600">{selectedConsentimiento.descripcion}</p>
              </div>

              {selectedConsentimiento.riesgos && selectedConsentimiento.riesgos.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Riesgos</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {selectedConsentimiento.riesgos.map((riesgo, index) => (
                      <li key={index} className="text-sm text-gray-600">{riesgo}</li>
                    ))}
                  </ul>
                </div>
              )}

              {selectedConsentimiento.beneficios && selectedConsentimiento.beneficios.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Beneficios</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {selectedConsentimiento.beneficios.map((beneficio, index) => (
                      <li key={index} className="text-sm text-gray-600">{beneficio}</li>
                    ))}
                  </ul>
                </div>
              )}

              {selectedConsentimiento.alternativas && selectedConsentimiento.alternativas.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Alternativas</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {selectedConsentimiento.alternativas.map((alternativa, index) => (
                      <li key={index} className="text-sm text-gray-600">{alternativa}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="border-t pt-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500">Fecha de creación</p>
                    <p className="font-medium text-gray-900">
                      {new Date(selectedConsentimiento.created_at).toLocaleString()}
                    </p>
                  </div>
                  {selectedConsentimiento.fecha_firma_paciente && (
                    <div>
                      <p className="text-gray-500">Firma del paciente</p>
                      <p className="font-medium text-gray-900">
                        {new Date(selectedConsentimiento.fecha_firma_paciente).toLocaleString()}
                      </p>
                    </div>
                  )}
                  {selectedConsentimiento.fecha_firma_medico && (
                    <div>
                      <p className="text-gray-500">Firma del médico</p>
                      <p className="font-medium text-gray-900">
                        {new Date(selectedConsentimiento.fecha_firma_medico).toLocaleString()}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
              <button
                onClick={() => setShowDetailDialog(false)}
                className="w-full px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GestionConsentimientos;
