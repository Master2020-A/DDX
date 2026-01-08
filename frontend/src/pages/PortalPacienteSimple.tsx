import { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Tabs,
  Tab,
  Paper,
  Card,
  CardContent,
  Button,
  Chip,
  Alert,
  CircularProgress,
  Grid,
} from '@mui/material';
import {
  CalendarMonth,
  Description,
  CreditCard,
  Message,
  Medication,
  Settings as SettingsIcon,
  Dashboard as DashboardIcon,
  Add,
} from '@mui/icons-material';
import portalPacienteService, {
  DashboardData,
  CitaPaciente,
  SolicitudEstudio,
  PagoServicio,
  MensajePacienteMedico,
  RecordatorioMedicamento,
  ConfiguracionPortal,
} from '@/services/portalPacienteService';

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
      id={`portal-tabpanel-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export default function PortalPaciente() {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [citas, setCitas] = useState<CitaPaciente[]>([]);
  const [solicitudes, setSolicitudes] = useState<SolicitudEstudio[]>([]);
  const [pagos, setPagos] = useState<PagoServicio[]>([]);
  const [mensajes, setMensajes] = useState<MensajePacienteMedico[]>([]);
  const [recordatorios, setRecordatorios] = useState<RecordatorioMedicamento[]>([]);
  const [configuracion, setConfiguracion] = useState<ConfiguracionPortal | null>(null);

  const pacienteId = '49bfb1e1-699c-4161-90cd-9162c226259c';

  useEffect(() => {
    cargarDatos();
  }, [activeTab]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const cargarDatos = async () => {
    setLoading(true);
    setError(null);
    try {
      if (activeTab === 0) {
        const data = await portalPacienteService.getDashboard(pacienteId);
        setDashboardData(data);
      } else if (activeTab === 1) {
        const data = await portalPacienteService.getCitas(pacienteId);
        setCitas(data);
      } else if (activeTab === 2) {
        const data = await portalPacienteService.getSolicitudesEstudios(pacienteId);
        setSolicitudes(data);
      } else if (activeTab === 3) {
        const data = await portalPacienteService.getPagos(pacienteId);
        setPagos(data);
      } else if (activeTab === 4) {
        const data = await portalPacienteService.getMensajes(pacienteId);
        setMensajes(data);
      } else if (activeTab === 5) {
        const data = await portalPacienteService.getRecordatorios(pacienteId, true);
        setRecordatorios(data);
      } else if (activeTab === 6) {
        const data = await portalPacienteService.getConfiguracion(pacienteId);
        setConfiguracion(data);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar los datos');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getEstadoChip = (estado: string) => {
    const colores: Record<string, 'success' | 'warning' | 'error' | 'default'> = {
      confirmada: 'success',
      solicitada: 'warning',
      cancelada: 'error',
      completada: 'success',
      pendiente: 'warning',
      aprobada: 'success',
      rechazada: 'error',
    };
    return <Chip label={estado.toUpperCase()} color={colores[estado] || 'default'} size="small" />;
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Portal del Paciente
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Gestiona tu salud desde un solo lugar
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ width: '100%' }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab icon={<DashboardIcon />} label="Dashboard" />
          <Tab icon={<CalendarMonth />} label="Citas" />
          <Tab icon={<Description />} label="Estudios" />
          <Tab icon={<CreditCard />} label="Pagos" />
          <Tab icon={<Message />} label="Mensajes" />
          <Tab icon={<Medication />} label="Medicamentos" />
          <Tab icon={<SettingsIcon />} label="Configuración" />
        </Tabs>

        {/* Dashboard */}
        <TabPanel value={activeTab} index={0}>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
              <CircularProgress />
            </Box>
          ) : dashboardData ? (
            <Box>
              <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={6} md={3}>
                  <Card>
                    <CardContent>
                      <Typography color="text.secondary" gutterBottom>
                        Citas Pendientes
                      </Typography>
                      <Typography variant="h4">
                        {dashboardData.citas_pendientes}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Card>
                    <CardContent>
                      <Typography color="text.secondary" gutterBottom>
                        Estudios Pendientes
                      </Typography>
                      <Typography variant="h4">
                        {dashboardData.solicitudes_pendientes}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Card>
                    <CardContent>
                      <Typography color="text.secondary" gutterBottom>
                        Mensajes No Leídos
                      </Typography>
                      <Typography variant="h4">
                        {dashboardData.mensajes_no_leidos}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Card>
                    <CardContent>
                      <Typography color="text.secondary" gutterBottom>
                        Recordatorios Activos
                      </Typography>
                      <Typography variant="h4">
                        {dashboardData.recordatorios_activos}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {dashboardData.proxima_cita && (
                <Card sx={{ mb: 3 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Próxima Cita
                    </Typography>
                    <Typography variant="body1">
                      {dashboardData.proxima_cita.especialidad_solicitada}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {dashboardData.proxima_cita.motivo_consulta}
                    </Typography>
                    <Box sx={{ mt: 2 }}>
                      {getEstadoChip(dashboardData.proxima_cita.estado)}
                    </Box>
                  </CardContent>
                </Card>
              )}
            </Box>
          ) : null}
        </TabPanel>

        {/* Citas */}
        <TabPanel value={activeTab} index={1}>
          <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="h6">Mis Citas</Typography>
            <Button variant="contained" startIcon={<Add />}>
              Nueva Cita
            </Button>
          </Box>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
              <CircularProgress />
            </Box>
          ) : (
            <Grid container spacing={2}>
              {citas.map((cita) => (
                <Grid item xs={12} key={cita.id}>
                  <Card>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="h6">
                          {cita.especialidad_solicitada || cita.tipo_cita}
                        </Typography>
                        {getEstadoChip(cita.estado)}
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        {cita.motivo_consulta}
                      </Typography>
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        Fecha: {new Date(cita.fecha_solicitada).toLocaleDateString('es-MX')}
                        {cita.hora_solicitada && ` - ${cita.hora_solicitada}`}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
              {citas.length === 0 && (
                <Grid item xs={12}>
                  <Typography align="center" color="text.secondary">
                    No tienes citas programadas
                  </Typography>
                </Grid>
              )}
            </Grid>
          )}
        </TabPanel>

        {/* Estudios */}
        <TabPanel value={activeTab} index={2}>
          <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="h6">Solicitudes de Estudios</Typography>
            <Button variant="contained" startIcon={<Add />}>
              Nueva Solicitud
            </Button>
          </Box>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
              <CircularProgress />
            </Box>
          ) : (
            <Grid container spacing={2}>
              {solicitudes.map((solicitud) => (
                <Grid item xs={12} key={solicitud.id}>
                  <Card>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="h6">{solicitud.nombre_estudio}</Typography>
                        {getEstadoChip(solicitud.estado)}
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        {solicitud.tipo_estudio.toUpperCase()}
                        {solicitud.prioridad && ` - Prioridad: ${solicitud.prioridad}`}
                      </Typography>
                      {solicitud.resultado_disponible && (
                        <Chip label="Resultado Disponible" color="success" size="small" sx={{ mt: 1 }} />
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
              {solicitudes.length === 0 && (
                <Grid item xs={12}>
                  <Typography align="center" color="text.secondary">
                    No tienes solicitudes de estudios
                  </Typography>
                </Grid>
              )}
            </Grid>
          )}
        </TabPanel>

        {/* Pagos */}
        <TabPanel value={activeTab} index={3}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Historial de Pagos
          </Typography>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
              <CircularProgress />
            </Box>
          ) : (
            <Grid container spacing={2}>
              {pagos.map((pago) => (
                <Grid item xs={12} key={pago.id}>
                  <Card>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="h6">{pago.concepto}</Typography>
                        {getEstadoChip(pago.estado)}
                      </Box>
                      <Typography variant="h5" color="primary">
                        ${pago.monto.toFixed(2)} {pago.moneda}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {pago.metodo_pago.replace('_', ' ').toUpperCase()}
                      </Typography>
                      {pago.referencia_pago && (
                        <Typography variant="caption" display="block">
                          Ref: {pago.referencia_pago}
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
              {pagos.length === 0 && (
                <Grid item xs={12}>
                  <Typography align="center" color="text.secondary">
                    No tienes pagos registrados
                  </Typography>
                </Grid>
              )}
            </Grid>
          )}
        </TabPanel>

        {/* Mensajes */}
        <TabPanel value={activeTab} index={4}>
          <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="h6">Mensajes con Médicos</Typography>
            <Button variant="contained" startIcon={<Add />}>
              Nuevo Mensaje
            </Button>
          </Box>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
              <CircularProgress />
            </Box>
          ) : (
            <Grid container spacing={2}>
              {mensajes.map((mensaje) => (
                <Grid item xs={12} key={mensaje.id}>
                  <Card sx={{ bgcolor: mensaje.leido ? 'background.paper' : 'action.hover' }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="h6">{mensaje.asunto || 'Sin asunto'}</Typography>
                        {!mensaje.leido && <Chip label="Nuevo" color="primary" size="small" />}
                      </Box>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {mensaje.remitente_tipo === 'medico' ? 'De: Médico' : 'De: Tú'}
                      </Typography>
                      <Typography variant="body2">{mensaje.mensaje}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
              {mensajes.length === 0 && (
                <Grid item xs={12}>
                  <Typography align="center" color="text.secondary">
                    No tienes mensajes
                  </Typography>
                </Grid>
              )}
            </Grid>
          )}
        </TabPanel>

        {/* Recordatorios */}
        <TabPanel value={activeTab} index={5}>
          <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="h6">Recordatorios de Medicamentos</Typography>
            <Button variant="contained" startIcon={<Add />}>
              Nuevo Recordatorio
            </Button>
          </Box>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
              <CircularProgress />
            </Box>
          ) : (
            <Grid container spacing={2}>
              {recordatorios.map((rec) => (
                <Grid item xs={12} key={rec.id}>
                  <Card>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="h6">{rec.nombre_medicamento}</Typography>
                        <Chip label={rec.activo ? 'Activo' : 'Inactivo'} color={rec.activo ? 'success' : 'default'} size="small" />
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        {rec.dosis} - {rec.via_administracion}
                      </Typography>
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        Frecuencia: {rec.frecuencia}
                      </Typography>
                      <Typography variant="body2">
                        Horarios: {rec.horarios.join(', ')}
                      </Typography>
                      <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                        Tomas registradas: {rec.tomas_registradas} | Omitidas: {rec.tomas_omitidas}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
              {recordatorios.length === 0 && (
                <Grid item xs={12}>
                  <Typography align="center" color="text.secondary">
                    No tienes recordatorios activos
                  </Typography>
                </Grid>
              )}
            </Grid>
          )}
        </TabPanel>

        {/* Configuración */}
        <TabPanel value={activeTab} index={6}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Configuración del Portal
          </Typography>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
              <CircularProgress />
            </Box>
          ) : configuracion ? (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Notificaciones
                    </Typography>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography>Email</Typography>
                        <Chip label={configuracion.notificaciones_email ? 'Activado' : 'Desactivado'} size="small" />
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography>SMS</Typography>
                        <Chip label={configuracion.notificaciones_sms ? 'Activado' : 'Desactivado'} size="small" />
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography>Push</Typography>
                        <Chip label={configuracion.notificaciones_push ? 'Activado' : 'Desactivado'} size="small" />
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Preferencias
                    </Typography>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography>Idioma</Typography>
                        <Typography color="text.secondary">{configuracion.idioma}</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography>Tema</Typography>
                        <Typography color="text.secondary">{configuracion.tema}</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography>Zona Horaria</Typography>
                        <Typography color="text.secondary">{configuracion.zona_horaria}</Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          ) : null}
        </TabPanel>
      </Paper>
    </Container>
  );
}
