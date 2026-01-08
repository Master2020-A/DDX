import React, { useState, useEffect } from 'react';
import { Box, Card, Grid, Chip, CircularProgress, Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField, MenuItem, Alert, Typography } from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { camaService } from '@/services/hospitalizacionService';
import type { Cama } from '@/types/hospitalizacion';

export default function GestionCamas() {
  const [camas, setCamas] = useState<Cama[]>([]);
  const [cargando, setCargando] = useState(true);
  const [dialogoAbierto, setDialogoAbierto] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    numero_cama: '',
    area: '',
    piso: '',
    habitacion: '',
    tipo_cama: 'estandar',
    tiene_oxigeno: false,
    tiene_monitor: false,
    tiene_ventilador: false
  });

  const cargarCamas = async () => {
    try {
      setCargando(true);
      const data = await camaService.listar({ limit: 100 });
      console.log('Camas cargadas:', data);
      setCamas(data);
    } catch (err) {
      console.error('Error cargando camas:', err);
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarCamas();
  }, []);

  const handleAbrirDialogo = () => {
    setDialogoAbierto(true);
    setError(null);
  };

  const handleCerrarDialogo = () => {
    setDialogoAbierto(false);
    setFormData({
      numero_cama: '',
      area: '',
      piso: '',
      habitacion: '',
      tipo_cama: 'estandar',
      tiene_oxigeno: false,
      tiene_monitor: false,
      tiene_ventilador: false
    });
  };

  const handleGuardar = async () => {
    try {
      setGuardando(true);
      setError(null);
      console.log('Guardando cama:', formData);
      const nuevaCama = await camaService.crear(formData);
      console.log('Cama creada:', nuevaCama);
      handleCerrarDialogo();
      await cargarCamas();
    } catch (err: any) {
      console.error('Error al guardar cama:', err);
      setError(err.response?.data?.detail || 'Error al crear la cama');
    } finally {
      setGuardando(false);
    }
  };

  if (cargando) return <Box display="flex" justifyContent="center" p={4}><CircularProgress /></Box>;

  return (
    <>
      <Box mb={3} display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h6">Gestión de Camas</Typography>
        <Button 
          variant="contained" 
          startIcon={<AddIcon />}
          onClick={handleAbrirDialogo}
        >
          Nueva Cama
        </Button>
      </Box>

      {camas.length === 0 ? (
        <Card sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No hay camas registradas
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Comienza registrando las camas disponibles en el hospital
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
            (Total de camas: {camas.length})
          </Typography>
          <Button 
            variant="contained" 
            startIcon={<AddIcon />}
            onClick={handleAbrirDialogo}
          >
            Registrar Primera Cama
          </Button>
        </Card>
      ) : (
        <Grid container spacing={2}>
      {camas.map((cama) => (
        <Grid item xs={12} sm={6} md={4} key={cama.id}>
          <Card sx={{ p: 2 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Box>
                <strong>Cama {cama.numero_cama}</strong>
                <Box>{cama.area}</Box>
              </Box>
              <Chip 
                label={cama.estado} 
                color={cama.estado === 'disponible' ? 'success' : 'error'}
                size="small"
              />
            </Box>
          </Card>
          </Grid>
        ))}
      </Grid>
      )}

      <Dialog open={dialogoAbierto} onClose={handleCerrarDialogo} maxWidth="sm" fullWidth>
        <DialogTitle>Registrar Nueva Cama</DialogTitle>
        <DialogContent>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Número de Cama"
                value={formData.numero_cama}
                onChange={(e) => setFormData({ ...formData, numero_cama: e.target.value })}
                required
                placeholder="Ej: UGC-01"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Área"
                value={formData.area}
                onChange={(e) => setFormData({ ...formData, area: e.target.value })}
                required
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
                label="Piso"
                value={formData.piso}
                onChange={(e) => setFormData({ ...formData, piso: e.target.value })}
                placeholder="Ej: 1, 2, 3"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Habitación"
                value={formData.habitacion}
                onChange={(e) => setFormData({ ...formData, habitacion: e.target.value })}
                placeholder="Ej: 101, 102"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                select
                label="Tipo de Cama"
                value={formData.tipo_cama}
                onChange={(e) => setFormData({ ...formData, tipo_cama: e.target.value })}
              >
                <MenuItem value="estandar">Estándar</MenuItem>
                <MenuItem value="electrica">Eléctrica</MenuItem>
                <MenuItem value="uci">UCI</MenuItem>
                <MenuItem value="pediatrica">Pediátrica</MenuItem>
              </TextField>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCerrarDialogo}>Cancelar</Button>
          <Button 
            onClick={handleGuardar} 
            variant="contained" 
            disabled={guardando || !formData.numero_cama || !formData.area}
          >
            {guardando ? 'Guardando...' : 'Guardar'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
