/**
 * Componente para comparar dos pruebas de laboratorio del mismo tipo
 */
import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Box,
  Chip,
  Alert,
  CircularProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import {
  Close as CloseIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Remove as RemoveIcon,
  CompareArrows as CompareIcon
} from '@mui/icons-material';
import { PruebaLaboratorio, PruebaLaboratorioResumen } from '@/types/laboratorio';
import laboratorioService from '@/services/laboratorioService';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';

interface ComparadorPruebasProps {
  open: boolean;
  onClose: () => void;
  pacienteId: string;
  pruebaActualId?: string;
}

const ComparadorPruebas: React.FC<ComparadorPruebasProps> = ({
  open,
  onClose,
  pacienteId,
  pruebaActualId
}) => {
  const [pruebas, setPruebas] = useState<PruebaLaboratorioResumen[]>([]);
  const [prueba1, setPrueba1] = useState<PruebaLaboratorio | null>(null);
  const [prueba2, setPrueba2] = useState<PruebaLaboratorio | null>(null);
  const [prueba1Id, setPrueba1Id] = useState<string>('');
  const [prueba2Id, setPrueba2Id] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [parametroSeleccionado, setParametroSeleccionado] = useState<string>('');

  useEffect(() => {
    if (open && pacienteId) {
      cargarPruebas();
    }
  }, [open, pacienteId]);

  useEffect(() => {
    if (pruebaActualId && pruebas.length > 0) {
      setPrueba1Id(pruebaActualId);
      cargarPrueba(pruebaActualId, 1);
    }
  }, [pruebaActualId, pruebas]);

  const cargarPruebas = async () => {
    setLoading(true);
    try {
      const data = await laboratorioService.listarPruebasPaciente(pacienteId);
      // Ordenar por fecha descendente
      data.sort((a, b) => new Date(b.fecha).getTime() - new Date(a.fecha).getTime());
      setPruebas(data);
    } catch (error) {
      console.error('Error cargando pruebas:', error);
    } finally {
      setLoading(false);
    }
  };

  const cargarPrueba = async (pruebaId: string, numero: 1 | 2) => {
    if (!pruebaId) return;
    
    setLoading(true);
    try {
      const data = await laboratorioService.obtenerPrueba(pruebaId);
      if (numero === 1) {
        setPrueba1(data);
        // Auto-seleccionar primer parámetro
        if (data.resultados && data.resultados.length > 0) {
          setParametroSeleccionado(data.resultados[0].parametro);
        }
      } else {
        setPrueba2(data);
      }
    } catch (error) {
      console.error('Error cargando prueba:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePrueba1Change = (pruebaId: string) => {
    setPrueba1Id(pruebaId);
    cargarPrueba(pruebaId, 1);
  };

  const handlePrueba2Change = (pruebaId: string) => {
    setPrueba2Id(pruebaId);
    cargarPrueba(pruebaId, 2);
  };

  const calcularDiferencia = (valor1: number, valor2: number): number => {
    return ((valor1 - valor2) / valor2) * 100;
  };

  const obtenerTendencia = (valor1: number, valor2: number) => {
    const diff = valor1 - valor2;
    if (Math.abs(diff) < 0.01) {
      return { icono: <RemoveIcon />, color: 'default', texto: 'Sin cambio' };
    } else if (diff > 0) {
      return { icono: <TrendingUpIcon />, color: 'error', texto: 'Aumentó' };
    } else {
      return { icono: <TrendingDownIcon />, color: 'success', texto: 'Disminuyó' };
    }
  };

  const formatearFecha = (fecha: string) => {
    return new Date(fecha).toLocaleDateString('es-MX', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const obtenerParametrosComunes = () => {
    if (!prueba1 || !prueba2) return [];
    
    const params1 = prueba1.resultados?.map(r => r.parametro) || [];
    const params2 = prueba2.resultados?.map(r => r.parametro) || [];
    
    return params1.filter(p => params2.includes(p));
  };

  const obtenerValorParametro = (prueba: PruebaLaboratorio | null, parametro: string) => {
    if (!prueba || !prueba.resultados) return null;
    const resultado = prueba.resultados.find(r => r.parametro === parametro);
    return resultado ? resultado.valor : null;
  };

  const obtenerDatosGrafica = () => {
    const parametrosComunes = obtenerParametrosComunes();
    
    return parametrosComunes.map(param => {
      const valor1 = obtenerValorParametro(prueba1, param);
      const valor2 = obtenerValorParametro(prueba2, param);
      
      return {
        parametro: param,
        [prueba1?.fecha || 'Prueba 1']: valor1,
        [prueba2?.fecha || 'Prueba 2']: valor2
      };
    });
  };

  const parametrosComunes = obtenerParametrosComunes();
  const puedenComparar = prueba1 && prueba2 && parametrosComunes.length > 0;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center" gap={1}>
            <CompareIcon />
            <Typography variant="h6">Comparar Pruebas de Laboratorio</Typography>
          </Box>
          <Button onClick={onClose} startIcon={<CloseIcon />}>
            Cerrar
          </Button>
        </Box>
      </DialogTitle>

      <DialogContent>
        {loading && (
          <Box display="flex" justifyContent="center" p={3}>
            <CircularProgress />
          </Box>
        )}

        {/* Selectores de pruebas */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Prueba 1 (Más reciente)</InputLabel>
              <Select
                value={prueba1Id}
                onChange={(e) => handlePrueba1Change(e.target.value)}
                label="Prueba 1 (Más reciente)"
              >
                {pruebas.map(p => (
                  <MenuItem key={p.id} value={p.id}>
                    {p.area.replace('_', ' ')} - {p.tipo_prueba.replace('_', ' ')} ({formatearFecha(p.fecha)})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Prueba 2 (Anterior)</InputLabel>
              <Select
                value={prueba2Id}
                onChange={(e) => handlePrueba2Change(e.target.value)}
                label="Prueba 2 (Anterior)"
                disabled={!prueba1Id}
              >
                {pruebas
                  .filter(p => p.id !== prueba1Id)
                  .map(p => (
                    <MenuItem key={p.id} value={p.id}>
                      {p.area.replace('_', ' ')} - {p.tipo_prueba.replace('_', ' ')} ({formatearFecha(p.fecha)})
                    </MenuItem>
                  ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        {!puedenComparar && prueba1 && prueba2 && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            Las pruebas seleccionadas no tienen parámetros en común para comparar.
          </Alert>
        )}

        {puedenComparar && (
          <>
            {/* Tabla de comparación */}
            <TableContainer component={Paper} sx={{ mb: 3 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Parámetro</strong></TableCell>
                    <TableCell align="center">
                      <strong>Prueba 1</strong><br />
                      <Typography variant="caption" color="text.secondary">
                        {formatearFecha(prueba1.fecha)}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <strong>Prueba 2</strong><br />
                      <Typography variant="caption" color="text.secondary">
                        {formatearFecha(prueba2.fecha)}
                      </Typography>
                    </TableCell>
                    <TableCell align="center"><strong>Diferencia</strong></TableCell>
                    <TableCell align="center"><strong>Tendencia</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {parametrosComunes.map(param => {
                    const valor1 = obtenerValorParametro(prueba1, param);
                    const valor2 = obtenerValorParametro(prueba2, param);
                    
                    if (valor1 === null || valor2 === null) return null;
                    
                    const diferencia = calcularDiferencia(valor1, valor2);
                    const tendencia = obtenerTendencia(valor1, valor2);
                    const resultado1 = prueba1.resultados?.find(r => r.parametro === param);
                    const unidad = resultado1?.unidad || '';
                    
                    return (
                      <TableRow key={param}>
                        <TableCell>{param}</TableCell>
                        <TableCell align="center">
                          <strong>{valor1}</strong> {unidad}
                        </TableCell>
                        <TableCell align="center">
                          <strong>{valor2}</strong> {unidad}
                        </TableCell>
                        <TableCell align="center">
                          <Chip
                            label={`${diferencia > 0 ? '+' : ''}${diferencia.toFixed(1)}%`}
                            color={Math.abs(diferencia) > 10 ? 'warning' : 'default'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="center">
                          <Chip
                            icon={tendencia.icono}
                            label={tendencia.texto}
                            color={tendencia.color as any}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>

            {/* Gráfica de comparación */}
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Comparación Visual
              </Typography>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Parámetro a visualizar</InputLabel>
                <Select
                  value={parametroSeleccionado}
                  onChange={(e) => setParametroSeleccionado(e.target.value)}
                  label="Parámetro a visualizar"
                >
                  {parametrosComunes.map(param => (
                    <MenuItem key={param} value={param}>{param}</MenuItem>
                  ))}
                </Select>
              </FormControl>

              {parametroSeleccionado && (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart
                    data={[
                      {
                        fecha: formatearFecha(prueba2.fecha),
                        valor: obtenerValorParametro(prueba2, parametroSeleccionado)
                      },
                      {
                        fecha: formatearFecha(prueba1.fecha),
                        valor: obtenerValorParametro(prueba1, parametroSeleccionado)
                      }
                    ]}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="fecha" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="valor"
                      stroke="#8884d8"
                      strokeWidth={2}
                      dot={{ r: 6 }}
                      name={parametroSeleccionado}
                    />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </Paper>
          </>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Cerrar</Button>
      </DialogActions>
    </Dialog>
  );
};

export default ComparadorPruebas;
