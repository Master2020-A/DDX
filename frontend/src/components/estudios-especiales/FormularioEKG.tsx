/**
 * Formulario para captura de Electrocardiograma (EKG)
 */
import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Grid,
  FormControlLabel,
  Checkbox,
  Alert,
  CircularProgress,
  Box,
  Typography,
  Divider,
  InputAdornment,
  Tabs,
  Tab,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import { CrearEstudioEKG } from '../../types/estudiosEspeciales';
import estudiosEspecialesService from '../../services/estudiosEspecialesService';
import SubirArchivoEstudio from './SubirArchivoEstudio';
import SubirImagenEKG from './SubirImagenEKG';

interface Props {
  open: boolean;
  pacienteId: string;
  onClose: () => void;
  onSuccess: () => void;
}

const FormularioEKG: React.FC<Props> = ({ open, pacienteId, onClose, onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [interpretacion, setInterpretacion] = useState<any>(null);
  const [tabActual, setTabActual] = useState(0);
  const [datosExtraidosExito, setDatosExtraidosExito] = useState(false);
  const [cantidadDatosExtraidos, setCantidadDatosExtraidos] = useState(0);
  const [estudioId, setEstudioId] = useState<string | null>(null);
  
  const [formData, setFormData] = useState<CrearEstudioEKG>({
    paciente_id: pacienteId,
    fecha_estudio: new Date().toISOString().slice(0, 16),
    motivo: '',
    indicacion_clinica: '',
    edad_paciente: undefined,
    peso_kg: undefined,
    altura_cm: undefined,
    presion_arterial: '',
    frecuencia_cardiaca: undefined,
    intervalo_pr: undefined,
    duracion_qrs: undefined,
    intervalo_qt: undefined,
    intervalo_qtc: undefined,
    eje_qrs: undefined,
    ritmo: 'sinusal',
    ritmo_regular: true,
    onda_p: '',
    complejo_qrs: '',
    segmento_st: '',
    onda_t: '',
    onda_u: ''
  });

  const handleChange = (field: keyof CrearEstudioEKG, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await estudiosEspecialesService.crearEstudioEKG(formData);
      setInterpretacion(response.interpretacion);
      setEstudioId(response.id); // Guardar ID del estudio
      
      // NO cerrar automáticamente - mostrar botones de PDF
      
    } catch (err: any) {
      console.error('Error al crear EKG:', err);
      setError(err.response?.data?.detail || 'Error al crear el estudio de EKG');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      paciente_id: pacienteId,
      fecha_estudio: new Date().toISOString().slice(0, 16),
      motivo: '',
      indicacion_clinica: '',
      edad_paciente: undefined,
      peso_kg: undefined,
      altura_cm: undefined,
      presion_arterial: '',
      frecuencia_cardiaca: undefined,
      intervalo_pr: undefined,
      duracion_qrs: undefined,
      intervalo_qt: undefined,
      intervalo_qtc: undefined,
      eje_qrs: undefined,
      ritmo: 'sinusal',
      ritmo_regular: true,
      onda_p: '',
      complejo_qrs: '',
      segmento_st: '',
      onda_t: '',
      onda_u: ''
    });
    setInterpretacion(null);
    setError(null);
    setEstudioId(null);
  };

  const handleClose = () => {
    if (!loading) {
      resetForm();
      setTabActual(0);
      onClose();
    }
  };

  const handleDatosExtraidos = (_tipo: string, datos: any, _anomalias?: string[]) => {
    console.log('🎯 Datos recibidos en formulario:', datos);
    
    // Contar cuántos datos se extrajeron
    let contador = 0;
    
    // Rellenar formulario con datos extraídos
    const nuevoFormData: any = { ...formData };
    
    if (datos.motivo) { nuevoFormData.motivo = datos.motivo; contador++; }
    if (datos.edad_paciente) { nuevoFormData.edad_paciente = datos.edad_paciente; contador++; }
    if (datos.peso_paciente) { nuevoFormData.peso_kg = datos.peso_paciente; contador++; }
    if (datos.altura_paciente) { nuevoFormData.altura_cm = datos.altura_paciente; contador++; }
    if (datos.presion_arterial) { nuevoFormData.presion_arterial = datos.presion_arterial; contador++; }
    
    // Parámetros del ECG (los más importantes)
    if (datos.frecuencia_cardiaca) { 
      nuevoFormData.frecuencia_cardiaca = typeof datos.frecuencia_cardiaca === 'number' 
        ? datos.frecuencia_cardiaca 
        : parseInt(datos.frecuencia_cardiaca); 
      contador++;
    }
    if (datos.intervalo_pr) { 
      nuevoFormData.intervalo_pr = typeof datos.intervalo_pr === 'number' 
        ? datos.intervalo_pr 
        : parseInt(datos.intervalo_pr); 
      contador++;
    }
    if (datos.duracion_qrs) { 
      nuevoFormData.duracion_qrs = typeof datos.duracion_qrs === 'number' 
        ? datos.duracion_qrs 
        : parseInt(datos.duracion_qrs); 
      contador++;
    }
    if (datos.intervalo_qt) { 
      nuevoFormData.intervalo_qt = typeof datos.intervalo_qt === 'number' 
        ? datos.intervalo_qt 
        : parseInt(datos.intervalo_qt); 
      contador++;
    }
    if (datos.intervalo_qtc || datos.qtc) { 
      const qtc = datos.intervalo_qtc || datos.qtc;
      nuevoFormData.intervalo_qtc = typeof qtc === 'number' 
        ? qtc 
        : parseInt(qtc); 
      contador++;
    }
    if (datos.eje_qrs) { 
      nuevoFormData.eje_qrs = typeof datos.eje_qrs === 'number' 
        ? datos.eje_qrs 
        : parseInt(datos.eje_qrs); 
      contador++;
    }
    
    // Datos cualitativos del nuevo sistema
    if (datos.ritmo) { nuevoFormData.ritmo = datos.ritmo.toLowerCase(); contador++; }
    if (datos.onda_p) { nuevoFormData.onda_p = datos.onda_p; contador++; }
    if (datos.complejo_qrs) { nuevoFormData.complejo_qrs = datos.complejo_qrs; contador++; }
    if (datos.onda_t) { nuevoFormData.onda_t = datos.onda_t.toLowerCase(); contador++; }
    if (datos.segmento_st) { nuevoFormData.segmento_st = datos.segmento_st; contador++; }
    
    // Actualizar formulario
    setFormData(nuevoFormData);
    
    // Mostrar mensaje de éxito
    setCantidadDatosExtraidos(contador);
    setDatosExtraidosExito(true);
    
    console.log(`✅ ${contador} datos extraídos y rellenados en el formulario`);
    
    // Cambiar a pestaña de captura manual para ver los datos
    setTabActual(0);
    
    // Ocultar mensaje después de 5 segundos
    setTimeout(() => {
      setDatosExtraidosExito(false);
    }, 5000);
  };

  const handleParametrosEKGExtraidos = (parametros: any) => {
    console.log('🎯 Parámetros EKG extraídos:', parametros);
    handleDatosExtraidos('ekg', parametros);
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        ❤️ Nuevo Electrocardiograma (EKG)
      </DialogTitle>
      
      <DialogContent>
        {/* Pestañas */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs value={tabActual} onChange={(_e, v) => setTabActual(v)}>
            <Tab label="📝 Captura Manual" />
            <Tab label="📄 Subir Archivo" />
          </Tabs>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {datosExtraidosExito && (
          <Alert severity="success" sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              <strong>✅ Datos Extraídos Exitosamente</strong>
            </Typography>
            <Typography variant="body2">
              Se extrajeron {cantidadDatosExtraidos} parámetros del archivo y se rellenaron automáticamente en el formulario.
              Revisa los campos y haz clic en "Guardar y Analizar" para continuar.
            </Typography>
          </Alert>
        )}

        {interpretacion && (
          <Alert 
            severity={interpretacion.es_critico ? 'error' : interpretacion.requiere_atencion ? 'warning' : 'success'}
            sx={{ mb: 2 }}
          >
            <Typography variant="subtitle2" gutterBottom>
              <strong>Interpretación Automática:</strong>
            </Typography>
            <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
              {interpretacion.interpretacion}
            </Typography>
          </Alert>
        )}

        {/* Pestaña 1: Captura Manual */}
        {tabActual === 0 && (
          <Grid container spacing={2}>
          {/* Información General */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" color="primary" gutterBottom>
              Información General
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Fecha y Hora del Estudio"
              type="datetime-local"
              value={formData.fecha_estudio}
              onChange={(e) => handleChange('fecha_estudio', e.target.value)}
              InputLabelProps={{ shrink: true }}
              required
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Motivo"
              value={formData.motivo}
              onChange={(e) => handleChange('motivo', e.target.value)}
              placeholder="Ej: Dolor torácico, chequeo rutinario"
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Indicación Clínica"
              value={formData.indicacion_clinica}
              onChange={(e) => handleChange('indicacion_clinica', e.target.value)}
              multiline
              rows={2}
              placeholder="Ej: Descartar síndrome coronario agudo"
            />
          </Grid>

          {/* Datos del Paciente */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" color="primary" gutterBottom sx={{ mt: 2 }}>
              Datos del Paciente
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={6} sm={3}>
            <TextField
              fullWidth
              label="Edad"
              type="number"
              value={formData.edad_paciente || ''}
              onChange={(e) => handleChange('edad_paciente', e.target.value ? parseInt(e.target.value) : undefined)}
              InputProps={{ endAdornment: <InputAdornment position="end">años</InputAdornment> }}
            />
          </Grid>

          <Grid item xs={6} sm={3}>
            <TextField
              fullWidth
              label="Peso"
              type="number"
              value={formData.peso_kg || ''}
              onChange={(e) => handleChange('peso_kg', e.target.value ? parseFloat(e.target.value) : undefined)}
              InputProps={{ endAdornment: <InputAdornment position="end">kg</InputAdornment> }}
            />
          </Grid>

          <Grid item xs={6} sm={3}>
            <TextField
              fullWidth
              label="Altura"
              type="number"
              value={formData.altura_cm || ''}
              onChange={(e) => handleChange('altura_cm', e.target.value ? parseFloat(e.target.value) : undefined)}
              InputProps={{ endAdornment: <InputAdornment position="end">cm</InputAdornment> }}
            />
          </Grid>

          <Grid item xs={6} sm={3}>
            <TextField
              fullWidth
              label="Presión Arterial"
              value={formData.presion_arterial}
              onChange={(e) => handleChange('presion_arterial', e.target.value)}
              placeholder="120/80"
            />
          </Grid>

          {/* Parámetros Medidos */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" color="primary" gutterBottom sx={{ mt: 2 }}>
              Parámetros Medidos
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={6} sm={4}>
            <TextField
              fullWidth
              label="Frecuencia Cardíaca"
              type="number"
              value={formData.frecuencia_cardiaca || ''}
              onChange={(e) => handleChange('frecuencia_cardiaca', e.target.value ? parseInt(e.target.value) : undefined)}
              InputProps={{ endAdornment: <InputAdornment position="end">lpm</InputAdornment> }}
              helperText="Normal: 60-100 lpm"
            />
          </Grid>

          <Grid item xs={6} sm={4}>
            <TextField
              fullWidth
              label="Intervalo PR"
              type="number"
              value={formData.intervalo_pr || ''}
              onChange={(e) => handleChange('intervalo_pr', e.target.value ? parseInt(e.target.value) : undefined)}
              InputProps={{ endAdornment: <InputAdornment position="end">ms</InputAdornment> }}
              helperText="Normal: 120-200 ms"
            />
          </Grid>

          <Grid item xs={6} sm={4}>
            <TextField
              fullWidth
              label="Duración QRS"
              type="number"
              value={formData.duracion_qrs || ''}
              onChange={(e) => handleChange('duracion_qrs', e.target.value ? parseInt(e.target.value) : undefined)}
              InputProps={{ endAdornment: <InputAdornment position="end">ms</InputAdornment> }}
              helperText="Normal: 80-120 ms"
            />
          </Grid>

          <Grid item xs={6} sm={4}>
            <TextField
              fullWidth
              label="Intervalo QT"
              type="number"
              value={formData.intervalo_qt || ''}
              onChange={(e) => handleChange('intervalo_qt', e.target.value ? parseInt(e.target.value) : undefined)}
              InputProps={{ endAdornment: <InputAdornment position="end">ms</InputAdornment> }}
              helperText="Normal: 350-450 ms"
            />
          </Grid>

          <Grid item xs={6} sm={4}>
            <TextField
              fullWidth
              label="Intervalo QTc"
              type="number"
              value={formData.intervalo_qtc || ''}
              onChange={(e) => handleChange('intervalo_qtc', e.target.value ? parseInt(e.target.value) : undefined)}
              InputProps={{ endAdornment: <InputAdornment position="end">ms</InputAdornment> }}
              helperText="Normal: 350-450 ms"
            />
          </Grid>

          <Grid item xs={6} sm={4}>
            <TextField
              fullWidth
              label="Eje QRS"
              type="number"
              value={formData.eje_qrs || ''}
              onChange={(e) => handleChange('eje_qrs', e.target.value ? parseInt(e.target.value) : undefined)}
              InputProps={{ endAdornment: <InputAdornment position="end">°</InputAdornment> }}
              helperText="Normal: -30 a 90°"
            />
          </Grid>

          {/* Ritmo */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" color="primary" gutterBottom sx={{ mt: 2 }}>
              Ritmo
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Tipo de Ritmo</InputLabel>
              <Select
                value={formData.ritmo}
                onChange={(e) => handleChange('ritmo', e.target.value)}
                label="Tipo de Ritmo"
              >
                <MenuItem value="sinusal">Sinusal</MenuItem>
                <MenuItem value="fibrilacion_auricular">Fibrilación Auricular</MenuItem>
                <MenuItem value="flutter_auricular">Flutter Auricular</MenuItem>
                <MenuItem value="taquicardia_supraventricular">Taquicardia Supraventricular</MenuItem>
                <MenuItem value="taquicardia_ventricular">Taquicardia Ventricular</MenuItem>
                <MenuItem value="bradicardia_sinusal">Bradicardia Sinusal</MenuItem>
                <MenuItem value="ritmo_nodal">Ritmo Nodal</MenuItem>
                <MenuItem value="ritmo_idioventricular">Ritmo Idioventricular</MenuItem>
                <MenuItem value="otro">Otro</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.ritmo_regular}
                  onChange={(e) => handleChange('ritmo_regular', e.target.checked)}
                />
              }
              label="Ritmo Regular"
            />
          </Grid>

          {/* Ondas y Segmentos */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" color="primary" gutterBottom sx={{ mt: 2 }}>
              Ondas y Segmentos (Opcional)
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Onda P</InputLabel>
              <Select
                value={formData.onda_p}
                onChange={(e) => handleChange('onda_p', e.target.value)}
                label="Onda P"
              >
                <MenuItem value=""><em>Seleccionar...</em></MenuItem>
                <MenuItem value="normal">Normal</MenuItem>
                <MenuItem value="ausente">Ausente</MenuItem>
                <MenuItem value="invertida">Invertida</MenuItem>
                <MenuItem value="bifasica">Bifásica</MenuItem>
                <MenuItem value="picuda">Picuda (P pulmonale)</MenuItem>
                <MenuItem value="ancha">Ancha (P mitrale)</MenuItem>
                <MenuItem value="variable">Variable</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Complejo QRS</InputLabel>
              <Select
                value={formData.complejo_qrs}
                onChange={(e) => handleChange('complejo_qrs', e.target.value)}
                label="Complejo QRS"
              >
                <MenuItem value=""><em>Seleccionar...</em></MenuItem>
                <MenuItem value="normal">Normal</MenuItem>
                <MenuItem value="ensanchado">Ensanchado</MenuItem>
                <MenuItem value="bloqueo_rama_derecha">Bloqueo de Rama Derecha</MenuItem>
                <MenuItem value="bloqueo_rama_izquierda">Bloqueo de Rama Izquierda</MenuItem>
                <MenuItem value="bajo_voltaje">Bajo Voltaje</MenuItem>
                <MenuItem value="alto_voltaje">Alto Voltaje</MenuItem>
                <MenuItem value="onda_q_patologica">Onda Q Patológica</MenuItem>
                <MenuItem value="fragmentado">Fragmentado</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Segmento ST</InputLabel>
              <Select
                value={formData.segmento_st}
                onChange={(e) => handleChange('segmento_st', e.target.value)}
                label="Segmento ST"
              >
                <MenuItem value=""><em>Seleccionar...</em></MenuItem>
                <MenuItem value="normal">Normal (Isoelétrico)</MenuItem>
                <MenuItem value="elevado">Elevado</MenuItem>
                <MenuItem value="deprimido">Deprimido</MenuItem>
                <MenuItem value="concavo">Cóncavo</MenuItem>
                <MenuItem value="convexo">Convexo</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Onda T</InputLabel>
              <Select
                value={formData.onda_t}
                onChange={(e) => handleChange('onda_t', e.target.value)}
                label="Onda T"
              >
                <MenuItem value=""><em>Seleccionar...</em></MenuItem>
                <MenuItem value="normal">Normal</MenuItem>
                <MenuItem value="invertida">Invertida</MenuItem>
                <MenuItem value="aplanada">Aplanada</MenuItem>
                <MenuItem value="picuda">Picuda</MenuItem>
                <MenuItem value="bifasica">Bifásica</MenuItem>
                <MenuItem value="hiperaguda">Hiperaguda</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
        )}

        {/* Pestaña 2: Subir Archivo */}
        {tabActual === 1 && (
          <Box>
            <SubirImagenEKG
              onParametrosExtraidos={handleParametrosEKGExtraidos}
            />
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          {estudioId ? 'Cerrar' : 'Cancelar'}
        </Button>
        
        {!estudioId && (
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={loading || !formData.fecha_estudio}
            startIcon={loading ? <CircularProgress size={20} /> : null}
          >
            {loading ? 'Guardando...' : 'Guardar y Analizar'}
          </Button>
        )}
        
        {estudioId && (
          <Button
            onClick={() => {
              onSuccess();
              handleClose();
            }}
            variant="contained"
            color="success"
          >
            Finalizar
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default FormularioEKG;
