import React, { useState, useEffect } from 'react';
import { Box, Card, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, CircularProgress, Button } from '@mui/material';
import { interconsultaService } from '@/services/interconsultaService';
import { ESTADOS } from '@/types/interconsulta';
import type { Interconsulta } from '@/types/interconsulta';

export default function MisInterconsultas({ onActualizar }: { onActualizar?: () => void }) {
  const [interconsultas, setInterconsultas] = useState<Interconsulta[]>([]);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    const cargar = async () => {
      try {
        const data = await interconsultaService.listar({ mis_interconsultas: true, limit: 100 });
        setInterconsultas(data);
      } catch (err) {
        console.error(err);
      } finally {
        setCargando(false);
      }
    };
    cargar();
  }, []);

  const handleAceptar = async (id: string) => {
    try {
      await interconsultaService.aceptar(id, {});
      onActualizar?.();
    } catch (err) {
      console.error(err);
    }
  };

  if (cargando) return <Box display="flex" justifyContent="center" p={4}><CircularProgress /></Box>;

  return (
    <Card>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Fecha</TableCell>
              <TableCell>Especialidad</TableCell>
              <TableCell>Motivo</TableCell>
              <TableCell>Estado</TableCell>
              <TableCell>Acciones</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {interconsultas.map((ic) => (
              <TableRow key={ic.id}>
                <TableCell>{new Date(ic.fecha_solicitud).toLocaleDateString()}</TableCell>
                <TableCell>{ic.especialidad_requerida}</TableCell>
                <TableCell>{ic.motivo_solicitud.substring(0, 50)}...</TableCell>
                <TableCell>
                  <Chip 
                    label={ESTADOS[ic.estado as keyof typeof ESTADOS]?.label || ic.estado}
                    color={ESTADOS[ic.estado as keyof typeof ESTADOS]?.color as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {ic.estado === 'solicitada' && (
                    <Button size="small" variant="contained" onClick={() => handleAceptar(ic.id)}>
                      Aceptar
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Card>
  );
}
