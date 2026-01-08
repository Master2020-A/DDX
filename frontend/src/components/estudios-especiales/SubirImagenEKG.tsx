import React, { useState } from 'react';
import { Upload, Loader2, CheckCircle2, XCircle, Activity } from 'lucide-react';
import { 
  Button, 
  Card, 
  CardContent, 
  Alert, 
  Box, 
  Typography,
  CircularProgress 
} from '@mui/material';
import api from '@/lib/api';

interface ParametrosExtraidos {
  frecuencia_cardiaca: number;
  ritmo: string;
  intervalo_pr: number;
  duracion_qrs: number;
  intervalo_qt: number;
  qtc: number;
  eje_qrs: number;
  onda_p: string;
  complejo_qrs: string;
  onda_t: string;
  segmento_st: string;
  hallazgos: string[];
  interpretacion_ia?: {
    P: string;
    PR: string;
    QRS: string;
    ST_T: string;
    QT: string;
  };
}

interface SubirImagenEKGProps {
  onParametrosExtraidos: (parametros: ParametrosExtraidos) => void;
  onClose?: () => void;
}

const SubirImagenEKG: React.FC<SubirImagenEKGProps> = ({
  onParametrosExtraidos,
  onClose
}) => {
  const [archivo, setArchivo] = useState<File | null>(null);
  const [previsualizacion, setPrevisualizacion] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exito, setExito] = useState(false);

  const handleArchivoSeleccionado = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validar tipo de archivo
    const tiposPermitidos = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf'];
    if (!tiposPermitidos.includes(file.type)) {
      setError('Formato no soportado. Use JPG, PNG o PDF');
      return;
    }

    // Validar tamaño (máx 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('El archivo es demasiado grande. Máximo 10MB');
      return;
    }

    setArchivo(file);
    setError(null);
    setExito(false);

    // Crear previsualización
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setPrevisualizacion(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    } else {
      setPrevisualizacion(null);
    }
  };

  const handleExtraerParametros = async () => {
    if (!archivo) return;

    setCargando(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('archivo', archivo);

      const response = await api.post(
        '/estudios-especiales/ekg/extraer-parametros',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      if (response.data.success) {
        setExito(true);
        onParametrosExtraidos(response.data.parametros);
        
        // Cerrar después de 1 segundo
        setTimeout(() => {
          if (onClose) onClose();
        }, 1000);
      } else {
        setError('No se pudieron extraer los parámetros');
      }
    } catch (err: any) {
      console.error('Error al extraer parámetros:', err);
      setError(err.response?.data?.detail || 'Error al procesar la imagen');
    } finally {
      setCargando(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();

    const file = e.dataTransfer.files[0];
    if (file) {
      const event = {
        target: { files: [file] }
      } as any;
      handleArchivoSeleccionado(event);
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {/* Área de carga */}
      <Box
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        sx={{
          border: '2px dashed',
          borderColor: 'grey.300',
          borderRadius: 2,
          p: 4,
          textAlign: 'center',
          cursor: 'pointer',
          '&:hover': {
            borderColor: 'primary.main'
          }
        }}
      >
        <input
          type="file"
          id="file-upload-ekg"
          style={{ display: 'none' }}
          accept="image/jpeg,image/png,image/jpg,application/pdf"
          onChange={handleArchivoSeleccionado}
        />
        <label htmlFor="file-upload-ekg" style={{ cursor: 'pointer' }}>
          <Box display="flex" flexDirection="column" alignItems="center" gap={1}>
            {archivo ? (
              <>
                <CheckCircle2 size={48} color="green" />
                <Typography variant="body2" fontWeight="medium">{archivo.name}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {(archivo.size / 1024 / 1024).toFixed(2)} MB
                </Typography>
              </>
            ) : (
              <>
                <Upload size={48} color="gray" />
                <Typography variant="body2" fontWeight="medium">
                  Arrastra una imagen de EKG o haz clic para seleccionar
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  JPG, PNG o PDF (máx. 10MB)
                </Typography>
              </>
            )}
          </Box>
        </label>
      </Box>

      {/* Previsualización */}
      {previsualizacion && (
        <Card>
          <CardContent sx={{ pt: 2 }}>
            <img
              src={previsualizacion}
              alt="Previsualización"
              style={{ width: '100%', height: 'auto', maxHeight: '256px', objectFit: 'contain', borderRadius: '4px' }}
            />
          </CardContent>
        </Card>
      )}

      {/* Mensajes */}
      {error && (
        <Alert severity="error" icon={<XCircle size={20} />}>
          {error}
        </Alert>
      )}

      {exito && (
        <Alert severity="success" icon={<CheckCircle2 size={20} />}>
          ¡Parámetros extraídos exitosamente! El formulario se ha llenado automáticamente.
        </Alert>
      )}

      {/* Botones de acción */}
      <Box display="flex" gap={2}>
        <Button
          onClick={handleExtraerParametros}
          disabled={!archivo || cargando}
          variant="contained"
          fullWidth
          startIcon={cargando ? <CircularProgress size={20} /> : <Activity size={20} />}
        >
          {cargando ? 'Analizando imagen...' : 'Extraer Parámetros'}
        </Button>
        {onClose && (
          <Button variant="outlined" onClick={onClose} disabled={cargando}>
            Cancelar
          </Button>
        )}
      </Box>

      {/* Información */}
      <Box sx={{ fontSize: '0.75rem', color: 'text.secondary' }}>
        <Typography variant="caption" fontWeight="bold" display="block" gutterBottom>
          ¿Cómo funciona?
        </Typography>
        <Box component="ul" sx={{ pl: 2, m: 0 }}>
          <li>Sube una imagen clara del EKG (foto o escaneo)</li>
          <li>El sistema digitaliza la señal automáticamente</li>
          <li>Detecta ondas P, Q, R, S, T y calcula intervalos</li>
          <li>Genera interpretación médica narrativa</li>
          <li>Pre-llena el formulario con los valores detectados</li>
        </Box>
      </Box>
    </Box>
  );
};

export default SubirImagenEKG;
