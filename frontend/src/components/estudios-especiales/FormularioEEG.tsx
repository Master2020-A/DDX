/**
 * Formulario simplificado para captura de Electroencefalograma (EEG)
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
  Typography,
  Divider,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  InputAdornment,
  Tabs,
  Tab,
  Box
} from '@mui/material';
import { CrearEstudioEEG } from '../../types/estudiosEspeciales';
import estudiosEspecialesService from '../../services/estudiosEspecialesService';
import SubirImagenEEG from './SubirImagenEEG';

interface Props {
  open: boolean;
  pacienteId: string;
  onClose: () => void;
  onSuccess: () => void;
}

const FormularioEEG: React.FC<Props> = ({ open, pacienteId, onClose, onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [interpretacion, setInterpretacion] = useState<any>(null);
  const [tabActual, setTabActual] = useState(0);
  const [datosExtraidosExito, setDatosExtraidosExito] = useState(false);
  const [cantidadDatosExtraidos, setCantidadDatosExtraidos] = useState(0);
  
  const [formData, setFormData] = useState<CrearEstudioEEG>({
    paciente_id: pacienteId,
    fecha_estudio: new Date().toISOString().slice(0, 16),
    motivo: '',
    indicacion_clinica: '',
    tipo_estudio: 'basal',
    duracion_minutos: 30,
    edad_paciente: undefined,
    medicamentos_actuales: '',
    estado_conciencia: '',
    cooperacion_paciente: '',
    actividad_fondo: '',
    frecuencia_dominante: undefined,
    amplitud_promedio: undefined,
    simetria: '',
    reactividad: '',
    ritmo_alfa: '',
    ritmo_beta: '',
    ritmo_theta: '',
    ritmo_delta: '',
    ondas_agudas: false,
    espigas: false,
    complejos_punta_onda: false,
    actividad_paroxistica: false,
    enlentecimiento: '',
    localizacion_hallazgos: [],
    lateralidad: '',
    fotoestimulacion: '',
    hiperventilacion: '',
    privacion_sueno: ''
  });

  const handleChange = (field: keyof CrearEstudioEEG, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await estudiosEspecialesService.crearEstudioEEG(formData);
      setInterpretacion(response.interpretacion);
      
      setTimeout(() => {
        onSuccess();
        onClose();
        resetForm();
      }, 3000);
      
    } catch (err: any) {
      console.error('Error al crear EEG:', err);
      setError(err.response?.data?.detail || 'Error al crear el estudio de EEG');
    } finally {
      setLoading(false);
    }
  };

  const handleParametrosEEGExtraidos = (parametros: any) => {
    console.log('🎯 Parámetros EEG extraídos:', parametros);
    
    // Contar cuántos datos se extrajeron
    let contador = 0;
    
    // Rellenar formulario con datos extraídos
    const nuevoFormData: any = { ...formData };
    
    if (parametros.tipo_estudio) { nuevoFormData.tipo_estudio = parametros.tipo_estudio; contador++; }
    if (parametros.duracion_minutos) { nuevoFormData.duracion_minutos = parametros.duracion_minutos; contador++; }
    if (parametros.edad_paciente) { nuevoFormData.edad_paciente = parametros.edad_paciente; contador++; }
    if (parametros.estado_conciencia) { nuevoFormData.estado_conciencia = parametros.estado_conciencia; contador++; }
    if (parametros.cooperacion_paciente) { nuevoFormData.cooperacion_paciente = parametros.cooperacion_paciente; contador++; }
    if (parametros.actividad_fondo) { nuevoFormData.actividad_fondo = parametros.actividad_fondo; contador++; }
    if (parametros.frecuencia_dominante) { nuevoFormData.frecuencia_dominante = parametros.frecuencia_dominante; contador++; }
    if (parametros.amplitud_promedio) { nuevoFormData.amplitud_promedio = parametros.amplitud_promedio; contador++; }
    if (parametros.simetria) { nuevoFormData.simetria = parametros.simetria; contador++; }
    if (parametros.reactividad) { nuevoFormData.reactividad = parametros.reactividad; contador++; }
    if (parametros.ritmo_alfa) { nuevoFormData.ritmo_alfa = parametros.ritmo_alfa; contador++; }
    if (parametros.ritmo_beta) { nuevoFormData.ritmo_beta = parametros.ritmo_beta; contador++; }
    if (parametros.ritmo_theta) { nuevoFormData.ritmo_theta = parametros.ritmo_theta; contador++; }
    if (parametros.ritmo_delta) { nuevoFormData.ritmo_delta = parametros.ritmo_delta; contador++; }
    if (parametros.lateralidad) { nuevoFormData.lateralidad = parametros.lateralidad; contador++; }
    if (parametros.hiperventilacion) { nuevoFormData.hiperventilacion = parametros.hiperventilacion; contador++; }
    if (parametros.privacion_sueno) { nuevoFormData.privacion_sueno = parametros.privacion_sueno; contador++; }
    
    // Hallazgos anormales (booleanos)
    if (parametros.ondas_agudas !== undefined) { nuevoFormData.ondas_agudas = parametros.ondas_agudas; contador++; }
    if (parametros.espigas !== undefined) { nuevoFormData.espigas = parametros.espigas; contador++; }
    if (parametros.complejos_punta_onda !== undefined) { nuevoFormData.complejos_punta_onda = parametros.complejos_punta_onda; contador++; }
    if (parametros.actividad_paroxistica !== undefined) { nuevoFormData.actividad_paroxistica = parametros.actividad_paroxistica; contador++; }
    
    // Actualizar formulario
    setFormData(nuevoFormData);
    
    // Mostrar mensaje de éxito con advertencia de campos faltantes
    setCantidadDatosExtraidos(contador);
    setDatosExtraidosExito(true);
    
    // Mostrar campos faltantes si existen
    if (parametros.campos_faltantes && parametros.campos_faltantes.length > 0) {
      const camposFaltantes = parametros.campos_faltantes.join(', ');
      setError(`⚠️ Campos que requieren llenado manual: ${camposFaltantes}`);
      setTimeout(() => setError(null), 10000); // Ocultar después de 10 segundos
    }
    
    console.log(`✅ ${contador} datos extraídos y rellenados en el formulario`);
    
    // Cambiar a pestaña de captura manual para ver los datos
    setTabActual(0);
    
    // Ocultar mensaje después de 5 segundos
    setTimeout(() => {
      setDatosExtraidosExito(false);
    }, 5000);
  };

  const resetForm = () => {
    setFormData({
      paciente_id: pacienteId,
      fecha_estudio: new Date().toISOString().slice(0, 16),
      motivo: '',
      indicacion_clinica: '',
      tipo_estudio: 'basal',
      duracion_minutos: 30,
      edad_paciente: undefined,
      medicamentos_actuales: '',
      estado_conciencia: '',
      cooperacion_paciente: '',
      actividad_fondo: '',
      frecuencia_dominante: undefined,
      amplitud_promedio: undefined,
      simetria: '',
      reactividad: '',
      ritmo_alfa: '',
      ritmo_beta: '',
      ritmo_theta: '',
      ritmo_delta: '',
      ondas_agudas: false,
      espigas: false,
      complejos_punta_onda: false,
      actividad_paroxistica: false,
      enlentecimiento: '',
      localizacion_hallazgos: [],
      lateralidad: '',
      fotoestimulacion: '',
      hiperventilacion: '',
      privacion_sueno: ''
    });
    setInterpretacion(null);
    setError(null);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>🧠 Nuevo Electroencefalograma (EEG)</DialogTitle>
      
      <DialogContent>
        {/* Pestañas */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs value={tabActual} onChange={(_e, v) => setTabActual(v)}>
            <Tab label="📝 Captura Manual" />
            <Tab label="📄 Subir Archivo" />
          </Tabs>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        
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
          <Alert severity={interpretacion.es_critico ? 'error' : interpretacion.requiere_atencion ? 'warning' : 'success'} sx={{ mb: 2 }}>
            <Typography variant="subtitle2"><strong>Interpretación:</strong></Typography>
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
            <FormControl fullWidth required>
              <InputLabel>Tipo de Estudio</InputLabel>
              <Select
                value={formData.tipo_estudio}
                onChange={(e) => handleChange('tipo_estudio', e.target.value)}
                label="Tipo de Estudio"
              >
                <MenuItem value="basal">Basal</MenuItem>
                <MenuItem value="sueno">Sueño</MenuItem>
                <MenuItem value="vigilia">Vigilia</MenuItem>
                <MenuItem value="prolongado">Prolongado (24h)</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Motivo"
              value={formData.motivo}
              onChange={(e) => handleChange('motivo', e.target.value)}
              placeholder="Ej: Crisis convulsivas, cefalea"
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              type="number"
              label="Duración"
              value={formData.duracion_minutos || ''}
              onChange={(e) => handleChange('duracion_minutos', e.target.value ? parseInt(e.target.value) : undefined)}
              InputProps={{ endAdornment: <InputAdornment position="end">min</InputAdornment> }}
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
              placeholder="Ej: Descartar epilepsia, evaluar encefalopatía"
            />
          </Grid>

          {/* Datos del Paciente */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" color="primary" gutterBottom sx={{ mt: 2 }}>
              Datos del Paciente
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              type="number"
              label="Edad"
              value={formData.edad_paciente || ''}
              onChange={(e) => handleChange('edad_paciente', e.target.value ? parseInt(e.target.value) : undefined)}
              InputProps={{ endAdornment: <InputAdornment position="end">años</InputAdornment> }}
            />
          </Grid>

          <Grid item xs={12} sm={4}>
            <FormControl fullWidth>
              <InputLabel>Estado de Conciencia</InputLabel>
              <Select
                value={formData.estado_conciencia}
                onChange={(e) => handleChange('estado_conciencia', e.target.value)}
                label="Estado de Conciencia"
              >
                <MenuItem value=""><em>Seleccionar...</em></MenuItem>
                <MenuItem value="despierto">Despierto</MenuItem>
                <MenuItem value="somnoliento">Somnoliento</MenuItem>
                <MenuItem value="dormido">Dormido</MenuItem>
                <MenuItem value="estuporoso">Estuporoso</MenuItem>
                <MenuItem value="comatoso">Comatoso</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={4}>
            <FormControl fullWidth>
              <InputLabel>Cooperación</InputLabel>
              <Select
                value={formData.cooperacion_paciente}
                onChange={(e) => handleChange('cooperacion_paciente', e.target.value)}
                label="Cooperación"
              >
                <MenuItem value=""><em>Seleccionar...</em></MenuItem>
                <MenuItem value="adecuada">Adecuada</MenuItem>
                <MenuItem value="limitada">Limitada</MenuItem>
                <MenuItem value="no_coopera">No Coopera</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Medicamentos Actuales"
              value={formData.medicamentos_actuales}
              onChange={(e) => handleChange('medicamentos_actuales', e.target.value)}
              placeholder="Ej: Ácido valproico 500mg, levetiracetam 1000mg"
            />
          </Grid>

          {/* Frecuencia (Ritmos Cerebrales) */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" color="primary" gutterBottom sx={{ mt: 2 }}>
              Frecuencia - Ritmos Cerebrales
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Ritmo Delta (0.5-4 Hz)</InputLabel>
              <Select
                value={formData.ritmo_delta}
                onChange={(e) => handleChange('ritmo_delta', e.target.value)}
                label="Ritmo Delta (0.5-4 Hz)"
              >
                <MenuItem value=""><em>Seleccionar...</em></MenuItem>
                <MenuItem value="normal_sueno_profundo">Normal (sueño profundo)</MenuItem>
                <MenuItem value="excesivo_vigilia">Excesivo en vigilia (anormal)</MenuItem>
                <MenuItem value="ausente">Ausente</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Ritmo Theta (4-8 Hz)</InputLabel>
              <Select
                value={formData.ritmo_theta}
                onChange={(e) => handleChange('ritmo_theta', e.target.value)}
                label="Ritmo Theta (4-8 Hz)"
              >
                <MenuItem value=""><em>Seleccionar...</em></MenuItem>
                <MenuItem value="normal_ninos">Normal (niños/somnolencia)</MenuItem>
                <MenuItem value="excesivo">Excesivo (anormal)</MenuItem>
                <MenuItem value="ausente">Ausente</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Ritmo Alfa (8-13 Hz)</InputLabel>
              <Select
                value={formData.ritmo_alfa}
                onChange={(e) => handleChange('ritmo_alfa', e.target.value)}
                label="Ritmo Alfa (8-13 Hz)"
              >
                <MenuItem value=""><em>Seleccionar...</em></MenuItem>
                <MenuItem value="normal_vigilia_relajada">Normal (vigilia relajada, ojos cerrados)</MenuItem>
                <MenuItem value="ausente">Ausente</MenuItem>
                <MenuItem value="asimetrico">Asimétrico</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Ritmo Beta (13-30 Hz)</InputLabel>
              <Select
                value={formData.ritmo_beta}
                onChange={(e) => handleChange('ritmo_beta', e.target.value)}
                label="Ritmo Beta (13-30 Hz)"
              >
                <MenuItem value=""><em>Seleccionar...</em></MenuItem>
                <MenuItem value="normal_vigilia_activa">Normal (vigilia activa)</MenuItem>
                <MenuItem value="excesivo">Excesivo (medicamentos)</MenuItem>
                <MenuItem value="ausente">Ausente</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              type="number"
              label="Frecuencia Dominante"
              value={formData.frecuencia_dominante || ''}
              onChange={(e) => handleChange('frecuencia_dominante', e.target.value ? parseFloat(e.target.value) : undefined)}
              InputProps={{ endAdornment: <InputAdornment position="end">Hz</InputAdornment> }}
              helperText="Gamma: >30 Hz (procesamiento cognitivo)"
            />
          </Grid>

          {/* Amplitud */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" color="primary" gutterBottom sx={{ mt: 2 }}>
              Amplitud
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              type="number"
              label="Amplitud Promedio"
              value={formData.amplitud_promedio || ''}
              onChange={(e) => handleChange('amplitud_promedio', e.target.value ? parseFloat(e.target.value) : undefined)}
              InputProps={{ endAdornment: <InputAdornment position="end">μV</InputAdornment> }}
              helperText="Normal: 10-100 μV"
            />
          </Grid>

          {/* Morfología */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" color="primary" gutterBottom sx={{ mt: 2 }}>
              Morfología
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Actividad de Fondo</InputLabel>
              <Select
                value={formData.actividad_fondo}
                onChange={(e) => handleChange('actividad_fondo', e.target.value)}
                label="Actividad de Fondo"
              >
                <MenuItem value=""><em>Seleccionar...</em></MenuItem>
                <MenuItem value="ondas_sinusoidales_suaves">Ondas sinusoidales suaves (normal)</MenuItem>
                <MenuItem value="espigas">Espigas</MenuItem>
                <MenuItem value="ondas_agudas">Ondas agudas</MenuItem>
                <MenuItem value="complejos_punta_onda">Complejos punta-onda</MenuItem>
                <MenuItem value="polipuntas">Polipuntas</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          {/* Localización */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" color="primary" gutterBottom sx={{ mt: 2 }}>
              Localización
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Localización Principal</InputLabel>
              <Select
                value={formData.lateralidad}
                onChange={(e) => handleChange('lateralidad', e.target.value)}
                label="Localización Principal"
              >
                <MenuItem value=""><em>Seleccionar...</em></MenuItem>
                <MenuItem value="alfa_posterior_occipital">Alfa posterior (occipital) - Normal</MenuItem>
                <MenuItem value="beta_frontal">Beta frontal - Normal</MenuItem>
                <MenuItem value="actividad_lenta_focal">Actividad lenta focal (lesión)</MenuItem>
                <MenuItem value="epileptiforme_focal">Epileptiforme focal</MenuItem>
                <MenuItem value="epileptiforme_multifocal">Epileptiforme multifocal</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          {/* Simetría */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" color="primary" gutterBottom sx={{ mt: 2 }}>
              Simetría
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Simetría Interhemisférica</InputLabel>
              <Select
                value={formData.simetria}
                onChange={(e) => handleChange('simetria', e.target.value)}
                label="Simetría Interhemisférica"
              >
                <MenuItem value=""><em>Seleccionar...</em></MenuItem>
                <MenuItem value="simetrica">Simétrica (diferencias &lt;10-20%) - Normal</MenuItem>
                <MenuItem value="asimetria_marcada">Asimetría marcada (tumor, ACV, encefalitis)</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          {/* Sincronía */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" color="primary" gutterBottom sx={{ mt: 2 }}>
              Sincronía
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Sincronía</InputLabel>
              <Select
                value={formData.enlentecimiento}
                onChange={(e) => handleChange('enlentecimiento', e.target.value)}
                label="Sincronía"
              >
                <MenuItem value=""><em>Seleccionar...</em></MenuItem>
                <MenuItem value="coherencia_ritmica">Coherencia rítmica entre regiones - Normal</MenuItem>
                <MenuItem value="desincronia_persistente">Desincronía persistente</MenuItem>
                <MenuItem value="actividad_desorganizada">Actividad desorganizada</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          {/* Reactividad */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" color="primary" gutterBottom sx={{ mt: 2 }}>
              Reactividad
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Reactividad</InputLabel>
              <Select
                value={formData.reactividad}
                onChange={(e) => handleChange('reactividad', e.target.value)}
                label="Reactividad"
              >
                <MenuItem value=""><em>Seleccionar...</em></MenuItem>
                <MenuItem value="bloqueo_alfa_normal">Bloqueo del alfa al abrir ojos - Normal</MenuItem>
                <MenuItem value="cambios_con_estimulos">Cambios con estímulos - Normal</MenuItem>
                <MenuItem value="ausencia_reactividad">Ausencia de reactividad (encefalopatía grave, coma, muerte cerebral)</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          {/* Patrones Transitorios */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" color="primary" gutterBottom sx={{ mt: 2 }}>
              Patrones Transitorios
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Patrones Transitorios</InputLabel>
              <Select
                value={formData.fotoestimulacion}
                onChange={(e) => handleChange('fotoestimulacion', e.target.value)}
                label="Patrones Transitorios"
              >
                <MenuItem value=""><em>Seleccionar...</em></MenuItem>
                <MenuItem value="complejos_k_husos">Complejos K, husos de sueño (etapa N2) - Normal</MenuItem>
                <MenuItem value="pleds_gpeds">PLEDs/GPEDs (encefalitis)</MenuItem>
                <MenuItem value="trenes_espigas_vigilia">Trenes de espigas en vigilia</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          {/* Hallazgos Anormales */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" color="primary" gutterBottom sx={{ mt: 2 }}>
              Hallazgos Anormales
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>
          
          <Grid item xs={6} sm={3}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.ondas_agudas}
                  onChange={(e) => handleChange('ondas_agudas', e.target.checked)}
                />
              }
              label="Ondas Agudas"
            />
          </Grid>

          <Grid item xs={6} sm={3}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.espigas}
                  onChange={(e) => handleChange('espigas', e.target.checked)}
                />
              }
              label="Espigas"
            />
          </Grid>

          <Grid item xs={6} sm={3}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.complejos_punta_onda}
                  onChange={(e) => handleChange('complejos_punta_onda', e.target.checked)}
                />
              }
              label="Complejos Punta-Onda"
            />
          </Grid>

          <Grid item xs={6} sm={3}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.actividad_paroxistica}
                  onChange={(e) => handleChange('actividad_paroxistica', e.target.checked)}
                />
              }
              label="Actividad Paroxística"
            />
          </Grid>

          {/* Pruebas de Activación */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" color="primary" gutterBottom sx={{ mt: 2 }}>
              Pruebas de Activación
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={12} sm={4}>
            <FormControl fullWidth>
              <InputLabel>Hiperventilación</InputLabel>
              <Select
                value={formData.hiperventilacion}
                onChange={(e) => handleChange('hiperventilacion', e.target.value)}
                label="Hiperventilación"
              >
                <MenuItem value=""><em>No realizada</em></MenuItem>
                <MenuItem value="sin_cambios">Sin cambios</MenuItem>
                <MenuItem value="enlentecimiento_difuso">Enlentecimiento difuso</MenuItem>
                <MenuItem value="actividad_epileptiforme">Actividad epileptiforme</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={4}>
            <FormControl fullWidth>
              <InputLabel>Privación de Sueño</InputLabel>
              <Select
                value={formData.privacion_sueno}
                onChange={(e) => handleChange('privacion_sueno', e.target.value)}
                label="Privación de Sueño"
              >
                <MenuItem value=""><em>No realizada</em></MenuItem>
                <MenuItem value="sin_cambios">Sin cambios</MenuItem>
                <MenuItem value="actividad_epileptiforme">Actividad epileptiforme</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
        )}

        {/* Pestaña 2: Subir Archivo */}
        {tabActual === 1 && (
          <Box>
            <SubirImagenEEG
              onParametrosExtraidos={handleParametrosEEGExtraidos}
            />
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={loading}>Cancelar</Button>
        <Button onClick={handleSubmit} variant="contained" disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : null}>
          {loading ? 'Guardando...' : 'Guardar y Analizar'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default FormularioEEG;
