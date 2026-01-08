/**
 * Lista de estudios de EKG de un paciente
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
import {
  Visibility as ViewIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Psychology as BrainIcon,
  PictureAsPdf as PdfIcon
} from '@mui/icons-material';
import { EstudioEKG } from '../../types/estudiosEspeciales';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import api from '@/lib/api';

interface Props {
  pacienteId: string;
  estudios: EstudioEKG[];
  onActualizar: () => void;
}

const ListaEstudiosEKG: React.FC<Props> = ({ estudios, onActualizar }) => {
  const [estudioSeleccionado, setEstudioSeleccionado] = useState<EstudioEKG | null>(null);
  const [dialogoAbierto, setDialogoAbierto] = useState(false);
  const [interpretandoIA, setInterpretandoIA] = useState(false);
  const [interpretacionIA, setInterpretacionIA] = useState<any>(null);
  const [descargandoPDF, setDescargandoPDF] = useState(false);

  const handleVerDetalle = (estudio: EstudioEKG) => {
    setEstudioSeleccionado(estudio);
    setInterpretacionIA(null); // Limpiar interpretación anterior
    setDialogoAbierto(true);
  };

  const handleInterpretarConIA = async () => {
    if (!estudioSeleccionado) return;
    
    try {
      setInterpretandoIA(true);
      const response = await api.post(`/estudios-especiales/ekg/${estudioSeleccionado.id}/interpretar-ia`);
      setInterpretacionIA(response.data.interpretacion_ia);
      
      // Actualizar la lista
      onActualizar();
      
    } catch (error: any) {
      console.error('Error al interpretar con IA:', error);
      alert(error.response?.data?.detail || 'Error al interpretar con IA');
    } finally {
      setInterpretandoIA(false);
    }
  };

  const handleDescargarPDFAnalisis = async () => {
    if (!estudioSeleccionado) return;
    
    try {
      setDescargandoPDF(true);
      const response = await api.get(
        `/estudios-especiales/ekg/${estudioSeleccionado.id}/pdf-analisis`,
        { responseType: 'blob' }
      );
      
      // Verificar si la respuesta es un error JSON
      if (response.data.type === 'application/json') {
        const text = await response.data.text();
        const errorData = JSON.parse(text);
        throw new Error(errorData.detail || 'Error al generar PDF');
      }
      
      // Crear URL del blob y descargar
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `EKG_Analisis_${estudioSeleccionado.id}.pdf`);
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
        `/estudios-especiales/ekg/${estudioSeleccionado.id}/pdf-interpretacion`,
        { responseType: 'blob' }
      );
      
      // Crear URL del blob y descargar
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `EKG_Interpretacion_${estudioSeleccionado.id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
    } catch (error: any) {
      console.error('Error al descargar PDF:', error);
      alert('Error al generar el PDF de interpretación');
    } finally {
      setDescargandoPDF(false);
    }
  };

  const getChipColor = (clasificacion?: string) => {
    switch (clasificacion) {
      case 'normal':
        return 'success';
      case 'anormal_leve':
        return 'info';
      case 'anormal_moderado':
        return 'warning';
      case 'anormal_severo':
        return 'error';
      default:
        return 'default';
    }
  };

  const getClasificacionLabel = (clasificacion?: string) => {
    switch (clasificacion) {
      case 'normal':
        return 'Normal';
      case 'anormal_leve':
        return 'Anormal Leve';
      case 'anormal_moderado':
        return 'Anormal Moderado';
      case 'anormal_severo':
        return 'Anormal Severo';
      default:
        return 'Sin clasificar';
    }
  };

  if (estudios.length === 0) {
    return (
      <Box textAlign="center" py={4}>
        <Typography color="textSecondary">
          No hay estudios de EKG registrados
        </Typography>
      </Box>
    );
  }

  return (
    <>
      <TableContainer component={Paper} variant="outlined">
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Fecha</TableCell>
              <TableCell>Motivo</TableCell>
              <TableCell align="center">FC (lpm)</TableCell>
              <TableCell align="center">Ritmo</TableCell>
              <TableCell align="center">Clasificación</TableCell>
              <TableCell align="center">Estado</TableCell>
              <TableCell align="center">Acciones</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {estudios.map((estudio) => (
              <TableRow key={estudio.id} hover>
                <TableCell>
                  {format(new Date(estudio.fecha_estudio), 'dd/MM/yyyy HH:mm', { locale: es })}
                </TableCell>
                <TableCell>{estudio.motivo || '-'}</TableCell>
                <TableCell align="center">
                  {estudio.frecuencia_cardiaca || '-'}
                </TableCell>
                <TableCell align="center">
                  {estudio.ritmo || '-'}
                </TableCell>
                <TableCell align="center">
                  <Chip
                    label={getClasificacionLabel(estudio.clasificacion)}
                    color={getChipColor(estudio.clasificacion)}
                    size="small"
                    icon={
                      estudio.es_critico ? <ErrorIcon /> :
                      estudio.requiere_atencion ? <WarningIcon /> :
                      <CheckIcon />
                    }
                  />
                </TableCell>
                <TableCell align="center">
                  <Chip
                    label={estudio.estado}
                    size="small"
                    variant="outlined"
                  />
                </TableCell>
                <TableCell align="center">
                  <Tooltip title="Ver detalle">
                    <IconButton
                      size="small"
                      color="primary"
                      onClick={() => handleVerDetalle(estudio)}
                    >
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Diálogo de detalle */}
      <Dialog
        open={dialogoAbierto}
        onClose={() => setDialogoAbierto(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          ❤️ Detalle de Electrocardiograma
        </DialogTitle>
        <DialogContent>
          {estudioSeleccionado && (
            <Box>
              {/* Alertas */}
              {estudioSeleccionado.es_critico && (
                <Box mb={2}>
                  <Chip
                    icon={<ErrorIcon />}
                    label="ESTUDIO CRÍTICO - Requiere atención inmediata"
                    color="error"
                    sx={{ width: '100%', justifyContent: 'flex-start', py: 2 }}
                  />
                </Box>
              )}
              {estudioSeleccionado.requiere_atencion && !estudioSeleccionado.es_critico && (
                <Box mb={2}>
                  <Chip
                    icon={<WarningIcon />}
                    label="Requiere atención médica"
                    color="warning"
                    sx={{ width: '100%', justifyContent: 'flex-start', py: 2 }}
                  />
                </Box>
              )}

              {/* Información general */}
              <Typography variant="subtitle1" color="primary" gutterBottom>
                Información General
              </Typography>
              <Box mb={2}>
                <Typography variant="body2">
                  <strong>Fecha:</strong> {format(new Date(estudioSeleccionado.fecha_estudio), 'dd/MM/yyyy HH:mm', { locale: es })}
                </Typography>
                <Typography variant="body2">
                  <strong>Motivo:</strong> {estudioSeleccionado.motivo || 'No especificado'}
                </Typography>
                {estudioSeleccionado.indicacion_clinica && (
                  <Typography variant="body2">
                    <strong>Indicación:</strong> {estudioSeleccionado.indicacion_clinica}
                  </Typography>
                )}
              </Box>

              {/* Parámetros medidos */}
              <Typography variant="subtitle1" color="primary" gutterBottom>
                Parámetros Medidos
              </Typography>
              <Box mb={2} display="grid" gridTemplateColumns="repeat(2, 1fr)" gap={1}>
                <Typography variant="body2">
                  <strong>Frecuencia Cardíaca:</strong> {estudioSeleccionado.frecuencia_cardiaca || '-'} lpm
                </Typography>
                <Typography variant="body2">
                  <strong>Intervalo PR:</strong> {estudioSeleccionado.intervalo_pr || '-'} ms
                </Typography>
                <Typography variant="body2">
                  <strong>Duración QRS:</strong> {estudioSeleccionado.duracion_qrs || '-'} ms
                </Typography>
                <Typography variant="body2">
                  <strong>Intervalo QTc:</strong> {estudioSeleccionado.intervalo_qtc || '-'} ms
                </Typography>
                <Typography variant="body2">
                  <strong>Eje QRS:</strong> {estudioSeleccionado.eje_qrs || '-'}°
                </Typography>
                <Typography variant="body2">
                  <strong>Ritmo:</strong> {estudioSeleccionado.ritmo || '-'}
                </Typography>
              </Box>

              {/* Hallazgos */}
              {estudioSeleccionado.hallazgos && estudioSeleccionado.hallazgos.length > 0 && (
                <>
                  <Typography variant="subtitle1" color="primary" gutterBottom>
                    Hallazgos
                  </Typography>
                  <Box mb={2}>
                    {estudioSeleccionado.hallazgos.map((hallazgo, index) => (
                      <Chip
                        key={index}
                        label={hallazgo}
                        size="small"
                        sx={{ mr: 1, mb: 1 }}
                        color="warning"
                      />
                    ))}
                  </Box>
                </>
              )}

              {/* Interpretación */}
              {estudioSeleccionado.interpretacion_ia && (
                <>
                  <Typography variant="subtitle1" color="primary" gutterBottom>
                    Interpretación Automática
                  </Typography>
                  <Paper variant="outlined" sx={{ p: 2, mb: 2, bgcolor: 'grey.50' }}>
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
                      {estudioSeleccionado.interpretacion_ia}
                    </Typography>
                  </Paper>
                </>
              )}

              {/* Recomendaciones */}
              {estudioSeleccionado.recomendaciones && (
                <>
                  <Typography variant="subtitle1" color="primary" gutterBottom>
                    Recomendaciones
                  </Typography>
                  <Paper variant="outlined" sx={{ p: 2, bgcolor: 'info.light' }}>
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
                      {estudioSeleccionado.recomendaciones}
                    </Typography>
                  </Paper>
                </>
              )}

              {/* Interpretación con IA */}
              {interpretacionIA && (
                <>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mt={3} mb={1}>
                    <Typography variant="subtitle1" sx={{ color: '#9333ea' }}>
                      🧠 Interpretación Avanzada con IA
                    </Typography>
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<PdfIcon />}
                      onClick={handleDescargarPDFInterpretacion}
                      disabled={descargandoPDF}
                      sx={{
                        borderColor: '#9333ea',
                        color: '#9333ea',
                        '&:hover': {
                          borderColor: '#7c3aed',
                          bgcolor: '#f3e8ff'
                        }
                      }}
                    >
                      {descargandoPDF ? 'Generando...' : 'PDF Interpretación'}
                    </Button>
                  </Box>
                  
                  {/* Diagnóstico Principal */}
                  {interpretacionIA.diagnostico_principal && (
                    <Paper variant="outlined" sx={{ p: 2, mb: 2, bgcolor: '#f3f4f6', borderLeft: '4px solid #9333ea' }}>
                      <Typography variant="subtitle2" gutterBottom>
                        <strong>Diagnóstico Principal:</strong>
                      </Typography>
                      <Typography variant="body2">
                        {interpretacionIA.diagnostico_principal}
                      </Typography>
                    </Paper>
                  )}

                  {/* Interpretación */}
                  {interpretacionIA.interpretacion && (
                    <Paper variant="outlined" sx={{ p: 2, mb: 2, bgcolor: 'grey.50' }}>
                      <Typography variant="subtitle2" gutterBottom>
                        <strong>Interpretación Clínica:</strong>
                      </Typography>
                      <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
                        {interpretacionIA.interpretacion}
                      </Typography>
                    </Paper>
                  )}

                  {/* Hallazgos Clave */}
                  {interpretacionIA.hallazgos_clave && interpretacionIA.hallazgos_clave.length > 0 && (
                    <Box mb={2}>
                      <Typography variant="subtitle2" gutterBottom>
                        <strong>Hallazgos Clave:</strong>
                      </Typography>
                      {interpretacionIA.hallazgos_clave.map((hallazgo: any, index: number) => (
                        <Paper key={index} variant="outlined" sx={{ p: 1.5, mb: 1, bgcolor: 'info.light' }}>
                          <Typography variant="body2">
                            <strong>{hallazgo.parametro}:</strong> {hallazgo.valor} - {hallazgo.interpretacion}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {hallazgo.significado_clinico}
                          </Typography>
                        </Paper>
                      ))}
                    </Box>
                  )}

                  {/* Recomendaciones de IA */}
                  {interpretacionIA.recomendaciones && interpretacionIA.recomendaciones.length > 0 && (
                    <Paper variant="outlined" sx={{ p: 2, mb: 2, bgcolor: 'success.light' }}>
                      <Typography variant="subtitle2" gutterBottom>
                        <strong>💡 Recomendaciones:</strong>
                      </Typography>
                      {interpretacionIA.recomendaciones.map((rec: string, index: number) => (
                        <Typography key={index} variant="body2">
                          • {rec}
                        </Typography>
                      ))}
                    </Paper>
                  )}

                  {/* Diagnósticos Diferenciales */}
                  {interpretacionIA.diagnosticos_diferenciales && interpretacionIA.diagnosticos_diferenciales.length > 0 && (
                    <Box mb={2}>
                      <Typography variant="subtitle2" gutterBottom>
                        <strong>🔍 Diagnósticos Diferenciales:</strong>
                      </Typography>
                      {interpretacionIA.diagnosticos_diferenciales.map((diag: any, index: number) => (
                        <Paper key={index} variant="outlined" sx={{ p: 1.5, mb: 1 }}>
                          <Typography variant="body2">
                            <strong>{diag.diagnostico}</strong> - Probabilidad: {diag.probabilidad}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {diag.criterios}
                          </Typography>
                        </Paper>
                      ))}
                    </Box>
                  )}
                </>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogoAbierto(false)}>
            Cerrar
          </Button>
          {estudioSeleccionado && (
            <>
              <Button
                variant="outlined"
                startIcon={<PdfIcon />}
                onClick={handleDescargarPDFAnalisis}
                disabled={descargandoPDF}
                sx={{
                  borderColor: '#3b82f6',
                  color: '#3b82f6',
                  '&:hover': {
                    borderColor: '#2563eb',
                    bgcolor: '#eff6ff'
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
                  background: 'linear-gradient(135deg, #9333ea 0%, #7c3aed 100%)',
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

export default ListaEstudiosEKG;
