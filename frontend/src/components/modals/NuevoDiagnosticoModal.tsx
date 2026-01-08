import React, { useState } from 'react';
import { X } from 'lucide-react';
import api from '@/lib/api';

interface NuevoDiagnosticoModalProps {
  consultaId: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const NuevoDiagnosticoModal: React.FC<NuevoDiagnosticoModalProps> = ({
  consultaId,
  isOpen,
  onClose,
  onSuccess
}) => {
  const [formData, setFormData] = useState({
    descripcion: '',
    tipo: 'diagnostico_presuntivo',
    codigo_cie10: '',
    confianza_nivel: 'medio',
    justificacion: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await api.post('/diagnosticos/', {
        consulta_id: consultaId,
        ...formData,
        estado: 'activo'
      });
      
      onSuccess();
      onClose();
      
      // Resetear formulario
      setFormData({
        descripcion: '',
        tipo: 'diagnostico_presuntivo',
        codigo_cie10: '',
        confianza_nivel: 'medio',
        justificacion: '',
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al crear diagnóstico');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-900">Nuevo Diagnóstico</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="label">Descripción del diagnóstico *</label>
            <textarea
              value={formData.descripcion}
              onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
              className="input"
              rows={3}
              placeholder="Ej: Faringoamigdalitis aguda"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Tipo de diagnóstico *</label>
              <select
                value={formData.tipo}
                onChange={(e) => setFormData({ ...formData, tipo: e.target.value })}
                className="input"
                required
              >
                <option value="pre_diagnostico">Pre-diagnóstico</option>
                <option value="diagnostico_presuntivo">Diagnóstico presuntivo</option>
                <option value="diagnostico_confirmado">Diagnóstico confirmado</option>
                <option value="diagnostico_diferencial">Diagnóstico diferencial</option>
              </select>
            </div>

            <div>
              <label className="label">Nivel de confianza *</label>
              <select
                value={formData.confianza_nivel}
                onChange={(e) => setFormData({ ...formData, confianza_nivel: e.target.value })}
                className="input"
                required
              >
                <option value="bajo">Bajo</option>
                <option value="medio">Medio</option>
                <option value="alto">Alto</option>
                <option value="confirmado">Confirmado</option>
              </select>
            </div>
          </div>

          <div>
            <label className="label">Código CIE-10</label>
            <input
              type="text"
              value={formData.codigo_cie10}
              onChange={(e) => setFormData({ ...formData, codigo_cie10: e.target.value.toUpperCase() })}
              className="input"
              placeholder="Ej: J02.9"
              maxLength={10}
            />
            <p className="text-sm text-gray-500 mt-1">
              Código de clasificación internacional de enfermedades
            </p>
          </div>

          <div>
            <label className="label">Justificación / Notas</label>
            <textarea
              value={formData.justificacion}
              onChange={(e) => setFormData({ ...formData, justificacion: e.target.value })}
              className="input"
              rows={4}
              placeholder="Justificación clínica del diagnóstico..."
            />
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button type="button" onClick={onClose} className="btn btn-secondary">
              Cancelar
            </button>
            <button type="submit" disabled={loading} className="btn btn-primary">
              {loading ? 'Guardando...' : 'Guardar Diagnóstico'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default NuevoDiagnosticoModal;
