/**
 * Componente para subir archivos de estudios especiales (EKG, EEG, Ecografías)
 * y extraer datos automáticamente con OCR
 */
import React, { useState } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  LinearProgress,
  Alert,
  Chip,
  Stack,
  IconButton,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Tooltip
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  InsertDriveFile as FileIcon,
  Close as CloseIcon,
  CheckCircle as CheckIcon
} from '@mui/icons-material';
import estudiosEspecialesService from '../../services/estudiosEspecialesService';

interface Props {
  onDatosExtraidos: (tipo: string, datos: any, anomalias?: string[]) => void;
  tipoEsperado?: 'ekg' | 'eeg' | 'ecografia';
}

const SubirArchivoEstudio: React.FC<Props> = ({ onDatosExtraidos, tipoEsperado }) => {
  const [archivo, setArchivo] = useState<File | null>(null);
  const [extrayendo, setExtrayendo] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exito, setExito] = useState(false);
  const [anomaliasDetectadas, setAnomaliasDetectadas] = useState<string[]>([]);
  const [metodoAnalisis, setMetodoAnalisis] = useState<'auto' | 'ocr' | 'ia'>('ia');
  const [csvConSenales, setCsvConSenales] = useState(false);
  const [convirtiendo, setConvirtiendo] = useState(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validar tamaño (máx 50MB)
      if (file.size > 50 * 1024 * 1024) {
        setError('El archivo es demasiado grande. Máximo 50MB.');
        return;
      }

      // Validar formato
      const extension = file.name.split('.').pop()?.toLowerCase();
      const formatosPermitidos = ['pdf', 'jpg', 'jpeg', 'png', 'tiff', 'bmp', 'ecg', 'mat', 'dat', 'csv'];
      
      if (!extension || !formatosPermitidos.includes(extension)) {
        setError(`Formato no soportado. Use: ${formatosPermitidos.join(', ')}`);
        return;
      }

      setArchivo(file);
      setError(null);
      setExito(false);
    }
  };

  const handleExtraer = async () => {
    if (!archivo) return;

    setExtrayendo(true);
    setError(null);

    try {
      const resultado = await estudiosEspecialesService.extraerDesdeArchivo(archivo, metodoAnalisis);

      // Verificar si el tipo coincide con el esperado
      if (tipoEsperado && resultado.tipo_estudio !== tipoEsperado && resultado.tipo_estudio !== 'desconocido') {
        setError(`El archivo parece ser un ${resultado.tipo_estudio.toUpperCase()}, pero se esperaba un ${tipoEsperado.toUpperCase()}`);
        setExtrayendo(false);
        return;
      }

      // Guardar anomalías detectadas
      const anomalias = resultado.anomalias || [];
      setAnomaliasDetectadas(anomalias);
      
      // Mostrar datos extraídos en consola para debug
      console.log('📊 Datos extraídos:', resultado.datos);
      console.log('⚠️ Anomalías detectadas:', anomalias);
      console.log('🎯 Método usado:', resultado.metodo);
      
      // Verificar si es CSV con señales
      if (resultado.conversion_csv_disponible) {
        setCsvConSenales(true);
        console.log('💡 CSV con señales detectado - conversión a imagen disponible');
      }
      
      // Notificar datos extraídos
      onDatosExtraidos(resultado.tipo_estudio, resultado.datos, anomalias);
      setExito(true);

    } catch (err: any) {
      console.error('Error extrayendo datos:', err);
      setError(err.response?.data?.detail || 'Error al extraer datos del archivo');
    } finally {
      setExtrayendo(false);
    }
  };

  const handleRemoverArchivo = () => {
    setArchivo(null);
    setError(null);
    setExito(false);
    setCsvConSenales(false);
  };

  const handleConvertirCsvAImagen = async () => {
    if (!archivo) return;

    setConvirtiendo(true);
    setError(null);

    try {
      const resultado = await estudiosEspecialesService.convertirCsvAImagen(archivo, 12, true);

      console.log('🎨 CSV convertido a imagen:', resultado);
      console.log('📊 Datos extraídos de la imagen:', resultado.datos);
      console.log('⚠️ Anomalías:', resultado.anomalias);

      // Notificar datos extraídos del análisis con IA
      onDatosExtraidos(resultado.tipo_estudio, resultado.datos, resultado.anomalias || []);
      setAnomaliasDetectadas(resultado.anomalias || []);
      setExito(true);
      setCsvConSenales(false);

    } catch (err: any) {
      console.error('Error convirtiendo CSV:', err);
      setError(err.response?.data?.detail || 'Error al convertir CSV a imagen');
    } finally {
      setConvirtiendo(false);
    }
  };

  const getTipoLabel = () => {
    if (tipoEsperado === 'ekg') return 'EKG';
    if (tipoEsperado === 'eeg') return 'EEG';
    if (tipoEsperado === 'ecografia') return 'Ecografía';
    return 'Estudio';
  };

  return (
    <Box>
      {/* Selector de método de análisis */}
      <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
        <FormControl component="fieldset">
          <FormLabel component="legend">Método de Análisis</FormLabel>
          <RadioGroup
            row
            value={metodoAnalisis}
            onChange={(e) => setMetodoAnalisis(e.target.value as 'auto' | 'ocr' | 'ia')}
          >
            <Tooltip title="Usa IA (GPT-4 Vision) para analizar la imagen del ECG">
              <FormControlLabel 
                value="ia" 
                control={<Radio />} 
                label="🤖 IA (Recomendado)" 
              />
            </Tooltip>
            <Tooltip title="Solo OCR, sin IA (más rápido pero menos preciso)">
              <FormControlLabel 
                value="ocr" 
                control={<Radio />} 
                label="📝 Solo OCR" 
              />
            </Tooltip>
            <Tooltip title="OCR primero, IA si falla">
              <FormControlLabel 
                value="auto" 
                control={<Radio />} 
                label="⚡ Automático" 
              />
            </Tooltip>
          </RadioGroup>
        </FormControl>
        
        {metodoAnalisis === 'ia' && (
          <Alert severity="info" sx={{ mt: 1 }}>
            <Typography variant="caption">
              <strong>IA:</strong> Analiza la imagen completa del ECG, detecta ondas y mide intervalos automáticamente. 
              Costo: ~$0.01-0.03 por imagen.
            </Typography>
          </Alert>
        )}
        {metodoAnalisis === 'ocr' && (
          <Alert severity="warning" sx={{ mt: 1 }}>
            <Typography variant="caption">
              <strong>OCR:</strong> Solo extrae texto visible. No puede interpretar gráficas de ondas.
            </Typography>
          </Alert>
        )}
      </Paper>

      {/* Área de carga */}
      {!archivo && (
        <Paper
          variant="outlined"
          sx={{
            p: 4,
            textAlign: 'center',
            borderStyle: 'dashed',
            borderWidth: 2,
            borderColor: 'primary.main',
            bgcolor: 'grey.50',
            cursor: 'pointer',
            '&:hover': {
              bgcolor: 'grey.100'
            }
          }}
          onClick={() => document.getElementById('file-input')?.click()}
        >
          <input
            id="file-input"
            type="file"
            accept=".pdf,.jpg,.jpeg,.png,.tiff,.bmp,.ecg,.mat,.dat,.csv"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
          
          <UploadIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
          
          <Typography variant="h6" gutterBottom>
            Subir archivo de {getTipoLabel()}
          </Typography>
          
          <Typography variant="body2" color="textSecondary" gutterBottom>
            Arrastra un archivo aquí o haz clic para seleccionar
          </Typography>
          
          <Typography variant="caption" color="textSecondary">
            Formatos: PDF, JPG, PNG, TIFF, BMP, ECG, MAT, DAT, CSV (máx 50MB)
          </Typography>
        </Paper>
      )}

      {/* Archivo seleccionado */}
      {archivo && !exito && (
        <Paper variant="outlined" sx={{ p: 2 }}>
          <Stack direction="row" spacing={2} alignItems="center">
            <FileIcon color="primary" sx={{ fontSize: 40 }} />
            
            <Box flex={1}>
              <Typography variant="body1" fontWeight="medium">
                {archivo.name}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                {(archivo.size / 1024).toFixed(2)} KB
              </Typography>
            </Box>

            {!extrayendo && (
              <IconButton size="small" onClick={handleRemoverArchivo}>
                <CloseIcon />
              </IconButton>
            )}
          </Stack>

          {extrayendo && (
            <Box mt={2}>
              <LinearProgress />
              <Typography variant="caption" color="textSecondary" mt={1}>
                Extrayendo datos con OCR...
              </Typography>
            </Box>
          )}

          {!extrayendo && (
            <Button
              variant="contained"
              fullWidth
              startIcon={<UploadIcon />}
              onClick={handleExtraer}
              sx={{ mt: 2 }}
            >
              📄 Extraer Datos del Archivo
            </Button>
          )}
        </Paper>
      )}

      {/* Opción de convertir CSV a imagen */}
      {csvConSenales && !exito && (
        <Paper variant="outlined" sx={{ p: 2, mt: 2, bgcolor: 'info.light', borderColor: 'info.main' }}>
          <Typography variant="subtitle2" gutterBottom color="info.dark">
            💡 CSV con Señales Detectado
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Este archivo contiene señales temporales de ECG. Puedes convertirlo a una imagen gráfica 
            y analizarlo con IA para obtener parámetros completos (FC, PR, QRS, QT, etc.).
          </Typography>
          
          {convirtiendo && (
            <Box mt={2}>
              <LinearProgress />
              <Typography variant="caption" color="textSecondary" mt={1}>
                Convirtiendo CSV a imagen y analizando con IA...
              </Typography>
            </Box>
          )}
          
          {!convirtiendo && (
            <Button
              variant="contained"
              color="info"
              fullWidth
              startIcon={<UploadIcon />}
              onClick={handleConvertirCsvAImagen}
              sx={{ mt: 2 }}
            >
              🎨 Convertir a Imagen y Analizar con IA
            </Button>
          )}
        </Paper>
      )}

      {/* Éxito */}
      {exito && (
        <Box>
          <Alert severity="success" icon={<CheckIcon />} sx={{ mt: 2 }}>
            <Typography variant="body2" fontWeight="medium">
              ✅ Datos extraídos exitosamente
            </Typography>
            <Typography variant="caption">
              Los campos del formulario se han rellenado automáticamente. Revisa y completa los datos faltantes.
            </Typography>
          </Alert>
          
          {/* Mostrar anomalías detectadas */}
          {anomaliasDetectadas.length > 0 && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              <Typography variant="body2" fontWeight="medium" gutterBottom>
                ⚠️ Anomalías detectadas:
              </Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" gap={1}>
                {anomaliasDetectadas.map((anomalia, index) => (
                  <Chip
                    key={index}
                    label={anomalia.replace(/_/g, ' ').toUpperCase()}
                    size="small"
                    color="warning"
                  />
                ))}
              </Stack>
            </Alert>
          )}
        </Box>
      )}

      {/* Error */}
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {/* Información */}
      <Box mt={2}>
        <Typography variant="caption" color="textSecondary">
          💡 <strong>Tip:</strong> El sistema extraerá automáticamente los datos del archivo usando OCR.
          Puedes revisar y modificar los datos antes de guardar el estudio.
        </Typography>
      </Box>
    </Box>
  );
};

export default SubirArchivoEstudio;
