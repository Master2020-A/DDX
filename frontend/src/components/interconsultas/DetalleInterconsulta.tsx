/**
 * Componente de detalle de interconsulta con chat
 */
import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  Box,
  Typography,
  Chip,
  Grid,
  Card,
  CardContent,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  Divider,
  IconButton,
  Alert,
} from '@mui/material';
import {
  Close as CloseIcon,
  Send as SendIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import { interconsultaService, mensajeService } from '@/services/interconsultaService';
import { ESTADOS, URGENCIAS } from '@/types/interconsulta';
import type { Interconsulta, MensajeInterconsulta } from '@/types/interconsulta';

interface Props {
  open: boolean;
  interconsultaId: string | null;
  onClose: () => void;
  onActualizar?: () => void;
}

export default function DetalleInterconsulta({ open, interconsultaId, onClose, onActualizar }: Props) {
  const [interconsulta, setInterconsulta] = useState<Interconsulta | null>(null);
  const [mensajes, setMensajes] = useState<MensajeInterconsulta[]>([]);
  const [nuevoMensaje, setNuevoMensaje] = useState('');
  const [cargando, setCargando] = useState(false);

  useEffect(() => {
    if (open && interconsultaId) {
      cargarDatos();
    }
  }, [open, interconsultaId]);

  const cargarDatos = async () => {
    if (!interconsultaId) return;
    
    try {
      setCargando(true);
      const [ic, msgs] = await Promise.all([
        interconsultaService.obtener(interconsultaId),
        mensajeService.obtener(interconsultaId)
      ]);
      setInterconsulta(ic);
      setMensajes(msgs);
    } catch (err) {
      console.error(err);
    } finally {
      setCargando(false);
    }
  };

  const handleEnviarMensaje = async () => {
    if (!nuevoMensaje.trim() || !interconsultaId) return;

    try {
      await mensajeService.enviar({
        interconsulta_id: interconsultaId,
        mensaje: nuevoMensaje
      });
      setNuevoMensaje('');
      cargarDatos();
    } catch (err) {
      console.error(err);
    }
  };

  const handleAceptar = async () => {
    if (!interconsultaId) return;
    try {
      await interconsultaService.aceptar(interconsultaId, {});
      cargarDatos();
      onActualizar?.();
    } catch (err) {
      console.error(err);
    }
  };

  const handleRechazar = async () => {
    if (!interconsultaId) return;
    const motivo = prompt('Motivo del rechazo:');
    if (!motivo) return;

    try {
      await interconsultaService.rechazar(interconsultaId, { motivo_rechazo: motivo });
      cargarDatos();
      onActualizar?.();
    } catch (err) {
      console.error(err);
    }
  };

  if (!interconsulta) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">Detalle de Interconsulta</Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={2}>
          {/* Información General */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="body2" color="text.secondary">Especialidad</Typography>
                    <Typography variant="body1" fontWeight="bold">
                      {interconsulta.especialidad_requerida}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Typography variant="body2" color="text.secondary">Urgencia</Typography>
                    <Chip
                      label={URGENCIAS[interconsulta.urgencia as keyof typeof URGENCIAS]?.label}
                      color={URGENCIAS[interconsulta.urgencia as keyof typeof URGENCIAS]?.color as any}
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Typography variant="body2" color="text.secondary">Estado</Typography>
                    <Chip
                      label={ESTADOS[interconsulta.estado as keyof typeof ESTADOS]?.label}
                      color={ESTADOS[interconsulta.estado as keyof typeof ESTADOS]?.color as any}
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">Motivo de Solicitud</Typography>
                    <Typography variant="body1">{interconsulta.motivo_solicitud}</Typography>
                  </Grid>
                  {interconsulta.antecedentes_relevantes && (
                    <Grid item xs={12}>
                      <Typography variant="body2" color="text.secondary">Antecedentes</Typography>
                      <Typography variant="body1">{interconsulta.antecedentes_relevantes}</Typography>
                    </Grid>
                  )}
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Respuesta del Especialista */}
          {interconsulta.diagnostico_especialista && (
            <Grid item xs={12}>
              <Card sx={{ bgcolor: 'success.light' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Respuesta del Especialista</Typography>
                  <Typography variant="body2" color="text.secondary">Diagnóstico</Typography>
                  <Typography variant="body1" paragraph>{interconsulta.diagnostico_especialista}</Typography>
                  {interconsulta.recomendaciones && (
                    <>
                      <Typography variant="body2" color="text.secondary">Recomendaciones</Typography>
                      <Typography variant="body1">{interconsulta.recomendaciones}</Typography>
                    </>
                  )}
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Acciones */}
          {interconsulta.estado === 'solicitada' && (
            <Grid item xs={12}>
              <Box display="flex" gap={2}>
                <Button
                  variant="contained"
                  color="success"
                  startIcon={<CheckCircleIcon />}
                  onClick={handleAceptar}
                >
                  Aceptar Interconsulta
                </Button>
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<CancelIcon />}
                  onClick={handleRechazar}
                >
                  Rechazar
                </Button>
              </Box>
            </Grid>
          )}

          {/* Chat */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>💬 Chat</Typography>
                <Box sx={{ maxHeight: 300, overflowY: 'auto', mb: 2 }}>
                  <List>
                    {mensajes.length === 0 ? (
                      <Alert severity="info">No hay mensajes aún</Alert>
                    ) : (
                      mensajes.map((msg) => (
                        <React.Fragment key={msg.id}>
                          <ListItem>
                            <ListItemText
                              primary={msg.mensaje}
                              secondary={new Date(msg.created_at).toLocaleString()}
                            />
                          </ListItem>
                          <Divider />
                        </React.Fragment>
                      ))
                    )}
                  </List>
                </Box>
                <Box display="flex" gap={1}>
                  <TextField
                    fullWidth
                    size="small"
                    placeholder="Escribe un mensaje..."
                    value={nuevoMensaje}
                    onChange={(e) => setNuevoMensaje(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleEnviarMensaje()}
                  />
                  <Button
                    variant="contained"
                    onClick={handleEnviarMensaje}
                    disabled={!nuevoMensaje.trim()}
                  >
                    <SendIcon />
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </DialogContent>
    </Dialog>
  );
}
