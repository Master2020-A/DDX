"""
Servicio de segmentación anatómica usando TotalSegmentator
Identifica 104 estructuras anatómicas en imágenes CT/MRI
"""
import nibabel as nib
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import json
import subprocess
import tempfile
import shutil
import sys
import os

logger = logging.getLogger(__name__)

# Las variables de entorno de nnU-Net se configuran en main.py


class SegmentadorAnatomico:
    """
    Segmentación anatómica avanzada para imágenes médicas 3D
    """
    
    # Mapeo de estructuras con colores RGB
    ESTRUCTURAS_COLORES = {
        # Órganos principales
        'spleen': (255, 0, 0),
        'kidney_right': (0, 255, 0),
        'kidney_left': (0, 255, 100),
        'gallbladder': (255, 255, 0),
        'liver': (255, 128, 0),
        'stomach': (128, 0, 255),
        'pancreas': (255, 0, 255),
        'adrenal_gland_right': (255, 100, 100),
        'adrenal_gland_left': (100, 255, 100),
        
        # Vasos
        'aorta': (255, 0, 0),
        'inferior_vena_cava': (0, 0, 255),
        'portal_vein_and_splenic_vein': (0, 100, 255),
        
        # Cerebro
        'brain': (255, 200, 200),
        
        # Pulmones
        'lung_upper_lobe_left': (0, 200, 255),
        'lung_lower_lobe_left': (0, 150, 200),
        'lung_upper_lobe_right': (100, 200, 255),
        'lung_middle_lobe_right': (150, 200, 255),
        'lung_lower_lobe_right': (200, 200, 255),
        
        # Corazón
        'heart': (255, 100, 100),
        
        # Huesos
        'vertebrae': (200, 200, 200),
        'rib_left': (180, 180, 180),
        'rib_right': (160, 160, 160),
        
        # Músculos
        'muscle': (200, 100, 100),
    }
    
    def __init__(self):
        self.logger = logger
        self.totalsegmentator_disponible = self._verificar_totalsegmentator()
    
    def _verificar_totalsegmentator(self) -> bool:
        """Verifica si TotalSegmentator está instalado"""
        try:
            # Intentar importar la API de Python
            from totalsegmentator.python_api import totalsegmentator
            
            print(f"\n{'='*80}")
            print(f"✅ DEBUG: TotalSegmentator importado correctamente (Python API)")
            print(f"{'='*80}\n")
            
            logger.info("✅ TotalSegmentator disponible (Python API)")
            return True
            
        except ImportError as e:
            print(f"\n{'='*80}")
            print(f"❌ DEBUG: No se pudo importar TotalSegmentator")
            print(f"   Error: {e}")
            print(f"{'='*80}\n")
            
            logger.warning(f"⚠️ TotalSegmentator no disponible: {e}")
            return False
        except Exception as e:
            print(f"❌ DEBUG: Excepción verificando TotalSegmentator: {e}")
            logger.warning(f"⚠️ TotalSegmentator no disponible: {e}")
            return False
    
    def segmentar_completo(
        self, 
        ruta_archivo: str, 
        output_dir: Optional[Path] = None,
        fast: bool = True
    ) -> Dict[str, Any]:
        """
        Ejecuta segmentación completa con TotalSegmentator
        
        Args:
            ruta_archivo: Ruta al archivo NIfTI
            output_dir: Directorio de salida (opcional)
            fast: Modo rápido (menos estructuras pero más rápido)
        
        Returns:
            Dict con resultados de segmentación
        """
        if not self.totalsegmentator_disponible:
            return self._segmentacion_basica(ruta_archivo, output_dir)
        
        try:
            # Crear directorio temporal si no se especifica
            if output_dir is None:
                output_dir = Path(tempfile.mkdtemp(prefix='segmentacion_'))
            else:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"🔍 Iniciando segmentación con TotalSegmentator (Python API)...")
            logger.info(f"   Archivo: {ruta_archivo}")
            logger.info(f"   Salida: {output_dir}")
            
            # Importar API de Python
            from totalsegmentator.python_api import totalsegmentator
            
            # Ejecutar segmentación usando Python API
            print(f"\n{'='*80}")
            print(f"🔬 DEBUG: ANTES de ejecutar TotalSegmentator")
            print(f"   Input: {ruta_archivo}")
            print(f"   Output: {output_dir}")
            print(f"   Output existe: {output_dir.exists()}")
            print(f"   Output es dir: {output_dir.is_dir()}")
            print(f"   Output absoluto: {output_dir.absolute()}")
            print(f"{'='*80}\n")
            
            print(f"🔬 Ejecutando TotalSegmentator (esto tomará 3-5 minutos)...")
            
            # Capturar resultado
            resultado = totalsegmentator(
                input=ruta_archivo,
                output=str(output_dir.absolute()),  # Usar ruta absoluta
                fast=fast,
                ml=True,  # Usar menos memoria
                quiet=False
            )
            
            print(f"\n{'='*80}")
            print(f"🔬 DEBUG: DESPUÉS de ejecutar TotalSegmentator")
            print(f"   Resultado retornado: {resultado}")
            print(f"   Output existe: {output_dir.exists()}")
            
            # Listar TODO lo que hay en output_dir
            if output_dir.exists():
                import os
                for root, dirs, files in os.walk(output_dir):
                    print(f"   Directorio: {root}")
                    for d in dirs:
                        print(f"      [DIR] {d}")
                    for f in files:
                        print(f"      [FILE] {f}")
            
            print(f"{'='*80}\n")
            
            logger.info("✅ Segmentación completada")
            
            # TotalSegmentator retorna un NIfTI con todas las estructuras en un solo volumen
            # Cada voxel tiene un valor que representa la estructura (labeled volume)
            return self._analizar_volumen_consolidado(resultado, ruta_archivo)
        except Exception as e:
            logger.error(f"❌ Error en segmentación: {e}")
            return {'error': str(e)}
    
    def _analizar_volumen_consolidado(self, volumen_nifti, archivo_original: str) -> Dict[str, Any]:
        """
        Analiza un volumen consolidado donde cada voxel tiene un label de estructura
        """
        try:
            print(f"\n{'='*80}")
            print(f"🔍 DEBUG: Analizando volumen consolidado")
            
            # Extraer datos del volumen
            data = volumen_nifti.get_fdata()
            
            # Cargar imagen original para obtener metadatos
            img_original = nib.load(archivo_original)
            voxel_volume = np.prod(img_original.header.get_zooms()[:3]) / 1000  # cm³
            
            # Encontrar todas las etiquetas únicas (excluyendo 0 = fondo)
            labels_unicos = np.unique(data)
            labels_unicos = labels_unicos[labels_unicos > 0]
            
            print(f"   Etiquetas encontradas: {len(labels_unicos)}")
            print(f"   Labels: {labels_unicos[:20]}")  # Mostrar primeros 20
            
            # Mapeo de labels a nombres (TotalSegmentator fast mode)
            # Labels según documentación de TotalSegmentator v2
            label_a_nombre = {
                1: 'spleen',
                2: 'kidney_right',
                3: 'kidney_left',
                4: 'gallbladder',
                5: 'liver',
                6: 'stomach',
                7: 'pancreas',
                8: 'adrenal_gland_right',
                9: 'adrenal_gland_left',
                10: 'lung_upper_lobe_left',
                11: 'lung_lower_lobe_left',
                12: 'lung_upper_lobe_right',
                13: 'lung_middle_lobe_right',
                14: 'lung_lower_lobe_right',
                15: 'esophagus',
                16: 'trachea',
                17: 'thyroid_gland',
                18: 'small_bowel',
                19: 'duodenum',
                20: 'colon',
                21: 'urinary_bladder',
                22: 'prostate',
                23: 'kidney_cyst_left',
                24: 'kidney_cyst_right',
                25: 'sacrum',
                26: 'vertebrae',
                27: 'intervertebral_discs',
                28: 'spinal_cord',
                29: 'heart',
                30: 'aorta',
                31: 'pulmonary_vein',
                32: 'brachiocephalic_trunk',
                33: 'subclavian_artery_right',
                34: 'subclavian_artery_left',
                35: 'common_carotid_artery_right',
                36: 'common_carotid_artery_left',
                37: 'brachiocephalic_vein_left',
                38: 'brachiocephalic_vein_right',
                39: 'atrial_appendage_left',
                40: 'superior_vena_cava',
                41: 'inferior_vena_cava',
                42: 'portal_vein_and_splenic_vein',
                43: 'iliac_artery_left',
                44: 'iliac_artery_right',
                45: 'iliac_vena_left',
                46: 'iliac_vena_right',
                47: 'humerus_left',
                48: 'humerus_right',
                49: 'scapula_left',
                50: 'scapula_right',
                51: 'clavicula_left',
                52: 'clavicula_right',
                53: 'femur_left',
                54: 'femur_right',
                55: 'hip_left',
                56: 'hip_right',
                57: 'gluteus_maximus_left',
                58: 'gluteus_maximus_right',
                59: 'gluteus_medius_left',
                60: 'gluteus_medius_right',
                61: 'gluteus_minimus_left',
                62: 'gluteus_minimus_right',
                63: 'autochthon_left',
                64: 'autochthon_right',
                65: 'iliopsoas_left',
                66: 'iliopsoas_right',
                67: 'brain',
                68: 'skull',
                69: 'rib_left_1',
                70: 'rib_left_2',
                71: 'rib_left_3',
                72: 'rib_left_4',
                73: 'rib_left_5',
                74: 'rib_left_6',
                75: 'rib_left_7',
                76: 'rib_left_8',
                77: 'rib_left_9',
                78: 'rib_left_10',
                79: 'rib_left_11',
                80: 'rib_left_12',
                81: 'rib_right_1',
                82: 'rib_right_2',
                83: 'rib_right_3',
                84: 'rib_right_4',
                85: 'rib_right_5',
                86: 'rib_right_6',
                87: 'rib_right_7',
                88: 'rib_right_8',
                89: 'rib_right_9',
                90: 'rib_right_10',
                91: 'rib_right_11',
                92: 'rib_right_12',
                93: 'sternum',
                94: 'costal_cartilages',
            }
            
            estructuras = {}
            
            for label in labels_unicos:
                nombre = label_a_nombre.get(int(label), f'estructura_{int(label)}')
                
                # Contar voxels de esta estructura
                voxels = int(np.sum(data == label))
                
                if voxels > 0:
                    estructuras[nombre] = {
                        'voxels': voxels,
                        'volumen_cm3': float(voxels * voxel_volume),
                        'label': int(label),
                        'color_rgb': self.ESTRUCTURAS_COLORES.get(nombre, (128, 128, 128))
                    }
                    
                    print(f"   - {nombre}: {voxels} voxels, {voxels * voxel_volume:.2f} cm³")
            
            # Ordenar por volumen
            estructuras_ordenadas = dict(
                sorted(estructuras.items(), key=lambda x: x[1]['volumen_cm3'], reverse=True)
            )
            
            print(f"\n   Total estructuras: {len(estructuras_ordenadas)}")
            print(f"{'='*80}\n")
            
            return {
                'metodo': 'totalsegmentator',
                'total_estructuras': len(estructuras_ordenadas),
                'estructuras': estructuras_ordenadas,
                'volumen_shape': list(data.shape),
                'mensaje': f'Segmentadas {len(estructuras_ordenadas)} estructuras anatómicas'
            }
            
        except Exception as e:
            logger.error(f"Error analizando volumen consolidado: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}
    
    def _segmentacion_basica(
        self, 
        ruta_archivo: str, 
        output_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Segmentación básica cuando TotalSegmentator no está disponible
        Usa umbralización simple para identificar tejidos
        """
        try:
            logger.info("📊 Ejecutando segmentación básica (sin TotalSegmentator)...")
            
            img = nib.load(ruta_archivo)
            data = img.get_fdata()
            
            # Segmentación simple por umbrales (CT Hounsfield units típicos)
            segmentos = {}
            
            # Aire/fondo
            segmentos['fondo'] = {
                'voxels': int(np.sum(data < -500)),
                'umbral': 'data < -500 HU',
                'interpretacion': 'Aire o fondo'
            }
            
            # Grasa
            segmentos['grasa'] = {
                'voxels': int(np.sum((data >= -120) & (data < -50))),
                'umbral': '-120 a -50 HU',
                'interpretacion': 'Tejido adiposo'
            }
            
            # Tejido blando
            segmentos['tejido_blando'] = {
                'voxels': int(np.sum((data >= 20) & (data < 80))),
                'umbral': '20 a 80 HU',
                'interpretacion': 'Órganos y músculos'
            }
            
            # Hueso
            segmentos['hueso'] = {
                'voxels': int(np.sum(data >= 200)),
                'umbral': '> 200 HU',
                'interpretacion': 'Estructura ósea'
            }
            
            # Calcular volúmenes
            voxel_volume = np.prod(img.header.get_zooms()[:3]) / 1000  # cm³
            
            for nombre, info in segmentos.items():
                info['volumen_cm3'] = float(info['voxels'] * voxel_volume)
            
            return {
                'metodo': 'segmentacion_basica',
                'mensaje': 'Segmentación por umbrales (instala TotalSegmentator para análisis avanzado)',
                'segmentos': segmentos,
                'total_estructuras': len(segmentos),
                'requiere_totalsegmentator': True
            }
            
        except Exception as e:
            logger.error(f"Error en segmentación básica: {e}")
            return {'error': str(e)}
    
    def _analizar_segmentacion(self, output_dir: Path, archivo_original: str) -> Dict[str, Any]:
        """Analiza los resultados de la segmentación"""
        try:
            # Cargar imagen original para obtener metadatos
            img_original = nib.load(archivo_original)
            voxel_volume = np.prod(img_original.header.get_zooms()[:3]) / 1000  # cm³
            
            # Buscar archivos de segmentación (.nii.gz)
            print(f"\n{'='*80}")
            print(f"🔍 DEBUG: Analizando archivos de segmentación")
            print(f"   Directorio base: {output_dir}")
            print(f"   Directorio existe: {output_dir.exists()}")
            
            # Buscar archivos en el directorio actual
            print(f"\n   Archivos en directorio base:")
            todos_archivos = list(output_dir.glob('*'))
            for f in todos_archivos:
                tipo = "DIR" if f.is_dir() else "FILE"
                print(f"      [{tipo}] {f.name} ({f.stat().st_size if f.is_file() else 'N/A'} bytes)")
            
            # Buscar RECURSIVAMENTE
            print(f"\n   Archivos .nii.gz (recursivo):")
            archivos_recursivos = list(output_dir.rglob('*.nii.gz'))
            for f in archivos_recursivos[:10]:  # Mostrar solo primeros 10
                print(f"      - {f.relative_to(output_dir)}")
            
            # Intentar diferentes patrones
            archivos_segmentacion = list(output_dir.glob('*.nii.gz'))
            print(f"\n   Archivos .nii.gz en raíz: {len(archivos_segmentacion)}")
            
            if not archivos_segmentacion:
                archivos_segmentacion = list(output_dir.glob('*.nii'))
                print(f"   Archivos .nii en raíz: {len(archivos_segmentacion)}")
            
            if not archivos_segmentacion:
                # Buscar en subdirectorios
                archivos_segmentacion = archivos_recursivos
                print(f"   Usando archivos recursivos: {len(archivos_segmentacion)}")
            
            print(f"{'='*80}\n")
            
            estructuras = {}
            
            for archivo in archivos_segmentacion:
                nombre_estructura = archivo.stem.replace('.nii', '')
                
                try:
                    # Cargar máscara
                    mascara = nib.load(str(archivo))
                    data_mascara = mascara.get_fdata()
                    
                    # Contar voxels de la estructura
                    voxels = int(np.sum(data_mascara > 0))
                    
                    if voxels > 0:
                        estructuras[nombre_estructura] = {
                            'voxels': voxels,
                            'volumen_cm3': float(voxels * voxel_volume),
                            'archivo_mascara': str(archivo),
                            'color_rgb': self.ESTRUCTURAS_COLORES.get(nombre_estructura, (128, 128, 128))
                        }
                
                except Exception as e:
                    logger.warning(f"Error procesando {archivo.name}: {e}")
            
            # Ordenar por volumen
            estructuras_ordenadas = dict(
                sorted(estructuras.items(), key=lambda x: x[1]['volumen_cm3'], reverse=True)
            )
            
            return {
                'metodo': 'totalsegmentator',
                'total_estructuras': len(estructuras_ordenadas),
                'estructuras': estructuras_ordenadas,
                'output_dir': str(output_dir),
                'mensaje': f'Segmentadas {len(estructuras_ordenadas)} estructuras anatómicas'
            }
            
        except Exception as e:
            logger.error(f"Error analizando segmentación: {e}")
            return {'error': str(e)}
    
    def generar_visualizacion_3d(
        self, 
        segmentacion: Dict[str, Any],
        top_n: int = 10
    ) -> Dict[str, Any]:
        """
        Genera datos para visualización 3D de las estructuras segmentadas
        
        Args:
            segmentacion: Resultados de segmentación
            top_n: Número de estructuras principales a incluir
        
        Returns:
            Dict con datos listos para visualizar en frontend
        """
        if 'estructuras' not in segmentacion:
            return {'error': 'Sin datos de estructuras'}
        
        estructuras = segmentacion['estructuras']
        
        # Seleccionar top N estructuras por volumen
        top_estructuras = list(estructuras.items())[:top_n]
        
        # Preparar datos para visualización
        vis_data = {
            'estructuras': [],
            'total_volumen': 0,
            'colores': []
        }
        
        for nombre, datos in top_estructuras:
            vis_data['estructuras'].append({
                'nombre': nombre.replace('_', ' ').title(),
                'volumen': datos['volumen_cm3'],
                'color': {
                    'r': datos['color_rgb'][0],
                    'g': datos['color_rgb'][1],
                    'b': datos['color_rgb'][2]
                },
                'porcentaje': 0  # Se calculará después
            })
            
            vis_data['total_volumen'] += datos['volumen_cm3']
        
        # Calcular porcentajes
        for estructura in vis_data['estructuras']:
            if vis_data['total_volumen'] > 0:
                estructura['porcentaje'] = (estructura['volumen'] / vis_data['total_volumen']) * 100
        
        return vis_data
    
    def generar_reporte_anatomico(self, segmentacion: Dict[str, Any]) -> str:
        """Genera reporte legible de la segmentación anatómica"""
        if 'error' in segmentacion:
            return f"Error en segmentación: {segmentacion['error']}"
        
        lineas = []
        lineas.append("=" * 80)
        lineas.append("🔬 SEGMENTACIÓN ANATÓMICA DETALLADA")
        lineas.append("=" * 80)
        lineas.append("")
        
        lineas.append(f"Método: {segmentacion.get('metodo', 'desconocido').upper()}")
        lineas.append(f"Estructuras identificadas: {segmentacion.get('total_estructuras', 0)}")
        lineas.append("")
        
        if 'estructuras' in segmentacion:
            lineas.append("📊 ESTRUCTURAS PRINCIPALES (ordenadas por volumen):")
            lineas.append("")
            
            estructuras = list(segmentacion['estructuras'].items())[:15]  # Top 15
            
            for i, (nombre, datos) in enumerate(estructuras, 1):
                nombre_legible = nombre.replace('_', ' ').title()
                volumen = datos.get('volumen_cm3', 0)
                lineas.append(f"  {i:2d}. {nombre_legible:40s} {volumen:8.2f} cm³")
        
        elif 'segmentos' in segmentacion:
            lineas.append("📊 SEGMENTACIÓN POR UMBRALES:")
            lineas.append("")
            
            for nombre, datos in segmentacion['segmentos'].items():
                lineas.append(f"  • {datos['interpretacion']:30s}")
                lineas.append(f"    Umbral: {datos['umbral']}")
                lineas.append(f"    Volumen: {datos.get('volumen_cm3', 0):.2f} cm³")
                lineas.append("")
        
        if segmentacion.get('requiere_totalsegmentator'):
            lineas.append("")
            lineas.append("💡 RECOMENDACIÓN:")
            lineas.append("   Instala TotalSegmentator para segmentación anatómica detallada")
            lineas.append("   pip install totalsegmentator")
        
        lineas.append("")
        lineas.append("=" * 80)
        
        return "\n".join(lineas)


# Instancia global
_segmentador = None

def get_segmentador() -> SegmentadorAnatomico:
    """Obtiene instancia única del segmentador"""
    global _segmentador
    if _segmentador is None:
        _segmentador = SegmentadorAnatomico()
    return _segmentador
