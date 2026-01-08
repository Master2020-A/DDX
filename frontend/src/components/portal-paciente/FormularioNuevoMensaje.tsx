import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2 } from 'lucide-react';
import portalPacienteService, { MensajePacienteMedico } from '@/services/portalPacienteService';
import { Alert, AlertDescription } from '@/components/ui/alert';
import api from '@/services/api';

interface FormularioNuevoMensajeProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  pacienteId: string;
  onSuccess: (mensaje: MensajePacienteMedico) => void;
}

interface Medico {
  id: string;
  nombre_completo: string;
  especialidad: string;
}

export default function FormularioNuevoMensaje({ open, onOpenChange, pacienteId, onSuccess }: FormularioNuevoMensajeProps) {
  const [loading, setLoading] = useState(false);
  const [loadingMedicos, setLoadingMedicos] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [medicos, setMedicos] = useState<Medico[]>([]);
  
  const [formData, setFormData] = useState({
    medico_id: '',
    asunto: '',
    mensaje: '',
  });

  useEffect(() => {
    if (open) {
      cargarMedicos();
    }
  }, [open]);

  const cargarMedicos = async () => {
    setLoadingMedicos(true);
    try {
      const response = await api.get('/usuarios?rol=medico&limit=100');
      setMedicos(response.data);
    } catch (err) {
      console.error('Error al cargar médicos:', err);
    } finally {
      setLoadingMedicos(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!formData.medico_id) {
      setError('Por favor selecciona un médico');
      return;
    }

    if (!formData.mensaje.trim()) {
      setError('Por favor escribe un mensaje');
      return;
    }

    setLoading(true);

    try {
      const nuevoMensaje = await portalPacienteService.enviarMensaje({
        paciente_id: pacienteId,
        medico_id: formData.medico_id,
        remitente_tipo: 'paciente',
        asunto: formData.asunto || undefined,
        mensaje: formData.mensaje,
        estado: 'enviado',
        leido: false,
      });

      onSuccess(nuevoMensaje);
      onOpenChange(false);
      
      // Reset form
      setFormData({
        medico_id: '',
        asunto: '',
        mensaje: '',
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al enviar el mensaje');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Nuevo Mensaje</DialogTitle>
          <DialogDescription>
            Envía un mensaje a tu médico. Recibirás una respuesta en tu bandeja de mensajes.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-2">
            <Label htmlFor="medico">Médico Destinatario *</Label>
            {loadingMedicos ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="h-6 w-6 animate-spin" />
              </div>
            ) : (
              <Select
                value={formData.medico_id}
                onValueChange={(value) => setFormData({ ...formData, medico_id: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecciona un médico" />
                </SelectTrigger>
                <SelectContent>
                  {medicos.map((medico) => (
                    <SelectItem key={medico.id} value={medico.id}>
                      {medico.nombre_completo} - {medico.especialidad || 'Medicina General'}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="asunto">Asunto (opcional)</Label>
            <Input
              id="asunto"
              placeholder="Ej: Consulta sobre medicamento"
              value={formData.asunto}
              onChange={(e) => setFormData({ ...formData, asunto: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="mensaje">Mensaje *</Label>
            <Textarea
              id="mensaje"
              placeholder="Escribe tu mensaje aquí..."
              value={formData.mensaje}
              onChange={(e) => setFormData({ ...formData, mensaje: e.target.value })}
              rows={6}
              required
            />
            <p className="text-xs text-muted-foreground">
              Tu médico recibirá una notificación y responderá a la brevedad.
            </p>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button type="submit" disabled={loading || loadingMedicos}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Enviar Mensaje
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
