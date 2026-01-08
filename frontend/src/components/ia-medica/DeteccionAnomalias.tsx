import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Chip,
  Grid,
  Paper,
  IconButton,
  Collapse,
} from '@mui/material';
import {
  BugReport as BugReportIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import iaMedicaService, { AnomaliaDetectadaResponse } from '../../services/iaMedicaService';

interface DeteccionAnomaliasProps {
  onActualizarDashboard?: () => void;
}

const DeteccionAnomalias: React.FC<DeteccionAnomaliasProps> = ({ onActualizarDashboard }) => {
  const [anomalias, setAnomalias] = useState<AnomaliaDetectadaResponse[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandidos, setExpandidos] = useState<{ [key: string]: boolean }>({});

  useEffect(() => {
    cargarAnomalias();
  }, []);

  const cargarAnomalias = async () => {
    try {
      setCargando(true);
      setError(null);
      const data = await iaMedicaService.obtenerAnomaliasPendientes();
      setAnomalias(data);
      
      if (onActualizarDashboard) {
        onActualizarDashboard();
      }
    } catch (err: any) {
      console.error('Error al cargar anomalías:', err);
      setError(err.response?.data?.detail || 'Error al cargar anomalías');
    } finally {
      setCargando(false);
    }
  };

  const toggleExpanded = (id: string) => {
    setExpandidos({
      ...expandidos,
      [id]: !expandidos[id],
    });
  };

  const getSeveridadColor = (severidad: string) => {
    switch (severidad.toLowerCase()) {
      case 'critica':
        return 'error';
      case 'severa':
        return 'error';
      case 'moderada':
        return 'warning';
      case 'leve':
        return 'info';
      default:
        return 'default';
    }
  };

  const getSeveridadIcon = (severidad: string) => {
    switch (severidad.toLowerCase()) {
      case 'critica':
      case 'severa':
        return <ErrorIcon color="error" />;
      case 'moderada':
        return <WarningIcon color="warning" />;
      case 'leve':
        return <InfoIcon color="info" />;
      default:
        return <InfoIcon />;
    }
  };

  const getTipoEstudioLabel = (tipo: string) => {
    const labels: { [key: string]: string } = {
      laboratorio: 'Laboratorio',
      ekg: 'Electrocardiograma',
      eeg: 'Electroencefalograma',
      imagen: 'Imagen Médica',
      ecografia: 'Ecografía',
    };
    return labels[tipo.toLowerCase()] || tipo;
  };

  // Agrupar anomalías por severidad
  const anomaliasCriticas = anomalias.filter(a => a.requiere_atencion_inmediata);
  const anomaliasNoCriticas = anomalias.filter(a => !a.requiere_atencion_inmediata);

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h5" gutterBottom fontWeight="600">
            <BugReportIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Detección de Anomalías
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Anomalías detectadas automáticamente en estudios médicos que requieren revisión
          </Typography>
        </Box>
        <IconButton onClick={cargarAnomalias} color="primary">
          <RefreshIcon />
        </IconButton>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {cargando ? (
        <Box display="flex" justifyContent="center" py={8}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          {/* Resumen */}
          <Grid container spacing={3} mb={4}>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
                <CardContent>
                  <Typography variant="h4" color="white" fontWeight="bold">
                    {anomalias.length}
                  </Typography>
                  <Typography variant="body2" color="rgba(255,255,255,0.8)">
                    Total Pendientes
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ background: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%)' }}>
                <CardContent>
                  <Typography variant="h4" color="white" fontWeight="bold">
                    {anomaliasCriticas.length}
                  </Typography>
                  <Typography variant="body2" color="rgba(255,255,255,0.8)">
                    Atención Inmediata
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' }}>
                <CardContent>
                  <Typography variant="h4" color="white" fontWeight="bold">
                    {anomalias.filter(a => a.severidad === 'severa').length}
                  </Typography>
                  <Typography variant="body2" color="rgba(255,255,255,0.8)">
                    Severas
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
                <CardContent>
                  <Typography variant="h4" color="white" fontWeight="bold">
                    {anomalias.filter(a => a.severidad === 'moderada').length}
                  </Typography>
                  <Typography variant="body2" color="rgba(255,255,255,0.8)">
                    Moderadas
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Anomalías Críticas */}
          {anomaliasCriticas.length > 0 && (
            <Card sx={{ mb: 3, borderLeft: 4, borderColor: 'error.main' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom color="error" fontWeight="600">
                  <ErrorIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Requieren Atención Inmediata ({anomaliasCriticas.length})
                </Typography>
                <List>
                  {anomaliasCriticas.map((anomalia, index) => (
                    <React.Fragment key={anomalia.id}>
                      <ListItem
                        sx={{
                          flexDirection: 'column',
                          alignItems: 'flex-start',
                          bgcolor: 'error.50',
                          borderRadius: 1,
                          mb: 1,
                        }}
                      >
                        <Box display="flex" alignItems="center" width="100%" mb={1}>
                          <ListItemIcon>
                            {getSeveridadIcon(anomalia.severidad)}
                          </ListItemIcon>
                          <ListItemText
                            primary={
                              <Box display="flex" alignItems="center" gap={1}>
                                <Typography variant="subtitle1" fontWeight="600">
                                  {anomalia.descripcion}
                                </Typography>
                                <Chip
                                  label={anomalia.severidad}
                                  size="small"
                                  color={getSeveridadColor(anomalia.severidad) as any}
                                />
                                <Chip
                                  label={getTipoEstudioLabel(anomalia.tipo_estudio)}
                                  size="small"
                                  variant="outlined"
                                />
                              </Box>
                            }
                            secondary={
                              <Typography variant="caption" color="text.secondary">
                                Tipo: {anomalia.tipo_anomalia} | Confianza: {(anomalia.confianza_deteccion * 100).toFixed(0)}% | 
                                {new Date(anomalia.created_at).toLocaleString()}
                              </Typography>
                            }
                          />
                          <IconButton onClick={() => toggleExpanded(anomalia.id)} size="small">
                            {expandidos[anomalia.id] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                          </IconButton>
                        </Box>

                        <Collapse in={expandidos[anomalia.id]} sx={{ width: '100%' }}>
                          <Box pl={7} pr={2}>
                            {anomalia.localizacion && (
                              <Typography variant="body2" gutterBottom>
                                <strong>Localización:</strong> {anomalia.localizacion}
                              </Typography>
                            )}

                            {anomalia.patron_detectado && (
                              <Typography variant="body2" gutterBottom>
                                <strong>Patrón Detectado:</strong> {anomalia.patron_detectado}
                              </Typography>
                            )}

                            {Object.keys(anomalia.valores_anormales).length > 0 && (
                              <Box mb={2}>
                                <Typography variant="body2" fontWeight="600" gutterBottom>
                                  Valores Anormales:
                                </Typography>
                                <Paper elevation={0} sx={{ p: 1, bgcolor: 'grey.50' }}>
                                  {Object.entries(anomalia.valores_anormales).map(([key, value]) => (
                                    <Typography key={key} variant="caption" display="block">
                                      • {key}: {JSON.stringify(value)}
                                    </Typography>
                                  ))}
                                </Paper>
                              </Box>
                            )}

                            {anomalia.recomendaciones.length > 0 && (
                              <Box mb={2}>
                                <Typography variant="body2" fontWeight="600" gutterBottom>
                                  Recomendaciones:
                                </Typography>
                                {anomalia.recomendaciones.map((rec, idx) => (
                                  <Typography key={idx} variant="body2">
                                    • {rec}
                                  </Typography>
                                ))}
                              </Box>
                            )}

                            {anomalia.estudios_adicionales.length > 0 && (
                              <Box>
                                <Typography variant="body2" fontWeight="600" gutterBottom>
                                  Estudios Adicionales Sugeridos:
                                </Typography>
                                <Box display="flex" flexWrap="wrap" gap={1}>
                                  {anomalia.estudios_adicionales.map((estudio, idx) => (
                                    <Chip key={idx} label={estudio} size="small" color="primary" variant="outlined" />
                                  ))}
                                </Box>
                              </Box>
                            )}
                          </Box>
                        </Collapse>
                      </ListItem>
                      {index < anomaliasCriticas.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              </CardContent>
            </Card>
          )}

          {/* Otras Anomalías */}
          {anomaliasNoCriticas.length > 0 && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom fontWeight="600">
                  Otras Anomalías Detectadas ({anomaliasNoCriticas.length})
                </Typography>
                <List>
                  {anomaliasNoCriticas.map((anomalia, index) => (
                    <React.Fragment key={anomalia.id}>
                      <ListItem
                        sx={{
                          flexDirection: 'column',
                          alignItems: 'flex-start',
                        }}
                      >
                        <Box display="flex" alignItems="center" width="100%" mb={1}>
                          <ListItemIcon>
                            {getSeveridadIcon(anomalia.severidad)}
                          </ListItemIcon>
                          <ListItemText
                            primary={
                              <Box display="flex" alignItems="center" gap={1}>
                                <Typography variant="subtitle1" fontWeight="500">
                                  {anomalia.descripcion}
                                </Typography>
                                <Chip
                                  label={anomalia.severidad}
                                  size="small"
                                  color={getSeveridadColor(anomalia.severidad) as any}
                                />
                                <Chip
                                  label={getTipoEstudioLabel(anomalia.tipo_estudio)}
                                  size="small"
                                  variant="outlined"
                                />
                              </Box>
                            }
                            secondary={
                              <Typography variant="caption" color="text.secondary">
                                Tipo: {anomalia.tipo_anomalia} | Confianza: {(anomalia.confianza_deteccion * 100).toFixed(0)}% | 
                                {new Date(anomalia.created_at).toLocaleString()}
                              </Typography>
                            }
                          />
                          <IconButton onClick={() => toggleExpanded(anomalia.id)} size="small">
                            {expandidos[anomalia.id] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                          </IconButton>
                        </Box>

                        <Collapse in={expandidos[anomalia.id]} sx={{ width: '100%' }}>
                          <Box pl={7} pr={2}>
                            {anomalia.localizacion && (
                              <Typography variant="body2" gutterBottom>
                                <strong>Localización:</strong> {anomalia.localizacion}
                              </Typography>
                            )}

                            {anomalia.patron_detectado && (
                              <Typography variant="body2" gutterBottom>
                                <strong>Patrón Detectado:</strong> {anomalia.patron_detectado}
                              </Typography>
                            )}

                            {Object.keys(anomalia.valores_anormales).length > 0 && (
                              <Box mb={2}>
                                <Typography variant="body2" fontWeight="600" gutterBottom>
                                  Valores Anormales:
                                </Typography>
                                <Paper elevation={0} sx={{ p: 1, bgcolor: 'grey.50' }}>
                                  {Object.entries(anomalia.valores_anormales).map(([key, value]) => (
                                    <Typography key={key} variant="caption" display="block">
                                      • {key}: {JSON.stringify(value)}
                                    </Typography>
                                  ))}
                                </Paper>
                              </Box>
                            )}

                            {anomalia.recomendaciones.length > 0 && (
                              <Box mb={2}>
                                <Typography variant="body2" fontWeight="600" gutterBottom>
                                  Recomendaciones:
                                </Typography>
                                {anomalia.recomendaciones.map((rec, idx) => (
                                  <Typography key={idx} variant="body2">
                                    • {rec}
                                  </Typography>
                                ))}
                              </Box>
                            )}

                            {anomalia.estudios_adicionales.length > 0 && (
                              <Box>
                                <Typography variant="body2" fontWeight="600" gutterBottom>
                                  Estudios Adicionales Sugeridos:
                                </Typography>
                                <Box display="flex" flexWrap="wrap" gap={1}>
                                  {anomalia.estudios_adicionales.map((estudio, idx) => (
                                    <Chip key={idx} label={estudio} size="small" color="primary" variant="outlined" />
                                  ))}
                                </Box>
                              </Box>
                            )}
                          </Box>
                        </Collapse>
                      </ListItem>
                      {index < anomaliasNoCriticas.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              </CardContent>
            </Card>
          )}

          {/* Sin Anomalías */}
          {anomalias.length === 0 && (
            <Card>
              <CardContent>
                <Box textAlign="center" py={8}>
                  <CheckCircleIcon sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    No hay anomalías pendientes de revisión
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Todas las anomalías detectadas han sido revisadas
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </Box>
  );
};

export default DeteccionAnomalias;
