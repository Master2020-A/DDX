import { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Switch } from '@/components/ui/switch';
import { CalendarIcon, Loader2, Plus, X } from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import portalPacienteService, { RecordatorioMedicamento } from '@/services/portalPacienteService';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface FormularioNuevoRecordatorioProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  pacienteId: string;
  onSuccess: (recordatorio: RecordatorioMedicamento) => void;
}

export default function FormularioNuevoRecordatorio({ open, onOpenChange, pacienteId, onSuccess }: FormularioNuevoRecordatorioProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fechaInicio, setFechaInicio] = useState<Date>();
  const [fechaFin, setFechaFin] = useState<Date>();
  const [horarios, setHorarios] = useState<string[]>(['08:00']);
  
  const [formData, setFormData] = useState({
    nombre_medicamento: '',
    dosis: '',
    via_administracion: 'oral',
    indicaciones: '',
    frecuencia: 'diario',
    duracion_dias: 30,
    notificar_email: true,
    notificar_sms: false,
    notificar_push: true,
  });

  const viasAdministracion = [
    { value: 'oral', label: 'Oral' },
    { value: 'sublingual', label: 'Sublingual' },
    { value: 'intravenosa', label: 'Intravenosa' },
    { value: 'intramuscular', label: 'Intramuscular' },
    { value: 'subcutanea', label: 'Subcutánea' },
    { value: 'topica', label: 'Tópica' },
    { value: 'inhalada', label: 'Inhalada' },
    { value: 'rectal', label: 'Rectal' },
    { value: 'oftálmica', label: 'Oftálmica' },
  ];

  const frecuencias = [
    { value: 'diario', label: 'Diario (1 vez al día)' },
    { value: 'cada_12_horas', label: 'Cada 12 horas (2 veces al día)' },
    { value: 'cada_8_horas', label: 'Cada 8 horas (3 veces al día)' },
    { value: 'cada_6_horas', label: 'Cada 6 horas (4 veces al día)' },
    { value: 'cada_4_horas', label: 'Cada 4 horas (6 veces al día)' },
    { value: 'semanal', label: 'Semanal' },
    { value: 'quincenal', label: 'Quincenal' },
    { value: 'mensual', label: 'Mensual' },
  ];

  const agregarHorario = () => {
    setHorarios([...horarios, '12:00']);
  };

  const eliminarHorario = (index: number) => {
    setHorarios(horarios.filter((_, i) => i !== index));
  };

  const actualizarHorario = (index: number, valor: string) => {
    const nuevosHorarios = [...horarios];
    nuevosHorarios[index] = valor;
    setHorarios(nuevosHorarios);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!fechaInicio) {
      setError('Por favor selecciona la fecha de inicio');
      return;
    }

    if (!formData.nombre_medicamento.trim()) {
      setError('Por favor ingresa el nombre del medicamento');
      return;
    }

    if (!formData.dosis.trim()) {
      setError('Por favor ingresa la dosis');
      return;
    }

    if (horarios.length === 0) {
      setError('Por favor agrega al menos un horario');
      return;
    }

    setLoading(true);

    try {
      const nuevoRecordatorio = await portalPacienteService.crearRecordatorio({
        paciente_id: pacienteId,
        nombre_medicamento: formData.nombre_medicamento,
        dosis: formData.dosis,
        via_administracion: formData.via_administracion,
        indicaciones: formData.indicaciones || undefined,
        frecuencia: formData.frecuencia,
        horarios: horarios,
        fecha_inicio: format(fechaInicio, 'yyyy-MM-dd'),
        fecha_fin: fechaFin ? format(fechaFin, 'yyyy-MM-dd') : undefined,
        duracion_dias: formData.duracion_dias,
        activo: true,
        pausado: false,
        notificar_email: formData.notificar_email,
        notificar_sms: formData.notificar_sms,
        notificar_push: formData.notificar_push,
        tomas_registradas: 0,
        tomas_omitidas: 0,
      });

      onSuccess(nuevoRecordatorio);
      onOpenChange(false);
      
      // Reset form
      setFormData({
        nombre_medicamento: '',
        dosis: '',
        via_administracion: 'oral',
        indicaciones: '',
        frecuencia: 'diario',
        duracion_dias: 30,
        notificar_email: true,
        notificar_sms: false,
        notificar_push: true,
      });
      setFechaInicio(undefined);
      setFechaFin(undefined);
      setHorarios(['08:00']);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al crear el recordatorio');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Nuevo Recordatorio de Medicamento</DialogTitle>
          <DialogDescription>
            Configura recordatorios para tomar tus medicamentos a tiempo.
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
              <Label htmlFor="medicamento">Nombre del Medicamento *</Label>
              <Input
                id="medicamento"
                placeholder="Ej: Losartán 50mg"
                value={formData.nombre_medicamento}
                onChange={(e) => setFormData({ ...formData, nombre_medicamento: e.target.value })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="dosis">Dosis *</Label>
              <Input
                id="dosis"
                placeholder="Ej: 50mg, 1 tableta"
                value={formData.dosis}
                onChange={(e) => setFormData({ ...formData, dosis: e.target.value })}
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="via">Vía de Administración</Label>
              <Select
                value={formData.via_administracion}
                onValueChange={(value) => setFormData({ ...formData, via_administracion: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {viasAdministracion.map((via) => (
                    <SelectItem key={via.value} value={via.value}>
                      {via.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="frecuencia">Frecuencia</Label>
              <Select
                value={formData.frecuencia}
                onValueChange={(value) => setFormData({ ...formData, frecuencia: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {frecuencias.map((frec) => (
                    <SelectItem key={frec.value} value={frec.value}>
                      {frec.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label>Horarios de Toma *</Label>
            <div className="space-y-2">
              {horarios.map((horario, index) => (
                <div key={index} className="flex items-center gap-2">
                  <Input
                    type="time"
                    value={horario}
                    onChange={(e) => actualizarHorario(index, e.target.value)}
                    className="flex-1"
                  />
                  {horarios.length > 1 && (
                    <Button
                      type="button"
                      variant="outline"
                      size="icon"
                      onClick={() => eliminarHorario(index)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={agregarHorario}
                className="w-full"
              >
                <Plus className="h-4 w-4 mr-2" />
                Agregar Horario
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Fecha de Inicio *</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className="w-full justify-start text-left font-normal"
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {fechaInicio ? format(fechaInicio, 'PP', { locale: es }) : 'Seleccionar'}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <Calendar
                    mode="single"
                    selected={fechaInicio}
                    onSelect={setFechaInicio}
                    locale={es}
                  />
                </PopoverContent>
              </Popover>
            </div>

            <div className="space-y-2">
              <Label>Fecha de Fin (opcional)</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className="w-full justify-start text-left font-normal"
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {fechaFin ? format(fechaFin, 'PP', { locale: es }) : 'Seleccionar'}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <Calendar
                    mode="single"
                    selected={fechaFin}
                    onSelect={setFechaFin}
                    disabled={(date) => fechaInicio ? date < fechaInicio : false}
                    locale={es}
                  />
                </PopoverContent>
              </Popover>
            </div>

            <div className="space-y-2">
              <Label htmlFor="duracion">Duración (días)</Label>
              <Input
                id="duracion"
                type="number"
                min="1"
                value={formData.duracion_dias}
                onChange={(e) => setFormData({ ...formData, duracion_dias: parseInt(e.target.value) })}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="indicaciones">Indicaciones (opcional)</Label>
            <Textarea
              id="indicaciones"
              placeholder="Ej: Tomar con alimentos, evitar alcohol, etc..."
              value={formData.indicaciones}
              onChange={(e) => setFormData({ ...formData, indicaciones: e.target.value })}
              rows={2}
            />
          </div>

          <div className="space-y-3">
            <Label>Notificaciones</Label>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="email" className="font-normal">Email</Label>
                <Switch
                  id="email"
                  checked={formData.notificar_email}
                  onCheckedChange={(checked) => setFormData({ ...formData, notificar_email: checked })}
                />
              </div>
              <div className="flex items-center justify-between">
                <Label htmlFor="sms" className="font-normal">SMS</Label>
                <Switch
                  id="sms"
                  checked={formData.notificar_sms}
                  onCheckedChange={(checked) => setFormData({ ...formData, notificar_sms: checked })}
                />
              </div>
              <div className="flex items-center justify-between">
                <Label htmlFor="push" className="font-normal">Notificación Push</Label>
                <Switch
                  id="push"
                  checked={formData.notificar_push}
                  onCheckedChange={(checked) => setFormData({ ...formData, notificar_push: checked })}
                />
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button type="submit" disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Crear Recordatorio
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
