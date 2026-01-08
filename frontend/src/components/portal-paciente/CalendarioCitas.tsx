import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight, Clock } from 'lucide-react';
import { CitaPaciente } from '@/services/portalPacienteService';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameDay, isSameMonth, addMonths, subMonths } from 'date-fns';
import { es } from 'date-fns/locale';

interface CalendarioCitasProps {
  citas: CitaPaciente[];
  onCitaClick: (cita: CitaPaciente) => void;
}

export default function CalendarioCitas({ citas, onCitaClick }: CalendarioCitasProps) {
  const [mesActual, setMesActual] = useState(new Date());
  const [diasDelMes, setDiasDelMes] = useState<Date[]>([]);

  useEffect(() => {
    const inicio = startOfMonth(mesActual);
    const fin = endOfMonth(mesActual);
    const dias = eachDayOfInterval({ start: inicio, end: fin });
    setDiasDelMes(dias);
  }, [mesActual]);

  const getCitasDelDia = (dia: Date) => {
    return citas.filter(cita => {
      const fechaCita = new Date(cita.fecha_solicitada);
      return isSameDay(fechaCita, dia);
    });
  };

  const getColorEstado = (estado: string) => {
    const colores: Record<string, string> = {
      confirmada: 'bg-green-500',
      solicitada: 'bg-yellow-500',
      cancelada: 'bg-red-500',
      completada: 'bg-blue-500',
    };
    return colores[estado] || 'bg-gray-500';
  };

  const mesAnterior = () => {
    setMesActual(subMonths(mesActual, 1));
  };

  const mesSiguiente = () => {
    setMesActual(addMonths(mesActual, 1));
  };

  const hoy = () => {
    setMesActual(new Date());
  };

  const diasSemana = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <CalendarIcon className="h-5 w-5" />
            Calendario de Citas
          </CardTitle>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={hoy}>
              Hoy
            </Button>
            <Button variant="outline" size="icon" onClick={mesAnterior}>
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-lg font-semibold min-w-[200px] text-center">
              {format(mesActual, 'MMMM yyyy', { locale: es })}
            </span>
            <Button variant="outline" size="icon" onClick={mesSiguiente}>
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-7 gap-2">
          {/* Encabezados de días */}
          {diasSemana.map((dia) => (
            <div key={dia} className="text-center font-semibold text-sm text-muted-foreground py-2">
              {dia}
            </div>
          ))}

          {/* Días del mes */}
          {diasDelMes.map((dia, index) => {
            const citasDelDia = getCitasDelDia(dia);
            const esHoy = isSameDay(dia, new Date());
            const esMesActual = isSameMonth(dia, mesActual);

            return (
              <div
                key={index}
                className={`
                  min-h-[100px] p-2 border rounded-lg
                  ${esMesActual ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-900'}
                  ${esHoy ? 'ring-2 ring-primary' : ''}
                  hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors
                `}
              >
                <div className={`text-sm font-medium mb-1 ${esHoy ? 'text-primary' : ''}`}>
                  {format(dia, 'd')}
                </div>
                <div className="space-y-1">
                  {citasDelDia.map((cita) => (
                    <button
                      key={cita.id}
                      onClick={() => onCitaClick(cita)}
                      className={`
                        w-full text-left p-1 rounded text-xs
                        ${getColorEstado(cita.estado)} text-white
                        hover:opacity-80 transition-opacity
                      `}
                    >
                      <div className="flex items-center gap-1">
                        {cita.hora_solicitada && (
                          <Clock className="h-3 w-3" />
                        )}
                        <span className="truncate">
                          {cita.hora_solicitada ? format(new Date(`2000-01-01T${cita.hora_solicitada}`), 'HH:mm') : 'Sin hora'}
                        </span>
                      </div>
                      <div className="truncate font-medium">
                        {cita.especialidad_solicitada || cita.tipo_cita}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        {/* Leyenda */}
        <div className="mt-4 flex items-center gap-4 text-sm">
          <span className="font-medium">Leyenda:</span>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-green-500"></div>
            <span>Confirmada</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-yellow-500"></div>
            <span>Solicitada</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-blue-500"></div>
            <span>Completada</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-red-500"></div>
            <span>Cancelada</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
