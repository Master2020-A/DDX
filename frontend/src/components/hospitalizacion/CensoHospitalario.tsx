/**
 * Componente de Censo Hospitalario
 * Muestra estadísticas en tiempo real de ocupación hospitalaria
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import {
  People as PeopleIcon,
  Hotel as HotelIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { censoService } from '@/services/hospitalizacionService';
import type { CensoHospitalario } from '@/types/hospitalizacion';

interface Props {
  onActualizar?: () => void;
}

export default function CensoHospitalarioComponent({ onActualizar }: Props) {
  const [censo, setCenso] = useState<CensoHospitalario | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const cargarCenso = async () => {
    try {
      setCargando(true);
      setError(null);
      const data = await censoService.obtenerCenso();
      setCenso(data);
    } catch (err: any) {
      console.error('Error al cargar censo:', err);
      setError(err.response?.data?.detail || 'Error al cargar el censo hospitalario');
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarCenso();
    // Actualizar cada 5 minutos
    const interval = setInterval(cargarCenso, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (cargando) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!censo) {
    return <Alert severity="info">No hay datos disponibles</Alert>;
  }

  const getColorOcupacion = (porcentaje: number) => {
    if (porcentaje >= 90) return 'error';
    if (porcentaje >= 75) return 'warning';
    return 'success';
  };

  return (
    <Box>
      {/* Tarjetas de estadísticas */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Total Hospitalizados */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)', mb: 1 }}>
                    Pacientes Hospitalizados
                  </Typography>
                  <Typography variant="h3" sx={{ color: 'white', fontWeight: 600 }}>
                    {censo.total_hospitalizados}
                  </Typography>
                </Box>
                <PeopleIcon sx={{ fontSize: 48, color: 'rgba(255,255,255,0.3)' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Camas Disponibles */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)', mb: 1 }}>
                    Camas Disponibles
                  </Typography>
                  <Typography variant="h3" sx={{ color: 'white', fontWeight: 600 }}>
                    {censo.camas_disponibles}
                  </Typography>
                </Box>
                <CheckCircleIcon sx={{ fontSize: 48, color: 'rgba(255,255,255,0.3)' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Camas Ocupadas */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)', mb: 1 }}>
                    Camas Ocupadas
                  </Typography>
                  <Typography variant="h3" sx={{ color: 'white', fontWeight: 600 }}>
                    {censo.camas_ocupadas}
                  </Typography>
                </Box>
                <HotelIcon sx={{ fontSize: 48, color: 'rgba(255,255,255,0.3)' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Porcentaje de Ocupación */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box sx={{ width: '100%' }}>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)', mb: 1 }}>
                    Ocupación
                  </Typography>
                  <Typography variant="h3" sx={{ color: 'white', fontWeight: 600, mb: 1 }}>
                    {censo.porcentaje_ocupacion}%
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={censo.porcentaje_ocupacion}
                    color={getColorOcupacion(censo.porcentaje_ocupacion)}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Distribución por Área */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                📊 Distribución por Área
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell><strong>Área</strong></TableCell>
                      <TableCell align="right"><strong>Pacientes</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(censo.por_area).map(([area, cantidad]) => (
                      <TableRow key={area}>
                        <TableCell>{area || 'Sin asignar'}</TableCell>
                        <TableCell align="right">
                          <Chip label={cantidad} color="primary" size="small" />
                        </TableCell>
                      </TableRow>
                    ))}
                    {Object.keys(censo.por_area).length === 0 && (
                      <TableRow>
                        <TableCell colSpan={2} align="center">
                          <Typography variant="body2" color="text.secondary">
                            No hay pacientes hospitalizados
                          </Typography>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                📈 Distribución por Estado
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell><strong>Estado</strong></TableCell>
                      <TableCell align="right"><strong>Cantidad</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(censo.por_estado).map(([estado, cantidad]) => (
                      <TableRow key={estado}>
                        <TableCell sx={{ textTransform: 'capitalize' }}>{estado.replace('_', ' ')}</TableCell>
                        <TableCell align="right">
                          <Chip
                            label={cantidad}
                            color={estado === 'activo' ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Ingresos Recientes */}
      {censo.hospitalizaciones_recientes.length > 0 && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
              🕐 Ingresos Recientes
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Fecha Ingreso</strong></TableCell>
                    <TableCell><strong>Área</strong></TableCell>
                    <TableCell><strong>Cama</strong></TableCell>
                    <TableCell><strong>Diagnóstico</strong></TableCell>
                    <TableCell><strong>Prioridad</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {censo.hospitalizaciones_recientes.map((hosp) => (
                    <TableRow key={hosp.id}>
                      <TableCell>
                        {new Date(hosp.fecha_ingreso).toLocaleString('es-MX', {
                          day: '2-digit',
                          month: '2-digit',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </TableCell>
                      <TableCell>{hosp.area_hospitalizacion || 'N/A'}</TableCell>
                      <TableCell>{hosp.numero_cama || 'Sin asignar'}</TableCell>
                      <TableCell>
                        <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                          {hosp.diagnostico_ingreso}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={hosp.prioridad}
                          color={
                            hosp.prioridad === 'urgente' ? 'error' :
                            hosp.prioridad === 'alta' ? 'warning' : 'default'
                          }
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}
