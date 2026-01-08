import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Alert,
  AlertTitle,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  CircularProgress,
  Tabs,
  Tab
} from '@mui/material';
import { FileText, Plus, RefreshCw, Activity, Beaker } from 'lucide-react';
import axios from 'axios';

interface Observation {
  id: string;
  status: string;
  category: string[];
  code: any;
  subject_id: string;
  effective_datetime: string;
  value_quantity?: any;
  interpretation?: any[];
  created_at: string;
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8612';

const FHIRObservations: React.FC = () => {
  const { pacienteId } = useParams<{ pacienteId: string }>();
  const [observations, setObservations] = useState<Observation[]>([]);
  const [loading, setLoading] = useState(false);
  const [openDialog, setOpenDialog] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  
  // Form state
  const [formData, setFormData] = useState({
    categoria: 'vital-signs',
    codigo: 'frecuencia_cardiaca',
    valor: '',
    unidad: 'bpm'
  });

  useEffect(() => {
    if (pacienteId) {
      loadObservations();
    }
  }, [pacienteId]);

  const loadObservations = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_URL}/api/fhir/observations/`,
        {
          params: { patient: pacienteId, limit: 50 },
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setObservations(response.data);
    } catch (error) {
      console.error('Error cargando observaciones:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateObservation = async () => {
    try {
      const token = localStorage.getItem('token');
      const endpoint = formData.categoria === 'vital-signs' 
        ? '/api/fhir/observations/from-vital-sign'
        : '/api/fhir/observations/from-lab-parameter';
      
      const data = {
        nombre_parametro: formData.codigo,
        valor: parseFloat(formData.valor),
        unidad: formData.unidad,
        paciente_id: pacienteId,
        fecha: new Date().toISOString()
      };

      await axios.post(`${API_URL}${endpoint}`, data, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setOpenDialog(false);
      loadObservations();
      setFormData({ categoria: 'vital-signs', codigo: 'frecuencia_cardiaca', valor: '', unidad: 'bpm' });
    } catch (error) {
      console.error('Error creando observación:', error);
      alert('Error al crear la observación');
    }
  };

  const getInterpretationColor = (interpretation?: any[]) => {
    if (!interpretation || interpretation.length === 0) return 'default';
    const code = interpretation[0]?.coding?.[0]?.code;
    switch (code) {
      case 'N': return 'success';
      case 'L': return 'info';
      case 'H': return 'warning';
      case 'AA': return 'error';
      default: return 'default';
    }
  };

  const getInterpretationLabel = (interpretation?: any[]) => {
    if (!interpretation || interpretation.length === 0) return 'N/A';
    return interpretation[0]?.coding?.[0]?.display || 'N/A';
  };

  const stats = {
    total: observations.length,
    vitalsCount: observations.filter(o => o.category.includes('vital-signs')).length,
    labsCount: observations.filter(o => o.category.includes('laboratory')).length,
    normal: observations.filter(o => o.interpretation?.some(i => i.coding?.some(c => c.code === 'N'))).length
  };

  const filteredObservations = tabValue === 0 
    ? observations
    : tabValue === 1
    ? observations.filter(o => o.category.includes('vital-signs'))
    : observations.filter(o => o.category.includes('laboratory'));

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Encabezado */}
      <Box mb={4}>
        <Box display="flex" alignItems="center" gap={2} mb={1}>
          <FileText size={32} color="#9333ea" />
          <Typography variant="h4" component="h1" fontWeight="bold">
            Observaciones FHIR
          </Typography>
        </Box>
        <Typography variant="body2" color="text.secondary">
          Recursos de observación según estándar HL7 FHIR R4
        </Typography>
      </Box>

      {/* Botones de acción */}
      <Box display="flex" gap={2} mb={4}>
        <Button
          variant="contained"
          startIcon={<Plus size={20} />}
          onClick={() => setOpenDialog(true)}
          sx={{ bgcolor: '#9333ea', '&:hover': { bgcolor: '#7e22ce' } }}
        >
          Nueva Observación
        </Button>
        <Button
          variant="outlined"
          startIcon={<RefreshCw size={20} />}
          onClick={loadObservations}
          disabled={loading}
        >
          Actualizar
        </Button>
      </Box>

      {/* Estadísticas */}
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="caption" color="text.secondary" gutterBottom>
                Total Observaciones
              </Typography>
              <Typography variant="h4" fontWeight="bold" color="primary">
                {stats.total}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Signos vitales y laboratorio
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="caption" color="text.secondary" gutterBottom>
                Signos Vitales
              </Typography>
              <Typography variant="h4" fontWeight="bold" color="info.main">
                {stats.vitalsCount}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Presión, FC, temperatura
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="caption" color="text.secondary" gutterBottom>
                Laboratorio
              </Typography>
              <Typography variant="h4" fontWeight="bold" sx={{ color: '#9333ea' }}>
                {stats.labsCount}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Resultados de análisis
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="caption" color="text.secondary" gutterBottom>
                Normales
              </Typography>
              <Typography variant="h4" fontWeight="bold" color="success.main">
                {stats.normal}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Valores en rango
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Pestañas y tabla de observaciones */}
      <Box mt={4}>
        <Card>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
              <Tab icon={<FileText size={18} />} label={`Todas (${stats.total})`} />
              <Tab icon={<Activity size={18} />} label={`Signos Vitales (${stats.vitalsCount})`} />
              <Tab icon={<Beaker size={18} />} label={`Laboratorio (${stats.labsCount})`} />
            </Tabs>
          </Box>
          
          <CardContent>
            {loading ? (
              <Box display="flex" justifyContent="center" py={4}>
                <CircularProgress />
              </Box>
            ) : filteredObservations.length === 0 ? (
              <Alert severity="info">
                No hay observaciones registradas. Haz clic en "Nueva Observación" para agregar una.
              </Alert>
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Fecha</TableCell>
                      <TableCell>Tipo</TableCell>
                      <TableCell>Código</TableCell>
                      <TableCell>Valor</TableCell>
                      <TableCell>Interpretación</TableCell>
                      <TableCell>Estado</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredObservations.map((obs) => (
                      <TableRow key={obs.id} hover>
                        <TableCell>
                          {new Date(obs.effective_datetime).toLocaleString('es-ES', {
                            day: '2-digit',
                            month: '2-digit',
                            year: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={obs.category[0] === 'vital-signs' ? 'Signos Vitales' : 'Laboratorio'}
                            size="small"
                            color={obs.category[0] === 'vital-signs' ? 'info' : 'secondary'}
                          />
                        </TableCell>
                        <TableCell>{obs.code?.text || 'N/A'}</TableCell>
                        <TableCell>
                          {obs.value_quantity ? 
                            `${obs.value_quantity.value} ${obs.value_quantity.unit || ''}` : 
                            'N/A'
                          }
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={getInterpretationLabel(obs.interpretation)}
                            size="small"
                            color={getInterpretationColor(obs.interpretation)}
                          />
                        </TableCell>
                        <TableCell>
                          <Chip label={obs.status} size="small" variant="outlined" />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>
      </Box>

      {/* Diálogo para crear observación */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Nueva Observación FHIR</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <FormControl fullWidth>
              <InputLabel>Categoría</InputLabel>
              <Select
                value={formData.categoria}
                label="Categoría"
                onChange={(e) => setFormData({ ...formData, categoria: e.target.value })}
              >
                <MenuItem value="vital-signs">Signos Vitales</MenuItem>
                <MenuItem value="laboratory">Laboratorio</MenuItem>
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel>Parámetro</InputLabel>
              <Select
                value={formData.codigo}
                label="Parámetro"
                onChange={(e) => {
                  const param = e.target.value;
                  let unidad = 'bpm';
                  if (param === 'temperatura') unidad = '°C';
                  if (param === 'presion_arterial_sistolica') unidad = 'mmHg';
                  if (param === 'glucosa') unidad = 'mg/dL';
                  if (param === 'hemoglobina') unidad = 'g/dL';
                  setFormData({ ...formData, codigo: param, unidad });
                }}
              >
                {formData.categoria === 'vital-signs' ? (
                  <>
                    <MenuItem value="frecuencia_cardiaca">Frecuencia Cardíaca</MenuItem>
                    <MenuItem value="frecuencia_respiratoria">Frecuencia Respiratoria</MenuItem>
                    <MenuItem value="temperatura">Temperatura</MenuItem>
                    <MenuItem value="saturacion_oxigeno">Saturación de Oxígeno</MenuItem>
                    <MenuItem value="presion_arterial_sistolica">Presión Arterial Sistólica</MenuItem>
                  </>
                ) : (
                  <>
                    <MenuItem value="glucosa">Glucosa</MenuItem>
                    <MenuItem value="hemoglobina">Hemoglobina</MenuItem>
                    <MenuItem value="creatinina">Creatinina</MenuItem>
                    <MenuItem value="colesterol">Colesterol Total</MenuItem>
                  </>
                )}
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Valor"
              type="number"
              value={formData.valor}
              onChange={(e) => setFormData({ ...formData, valor: e.target.value })}
            />

            <TextField
              fullWidth
              label="Unidad"
              value={formData.unidad}
              onChange={(e) => setFormData({ ...formData, unidad: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancelar</Button>
          <Button 
            onClick={handleCreateObservation} 
            variant="contained"
            disabled={!formData.valor}
            sx={{ bgcolor: '#9333ea', '&:hover': { bgcolor: '#7e22ce' } }}
          >
            Crear Observación
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default FHIRObservations;
