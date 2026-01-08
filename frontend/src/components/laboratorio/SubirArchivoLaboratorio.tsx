/**
 * Componente para subir archivos PDF/Imágenes de laboratorio y extraer datos automáticamente
 */
import React, { useState } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  Alert,
  CircularProgress,
  LinearProgress,
  Chip,
  Divider,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  MenuItem
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  CheckCircle as CheckIcon,
  Close as CloseIcon,
  Description as PdfIcon,
  Image as ImageIcon,
  Science as ScienceIcon,
  Add as AddIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import laboratorioService from '@/services/laboratorioService';

interface SubirArchivoLaboratorioProps {
  pacienteId: string;
  consultaId?: string;
  onSuccess?: (prueba: any) => void;
  onCancel?: () => void;
}

interface ParametroEditable {
  parametro: string;
  valor: number;
  unidad?: string;
  rango_min?: number;
  rango_max?: number;
  esNuevo?: boolean;
}

const UNIDADES_COMUNES = [
  'mg/dL',
  'g/dL',
  'mEq/L',
  'mmol/L',
  'U/L',
  'UI/L',
  'ng/mL',
  'pg/mL',
  'µg/dL',
  'µU/mL',
  'K/µL',
  'M/µL',
  '%',
  'fL',
  'pg',
  'g/L',
  'mm/h'
];

const SubirArchivoLaboratorio: React.FC<SubirArchivoLaboratorioProps> = ({
  pacienteId,
  consultaId,
  onSuccess,
  onCancel
}) => {
  const [archivo, setArchivo] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [extraccion, setExtraccion] = useState<any>(null);
  const [mostrarDialogoConfirmacion, setMostrarDialogoConfirmacion] = useState(false);
  const [parametrosEditables, setParametrosEditables] = useState<ParametroEditable[]>([]);
  const [nuevoParametro, setNuevoParametro] = useState('');
  const [nuevoValor, setNuevoValor] = useState('');
  const [nuevaUnidad, setNuevaUnidad] = useState('mg/dL');
  const [rangos, setRangos] = useState<any[]>([]);

  const tiposPermitidos = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff'];
  const extensionesPermitidas = ['.pdf', '.jpg', '.jpeg', '.png', '.bmp', '.tiff'];

  const handleArchivoSeleccionado = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Verificar tipo de archivo
      const extension = '.' + file.name.split('.').pop()?.toLowerCase();
      if (!extensionesPermitidas.includes(extension)) {
        setError(`Tipo de archivo no soportado. Use: ${extensionesPermitidas.join(', ')}`);
        return;
      }

      setArchivo(file);
      setError(null);
      setExtraccion(null);
    }
  };

  const handleExtraerDatos = async () => {
    if (!archivo) return;

    setLoading(true);
    setError(null);

    try {
      const resultado = await laboratorioService.extraerDesdeArchivo(
        archivo,
        pacienteId,
        consultaId
      );

      if (resultado.exito && resultado.parametros_encontrados > 0) {
        setExtraccion(resultado);
        
        // Cargar rangos de referencia del área detectada
        let rangosData: any[] = [];
        try {
          rangosData = await laboratorioService.obtenerRangos(resultado.area_sugerida);
          setRangos(rangosData);
        } catch (err) {
          console.error('Error cargando rangos:', err);
        }
        
        // Inicializar parámetros editables con los extraídos
        const parametrosIniciales: ParametroEditable[] = Object.entries(resultado.resultados_extraidos).map(
          ([parametro, valor]: [string, any]) => {
            // Buscar rango de referencia para este parámetro
            const rango = rangosData?.find((r: any) => 
              r.parametro.toLowerCase() === parametro.toLowerCase()
            );
            
            return {
              parametro,
              valor: parseFloat(valor),
              unidad: rango?.unidad || 'mg/dL',
              rango_min: rango?.valor_min,
              rango_max: rango?.valor_max,
              esNuevo: false
            };
          }
        );
        setParametrosEditables(parametrosIniciales);
        setNuevoParametro('');
        setNuevoValor('');
        setNuevaUnidad('mg/dL');
        
        setMostrarDialogoConfirmacion(true);
      } else {
        setError('No se encontraron parámetros de laboratorio en el archivo. Intente con otro archivo o capture manualmente.');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al extraer datos del archivo');
    } finally {
      setLoading(false);
    }
  };

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
    if (parametrosEditables.some(p => p.parametro.toLowerCase() === nuevoParametro.toLowerCase())) {
      setError('Este parámetro ya existe');
      return;
    }

    // Buscar rango de referencia
    const rango = rangos.find((r: any) => 
      r.parametro.toLowerCase() === nuevoParametro.toLowerCase()
    );

    setParametrosEditables([
      ...parametrosEditables,
      {
        parametro: nuevoParametro.trim(),
        valor: valor,
        unidad: nuevaUnidad,
        rango_min: rango?.valor_min,
        rango_max: rango?.valor_max,
        esNuevo: true
      }
    ]);

    setNuevoParametro('');
    setNuevoValor('');
    setError(null);
  };

  const handleEliminarParametro = (index: number) => {
    setParametrosEditables(parametrosEditables.filter((_, i) => i !== index));
  };

  const handleActualizarValor = (index: number, nuevoValor: string) => {
    const valor = parseFloat(nuevoValor);
    if (!isNaN(valor)) {
      const nuevosParametros = [...parametrosEditables];
      nuevosParametros[index].valor = valor;
      setParametrosEditables(nuevosParametros);
    }
  };

  const handleCrearPrueba = async () => {
    if (!extraccion || parametrosEditables.length === 0) return;

    setLoading(true);
    setError(null);

    try {
      // Crear prueba con los parámetros editables (incluyendo los agregados manualmente)
      const resultados = parametrosEditables.map(p => ({
        parametro: p.parametro,
        valor: p.valor
      }));

      const prueba = await laboratorioService.crearPrueba({
        paciente_id: pacienteId,
        consulta_id: consultaId,
        area: extraccion.area_sugerida,
        tipo_prueba: extraccion.tipo_prueba_sugerido,
        resultados: resultados
      });

      if (onSuccess) {
        onSuccess(prueba);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al crear la prueba de laboratorio');
    } finally {
      setLoading(false);
      setMostrarDialogoConfirmacion(false);
    }
  };

  const obtenerIconoArchivo = () => {
    if (!archivo) return <UploadIcon sx={{ fontSize: 48, color: 'primary.main' }} />;
    
    const extension = archivo.name.split('.').pop()?.toLowerCase();
    if (extension === 'pdf') {
      return <PdfIcon sx={{ fontSize: 48, color: 'error.main' }} />;
    }
    return <ImageIcon sx={{ fontSize: 48, color: 'info.main' }} />;
  };

  const formatearTamanio = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <Box>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <UploadIcon />
          Subir Resultado de Laboratorio
        </Typography>
        
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Sube un archivo PDF o imagen de resultados de laboratorio. El sistema extraerá automáticamente los valores.
        </Typography>

        <Divider sx={{ mb: 3 }} />

        {/* Área de carga */}
        <Box
          sx={{
            border: '2px dashed',
            borderColor: archivo ? 'success.main' : 'grey.300',
            borderRadius: 2,
            p: 4,
            textAlign: 'center',
            bgcolor: archivo ? 'success.50' : 'grey.50',
            cursor: 'pointer',
            transition: 'all 0.3s',
            '&:hover': {
              borderColor: 'primary.main',
              bgcolor: 'primary.50'
            }
          }}
          onClick={() => document.getElementById('file-input')?.click()}
        >
          <input
            id="file-input"
            type="file"
            accept={extensionesPermitidas.join(',')}
            onChange={handleArchivoSeleccionado}
            style={{ display: 'none' }}
          />

          {obtenerIconoArchivo()}

          {archivo ? (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body1" fontWeight="bold">
                {archivo.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {formatearTamanio(archivo.size)}
              </Typography>
              <Chip
                label="Archivo cargado"
                color="success"
                size="small"
                icon={<CheckIcon />}
                sx={{ mt: 1 }}
              />
            </Box>
          ) : (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body1" gutterBottom>
                Click para seleccionar archivo
              </Typography>
              <Typography variant="body2" color="text.secondary">
                PDF, JPG, PNG, BMP, TIFF (máx. 10MB)
              </Typography>
            </Box>
          )}
        </Box>

        {/* Información de formatos */}
        <Alert severity="info" sx={{ mt: 2 }}>
          <Typography variant="body2" fontWeight="bold" gutterBottom>
            Formatos soportados:
          </Typography>
          <Typography variant="body2" component="div">
            • <strong>PDF:</strong> Resultados de laboratorio en formato PDF<br />
            • <strong>Imágenes:</strong> Fotos o escaneos de resultados (JPG, PNG, etc.)
          </Typography>
        </Alert>

        {/* Error */}
        {error && (
          <Alert severity="error" sx={{ mt: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Loading */}
        {loading && (
          <Box sx={{ mt: 2 }}>
            <LinearProgress />
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1, textAlign: 'center' }}>
              Extrayendo datos del archivo...
            </Typography>
          </Box>
        )}

        {/* Botones */}
        <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
          {onCancel && (
            <Button onClick={onCancel} disabled={loading}>
              Cancelar
            </Button>
          )}
          <Button
            variant="contained"
            startIcon={loading ? <CircularProgress size={20} /> : <ScienceIcon />}
            onClick={handleExtraerDatos}
            disabled={!archivo || loading}
          >
            Extraer y Crear Prueba
          </Button>
        </Box>
      </Paper>

      {/* Diálogo de confirmación */}
      <Dialog
        open={mostrarDialogoConfirmacion}
        onClose={() => setMostrarDialogoConfirmacion(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Typography variant="h6">Datos Extraídos</Typography>
            <IconButton onClick={() => setMostrarDialogoConfirmacion(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        
        <DialogContent dividers>
          {extraccion && (
            <Box>
              <Alert severity="success" sx={{ mb: 2 }}>
                Se encontraron <strong>{parametrosEditables.filter(p => !p.esNuevo).length}</strong> parámetros automáticamente
              </Alert>

              <Typography variant="subtitle2" gutterBottom>
                Área detectada: <Chip label={extraccion.area_sugerida} size="small" color="primary" />
              </Typography>
              <Typography variant="subtitle2" gutterBottom sx={{ mb: 2 }}>
                Tipo de prueba: <Chip label={extraccion.tipo_prueba_sugerido} size="small" color="secondary" />
              </Typography>

              <Divider sx={{ my: 2 }} />

              {/* Tabla de parámetros editables */}
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Parámetros ({parametrosEditables.length}):
              </Typography>
              
              <TableContainer component={Paper} variant="outlined" sx={{ mb: 3, maxHeight: 400 }}>
                <Table size="small" stickyHeader>
                  <TableHead>
                    <TableRow>
                      <TableCell>Parámetro</TableCell>
                      <TableCell align="right">Valor</TableCell>
                      <TableCell align="center">Unidad</TableCell>
                      <TableCell align="center">Rango de Referencia</TableCell>
                      <TableCell align="center" width={80}>Acciones</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {parametrosEditables.map((param, index) => (
                      <TableRow 
                        key={index}
                        sx={{ bgcolor: param.esNuevo ? 'success.lighter' : 'inherit' }}
                      >
                        <TableCell>
                          {param.esNuevo && (
                            <Chip label="NUEVO" size="small" color="success" sx={{ mr: 1 }} />
                          )}
                          {param.parametro.replace(/_/g, ' ').toUpperCase()}
                        </TableCell>
                        <TableCell align="right">
                          <TextField
                            type="number"
                            value={param.valor}
                            onChange={(e) => handleActualizarValor(index, e.target.value)}
                            size="small"
                            inputProps={{ step: 0.01 }}
                            sx={{ width: 100 }}
                          />
                        </TableCell>
                        <TableCell align="center">
                          <Typography variant="body2" color="text.secondary">
                            {param.unidad || '-'}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          {param.rango_min !== undefined && param.rango_max !== undefined ? (
                            <Typography variant="body2" color="text.secondary">
                              {param.rango_min} - {param.rango_max}
                            </Typography>
                          ) : (
                            <Typography variant="body2" color="text.secondary">
                              -
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell align="center">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleEliminarParametro(index)}
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              <Divider sx={{ my: 2 }} />

              {/* Agregar nuevo parámetro */}
              <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                Agregar Parámetro Faltante:
              </Typography>
              <Box display="flex" gap={1} alignItems="flex-start" flexWrap="wrap">
                <TextField
                  label="Nombre del Parámetro"
                  value={nuevoParametro}
                  onChange={(e) => setNuevoParametro(e.target.value)}
                  placeholder="ej: glucosa, sodio"
                  size="small"
                  sx={{ flex: '1 1 200px', minWidth: 200 }}
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
                  sx={{ width: 120 }}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAgregarParametro();
                    }
                  }}
                />
                <TextField
                  select
                  label="Unidad"
                  value={nuevaUnidad}
                  onChange={(e) => setNuevaUnidad(e.target.value)}
                  size="small"
                  sx={{ width: 120 }}
                >
                  {UNIDADES_COMUNES.map((unidad) => (
                    <MenuItem key={unidad} value={unidad}>
                      {unidad}
                    </MenuItem>
                  ))}
                </TextField>
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
                El sistema analizará todos los valores con los rangos de referencia.
              </Alert>
            </Box>
          )}
        </DialogContent>

        <DialogActions>
          <Button onClick={() => setMostrarDialogoConfirmacion(false)}>
            Cancelar
          </Button>
          <Button
            variant="contained"
            onClick={handleCrearPrueba}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <CheckIcon />}
          >
            Confirmar y Crear Prueba
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SubirArchivoLaboratorio;
