import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Alert,
  CircularProgress,
  Autocomplete,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider,
  Paper,
} from '@mui/material';
import {
  Warning as WarningIcon,
  TrendingUp as TrendingUpIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import iaMedicaService, { PrediccionRiesgoResponse } from '../../services/iaMedicaService';
import { pacienteService } from '../../services/pacienteService';

const TIPOS_RIESGO = [
  { value: 'cardiovascular', label: 'Riesgo Cardiovascular (Framingham)' },
  { value: 'diabetes', label: 'Riesgo de Diabetes Tipo 2' },
  { value: 'cancer_pulmon', label: 'Riesgo de Cáncer de Pulmón' },
  { value: 'osteoporosis', label: 'Riesgo de Osteoporosis' },
  { value: 'renal', label: 'Riesgo de Enfermedad Renal' },
];

const PrediccionRiesgos: React.FC = () => {
  const [pacienteSeleccionado, setPacienteSeleccionado] = useState<any>(null);
  const [pacientes, setPacientes] = useState<any[]>([]);
  const [tipoRiesgo, setTipoRiesgo] = useState('cardiovascular');
  const [generando, setGenerando] = useState(false);
  const [prediccionActual, setPrediccionActual] = useState<PrediccionRiesgoResponse | null>(null);
  const [prediccionesHistoricas, setPrediccionesHistoricas] = useState<PrediccionRiesgoResponse[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    cargarPacientes();
  }, []);

  useEffect(() => {
    if (pacienteSeleccionado) {
      cargarPrediccionesPaciente();
    }
  }, [pacienteSeleccionado]);

  const cargarPacientes = async () => {
    try {
      const data = await pacienteService.listar();
      setPacientes(data);
    } catch (err) {
      console.error('Error al cargar pacientes:', err);
    }
  };

  const cargarPrediccionesPaciente = async () => {
    if (!pacienteSeleccionado) return;
    
    try {
      const data = await iaMedicaService.obtenerPrediccionesPaciente(pacienteSeleccionado.id);
      setPrediccionesHistoricas(data);
    } catch (err) {
      console.error('Error al cargar predicciones:', err);
    }
  };

  const handleGenerarPrediccion = async () => {
    if (!pacienteSeleccionado) {
      setError('Por favor selecciona un paciente');
      return;
    }

    try {
      setGenerando(true);
      setError(null);

      const request = {
        paciente_id: pacienteSeleccionado.id,
        tipo_riesgo: tipoRiesgo,
        incluir_recomendaciones: true,
      };

      const prediccion = await iaMedicaService.predecirRiesgo(request);
      setPrediccionActual(prediccion);
      
      // Recargar predicciones históricas
      await cargarPrediccionesPaciente();
    } catch (err: any) {
      console.error('Error al generar predicción:', err);
      setError(err.response?.data?.detail || 'Error al generar predicción de riesgo');
    } finally {
      setGenerando(false);
    }
  };

  const getNivelRiesgoColor = (nivel: string) => {
    switch (nivel.toLowerCase()) {
      case 'muy_alto':
        return 'error';
      case 'alto':
        return 'error';
      case 'moderado':
        return 'warning';
      case 'bajo':
        return 'success';
      default:
        return 'info';
    }
  };

  const getNivelRiesgoIcon = (nivel: string) => {
    switch (nivel.toLowerCase()) {
      case 'muy_alto':
      case 'alto':
        return <ErrorIcon />;
      case 'moderado':
        return <WarningIcon />;
      case 'bajo':
        return <CheckCircleIcon />;
      default:
        return <InfoIcon />;
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom fontWeight="600">
        <TrendingUpIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Predicción de Riesgos
      </Typography>
      <Typography variant="body2" color="text.secondary" mb={3}>
        Evalúa el riesgo del paciente para diferentes condiciones médicas usando algoritmos validados e IA
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Formulario */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Generar Nueva Predicción
          </Typography>

          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Autocomplete
                options={pacientes}
                getOptionLabel={(option) => `${option.nombre_completo} - ${option.numero_expediente}`}
                value={pacienteSeleccionado}
                onChange={(_e, newValue) => setPacienteSeleccionado(newValue)}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Paciente *"
                    placeholder="Selecciona un paciente"
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Tipo de Riesgo</InputLabel>
                <Select
                  value={tipoRiesgo}
                  label="Tipo de Riesgo"
                  onChange={(e) => setTipoRiesgo(e.target.value)}
                >
                  {TIPOS_RIESGO.map((tipo) => (
                    <MenuItem key={tipo.value} value={tipo.value}>
                      {tipo.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <Button
                variant="contained"
                size="large"
                fullWidth
                startIcon={generando ? <CircularProgress size={20} /> : <TrendingUpIcon />}
                onClick={handleGenerarPrediccion}
                disabled={generando || !pacienteSeleccionado}
                sx={{
                  background: 'linear-gradient(45deg, #f093fb 30%, #f5576c 90%)',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #d87ae8 30%, #e04560 90%)',
                  },
                }}
              >
                {generando ? 'Generando Predicción...' : 'Generar Predicción de Riesgo'}
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Resultado de Predicción */}
      {prediccionActual && (
        <Card sx={{ mb: 3, borderLeft: 4, borderColor: `${getNivelRiesgoColor(prediccionActual.nivel_riesgo)}.main` }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
              <Typography variant="h6" fontWeight="600">
                Resultado de Predicción de Riesgo
              </Typography>
              <Chip
                icon={getNivelRiesgoIcon(prediccionActual.nivel_riesgo)}
                label={`Riesgo ${prediccionActual.nivel_riesgo.toUpperCase()}`}
                color={getNivelRiesgoColor(prediccionActual.nivel_riesgo) as any}
                size="medium"
              />
            </Box>

            {/* Porcentaje de Riesgo */}
            <Paper elevation={0} sx={{ p: 3, bgcolor: 'grey.50', mb: 3 }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Porcentaje de Riesgo
              </Typography>
              <Box display="flex" alignItems="center" gap={2}>
                <Box flex={1}>
                  <LinearProgress
                    variant="determinate"
                    value={prediccionActual.porcentaje_riesgo}
                    color={getNivelRiesgoColor(prediccionActual.nivel_riesgo) as any}
                    sx={{ height: 12, borderRadius: 6 }}
                  />
                </Box>
                <Typography variant="h5" fontWeight="bold" color={`${getNivelRiesgoColor(prediccionActual.nivel_riesgo)}.main`}>
                  {prediccionActual.porcentaje_riesgo.toFixed(1)}%
                </Typography>
              </Box>
              <Typography variant="caption" color="text.secondary" mt={1} display="block">
                Algoritmo: {prediccionActual.algoritmo}
              </Typography>
            </Paper>

            {/* Factores de Riesgo */}
            <Box mb={3}>
              <Typography variant="subtitle1" fontWeight="600" gutterBottom>
                Factores de Riesgo
              </Typography>
              <Grid container spacing={2}>
                {prediccionActual.factores_riesgo.map((factor, index) => (
                  <Grid item xs={12} sm={6} key={index}>
                    <Paper
                      elevation={0}
                      sx={{
                        p: 2,
                        border: 1,
                        borderColor: factor.impacto === 'alto' ? 'error.main' : factor.impacto === 'medio' ? 'warning.main' : 'info.main',
                        borderRadius: 2,
                      }}
                    >
                      <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                        <Typography variant="body2" fontWeight="600">
                          {factor.nombre}
                        </Typography>
                        <Chip
                          label={factor.impacto}
                          size="small"
                          color={factor.impacto === 'alto' ? 'error' : factor.impacto === 'medio' ? 'warning' : 'info'}
                        />
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {factor.modificable ? '✓ Modificable' : '✗ No modificable'}
                      </Typography>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </Box>

            {/* Factores Protectores */}
            {prediccionActual.factores_protectores.length > 0 && (
              <Box mb={3}>
                <Typography variant="subtitle1" fontWeight="600" gutterBottom>
                  Factores Protectores
                </Typography>
                <Box display="flex" flexWrap="wrap" gap={1}>
                  {prediccionActual.factores_protectores.map((factor, index) => (
                    <Chip
                      key={index}
                      label={factor}
                      color="success"
                      variant="outlined"
                      icon={<CheckCircleIcon />}
                    />
                  ))}
                </Box>
              </Box>
            )}

            {/* Recomendaciones */}
            <Box mb={3}>
              <Typography variant="subtitle1" fontWeight="600" gutterBottom>
                Recomendaciones
              </Typography>
              <List>
                {prediccionActual.recomendaciones.map((rec, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={`• ${rec}`} />
                  </ListItem>
                ))}
              </List>
            </Box>

            {/* Estudios Sugeridos */}
            {prediccionActual.estudios_sugeridos.length > 0 && (
              <Box>
                <Typography variant="subtitle1" fontWeight="600" gutterBottom>
                  Estudios Sugeridos
                </Typography>
                <Box display="flex" flexWrap="wrap" gap={1}>
                  {prediccionActual.estudios_sugeridos.map((estudio, index) => (
                    <Chip key={index} label={estudio} color="primary" variant="outlined" />
                  ))}
                </Box>
              </Box>
            )}

            <Divider sx={{ my: 2 }} />
            <Typography variant="caption" color="text.secondary">
              Válido hasta: {new Date(prediccionActual.valido_hasta).toLocaleDateString()} | 
              Generado: {new Date(prediccionActual.created_at).toLocaleString()}
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Predicciones Históricas */}
      {prediccionesHistoricas.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Predicciones Anteriores
            </Typography>
            <List>
              {prediccionesHistoricas.map((pred, index) => (
                <React.Fragment key={pred.id}>
                  <ListItem
                    sx={{
                      cursor: 'pointer',
                      '&:hover': { bgcolor: 'action.hover' },
                    }}
                    onClick={() => setPrediccionActual(pred)}
                  >
                    <ListItemText
                      primary={
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="subtitle1">
                            {pred.tipo_riesgo.replace('_', ' ').toUpperCase()}
                          </Typography>
                          <Chip
                            label={`${pred.porcentaje_riesgo.toFixed(0)}%`}
                            size="small"
                            color={getNivelRiesgoColor(pred.nivel_riesgo) as any}
                          />
                        </Box>
                      }
                      secondary={
                        <>
                          Nivel: {pred.nivel_riesgo} | {new Date(pred.created_at).toLocaleDateString()}
                        </>
                      }
                    />
                  </ListItem>
                  {index < prediccionesHistoricas.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default PrediccionRiesgos;
