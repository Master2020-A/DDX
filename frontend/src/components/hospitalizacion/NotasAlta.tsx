import React from 'react';
import { Box, Card, Typography } from '@mui/material';

export default function NotasAlta() {
  return (
    <Card sx={{ p: 3 }}>
      <Typography variant="h6">🚪 Notas de Alta</Typography>
      <Box mt={2}>
        <Typography color="text.secondary">
          Seleccione una hospitalización activa para generar nota de alta.
        </Typography>
      </Box>
    </Card>
  );
}
