/**
 * Formulario para captura de resultados de laboratorio
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  TextField,
  MenuItem,
  Grid,
  Typography,
  Paper,
  Divider,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Science as ScienceIcon,
  Save as SaveIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import {
  AREAS_LABORATORIO,
  TIPOS_PRUEBAS,
  PARAMETROS_LABELS,
  CrearPruebaLaboratorio,
  ResultadoLaboratorio,
  RangoReferencia
} from '@/types/laboratorio';
import laboratorioService from '@/services/laboratorioService';

interface FormularioLaboratorioProps {
  pacienteId: string;
  consultaId?: string;
  onSuccess?: (prueba: any) => void;
  onCancel?: () => void;
}

const FormularioLaboratorio: React.FC<FormularioLaboratorioProps> = ({
  pacienteId,
  consultaId,
  onSuccess,
  onCancel
}) => {
  const [area, setArea] = useState('');
  const [tipoPrueba, setTipoPrueba] = useState('');
  const [resultados, setResultados] = useState<ResultadoLaboratorio[]>([]);
  const [laboratorioExterno, setLaboratorioExterno] = useState('');
  const [numeroOrden, setNumeroOrden] = useState('');
  const [fechaResultado, setFechaResultado] = useState('');
  const [notas, setNotas] = useState('');
  const [rangos, setRangos] = useState<RangoReferencia[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // Cargar rangos cuando cambia el área
  useEffect(() => {
    if (area) {
      cargarRangos();
    }
  }, [area]);

  // Inicializar resultados cuando cambia el tipo de prueba
  useEffect(() => {
    if (tipoPrueba && area) {
      const prueba = TIPOS_PRUEBAS[area]?.find(p => p.value === tipoPrueba);
      if (prueba) {
        const nuevosResultados = prueba.parametros.map(param => ({
          parametro: param,
          valor: 0
        }));
        setResultados(nuevosResultados);
      }
    }
  }, [tipoPrueba, area]);

  const cargarRangos = async () => {
    try {
      const data = await laboratorioService.obtenerRangos(area);
      setRangos(data);
    } catch (err) {
      console.error('Error cargando rangos:', err);
    }
  };

  const handleAreaChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setArea(e.target.value);
    setTipoPrueba('');
    setResultados([]);
  };

  const handleResultadoChange = (index: number, valor: string) => {
    const nuevosResultados = [...resultados];
    nuevosResultados[index].valor = parseFloat(valor) || 0;
    setResultados(nuevosResultados);
  };

  const agregarParametroPersonalizado = () => {
    setResultados([...resultados, { parametro: '', valor: 0 }]);
  };

  const eliminarParametro = (index: number) => {
    const nuevosResultados = resultados.filter((_, i) => i !== index);
    setResultados(nuevosResultados);
  };

  const obtenerRangoParametro = (parametro: string): RangoReferencia | undefined => {
    return rangos.find(r => r.parametro.toLowerCase() === parametro.toLowerCase());
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const data: CrearPruebaLaboratorio = {
        paciente_id: pacienteId,
        consulta_id: consultaId,
        area,
        tipo_prueba: tipoPrueba,
        resultados: resultados.filter(r => r.parametro && r.valor !== undefined),
        laboratorio_externo: laboratorioExterno || undefined,
        numero_orden: numeroOrden || undefined,
        fecha_resultado: fechaResultado || undefined,
        notas_medico: notas || undefined
      };

      const prueba = await laboratorioService.crearPrueba(data);
      setSuccess(true);
      
      if (onSuccess) {
        onSuccess(prueba);
      }

      // Limpiar formulario
      setTimeout(() => {
        setArea('');
        setTipoPrueba('');
        setResultados([]);
        setLaboratorioExterno('');
        setNumeroOrden('');
        setFechaResultado('');
        setNotas('');
        setSuccess(false);
      }, 2000);

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al crear prueba de laboratorio');
    } finally {
      setLoading(false);
    }
  };

  const tiposPruebasDisponibles = area ? TIPOS_PRUEBAS[area] || [] : [];

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Box display="flex" alignItems="center" mb={3}>
        <ScienceIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
        <Typography variant="h5" fontWeight="bold">
          Registrar Resultados de Laboratorio
        </Typography>
      </Box>

      <Divider sx={{ mb: 3 }} />

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          ✅ Prueba de laboratorio registrada y analizada correctamente
        </Alert>
      )}

      <form onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          {/* Información General */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom color="primary">
              📋 Información General
            </Typography>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              select
              fullWidth
              required
              label="Área de Laboratorio"
              value={area}
              onChange={handleAreaChange}
              disabled={loading}
            >
              {AREAS_LABORATORIO.map(option => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              select
              fullWidth
              required
              label="Tipo de Prueba"
              value={tipoPrueba}
              onChange={(e) => setTipoPrueba(e.target.value)}
              disabled={!area || loading}
            >
              {tiposPruebasDisponibles.map(option => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>

          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Laboratorio Externo"
              value={laboratorioExterno}
              onChange={(e) => setLaboratorioExterno(e.target.value)}
              disabled={loading}
              placeholder="Ej: Lab Central"
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Número de Orden"
              value={numeroOrden}
              onChange={(e) => setNumeroOrden(e.target.value)}
              disabled={loading}
              placeholder="Ej: LAB-2024-001"
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              type="datetime-local"
              label="Fecha de Resultado"
              value={fechaResultado}
              onChange={(e) => setFechaResultado(e.target.value)}
              disabled={loading}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>

          {/* Resultados */}
          {resultados.length > 0 && (
            <>
              <Grid item xs={12}>
                <Divider sx={{ my: 2 }} />
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Typography variant="h6" color="primary">
                    🧪 Resultados
                  </Typography>
                  <Button
                    startIcon={<AddIcon />}
                    onClick={agregarParametroPersonalizado}
                    size="small"
                    disabled={loading}
                  >
                    Agregar Parámetro
                  </Button>
                </Box>
              </Grid>

              {resultados.map((resultado, index) => {
                const rango = obtenerRangoParametro(resultado.parametro);
                const label = PARAMETROS_LABELS[resultado.parametro] || resultado.parametro;

                return (
                  <Grid item xs={12} md={6} key={index}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <TextField
                        fullWidth
                        required
                        type="number"
                        label={label}
                        value={resultado.valor}
                        onChange={(e) => handleResultadoChange(index, e.target.value)}
                        disabled={loading}
                        inputProps={{ step: '0.01' }}
                        helperText={
                          rango
                            ? `Rango: ${rango.valor_min || '?'} - ${rango.valor_max || '?'} ${rango.unidad || ''}`
                            : undefined
                        }
                      />
                      {rango && (
                        <Tooltip title={rango.descripcion || ''}>
                          <IconButton size="small">
                            <InfoIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                      {!PARAMETROS_LABELS[resultado.parametro] && (
                        <IconButton
                          onClick={() => eliminarParametro(index)}
                          color="error"
                          size="small"
                        >
                          <DeleteIcon />
                        </IconButton>
                      )}
                    </Box>
                  </Grid>
                );
              })}
            </>
          )}

          {/* Notas */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Notas del Médico"
              value={notas}
              onChange={(e) => setNotas(e.target.value)}
              disabled={loading}
              placeholder="Observaciones adicionales..."
            />
          </Grid>

          {/* Botones */}
          <Grid item xs={12}>
            <Box display="flex" gap={2} justifyContent="flex-end">
              {onCancel && (
                <Button
                  variant="outlined"
                  onClick={onCancel}
                  disabled={loading}
                >
                  Cancelar
                </Button>
              )}
              <Button
                type="submit"
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <SaveIcon />}
                disabled={loading || !area || !tipoPrueba || resultados.length === 0}
              >
                {loading ? 'Guardando...' : 'Guardar y Analizar'}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </form>
    </Paper>
  );
};

export default FormularioLaboratorio;
