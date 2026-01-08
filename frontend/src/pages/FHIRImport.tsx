import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
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
  Chip,
  CircularProgress,
  Alert,
  Stepper,
  Step,
  StepLabel,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Divider
} from '@mui/material';
import { 
  Download, 
  Server, 
  Search, 
  CheckCircle, 
  AlertCircle,
  Database,
  User
} from 'lucide-react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8612';

interface FHIRServer {
  name: string;
  url: string;
  description: string;
}

interface FHIRPatient {
  id: string;
  name: string;
  birthDate?: string;
  gender?: string;
  identifier?: any[];
}

interface ImportedCondition {
  id: string;
  diagnosis: string;
  code?: string;
  code_system?: string;
  clinical_status: string;
  verification_status: string;
  severity?: string;
  onset_date?: string;
  recorded_date?: string;
  notes: string[];
  fhir_id?: string;
  source?: string;
}

const FHIRImport: React.FC = () => {
  const { pacienteId } = useParams<{ pacienteId: string }>();
  
  // Estados
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [publicServers, setPublicServers] = useState<Record<string, FHIRServer>>({});
  const [selectedServer, setSelectedServer] = useState('');
  const [customServerUrl, setCustomServerUrl] = useState('');
  const [authToken, setAuthToken] = useState('');
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
  
  // Búsqueda de pacientes
  const [searchName, setSearchName] = useState('');
  const [searchIdentifier, setSearchIdentifier] = useState('');
  const [fhirPatients, setFhirPatients] = useState<FHIRPatient[]>([]);
  const [selectedFhirPatient, setSelectedFhirPatient] = useState<FHIRPatient | null>(null);
  
  // Diagnósticos importados
  const [importedConditions, setImportedConditions] = useState<ImportedCondition[]>([]);
  const [viewConditionsDialog, setViewConditionsDialog] = useState(false);

  const steps = ['Seleccionar Servidor FHIR', 'Buscar Paciente', 'Importar Diagnósticos'];

  useEffect(() => {
    loadPublicServers();
    if (pacienteId) {
      loadImportedConditions();
    }
  }, [pacienteId]);

  const loadPublicServers = async () => {
    try {
      // Los servidores públicos no requieren autenticación
      const response = await axios.get(`${API_URL}/api/fhir/import/servers/public`);
      setPublicServers(response.data);
    } catch (error: any) {
      console.error('Error cargando servidores:', error);
    }
  };

  const loadImportedConditions = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_URL}/api/fhir/import/conditions/patient/${pacienteId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setImportedConditions(response.data.conditions || []);
    } catch (error) {
      console.error('Error cargando diagnósticos:', error);
    }
  };

  const testConnection = async () => {
    setConnectionStatus('testing');
    const serverUrl = selectedServer === 'custom' ? customServerUrl : publicServers[selectedServer]?.url;
    
    try {
      const token = localStorage.getItem('token');
      
      const response = await axios.post(
        `${API_URL}/api/fhir/import/test-connection`,
        { url: serverUrl, auth_token: authToken || null },
        { headers: token ? { Authorization: `Bearer ${token}` } : {} }
      );
      
      if (response.data.success) {
        setConnectionStatus('success');
        setTimeout(() => setActiveStep(1), 1000);
      } else {
        setConnectionStatus('error');
      }
    } catch (error: any) {
      console.error('Error probando conexión:', error);
      setConnectionStatus('error');
    }
  };

  const searchFhirPatients = async () => {
    setLoading(true);
    const serverUrl = selectedServer === 'custom' ? customServerUrl : publicServers[selectedServer]?.url;
    
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_URL}/api/fhir/import/search-patients`,
        {
          fhir_server_url: serverUrl,
          name: searchName || null,
          identifier: searchIdentifier || null,
          auth_token: authToken || null
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setFhirPatients(response.data.patients || []);
    } catch (error) {
      console.error('Error buscando pacientes:', error);
      alert('Error al buscar pacientes en el servidor FHIR');
    } finally {
      setLoading(false);
    }
  };

  const importConditions = async () => {
    if (!selectedFhirPatient || !pacienteId) return;
    
    setLoading(true);
    const serverUrl = selectedServer === 'custom' ? customServerUrl : publicServers[selectedServer]?.url;
    
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_URL}/api/fhir/import/import/conditions`,
        {
          fhir_server_url: serverUrl,
          fhir_patient_id: selectedFhirPatient.id,
          local_patient_id: pacienteId,
          auth_token: authToken || null
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        alert(`✅ Se importaron ${response.data.total_imported} diagnósticos correctamente`);
        setActiveStep(0);
        setSelectedFhirPatient(null);
        loadImportedConditions();
      }
    } catch (error) {
      console.error('Error importando diagnósticos:', error);
      alert('Error al importar diagnósticos desde FHIR');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, any> = {
      'active': 'error',
      'resolved': 'success',
      'inactive': 'default',
      'confirmed': 'success',
      'provisional': 'warning'
    };
    return colors[status] || 'default';
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Encabezado */}
      <Box mb={4}>
        <Box display="flex" alignItems="center" gap={2} mb={1}>
          <Download size={32} color="#9333ea" />
          <Typography variant="h4" component="h1" fontWeight="bold">
            Importar desde HL7 FHIR
          </Typography>
        </Box>
        <Typography variant="body2" color="text.secondary">
          Importar diagnósticos y datos clínicos desde servidores FHIR externos
        </Typography>
      </Box>

      {/* Botón para ver diagnósticos importados */}
      <Box mb={4}>
        <Button
          variant="outlined"
          startIcon={<Database size={20} />}
          onClick={() => setViewConditionsDialog(true)}
        >
          Ver Diagnósticos Importados ({importedConditions.length})
        </Button>
      </Box>

      {/* Stepper */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Stepper activeStep={activeStep}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
        </CardContent>
      </Card>

      {/* Paso 1: Seleccionar Servidor */}
      {activeStep === 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <Server size={20} style={{ verticalAlign: 'middle', marginRight: 8 }} />
              Configurar Conexión FHIR
            </Typography>
            
            <Box mt={3}>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Servidor FHIR</InputLabel>
                <Select
                  value={selectedServer}
                  label="Servidor FHIR"
                  onChange={(e) => setSelectedServer(e.target.value)}
                >
                  <MenuItem value="">Seleccionar...</MenuItem>
                  {Object.entries(publicServers).map(([key, server]) => (
                    <MenuItem key={key} value={key}>
                      {server.name}
                    </MenuItem>
                  ))}
                  <MenuItem value="custom">🔧 Servidor Personalizado</MenuItem>
                </Select>
              </FormControl>

              {selectedServer && selectedServer !== 'custom' && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  <strong>{publicServers[selectedServer]?.name}</strong><br />
                  {publicServers[selectedServer]?.description}<br />
                  URL: <code>{publicServers[selectedServer]?.url}</code>
                </Alert>
              )}

              {selectedServer === 'custom' && (
                <TextField
                  fullWidth
                  label="URL del Servidor FHIR"
                  placeholder="https://servidor-fhir.com/fhir"
                  value={customServerUrl}
                  onChange={(e) => setCustomServerUrl(e.target.value)}
                  sx={{ mb: 2 }}
                />
              )}

              <TextField
                fullWidth
                label="Token de Autenticación (Opcional)"
                placeholder="Bearer token..."
                value={authToken}
                onChange={(e) => setAuthToken(e.target.value)}
                sx={{ mb: 3 }}
              />

              <Box display="flex" gap={2}>
                <Button
                  variant="contained"
                  onClick={testConnection}
                  disabled={!selectedServer || connectionStatus === 'testing'}
                  sx={{ bgcolor: '#9333ea', '&:hover': { bgcolor: '#7e22ce' } }}
                >
                  {connectionStatus === 'testing' ? (
                    <>
                      <CircularProgress size={20} sx={{ mr: 1 }} />
                      Probando Conexión...
                    </>
                  ) : (
                    'Probar Conexión'
                  )}
                </Button>

                {connectionStatus === 'success' && (
                  <Chip icon={<CheckCircle size={16} />} label="Conexión Exitosa" color="success" />
                )}
                {connectionStatus === 'error' && (
                  <Chip icon={<AlertCircle size={16} />} label="Error de Conexión" color="error" />
                )}
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Paso 2: Buscar Paciente */}
      {activeStep === 1 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <Search size={20} style={{ verticalAlign: 'middle', marginRight: 8 }} />
              Buscar Paciente en FHIR
            </Typography>

            <Grid container spacing={2} sx={{ mt: 2, mb: 3 }}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Nombre del Paciente"
                  value={searchName}
                  onChange={(e) => setSearchName(e.target.value)}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Identificador (DNI, Pasaporte, etc.)"
                  value={searchIdentifier}
                  onChange={(e) => setSearchIdentifier(e.target.value)}
                />
              </Grid>
            </Grid>

            <Box display="flex" gap={2} mb={3}>
              <Button
                variant="contained"
                startIcon={<Search size={20} />}
                onClick={searchFhirPatients}
                disabled={loading || (!searchName && !searchIdentifier)}
                sx={{ bgcolor: '#9333ea', '&:hover': { bgcolor: '#7e22ce' } }}
              >
                Buscar
              </Button>
              <Button variant="outlined" onClick={() => setActiveStep(0)}>
                Volver
              </Button>
            </Box>

            {loading && (
              <Box display="flex" justifyContent="center" py={4}>
                <CircularProgress />
              </Box>
            )}

            {!loading && fhirPatients.length > 0 && (
              <>
                <Typography variant="subtitle2" color="text.secondary" mb={2}>
                  {fhirPatients.length} paciente(s) encontrado(s)
                </Typography>
                <List>
                  {fhirPatients.map((patient) => (
                    <React.Fragment key={patient.id}>
                      <ListItemButton
                        selected={selectedFhirPatient?.id === patient.id}
                        onClick={() => setSelectedFhirPatient(patient)}
                      >
                        <ListItemText
                          primary={patient.name}
                          secondary={
                            <>
                              ID: {patient.id} | 
                              {patient.birthDate && ` Fecha Nac: ${patient.birthDate} |`}
                              {patient.gender && ` Género: ${patient.gender}`}
                            </>
                          }
                        />
                      </ListItemButton>
                      <Divider />
                    </React.Fragment>
                  ))}
                </List>

                {selectedFhirPatient && (
                  <Box mt={3}>
                    <Button
                      variant="contained"
                      onClick={() => setActiveStep(2)}
                      sx={{ bgcolor: '#9333ea', '&:hover': { bgcolor: '#7e22ce' } }}
                    >
                      Continuar con {selectedFhirPatient.name}
                    </Button>
                  </Box>
                )}
              </>
            )}

            {!loading && fhirPatients.length === 0 && searchName && (
              <Alert severity="info">
                No se encontraron pacientes con los criterios de búsqueda
              </Alert>
            )}
          </CardContent>
        </Card>
      )}

      {/* Paso 3: Importar Diagnósticos */}
      {activeStep === 2 && selectedFhirPatient && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <Download size={20} style={{ verticalAlign: 'middle', marginRight: 8 }} />
              Importar Diagnósticos
            </Typography>

            <Alert severity="info" sx={{ mt: 2, mb: 3 }}>
              <strong>Paciente FHIR seleccionado:</strong><br />
              {selectedFhirPatient.name} (ID: {selectedFhirPatient.id})
            </Alert>

            <Typography variant="body2" paragraph>
              Se importarán todos los diagnósticos (Condition) del paciente desde el servidor FHIR
              al paciente local seleccionado.
            </Typography>

            <Box display="flex" gap={2}>
              <Button
                variant="contained"
                startIcon={<Download size={20} />}
                onClick={importConditions}
                disabled={loading}
                sx={{ bgcolor: '#9333ea', '&:hover': { bgcolor: '#7e22ce' } }}
              >
                {loading ? 'Importando...' : 'Importar Diagnósticos'}
              </Button>
              <Button variant="outlined" onClick={() => setActiveStep(1)}>
                Volver
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Diálogo de Diagnósticos Importados */}
      <Dialog
        open={viewConditionsDialog}
        onClose={() => setViewConditionsDialog(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          Diagnósticos Importados desde FHIR
        </DialogTitle>
        <DialogContent>
          {importedConditions.length === 0 ? (
            <Alert severity="info">
              No hay diagnósticos importados para este paciente
            </Alert>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Diagnóstico</TableCell>
                    <TableCell>Código</TableCell>
                    <TableCell>Estado</TableCell>
                    <TableCell>Verificación</TableCell>
                    <TableCell>Fecha Inicio</TableCell>
                    <TableCell>Origen</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {importedConditions.map((condition) => (
                    <TableRow key={condition.id}>
                      <TableCell>{condition.diagnosis}</TableCell>
                      <TableCell>
                        {condition.code && (
                          <Typography variant="caption">
                            {condition.code}
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={condition.clinical_status}
                          size="small"
                          color={getStatusColor(condition.clinical_status)}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={condition.verification_status}
                          size="small"
                          variant="outlined"
                          color={getStatusColor(condition.verification_status)}
                        />
                      </TableCell>
                      <TableCell>
                        {condition.onset_date ? 
                          new Date(condition.onset_date).toLocaleDateString('es-ES') : 
                          'N/A'
                        }
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption" color="text.secondary">
                          FHIR
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewConditionsDialog(false)}>Cerrar</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default FHIRImport;
