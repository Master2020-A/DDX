/**
 * Componente para mostrar resultados del pre-diagnóstico
 */
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Grid,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  LocalHospital as LocalHospitalIcon,
  Science as ScienceIcon,
  MedicalServices as MedicalServicesIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import type { PreDiagnosticoResponse } from '@/services/prediagnosticoService';

interface Props {
  resultado: PreDiagnosticoResponse;
}

export default function ResultadosPrediagnostico({ resultado }: Props) {
  const getUrgenciaColor = (urgencia: string) => {
    switch (urgencia.toLowerCase()) {
      case 'critico':
        return 'error';
      case 'alto':
        return 'warning';
      case 'medio':
        return 'info';
      case 'bajo':
        return 'success';
      default:
        return 'default';
    }
  };

  const getUrgenciaIcon = (urgencia: string) => {
    switch (urgencia.toLowerCase()) {
      case 'critico':
      case 'alto':
        return <WarningIcon />;
      default:
        return <InfoIcon />;
    }
  };

  return (
    <Box>
      {/* Nivel de Urgencia Global */}
      <Alert 
        severity={getUrgenciaColor(resultado.nivel_urgencia) as any}
        icon={getUrgenciaIcon(resultado.nivel_urgencia)}
        sx={{ mb: 3 }}
      >
        <Typography variant="h6">
          Nivel de Urgencia: {resultado.nivel_urgencia.toUpperCase()}
        </Typography>
      </Alert>

      {/* Diagnósticos Diferenciales */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <LocalHospitalIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">Diagnósticos Diferenciales</Typography>
          </Box>

          {resultado.diagnosticos_diferenciales.map((diagnostico, index) => (
            <Accordion key={index} defaultExpanded={index === 0}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box display="flex" alignItems="center" width="100%" gap={2}>
                  <Typography variant="subtitle1" fontWeight="bold" flex={1}>
                    {index + 1}. {diagnostico.nombre}
                  </Typography>
                  {diagnostico.codigo_cie10 && (
                    <Chip label={`CIE-10: ${diagnostico.codigo_cie10}`} size="small" variant="outlined" />
                  )}
                  <Chip 
                    label={`${diagnostico.probabilidad.toFixed(1)}%`}
                    color={diagnostico.probabilidad > 70 ? 'error' : diagnostico.probabilidad > 40 ? 'warning' : 'info'}
                    size="small"
                  />
                  <Chip 
                    label={diagnostico.urgencia}
                    color={getUrgenciaColor(diagnostico.urgencia) as any}
                    size="small"
                  />
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  {/* Probabilidad */}
                  <Grid item xs={12}>
                    <Typography variant="caption" color="text.secondary">
                      Probabilidad
                    </Typography>
                    <Box display="flex" alignItems="center" gap={1}>
                      <LinearProgress 
                        variant="determinate" 
                        value={diagnostico.probabilidad} 
                        sx={{ flex: 1, height: 8, borderRadius: 1 }}
                        color={diagnostico.probabilidad > 70 ? 'error' : diagnostico.probabilidad > 40 ? 'warning' : 'info'}
                      />
                      <Typography variant="body2" fontWeight="bold">
                        {diagnostico.probabilidad.toFixed(1)}%
                      </Typography>
                    </Box>
                  </Grid>

                  {/* Evidencias */}
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                      Evidencias:
                    </Typography>
                    <List dense>
                      {diagnostico.evidencias.map((evidencia, i) => (
                        <ListItem key={i}>
                          <ListItemIcon sx={{ minWidth: 30 }}>
                            <CheckCircleIcon fontSize="small" color="success" />
                          </ListItemIcon>
                          <ListItemText primary={evidencia} />
                        </ListItem>
                      ))}
                    </List>
                  </Grid>

                  {/* Síntomas Coincidentes */}
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                      Síntomas Coincidentes:
                    </Typography>
                    <List dense>
                      {diagnostico.sintomas_coincidentes.map((sintoma, i) => (
                        <ListItem key={i}>
                          <ListItemIcon sx={{ minWidth: 30 }}>
                            <CheckCircleIcon fontSize="small" color="primary" />
                          </ListItemIcon>
                          <ListItemText primary={sintoma} />
                        </ListItem>
                      ))}
                    </List>
                  </Grid>

                  {/* Síntomas Faltantes */}
                  {diagnostico.sintomas_faltantes && diagnostico.sintomas_faltantes.length > 0 && (
                    <Grid item xs={12}>
                      <Typography variant="subtitle2" gutterBottom>
                        Síntomas que faltarían para confirmar:
                      </Typography>
                      <List dense>
                        {diagnostico.sintomas_faltantes.map((sintoma, i) => (
                          <ListItem key={i}>
                            <ListItemIcon sx={{ minWidth: 30 }}>
                              <InfoIcon fontSize="small" color="info" />
                            </ListItemIcon>
                            <ListItemText primary={sintoma} />
                          </ListItem>
                        ))}
                      </List>
                    </Grid>
                  )}

                  {/* Recomendaciones */}
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom>
                      Recomendaciones:
                    </Typography>
                    <List dense>
                      {diagnostico.recomendaciones.map((recomendacion, i) => (
                        <ListItem key={i}>
                          <ListItemIcon sx={{ minWidth: 30 }}>
                            <MedicalServicesIcon fontSize="small" color="primary" />
                          </ListItemIcon>
                          <ListItemText primary={recomendacion} />
                        </ListItem>
                      ))}
                    </List>
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          ))}
        </CardContent>
      </Card>

      {/* Exámenes Sugeridos */}
      {resultado.examenes_sugeridos.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <ScienceIcon sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">Exámenes Complementarios Sugeridos</Typography>
            </Box>
            <List>
              {resultado.examenes_sugeridos.map((examen, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <ScienceIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText primary={examen} />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {/* Signos de Alarma */}
      {resultado.signos_alarma.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <WarningIcon sx={{ mr: 1, color: 'error.main' }} />
              <Typography variant="h6" color="error">
                Signos de Alarma a Vigilar
              </Typography>
            </Box>
            <Alert severity="warning" sx={{ mb: 2 }}>
              Busque atención médica inmediata si presenta alguno de estos signos
            </Alert>
            <List>
              {resultado.signos_alarma.map((signo, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <WarningIcon color="error" />
                  </ListItemIcon>
                  <ListItemText primary={signo} />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {/* Factores de Riesgo */}
      {resultado.factores_riesgo.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Factores de Riesgo Identificados
            </Typography>
            <Box display="flex" flexWrap="wrap" gap={1}>
              {resultado.factores_riesgo.map((factor, index) => (
                <Chip key={index} label={factor} color="warning" variant="outlined" />
              ))}
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Recomendaciones Generales */}
      {resultado.recomendaciones_generales.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recomendaciones Generales
            </Typography>
            <List>
              {resultado.recomendaciones_generales.map((recomendacion, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <MedicalServicesIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText primary={recomendacion} />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {/* Timestamp */}
      <Typography variant="caption" color="text.secondary" display="block" mt={2} textAlign="right">
        Generado: {new Date(resultado.timestamp).toLocaleString('es-MX')}
      </Typography>
    </Box>
  );
}
