import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  Divider,
  CircularProgress,
  Alert,
  Autocomplete,
  FormControlLabel,
  Checkbox,
  Paper,
  Chip,
} from '@mui/material';
import {
  Send as SendIcon,
  Psychology as PsychologyIcon,
  History as HistoryIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import iaMedicaService, { AsistenteConsultaResponse } from '../../services/iaMedicaService';
import { pacienteService } from '../../services/pacienteService';

const AsistenteIA: React.FC = () => {
  const [pregunta, setPregunta] = useState('');
  const [pacienteSeleccionado, setPacienteSeleccionado] = useState<any>(null);
  const [pacientes, setPacientes] = useState<any[]>([]);
  const [incluirHistorial, setIncluirHistorial] = useState(true);
  const [incluirEstudios, setIncluirEstudios] = useState(true);
  const [consultando, setConsultando] = useState(false);
  const [respuestaActual, setRespuestaActual] = useState<AsistenteConsultaResponse | null>(null);
  const [historial, setHistorial] = useState<AsistenteConsultaResponse[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    cargarPacientes();
    cargarHistorial();
  }, []);

  const cargarPacientes = async () => {
    try {
      const data = await pacienteService.listar();
      setPacientes(data);
    } catch (err) {
      console.error('Error al cargar pacientes:', err);
    }
  };

  const cargarHistorial = async () => {
    try {
      const data = await iaMedicaService.obtenerHistorialAsistente(undefined, 10);
      setHistorial(data);
    } catch (err) {
      console.error('Error al cargar historial:', err);
    }
  };

  const handleConsultar = async () => {
    if (!pregunta.trim()) {
      setError('Por favor ingresa una pregunta');
      return;
    }

    try {
      setConsultando(true);
      setError(null);
      
      const request = {
        pregunta: pregunta.trim(),
        paciente_id: pacienteSeleccionado?.id,
        incluir_historial: incluirHistorial,
        incluir_estudios: incluirEstudios,
        tipo_consulta: 'diagnostico',
      };

      const respuesta = await iaMedicaService.consultarAsistente(request);
      setRespuestaActual(respuesta);
      
      // Agregar al historial
      setHistorial([respuesta, ...historial]);
      
      // Limpiar pregunta
      setPregunta('');
    } catch (err: any) {
      console.error('Error al consultar asistente:', err);
      setError(err.response?.data?.detail || 'Error al consultar al asistente');
    } finally {
      setConsultando(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleConsultar();
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom fontWeight="600">
        <PsychologyIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Asistente de Diagnóstico con IA
      </Typography>
      <Typography variant="body2" color="text.secondary" mb={3}>
        Consulta al asistente de IA para obtener ayuda con diagnósticos, interpretación de estudios y recomendaciones clínicas
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Formulario de Consulta */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Nueva Consulta
          </Typography>

          {/* Selección de Paciente */}
          <Autocomplete
            options={pacientes}
            getOptionLabel={(option) => `${option.nombre_completo} - ${option.numero_expediente}`}
            value={pacienteSeleccionado}
            onChange={(_e, newValue) => setPacienteSeleccionado(newValue)}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Paciente (Opcional)"
                placeholder="Selecciona un paciente para incluir su contexto"
                margin="normal"
              />
            )}
            sx={{ mb: 2 }}
          />

          {/* Opciones de Contexto */}
          {pacienteSeleccionado && (
            <Box sx={{ mb: 2 }}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={incluirHistorial}
                    onChange={(e) => setIncluirHistorial(e.target.checked)}
                  />
                }
                label="Incluir historial clínico"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={incluirEstudios}
                    onChange={(e) => setIncluirEstudios(e.target.checked)}
                  />
                }
                label="Incluir estudios recientes"
              />
            </Box>
          )}

          {/* Campo de Pregunta */}
          <TextField
            fullWidth
            multiline
            rows={4}
            label="Tu Pregunta"
            placeholder="Ejemplo: ¿Cuál es el diagnóstico diferencial para un paciente con dolor torácico y disnea?"
            value={pregunta}
            onChange={(e) => setPregunta(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={consultando}
            sx={{ mb: 2 }}
          />

          {/* Botón de Enviar */}
          <Button
            variant="contained"
            size="large"
            startIcon={consultando ? <CircularProgress size={20} /> : <SendIcon />}
            onClick={handleConsultar}
            disabled={consultando || !pregunta.trim()}
            fullWidth
            sx={{
              background: 'linear-gradient(45deg, #9c27b0 30%, #673ab7 90%)',
              '&:hover': {
                background: 'linear-gradient(45deg, #7b1fa2 30%, #512da8 90%)',
              },
            }}
          >
            {consultando ? 'Consultando...' : 'Consultar al Asistente'}
          </Button>
        </CardContent>
      </Card>

      {/* Respuesta Actual */}
      {respuestaActual && (
        <Card sx={{ mb: 3, borderLeft: 4, borderColor: 'primary.main' }}>
          <CardContent>
            <Box display="flex" alignItems="center" gap={1} mb={2}>
              <PsychologyIcon color="primary" />
              <Typography variant="h6" fontWeight="600">
                Respuesta del Asistente
              </Typography>
              {pacienteSeleccionado && (
                <Chip
                  icon={<PersonIcon />}
                  label={pacienteSeleccionado.nombre_completo}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              )}
            </Box>

            <Paper elevation={0} sx={{ p: 2, bgcolor: 'grey.50', mb: 2 }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Pregunta:
              </Typography>
              <Typography variant="body1" paragraph>
                {respuestaActual.pregunta}
              </Typography>
            </Paper>

            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Respuesta:
            </Typography>
            <Typography
              variant="body1"
              sx={{
                whiteSpace: 'pre-wrap',
                lineHeight: 1.8,
              }}
            >
              {respuestaActual.respuesta}
            </Typography>

            <Box mt={2}>
              <Typography variant="caption" color="text.secondary">
                Tipo: {respuestaActual.tipo_consulta} | {new Date(respuestaActual.created_at).toLocaleString()}
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Historial de Consultas */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            <HistoryIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Historial de Consultas
          </Typography>

          {historial.length === 0 ? (
            <Alert severity="info" sx={{ mt: 2 }}>
              No hay consultas previas
            </Alert>
          ) : (
            <List>
              {historial.map((consulta, index) => (
                <React.Fragment key={consulta.id}>
                  <ListItem
                    alignItems="flex-start"
                    sx={{
                      cursor: 'pointer',
                      '&:hover': { bgcolor: 'action.hover' },
                    }}
                    onClick={() => setRespuestaActual(consulta)}
                  >
                    <ListItemText
                      primary={
                        <Typography variant="subtitle1" fontWeight="500">
                          {consulta.pregunta.length > 100
                            ? consulta.pregunta.substring(0, 100) + '...'
                            : consulta.pregunta}
                        </Typography>
                      }
                      secondary={
                        <>
                          <Typography variant="body2" color="text.secondary" component="span">
                            {consulta.respuesta.length > 150
                              ? consulta.respuesta.substring(0, 150) + '...'
                              : consulta.respuesta}
                          </Typography>
                          <br />
                          <Typography variant="caption" color="text.secondary">
                            {new Date(consulta.created_at).toLocaleString()}
                          </Typography>
                        </>
                      }
                    />
                  </ListItem>
                  {index < historial.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default AsistenteIA;
