/**
 * Lista simplificada de estudios de EEG
 */
import React, { useState } from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button
} from '@mui/material';
import { Visibility as ViewIcon, Error as ErrorIcon, Warning as WarningIcon, CheckCircle as CheckIcon, PictureAsPdf as PdfIcon, Psychology as BrainIcon } from '@mui/icons-material';
import { EstudioEEG } from '../../types/estudiosEspeciales';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import api from '../../lib/api';

interface Props {
  pacienteId: string;
  estudios: EstudioEEG[];
  onActualizar: () => void;
}

const ListaEstudiosEEG: React.FC<Props> = ({ estudios, onActualizar }) => {
  const [estudioSeleccionado, setEstudioSeleccionado] = useState<EstudioEEG | null>(null);
  const [dialogoAbierto, setDialogoAbierto] = useState(false);
  const [descargandoPDF, setDescargandoPDF] = useState(false);
  const [interpretandoIA, setInterpretandoIA] = useState(false);
  const [interpretacionIA, setInterpretacionIA] = useState<string | null>(null);

  const handleDescargarPDFAnalisis = async () => {
    if (!estudioSeleccionado) return;
    
    try {
      setDescargandoPDF(true);
      const response = await api.get(
        `/estudios-especiales/eeg/${estudioSeleccionado.id}/pdf-analisis`,
        { responseType: 'blob' }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `EEG_Analisis_${estudioSeleccionado.id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
    } catch (error: any) {
      console.error('Error al descargar PDF:', error);
      const mensaje = error.response?.data?.detail || error.message || 'Error al generar el PDF de análisis';
      alert(mensaje);
    } finally {
      setDescargandoPDF(false);
    }
  };

  const handleDescargarPDFInterpretacion = async () => {
    if (!estudioSeleccionado) return;
    
    try {
      setDescargandoPDF(true);
      const response = await api.get(
        `/estudios-especiales/eeg/${estudioSeleccionado.id}/pdf-interpretacion`,
        { responseType: 'blob' }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `EEG_Interpretacion_${estudioSeleccionado.id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
    } catch (error: any) {
      console.error('Error al descargar PDF:', error);
      const mensaje = error.response?.data?.detail || error.message || 'Error al generar el PDF de interpretación';
      alert(mensaje);
    } finally {
      setDescargandoPDF(false);
    }
  };

  const handleInterpretarConIA = async () => {
    if (!estudioSeleccionado) return;
    
    try {
      setInterpretandoIA(true);
      const response = await api.post(`/estudios-especiales/eeg/${estudioSeleccionado.id}/interpretar-ia`);
      setInterpretacionIA(response.data.interpretacion_ia);
      onActualizar();
      
    } catch (error: any) {
      console.error('Error al interpretar con IA:', error);
      alert(error.response?.data?.detail || 'Error al interpretar con IA');
    } finally {
      setInterpretandoIA(false);
    }
  };

  if (estudios.length === 0) {
    return <Box textAlign="center" py={4}><Typography color="textSecondary">No hay estudios de EEG registrados</Typography></Box>;
  }

  return (
    <>
      <TableContainer component={Paper} variant="outlined">
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Fecha</TableCell>
              <TableCell>Tipo</TableCell>
              <TableCell>Motivo</TableCell>
              <TableCell align="center">Clasificación</TableCell>
              <TableCell align="center">Acciones</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {estudios.map((estudio) => (
              <TableRow key={estudio.id} hover>
                <TableCell>{format(new Date(estudio.fecha_estudio), 'dd/MM/yyyy HH:mm', { locale: es })}</TableCell>
                <TableCell>{estudio.tipo_estudio}</TableCell>
                <TableCell>{estudio.motivo || '-'}</TableCell>
                <TableCell align="center">
                  <Chip label={estudio.clasificacion || 'Sin clasificar'} size="small"
                    color={estudio.es_critico ? 'error' : estudio.requiere_atencion ? 'warning' : 'success'}
                    icon={estudio.es_critico ? <ErrorIcon /> : estudio.requiere_atencion ? <WarningIcon /> : <CheckIcon />} />
                </TableCell>
                <TableCell align="center">
                  <Tooltip title="Ver detalle">
                    <IconButton size="small" color="primary" onClick={() => { setEstudioSeleccionado(estudio); setDialogoAbierto(true); }}>
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={dialogoAbierto} onClose={() => setDialogoAbierto(false)} maxWidth="md" fullWidth>
        <DialogTitle>🧠 Detalle de Electroencefalograma</DialogTitle>
        <DialogContent>
          {estudioSeleccionado && (
            <Box>
              <Typography variant="body2"><strong>Fecha:</strong> {format(new Date(estudioSeleccionado.fecha_estudio), 'dd/MM/yyyy HH:mm', { locale: es })}</Typography>
              <Typography variant="body2"><strong>Tipo:</strong> {estudioSeleccionado.tipo_estudio}</Typography>
              <Typography variant="body2"><strong>Duración:</strong> {estudioSeleccionado.duracion_minutos} min</Typography>
              
              {(estudioSeleccionado.interpretacion_ia || interpretacionIA) && (
                <Box mt={3}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="subtitle1" sx={{ color: '#8b5cf6' }}>
                      🧠 Interpretación Avanzada con IA
                    </Typography>
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<PdfIcon />}
                      onClick={handleDescargarPDFInterpretacion}
                      disabled={descargandoPDF}
                      sx={{
                        borderColor: '#8b5cf6',
                        color: '#8b5cf6',
                        '&:hover': {
                          borderColor: '#7c3aed',
                          bgcolor: '#f3e8ff'
                        }
                      }}
                    >
                      {descargandoPDF ? 'Generando...' : 'PDF Interpretación'}
                    </Button>
                  </Box>
                  <Paper variant="outlined" sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
                      {interpretacionIA || estudioSeleccionado.interpretacion_ia}
                    </Typography>
                  </Paper>
                </Box>
              )}
              
              {estudioSeleccionado.hallazgos && estudioSeleccionado.hallazgos.length > 0 && (
                <Box mt={2}>
                  <Typography variant="subtitle2" color="primary">Hallazgos:</Typography>
                  {estudioSeleccionado.hallazgos.map((h, i) => <Chip key={i} label={h} size="small" sx={{ mr: 1, mb: 1 }} />)}
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogoAbierto(false)}>Cerrar</Button>
          {estudioSeleccionado && (
            <>
              <Button
                variant="outlined"
                startIcon={<PdfIcon />}
                onClick={handleDescargarPDFAnalisis}
                disabled={descargandoPDF}
                sx={{
                  borderColor: '#8b5cf6',
                  color: '#8b5cf6',
                  '&:hover': {
                    borderColor: '#7c3aed',
                    bgcolor: '#f3e8ff'
                  }
                }}
              >
                {descargandoPDF ? 'Generando...' : 'PDF Análisis'}
              </Button>
              
              <Button
                variant="contained"
                onClick={handleInterpretarConIA}
                disabled={interpretandoIA}
                startIcon={<BrainIcon />}
                sx={{
                  background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)',
                  }
                }}
              >
                {interpretandoIA ? 'Analizando...' : '🧠 Interpretar con IA'}
              </Button>
            </>
          )}
        </DialogActions>
      </Dialog>
    </>
  );
};

export default ListaEstudiosEEG;
