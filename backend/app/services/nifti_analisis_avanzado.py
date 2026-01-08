"""
Servicio para análisis avanzado de archivos NIfTI
Incluye: análisis multiplanar, métricas cuantitativas, detección de anomalías
"""
import nibabel as nib
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple
import logging
from scipy import ndimage
from skimage import filters, measure

logger = logging.getLogger(__name__)


class NIfTIAnalisisAvanzado:
    """Análisis avanzado de imágenes NIfTI (MRI/CT)"""
    
    def __init__(self):
        self.logger = logger
    
    def analizar_completo(self, ruta_archivo: str) -> Dict[str, Any]:
        """
        Análisis completo de un archivo NIfTI
        
        Returns:
            Dict con todos los resultados de análisis
        """
        try:
            # Cargar imagen
            img = nib.load(ruta_archivo)
            data = img.get_fdata()
            header = img.header
            
            resultados = {
                'metricas_globales': self._extraer_metricas_globales(data, header),
                'analisis_multiplanar': self._analizar_multiplanar(data),
                'estadisticas_intensidad': self._estadisticas_intensidad(data),
                'deteccion_regiones': self._detectar_regiones_interes(data),
                'calidad_imagen': self._evaluar_calidad(data),
            }
            
            return resultados
            
        except Exception as e:
            logger.error(f"Error en análisis avanzado: {e}")
            return {'error': str(e)}
    
    def _extraer_metricas_globales(self, data: np.ndarray, header) -> Dict[str, Any]:
        """Extrae métricas globales del volumen"""
        voxel_dims = header.get_zooms()
        voxel_volume = np.prod(voxel_dims[:3])  # mm³ por voxel
        
        # Calcular volúmenes
        total_voxels = data.size
        non_zero_voxels = np.count_nonzero(data)
        
        return {
            'dimensiones': [int(d) for d in data.shape],
            'voxel_size': [float(v) for v in voxel_dims[:3]],
            'voxel_volume_mm3': float(voxel_volume),
            'volumen_total_cm3': float(total_voxels * voxel_volume / 1000),
            'volumen_tejido_cm3': float(non_zero_voxels * voxel_volume / 1000),
            'porcentaje_tejido': float(non_zero_voxels / total_voxels * 100),
        }
    
    def _analizar_multiplanar(self, data: np.ndarray) -> Dict[str, Any]:
        """Analiza los 3 planos principales"""
        resultados = {}
        
        for plano, idx_eje, nombre in [
            ('axial', 2, 'horizontal'),
            ('sagital', 0, 'lateral'),
            ('coronal', 1, 'frontal')
        ]:
            # Obtener corte central
            slice_idx = data.shape[idx_eje] // 2
            
            if idx_eje == 0:
                slice_2d = data[slice_idx, :, :]
            elif idx_eje == 1:
                slice_2d = data[:, slice_idx, :]
            else:
                slice_2d = data[:, :, slice_idx]
            
            # Analizar corte
            analisis = self._analizar_corte(slice_2d)
            analisis['nombre_plano'] = nombre
            analisis['slice_numero'] = int(slice_idx)
            analisis['total_slices'] = int(data.shape[idx_eje])
            
            resultados[plano] = analisis
        
        return resultados
    
    def _analizar_corte(self, slice_2d: np.ndarray) -> Dict[str, Any]:
        """Analiza un corte 2D individual"""
        # Filtrar valores no-cero
        valores_tejido = slice_2d[slice_2d > 0]
        
        if len(valores_tejido) == 0:
            return {
                'vacio': True,
                'mensaje': 'Corte sin tejido visible'
            }
        
        return {
            'vacio': False,
            'intensidad_media': float(np.mean(valores_tejido)),
            'intensidad_std': float(np.std(valores_tejido)),
            'intensidad_min': float(np.min(valores_tejido)),
            'intensidad_max': float(np.max(valores_tejido)),
            'area_tejido_pixels': int(len(valores_tejido)),
            'porcentaje_ocupacion': float(len(valores_tejido) / slice_2d.size * 100),
        }
    
    def _estadisticas_intensidad(self, data: np.ndarray) -> Dict[str, Any]:
        """Estadísticas detalladas de intensidades"""
        valores_tejido = data[data > 0]
        
        if len(valores_tejido) == 0:
            return {'error': 'No hay tejido visible'}
        
        # Calcular percentiles
        percentiles = [5, 25, 50, 75, 95]
        valores_percentiles = np.percentile(valores_tejido, percentiles)
        
        # Histograma simplificado
        hist, bin_edges = np.histogram(valores_tejido, bins=20)
        
        return {
            'media': float(np.mean(valores_tejido)),
            'mediana': float(np.median(valores_tejido)),
            'desviacion_std': float(np.std(valores_tejido)),
            'rango': [float(np.min(valores_tejido)), float(np.max(valores_tejido))],
            'percentiles': {
                f'p{p}': float(v) for p, v in zip(percentiles, valores_percentiles)
            },
            'coeficiente_variacion': float(np.std(valores_tejido) / np.mean(valores_tejido) * 100),
        }
    
    def _detectar_regiones_interes(self, data: np.ndarray) -> Dict[str, Any]:
        """Detecta y caracteriza regiones de interés"""
        try:
            # Umbralizar para encontrar regiones
            umbral = filters.threshold_otsu(data[data > 0]) if np.any(data > 0) else 0
            
            if umbral == 0:
                return {'error': 'No se pudo calcular umbral'}
            
            # Binarizar
            mascara = data > umbral
            
            # Etiquetar regiones conectadas
            regiones_etiquetadas, num_regiones = ndimage.label(mascara)
            
            # Analizar cada región
            regiones = []
            for region_id in range(1, min(num_regiones + 1, 11)):  # Máximo 10 regiones
                region_mask = regiones_etiquetadas == region_id
                voxels = np.sum(region_mask)
                
                if voxels > 100:  # Filtrar regiones muy pequeñas
                    intensidad_media = float(np.mean(data[region_mask]))
                    regiones.append({
                        'region_id': int(region_id),
                        'voxels': int(voxels),
                        'intensidad_media': intensidad_media,
                    })
            
            return {
                'umbral_utilizado': float(umbral),
                'total_regiones': int(num_regiones),
                'regiones_principales': sorted(regiones, key=lambda x: x['voxels'], reverse=True)[:5],
            }
            
        except Exception as e:
            logger.error(f"Error en detección de regiones: {e}")
            return {'error': str(e)}
    
    def _evaluar_calidad(self, data: np.ndarray) -> Dict[str, Any]:
        """Evalúa la calidad de la imagen"""
        try:
            valores_tejido = data[data > 0]
            
            if len(valores_tejido) == 0:
                return {'error': 'No hay datos para evaluar'}
            
            # Signal-to-Noise Ratio (SNR) aproximado
            media = np.mean(valores_tejido)
            std = np.std(valores_tejido)
            snr = media / std if std > 0 else 0
            
            # Contrast-to-Noise Ratio (CNR) aproximado
            # Usar percentiles como proxy para diferentes tejidos
            bajo = np.percentile(valores_tejido, 25)
            alto = np.percentile(valores_tejido, 75)
            cnr = (alto - bajo) / std if std > 0 else 0
            
            # Evaluar homogeneidad
            coef_variacion = (std / media * 100) if media > 0 else 0
            
            # Clasificar calidad
            if snr > 20 and cnr > 5:
                calidad = 'excelente'
            elif snr > 10 and cnr > 3:
                calidad = 'buena'
            elif snr > 5 and cnr > 2:
                calidad = 'aceptable'
            else:
                calidad = 'baja'
            
            return {
                'snr': float(snr),
                'cnr': float(cnr),
                'coeficiente_variacion': float(coef_variacion),
                'calidad_estimada': calidad,
                'recomendaciones': self._generar_recomendaciones(snr, cnr, coef_variacion)
            }
            
        except Exception as e:
            logger.error(f"Error evaluando calidad: {e}")
            return {'error': str(e)}
    
    def _generar_recomendaciones(self, snr: float, cnr: float, cv: float) -> List[str]:
        """Genera recomendaciones basadas en métricas de calidad"""
        recomendaciones = []
        
        if snr < 10:
            recomendaciones.append("SNR bajo: Considerar mayor tiempo de adquisición")
        
        if cnr < 3:
            recomendaciones.append("Contraste bajo: Verificar parámetros de secuencia")
        
        if cv > 50:
            recomendaciones.append("Alta variabilidad: Posible presencia de artefactos")
        
        if not recomendaciones:
            recomendaciones.append("Calidad de imagen adecuada para diagnóstico")
        
        return recomendaciones
    
    def generar_reporte_detallado(self, analisis: Dict[str, Any], nombre_archivo: str) -> str:
        """Genera un reporte legible en texto"""
        lineas = []
        lineas.append("=" * 80)
        lineas.append(f"📊 ANÁLISIS AVANZADO: {nombre_archivo}")
        lineas.append("=" * 80)
        lineas.append("")
        
        # Métricas globales
        if 'metricas_globales' in analisis:
            m = analisis['metricas_globales']
            lineas.append("🔍 MÉTRICAS GLOBALES")
            lineas.append(f"   Dimensiones: {m['dimensiones']}")
            lineas.append(f"   Tamaño voxel: {m['voxel_size']} mm")
            lineas.append(f"   Volumen total: {m['volumen_total_cm3']:.1f} cm³")
            lineas.append(f"   Volumen tejido: {m['volumen_tejido_cm3']:.1f} cm³")
            lineas.append("")
        
        # Análisis multiplanar
        if 'analisis_multiplanar' in analisis:
            lineas.append("🎯 ANÁLISIS MULTIPLANAR")
            for plano, datos in analisis['analisis_multiplanar'].items():
                if not datos.get('vacio'):
                    lineas.append(f"   {plano.upper()} ({datos['nombre_plano']}):")
                    lineas.append(f"      Intensidad: {datos['intensidad_media']:.1f} ± {datos['intensidad_std']:.1f}")
                    lineas.append(f"      Ocupación: {datos['porcentaje_ocupacion']:.1f}%")
            lineas.append("")
        
        # Calidad
        if 'calidad_imagen' in analisis and 'error' not in analisis['calidad_imagen']:
            c = analisis['calidad_imagen']
            lineas.append("✨ CALIDAD DE IMAGEN")
            lineas.append(f"   Calidad: {c['calidad_estimada'].upper()}")
            lineas.append(f"   SNR: {c['snr']:.2f}")
            lineas.append(f"   CNR: {c['cnr']:.2f}")
            for rec in c['recomendaciones']:
                lineas.append(f"   • {rec}")
            lineas.append("")
        
        lineas.append("=" * 80)
        
        return "\n".join(lineas)


# Instancia global
_analisis_avanzado = None

def get_analisis_avanzado() -> NIfTIAnalisisAvanzado:
    """Obtiene instancia única del analizador avanzado"""
    global _analisis_avanzado
    if _analisis_avanzado is None:
        _analisis_avanzado = NIfTIAnalisisAvanzado()
    return _analisis_avanzado
