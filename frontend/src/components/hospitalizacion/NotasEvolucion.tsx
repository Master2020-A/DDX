import React from 'react';
import { Box, Card, Typography } from '@mui/material';

export default function NotasEvolucion() {
  return (
    <Card sx={{ p: 3 }}>
      <Typography variant="h6">📝 Notas de Evolución</Typography>
      <Box mt={2}>
        <Typography color="text.secondary">
          Seleccione una hospitalización activa para ver y agregar notas de evolución.
        </Typography>
      </Box>
    </Card>
  );
}
