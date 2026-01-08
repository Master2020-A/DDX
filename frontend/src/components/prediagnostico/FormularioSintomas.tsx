/**
 * Formulario para ingresar síntomas y generar pre-diagnóstico
 */
import { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  IconButton,
  Grid,
  MenuItem,
  Typography,
  Chip,
  Stack,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon, Psychology as PsychologyIcon } from '@mui/icons-material';
import type { SintomaInput, PreDiagnosticoRequest } from '@/services/prediagnosticoService';

interface Props {
  pacienteId: string;
  onGenerarPrediagnostico: (request: PreDiagnosticoRequest) => void;
  cargando?: boolean;
}

export default function FormularioSintomas({ pacienteId, onGenerarPrediagnostico, cargando }: Props) {
  const [sintomas, setSintomas] = useState<SintomaInput[]>([
    { descripcion: '', intensidad: undefined, duracion: '', frecuencia: '' }
  ]);
  const [antecedentes, setAntecedentes] = useState('');
  const [medicamentos, setMedicamentos] = useState<string[]>([]);
  const [nuevoMedicamento, setNuevoMedicamento] = useState('');
  const [alergias, setAlergias] = useState<string[]>([]);
  const [nuevaAlergia, setNuevaAlergia] = useState('');
  const [error, setError] = useState<string | null>(null);

  const agregarSintoma = () => {
    setSintomas([...sintomas, { descripcion: '', intensidad: undefined, duracion: '', frecuencia: '' }]);
  };

  const eliminarSintoma = (index: number) => {
    setSintomas(sintomas.filter((_, i) => i !== index));
  };

  const actualizarSintoma = (index: number, campo: keyof SintomaInput, valor: any) => {
    const nuevosSintomas = [...sintomas];
    nuevosSintomas[index] = { ...nuevosSintomas[index], [campo]: valor };
    setSintomas(nuevosSintomas);
  };

  const agregarMedicamento = () => {
    if (nuevoMedicamento.trim()) {
      setMedicamentos([...medicamentos, nuevoMedicamento.trim()]);
      setNuevoMedicamento('');
    }
  };

  const eliminarMedicamento = (index: number) => {
    setMedicamentos(medicamentos.filter((_, i) => i !== index));
  };

  const agregarAlergia = () => {
    if (nuevaAlergia.trim()) {
      setAlergias([...alergias, nuevaAlergia.trim()]);
      setNuevaAlergia('');
    }
  };

  const eliminarAlergia = (index: number) => {
    setAlergias(alergias.filter((_, i) => i !== index));
  };

  const handleSubmit = () => {
    // Validar que haya al menos un síntoma con descripción
    const sintomasValidos = sintomas.filter(s => s.descripcion.trim());
    
    if (sintomasValidos.length === 0) {
      setError('Debe ingresar al menos un síntoma');
      return;
    }

    setError(null);

    const request: PreDiagnosticoRequest = {
      paciente_id: pacienteId,
      sintomas: sintomasValidos,
      antecedentes: antecedentes.trim() || undefined,
      medicamentos_actuales: medicamentos.length > 0 ? medicamentos : [],
      alergias: alergias.length > 0 ? alergias : [],
    };

    onGenerarPrediagnostico(request);
  };

  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" mb={3}>
          <PsychologyIcon sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6">Pre-diagnóstico Inteligente</Typography>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        {/* Síntomas */}
        <Typography variant="subtitle1" gutterBottom fontWeight="bold">
          Síntomas
        </Typography>
        {sintomas.map((sintoma, index) => (
          <Grid container spacing={2} key={index} sx={{ mb: 2 }}>
            <Grid item xs={12} sm={5}>
              <TextField
                fullWidth
                label="Descripción del síntoma"
                value={sintoma.descripcion}
                onChange={(e) => actualizarSintoma(index, 'descripcion', e.target.value)}
                placeholder="Ej: Dolor de cabeza, fiebre, tos..."
                required
              />
            </Grid>
            <Grid item xs={6} sm={2}>
              <TextField
                fullWidth
                select
                label="Intensidad"
                value={sintoma.intensidad || ''}
                onChange={(e) => actualizarSintoma(index, 'intensidad', e.target.value || undefined)}
              >
                <MenuItem value="">Sin especificar</MenuItem>
                <MenuItem value="leve">Leve</MenuItem>
                <MenuItem value="moderado">Moderado</MenuItem>
                <MenuItem value="severo">Severo</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={6} sm={2}>
              <TextField
                fullWidth
                label="Duración"
                value={sintoma.duracion}
                onChange={(e) => actualizarSintoma(index, 'duracion', e.target.value)}
                placeholder="Ej: 3 días"
              />
            </Grid>
            <Grid item xs={10} sm={2}>
              <TextField
                fullWidth
                label="Frecuencia"
                value={sintoma.frecuencia}
                onChange={(e) => actualizarSintoma(index, 'frecuencia', e.target.value)}
                placeholder="Ej: Constante"
              />
            </Grid>
            <Grid item xs={2} sm={1}>
              <IconButton 
                onClick={() => eliminarSintoma(index)} 
                disabled={sintomas.length === 1}
                color="error"
              >
                <DeleteIcon />
              </IconButton>
            </Grid>
          </Grid>
        ))}
        <Button startIcon={<AddIcon />} onClick={agregarSintoma} sx={{ mb: 3 }}>
          Agregar Síntoma
        </Button>

        {/* Antecedentes */}
        <Typography variant="subtitle1" gutterBottom fontWeight="bold" sx={{ mt: 3 }}>
          Antecedentes Relevantes
        </Typography>
        <TextField
          fullWidth
          multiline
          rows={3}
          value={antecedentes}
          onChange={(e) => setAntecedentes(e.target.value)}
          placeholder="Enfermedades previas, cirugías, hospitalizaciones..."
          sx={{ mb: 3 }}
        />

        {/* Medicamentos */}
        <Typography variant="subtitle1" gutterBottom fontWeight="bold">
          Medicamentos Actuales
        </Typography>
        <Box display="flex" gap={1} mb={2}>
          <TextField
            fullWidth
            value={nuevoMedicamento}
            onChange={(e) => setNuevoMedicamento(e.target.value)}
            placeholder="Nombre del medicamento"
            onKeyPress={(e) => e.key === 'Enter' && agregarMedicamento()}
          />
          <Button onClick={agregarMedicamento} variant="outlined">
            Agregar
          </Button>
        </Box>
        <Stack direction="row" spacing={1} flexWrap="wrap" mb={3}>
          {medicamentos.map((med, index) => (
            <Chip
              key={index}
              label={med}
              onDelete={() => eliminarMedicamento(index)}
              color="primary"
              variant="outlined"
            />
          ))}
        </Stack>

        {/* Alergias */}
        <Typography variant="subtitle1" gutterBottom fontWeight="bold">
          Alergias
        </Typography>
        <Box display="flex" gap={1} mb={2}>
          <TextField
            fullWidth
            value={nuevaAlergia}
            onChange={(e) => setNuevaAlergia(e.target.value)}
            placeholder="Alergia a medicamento o sustancia"
            onKeyPress={(e) => e.key === 'Enter' && agregarAlergia()}
          />
          <Button onClick={agregarAlergia} variant="outlined">
            Agregar
          </Button>
        </Box>
        <Stack direction="row" spacing={1} flexWrap="wrap" mb={3}>
          {alergias.map((alergia, index) => (
            <Chip
              key={index}
              label={alergia}
              onDelete={() => eliminarAlergia(index)}
              color="error"
              variant="outlined"
            />
          ))}
        </Stack>

        {/* Botón de generar */}
        <Box display="flex" justifyContent="flex-end" mt={3}>
          <Button
            variant="contained"
            size="large"
            onClick={handleSubmit}
            disabled={cargando}
            startIcon={cargando ? <CircularProgress size={20} /> : <PsychologyIcon />}
          >
            {cargando ? 'Generando Pre-diagnóstico...' : 'Generar Pre-diagnóstico'}
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
}
