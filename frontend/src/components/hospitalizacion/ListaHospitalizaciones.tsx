/**
 * Componente para listar y gestionar hospitalizaciones
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  Chip,
  Alert,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { hospitalizacionService } from '@/services/hospitalizacionService';
import { pacienteService } from '@/services/pacienteService';
import type { Hospitalizacion } from '@/types/hospitalizacion';
import type { Paciente } from '@/types/paciente';

interface Props {
  onActualizar?: () => void;
}

export default function ListaHospitalizaciones({ onActualizar }: Props) {
  const [hospitalizaciones, setHospitalizaciones] = useState<Hospitalizacion[]>([]);
  const [cargando, setCargando] = useState(true);
  const [dialogoAbierto, setDialogoAbierto] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pacientes, setPacientes] = useState<Paciente[]>([]);
  const [cargandoPacientes, setCargandoPacientes] = useState(false);
  const [busquedaPaciente, setBusquedaPaciente] = useState('');
  const [formData, setFormData] = useState({
    paciente_id: '',
    motivo_ingreso: '',
    diagnostico_ingreso: '',
    area_hospitalizacion: '',
    prioridad: 'normal',
    tipo_ingreso: 'programado'
  });

  const cargarHospitalizaciones = async () => {
    try {
      setCargando(true);
      const data = await hospitalizacionService.listar({ estado: 'activo', limit: 100 });
      setHospitalizaciones(data);
    } catch (err) {
      console.error('Error:', err);
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarHospitalizaciones();
  }, []);

  const handleAbrirDialogo = async () => {
    setDialogoAbierto(true);
    setError(null);
    await cargarPacientes();
  };

  const cargarPacientes = async () => {
    try {
      setCargandoPacientes(true);
      const data = await pacienteService.listar({ limit: 100 });
      setPacientes(data);
    } catch (err) {
      console.error('Error cargando pacientes:', err);
    } finally {
      setCargandoPacientes(false);
    }
  };

  const handleCerrarDialogo = () => {
    setDialogoAbierto(false);
    setBusquedaPaciente('');
    setFormData({
      paciente_id: '',
      motivo_ingreso: '',
      diagnostico_ingreso: '',
      area_hospitalizacion: '',
      prioridad: 'normal',
      tipo_ingreso: 'programado'
    });
  };

  const handleGuardar = async () => {
    try {
      setGuardando(true);
      setError(null);
      await hospitalizacionService.crear(formData);
      await cargarHospitalizaciones();
      handleCerrarDialogo();
      if (onActualizar) onActualizar();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al crear el ingreso');
    } finally {
      setGuardando(false);
    }
  };

  if (cargando) {
    return <Box display="flex" justifyContent="center" p={4}><CircularProgress /></Box>;
  }

  return (
    <>
      <Card>
        <Box p={2}>
          <Button 
            variant="contained" 
            startIcon={<AddIcon />}
            onClick={handleAbrirDialogo}
          >
            Nuevo Ingreso
          </Button>
        </Box>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Fecha Ingreso</TableCell>
              <TableCell>Área</TableCell>
              <TableCell>Cama</TableCell>
              <TableCell>Diagnóstico</TableCell>
              <TableCell>Estado</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {hospitalizaciones.map((hosp) => (
              <TableRow key={hosp.id}>
                <TableCell>{new Date(hosp.fecha_ingreso).toLocaleDateString()}</TableCell>
                <TableCell>{hosp.area_hospitalizacion || 'N/A'}</TableCell>
                <TableCell>{hosp.numero_cama || 'Sin asignar'}</TableCell>
                <TableCell>{hosp.diagnostico_ingreso}</TableCell>
                <TableCell><Chip label={hosp.estado} size="small" /></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Card>

    <Dialog open={dialogoAbierto} onClose={handleCerrarDialogo} maxWidth="md" fullWidth>
      <DialogTitle>Nuevo Ingreso Hospitalario</DialogTitle>
      <DialogContent>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              select
              label="Paciente"
              value={formData.paciente_id}
              onChange={(e) => setFormData({ ...formData, paciente_id: e.target.value })}
              required
              disabled={cargandoPacientes}
              helperText={cargandoPacientes ? 'Cargando pacientes...' : 'Selecciona el paciente a hospitalizar'}
            >
              {pacientes.map((paciente) => (
                <MenuItem key={paciente.id} value={paciente.id}>
                  {paciente.nombre_completo} - {paciente.numero_expediente}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              select
              label="Área de Hospitalización"
              value={formData.area_hospitalizacion}
              onChange={(e) => setFormData({ ...formData, area_hospitalizacion: e.target.value })}
            >
              <MenuItem value="Urgencias">Urgencias</MenuItem>
              <MenuItem value="Medicina Interna">Medicina Interna</MenuItem>
              <MenuItem value="Cirugia">Cirugía</MenuItem>
              <MenuItem value="Pediatria">Pediatría</MenuItem>
              <MenuItem value="UCI">UCI</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              select
              label="Prioridad"
              value={formData.prioridad}
              onChange={(e) => setFormData({ ...formData, prioridad: e.target.value })}
            >
              <MenuItem value="normal">Normal</MenuItem>
              <MenuItem value="urgente">Urgente</MenuItem>
              <MenuItem value="emergencia">Emergencia</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Motivo de Ingreso"
              value={formData.motivo_ingreso}
              onChange={(e) => setFormData({ ...formData, motivo_ingreso: e.target.value })}
              required
              multiline
              rows={2}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Diagnóstico de Ingreso"
              value={formData.diagnostico_ingreso}
              onChange={(e) => setFormData({ ...formData, diagnostico_ingreso: e.target.value })}
              required
              multiline
              rows={2}
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleCerrarDialogo}>Cancelar</Button>
        <Button 
          onClick={handleGuardar} 
          variant="contained" 
          disabled={guardando || !formData.paciente_id || !formData.motivo_ingreso || !formData.diagnostico_ingreso}
        >
          {guardando ? 'Guardando...' : 'Guardar'}
        </Button>
      </DialogActions>
    </Dialog>
  </>
  );
}
