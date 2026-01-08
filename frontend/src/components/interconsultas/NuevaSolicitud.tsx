import React, { useState, useEffect } from 'react';
import { Card, CardContent, TextField, Button, Grid, MenuItem, Alert, Autocomplete } from '@mui/material';
import { interconsultaService } from '@/services/interconsultaService';
import { pacienteService } from '@/services/pacienteService';
import { ESPECIALIDADES } from '@/types/interconsulta';

export default function NuevaSolicitud({ onSuccess }: { onSuccess?: () => void }) {
  const [formulario, setFormulario] = useState({
    paciente_id: '',
    especialidad_requerida: '',
    motivo_solicitud: '',
    urgencia: 'normal',
    antecedentes_relevantes: ''
  });
  const [pacientes, setPacientes] = useState<any[]>([]);
  const [pacienteSeleccionado, setPacienteSeleccionado] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [guardando, setGuardando] = useState(false);

  useEffect(() => {
    cargarPacientes();
  }, []);

  const cargarPacientes = async () => {
    try {
      const data = await pacienteService.listar();
      setPacientes(data);
    } catch (err) {
      console.error('Error al cargar pacientes:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('🔵 Iniciando envío de solicitud...');
    console.log('📋 Datos del formulario:', formulario);
    
    try {
      setGuardando(true);
      setError(null);
      
      console.log('📤 Enviando petición al backend...');
      const resultado = await interconsultaService.crear(formulario);
      console.log('✅ Solicitud creada exitosamente:', resultado);
      
      setFormulario({
        paciente_id: '',
        especialidad_requerida: '',
        motivo_solicitud: '',
        urgencia: 'normal',
        antecedentes_relevantes: ''
      });
      setPacienteSeleccionado(null);
      
      alert('✅ Solicitud de interconsulta creada exitosamente');
      onSuccess?.();
    } catch (err: any) {
      console.error('❌ Error completo:', err);
      console.error('❌ Respuesta del servidor:', err.response?.data);
      console.error('❌ Status:', err.response?.status);
      
      const errorDetail = err.response?.data?.detail;
      if (Array.isArray(errorDetail)) {
        setError(errorDetail.map((e: any) => `${e.loc?.join('.')}: ${e.msg}`).join(', '));
      } else if (typeof errorDetail === 'string') {
        setError(errorDetail);
      } else {
        setError(`Error al crear solicitud: ${err.message || 'Error desconocido'}`);
      }
    } finally {
      setGuardando(false);
      console.log('🔵 Proceso finalizado');
    }
  };

  return (
    <Card>
      <CardContent>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={2}>
            {error && (
              <Grid item xs={12}>
                <Alert severity="error">{error}</Alert>
              </Grid>
            )}
            <Grid item xs={12}>
              <Autocomplete
                id="autocomplete-paciente"
                options={pacientes}
                getOptionLabel={(option) => `${option.nombre_completo} - ${option.numero_expediente}`}
                value={pacienteSeleccionado}
                onChange={(_, newValue) => {
                  setPacienteSeleccionado(newValue);
                  setFormulario({...formulario, paciente_id: newValue?.id || ''});
                }}
                renderInput={(params) => (
                  <TextField 
                    {...params}
                    id="textfield-paciente"
                    label="Seleccionar Paciente" 
                    required 
                    helperText={pacientes.length === 0 ? "No hay pacientes disponibles o no tienes permisos para verlos" : ""}
                  />
                )}
                noOptionsText="No hay pacientes disponibles"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                id="textfield-especialidad"
                fullWidth
                select
                label="Especialidad Requerida"
                value={formulario.especialidad_requerida}
                onChange={(e) => setFormulario({...formulario, especialidad_requerida: e.target.value})}
                required
              >
                {ESPECIALIDADES.map((esp) => (
                  <MenuItem key={esp} value={esp}>{esp}</MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                id="textfield-urgencia"
                fullWidth
                select
                label="Urgencia"
                value={formulario.urgencia}
                onChange={(e) => setFormulario({...formulario, urgencia: e.target.value})}
              >
                <MenuItem value="normal">Normal</MenuItem>
                <MenuItem value="urgente">Urgente</MenuItem>
                <MenuItem value="emergencia">Emergencia</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                id="textfield-motivo"
                fullWidth
                multiline
                rows={4}
                label="Motivo de la Solicitud"
                value={formulario.motivo_solicitud}
                onChange={(e) => setFormulario({...formulario, motivo_solicitud: e.target.value})}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                id="textfield-antecedentes"
                fullWidth
                multiline
                rows={3}
                label="Antecedentes Relevantes"
                value={formulario.antecedentes_relevantes}
                onChange={(e) => setFormulario({...formulario, antecedentes_relevantes: e.target.value})}
              />
            </Grid>
            {error && (
              <Grid item xs={12}>
                <Alert severity="error">{error}</Alert>
              </Grid>
            )}
            <Grid item xs={12}>
              <Button type="submit" variant="contained" disabled={guardando}>
                {guardando ? 'Enviando...' : 'Enviar Solicitud'}
              </Button>
            </Grid>
          </Grid>
        </form>
      </CardContent>
    </Card>
  );
}
