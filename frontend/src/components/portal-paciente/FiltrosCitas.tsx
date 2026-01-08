import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Calendar } from '@/components/ui/calendar';
import { CalendarIcon, Filter, X } from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

export interface FiltrosCitasState {
  estado?: string;
  especialidad?: string;
  fechaDesde?: Date;
  fechaHasta?: Date;
  busqueda?: string;
}

interface FiltrosCitasProps {
  filtros: FiltrosCitasState;
  onFiltrosChange: (filtros: FiltrosCitasState) => void;
}

export default function FiltrosCitas({ filtros, onFiltrosChange }: FiltrosCitasProps) {
  const [abierto, setAbierto] = useState(false);

  const estados = [
    { value: 'todos', label: 'Todos los estados' },
    { value: 'solicitada', label: 'Solicitada' },
    { value: 'confirmada', label: 'Confirmada' },
    { value: 'completada', label: 'Completada' },
    { value: 'cancelada', label: 'Cancelada' },
  ];

  const especialidades = [
    'Todas las especialidades',
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

  const limpiarFiltros = () => {
    onFiltrosChange({});
  };

  const tieneFiltrosActivos = () => {
    return Object.keys(filtros).length > 0;
  };

  return (
    <div className="flex items-center gap-2">
      <div className="flex-1">
        <Input
          placeholder="Buscar por motivo, especialidad..."
          value={filtros.busqueda || ''}
          onChange={(e) => onFiltrosChange({ ...filtros, busqueda: e.target.value })}
        />
      </div>

      <Popover open={abierto} onOpenChange={setAbierto}>
        <PopoverTrigger asChild>
          <Button variant="outline" className="gap-2">
            <Filter className="h-4 w-4" />
            Filtros
            {tieneFiltrosActivos() && (
              <span className="ml-1 bg-primary text-primary-foreground rounded-full px-2 py-0.5 text-xs">
                {Object.keys(filtros).length}
              </span>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-80" align="end">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="font-medium">Filtros</h4>
              {tieneFiltrosActivos() && (
                <Button variant="ghost" size="sm" onClick={limpiarFiltros}>
                  <X className="h-4 w-4 mr-1" />
                  Limpiar
                </Button>
              )}
            </div>

            <div className="space-y-2">
              <Label>Estado</Label>
              <Select
                value={filtros.estado || 'todos'}
                onValueChange={(value) => 
                  onFiltrosChange({ ...filtros, estado: value === 'todos' ? undefined : value })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {estados.map((estado) => (
                    <SelectItem key={estado.value} value={estado.value}>
                      {estado.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Especialidad</Label>
              <Select
                value={filtros.especialidad || 'Todas las especialidades'}
                onValueChange={(value) => 
                  onFiltrosChange({ 
                    ...filtros, 
                    especialidad: value === 'Todas las especialidades' ? undefined : value 
                  })
                }
              >
                <SelectTrigger>
                  <SelectValue />
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

            <div className="space-y-2">
              <Label>Fecha Desde</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="outline" className="w-full justify-start text-left font-normal">
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {filtros.fechaDesde ? format(filtros.fechaDesde, 'PP', { locale: es }) : 'Seleccionar'}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <Calendar
                    mode="single"
                    selected={filtros.fechaDesde}
                    onSelect={(date) => onFiltrosChange({ ...filtros, fechaDesde: date })}
                    locale={es}
                  />
                </PopoverContent>
              </Popover>
            </div>

            <div className="space-y-2">
              <Label>Fecha Hasta</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="outline" className="w-full justify-start text-left font-normal">
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {filtros.fechaHasta ? format(filtros.fechaHasta, 'PP', { locale: es }) : 'Seleccionar'}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <Calendar
                    mode="single"
                    selected={filtros.fechaHasta}
                    onSelect={(date) => onFiltrosChange({ ...filtros, fechaHasta: date })}
                    disabled={(date) => filtros.fechaDesde ? date < filtros.fechaDesde : false}
                    locale={es}
                  />
                </PopoverContent>
              </Popover>
            </div>
          </div>
        </PopoverContent>
      </Popover>
    </div>
  );
}
