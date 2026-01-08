"""
Servicio de Procesamiento de Archivos NIfTI
Sistema DDX - Diagnóstico Diferencial Inteligente

Maneja archivos .nii y .nii.gz (Neuroimaging Informatics Technology Initiative)
"""
import logging
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import nibabel as nib
from PIL import Image
import io

logger = logging.getLogger(__name__)

class NIfTIProcessor:
    """Procesador de archivos NIfTI para imágenes médicas 3D/4D"""
    
    def __init__(self):
        """Inicializa el procesador NIfTI"""
        self.formatos_soportados = ['.nii', '.nii.gz']
    
    def es_nifti(self, ruta_archivo: str) -> bool:
        """
        Verifica si un archivo es NIfTI
        
        Args:
            ruta_archivo: Ruta al archivo
            
        Returns:
            bool: True si es NIfTI
        """
        archivo_str = str(ruta_archivo).lower()
        return any(archivo_str.endswith(ext) for ext in self.formatos_soportados)
    
    def cargar_nifti(self, ruta_archivo: str) -> Optional[nib.Nifti1Image]:
        """
        Carga un archivo NIfTI
        
        Args:
            ruta_archivo: Ruta al archivo .nii o .nii.gz
            
        Returns:
            Imagen NIfTI cargada o None si hay error
        """
        try:
            img = nib.load(ruta_archivo)
            logger.info(f"✅ Archivo NIfTI cargado: {ruta_archivo}")
            return img
        except Exception as e:
            logger.error(f"❌ Error cargando NIfTI {ruta_archivo}: {e}")
            return None
    
    def extraer_metadatos(self, ruta_archivo: str) -> Dict[str, Any]:
        """
        Extrae metadatos de un archivo NIfTI
        
        Args:
            ruta_archivo: Ruta al archivo NIfTI
            
        Returns:
            Dict con metadatos de la imagen
        """
        try:
            img = nib.load(ruta_archivo)
            data = img.get_fdata()
            header = img.header
            
            # Convertir todos los valores a tipos Python nativos (JSON-serializables)
            voxel_dims = header.get_zooms()
            orientacion = nib.aff2axcodes(img.affine)
            
            metadatos = {
                'formato': 'NIfTI',
                'dimensiones': [int(d) for d in data.shape],  # Convertir a lista de ints
                'num_dimensiones': int(len(data.shape)),
                'tipo_dato': str(data.dtype),
                'voxel_dims': [float(v) for v in voxel_dims],  # Convertir a lista de floats
                'orientacion': [str(o) for o in orientacion],  # Convertir a lista de strings
                'unidades_espaciales': str(header.get_xyzt_units()[0]),
                'unidades_temporales': str(header.get_xyzt_units()[1]),
                'min_valor': float(np.min(data)),
                'max_valor': float(np.max(data)),
                'media': float(np.mean(data)),
                'desviacion': float(np.std(data)),
            }
            
            # Información de tamaño
            if len(data.shape) >= 3:
                metadatos['es_3d'] = True
                metadatos['dimensiones_str'] = f"{data.shape[0]}x{data.shape[1]}x{data.shape[2]}"
            if len(data.shape) == 4:
                metadatos['es_4d'] = True
                metadatos['num_volumenes'] = data.shape[3]
            
            logger.info(f"Metadatos NIfTI extraídos: {metadatos['dimensiones']}")
            return metadatos
            
        except Exception as e:
            logger.error(f"Error extrayendo metadatos NIfTI: {e}")
            return {
                'formato': 'NIfTI',
                'error': str(e)
            }
    
    def generar_preview_2d(self, ruta_archivo: str, slice_idx: Optional[int] = None,
                          eje: str = 'axial', tamano: Tuple[int, int] = (512, 512)) -> Optional[bytes]:
        """
        Genera una vista previa 2D de un volumen NIfTI 3D
        
        Args:
            ruta_archivo: Ruta al archivo NIfTI
            slice_idx: Índice del corte (None = corte medio)
            eje: 'axial', 'sagital', 'coronal'
            tamano: Tamaño de la imagen de salida
            
        Returns:
            Bytes de la imagen PNG o None si hay error
        """
        try:
            img = nib.load(ruta_archivo)
            data = img.get_fdata()
            
            # Seleccionar eje y slice
            if len(data.shape) < 3:
                logger.warning("Imagen NIfTI no es 3D")
                return None
            
            # Para imágenes 4D, tomar el primer volumen
            if len(data.shape) == 4:
                data = data[:, :, :, 0]
            
            # Seleccionar corte según el eje
            if eje == 'axial':
                slice_idx = slice_idx or data.shape[2] // 2
                slice_2d = data[:, :, slice_idx]
            elif eje == 'sagital':
                slice_idx = slice_idx or data.shape[0] // 2
                slice_2d = data[slice_idx, :, :]
            elif eje == 'coronal':
                slice_idx = slice_idx or data.shape[1] // 2
                slice_2d = data[:, slice_idx, :]
            else:
                slice_2d = data[:, :, data.shape[2] // 2]
            
            # Normalizar a 0-255
            slice_2d = slice_2d.astype(float)
            slice_min = np.min(slice_2d)
            slice_max = np.max(slice_2d)
            
            if slice_max > slice_min:
                slice_norm = ((slice_2d - slice_min) / (slice_max - slice_min) * 255).astype(np.uint8)
            else:
                slice_norm = np.zeros_like(slice_2d, dtype=np.uint8)
            
            # Rotar para visualización correcta
            slice_norm = np.rot90(slice_norm)
            
            # Convertir a imagen PIL
            pil_img = Image.fromarray(slice_norm, mode='L')
            pil_img = pil_img.resize(tamano, Image.Resampling.LANCZOS)
            
            # Convertir a bytes PNG
            buffer = io.BytesIO()
            pil_img.save(buffer, format='PNG')
            buffer.seek(0)
            
            logger.info(f"✅ Preview generado: eje={eje}, slice={slice_idx}")
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"❌ Error generando preview NIfTI: {e}")
            return None
    
    def procesar_para_visualizacion(self, ruta_archivo: str, output_dir: Path) -> Dict[str, Any]:
        """
        Procesa archivo NIfTI y genera vistas previas en los 3 ejes
        
        Args:
            ruta_archivo: Ruta al archivo NIfTI
            output_dir: Directorio para guardar previews
            
        Returns:
            Dict con rutas a las imágenes generadas
        """
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            base_name = Path(ruta_archivo).stem
            if base_name.endswith('.nii'):  # Para .nii.gz
                base_name = base_name[:-4]
            
            resultados = {
                'metadatos': self.extraer_metadatos(ruta_archivo),
                'previews': {}
            }
            
            # Generar preview en cada eje
            for eje in ['axial', 'sagital', 'coronal']:
                preview_bytes = self.generar_preview_2d(ruta_archivo, eje=eje)
                if preview_bytes:
                    preview_path = output_dir / f"{base_name}_{eje}.png"
                    with open(preview_path, 'wb') as f:
                        f.write(preview_bytes)
                    resultados['previews'][eje] = str(preview_path)
                    logger.info(f"Preview {eje} guardado: {preview_path}")
            
            return resultados
            
        except Exception as e:
            logger.error(f"Error procesando NIfTI para visualización: {e}")
            return {
                'error': str(e),
                'metadatos': self.extraer_metadatos(ruta_archivo)
            }


# Instancia global
_nifti_processor = None

def get_nifti_processor() -> NIfTIProcessor:
    """Obtiene instancia única del procesador NIfTI"""
    global _nifti_processor
    if _nifti_processor is None:
        _nifti_processor = NIfTIProcessor()
    return _nifti_processor
