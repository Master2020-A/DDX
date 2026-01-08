/**
 * Gráfica de tendencias de parámetros de laboratorio
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  MenuItem,
  Grid,
  Alert,
  CircularProgress
} from '@mui/material';
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
import {
  PruebaLaboratorioResumen,
  PruebaLaboratorio,
  PARAMETROS_LABELS,
  TIPOS_PRUEBAS
} from '@/types/laboratorio';
import laboratorioService from '@/services/laboratorioService';

interface GraficaTendenciasProps {
  pacienteId: string;
  pruebas: PruebaLaboratorioResumen[];
}

const GraficaTendencias: React.FC<GraficaTendenciasProps> = ({
  pacienteId,
  pruebas
}) => {
  const [parametroSeleccionado, setParametroSeleccionado] = useState('');
  const [datosGrafica, setDatosGrafica] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [rangoMin, setRangoMin] = useState<number | null>(null);
  const [rangoMax, setRangoMax] = useState<number | null>(null);
  const [parametrosDisponibles, setParametrosDisponibles] = useState<string[]>([]);

  useEffect(() => {
    // Obtener parámetros únicos de todas las pruebas
    const parametros = new Set<string>();
    
    // Extraer parámetros de los tipos de pruebas disponibles
    Object.values(TIPOS_PRUEBAS).forEach(tipos => {
      tipos.forEach(tipo => {
        tipo.parametros.forEach(param => parametros.add(param));
      });
    });

    setParametrosDisponibles(Array.from(parametros).sort());
  }, []);

  useEffect(() => {
    if (parametroSeleccionado) {
      cargarDatosTendencia();
    }
  }, [parametroSeleccionado, pruebas]);

  const cargarDatosTendencia = async () => {
    if (!parametroSeleccionado) return;

    setLoading(true);
    try {
      // Cargar detalles de todas las pruebas
      const pruebasDetalladas = await Promise.all(
        pruebas.map(p => laboratorioService.obtenerPrueba(p.id))
      );

      // Filtrar pruebas que tengan el parámetro seleccionado
      const pruebasFiltradas = pruebasDetalladas.filter(
        p => p.resultados[parametroSeleccionado] !== undefined
      );

      // Ordenar por fecha
      pruebasFiltradas.sort(
        (a, b) =>
          new Date(a.fecha_resultado || a.created_at).getTime() -
          new Date(b.fecha_resultado || b.created_at).getTime()
      );

      // Preparar datos para la gráfica
      const datos = pruebasFiltradas.map(prueba => {
        const fecha = new Date(prueba.fecha_resultado || prueba.created_at);
        const valorAnormal = prueba.valores_anormales.find(
          v => v.parametro === parametroSeleccionado
        );

        return {
          fecha: fecha.toLocaleDateString('es-MX', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
          }),
          valor: prueba.resultados[parametroSeleccionado],
          estado: valorAnormal ? valorAnormal.estado : 'normal',
          fechaCompleta: fecha.toLocaleString('es-MX')
        };
      });

      setDatosGrafica(datos);

      // Obtener rangos de referencia
      if (pruebasFiltradas.length > 0) {
        const valorAnormal = pruebasFiltradas[0].valores_anormales.find(
          v => v.parametro === parametroSeleccionado
        );
        if (valorAnormal) {
          setRangoMin(valorAnormal.rango_min);
          setRangoMax(valorAnormal.rango_max);
        } else {
          // Buscar en todos los valores para obtener rangos
          for (const prueba of pruebasFiltradas) {
            const valor = [...prueba.valores_anormales, ...prueba.valores_criticos].find(
              v => v.parametro === parametroSeleccionado
            );
            if (valor && valor.rango_min !== null && valor.rango_max !== null) {
              setRangoMin(valor.rango_min);
              setRangoMax(valor.rango_max);
              break;
            }
          }
        }
      }
    } catch (err) {
      console.error('Error cargando tendencias:', err);
    } finally {
      setLoading(false);
    }
  };

  const obtenerColorPunto = (estado: string) => {
    switch (estado) {
      case 'critico_bajo':
      case 'critico_alto':
        return '#d32f2f';
      case 'bajo':
      case 'alto':
        return '#ed6c02';
      default:
        return '#2e7d32';
    }
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <Paper sx={{ p: 2 }}>
          <Typography variant="body2">
            <strong>Fecha:</strong> {data.fechaCompleta}
          </Typography>
          <Typography variant="body2">
            <strong>Valor:</strong> {data.valor}
          </Typography>
          <Typography variant="body2" color={obtenerColorPunto(data.estado)}>
            <strong>Estado:</strong> {data.estado === 'normal' ? 'Normal' : data.estado.toUpperCase()}
          </Typography>
        </Paper>
      );
    }
    return null;
  };

  if (parametrosDisponibles.length === 0) {
    return (
      <Alert severity="info">
        No hay parámetros disponibles para mostrar tendencias.
      </Alert>
    );
  }

  return (
    <Box>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom color="primary">
          📈 Tendencias de Parámetros
        </Typography>

        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} md={6}>
            <TextField
              select
              fullWidth
              label="Seleccionar Parámetro"
              value={parametroSeleccionado}
              onChange={(e) => setParametroSeleccionado(e.target.value)}
            >
              {parametrosDisponibles.map(param => (
                <MenuItem key={param} value={param}>
                  {PARAMETROS_LABELS[param] || param}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
        </Grid>

        {loading ? (
          <Box display="flex" justifyContent="center" p={4}>
            <CircularProgress />
          </Box>
        ) : datosGrafica.length === 0 ? (
          <Alert severity="info">
            {parametroSeleccionado
              ? 'No hay datos disponibles para este parámetro.'
              : 'Selecciona un parámetro para ver su tendencia.'}
          </Alert>
        ) : (
          <>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Mostrando {datosGrafica.length} mediciones de{' '}
                <strong>{PARAMETROS_LABELS[parametroSeleccionado] || parametroSeleccionado}</strong>
              </Typography>
              {rangoMin !== null && rangoMax !== null && (
                <Typography variant="body2" color="text.secondary">
                  Rango de referencia: {rangoMin} - {rangoMax}
                </Typography>
              )}
            </Box>

            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={datosGrafica}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="fecha"
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis />
                <Tooltip content={<CustomTooltip />} />
                <Legend />

                {/* Líneas de referencia */}
                {rangoMin !== null && (
                  <ReferenceLine
                    y={rangoMin}
                    stroke="#2196f3"
                    strokeDasharray="3 3"
                    label="Mín"
                  />
                )}
                {rangoMax !== null && (
                  <ReferenceLine
                    y={rangoMax}
                    stroke="#2196f3"
                    strokeDasharray="3 3"
                    label="Máx"
                  />
                )}

                <Line
                  type="monotone"
                  dataKey="valor"
                  stroke="#1976d2"
                  strokeWidth={2}
                  dot={(props: any) => {
                    const { cx, cy, payload } = props;
                    return (
                      <circle
                        cx={cx}
                        cy={cy}
                        r={6}
                        fill={obtenerColorPunto(payload.estado)}
                        stroke="#fff"
                        strokeWidth={2}
                      />
                    );
                  }}
                  activeDot={{ r: 8 }}
                />
              </LineChart>
            </ResponsiveContainer>

            {/* Leyenda de colores */}
            <Box display="flex" gap={3} justifyContent="center" mt={2}>
              <Box display="flex" alignItems="center" gap={1}>
                <Box
                  sx={{
                    width: 16,
                    height: 16,
                    borderRadius: '50%',
                    bgcolor: '#2e7d32'
                  }}
                />
                <Typography variant="body2">Normal</Typography>
              </Box>
              <Box display="flex" alignItems="center" gap={1}>
                <Box
                  sx={{
                    width: 16,
                    height: 16,
                    borderRadius: '50%',
                    bgcolor: '#ed6c02'
                  }}
                />
                <Typography variant="body2">Anormal</Typography>
              </Box>
              <Box display="flex" alignItems="center" gap={1}>
                <Box
                  sx={{
                    width: 16,
                    height: 16,
                    borderRadius: '50%',
                    bgcolor: '#d32f2f'
                  }}
                />
                <Typography variant="body2">Crítico</Typography>
              </Box>
            </Box>
          </>
        )}
      </Paper>
    </Box>
  );
};

export default GraficaTendencias;
