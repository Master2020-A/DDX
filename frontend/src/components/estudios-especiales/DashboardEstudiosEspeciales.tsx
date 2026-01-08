/**
 * Dashboard principal para Estudios Especiales
 * Muestra resumen de EKG, EEG y Ecografías de un paciente
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  Tab,
  Tabs,
  Alert,
  CircularProgress,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  Favorite as HeartIcon,
  Psychology as BrainIcon,
  Radar as UltrasoundIcon,
  Add as AddIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { ResumenEstudiosEspeciales } from '../../types/estudiosEspeciales';
import estudiosEspecialesService from '../../services/estudiosEspecialesService';
import ListaEstudiosEKG from './ListaEstudiosEKG';
import ListaEstudiosEEG from './ListaEstudiosEEG';
import ListaEcografias from './ListaEcografias';

interface Props {
  pacienteId: string;
  onNuevoEstudio: (tipo: 'ekg' | 'eeg' | 'ecografia') => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`estudios-tabpanel-${index}`}
      aria-labelledby={`estudios-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const DashboardEstudiosEspeciales: React.FC<Props> = ({ pacienteId, onNuevoEstudio }) => {
  const [resumen, setResumen] = useState<ResumenEstudiosEspeciales | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tabActual, setTabActual] = useState(0);

  const cargarResumen = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await estudiosEspecialesService.obtenerResumenEstudios(pacienteId);
      setResumen(data);
    } catch (err: any) {
      console.error('Error al cargar resumen:', err);
      setError(err.response?.data?.detail || 'Error al cargar estudios especiales');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (pacienteId) {
      cargarResumen();
    }
  }, [pacienteId]);

  const handleCambiarTab = (event: React.SyntheticEvent, newValue: number) => {
    setTabActual(newValue);
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
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!resumen) {
    return (
      <Alert severity="info">
        No se encontraron estudios especiales para este paciente.
      </Alert>
    );
  }

  return (
    <Box>
      {/* Tarjetas de resumen */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {/* EKG */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="flex-start" justifyContent="space-between" mb={2}>
                <Box display="flex" alignItems="center" gap={1} flex={1}>
                  <HeartIcon color="error" fontSize="large" />
                  <Typography variant="h6" sx={{ fontSize: '1rem' }}>EKG</Typography>
                </Box>
                <button
                  onClick={() => onNuevoEstudio('ekg')}
                  title="Nuevo EKG"
                  style={{
                    border: '2px solid #1976d2',
                    color: '#1976d2',
                    borderRadius: '8px',
                    padding: '8px',
                    backgroundColor: 'transparent',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    transition: 'all 0.2s',
                    minWidth: '36px',
                    minHeight: '36px',
                    flexShrink: 0,
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#1976d2';
                    e.currentTarget.style.color = 'white';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'transparent';
                    e.currentTarget.style.color = '#1976d2';
                  }}
                >
                  <AddIcon fontSize="small" />
                </button>
              </Box>
              
              <Typography variant="h3" color="primary" gutterBottom>
                {resumen.ekg.total}
              </Typography>
              
              <Box display="flex" gap={1} flexWrap="wrap">
                {resumen.ekg.criticos > 0 && (
                  <Chip
                    icon={<ErrorIcon />}
                    label={`${resumen.ekg.criticos} Críticos`}
                    color="error"
                    size="small"
                  />
                )}
                {resumen.ekg.requieren_atencion > 0 && (
                  <Chip
                    icon={<WarningIcon />}
                    label={`${resumen.ekg.requieren_atencion} Atención`}
                    color="warning"
                    size="small"
                  />
                )}
                {resumen.ekg.total > 0 && resumen.ekg.criticos === 0 && resumen.ekg.requieren_atencion === 0 && (
                  <Chip
                    icon={<CheckIcon />}
                    label="Sin alertas"
                    color="success"
                    size="small"
                  />
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* EEG */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="flex-start" justifyContent="space-between" mb={2}>
                <Box display="flex" alignItems="center" gap={1} flex={1}>
                  <BrainIcon color="secondary" fontSize="large" />
                  <Typography variant="h6" sx={{ fontSize: '1rem' }}>EEG</Typography>
                </Box>
                <button
                  onClick={() => onNuevoEstudio('eeg')}
                  title="Nuevo EEG"
                  style={{
                    border: '2px solid #9c27b0',
                    color: '#9c27b0',
                    borderRadius: '8px',
                    padding: '8px',
                    backgroundColor: 'transparent',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    transition: 'all 0.2s',
                    minWidth: '36px',
                    minHeight: '36px',
                    flexShrink: 0,
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#9c27b0';
                    e.currentTarget.style.color = 'white';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'transparent';
                    e.currentTarget.style.color = '#9c27b0';
                  }}
                >
                  <AddIcon fontSize="small" />
                </button>
              </Box>
              
              <Typography variant="h3" color="secondary" gutterBottom>
                {resumen.eeg.total}
              </Typography>
              
              <Box display="flex" gap={1} flexWrap="wrap">
                {resumen.eeg.criticos > 0 && (
                  <Chip
                    icon={<ErrorIcon />}
                    label={`${resumen.eeg.criticos} Críticos`}
                    color="error"
                    size="small"
                  />
                )}
                {resumen.eeg.requieren_atencion > 0 && (
                  <Chip
                    icon={<WarningIcon />}
                    label={`${resumen.eeg.requieren_atencion} Atención`}
                    color="warning"
                    size="small"
                  />
                )}
                {resumen.eeg.total > 0 && resumen.eeg.criticos === 0 && resumen.eeg.requieren_atencion === 0 && (
                  <Chip
                    icon={<CheckIcon />}
                    label="Sin alertas"
                    color="success"
                    size="small"
                  />
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Ecografías */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                <Box display="flex" alignItems="center" gap={1}>
                  <UltrasoundIcon color="info" fontSize="large" />
                  <Typography variant="h6">Ecografías</Typography>
                </Box>
                <Tooltip title="Nueva Ecografía">
                  <Box
                    component="button"
                    onClick={() => onNuevoEstudio('ecografia')}
                    sx={{
                      border: '1px solid',
                      borderColor: 'info.main',
                      color: 'info.main',
                      borderRadius: 2,
                      p: 0.5,
                      lineHeight: 0,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      backgroundColor: 'transparent',
                      cursor: 'pointer',
                      '&:hover': {
                        backgroundColor: 'info.main',
                        color: 'white',
                      },
                    }}
                  >
                    <AddIcon fontSize="small" />
                  </Box>
                </Tooltip>
              </Box>
              
              <Typography variant="h3" color="info.main" gutterBottom>
                {resumen.ecografias.total}
              </Typography>
              
              <Box display="flex" gap={1} flexWrap="wrap">
                {resumen.ecografias.requieren_atencion > 0 && (
                  <Chip
                    icon={<WarningIcon />}
                    label={`${resumen.ecografias.requieren_atencion} Atención`}
                    color="warning"
                    size="small"
                  />
                )}
                {resumen.ecografias.requieren_seguimiento > 0 && (
                  <Chip
                    label={`${resumen.ecografias.requieren_seguimiento} Seguimiento`}
                    color="info"
                    size="small"
                  />
                )}
                {resumen.ecografias.total > 0 && 
                 resumen.ecografias.requieren_atencion === 0 && 
                 resumen.ecografias.requieren_seguimiento === 0 && (
                  <Chip
                    icon={<CheckIcon />}
                    label="Sin alertas"
                    color="success"
                    size="small"
                  />
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Pestañas con listados */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center', px: 2 }}>
          <Tabs value={tabActual} onChange={handleCambiarTab}>
            <Tab 
              label={`EKG (${resumen.ekg.total})`} 
              icon={<HeartIcon />}
              iconPosition="start"
            />
            <Tab 
              label={`EEG (${resumen.eeg.total})`}
              icon={<BrainIcon />}
              iconPosition="start"
            />
            <Tab 
              label={`Ecografías (${resumen.ecografias.total})`}
              icon={<UltrasoundIcon />}
              iconPosition="start"
            />
          </Tabs>
          <Tooltip title="Recargar">
            <IconButton onClick={cargarResumen} size="small">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>

        <TabPanel value={tabActual} index={0}>
          <ListaEstudiosEKG 
            pacienteId={pacienteId} 
            estudios={resumen.ekg.estudios}
            onActualizar={cargarResumen}
          />
        </TabPanel>

        <TabPanel value={tabActual} index={1}>
          <ListaEstudiosEEG 
            pacienteId={pacienteId}
            estudios={resumen.eeg.estudios}
            onActualizar={cargarResumen}
          />
        </TabPanel>

        <TabPanel value={tabActual} index={2}>
          <ListaEcografias 
            pacienteId={pacienteId}
            estudios={resumen.ecografias.estudios}
            onActualizar={cargarResumen}
          />
        </TabPanel>
      </Card>
    </Box>
  );
};

export default DashboardEstudiosEspeciales;
