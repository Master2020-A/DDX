import React, { useState } from 'react';
import { Upload, CheckCircle2, Activity } from 'lucide-react';
import { 
  Button, 
  Box, 
  Typography,
  CircularProgress,
  Alert
} from '@mui/material';
import api from '@/lib/api';

interface ParametrosExtraidos {
  tipo: string;
  region_anatomica: string;
  modo: string;
  via_acceso: string;
  transductor: string;
  equipo: string;
  es_obstetrica: boolean;
  edad_gestacional?: number;
  numero_fetos?: number;
  hallazgos_2d: string;
  hallazgos_3d: string;
  hallazgos_4d: string;
  realizar_doppler: boolean;
  flujo_vascular: string;
  resistencia_vascular: string;
  liquido_libre: boolean;
  cantidad_liquido: string;
  calidad: string;
  limitaciones: string;
  birads: string;
  interpretacion?: string;
  hallazgos?: string[];
}

interface SubirImagenEcografiaProps {
  onParametrosExtraidos: (parametros: ParametrosExtraidos) => void;
  onClose?: () => void;
}

const SubirImagenEcografia: React.FC<SubirImagenEcografiaProps> = ({
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
        '/estudios-especiales/ecografia/extraer-parametros',
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
            borderColor: 'primary.main',
            bgcolor: 'action.hover'
          }
        }}
      >
        <input
          type="file"
          id="file-upload-eco"
          accept="image/jpeg,image/png,image/jpg,application/pdf"
          onChange={handleArchivoSeleccionado}
          style={{ display: 'none' }}
        />
        <label htmlFor="file-upload-eco" style={{ cursor: 'pointer' }}>
          <Upload size={48} style={{ margin: '0 auto', display: 'block', color: '#1976d2' }} />
          <Typography variant="h6" sx={{ mt: 2 }}>
            Arrastra una imagen de Ecografía aquí
          </Typography>
          <Typography variant="body2" color="text.secondary">
            o haz clic para seleccionar
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            Formatos: JPG, PNG, PDF (máx. 10MB)
          </Typography>
        </label>
      </Box>

      {/* Previsualización */}
      {previsualizacion && (
        <Box sx={{ textAlign: 'center' }}>
          <img
            src={previsualizacion}
            alt="Previsualización"
            style={{ maxWidth: '100%', maxHeight: '300px', borderRadius: '8px' }}
          />
        </Box>
      )}

      {/* Nombre del archivo */}
      {archivo && (
        <Typography variant="body2" color="text.secondary">
          📄 {archivo.name} ({(archivo.size / 1024).toFixed(2)} KB)
        </Typography>
      )}

      {/* Mensajes */}
      {error && (
        <Alert severity="error">{error}</Alert>
      )}

      {exito && (
        <Alert severity="success" icon={<CheckCircle2 />}>
          ¡Parámetros extraídos exitosamente!
        </Alert>
      )}

      {/* Botón de extracción */}
      {archivo && !exito && (
        <Button
          variant="contained"
          onClick={handleExtraerParametros}
          disabled={cargando}
          startIcon={cargando ? <CircularProgress size={20} /> : <Activity />}
          fullWidth
        >
          {cargando ? 'Extrayendo parámetros...' : '🧠 Extraer Parámetros'}
        </Button>
      )}

      {/* Información */}
      <Box sx={{ bgcolor: 'info.light', p: 2, borderRadius: 1 }}>
        <Typography variant="subtitle2" gutterBottom>
          <strong>¿Cómo funciona?</strong>
        </Typography>
        <Typography variant="body2">
          1. Sube una imagen de Ecografía (JPG, PNG o PDF)
          <br />
          2. El sistema analiza la imagen automáticamente
          <br />
          3. Los parámetros se extraen y rellenan en el formulario
          <br />
          4. Revisa los datos y guarda el estudio
        </Typography>
      </Box>
    </Box>
  );
};

export default SubirImagenEcografia;
