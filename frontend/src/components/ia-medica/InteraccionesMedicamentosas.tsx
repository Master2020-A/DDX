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
  Chip,
  List,
  ListItem,
  ListItemText,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  LocalPharmacy as LocalPharmacyIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import iaMedicaService, { InteraccionMedicamentosaResponse } from '../../services/iaMedicaService';
import { pacienteService } from '../../services/pacienteService';

const InteraccionesMedicamentosas: React.FC = () => {
  const [pacienteSeleccionado, setPacienteSeleccionado] = useState<any>(null);
  const [pacientes, setPacientes] = useState<any[]>([]);
  const [medicamentos, setMedicamentos] = useState<string[]>([]);
  const [medicamentoInput, setMedicamentoInput] = useState('');
  const [incluirAlergias, setIncluirAlergias] = useState(true);
  const [incluirCondiciones, setIncluirCondiciones] = useState(true);
  const [analizando, setAnalizando] = useState(false);
  const [analisisActual, setAnalisisActual] = useState<InteraccionMedicamentosaResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    cargarPacientes();
  }, []);

  const cargarPacientes = async () => {
    try {
      const data = await pacienteService.listar();
      setPacientes(data);
    } catch (err) {
      console.error('Error al cargar pacientes:', err);
    }
  };

  const handleAgregarMedicamento = () => {
    if (medicamentoInput.trim() && !medicamentos.includes(medicamentoInput.trim())) {
      setMedicamentos([...medicamentos, medicamentoInput.trim()]);
      setMedicamentoInput('');
    }
  };

  const handleEliminarMedicamento = (medicamento: string) => {
    setMedicamentos(medicamentos.filter(m => m !== medicamento));
  };

  const handleAnalizar = async () => {
    if (!pacienteSeleccionado) {
      setError('Por favor selecciona un paciente');
      return;
    }

    if (medicamentos.length < 2) {
      setError('Por favor agrega al menos 2 medicamentos para analizar');
      return;
    }

    try {
      setAnalizando(true);
      setError(null);

      const request = {
        paciente_id: pacienteSeleccionado.id,
        medicamentos: medicamentos,
        incluir_alergias: incluirAlergias,
        incluir_condiciones: incluirCondiciones,
      };

      const analisis = await iaMedicaService.analizarInteracciones(request);
      setAnalisisActual(analisis);
    } catch (err: any) {
      console.error('Error al analizar interacciones:', err);
      setError(err.response?.data?.detail || 'Error al analizar interacciones medicamentosas');
    } finally {
      setAnalizando(false);
    }
  };

  const getSeveridadColor = (severidad: string) => {
    switch (severidad.toLowerCase()) {
      case 'contraindicada':
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
      case 'contraindicada':
      case 'severa':
        return <ErrorIcon />;
      case 'moderada':
        return <WarningIcon />;
      default:
        return <InfoIcon />;
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom fontWeight="600">
        <LocalPharmacyIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Análisis de Interacciones Medicamentosas
      </Typography>
      <Typography variant="body2" color="text.secondary" mb={3}>
        Detecta interacciones entre medicamentos y contraindicaciones basadas en alergias y condiciones del paciente
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
            Analizar Interacciones
          </Typography>

          <Grid container spacing={2}>
            <Grid item xs={12}>
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

            <Grid item xs={12}>
              <Box display="flex" gap={1}>
                <TextField
                  fullWidth
                  label="Agregar Medicamento"
                  placeholder="Ej: Losartán 50mg"
                  value={medicamentoInput}
                  onChange={(e) => setMedicamentoInput(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAgregarMedicamento();
                    }
                  }}
                />
                <Button
                  variant="outlined"
                  onClick={handleAgregarMedicamento}
                  disabled={!medicamentoInput.trim()}
                >
                  Agregar
                </Button>
              </Box>
            </Grid>

            {medicamentos.length > 0 && (
              <Grid item xs={12}>
                <Paper elevation={0} sx={{ p: 2, border: 1, borderColor: 'divider' }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Medicamentos a Analizar ({medicamentos.length})
                  </Typography>
                  <Box display="flex" flexWrap="wrap" gap={1} mt={1}>
                    {medicamentos.map((med, index) => (
                      <Chip
                        key={index}
                        label={med}
                        onDelete={() => handleEliminarMedicamento(med)}
                        color="primary"
                      />
                    ))}
                  </Box>
                </Paper>
              </Grid>
            )}

            <Grid item xs={12}>
              <Button
                variant="contained"
                size="large"
                fullWidth
                startIcon={analizando ? <CircularProgress size={20} /> : <LocalPharmacyIcon />}
                onClick={handleAnalizar}
                disabled={analizando || !pacienteSeleccionado || medicamentos.length < 2}
                sx={{
                  background: 'linear-gradient(45deg, #FF6B6B 30%, #EE5A6F 90%)',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #E85555 30%, #D84860 90%)',
                  },
                }}
              >
                {analizando ? 'Analizando Interacciones...' : 'Analizar Interacciones'}
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Resultado del Análisis */}
      {analisisActual && (
        <Box>
          {/* Resumen de Severidad */}
          <Card sx={{ mb: 3, borderLeft: 4, borderColor: `${getSeveridadColor(analisisActual.severidad_maxima)}.main` }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                <Typography variant="h6" fontWeight="600">
                  Resultado del Análisis
                </Typography>
                <Chip
                  icon={getSeveridadIcon(analisisActual.severidad_maxima)}
                  label={`Severidad Máxima: ${analisisActual.severidad_maxima.toUpperCase()}`}
                  color={getSeveridadColor(analisisActual.severidad_maxima) as any}
                  size="medium"
                />
              </Box>

              <Typography variant="body2" color="text.secondary">
                Se analizaron {analisisActual.medicamentos_analizados.length} medicamentos y se encontraron{' '}
                {analisisActual.interacciones_encontradas.length} interacciones
              </Typography>
            </CardContent>
          </Card>

          {/* Alertas Críticas */}
          {analisisActual.alertas_criticas.length > 0 && (
            <Alert severity="error" sx={{ mb: 3 }}>
              <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                ⚠️ Alertas Críticas
              </Typography>
              <List dense>
                {analisisActual.alertas_criticas.map((alerta, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={`• ${alerta}`} />
                  </ListItem>
                ))}
              </List>
            </Alert>
          )}

          {/* Interacciones Encontradas */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Interacciones Detectadas ({analisisActual.interacciones_encontradas.length})
              </Typography>

              {analisisActual.interacciones_encontradas.length === 0 ? (
                <Alert severity="success">
                  No se detectaron interacciones entre los medicamentos analizados
                </Alert>
              ) : (
                <TableContainer component={Paper} elevation={0} sx={{ border: 1, borderColor: 'divider' }}>
                  <Table>
                    <TableHead>
                      <TableRow sx={{ bgcolor: 'grey.50' }}>
                        <TableCell><strong>Medicamentos</strong></TableCell>
                        <TableCell><strong>Severidad</strong></TableCell>
                        <TableCell><strong>Descripción</strong></TableCell>
                        <TableCell><strong>Manejo</strong></TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {analisisActual.interacciones_encontradas.map((interaccion, index) => (
                        <TableRow key={index}>
                          <TableCell>
                            <Typography variant="body2" fontWeight="600">
                              {interaccion.medicamento1}
                            </Typography>
                            <Typography variant="body2" fontWeight="600">
                              + {interaccion.medicamento2}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={interaccion.severidad}
                              size="small"
                              color={getSeveridadColor(interaccion.severidad) as any}
                              icon={getSeveridadIcon(interaccion.severidad)}
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" gutterBottom>
                              {interaccion.descripcion}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              <strong>Mecanismo:</strong> {interaccion.mecanismo}
                            </Typography>
                            {interaccion.efectos.length > 0 && (
                              <Box mt={1}>
                                <Typography variant="caption" color="text.secondary">
                                  <strong>Efectos:</strong> {interaccion.efectos.join(', ')}
                                </Typography>
                              </Box>
                            )}
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {interaccion.manejo}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>

          {/* Recomendaciones de Ajuste */}
          {analisisActual.recomendaciones_ajuste.length > 0 && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <WarningIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Recomendaciones de Ajuste
                </Typography>
                <List>
                  {analisisActual.recomendaciones_ajuste.map((rec, index) => (
                    <ListItem key={index}>
                      <ListItemText primary={`• ${rec}`} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          )}

          {/* Información del Paciente Considerada */}
          <Grid container spacing={3}>
            {analisisActual.alergias_consideradas.length > 0 && (
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Alergias Consideradas
                    </Typography>
                    <Box display="flex" flexWrap="wrap" gap={1}>
                      {analisisActual.alergias_consideradas.map((alergia, index) => (
                        <Chip key={index} label={alergia} color="error" variant="outlined" />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )}

            {analisisActual.condiciones_consideradas.length > 0 && (
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Condiciones Consideradas
                    </Typography>
                    <Box display="flex" flexWrap="wrap" gap={1}>
                      {analisisActual.condiciones_consideradas.map((condicion, index) => (
                        <Chip key={index} label={condicion} color="warning" variant="outlined" />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>

          <Box mt={2}>
            <Typography variant="caption" color="text.secondary">
              Análisis generado: {new Date(analisisActual.created_at).toLocaleString()}
            </Typography>
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default InteraccionesMedicamentosas;
