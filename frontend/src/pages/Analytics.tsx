import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Typography,
  Button,
  ButtonGroup,
  Paper,
  Alert,
  CircularProgress,
  IconButton,
  Menu,
  MenuItem,
  TextField,
} from '@mui/material';
import {
  People,
  LocalHospital,
  Assignment,
  Hotel,
  FileDownload,
  Refresh,
  DateRange,
} from '@mui/icons-material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';
import StatCard from '../components/analytics/StatCard';
import ChartCard from '../components/analytics/ChartCard';
import analyticsService, { DashboardData } from '../services/analyticsService';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const Analytics: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [periodo, setPeriodo] = useState<'7d' | '30d' | '90d' | 'custom'>('30d');
  const [fechaInicio] = useState<string>('');
  const [fechaFin] = useState<string>('');
  const [exportAnchor, setExportAnchor] = useState<null | HTMLElement>(null);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    loadDashboard();
  }, [periodo, fechaInicio, fechaFin]);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);

      let inicio: string | undefined;
      let fin: string | undefined;

      if (periodo === 'custom') {
        inicio = fechaInicio;
        fin = fechaFin;
      } else {
        const hoy = new Date();
        fin = hoy.toISOString().split('T')[0];
        
        const dias = periodo === '7d' ? 7 : periodo === '30d' ? 30 : 90;
        const inicioDate = new Date(hoy);
        inicioDate.setDate(inicioDate.getDate() - dias);
        inicio = inicioDate.toISOString().split('T')[0];
      }

      const data = await analyticsService.getDashboard(inicio, fin);
      setDashboardData(data);
    } catch (err: any) {
      console.error('Error al cargar dashboard:', err);
      setError(err.response?.data?.detail || 'Error al cargar los datos del dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (formato: 'csv' | 'excel' | 'pdf') => {
    try {
      setExporting(true);
      setExportAnchor(null);

      let inicio: string | undefined;
      let fin: string | undefined;

      if (periodo === 'custom') {
        inicio = fechaInicio;
        fin = fechaFin;
      } else {
        const hoy = new Date();
        fin = hoy.toISOString().split('T')[0];
        
        const dias = periodo === '7d' ? 7 : periodo === '30d' ? 30 : 90;
        const inicioDate = new Date(hoy);
        inicioDate.setDate(inicioDate.getDate() - dias);
        inicio = inicioDate.toISOString().split('T')[0];
      }

      let blob: Blob;
      let filename: string;

      switch (formato) {
        case 'csv':
          blob = await analyticsService.exportarCSV(inicio, fin);
          filename = `reporte_analytics_${inicio}_${fin}.csv`;
          break;
        case 'excel':
          blob = await analyticsService.exportarExcel(inicio, fin, true);
          filename = `reporte_analytics_${inicio}_${fin}.xlsx`;
          break;
        case 'pdf':
          blob = await analyticsService.exportarPDF(inicio, fin, 'portrait');
          filename = `reporte_analytics_${inicio}_${fin}.pdf`;
          break;
      }

      analyticsService.downloadFile(blob, filename);
    } catch (err: any) {
      console.error('Error al exportar:', err);
      setError(err.response?.data?.detail || 'Error al exportar el reporte');
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Box>
    );
  }

  if (!dashboardData) {
    return null;
  }

  const { estadisticas_generales, estadisticas_consultas, indicadores_calidad, tiempos_atencion, estadisticas_diagnosticos, estadisticas_hospitalizacion } = dashboardData;

  // Datos para gráfico de consultas por mes
  const consultasPorMesData = {
    labels: estadisticas_consultas.por_mes.map(m => m.mes),
    datasets: [
      {
        label: 'Consultas',
        data: estadisticas_consultas.por_mes.map(m => m.count),
        borderColor: '#1976d2',
        backgroundColor: 'rgba(25, 118, 210, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  // Datos para gráfico de consultas por tipo
  const consultasPorTipoData = {
    labels: Object.keys(estadisticas_consultas.por_tipo).map(t => t.replace('_', ' ').toUpperCase()),
    datasets: [
      {
        label: 'Consultas',
        data: Object.values(estadisticas_consultas.por_tipo),
        backgroundColor: [
          'rgba(25, 118, 210, 0.8)',
          'rgba(76, 175, 80, 0.8)',
          'rgba(255, 152, 0, 0.8)',
          'rgba(244, 67, 54, 0.8)',
        ],
      },
    ],
  };

  // Datos para gráfico de diagnósticos por categoría
  const diagnosticosCategoriaData = {
    labels: Object.keys(estadisticas_diagnosticos.por_categoria_cie10),
    datasets: [
      {
        data: Object.values(estadisticas_diagnosticos.por_categoria_cie10),
        backgroundColor: [
          '#1976d2',
          '#4caf50',
          '#ff9800',
          '#f44336',
          '#9c27b0',
          '#00bcd4',
          '#ffeb3b',
          '#795548',
        ],
      },
    ],
  };

  // Datos para gráfico de tiempos por hora
  const tiemposPorHoraData = {
    labels: tiempos_atencion.distribucion_horaria.map(h => h.hora),
    datasets: [
      {
        label: 'Consultas',
        data: tiempos_atencion.distribucion_horaria.map(h => h.consultas),
        backgroundColor: 'rgba(25, 118, 210, 0.8)',
        yAxisID: 'y',
      },
      {
        label: 'Tiempo Promedio (min)',
        data: tiempos_atencion.distribucion_horaria.map(h => h.tiempo_promedio),
        backgroundColor: 'rgba(76, 175, 80, 0.8)',
        yAxisID: 'y1',
      },
    ],
  };

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          📊 Reportes y Analytics
        </Typography>
        <Box display="flex" gap={2}>
          <ButtonGroup variant="outlined" size="small">
            <Button
              variant={periodo === '7d' ? 'contained' : 'outlined'}
              onClick={() => setPeriodo('7d')}
            >
              7 días
            </Button>
            <Button
              variant={periodo === '30d' ? 'contained' : 'outlined'}
              onClick={() => setPeriodo('30d')}
            >
              30 días
            </Button>
            <Button
              variant={periodo === '90d' ? 'contained' : 'outlined'}
              onClick={() => setPeriodo('90d')}
            >
              90 días
            </Button>
          </ButtonGroup>
          <IconButton onClick={loadDashboard} color="primary">
            <Refresh />
          </IconButton>
          <Button
            variant="contained"
            startIcon={exporting ? <CircularProgress size={20} /> : <FileDownload />}
            onClick={(e) => setExportAnchor(e.currentTarget)}
            disabled={exporting}
          >
            Exportar
          </Button>
          <Menu
            anchorEl={exportAnchor}
            open={Boolean(exportAnchor)}
            onClose={() => setExportAnchor(null)}
          >
            <MenuItem onClick={() => handleExport('csv')}>Exportar CSV</MenuItem>
            <MenuItem onClick={() => handleExport('excel')}>Exportar Excel</MenuItem>
            <MenuItem onClick={() => handleExport('pdf')}>Exportar PDF</MenuItem>
          </Menu>
        </Box>
      </Box>

      {/* Estadísticas Generales */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Consultas"
            value={estadisticas_generales.total_consultas}
            subtitle={`${estadisticas_generales.consultas_hoy} hoy`}
            icon={<Assignment />}
            color="#1976d2"
            trend={estadisticas_consultas.tendencia === 'ascendente' ? 'up' : estadisticas_consultas.tendencia === 'descendente' ? 'down' : 'flat'}
            trendValue={estadisticas_consultas.tendencia}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Pacientes"
            value={estadisticas_generales.total_pacientes}
            subtitle={`${estadisticas_generales.pacientes_nuevos_mes} nuevos este mes`}
            icon={<People />}
            color="#4caf50"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Diagnósticos"
            value={estadisticas_generales.total_diagnosticos}
            subtitle={`${indicadores_calidad.diagnosticos_confirmados.toFixed(1)}% confirmados`}
            icon={<LocalHospital />}
            color="#ff9800"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Hospitalizaciones"
            value={estadisticas_generales.total_hospitalizaciones}
            subtitle={`${estadisticas_hospitalizacion.ocupacion_actual.toFixed(1)}% ocupación`}
            icon={<Hotel />}
            color="#f44336"
          />
        </Grid>
      </Grid>

      {/* Gráficos de Consultas */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={8}>
          <ChartCard title="Tendencia de Consultas" subtitle="Consultas por mes">
            <Line
              data={consultasPorMesData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    display: false,
                  },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                  },
                },
              }}
            />
          </ChartCard>
        </Grid>
        <Grid item xs={12} md={4}>
          <ChartCard title="Consultas por Tipo" subtitle="Distribución">
            <Doughnut
              data={consultasPorTipoData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'bottom',
                  },
                },
              }}
            />
          </ChartCard>
        </Grid>
      </Grid>

      {/* Indicadores de Calidad */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Indicadores de Calidad
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Box textAlign="center">
              <Typography variant="h4" color="primary">
                {indicadores_calidad.tiempo_promedio_atencion.toFixed(1)}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Min. Atención Promedio
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Box textAlign="center">
              <Typography variant="h4" color="success.main">
                {indicadores_calidad.adherencia_protocolos.toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Adherencia Protocolos
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Box textAlign="center">
              <Typography variant="h4" color="warning.main">
                {indicadores_calidad.tasa_reingreso.toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Tasa de Reingreso
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Box textAlign="center">
              <Typography variant="h4" color="error.main">
                {indicadores_calidad.tasa_complicaciones.toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Tasa de Complicaciones
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Gráficos de Diagnósticos y Tiempos */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={6}>
          <ChartCard title="Diagnósticos por Categoría CIE-10" subtitle="Distribución">
            <Pie
              data={diagnosticosCategoriaData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'right',
                  },
                },
              }}
            />
          </ChartCard>
        </Grid>
        <Grid item xs={12} md={6}>
          <ChartCard title="Distribución Horaria" subtitle="Consultas y tiempos por hora">
            <Bar
              data={tiemposPorHoraData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                  y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                      display: true,
                      text: 'Consultas',
                    },
                  },
                  y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                      display: true,
                      text: 'Tiempo (min)',
                    },
                    grid: {
                      drawOnChartArea: false,
                    },
                  },
                },
              }}
            />
          </ChartCard>
        </Grid>
      </Grid>

      {/* Top Diagnósticos */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Top 10 Diagnósticos
        </Typography>
        <Grid container spacing={2}>
          {estadisticas_diagnosticos.top_diagnosticos.slice(0, 10).map((diag, index) => (
            <Grid item xs={12} sm={6} key={index}>
              <Box display="flex" justifyContent="space-between" alignItems="center" p={1}>
                <Box flex={1}>
                  <Typography variant="body1" fontWeight="bold">
                    {diag.codigo_cie10}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {diag.descripcion}
                  </Typography>
                </Box>
                <Typography variant="h6" color="primary">
                  {diag.count}
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
      </Paper>
    </Box>
  );
};

export default Analytics;
