import React, { useState, useEffect, useMemo } from 'react';

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
  Dialog,
  DialogTitle,
  DialogContent,
  Tabs,
  Tab,
  Divider,
} from '@mui/material';
import {
  MedicalServices as MedicalServicesIcon,
  LocalPharmacy as LocalPharmacyIcon,
  FitnessCenter as FitnessCenterIcon,
  Warning as WarningIcon,
  MenuBook as MenuBookIcon,
} from '@mui/icons-material';
import iaMedicaService, { RecomendacionTratamientoResponse } from '../../services/iaMedicaService';
import { pacienteService } from '../../services/pacienteService';
import fhirService, { FhirCarePlan, FhirMedicationRequest } from '../../services/fhirService';
import { prediagnosticoService, CIE10SearchResult } from '../../services/prediagnosticoService';

const RecomendacionesTratamiento: React.FC = () => {
  const [pacienteSeleccionado, setPacienteSeleccionado] = useState<any>(null);
  const [pacientes, setPacientes] = useState<any[]>([]);
  const [diagnostico, setDiagnostico] = useState('');
  const [codigoCie10, setCodigoCie10] = useState('');
  const [cieOptions, setCieOptions] = useState<CIE10SearchResult[]>([]);
  const [cieLoading, setCieLoading] = useState(false);
  const [cieQuery, setCieQuery] = useState('');

  const [sintomas, setSintomas] = useState('');
  const [comorbilidades, setComorbilidades] = useState('');
  const [generando, setGenerando] = useState(false);
  const [recomendacionActual, setRecomendacionActual] = useState<RecomendacionTratamientoResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Estado para CarePlan FHIR
  const [carePlanFhir, setCarePlanFhir] = useState<FhirCarePlan | null>(null);
  const [carePlanOpen, setCarePlanOpen] = useState(false);
  const [carePlanLoading, setCarePlanLoading] = useState(false);
  const [carePlanError, setCarePlanError] = useState<string | null>(null);
  const [carePlanTab, setCarePlanTab] = useState(0); // 0 = Resumen, 1 = JSON

  // Estado para MedicationRequest FHIR
  const [medReqsFhir, setMedReqsFhir] = useState<FhirMedicationRequest[]>([]);
  const [medReqOpen, setMedReqOpen] = useState(false);
  const [medReqLoading, setMedReqLoading] = useState(false);
  const [medReqError, setMedReqError] = useState<string | null>(null);

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

  // Buscar CIE-10 al escribir
  useEffect(() => {
    const fetchCie = async () => {
      if (!cieQuery || cieQuery.length < 2) {
        setCieOptions([]);
        return;
      }
      try {
        setCieLoading(true);
        const results = await prediagnosticoService.buscarCIE10(cieQuery, 15);
        setCieOptions(results);
      } catch (err) {
        console.error('Error al buscar CIE-10:', err);
      } finally {
        setCieLoading(false);
      }
    };

    const id = setTimeout(fetchCie, 250);
    return () => clearTimeout(id);
  }, [cieQuery]);

  const handleGenerarRecomendacion = async () => {
    if (!pacienteSeleccionado) {
      setError('Por favor selecciona un paciente');
      return;
    }

    if (!diagnostico.trim()) {
      setError('Por favor ingresa el diagnóstico principal');
      return;
    }

    try {
      setGenerando(true);
      setError(null);

      const request = {
        paciente_id: pacienteSeleccionado.id,
        diagnostico_principal: diagnostico.trim(),
        codigo_cie10: codigoCie10.trim() || undefined,
        sintomas: sintomas.trim() ? sintomas.split(',').map(s => s.trim()) : [],
        comorbilidades: comorbilidades.trim() ? comorbilidades.split(',').map(c => c.trim()) : [],
      };

      const recomendacion = await iaMedicaService.generarRecomendacionTratamiento(request);
      setRecomendacionActual(recomendacion);
    } catch (err: any) {
      console.error('Error al generar recomendación:', err);
      setError(err.response?.data?.detail || 'Error al generar recomendación de tratamiento');
    } finally {
      setGenerando(false);
    }
  };

  const handleVerCarePlanFhir = async () => {
    if (!recomendacionActual) return;

    try {
      setCarePlanLoading(true);
      setCarePlanError(null);
      setCarePlanFhir(null);
      setCarePlanTab(0);

      const data = await fhirService.getCarePlan(recomendacionActual.id);
      setCarePlanFhir(data);
      setCarePlanOpen(true);
    } catch (err: any) {
      console.error('Error al cargar CarePlan FHIR:', err);
      setCarePlanError(err.response?.data?.detail || 'Error al cargar CarePlan FHIR');
      setCarePlanOpen(true);
    } finally {
      setCarePlanLoading(false);
    }
  };

  const handleVerMedicationRequestsFhir = async () => {
    if (!pacienteSeleccionado) {
      setError('Selecciona un paciente para ver MedicationRequest FHIR');
      return;
    }

    try {
      setMedReqLoading(true);
      setMedReqError(null);
      setMedReqsFhir([]);

      const data = await fhirService.getMedicationRequestsByPatient(pacienteSeleccionado.id);
      setMedReqsFhir(data);
      setMedReqOpen(true);
    } catch (err: any) {
      console.error('Error al cargar MedicationRequest FHIR:', err);
      setMedReqError(err.response?.data?.detail || 'Error al cargar MedicationRequest FHIR');
      setMedReqOpen(true);
    } finally {
      setMedReqLoading(false);
    }
  };

  const downloadJson = (data: any, filename: string) => {
    try {
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: 'application/json',
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error al descargar JSON:', err);
    }
  };

  const copyJson = async (data: any) => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(data, null, 2));
      console.log('JSON copiado al portapapeles');
    } catch (err) {
      console.error('Error al copiar JSON al portapapeles:', err);
    }
  };

  const getPrioridadColor = (prioridad: string) => {
    switch (prioridad.toLowerCase()) {
      case 'inmediata':
        return 'error';
      case 'alta':
        return 'error';
      case 'media':
        return 'warning';
      case 'baja':
        return 'info';
      default:
        return 'default';
    }
  };

  const getNivelEvidenciaColor = (nivel: string) => {
    switch (nivel.toUpperCase()) {
      case 'A':
        return 'success';
      case 'B':
        return 'info';
      case 'C':
        return 'warning';
      default:
        return 'default';
    }
  };

  // Vista resumida del CarePlan
  const renderCarePlanResumen = (cp: FhirCarePlan) => {
    const activities = cp.activity || [];
    const notes = cp.note || [];

    return (
      <Box>
        <Typography variant="subtitle1" gutterBottom>
          <strong>Status:</strong> {cp.status || 'N/A'} &nbsp;|&nbsp;
          <strong>Intent:</strong> {cp.intent || 'N/A'}
        </Typography>
        {cp.title && (
          <Typography variant="h6" gutterBottom>
            {cp.title}
          </Typography>
        )}
        {cp.description && (
          <Typography variant="body2" gutterBottom>
            {cp.description}
          </Typography>
        )}
        {cp.created && (
          <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
            Creado: {new Date(cp.created).toLocaleString()}
          </Typography>
        )}

        <Divider sx={{ my: 2 }} />

        <Typography variant="subtitle1" gutterBottom>
          Actividades
        </Typography>
        {activities.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            No hay actividades definidas en el CarePlan.
          </Typography>
        ) : (
          <List dense>
            {activities.map((act: any, idx: number) => (
              <ListItem key={idx}>
                <ListItemText
                  primary={act.detail?.description || 'Actividad'}
                  secondary={act.detail?.kind ? `Tipo: ${act.detail.kind}` : undefined}
                />
              </ListItem>
            ))}
          </List>
        )}

        {notes.length > 0 && (
          <>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle1" gutterBottom>
              Notas / Evidencia
            </Typography>
            <List dense>
              {notes.map((n, idx) => (
                <ListItem key={idx}>
                  <ListItemText primary={n.text} />
                </ListItem>
              ))}
            </List>
          </>
        )}
      </Box>
    );
  };

  // 🔹 ESTE ES EL ÚNICO return PRINCIPAL DEL COMPONENTE
  return (
    <Box>
      <Typography variant="h5" gutterBottom fontWeight="600">
        <MedicalServicesIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Recomendaciones de Tratamiento
      </Typography>
      <Typography variant="body2" color="text.secondary" mb={3}>
        Genera recomendaciones de tratamiento personalizadas basadas en evidencia científica
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
            Generar Recomendación
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

            <Grid item xs={12} md={8}>
              <Autocomplete
                fullWidth
                options={cieOptions}
                loading={cieLoading}
                getOptionLabel={(option) =>
                  typeof option === 'string'
                    ? option
                    : `${option.codigo} - ${option.descripcion}`
                }
                filterOptions={(x) => x} // usamos resultados tal cual
                onInputChange={(_e, value) => setCieQuery(value)}
                onChange={(_e, value) => {
                  if (value && typeof value !== 'string') {
                    setDiagnostico(value.descripcion);
                    setCodigoCie10(value.codigo);
                  }
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Diagnóstico Principal *"
                    placeholder="Ej: Hipertensión Arterial o I10"
                    value={diagnostico}
                    onChange={(e) => {
                      setDiagnostico(e.target.value);
                      setCieQuery(e.target.value);
                    }}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Código CIE-10"
                placeholder="Ej: I10"
                value={codigoCie10}
                onChange={(e) => setCodigoCie10(e.target.value.toUpperCase())}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Síntomas"
                placeholder="Separados por comas: cefalea, mareo, visión borrosa"
                value={sintomas}
                onChange={(e) => setSintomas(e.target.value)}
                multiline
                rows={2}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Comorbilidades"
                placeholder="Separadas por comas: diabetes, obesidad"
                value={comorbilidades}
                onChange={(e) => setComorbilidades(e.target.value)}
                multiline
                rows={2}
              />
            </Grid>

            <Grid item xs={12}>
              <Button
                variant="contained"
                size="large"
                fullWidth
                startIcon={generando ? <CircularProgress size={20} /> : <MedicalServicesIcon />}
                onClick={handleGenerarRecomendacion}
                disabled={generando || !pacienteSeleccionado || !diagnostico.trim()}
                sx={{
                  background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #1976D2 30%, #00ACC1 90%)',
                  },
                }}
              >
                {generando ? 'Generando Recomendaciones...' : 'Generar Recomendaciones de Tratamiento'}
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Resultado */}
      {recomendacionActual && (
        <Box>
          {/* Header con Prioridad */}
          <Card sx={{ mb: 3, borderLeft: 4, borderColor: `${getPrioridadColor(recomendacionActual.prioridad)}.main` }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                <Typography variant="h6" fontWeight="600">
                  Plan de Tratamiento
                </Typography>
                <Box display="flex" alignItems="center" gap={1}>
                  <Chip
                    label={`Prioridad: ${recomendacionActual.prioridad.toUpperCase()}`}
                    color={getPrioridadColor(recomendacionActual.prioridad) as any}
                  />
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={handleVerCarePlanFhir}
                  >
                    Ver CarePlan FHIR
                  </Button>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={handleVerMedicationRequestsFhir}
                  >
                    Ver MedicationRequest FHIR
                  </Button>
                </Box>
              </Box>

              <Typography variant="subtitle1" gutterBottom>
                <strong>Diagnóstico:</strong> {recomendacionActual.diagnostico_principal}
                {recomendacionActual.codigo_cie10 && ` (${recomendacionActual.codigo_cie10})`}
              </Typography>
            </CardContent>
          </Card>

          {/* Medicamentos Sugeridos */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <LocalPharmacyIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Tratamiento Farmacológico
              </Typography>

              {recomendacionActual.medicamentos_sugeridos.length === 0 ? (
                <Alert severity="info">No se sugieren medicamentos para este caso</Alert>
              ) : (
                <TableContainer component={Paper} elevation={0} sx={{ border: 1, borderColor: 'divider' }}>
                  <Table>
                    <TableHead>
                      <TableRow sx={{ bgcolor: 'grey.50' }}>
                        <TableCell><strong>Medicamento</strong></TableCell>
                        <TableCell><strong>Dosis</strong></TableCell>
                        <TableCell><strong>Frecuencia</strong></TableCell>
                        <TableCell><strong>Duración</strong></TableCell>
                        <TableCell><strong>Vía</strong></TableCell>
                        <TableCell><strong>Evidencia</strong></TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {recomendacionActual.medicamentos_sugeridos.map((med, index) => (
                        <TableRow key={index}>
                          <TableCell>
                            <Typography variant="body2" fontWeight="600">
                              {med.nombre}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {med.razon}
                            </Typography>
                          </TableCell>
                          <TableCell>{med.dosis}</TableCell>
                          <TableCell>{med.frecuencia}</TableCell>
                          <TableCell>{med.duracion}</TableCell>
                          <TableCell>{med.via_administracion}</TableCell>
                          <TableCell>
                            <Chip
                              label={med.nivel_evidencia}
                              size="small"
                              color={getNivelEvidenciaColor(med.nivel_evidencia) as any}
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>

          {/* Terapias No Farmacológicas */}
          {recomendacionActual.terapias_no_farmacologicas.length > 0 && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <FitnessCenterIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Terapias No Farmacológicas
                </Typography>
                <List>
                  {recomendacionActual.terapias_no_farmacologicas.map((terapia, index) => (
                    <ListItem key={index}>
                      <ListItemText primary={`• ${terapia}`} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          )}

          {/* Cambios de Estilo de Vida */}
          {recomendacionActual.cambios_estilo_vida.length > 0 && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Cambios en Estilo de Vida
                </Typography>
                <Grid container spacing={1}>
                  {recomendacionActual.cambios_estilo_vida.map((cambio, index) => (
                    <Grid item xs={12} sm={6} key={index}>
                      <Paper elevation={0} sx={{ p: 2, border: 1, borderColor: 'success.main', borderRadius: 2 }}>
                        <Typography variant="body2">{cambio}</Typography>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          )}

          {/* Contraindicaciones y Precauciones */}
          <Grid container spacing={3} mb={3}>
            {recomendacionActual.contraindicaciones.length > 0 && (
              <Grid item xs={12} md={6}>
                <Card sx={{ borderLeft: 4, borderColor: 'error.main' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom color="error">
                      <WarningIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                      Contraindicaciones
                    </Typography>
                    <List dense>
                      {recomendacionActual.contraindicaciones.map((contra, index) => (
                        <ListItem key={index}>
                          <ListItemText primary={`• ${contra}`} />
                        </ListItem>
                      ))}
                    </List>
                  </CardContent>
                </Card>
              </Grid>
            )}

            {recomendacionActual.precauciones.length > 0 && (
              <Grid item xs={12} md={6}>
                <Card sx={{ borderLeft: 4, borderColor: 'warning.main' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom color="warning.main">
                      <WarningIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                      Precauciones
                    </Typography>
                    <List dense>
                      {recomendacionActual.precauciones.map((prec, index) => (
                        <ListItem key={index}>
                          <ListItemText primary={`• ${prec}`} />
                        </ListItem>
                      ))}
                    </List>
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>

          {/* Guías Clínicas */}
          {recomendacionActual.guias_clinicas.length > 0 && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <MenuBookIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Guías Clínicas de Referencia
                </Typography>
                <Box display="flex" flexWrap="wrap" gap={1}>
                  {recomendacionActual.guias_clinicas.map((guia, index) => (
                    <Chip key={index} label={guia} color="primary" variant="outlined" />
                  ))}
                </Box>
              </CardContent>
            </Card>
          )}

          <Box mt={2}>
            <Typography variant="caption" color="text.secondary">
              Generado: {new Date(recomendacionActual.created_at).toLocaleString()}
            </Typography>
          </Box>
        </Box>
      )}

      {/* Dialogo CarePlan FHIR */}
      <Dialog
        open={carePlanOpen}
        onClose={() => setCarePlanOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle
          sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
        >
          CarePlan FHIR
          {carePlanFhir && (
            <Box display="flex" gap={1}>
              <Button
                size="small"
                variant="outlined"
                onClick={() => copyJson(carePlanFhir)}
              >
                Copiar JSON
              </Button>
              <Button
                size="small"
                variant="outlined"
                onClick={() =>
                  downloadJson(carePlanFhir, `careplan_${carePlanFhir.id}.json`)
                }
              >
                Descargar JSON
              </Button>
            </Box>
          )}
        </DialogTitle>
        <DialogContent dividers>
          {carePlanLoading && (
            <Box display="flex" justifyContent="center" my={2}>
              <CircularProgress />
            </Box>
          )}

          {carePlanError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {carePlanError}
            </Alert>
          )}

          {carePlanFhir && (
            <>
              <Tabs
                value={carePlanTab}
                onChange={(_e, v) => setCarePlanTab(v)}
                sx={{ mb: 2 }}
              >
                <Tab label="Resumen" />
                <Tab label="JSON" />
              </Tabs>

              {carePlanTab === 0 && renderCarePlanResumen(carePlanFhir)}

              {carePlanTab === 1 && (
                <Box
                  component="pre"
                  sx={{
                    whiteSpace: 'pre-wrap',
                    wordWrap: 'break-word',
                    fontFamily: 'monospace',
                    fontSize: 12,
                    maxHeight: 400,
                    overflow: 'auto',
                  }}
                >
                  {JSON.stringify(carePlanFhir, null, 2)}
                </Box>
              )}
            </>
          )}

          {!carePlanLoading && !carePlanError && !carePlanFhir && (
            <Typography variant="body2" color="text.secondary">
              No hay datos FHIR para mostrar.
            </Typography>
          )}
        </DialogContent>
      </Dialog>

      {/* Dialogo MedicationRequest FHIR */}
      <Dialog
        open={medReqOpen}
        onClose={() => setMedReqOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle
          sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
        >
          MedicationRequest FHIR
          {medReqsFhir.length > 0 && (
            <Box display="flex" gap={1}>
              <Button
                size="small"
                variant="outlined"
                onClick={() => copyJson(medReqsFhir)}
              >
                Copiar JSON
              </Button>
              <Button
                size="small"
                variant="outlined"
                onClick={() =>
                  downloadJson(
                    medReqsFhir,
                    `medicationrequest_${pacienteSeleccionado?.numero_expediente || 'paciente'}.json`
                  )
                }
              >
                Descargar JSON
              </Button>
            </Box>
          )}
        </DialogTitle>
        <DialogContent dividers>
          {medReqLoading && (
            <Box display="flex" justifyContent="center" my={2}>
              <CircularProgress />
            </Box>
          )}

          {medReqError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {medReqError}
            </Alert>
          )}

          {!medReqLoading && !medReqError && medReqsFhir.length === 0 && (
            <Typography variant="body2" color="text.secondary">
              No se encontraron MedicationRequest FHIR para este paciente.
            </Typography>
          )}

          {medReqsFhir.length > 0 && (
            <TableContainer component={Paper} elevation={0} sx={{ border: 1, borderColor: 'divider' }}>
              <Table size="small">
                <TableHead>
                  <TableRow sx={{ bgcolor: 'grey.50' }}>
                    <TableCell><strong>Medicamento</strong></TableCell>
                    <TableCell><strong>Status</strong></TableCell>
                    <TableCell><strong>Intent</strong></TableCell>
                    <TableCell><strong>Dosificación</strong></TableCell>
                    <TableCell><strong>Fecha</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {medReqsFhir.map((mr) => (
                    <TableRow key={mr.id}>
                      <TableCell>{mr.medicationCodeableConcept?.text || 'N/A'}</TableCell>
                      <TableCell>{mr.status || 'N/A'}</TableCell>
                      <TableCell>{mr.intent || 'N/A'}</TableCell>
                      <TableCell>
                        {mr.dosageInstruction && mr.dosageInstruction.length > 0
                          ? mr.dosageInstruction[0].text
                          : 'N/A'}
                      </TableCell>
                      <TableCell>
                        {mr.authoredOn
                          ? new Date(mr.authoredOn).toLocaleString()
                          : 'N/A'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default RecomendacionesTratamiento;