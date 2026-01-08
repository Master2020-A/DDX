import React, { useState, useEffect } from 'react';
import { X, Save, Building2 } from 'lucide-react';
import { InstitucionExterna } from '@/services/interoperabilidadService';

interface FormularioInstitucionProps {
  institucion?: InstitucionExterna;
  onClose: () => void;
  onSave: (data: Partial<InstitucionExterna>) => Promise<void>;
}

const FormularioInstitucion: React.FC<FormularioInstitucionProps> = ({
  institucion,
  onClose,
  onSave,
}) => {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    nombre: '',
    codigo_institucional: '',
    nivel_atencion: 'primario',
    tipo_institucion: 'publico',
    pais: 'México',
    estado: '',
    ciudad: '',
    direccion: '',
    telefono: '',
    email: '',
    url_endpoint_fhir: '',
    activa: true,
    protocolos_soportados: ['FHIR_R4'],
    versiones_fhir: ['4.0.1'],
  });

  useEffect(() => {
    if (institucion) {
      setFormData({
        nombre: institucion.nombre || '',
        codigo_institucional: institucion.codigo_institucional || '',
        nivel_atencion: institucion.nivel_atencion || 'primario',
        tipo_institucion: institucion.tipo_institucion || 'publico',
        pais: institucion.pais || 'México',
        estado: institucion.estado || '',
        ciudad: institucion.ciudad || '',
        direccion: institucion.direccion || '',
        telefono: institucion.telefono || '',
        email: institucion.email || '',
        url_endpoint_fhir: institucion.url_endpoint_fhir || '',
        activa: institucion.activa ?? true,
        protocolos_soportados: institucion.protocolos_soportados || ['FHIR_R4'],
        versiones_fhir: institucion.versiones_fhir || ['4.0.1'],
      });
    }
  }, [institucion]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onSave(formData);
      onClose();
    } catch (error) {
      console.error('Error al guardar institución:', error);
      alert('Error al guardar la institución');
    } finally {
      setLoading(false);
    }
  };

  const handleProtocoloChange = (protocolo: string) => {
    const protocolos = formData.protocolos_soportados.includes(protocolo)
      ? formData.protocolos_soportados.filter((p) => p !== protocolo)
      : [...formData.protocolos_soportados, protocolo];
    setFormData({ ...formData, protocolos_soportados: protocolos });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Building2 className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-bold text-gray-900">
              {institucion ? 'Editar Institución' : 'Nueva Institución Externa'}
            </h2>
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
          {/* Información Básica */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Información Básica</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nombre de la Institución *
                </label>
                <input
                  type="text"
                  required
                  value={formData.nombre}
                  onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Hospital General de México"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Código Institucional *
                </label>
                <input
                  type="text"
                  required
                  value={formData.codigo_institucional}
                  onChange={(e) => setFormData({ ...formData, codigo_institucional: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="HGM-001"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nivel de Atención *
                </label>
                <select
                  required
                  value={formData.nivel_atencion}
                  onChange={(e) => setFormData({ ...formData, nivel_atencion: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="primario">Primario</option>
                  <option value="secundario">Secundario</option>
                  <option value="terciario">Terciario</option>
                  <option value="especializado">Especializado</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tipo de Institución *
                </label>
                <select
                  required
                  value={formData.tipo_institucion}
                  onChange={(e) => setFormData({ ...formData, tipo_institucion: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="publico">Público</option>
                  <option value="privado">Privado</option>
                  <option value="mixto">Mixto</option>
                </select>
              </div>
            </div>
          </div>

          {/* Ubicación */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Ubicación</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">País *</label>
                <input
                  type="text"
                  required
                  value={formData.pais}
                  onChange={(e) => setFormData({ ...formData, pais: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Estado *</label>
                <input
                  type="text"
                  required
                  value={formData.estado}
                  onChange={(e) => setFormData({ ...formData, estado: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Ciudad *</label>
                <input
                  type="text"
                  required
                  value={formData.ciudad}
                  onChange={(e) => setFormData({ ...formData, ciudad: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="md:col-span-3">
                <label className="block text-sm font-medium text-gray-700 mb-1">Dirección</label>
                <input
                  type="text"
                  value={formData.direccion}
                  onChange={(e) => setFormData({ ...formData, direccion: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Contacto */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Contacto</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
                <input
                  type="tel"
                  value={formData.telefono}
                  onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Interoperabilidad */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Configuración de Interoperabilidad</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  URL Endpoint FHIR
                </label>
                <input
                  type="url"
                  value={formData.url_endpoint_fhir}
                  onChange={(e) => setFormData({ ...formData, url_endpoint_fhir: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="https://hospital.com/fhir/r4"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Protocolos Soportados
                </label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {['FHIR_R4', 'FHIR_R5', 'HL7V2', 'REST_API'].map((protocolo) => (
                    <label key={protocolo} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={formData.protocolos_soportados.includes(protocolo)}
                        onChange={() => handleProtocoloChange(protocolo)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-700">{protocolo}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="activa"
                  checked={formData.activa}
                  onChange={(e) => setFormData({ ...formData, activa: e.target.checked })}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <label htmlFor="activa" className="text-sm font-medium text-gray-700">
                  Institución Activa
                </label>
              </div>
            </div>
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
              {loading ? 'Guardando...' : 'Guardar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default FormularioInstitucion;
