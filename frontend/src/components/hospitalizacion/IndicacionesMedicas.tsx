import React from 'react';
import { Box, Card, Typography } from '@mui/material';

export default function IndicacionesMedicas() {
  return (
    <Card sx={{ p: 3 }}>
      <Typography variant="h6">💊 Indicaciones Médicas</Typography>
      <Box mt={2}>
        <Typography color="text.secondary">
          Seleccione una hospitalización activa para gestionar indicaciones médicas.
        </Typography>
      </Box>
    </Card>
  );
}
