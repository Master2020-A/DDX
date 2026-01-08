import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Alert,
  CircularProgress,
  Autocomplete,
  TextField,
  Button,
  Chip,
  List,
  ListItem,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import {
  IntegrationInstructions as IntegrationIcon,
  Person as PersonIcon,
  Assignment as AssignmentIcon,
  ReportGmailerrorred as ReportIcon,
  Visibility as VisibilityIcon,
} from '@mui/icons-material';

import { pacienteService } from '../../services/pacienteService';
import fhirService, {
  FhirPatient,
  FhirCarePlan,
  FhirDetectedIssue,
  FhirObservation,
} from '../../services/fhirService';

const PanelInteroperabilidadFHIR: React.FC = () => {
  const [pacientes, setPacientes] = useState<any[]>([]);
  const [pacienteSeleccionado, setPacienteSeleccionado] = useState<any | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [patientFhir, setPatientFhir] = useState<FhirPatient | null>(null);
  const [careplansFhir, setCareplansFhir] = useState<FhirCarePlan[]>([]);
  const [issuesFhir, setIssuesFhir] = useState<FhirDetectedIssue[]>([]);
  const [obsFhir, setObsFhir] = useState<FhirObservation[]>([]);

  // Diálogo genérico para ver JSON
  const [jsonOpen, setJsonOpen] = useState(false);
  const [jsonTitle, setJsonTitle] = useState('');
  const [jsonData, setJsonData] = useState<any>(null);
  const [jsonTab, setJsonTab] = useState(0);

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

  const handleCargarFHIR = async () => {
    if (!pacienteSeleccionado) {
      setError('Por favor selecciona un paciente');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const pacienteId = pacienteSeleccionado.id;

      const [
        patient,
        careplans,
        issues,
        observations,
      ] = await Promise.all([
        fhirService.getPatient(pacienteId),
        fhirService.getCarePlansByPatient(pacienteId),
        fhirService.getDetectedIssuesByPatient(pacienteId),
        fhirService.getObservationsByPatient(pacienteId),
      ]);

      setPatientFhir(patient);
      setCareplansFhir(careplans);
      setIssuesFhir(issues);
      setObsFhir(observations);
    } catch (err: any) {
      console.error('Error cargando datos FHIR:', err);
      setError(err.response?.data?.detail || 'Error al cargar datos FHIR del paciente');
    } finally {
      setLoading(false);
    }
  };

  const abrirJSON = (title: string, data: any) => {
    setJsonTitle(title);
    setJsonData(data);
    setJsonTab(0);
    setJsonOpen(true);
  };

  const formatDateTime = (dt?: string) =>
    dt ? new Date(dt).toLocaleString() : 'N/A';

  const getIssueSeverityColor = (sev?: string) => {
    switch ((sev || '').toLowerCase()) {
      case 'high':
        return 'error';
      case 'moderate':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom fontWeight="600">
        <IntegrationIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Interoperabilidad FHIR por Paciente
      </Typography>
      <Typography variant="body2" color="text.secondary" mb={3}>
        Visualiza la información del paciente en formato HL7 FHIR: datos demográficos (Patient),
        planes de tratamiento (CarePlan), interacciones medicamentosas (DetectedIssue) y
        anomalías detectadas (Observation).
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Selector de paciente y botón */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={8}>
              <Autocomplete
                options={pacientes}
                getOptionLabel={(option) =>
                  `${option.nombre_completo} - ${option.numero_expediente}`
                }
                value={pacienteSeleccionado}
                onChange={(_e, newValue) => setPacienteSeleccionado(newValue)}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Paciente *"
                    placeholder="Selecciona un paciente"
                    fullWidth
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Button
                variant="contained"
                fullWidth
                size="large"
                onClick={handleCargarFHIR}
                disabled={loading || !pacienteSeleccionado}
                startIcon={loading ? <CircularProgress size={20} /> : <IntegrationIcon />}
              >
                {loading ? 'Cargando datos FHIR...' : 'Cargar datos FHIR'}
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Panel de resultados */}
      {patientFhir && (
        <Grid container spacing={3}>
          {/* Patient */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="h6">
                    <PersonIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Paciente (FHIR Patient)
                  </Typography>
                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<VisibilityIcon />}
                    onClick={() => abrirJSON('Patient', patientFhir)}
                  >
                    Ver JSON
                  </Button>
                </Box>
                <Typography variant="subtitle1" gutterBottom>
                  {patientFhir.name && patientFhir.name.length > 0
                    ? patientFhir.name[0].text ||
                      `${patientFhir.name[0].given?.join(' ') || ''} ${patientFhir.name[0].family || ''}`
                    : 'Nombre no disponible'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  <strong>Sexo:</strong> {patientFhir.gender || 'N/A'}<br />
                  <strong>Fecha nacimiento:</strong> {patientFhir.birthDate || 'N/A'}
                </Typography>
                {patientFhir.identifier && patientFhir.identifier.length > 0 && (
                  <Box mt={1}>
                    <Typography variant="body2" fontWeight="600">
                      Identificadores:
                    </Typography>
                    {patientFhir.identifier.map((id, idx) => (
                      <Typography key={idx} variant="body2">
                        {id.system && `[${id.system}] `}{id.value}
                      </Typography>
                    ))}
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* CarePlans */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="h6">
                    <AssignmentIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Planes de Tratamiento (CarePlan)
                  </Typography>
                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<VisibilityIcon />}
                    disabled={careplansFhir.length === 0}
                    onClick={() => abrirJSON('CarePlan[]', careplansFhir)}
                  >
                    Ver JSON
                  </Button>
                </Box>

                {careplansFhir.length === 0 ? (
                  <Typography variant="body2" color="text.secondary">
                    No se encontraron CarePlan FHIR para este paciente.
                  </Typography>
                ) : (
                  <List dense>
                    {careplansFhir.map((cp) => (
                      <ListItem key={cp.id}>
                        <ListItemText
                          primary={cp.title || 'Plan de tratamiento'}
                          secondary={
                            <>
                              <Typography variant="caption" color="text.secondary">
                                Status: {cp.status || 'N/A'} | Intent: {cp.intent || 'N/A'}
                              </Typography>
                              <br />
                              <Typography variant="caption" color="text.secondary">
                                Creado: {cp.created ? new Date(cp.created).toLocaleString() : 'N/A'}
                              </Typography>
                            </>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* DetectedIssues */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="h6">
                    <ReportIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Interacciones Medicamentosas (DetectedIssue)
                  </Typography>
                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<VisibilityIcon />}
                    disabled={issuesFhir.length === 0}
                    onClick={() => abrirJSON('DetectedIssue[]', issuesFhir)}
                  >
                    Ver JSON
                  </Button>
                </Box>

                {issuesFhir.length === 0 ? (
                  <Typography variant="body2" color="text.secondary">
                    No se encontraron DetectedIssue FHIR (interacciones) para este paciente.
                  </Typography>
                ) : (
                  <List dense>
                    {issuesFhir.map((issue) => (
                      <ListItem key={issue.id} alignItems="flex-start">
                        <ListItemText
                          primary={
                            <Box display="flex" alignItems="center" gap={1}>
                              <Chip
                                size="small"
                                label={issue.severity || 'sin severidad'}
                                color={getIssueSeverityColor(issue.severity) as any}
                              />
                              <Typography variant="body2">
                                {issue.code?.text || 'Interacción medicamentosa'}
                              </Typography>
                            </Box>
                          }
                          secondary={
                            <>
                              <Typography variant="caption" color="text.secondary">
                                {issue.detail}
                              </Typography>
                              <br />
                              <Typography variant="caption" color="text.secondary">
                                Detectado: {formatDateTime(issue.identifiedDateTime)}
                              </Typography>
                            </>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Observations (Anomalías) */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="h6">
                    <ReportIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Anomalías Detectadas (Observation)
                  </Typography>
                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<VisibilityIcon />}
                    disabled={obsFhir.length === 0}
                    onClick={() => abrirJSON('Observation[]', obsFhir)}
                  >
                    Ver JSON
                  </Button>
                </Box>

                {obsFhir.length === 0 ? (
                  <Typography variant="body2" color="text.secondary">
                    No se encontraron Observation FHIR de anomalías para este paciente.
                  </Typography>
                ) : (
                  <TableContainer component={Paper} elevation={0} sx={{ border: 1, borderColor: 'divider' }}>
                    <Table size="small">
                      <TableHead>
                        <TableRow sx={{ bgcolor: 'grey.50' }}>
                          <TableCell><strong>Categoría</strong></TableCell>
                          <TableCell><strong>Código</strong></TableCell>
                          <TableCell><strong>Detalle</strong></TableCell>
                          <TableCell><strong>Fecha</strong></TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {obsFhir.map((obs) => (
                          <TableRow key={obs.id}>
                            <TableCell>
                              {obs.category && obs.category.length > 0
                                ? obs.category[0].text ||
                                  obs.category[0].coding?.[0]?.display ||
                                  obs.category[0].coding?.[0]?.code
                                : 'N/A'}
                            </TableCell>
                            <TableCell>
                              {obs.code?.text || 'Anomalía'}
                            </TableCell>
                            <TableCell>
                              {obs.note && obs.note.length > 0
                                ? obs.note[0].text?.slice(0, 80) + '...'
                                : 'N/A'}
                            </TableCell>
                            <TableCell>
                              {formatDateTime(obs.effectiveDateTime)}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Diálogo genérico para ver JSON */}
      <Dialog
        open={jsonOpen}
        onClose={() => setJsonOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>{jsonTitle}</DialogTitle>
        <DialogContent dividers>
          {jsonData ? (
            <>
              <Tabs
                value={jsonTab}
                onChange={(_e, v) => setJsonTab(v)}
                sx={{ mb: 2 }}
              >
                <Tab label="Resumen (no implementado)" />
                <Tab label="JSON" />
              </Tabs>

              {jsonTab === 1 && (
                <Box
                  component="pre"
                  sx={{
                    whiteSpace: 'pre-wrap',
                    wordWrap: 'break-word',
                    fontFamily: 'monospace',
                    fontSize: 12,
                    maxHeight: 500,
                    overflow: 'auto',
                  }}
                >
                  {JSON.stringify(jsonData, null, 2)}
                </Box>
              )}

              {jsonTab === 0 && (
                <Typography variant="body2" color="text.secondary">
                  Aquí podrías implementar un resumen específico para este tipo de recurso.
                </Typography>
              )}
            </>
          ) : (
            <Typography variant="body2" color="text.secondary">
              No hay datos JSON para mostrar.
            </Typography>
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default PanelInteroperabilidadFHIR;