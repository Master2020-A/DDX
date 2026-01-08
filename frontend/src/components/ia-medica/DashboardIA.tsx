import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Divider,
  Alert,
} from '@mui/material';
import {
  Assessment as AssessmentIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  Refresh as RefreshIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { DashboardIAResponse } from '../../services/iaMedicaService';

interface DashboardIAProps {
  dashboard: DashboardIAResponse;
  onRecargar: () => void;
}

const DashboardIA: React.FC<DashboardIAProps> = ({ dashboard, onRecargar }) => {
  const { estadisticas, analisis_recientes, alertas_criticas, recomendaciones_pendientes } = dashboard;

  const getSeveridadColor = (severidad?: string) => {
    switch (severidad?.toLowerCase()) {
      case 'critica':
        return 'error';
      case 'severa':
      case 'alta':
        return 'error';
      case 'moderada':
      case 'media':
        return 'warning';
      case 'leve':
      case 'baja':
        return 'info';
      default:
        return 'default';
    }
  };

  const getSeveridadIcon = (severidad?: string) => {
    switch (severidad?.toLowerCase()) {
      case 'critica':
      case 'severa':
        return <ErrorIcon color="error" />;
      case 'moderada':
        return <WarningIcon color="warning" />;
      default:
        return <InfoIcon color="info" />;
    }
  };

  return (
    <Box>
      {/* Header con botón de recarga */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight="600">
          Dashboard de Inteligencia Artificial
        </Typography>
        <IconButton onClick={onRecargar} color="primary">
          <RefreshIcon />
        </IconButton>
      </Box>

      {/* Tarjetas de Estadísticas */}
      <Grid container spacing={3} mb={4}>
        {/* Total de Análisis */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="white" fontWeight="bold">
                    {estadisticas.total_analisis}
                  </Typography>
                  <Typography variant="body2" color="rgba(255,255,255,0.8)">
                    Análisis Totales
                  </Typography>
                </Box>
                <AssessmentIcon sx={{ fontSize: 48, color: 'rgba(255,255,255,0.3)' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Predicciones Activas */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="white" fontWeight="bold">
                    {estadisticas.predicciones_riesgo_activas}
                  </Typography>
                  <Typography variant="body2" color="rgba(255,255,255,0.8)">
                    Predicciones Activas
                  </Typography>
                </Box>
                <TrendingUpIcon sx={{ fontSize: 48, color: 'rgba(255,255,255,0.3)' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Anomalías Pendientes */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="white" fontWeight="bold">
                    {estadisticas.anomalias_pendientes_revision}
                  </Typography>
                  <Typography variant="body2" color="rgba(255,255,255,0.8)">
                    Anomalías Pendientes
                  </Typography>
                </Box>
                <WarningIcon sx={{ fontSize: 48, color: 'rgba(255,255,255,0.3)' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Interacciones Críticas */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%)' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="white" fontWeight="bold">
                    {estadisticas.interacciones_criticas}
                  </Typography>
                  <Typography variant="body2" color="rgba(255,255,255,0.8)">
                    Interacciones Críticas
                  </Typography>
                </Box>
                <ErrorIcon sx={{ fontSize: 48, color: 'rgba(255,255,255,0.3)' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Métricas de Rendimiento */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight="600">
                <SpeedIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Rendimiento del Sistema
              </Typography>
              <Box mt={2}>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">Tiempo Promedio de Respuesta</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {estadisticas.tiempo_promedio_respuesta.toFixed(1)}s
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={Math.min((estadisticas.tiempo_promedio_respuesta / 5) * 100, 100)}
                  sx={{ height: 8, borderRadius: 4 }}
                />

                <Box display="flex" justifyContent="space-between" mt={3} mb={1}>
                  <Typography variant="body2">Tasa de Validación por Médico</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {(estadisticas.tasa_validacion_medico * 100).toFixed(0)}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={estadisticas.tasa_validacion_medico * 100}
                  color="success"
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight="600">
                <AssessmentIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Uso del Asistente de IA
              </Typography>
              <Box mt={2}>
                <Box display="flex" justifyContent="space-between" mb={2}>
                  <Typography variant="body2">Consultas Hoy</Typography>
                  <Chip
                    label={estadisticas.consultas_asistente_hoy}
                    color="primary"
                    size="small"
                  />
                </Box>
                <Box display="flex" justifyContent="space-between" mb={2}>
                  <Typography variant="body2">Consultas Este Mes</Typography>
                  <Chip
                    label={estadisticas.consultas_asistente_mes}
                    color="secondary"
                    size="small"
                  />
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Recomendaciones Pendientes</Typography>
                  <Chip
                    label={recomendaciones_pendientes}
                    color="warning"
                    size="small"
                  />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Alertas Críticas */}
      {alertas_criticas.length > 0 && (
        <Card sx={{ mb: 4, borderLeft: 4, borderColor: 'error.main' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom fontWeight="600" color="error">
              <ErrorIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Alertas Críticas ({alertas_criticas.length})
            </Typography>
            <List>
              {alertas_criticas.map((alerta, index) => (
                <React.Fragment key={alerta.id || index}>
                  <ListItem>
                    <ListItemIcon>
                      <ErrorIcon color="error" />
                    </ListItemIcon>
                    <ListItemText
                      primary={alerta.descripcion}
                      secondary={`Tipo: ${alerta.tipo} - ${new Date(alerta.created_at).toLocaleString()}`}
                    />
                  </ListItem>
                  {index < alertas_criticas.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {/* Análisis Recientes */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom fontWeight="600">
            <AssessmentIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Análisis Recientes
          </Typography>
          {analisis_recientes.length === 0 ? (
            <Alert severity="info" sx={{ mt: 2 }}>
              No hay análisis recientes
            </Alert>
          ) : (
            <List>
              {analisis_recientes.map((analisis, index) => (
                <React.Fragment key={analisis.id}>
                  <ListItem>
                    <ListItemIcon>
                      {getSeveridadIcon(analisis.severidad)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="body1">
                            {analisis.resultado_resumen}
                          </Typography>
                          {analisis.severidad && (
                            <Chip
                              label={analisis.severidad}
                              size="small"
                              color={getSeveridadColor(analisis.severidad) as any}
                            />
                          )}
                        </Box>
                      }
                      secondary={
                        <>
                          <Typography variant="caption" component="span" display="block">
                            Paciente: {analisis.paciente_nombre} | Tipo: {analisis.tipo}
                          </Typography>
                          <Typography variant="caption" component="span" color="text.secondary">
                            {new Date(analisis.created_at).toLocaleString()}
                          </Typography>
                        </>
                      }
                    />
                  </ListItem>
                  {index < analisis_recientes.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      {/* Análisis por Tipo */}
      {Object.keys(estadisticas.analisis_por_tipo).length > 0 && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom fontWeight="600">
              Análisis por Tipo
            </Typography>
            <Grid container spacing={2} mt={1}>
              {Object.entries(estadisticas.analisis_por_tipo).map(([tipo, cantidad]) => (
                <Grid item xs={12} sm={6} md={4} key={tipo}>
                  <Box
                    sx={{
                      p: 2,
                      border: 1,
                      borderColor: 'divider',
                      borderRadius: 2,
                      textAlign: 'center',
                    }}
                  >
                    <Typography variant="h4" color="primary" fontWeight="bold">
                      {cantidad}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" textTransform="capitalize">
                      {tipo}
                    </Typography>
                  </Box>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default DashboardIA;
