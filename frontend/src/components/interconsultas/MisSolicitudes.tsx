import React, { useState, useEffect } from 'react';
import { Box, Card, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, CircularProgress, IconButton } from '@mui/material';
import { Visibility as VisibilityIcon } from '@mui/icons-material';
import { Download, FileSpreadsheet, Printer } from 'lucide-react';
import { interconsultaService } from '@/services/interconsultaService';
import { ESTADOS, URGENCIAS } from '@/types/interconsulta';
import type { Interconsulta } from '@/types/interconsulta';
import DetalleInterconsulta from './DetalleInterconsulta';
import FilterBar from './FilterBar';
import { exportToCSV, exportToXLSX, printTable } from '@/utils/exportUtils';

export default function MisSolicitudes({ onActualizar }: { onActualizar?: () => void }) {
  const [interconsultas, setInterconsultas] = useState<Interconsulta[]>([]);
  const [cargando, setCargando] = useState(true);
  const [detalleAbierto, setDetalleAbierto] = useState(false);
  const [interconsultaSeleccionada, setInterconsultaSeleccionada] = useState<string | null>(null);
  const [filters, setFilters] = useState<{
    estado?: string;
    urgencia?: string;
    especialidad?: string;
  }>({});

  useEffect(() => {
    const cargar = async () => {
      setCargando(true);
      try {
        const data = await interconsultaService.listar({ 
          limit: 100,
          ...filters
        });
        setInterconsultas(data);
      } catch (err) {
        console.error(err);
      } finally {
        setCargando(false);
      }
    };
    cargar();
  }, [filters]);

  const handleVerDetalle = (id: string) => {
    setInterconsultaSeleccionada(id);
    setDetalleAbierto(true);
  };

  const handleExportCSV = () => {
    const data = interconsultas.map(ic => ({
      Fecha: new Date(ic.fecha_solicitud).toLocaleDateString(),
      Especialidad: ic.especialidad_requerida,
      Urgencia: ic.urgencia,
      Estado: ic.estado,
      Motivo: ic.motivo_solicitud.substring(0, 50)
    }));
    exportToCSV('interconsultas', data);
  };

  const handleExportXLSX = () => {
    const data = interconsultas.map(ic => ({
      Fecha: new Date(ic.fecha_solicitud).toLocaleDateString(),
      Especialidad: ic.especialidad_requerida,
      Urgencia: ic.urgencia,
      Estado: ic.estado,
      Motivo: ic.motivo_solicitud.substring(0, 50)
    }));
    exportToXLSX('interconsultas', data);
  };

  if (cargando) return <Box display="flex" justifyContent="center" p={4}><CircularProgress /></Box>;

  return (
    <>
      <FilterBar 
        filters={filters}
        onFilterChange={setFilters}
        onClearFilters={() => setFilters({})}
      />

      <div className="flex justify-end gap-2 mb-4">
        <button
          onClick={handleExportCSV}
          className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-gray-700 dark:text-gray-200"
          title="Exportar a CSV"
        >
          <Download size={18} />
          CSV
        </button>
        <button
          onClick={handleExportXLSX}
          className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-gray-700 dark:text-gray-200"
          title="Exportar a Excel"
        >
          <FileSpreadsheet size={18} />
          Excel
        </button>
        <button
          onClick={printTable}
          className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-gray-700 dark:text-gray-200"
          title="Imprimir"
        >
          <Printer size={18} />
          Imprimir
        </button>
      </div>

      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Fecha</TableCell>
                <TableCell>Especialidad</TableCell>
                <TableCell>Urgencia</TableCell>
                <TableCell>Estado</TableCell>
                <TableCell>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {interconsultas.map((ic) => (
                <TableRow key={ic.id}>
                  <TableCell>{new Date(ic.fecha_solicitud).toLocaleDateString()}</TableCell>
                  <TableCell>{ic.especialidad_requerida}</TableCell>
                  <TableCell>
                    <Chip 
                      label={URGENCIAS[ic.urgencia as keyof typeof URGENCIAS]?.label || ic.urgencia}
                      color={URGENCIAS[ic.urgencia as keyof typeof URGENCIAS]?.color as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={ESTADOS[ic.estado as keyof typeof ESTADOS]?.label || ic.estado}
                      color={ESTADOS[ic.estado as keyof typeof ESTADOS]?.color as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleVerDetalle(ic.id)}
                      aria-label="Ver detalle de interconsulta"
                    >
                      <VisibilityIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      <DetalleInterconsulta
        open={detalleAbierto}
        interconsultaId={interconsultaSeleccionada}
        onClose={() => setDetalleAbierto(false)}
        onActualizar={onActualizar}
      />
    </>
  );
}
