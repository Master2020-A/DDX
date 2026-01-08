/**
 * Formulario simplificado para captura de Ecografía
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
  Chip,
  Box,
  Tabs,
  Tab
} from '@mui/material';
import { CrearEcografia, TIPOS_ECOGRAFIA } from '../../types/estudiosEspeciales';
import estudiosEspecialesService from '../../services/estudiosEspecialesService';
import SubirImagenEcografia from './SubirImagenEcografia';

interface Props {
  open: boolean;
  pacienteId: string;
  onClose: () => void;
  onSuccess: () => void;
}

const FormularioEcografia: React.FC<Props> = ({ open, pacienteId, onClose, onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [interpretacion, setInterpretacion] = useState<any>(null);
  const [tabActual, setTabActual] = useState(0);
  const [datosExtraidosExito, setDatosExtraidosExito] = useState(false);
  const [cantidadDatosExtraidos, setCantidadDatosExtraidos] = useState(0);
  
  const [formData, setFormData] = useState<CrearEcografia>({
    paciente_id: pacienteId,
    fecha_estudio: new Date().toISOString().slice(0, 16),
    motivo: '',
    indicacion_clinica: '',
    tipo_ecografia: 'abdominal',
    region_anatomica: '',
    via_acceso: '',
    es_obstetrica: false,
    edad_gestacional_semanas: undefined,
    numero_fetos: undefined,
    equipo_utilizado: '',
    transductor: '',
    modo: '2D',
    mediciones: [],
    hallazgos_organos: {},
    masas_detectadas: [],
    liquido_libre: false,
    cantidad_liquido: '',
    estudio_doppler: false,
    flujo_vascular: '',
    resistencia_vascular: '',
    calidad_estudio: '',
    limitaciones: '',
    birads: ''
  });

  const handleChange = (field: keyof CrearEcografia, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await estudiosEspecialesService.crearEcografia(formData);
      setInterpretacion(response.interpretacion);
      
      setTimeout(() => {
        onSuccess();
        onClose();
        resetForm();
      }, 3000);
      
    } catch (err: any) {
      console.error('Error al crear ecografía:', err);
      setError(err.response?.data?.detail || 'Error al crear la ecografía');
    } finally {
      setLoading(false);
    }
  };

  const handleParametrosEcografiaExtraidos = (parametros: any) => {
    console.log('🎯 Parámetros Ecografía extraídos:', parametros);
    
    // Contar cuántos datos se extrajeron
    let contador = 0;
    
    // Rellenar formulario con datos extraídos
    const nuevoFormData: any = { ...formData };
    
    if (parametros.tipo) { nuevoFormData.tipo_ecografia = parametros.tipo; contador++; }
    if (parametros.region_anatomica) { nuevoFormData.region_anatomica = parametros.region_anatomica; contador++; }
    if (parametros.modo) { nuevoFormData.modo = parametros.modo; contador++; }
    if (parametros.via_acceso) { nuevoFormData.via_acceso = parametros.via_acceso; contador++; }
    if (parametros.transductor) { nuevoFormData.transductor = parametros.transductor; contador++; }
    if (parametros.equipo) { nuevoFormData.equipo_utilizado = parametros.equipo; contador++; }
    if (parametros.es_obstetrica !== undefined) { nuevoFormData.es_obstetrica = parametros.es_obstetrica; contador++; }
    if (parametros.edad_gestacional) { nuevoFormData.edad_gestacional_semanas = parametros.edad_gestacional; contador++; }
    if (parametros.numero_fetos) { nuevoFormData.numero_fetos = parametros.numero_fetos; contador++; }
    if (parametros.calidad) { nuevoFormData.calidad_estudio = parametros.calidad; contador++; }
    if (parametros.limitaciones) { nuevoFormData.limitaciones_tecnicas = parametros.limitaciones; contador++; }
    
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
      tipo_ecografia: 'abdominal',
      region_anatomica: '',
      via_acceso: '',
      es_obstetrica: false,
      edad_gestacional_semanas: undefined,
      numero_fetos: undefined,
      equipo_utilizado: '',
      transductor: '',
      modo: '2D',
      mediciones: [],
      hallazgos_organos: {},
      masas_detectadas: [],
      liquido_libre: false,
      cantidad_liquido: '',
      estudio_doppler: false,
      flujo_vascular: '',
      resistencia_vascular: '',
      calidad_estudio: '',
      limitaciones: '',
      birads: ''
    });
    setInterpretacion(null);
    setError(null);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>📡 Nueva Ecografía</DialogTitle>
      
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
          <Alert severity={interpretacion.requiere_atencion ? 'warning' : 'success'} sx={{ mb: 2 }}>
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
              <InputLabel>Tipo de Ecografía</InputLabel>
              <Select
                value={formData.tipo_ecografia}
                onChange={(e) => handleChange('tipo_ecografia', e.target.value)}
                label="Tipo de Ecografía"
              >
                {TIPOS_ECOGRAFIA.map(tipo => (
                  <MenuItem key={tipo} value={tipo}>
                    {tipo.replace('_', ' ').charAt(0).toUpperCase() + tipo.replace('_', ' ').slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Motivo"
              value={formData.motivo}
              onChange={(e) => handleChange('motivo', e.target.value)}
              placeholder="Ej: Dolor abdominal, control prenatal"
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Región Anatómica"
              value={formData.region_anatomica}
              onChange={(e) => handleChange('region_anatomica', e.target.value)}
              placeholder="Ej: Abdomen superior, pelvis"
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
              placeholder="Ej: Descartar colelitiasis, evaluar embarazo"
            />
          </Grid>

          {/* Equipo y Técnica */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" color="primary" gutterBottom sx={{ mt: 2 }}>
              Equipo y Técnica
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={12} sm={4}>
            <FormControl fullWidth>
              <InputLabel>Modo / Dimensionalidad</InputLabel>
              <Select
                value={formData.modo}
                onChange={(e) => handleChange('modo', e.target.value)}
                label="Modo / Dimensionalidad"
              >
                <MenuItem value="2D">2D (Bidimensional)</MenuItem>
                <MenuItem value="3D">3D (Tridimensional)</MenuItem>
                <MenuItem value="4D">4D (Cuatridimensional - Tiempo Real)</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={4}>
            <FormControl fullWidth>
              <InputLabel>Vía de Acceso</InputLabel>
              <Select
                value={formData.via_acceso}
                onChange={(e) => handleChange('via_acceso', e.target.value)}
                label="Vía de Acceso"
              >
                <MenuItem value=""><em>Seleccionar...</em></MenuItem>
                <MenuItem value="transabdominal">Transabdominal</MenuItem>
                <MenuItem value="transvaginal">Transvaginal</MenuItem>
                <MenuItem value="transrectal">Transrectal</MenuItem>
                <MenuItem value="endocavitaria">Endocavitaria</MenuItem>
                <MenuItem value="superficial">Superficial</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="Transductor"
              value={formData.transductor}
              onChange={(e) => handleChange('transductor', e.target.value)}
              placeholder="Ej: Lineal 7.5 MHz, Convex 3.5 MHz"
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Equipo Utilizado"
              value={formData.equipo_utilizado}
              onChange={(e) => handleChange('equipo_utilizado', e.target.value)}
              placeholder="Ej: GE Voluson E10, Philips EPIQ"
            />
          </Grid>

          {/* Datos Obstétricos (si aplica) */}
          {formData.tipo_ecografia === 'obstetrica' && (
            <>
              <Grid item xs={12}>
                <Typography variant="subtitle1" color="primary" gutterBottom sx={{ mt: 2 }}>
                  Datos Obstétricos
                </Typography>
                <Divider sx={{ mb: 2 }} />
              </Grid>

              <Grid item xs={12} sm={4}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={formData.es_obstetrica}
                      onChange={(e) => handleChange('es_obstetrica', e.target.checked)}
                    />
                  }
                  label="Ecografía Obstétrica"
                />
              </Grid>

              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  type="number"
                  label="Edad Gestacional"
                  value={formData.edad_gestacional_semanas || ''}
                  onChange={(e) => handleChange('edad_gestacional_semanas', e.target.value ? parseInt(e.target.value) : undefined)}
                  InputProps={{ endAdornment: <InputAdornment position="end">semanas</InputAdornment> }}
                />
              </Grid>

              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  type="number"
                  label="Número de Fetos"
                  value={formData.numero_fetos || ''}
                  onChange={(e) => handleChange('numero_fetos', e.target.value ? parseInt(e.target.value) : undefined)}
                />
              </Grid>
            </>
          )}

          {/* Hallazgos por Modo */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" color="primary" gutterBottom sx={{ mt: 2 }}>
              Hallazgos - {formData.modo}
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          {/* 2D - Hallazgos */}
          {formData.modo === '2D' && (
            <>
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  <strong>Hallazgos Normales (2D):</strong> Anatomía bien definida, contornos suaves, órganos con morfología y simetría esperadas
                </Typography>
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Anatomía y Morfología</InputLabel>
                  <Select
                    value={formData.hallazgos_organos?.anatomia || ''}
                    onChange={(e) => handleChange('hallazgos_organos', { ...formData.hallazgos_organos, anatomia: e.target.value })}
                    label="Anatomía y Morfología"
                  >
                    <MenuItem value=""><em>Seleccionar...</em></MenuItem>
                    <MenuItem value="anatomia_bien_definida">Anatomía bien definida - Normal</MenuItem>
                    <MenuItem value="contornos_suaves">Contornos suaves - Normal</MenuItem>
                    <MenuItem value="morfologia_simetria_esperadas">Órganos con morfología y simetría esperadas - Normal</MenuItem>
                    <MenuItem value="malformaciones">Malformaciones detectadas</MenuItem>
                    <MenuItem value="masas">Masas o tumores</MenuItem>
                    <MenuItem value="asimetrias">Asimetrías</MenuItem>
                    <MenuItem value="perdida_diferenciacion">Pérdida de diferenciación tisular</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </>
          )}

          {/* 3D - Hallazgos */}
          {formData.modo === '3D' && (
            <>
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  <strong>Hallazgos Normales (3D):</strong> Superficies fetales o anatómicas completas y simétricas, ausencia de defectos estructurales
                </Typography>
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Superficies y Estructuras</InputLabel>
                  <Select
                    value={formData.hallazgos_organos?.superficies || ''}
                    onChange={(e) => handleChange('hallazgos_organos', { ...formData.hallazgos_organos, superficies: e.target.value })}
                    label="Superficies y Estructuras"
                  >
                    <MenuItem value=""><em>Seleccionar...</em></MenuItem>
                    <MenuItem value="superficies_completas">Superficies fetales/anatómicas completas - Normal</MenuItem>
                    <MenuItem value="simetricas">Simétricas - Normal</MenuItem>
                    <MenuItem value="ausencia_defectos">Ausencia de defectos estructurales - Normal</MenuItem>
                    <MenuItem value="hendiduras_faciales">Hendiduras faciales (labio/paladar hendido)</MenuItem>
                    <MenuItem value="craneosinostosis">Craneosinostosis</MenuItem>
                    <MenuItem value="defectos_tubo_neural">Defectos del tubo neural visibles en reconstrucción</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </>
          )}

          {/* 4D - Hallazgos */}
          {formData.modo === '4D' && (
            <>
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  <strong>Hallazgos Normales (4D):</strong> Movimientos fetales coordinados (succión, parpadeo, giros), flujo dinámico normal en estructuras
                </Typography>
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Movimientos y Dinámica</InputLabel>
                  <Select
                    value={formData.hallazgos_organos?.movimientos || ''}
                    onChange={(e) => handleChange('hallazgos_organos', { ...formData.hallazgos_organos, movimientos: e.target.value })}
                    label="Movimientos y Dinámica"
                  >
                    <MenuItem value=""><em>Seleccionar...</em></MenuItem>
                    <MenuItem value="movimientos_coordinados">Movimientos fetales coordinados - Normal</MenuItem>
                    <MenuItem value="succion_parpadeo">Succión, parpadeo, giros - Normal</MenuItem>
                    <MenuItem value="flujo_dinamico_normal">Flujo dinámico normal - Normal</MenuItem>
                    <MenuItem value="movimientos_ausentes">Movimientos ausentes o descoordinados</MenuItem>
                    <MenuItem value="anomalias_dinamicas">Anomalías dinámicas (ej. arritmias visibles en corazón fetal)</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </>
          )}

          {/* Estudio Doppler */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" color="primary" gutterBottom sx={{ mt: 2 }}>
              Estudio Doppler (Color / Power / Spectral)
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={12} sm={4}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.estudio_doppler}
                  onChange={(e) => handleChange('estudio_doppler', e.target.checked)}
                />
              }
              label="Realizar Estudio Doppler"
            />
          </Grid>

          {formData.estudio_doppler && (
            <>
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  <strong>Hallazgos Normales:</strong> Flujo laminar, direccional, sin turbulencia. Índices Doppler normales (ej. IR, S/D según contexto)
                </Typography>
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Flujo Vascular</InputLabel>
                  <Select
                    value={formData.flujo_vascular}
                    onChange={(e) => handleChange('flujo_vascular', e.target.value)}
                    label="Flujo Vascular"
                  >
                    <MenuItem value=""><em>Seleccionar...</em></MenuItem>
                    <MenuItem value="flujo_laminar">Flujo laminar - Normal</MenuItem>
                    <MenuItem value="flujo_direccional">Flujo direccional - Normal</MenuItem>
                    <MenuItem value="sin_turbulencia">Sin turbulencia - Normal</MenuItem>
                    <MenuItem value="flujo_ausente">Flujo ausente</MenuItem>
                    <MenuItem value="flujo_revertido">Flujo revertido</MenuItem>
                    <MenuItem value="flujo_turbulento">Flujo turbulento</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Resistencia Vascular</InputLabel>
                  <Select
                    value={formData.resistencia_vascular}
                    onChange={(e) => handleChange('resistencia_vascular', e.target.value)}
                    label="Resistencia Vascular"
                  >
                    <MenuItem value=""><em>Seleccionar...</em></MenuItem>
                    <MenuItem value="indices_normales">Índices Doppler normales - Normal</MenuItem>
                    <MenuItem value="ir_normal">IR normal (según contexto) - Normal</MenuItem>
                    <MenuItem value="sd_normal">S/D normal - Normal</MenuItem>
                    <MenuItem value="indices_elevados">Índices elevados (ej. IR &gt;0.7 en arterias uterinas)</MenuItem>
                    <MenuItem value="vascularizacion_aumentada">Vascularización aumentada (sospecha de malignidad)</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </>
          )}

          {/* Hallazgos Adicionales */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" color="primary" gutterBottom sx={{ mt: 2 }}>
              Hallazgos Adicionales
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={12} sm={4}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.liquido_libre}
                  onChange={(e) => handleChange('liquido_libre', e.target.checked)}
                />
              }
              label="Líquido Libre"
            />
          </Grid>

          {formData.liquido_libre && (
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth>
                <InputLabel>Cantidad de Líquido</InputLabel>
                <Select
                  value={formData.cantidad_liquido}
                  onChange={(e) => handleChange('cantidad_liquido', e.target.value)}
                  label="Cantidad de Líquido"
                >
                  <MenuItem value=""><em>Seleccionar...</em></MenuItem>
                  <MenuItem value="escaso">Escaso</MenuItem>
                  <MenuItem value="moderado">Moderado</MenuItem>
                  <MenuItem value="abundante">Abundante</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          )}

          {/* Calidad del Estudio */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" color="primary" gutterBottom sx={{ mt: 2 }}>
              Calidad del Estudio
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Calidad del Estudio</InputLabel>
              <Select
                value={formData.calidad_estudio}
                onChange={(e) => handleChange('calidad_estudio', e.target.value)}
                label="Calidad del Estudio"
              >
                <MenuItem value=""><em>Seleccionar...</em></MenuItem>
                <MenuItem value="excelente">Excelente</MenuItem>
                <MenuItem value="buena">Buena</MenuItem>
                <MenuItem value="regular">Regular</MenuItem>
                <MenuItem value="limitada">Limitada</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Limitaciones"
              value={formData.limitaciones}
              onChange={(e) => handleChange('limitaciones', e.target.value)}
              placeholder="Ej: Obesidad, gas intestinal, paciente poco cooperador"
            />
          </Grid>

          {/* BI-RADS (solo para ecografía mamaria) */}
          {formData.tipo_ecografia === 'mamaria' && (
            <>
              <Grid item xs={12}>
                <Typography variant="subtitle1" color="primary" gutterBottom sx={{ mt: 2 }}>
                  Clasificación BI-RADS
                </Typography>
                <Divider sx={{ mb: 2 }} />
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>BI-RADS</InputLabel>
                  <Select
                    value={formData.birads}
                    onChange={(e) => handleChange('birads', e.target.value)}
                    label="BI-RADS"
                  >
                    <MenuItem value=""><em>Seleccionar...</em></MenuItem>
                    <MenuItem value="0">0 - Incompleto (requiere evaluación adicional)</MenuItem>
                    <MenuItem value="1">1 - Negativo (normal)</MenuItem>
                    <MenuItem value="2">2 - Hallazgo benigno</MenuItem>
                    <MenuItem value="3">3 - Probablemente benigno (seguimiento corto)</MenuItem>
                    <MenuItem value="4">4 - Sospechoso (considerar biopsia)</MenuItem>
                    <MenuItem value="5">5 - Altamente sugestivo de malignidad</MenuItem>
                    <MenuItem value="6">6 - Malignidad comprobada por biopsia</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </>
          )}
        </Grid>
        )}

        {/* Pestaña 2: Subir Archivo */}
        {tabActual === 1 && (
          <Box>
            <SubirImagenEcografia
              onParametrosExtraidos={handleParametrosEcografiaExtraidos}
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

export default FormularioEcografia;
