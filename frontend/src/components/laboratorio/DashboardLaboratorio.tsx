/**
 * Dashboard de laboratorios por paciente
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Divider,
  Button
} from '@mui/material';
import {
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Visibility as VisibilityIcon,
  TrendingUp as TrendingUpIcon,
  Science as ScienceIcon,
  CalendarToday as CalendarIcon,
  CompareArrows as CompareIcon
} from '@mui/icons-material';
import { PruebaLaboratorioResumen } from '@/types/laboratorio';
import laboratorioService from '@/services/laboratorioService';
import DetallePruebaLaboratorio from '@/components/laboratorio/DetallePruebaLaboratorio';
import GraficaTendencias from '@/components/laboratorio/GraficaTendencias';
import NotificacionesLaboratorio from '@/components/laboratorio/NotificacionesLaboratorio';
import ComparadorPruebas from '@/components/laboratorio/ComparadorPruebas';

interface DashboardLaboratorioProps {
  pacienteId: string;
}

const DashboardLaboratorio: React.FC<DashboardLaboratorioProps> = ({ pacienteId }) => {
  const [pruebas, setPruebas] = useState<PruebaLaboratorioResumen[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tabActual, setTabActual] = useState(0);
  const [pruebaSeleccionada, setPruebaSeleccionada] = useState<string | null>(null);
  const [areaFiltro, setAreaFiltro] = useState<string | null>(null);
  const [comparadorAbierto, setComparadorAbierto] = useState(false);

  useEffect(() => {
    cargarPruebas();
  }, [pacienteId, areaFiltro]);

  const cargarPruebas = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await laboratorioService.listarPruebasPaciente(
        pacienteId,
        areaFiltro || undefined
      );
      setPruebas(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar pruebas de laboratorio');
    } finally {
      setLoading(false);
    }
  };

  const handleVerDetalle = (pruebaId: string, event?: React.MouseEvent) => {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    setPruebaSeleccionada(pruebaId);
    setTabActual(1);
  };

  const handleCerrarDetalle = () => {
    setPruebaSeleccionada(null);
    setTabActual(0);
  };

  // Estadísticas
  const totalPruebas = pruebas.length;
  const pruebasConAtencion = pruebas.filter(p => p.requiere_atencion).length;
  const pruebasConCriticos = pruebas.filter(p => p.valores_criticos_count > 0).length;
  const pruebasNormales = pruebas.filter(
    p => !p.requiere_atencion && p.valores_anormales_count === 0
  ).length;

  // Agrupar por área
  const pruebasPorArea = pruebas.reduce((acc, prueba) => {
    if (!acc[prueba.area]) {
      acc[prueba.area] = [];
    }
    acc[prueba.area].push(prueba);
    return acc;
  }, {} as Record<string, PruebaLaboratorioResumen[]>);

  const obtenerColorEstado = (prueba: PruebaLaboratorioResumen) => {
    if (prueba.valores_criticos_count > 0) return 'error';
    if (prueba.requiere_atencion) return 'warning';
    if (prueba.valores_anormales_count > 0) return 'info';
    return 'success';
  };

  const obtenerIconoEstado = (prueba: PruebaLaboratorioResumen) => {
    if (prueba.valores_criticos_count > 0) return <ErrorIcon />;
    if (prueba.requiere_atencion) return <WarningIcon />;
    return <CheckCircleIcon />;
  };

  const formatearFecha = (fecha?: string) => {
    if (!fecha) return 'Pendiente';
    return new Date(fecha).toLocaleDateString('es-MX', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header con estadísticas */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
          <Box display="flex" alignItems="center">
            <ScienceIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
            <Typography variant="h5" fontWeight="bold">
              Laboratorios Clínicos
            </Typography>
          </Box>
          <Box display="flex" gap={1} alignItems="center">
            <NotificacionesLaboratorio pacienteId={pacienteId} />
            <Button
              variant="outlined"
              startIcon={<CompareIcon />}
              onClick={() => setComparadorAbierto(true)}
              disabled={pruebas.length < 2}
            >
              Comparar Pruebas
            </Button>
          </Box>
        </Box>

        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'primary.light', color: 'white' }}>
              <CardContent>
                <Typography variant="h4" fontWeight="bold">
                  {totalPruebas}
                </Typography>
                <Typography variant="body2">Total de Pruebas</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'success.light', color: 'white' }}>
              <CardContent>
                <Typography variant="h4" fontWeight="bold">
                  {pruebasNormales}
                </Typography>
                <Typography variant="body2">Resultados Normales</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'warning.light', color: 'white' }}>
              <CardContent>
                <Typography variant="h4" fontWeight="bold">
                  {pruebasConAtencion}
                </Typography>
                <Typography variant="body2">Requieren Atención</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'error.light', color: 'white' }}>
              <CardContent>
                <Typography variant="h4" fontWeight="bold">
                  {pruebasConCriticos}
                </Typography>
                <Typography variant="body2">Valores Críticos</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>

      {/* Tabs */}
      <Paper elevation={3}>
        <Tabs
          value={tabActual}
          onChange={(_, newValue) => setTabActual(newValue)}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="📋 Historial" />
          <Tab label="📊 Detalle" disabled={!pruebaSeleccionada} />
          <Tab label="📈 Tendencias" />
        </Tabs>

        {/* Tab: Historial */}
        {tabActual === 0 && (
          <Box p={3}>
            {totalPruebas === 0 ? (
              <Alert severity="info">
                No hay pruebas de laboratorio registradas para este paciente.
              </Alert>
            ) : (
              <Grid container spacing={2}>
                {pruebas.map((prueba) => (
                  <Grid item xs={12} key={prueba.id}>
                    <Card
                      sx={{
                        border: 2,
                        borderColor: `${obtenerColorEstado(prueba)}.main`,
                        cursor: 'default',
                        '&:hover': {
                          boxShadow: 6,
                          transform: 'translateY(-2px)',
                          transition: 'all 0.3s'
                        }
                      }}
                      component="div"
                    >
                      <CardContent>
                        <Grid container spacing={2} alignItems="center">
                          <Grid item xs={12} md={1}>
                            <Box
                              display="flex"
                              justifyContent="center"
                              color={`${obtenerColorEstado(prueba)}.main`}
                            >
                              {obtenerIconoEstado(prueba)}
                            </Box>
                          </Grid>

                          <Grid item xs={12} md={3}>
                            <Typography variant="h6" fontWeight="bold">
                              {prueba.tipo_prueba.replace(/_/g, ' ').toUpperCase()}
                            </Typography>
                            <Chip
                              label={prueba.area}
                              size="small"
                              color="primary"
                              variant="outlined"
                            />
                          </Grid>

                          <Grid item xs={12} md={2}>
                            <Box display="flex" alignItems="center" gap={1}>
                              <CalendarIcon fontSize="small" color="action" />
                              <Typography variant="body2" color="text.secondary">
                                {formatearFecha(prueba.fecha_resultado)}
                              </Typography>
                            </Box>
                          </Grid>

                          <Grid item xs={12} md={4}>
                            <Box display="flex" gap={1} flexWrap="wrap">
                              {prueba.valores_criticos_count > 0 && (
                                <Chip
                                  icon={<ErrorIcon />}
                                  label={`${prueba.valores_criticos_count} Críticos`}
                                  color="error"
                                  size="small"
                                />
                              )}
                              {prueba.valores_anormales_count > 0 && (
                                <Chip
                                  icon={<WarningIcon />}
                                  label={`${prueba.valores_anormales_count} Anormales`}
                                  color="warning"
                                  size="small"
                                />
                              )}
                              {prueba.valores_anormales_count === 0 &&
                                prueba.valores_criticos_count === 0 && (
                                  <Chip
                                    icon={<CheckCircleIcon />}
                                    label="Normal"
                                    color="success"
                                    size="small"
                                  />
                                )}
                            </Box>
                            {prueba.laboratorio_externo && (
                              <Typography variant="caption" color="text.secondary">
                                Lab: {prueba.laboratorio_externo}
                              </Typography>
                            )}
                          </Grid>

                          <Grid item xs={12} md={2}>
                            <Box display="flex" justifyContent="flex-end">
                              <Tooltip title="Ver Detalle">
                                <span>
                                  <IconButton
                                    color="primary"
                                    onClick={(e) => {
                                      e.preventDefault();
                                      e.stopPropagation();
                                      handleVerDetalle(prueba.id, e);
                                    }}
                                    component="button"
                                    type="button"
                                  >
                                    <VisibilityIcon />
                                  </IconButton>
                                </span>
                              </Tooltip>
                            </Box>
                          </Grid>
                        </Grid>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            )}
          </Box>
        )}

        {/* Tab: Detalle */}
        {tabActual === 1 && pruebaSeleccionada && (
          <Box p={3}>
            <Button onClick={handleCerrarDetalle} sx={{ mb: 2 }}>
              ← Volver al Historial
            </Button>
            <DetallePruebaLaboratorio
              pruebaId={pruebaSeleccionada}
              onClose={handleCerrarDetalle}
            />
          </Box>
        )}

        {/* Tab: Tendencias */}
        {tabActual === 2 && (
          <Box p={3}>
            <GraficaTendencias pacienteId={pacienteId} pruebas={pruebas} />
          </Box>
        )}
      </Paper>

      {/* Diálogo de Comparador */}
      <ComparadorPruebas
        open={comparadorAbierto}
        onClose={() => setComparadorAbierto(false)}
        pacienteId={pacienteId}
        pruebaActualId={pruebaSeleccionada || undefined}
      />
    </Box>
  );
};

export default DashboardLaboratorio;
