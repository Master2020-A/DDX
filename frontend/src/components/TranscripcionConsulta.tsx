import React, { useState, useRef } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  Mic,
  Stop,
  PlayArrow,
  Pause,
  Close,
  CheckCircle,
  AutoAwesome,
} from '@mui/icons-material';
import plnService from '../services/plnService';

interface TranscripcionConsultaProps {
  pacienteId: string;
  onDatosExtraidos?: (datos: any) => void;
  onTranscripcionCompleta?: (texto: string) => void;
}

const TranscripcionConsulta: React.FC<TranscripcionConsultaProps> = ({
  pacienteId,
  onDatosExtraidos,
  onTranscripcionCompleta,
}) => {
  const [grabando, setGrabando] = useState(false);
  const [procesando, setProcesando] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [transcripcion, setTranscripcion] = useState<string>('');
  const [datosExtraidos, setDatosExtraidos] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [tiempoGrabacion, setTiempoGrabacion] = useState(0);
  const [mostrarResultados, setMostrarResultados] = useState(false);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const iniciarGrabacion = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setAudioBlob(blob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setGrabando(true);
      setTiempoGrabacion(0);
      setError(null);

      timerRef.current = setInterval(() => {
        setTiempoGrabacion(prev => prev + 1);
      }, 1000);

    } catch (err) {
      console.error('Error al acceder al micrófono:', err);
      setError('No se pudo acceder al micrófono. Verifica los permisos.');
    }
  };

  const detenerGrabacion = () => {
    if (mediaRecorderRef.current && grabando) {
      mediaRecorderRef.current.stop();
      setGrabando(false);
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  const procesarAudio = async () => {
    if (!audioBlob) return;

    try {
      setProcesando(true);
      setError(null);

      const archivo = new File([audioBlob], 'consulta.webm', { type: 'audio/webm' });

      const resultado = await plnService.transcribirAudio(
        archivo,
        pacienteId,
        'es',
        true
      );

      setTranscripcion(resultado.texto);
      
      if (resultado.informacion_extraida) {
        setDatosExtraidos(resultado.informacion_extraida);
        
        if (onDatosExtraidos) {
          onDatosExtraidos(resultado.informacion_extraida);
        }
      }

      if (onTranscripcionCompleta) {
        onTranscripcionCompleta(resultado.texto);
      }

      setMostrarResultados(true);

    } catch (err: any) {
      console.error('Error al procesar audio:', err);
      setError(err.response?.data?.detail || 'Error al transcribir el audio');
    } finally {
      setProcesando(false);
    }
  };

  const formatearTiempo = (segundos: number) => {
    const mins = Math.floor(segundos / 60);
    const secs = segundos % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const limpiar = () => {
    setAudioBlob(null);
    setTranscripcion('');
    setDatosExtraidos(null);
    setTiempoGrabacion(0);
    setMostrarResultados(false);
    setError(null);
  };

  return (
    <Box>
      <Card sx={{ mb: 3, background: 'linear-gradient(135deg, #667eea15 0%, #764ba215 100%)' }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Box display="flex" alignItems="center" gap={1}>
              <Mic sx={{ fontSize: 28, color: 'primary.main' }} />
              <Typography variant="h6" fontWeight="600">
                Captura de Consulta por Voz
              </Typography>
            </Box>
            {audioBlob && (
              <Chip
                icon={<CheckCircle />}
                label="Audio grabado"
                color="success"
                size="small"
              />
            )}
          </Box>

          <Typography variant="body2" color="text.secondary" mb={3}>
            Graba la consulta médica y el sistema transcribirá automáticamente el audio,
            extrayendo síntomas, signos vitales, diagnósticos y más para pre-llenar el expediente.
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          <Box display="flex" gap={2} alignItems="center" flexWrap="wrap">
            {!grabando && !audioBlob && (
              <Button
                variant="contained"
                size="large"
                startIcon={<Mic />}
                onClick={iniciarGrabacion}
                sx={{
                  background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #5568d3 30%, #63408a 90%)',
                  },
                }}
              >
                Iniciar Grabación
              </Button>
            )}

            {grabando && (
              <>
                <Button
                  variant="contained"
                  color="error"
                  size="large"
                  startIcon={<Stop />}
                  onClick={detenerGrabacion}
                >
                  Detener Grabación
                </Button>
                <Box display="flex" alignItems="center" gap={1}>
                  <Box
                    sx={{
                      width: 12,
                      height: 12,
                      borderRadius: '50%',
                      bgcolor: 'error.main',
                      animation: 'pulse 1.5s ease-in-out infinite',
                      '@keyframes pulse': {
                        '0%, 100%': { opacity: 1 },
                        '50%': { opacity: 0.3 },
                      },
                    }}
                  />
                  <Typography variant="h6" color="error.main" fontWeight="600">
                    {formatearTiempo(tiempoGrabacion)}
                  </Typography>
                </Box>
              </>
            )}

            {audioBlob && !procesando && (
              <>
                <Button
                  variant="contained"
                  size="large"
                  startIcon={<AutoAwesome />}
                  onClick={procesarAudio}
                  sx={{
                    background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
                  }}
                >
                  Transcribir y Extraer Datos
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  onClick={limpiar}
                >
                  Nueva Grabación
                </Button>
              </>
            )}

            {procesando && (
              <Box display="flex" alignItems="center" gap={2} width="100%">
                <CircularProgress size={24} />
                <Box flex={1}>
                  <Typography variant="body2" color="text.secondary" mb={1}>
                    Procesando audio con IA...
                  </Typography>
                  <LinearProgress />
                </Box>
              </Box>
            )}
          </Box>

          {audioBlob && (
            <Box mt={2}>
              <Typography variant="caption" color="text.secondary">
                Duración: {formatearTiempo(tiempoGrabacion)}
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Diálogo de Resultados */}
      <Dialog
        open={mostrarResultados}
        onClose={() => setMostrarResultados(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" gap={1}>
              <CheckCircle color="success" />
              <Typography variant="h6">Transcripción Completada</Typography>
            </Box>
            <IconButton onClick={() => setMostrarResultados(false)}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          {/* Transcripción */}
          <Box mb={3}>
            <Typography variant="subtitle1" fontWeight="600" gutterBottom>
              📝 Texto Transcrito:
            </Typography>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="body2" style={{ whiteSpace: 'pre-wrap' }}>
                  {transcripcion}
                </Typography>
              </CardContent>
            </Card>
          </Box>

          {/* Datos Extraídos */}
          {datosExtraidos && (
            <Box>
              <Typography variant="subtitle1" fontWeight="600" gutterBottom>
                🔍 Información Extraída Automáticamente:
              </Typography>

              {/* Síntomas */}
              {datosExtraidos.sintomas && datosExtraidos.sintomas.length > 0 && (
                <Box mb={2}>
                  <Typography variant="subtitle2" color="primary" gutterBottom>
                    Síntomas:
                  </Typography>
                  <Box display="flex" flexWrap="wrap" gap={1}>
                    {datosExtraidos.sintomas.map((sintoma: any, idx: number) => (
                      <Chip
                        key={idx}
                        label={sintoma.nombre || sintoma}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </Box>
              )}

              {/* Signos Vitales */}
              {datosExtraidos.signos_vitales && (
                <Box mb={2}>
                  <Typography variant="subtitle2" color="primary" gutterBottom>
                    Signos Vitales:
                  </Typography>
                  <List dense>
                    {Object.entries(datosExtraidos.signos_vitales).map(([key, value]: [string, any]) => (
                      <ListItem key={key}>
                        <ListItemText
                          primary={key.replace(/_/g, ' ').toUpperCase()}
                          secondary={value}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              {/* Medicamentos */}
              {datosExtraidos.medicamentos && datosExtraidos.medicamentos.length > 0 && (
                <Box mb={2}>
                  <Typography variant="subtitle2" color="primary" gutterBottom>
                    Medicamentos Mencionados:
                  </Typography>
                  <Box display="flex" flexWrap="wrap" gap={1}>
                    {datosExtraidos.medicamentos.map((med: any, idx: number) => (
                      <Chip
                        key={idx}
                        label={med.nombre || med}
                        size="small"
                        color="secondary"
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </Box>
              )}

              {/* Diagnósticos */}
              {datosExtraidos.diagnosticos && datosExtraidos.diagnosticos.length > 0 && (
                <Box mb={2}>
                  <Typography variant="subtitle2" color="primary" gutterBottom>
                    Diagnósticos Sugeridos:
                  </Typography>
                  <List dense>
                    {datosExtraidos.diagnosticos.map((diag: any, idx: number) => (
                      <ListItem key={idx}>
                        <ListItemText
                          primary={diag.nombre || diag}
                          secondary={diag.codigo_cie10}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              {/* Antecedentes */}
              {datosExtraidos.antecedentes && datosExtraidos.antecedentes.length > 0 && (
                <Box mb={2}>
                  <Typography variant="subtitle2" color="primary" gutterBottom>
                    Antecedentes:
                  </Typography>
                  <List dense>
                    {datosExtraidos.antecedentes.map((ant: any, idx: number) => (
                      <ListItem key={idx}>
                        <ListItemText primary={ant} />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMostrarResultados(false)}>
            Cerrar
          </Button>
          <Button
            variant="contained"
            onClick={() => {
              setMostrarResultados(false);
              limpiar();
            }}
          >
            Aceptar y Continuar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TranscripcionConsulta;
