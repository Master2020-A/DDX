/**
 * Página principal del módulo de Hospitalización
 * Incluye: Censo, Ingresos, Camas, Notas de Evolución, Indicaciones, Altas
 */
import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Tabs,
  Tab,
  Paper,
} from '@mui/material';
import {
  Hotel as HotelIcon,
  PersonAdd as PersonAddIcon,
  Description as DescriptionIcon,
  MedicalServices as MedicalServicesIcon,
  ExitToApp as ExitToAppIcon,
  Dashboard as DashboardIcon,
} from '@mui/icons-material';

// Componentes (los crearemos después)
import CensoHospitalario from '@/components/hospitalizacion/CensoHospitalario';
import ListaHospitalizaciones from '@/components/hospitalizacion/ListaHospitalizaciones';
import GestionCamas from '@/components/hospitalizacion/GestionCamas';
import NotasEvolucion from '@/components/hospitalizacion/NotasEvolucion';
import IndicacionesMedicas from '@/components/hospitalizacion/IndicacionesMedicas';
import NotasAlta from '@/components/hospitalizacion/NotasAlta';

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
      id={`hospitalizacion-tabpanel-${index}`}
      aria-labelledby={`hospitalizacion-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export default function Hospitalizacion() {
  const [tabActual, setTabActual] = useState(0);
  const [actualizarKey, setActualizarKey] = useState(0);

  const handleCambiarTab = (event: React.SyntheticEvent, newValue: number) => {
    setTabActual(newValue);
  };

  const handleActualizar = () => {
    setActualizarKey(prev => prev + 1);
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Encabezado */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
          🏥 Hospitalización
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Gestión completa de ingresos hospitalarios, camas, evolución y altas
        </Typography>
      </Box>

      {/* Pestañas */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={tabActual}
          onChange={handleCambiarTab}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            borderBottom: 1,
            borderColor: 'divider',
            '& .MuiTab-root': {
              minHeight: 64,
              textTransform: 'none',
              fontSize: '0.95rem',
            },
          }}
        >
          <Tab
            icon={<DashboardIcon />}
            label="Censo Hospitalario"
            iconPosition="start"
          />
          <Tab
            icon={<PersonAddIcon />}
            label="Ingresos"
            iconPosition="start"
          />
          <Tab
            icon={<HotelIcon />}
            label="Gestión de Camas"
            iconPosition="start"
          />
          <Tab
            icon={<DescriptionIcon />}
            label="Notas de Evolución"
            iconPosition="start"
          />
          <Tab
            icon={<MedicalServicesIcon />}
            label="Indicaciones Médicas"
            iconPosition="start"
          />
          <Tab
            icon={<ExitToAppIcon />}
            label="Notas de Alta"
            iconPosition="start"
          />
        </Tabs>
      </Paper>

      {/* Contenido de las pestañas */}
      <TabPanel value={tabActual} index={0}>
        <CensoHospitalario key={actualizarKey} onActualizar={handleActualizar} />
      </TabPanel>

      <TabPanel value={tabActual} index={1}>
        <ListaHospitalizaciones key={actualizarKey} onActualizar={handleActualizar} />
      </TabPanel>

      <TabPanel value={tabActual} index={2}>
        <GestionCamas key={actualizarKey} onActualizar={handleActualizar} />
      </TabPanel>

      <TabPanel value={tabActual} index={3}>
        <NotasEvolucion key={actualizarKey} onActualizar={handleActualizar} />
      </TabPanel>

      <TabPanel value={tabActual} index={4}>
        <IndicacionesMedicas key={actualizarKey} onActualizar={handleActualizar} />
      </TabPanel>

      <TabPanel value={tabActual} index={5}>
        <NotasAlta key={actualizarKey} onActualizar={handleActualizar} />
      </TabPanel>
    </Container>
  );
}
