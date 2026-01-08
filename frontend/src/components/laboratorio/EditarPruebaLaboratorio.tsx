/**
 * Componente para editar prueba de laboratorio existente
 * Permite agregar parámetros faltantes manualmente
 */
import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  Chip,
  Divider
} from '@mui/material';
import {
  Close as CloseIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Save as SaveIcon
} from '@mui/icons-material';
import laboratorioService from '@/services/laboratorioService';
import { PruebaLaboratorio } from '@/types/laboratorio';

interface EditarPruebaLaboratorioProps {
  open: boolean;
  prueba: PruebaLaboratorio | null;
  onClose: () => void;
  onSuccess: () => void;
}

interface ParametroEditable {
  parametro: string;
  valor: number;
  esNuevo?: boolean;
}

const EditarPruebaLaboratorio: React.FC<EditarPruebaLaboratorioProps> = ({
  open,
  prueba,
  onClose,
  onSuccess
}) => {
  const [parametros, setParametros] = useState<ParametroEditable[]>([]);
  const [nuevoParametro, setNuevoParametro] = useState('');
  const [nuevoValor, setNuevoValor] = useState('');
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log('🟢 EditarPruebaLaboratorio - useEffect ejecutado');
    console.log('🟢 open:', open);
    console.log('🟢 prueba:', prueba);
    
    if (prueba && open) {
      console.log('🟢 Cargando parámetros existentes...');
      console.log('🟢 prueba.resultados:', prueba.resultados);
      console.log('🟢 Tipo de resultados:', typeof prueba.resultados);
      
      // Cargar parámetros existentes
      // resultados puede ser un array o un objeto
      let parametrosExistentes: ParametroEditable[] = [];
      
      if (Array.isArray(prueba.resultados)) {
        // Si es un array
        parametrosExistentes = prueba.resultados.map((r: any) => ({
          parametro: r.parametro,
          valor: r.valor,
          esNuevo: false
        }));
      } else if (prueba.resultados && typeof prueba.resultados === 'object') {
        // Si es un objeto, convertir a array
        parametrosExistentes = Object.entries(prueba.resultados).map(([parametro, valor]) => ({
          parametro,
          valor: typeof valor === 'number' ? valor : parseFloat(String(valor)),
          esNuevo: false
        }));
      }
      
      console.log('🟢 Parámetros cargados:', parametrosExistentes);
      setParametros(parametrosExistentes);
      setNuevoParametro('');
      setNuevoValor('');
      setError(null);
    }
  }, [prueba, open]);

  const handleAgregarParametro = () => {
    if (!nuevoParametro.trim() || !nuevoValor.trim()) {
      setError('Ingrese nombre y valor del parámetro');
      return;
    }

    const valor = parseFloat(nuevoValor);
    if (isNaN(valor)) {
      setError('El valor debe ser un número válido');
      return;
    }

    // Verificar si ya existe
    if (parametros.some(p => p.parametro.toLowerCase() === nuevoParametro.toLowerCase())) {
      setError('Este parámetro ya existe');
      return;
    }

    setParametros([
      ...parametros,
      {
        parametro: nuevoParametro.trim(),
        valor: valor,
        esNuevo: true
      }
    ]);

    setNuevoParametro('');
    setNuevoValor('');
    setError(null);
  };

  const handleEliminarParametro = (index: number) => {
    setParametros(parametros.filter((_, i) => i !== index));
  };

  const handleActualizarValor = (index: number, nuevoValor: string) => {
    const valor = parseFloat(nuevoValor);
    if (!isNaN(valor)) {
      const nuevosParametros = [...parametros];
      nuevosParametros[index].valor = valor;
      setParametros(nuevosParametros);
    }
  };

  const handleGuardar = async () => {
    if (!prueba) return;

    if (parametros.length === 0) {
      setError('Debe haber al menos un parámetro');
      return;
    }

    setGuardando(true);
    setError(null);

    try {
      const resultados = parametros.map(p => ({
        parametro: p.parametro,
        valor: p.valor
      }));

      await laboratorioService.actualizarPrueba(prueba.id, { resultados });

      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Error actualizando prueba:', err);
      setError(err.response?.data?.detail || 'Error al actualizar la prueba');
    } finally {
      setGuardando(false);
    }
  };

  if (!prueba) return null;

  const parametrosNuevos = parametros.filter(p => p.esNuevo);
  const parametrosExistentes = parametros.filter(p => !p.esNuevo);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h6">Editar Prueba de Laboratorio</Typography>
            <Typography variant="caption" color="text.secondary">
              {prueba.area} - {prueba.tipo_prueba}
            </Typography>
          </Box>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Información de la prueba */}
        <Box mb={3}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Información General
          </Typography>
          <Box display="flex" gap={1} flexWrap="wrap">
            <Chip label={`Fecha: ${prueba.fecha_resultado ? new Date(prueba.fecha_resultado).toLocaleDateString() : 'N/A'}`} size="small" />
            {prueba.laboratorio_externo && (
              <Chip label={`Lab: ${prueba.laboratorio_externo}`} size="small" />
            )}
            {prueba.numero_orden && (
              <Chip label={`Orden: ${prueba.numero_orden}`} size="small" />
            )}
          </Box>
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Parámetros existentes */}
        <Typography variant="subtitle2" gutterBottom>
          Parámetros Actuales ({parametrosExistentes.length})
        </Typography>
        <TableContainer component={Paper} variant="outlined" sx={{ mb: 3, maxHeight: 300 }}>
          <Table size="small" stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Parámetro</TableCell>
                <TableCell align="right">Valor</TableCell>
                <TableCell align="center" width={80}>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {parametrosExistentes.map((param) => {
                const indexReal = parametros.findIndex(p => p === param);
                return (
                  <TableRow key={indexReal}>
                    <TableCell>{param.parametro}</TableCell>
                    <TableCell align="right">
                      <TextField
                        type="number"
                        value={param.valor}
                        onChange={(e) => handleActualizarValor(indexReal, e.target.value)}
                        size="small"
                        inputProps={{ step: 0.01 }}
                        sx={{ width: 100 }}
                      />
                    </TableCell>
                    <TableCell align="center">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleEliminarParametro(indexReal)}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Parámetros nuevos agregados */}
        {parametrosNuevos.length > 0 && (
          <>
            <Typography variant="subtitle2" gutterBottom color="primary">
              Parámetros Agregados ({parametrosNuevos.length})
            </Typography>
            <TableContainer component={Paper} variant="outlined" sx={{ mb: 3, maxHeight: 200 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Parámetro</TableCell>
                    <TableCell align="right">Valor</TableCell>
                    <TableCell align="center" width={80}>Acciones</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {parametrosNuevos.map((param) => {
                    const indexReal = parametros.findIndex(p => p === param);
                    return (
                      <TableRow key={indexReal} sx={{ bgcolor: 'success.lighter' }}>
                        <TableCell>
                          <Chip label="NUEVO" size="small" color="success" sx={{ mr: 1 }} />
                          {param.parametro}
                        </TableCell>
                        <TableCell align="right">
                          <TextField
                            type="number"
                            value={param.valor}
                            onChange={(e) => handleActualizarValor(indexReal, e.target.value)}
                            size="small"
                            inputProps={{ step: 0.01 }}
                            sx={{ width: 100 }}
                          />
                        </TableCell>
                        <TableCell align="center">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleEliminarParametro(indexReal)}
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          </>
        )}

        <Divider sx={{ my: 2 }} />

        {/* Agregar nuevo parámetro */}
        <Typography variant="subtitle2" gutterBottom>
          Agregar Parámetro Faltante
        </Typography>
        <Box display="flex" gap={2} alignItems="flex-start">
          <TextField
            label="Nombre del Parámetro"
            value={nuevoParametro}
            onChange={(e) => setNuevoParametro(e.target.value)}
            placeholder="ej: glucosa, hemoglobina"
            size="small"
            fullWidth
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                handleAgregarParametro();
              }
            }}
          />
          <TextField
            label="Valor"
            type="number"
            value={nuevoValor}
            onChange={(e) => setNuevoValor(e.target.value)}
            placeholder="ej: 95.5"
            size="small"
            inputProps={{ step: 0.01 }}
            sx={{ width: 150 }}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                handleAgregarParametro();
              }
            }}
          />
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleAgregarParametro}
            sx={{ minWidth: 120 }}
          >
            Agregar
          </Button>
        </Box>

        <Alert severity="info" sx={{ mt: 2 }}>
          💡 <strong>Tip:</strong> Agregue los parámetros que no fueron detectados automáticamente.
          El sistema re-analizará todos los valores con los rangos de referencia.
        </Alert>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={guardando}>
          Cancelar
        </Button>
        <Button
          variant="contained"
          startIcon={<SaveIcon />}
          onClick={handleGuardar}
          disabled={guardando || parametros.length === 0}
        >
          {guardando ? 'Guardando...' : 'Guardar Cambios'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default EditarPruebaLaboratorio;
