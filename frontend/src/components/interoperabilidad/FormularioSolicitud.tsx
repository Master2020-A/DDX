import React, { useState, useEffect } from 'react';
import { X, Save, ArrowLeftRight, AlertCircle } from 'lucide-react';
import { SolicitudIntercambio, InstitucionExterna } from '@/services/interoperabilidadService';

interface FormularioSolicitudProps {
  pacienteId: string;
  instituciones: InstitucionExterna[];
  onClose: () => void;
  onSave: (data: any) => Promise<void>;
}

const FormularioSolicitud: React.FC<FormularioSolicitudProps> = ({
  pacienteId,
  instituciones,
  onClose,
  onSave,
}) => {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    paciente_id: pacienteId,
    institucion_destino_id: '',
    tipo_intercambio: 'expediente_completo',
    protocolo: 'FHIR_R4',
    prioridad: 'normal',
    motivo_solicitud: '',
    periodo_inicio: '',
    periodo_fin: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onSave(formData);
      onClose();
    } catch (error) {
      console.error('Error al crear solicitud:', error);
      alert('Error al crear la solicitud');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ArrowLeftRight className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-bold text-gray-900">Nueva Solicitud de Intercambio</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            disabled={loading}
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Alerta informativa */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex gap-3">
            <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">Verificación de Consentimiento</p>
              <p>
                El sistema verificará automáticamente que el paciente haya otorgado su consentimiento
                antes de procesar la solicitud.
              </p>
            </div>
          </div>

          {/* Institución Destino */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Institución Destino *
            </label>
            <select
              required
              value={formData.institucion_destino_id}
              onChange={(e) =>
                setFormData({ ...formData, institucion_destino_id: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Seleccione una institución</option>
              {instituciones
                .filter((inst) => inst.activa)
                .map((inst) => (
                  <option key={inst.id} value={inst.id}>
                    {inst.nombre} - {inst.ciudad}, {inst.estado}
                  </option>
                ))}
            </select>
          </div>

          {/* Tipo de Intercambio */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo de Intercambio *
            </label>
            <select
              required
              value={formData.tipo_intercambio}
              onChange={(e) => setFormData({ ...formData, tipo_intercambio: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="expediente_completo">Expediente Completo</option>
              <option value="consultas">Consultas</option>
              <option value="laboratorios">Laboratorios</option>
              <option value="imagenes">Imágenes</option>
              <option value="recetas">Recetas</option>
              <option value="hospitalizacion">Hospitalización</option>
            </select>
            <p className="mt-1 text-xs text-gray-500">
              Seleccione qué tipo de información desea intercambiar
            </p>
          </div>

          {/* Protocolo y Prioridad */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Protocolo *</label>
              <select
                required
                value={formData.protocolo}
                onChange={(e) => setFormData({ ...formData, protocolo: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="FHIR_R4">FHIR R4</option>
                <option value="FHIR_R5">FHIR R5</option>
                <option value="HL7V2">HL7 v2</option>
                <option value="REST_API">REST API</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Prioridad *</label>
              <select
                required
                value={formData.prioridad}
                onChange={(e) => setFormData({ ...formData, prioridad: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="baja">Baja</option>
                <option value="normal">Normal</option>
                <option value="alta">Alta</option>
                <option value="urgente">Urgente</option>
              </select>
            </div>
          </div>

          {/* Período */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Período de Información
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-gray-600 mb-1">Fecha Inicio</label>
                <input
                  type="date"
                  value={formData.periodo_inicio}
                  onChange={(e) => setFormData({ ...formData, periodo_inicio: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">Fecha Fin</label>
                <input
                  type="date"
                  value={formData.periodo_fin}
                  onChange={(e) => setFormData({ ...formData, periodo_fin: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <p className="mt-1 text-xs text-gray-500">
              Opcional: Especifique el rango de fechas de la información a intercambiar
            </p>
          </div>

          {/* Motivo */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Motivo de la Solicitud *
            </label>
            <textarea
              required
              value={formData.motivo_solicitud}
              onChange={(e) => setFormData({ ...formData, motivo_solicitud: e.target.value })}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Describa el motivo de la solicitud de intercambio..."
            />
          </div>

          {/* Botones */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 disabled:opacity-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              {loading ? 'Creando...' : 'Crear Solicitud'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default FormularioSolicitud;
