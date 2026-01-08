import React, { useState, useEffect } from 'react';
import { Box, Card, CardContent, Grid, Typography, CircularProgress } from '@mui/material';
import { estadisticasService } from '@/services/interconsultaService';
import type { EstadisticasInterconsultas } from '@/types/interconsulta';

export default function Estadisticas() {
  const [stats, setStats] = useState<EstadisticasInterconsultas | null>(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    const cargar = async () => {
      try {
        const data = await estadisticasService.obtenerGeneral();
        setStats(data);
      } catch (err) {
        console.error(err);
      } finally {
        setCargando(false);
      }
    };
    cargar();
  }, []);

  if (cargando) return <Box display="flex" justifyContent="center" p={4}><CircularProgress /></Box>;
  if (!stats) return null;

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
          <CardContent>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>Total</Typography>
            <Typography variant="h3" sx={{ color: 'white', fontWeight: 600 }}>{stats.total_solicitadas}</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
          <CardContent>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>Pendientes</Typography>
            <Typography variant="h3" sx={{ color: 'white', fontWeight: 600 }}>{stats.pendientes}</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }}>
          <CardContent>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>Aceptadas</Typography>
            <Typography variant="h3" sx={{ color: 'white', fontWeight: 600 }}>{stats.aceptadas}</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' }}>
          <CardContent>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>Completadas</Typography>
            <Typography variant="h3" sx={{ color: 'white', fontWeight: 600 }}>{stats.completadas}</Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}
