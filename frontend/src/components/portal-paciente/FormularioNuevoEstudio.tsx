import { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2 } from 'lucide-react';
import portalPacienteService, { SolicitudEstudio } from '@/services/portalPacienteService';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface FormularioNuevoEstudioProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  pacienteId: string;
  onSuccess: (estudio: SolicitudEstudio) => void;
}

export default function FormularioNuevoEstudio({ open, onOpenChange, pacienteId, onSuccess }: FormularioNuevoEstudioProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState({
    tipo_estudio: 'laboratorio',
    nombre_estudio: '',
    descripcion: '',
    indicaciones_especiales: '',
    prioridad: 'normal',
  });

  const tiposEstudio = [
    { value: 'laboratorio', label: 'Laboratorio' },
    { value: 'imagen', label: 'Imagen (Rayos X, TAC, MRI)' },
    { value: 'especializado', label: 'Estudio Especializado' },
  ];

  const prioridades = [
    { value: 'normal', label: 'Normal' },
    { value: 'urgente', label: 'Urgente' },
    { value: 'emergencia', label: 'Emergencia' },
  ];

  const estudiosLaboratorio = [
    'Biometría Hemática Completa',
    'Química Sanguínea',
    'Perfil de Lípidos',
    'Examen General de Orina',
    'Pruebas de Función Hepática',
    'Pruebas de Función Renal',
    'Hemoglobina Glucosilada (HbA1c)',
    'Perfil Tiroideo',
  ];

  const estudiosImagen = [
    'Radiografía de Tórax',
    'Radiografía de Abdomen',
    'Ultrasonido Abdominal',
    'Tomografía Computarizada',
    'Resonancia Magnética',
    'Ecocardiograma',
  ];

  const estudiosEspecializados = [
    'Electrocardiograma',
    'Espirometría',
    'Endoscopia',
    'Colonoscopia',
    'Mamografía',
    'Densitometría Ósea',
  ];

  const getEstudiosDisponibles = () => {
    switch (formData.tipo_estudio) {
      case 'laboratorio':
        return estudiosLaboratorio;
      case 'imagen':
        return estudiosImagen;
      case 'especializado':
        return estudiosEspecializados;
      default:
        return [];
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!formData.nombre_estudio) {
      setError('Por favor selecciona un estudio');
      return;
    }

    setLoading(true);

    try {
      const nuevoEstudio = await portalPacienteService.crearSolicitudEstudio({
        paciente_id: pacienteId,
        tipo_estudio: formData.tipo_estudio,
        nombre_estudio: formData.nombre_estudio,
        descripcion: formData.descripcion || undefined,
        indicaciones_especiales: formData.indicaciones_especiales || undefined,
        prioridad: formData.prioridad,
        estado: 'pendiente',
      });

      onSuccess(nuevoEstudio);
      onOpenChange(false);
      
      // Reset form
      setFormData({
        tipo_estudio: 'laboratorio',
        nombre_estudio: '',
        descripcion: '',
        indicaciones_especiales: '',
        prioridad: 'normal',
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al crear la solicitud');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Solicitar Estudio</DialogTitle>
          <DialogDescription>
            Solicita un estudio de laboratorio, imagen o especializado. Tu médico lo revisará y autorizará.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="tipo_estudio">Tipo de Estudio</Label>
              <Select
                value={formData.tipo_estudio}
                onValueChange={(value) => setFormData({ ...formData, tipo_estudio: value, nombre_estudio: '' })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {tiposEstudio.map((tipo) => (
                    <SelectItem key={tipo.value} value={tipo.value}>
                      {tipo.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="prioridad">Prioridad</Label>
              <Select
                value={formData.prioridad}
                onValueChange={(value) => setFormData({ ...formData, prioridad: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {prioridades.map((p) => (
                    <SelectItem key={p.value} value={p.value}>
                      {p.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="nombre_estudio">Estudio Solicitado *</Label>
            <Select
              value={formData.nombre_estudio}
              onValueChange={(value) => setFormData({ ...formData, nombre_estudio: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Selecciona un estudio" />
              </SelectTrigger>
              <SelectContent>
                {getEstudiosDisponibles().map((estudio) => (
                  <SelectItem key={estudio} value={estudio}>
                    {estudio}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="descripcion">Descripción / Motivo (opcional)</Label>
            <Textarea
              id="descripcion"
              placeholder="Describe el motivo de la solicitud..."
              value={formData.descripcion}
              onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
              rows={3}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="indicaciones">Indicaciones Especiales (opcional)</Label>
            <Textarea
              id="indicaciones"
              placeholder="Ej: En ayunas, suspender medicamento, etc..."
              value={formData.indicaciones_especiales}
              onChange={(e) => setFormData({ ...formData, indicaciones_especiales: e.target.value })}
              rows={2}
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button type="submit" disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Enviar Solicitud
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
