import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send, Loader2, User, Stethoscope } from 'lucide-react';
import portalPacienteService, { MensajePacienteMedico } from '@/services/portalPacienteService';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

interface ChatMedicoProps {
  pacienteId: string;
  medicoId: string;
  medicoNombre: string;
}

export default function ChatMedico({ pacienteId, medicoId, medicoNombre }: ChatMedicoProps) {
  const [mensajes, setMensajes] = useState<MensajePacienteMedico[]>([]);
  const [nuevoMensaje, setNuevoMensaje] = useState('');
  const [loading, setLoading] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    cargarMensajes();
    const interval = setInterval(cargarMensajes, 5000); // Actualizar cada 5 segundos
    return () => clearInterval(interval);
  }, [pacienteId, medicoId]);

  useEffect(() => {
    scrollToBottom();
  }, [mensajes]);

  const cargarMensajes = async () => {
    setLoading(true);
    try {
      const data = await portalPacienteService.getMensajes(pacienteId, medicoId);
      setMensajes(data.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()));
      
      // Marcar mensajes no leídos como leídos
      data.forEach(async (msg) => {
        if (!msg.leido && msg.remitente_tipo === 'medico') {
          await portalPacienteService.marcarMensajeLeido(msg.id);
        }
      });
    } catch (err) {
      console.error('Error al cargar mensajes:', err);
    } finally {
      setLoading(false);
    }
  };

  const scrollToBottom = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  };

  const enviarMensaje = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!nuevoMensaje.trim()) return;

    setEnviando(true);
    try {
      const mensaje = await portalPacienteService.enviarMensaje({
        paciente_id: pacienteId,
        medico_id: medicoId,
        remitente_tipo: 'paciente',
        mensaje: nuevoMensaje,
        estado: 'enviado',
        leido: false,
      });

      setMensajes([...mensajes, mensaje]);
      setNuevoMensaje('');
    } catch (err) {
      console.error('Error al enviar mensaje:', err);
    } finally {
      setEnviando(false);
    }
  };

  return (
    <Card className="flex flex-col h-[600px]">
      <CardHeader className="border-b">
        <CardTitle className="flex items-center gap-2">
          <Stethoscope className="h-5 w-5" />
          Chat con {medicoNombre}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col p-0">
        <ScrollArea className="flex-1 p-4" ref={scrollRef}>
          {loading && mensajes.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : mensajes.length === 0 ? (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              No hay mensajes. Envía el primero para iniciar la conversación.
            </div>
          ) : (
            <div className="space-y-4">
              {mensajes.map((mensaje) => {
                const esPaciente = mensaje.remitente_tipo === 'paciente';
                return (
                  <div
                    key={mensaje.id}
                    className={`flex gap-3 ${esPaciente ? 'flex-row-reverse' : ''}`}
                  >
                    <Avatar className="h-8 w-8">
                      <AvatarFallback>
                        {esPaciente ? <User className="h-4 w-4" /> : <Stethoscope className="h-4 w-4" />}
                      </AvatarFallback>
                    </Avatar>
                    <div className={`flex-1 max-w-[70%] ${esPaciente ? 'items-end' : ''}`}>
                      <div
                        className={`
                          p-3 rounded-lg
                          ${esPaciente 
                            ? 'bg-primary text-primary-foreground ml-auto' 
                            : 'bg-muted'
                          }
                        `}
                      >
                        {mensaje.asunto && (
                          <div className="font-semibold mb-1 text-sm">
                            {mensaje.asunto}
                          </div>
                        )}
                        <p className="text-sm whitespace-pre-wrap">{mensaje.mensaje}</p>
                      </div>
                      <div className={`text-xs text-muted-foreground mt-1 ${esPaciente ? 'text-right' : ''}`}>
                        {format(new Date(mensaje.created_at), 'PPp', { locale: es })}
                        {!mensaje.leido && mensaje.remitente_tipo === 'paciente' && (
                          <span className="ml-2">Enviado</span>
                        )}
                        {mensaje.leido && mensaje.remitente_tipo === 'paciente' && (
                          <span className="ml-2">Leído</span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </ScrollArea>

        <form onSubmit={enviarMensaje} className="p-4 border-t">
          <div className="flex gap-2">
            <Input
              placeholder="Escribe tu mensaje..."
              value={nuevoMensaje}
              onChange={(e) => setNuevoMensaje(e.target.value)}
              disabled={enviando}
              className="flex-1"
            />
            <Button type="submit" disabled={enviando || !nuevoMensaje.trim()}>
              {enviando ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
