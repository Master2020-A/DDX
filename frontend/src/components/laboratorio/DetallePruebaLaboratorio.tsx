/**
 * Componente para mostrar detalle completo de una prueba de laboratorio
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Alert,
  CircularProgress,
  Divider,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Card,
  CardContent,
  Button
} from '@mui/material';
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
  TrendingDown as TrendingDownIcon,
  TrendingUp as TrendingUpIcon,
  Edit as EditIcon,
  PictureAsPdf as PdfIcon
} from '@mui/icons-material';
import { PruebaLaboratorio, PARAMETROS_LABELS } from '@/types/laboratorio';
import laboratorioService from '@/services/laboratorioService';
import EditarPruebaLaboratorio from './EditarPruebaLaboratorio';

interface DetallePruebaLaboratorioProps {
  pruebaId: string;
  onClose?: () => void;
}

const DetallePruebaLaboratorio: React.FC<DetallePruebaLaboratorioProps> = ({
  pruebaId
}) => {
  const [prueba, setPrueba] = useState<PruebaLaboratorio | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogoEditarAbierto, setDialogoEditarAbierto] = useState(false);
  const [descargandoPDF, setDescargandoPDF] = useState(false);

  const cargarPrueba = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await laboratorioService.obtenerPrueba(pruebaId);
      setPrueba(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar detalle de prueba');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (pruebaId) {
      cargarPrueba();
    }
  }, [pruebaId]);

  const formatearFecha = (fecha: string) => {
    return new Date(fecha).toLocaleDateString('es-MX', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleDescargarPDF = async () => {
    if (!prueba) return;
    
    setDescargandoPDF(true);
    try {
      const blob = await laboratorioService.descargarPDF(prueba.id);
      
      // Crear URL temporal y descargar
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `Laboratorio_${prueba.area}_${prueba.tipo_prueba}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      alert('Error al descargar PDF: ' + (err.response?.data?.detail || err.message));
    } finally {
      setDescargandoPDF(false);
    }
  };

  const obtenerEstadoParametro = (parametro: string) => {
    if (!prueba) return 'normal';
    
    const critico = prueba.valores_criticos?.find(v => v.parametro === parametro);
    if (critico) return critico.estado;
    
    const anormal = prueba.valores_anormales?.find(v => v.parametro === parametro);
    if (anormal) return anormal.estado;
    
    return 'normal';
  };

  const obtenerColorEstado = (estado: string) => {
    switch (estado) {
      case 'critico_bajo':
      case 'critico_alto':
        return 'error';
      case 'bajo':
      case 'alto':
        return 'warning';
      default:
        return 'success';
    }
  };

  const obtenerIconoEstado = (estado: string) => {
    switch (estado) {
      case 'critico_bajo':
      case 'critico_alto':
        return <ErrorIcon />;
      case 'bajo':
        return <TrendingDownIcon />;
      case 'alto':
        return <TrendingUpIcon />;
      default:
        return <CheckCircleIcon />;
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !prueba) {
    return (
      <Alert severity="error">
        {error || 'No se pudo cargar la prueba'}
      </Alert>
    );
  }

  const handleEditarSuccess = () => {
    setDialogoEditarAbierto(false);
    cargarPrueba(); // Recargar datos actualizados
  };

  return (
    <Box>
      {/* Header */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box flex={1}>
            <Typography variant="h5" fontWeight="bold" gutterBottom>
              {prueba.tipo_prueba.replace(/_/g, ' ').toUpperCase()}
            </Typography>
            <Box display="flex" gap={2} flexWrap="wrap">
              <Chip label={prueba.area} color="primary" />
              <Chip label={prueba.estado} color="info" variant="outlined" />
              {prueba.requiere_atencion && (
                <Chip
                  icon={<WarningIcon />}
                  label="Requiere Atención"
                  color="warning"
                />
              )}
            </Box>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="contained"
              startIcon={<PdfIcon />}
              onClick={handleDescargarPDF}
              disabled={descargandoPDF}
              size="small"
              color="error"
            >
              {descargandoPDF ? 'Generando...' : 'Descargar PDF'}
            </Button>
            <Button
              variant="outlined"
              startIcon={<EditIcon />}
              onClick={() => {
                console.log('🔵 Click en botón Editar');
                console.log('🔵 Prueba actual:', prueba);
                console.log('🔵 Estado dialogoEditarAbierto antes:', dialogoEditarAbierto);
                setDialogoEditarAbierto(true);
                console.log('🔵 Abriendo diálogo de edición...');
              }}
              size="small"
            >
              Editar
            </Button>
          </Box>
        </Box>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">
              <strong>Fecha de Resultado:</strong> {formatearFecha(prueba.fecha_resultado || prueba.created_at)}
            </Typography>
          </Grid>
          {prueba.laboratorio_externo && (
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">
                <strong>Laboratorio:</strong> {prueba.laboratorio_externo}
              </Typography>
            </Grid>
          )}
          {prueba.numero_orden && (
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">
                <strong>Número de Orden:</strong> {prueba.numero_orden}
              </Typography>
            </Grid>
          )}
        </Grid>
      </Paper>

      {/* Valores Críticos */}
      {prueba.valores_criticos && prueba.valores_criticos.length > 0 && (
        <Alert severity="error" icon={<ErrorIcon />} sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            🚨 VALORES CRÍTICOS - ATENCIÓN INMEDIATA
          </Typography>
          {prueba.valores_criticos.map((valor, index) => (
            <Typography key={index} variant="body2" sx={{ mt: 1 }}>
              • {valor.interpretacion}
            </Typography>
          ))}
        </Alert>
      )}

      {/* Valores Anormales */}
      {prueba.valores_anormales && prueba.valores_anormales.filter(v => !v.critico).length > 0 && (
        <Alert severity="warning" icon={<WarningIcon />} sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            ⚠️ Valores Fuera de Rango Normal
          </Typography>
          {prueba.valores_anormales
            .filter(v => !v.critico)
            .map((valor, index) => (
              <Typography key={index} variant="body2" sx={{ mt: 1 }}>
                • {valor.interpretacion}
              </Typography>
            ))}
        </Alert>
      )}

      {/* Tabla de Resultados */}
      <Paper elevation={3} sx={{ mb: 3 }}>
        <Box p={2}>
          <Typography variant="h6" gutterBottom color="primary">
            📊 Resultados Detallados
          </Typography>
        </Box>
        <Divider />
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><strong>Parámetro</strong></TableCell>
                <TableCell align="right"><strong>Valor</strong></TableCell>
                <TableCell align="center"><strong>Estado</strong></TableCell>
                <TableCell><strong>Rango de Referencia</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {Object.entries(prueba.resultados).map(([parametro, valor]) => {
                const estado = obtenerEstadoParametro(parametro);
                const valorInfo = [
                  ...(prueba.valores_anormales || []),
                  ...(prueba.valores_criticos || [])
                ].find(v => v.parametro === parametro);
                const label = PARAMETROS_LABELS[parametro] || parametro;

                return (
                  <TableRow
                    key={parametro}
                    sx={{
                      bgcolor: estado !== 'normal' ? `${obtenerColorEstado(estado)}.light` : 'inherit',
                      '&:hover': { bgcolor: 'action.hover' }
                    }}
                  >
                    <TableCell>{label}</TableCell>
                    <TableCell align="right">
                      <Typography fontWeight="bold">
                        {valor} {valorInfo?.unidad || ''}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        icon={obtenerIconoEstado(estado)}
                        label={estado === 'normal' ? 'Normal' : estado.replace(/_/g, ' ').toUpperCase()}
                        color={obtenerColorEstado(estado)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {valorInfo ? (
                        <Typography variant="body2">
                          {valorInfo.rango_min !== null && valorInfo.rango_max !== null
                            ? `${valorInfo.rango_min} - ${valorInfo.rango_max} ${valorInfo.unidad || ''}`
                            : 'N/A'}
                        </Typography>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          Dentro de rango
                        </Typography>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Interpretación Clínica */}
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom color="primary">
          💡 Interpretación Clínica
        </Typography>
        <Divider sx={{ mb: 2 }} />
        <Box
          sx={{
            bgcolor: 'grey.50',
            p: 2,
            borderRadius: 1,
            fontFamily: 'monospace',
            whiteSpace: 'pre-wrap'
          }}
        >
          {prueba.interpretacion || 'No hay interpretación clínica disponible. La prueba puede estar pendiente de análisis.'}
        </Box>

        {prueba.notas_medico && (
          <>
            <Typography variant="h6" gutterBottom color="primary" sx={{ mt: 3 }}>
              📝 Notas del Médico
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="body1">{prueba.notas_medico}</Typography>
          </>
        )}
      </Paper>

      {/* Diálogo de Edición */}
      <EditarPruebaLaboratorio
        open={dialogoEditarAbierto}
        prueba={prueba}
        onClose={() => setDialogoEditarAbierto(false)}
        onSuccess={handleEditarSuccess}
      />
    </Box>
  );
};

export default DetallePruebaLaboratorio;
