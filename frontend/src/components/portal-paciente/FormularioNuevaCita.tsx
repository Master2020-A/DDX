import { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { CalendarIcon, Loader2 } from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import portalPacienteService, { CitaPaciente } from '@/services/portalPacienteService';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface FormularioNuevaCitaProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  pacienteId: string;
  onSuccess: (cita: CitaPaciente) => void;
}

export default function FormularioNuevaCita({ open, onOpenChange, pacienteId, onSuccess }: FormularioNuevaCitaProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fecha, setFecha] = useState<Date>();
  
  const [formData, setFormData] = useState({
    tipo_cita: 'primera_vez',
    especialidad_solicitada: '',
    motivo_consulta: '',
    hora_solicitada: '',
    notas_paciente: '',
  });

  const especialidades = [
    'Medicina General',
    'Cardiología',
    'Dermatología',
    'Endocrinología',
    'Gastroenterología',
    'Ginecología',
    'Neurología',
    'Oftalmología',
    'Ortopedia',
    'Pediatría',
    'Psiquiatría',
    'Urología',
  ];

  const tiposCita = [
    { value: 'primera_vez', label: 'Primera Vez' },
    { value: 'seguimiento', label: 'Seguimiento' },
    { value: 'urgencia', label: 'Urgencia' },
    { value: 'revision', label: 'Revisión' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!fecha) {
      setError('Por favor selecciona una fecha');
      return;
    }

    if (!formData.especialidad_solicitada) {
      setError('Por favor selecciona una especialidad');
      return;
    }

    if (!formData.motivo_consulta.trim()) {
      setError('Por favor describe el motivo de la consulta');
      return;
    }

    setLoading(true);

    try {
      const nuevaCita = await portalPacienteService.crearCita({
        paciente_id: pacienteId,
        tipo_cita: formData.tipo_cita,
        especialidad_solicitada: formData.especialidad_solicitada,
        motivo_consulta: formData.motivo_consulta,
        fecha_solicitada: format(fecha, 'yyyy-MM-dd'),
        hora_solicitada: formData.hora_solicitada || undefined,
        estado: 'solicitada',
        notas_paciente: formData.notas_paciente || undefined,
      });

      onSuccess(nuevaCita);
      onOpenChange(false);
      
      // Reset form
      setFormData({
        tipo_cita: 'primera_vez',
        especialidad_solicitada: '',
        motivo_consulta: '',
        hora_solicitada: '',
        notas_paciente: '',
      });
      setFecha(undefined);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al crear la cita');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Agendar Nueva Cita</DialogTitle>
          <DialogDescription>
            Solicita una cita médica. Recibirás confirmación una vez que sea aprobada.
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
              <Label htmlFor="tipo_cita">Tipo de Cita</Label>
              <Select
                value={formData.tipo_cita}
                onValueChange={(value) => setFormData({ ...formData, tipo_cita: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {tiposCita.map((tipo) => (
                    <SelectItem key={tipo.value} value={tipo.value}>
                      {tipo.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="especialidad">Especialidad *</Label>
              <Select
                value={formData.especialidad_solicitada}
                onValueChange={(value) => setFormData({ ...formData, especialidad_solicitada: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecciona especialidad" />
                </SelectTrigger>
                <SelectContent>
                  {especialidades.map((esp) => (
                    <SelectItem key={esp} value={esp}>
                      {esp}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Fecha Deseada *</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className="w-full justify-start text-left font-normal"
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {fecha ? format(fecha, 'PPP', { locale: es }) : 'Selecciona una fecha'}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <Calendar
                    mode="single"
                    selected={fecha}
                    onSelect={setFecha}
                    disabled={(date) => date < new Date()}
                    locale={es}
                  />
                </PopoverContent>
              </Popover>
            </div>

            <div className="space-y-2">
              <Label htmlFor="hora">Hora Preferida (opcional)</Label>
              <Input
                id="hora"
                type="time"
                value={formData.hora_solicitada}
                onChange={(e) => setFormData({ ...formData, hora_solicitada: e.target.value })}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="motivo">Motivo de la Consulta *</Label>
            <Textarea
              id="motivo"
              placeholder="Describe brevemente el motivo de tu consulta..."
              value={formData.motivo_consulta}
              onChange={(e) => setFormData({ ...formData, motivo_consulta: e.target.value })}
              rows={3}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="notas">Notas Adicionales (opcional)</Label>
            <Textarea
              id="notas"
              placeholder="Información adicional que consideres relevante..."
              value={formData.notas_paciente}
              onChange={(e) => setFormData({ ...formData, notas_paciente: e.target.value })}
              rows={2}
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button type="submit" disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Solicitar Cita
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
