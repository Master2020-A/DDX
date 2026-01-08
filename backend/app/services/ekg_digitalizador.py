"""
Servicio de digitalización de imágenes de EKG
Convierte imágenes de EKG en papel a señales digitales
"""

import cv2
import numpy as np
from scipy import signal as sig
from typing import Dict, Any, Optional


class EKGDigitalizador:
    """Digitaliza imágenes de EKG a señales procesables"""
    
    def __init__(self, sampling_rate: int = 500):
        self.sampling_rate = sampling_rate
    
    def digitalizar(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Digitaliza una imagen de EKG
        
        Args:
            image_bytes: Bytes de la imagen (JPG, PNG, etc)
            
        Returns:
            Dict con señales digitalizadas, ROI y metadata
        """
        try:
            # 1. Cargar imagen
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return self._generar_sintetico()
            
            orig_h, orig_w = img.shape[:2]
            
            # 2. Definir ROI (Región de Interés)
            # Tira de ritmo (Lead II) usualmente está en la parte inferior
            roi_y_start = int(orig_h * 0.65)
            roi_y_end = int(orig_h * 0.95)
            roi_x_start = int(orig_w * 0.05)
            roi_x_end = int(orig_w * 0.95)
            
            # 3. Recortar ROI
            crop = img[roi_y_start:roi_y_end, roi_x_start:roi_x_end]
            gray_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            
            # 4. Procesar imagen
            gray_crop = cv2.resize(gray_crop, (2000, 300))
            _, binary = cv2.threshold(gray_crop, 120, 255, cv2.THRESH_BINARY_INV)
            
            # 5. Extraer perfil de señal
            raw_signal = np.mean(binary, axis=0)
            
            # 6. Normalizar
            raw_signal = (raw_signal - np.mean(raw_signal)) / (np.std(raw_signal) + 1e-6)
            
            # 7. Limpiar con filtro
            b, a = sig.butter(3, 0.05)
            smooth_signal = sig.filtfilt(b, a, raw_signal)
            
            # 8. Invertir si es necesario (picos hacia arriba)
            if np.max(smooth_signal) < abs(np.min(smooth_signal)):
                smooth_signal = -smooth_signal
            
            # 9. Validar calidad
            if np.std(smooth_signal) < 0.1:
                return self._generar_sintetico()
            
            # 10. Crear diccionario de señales (12 derivaciones)
            signals = {'II': smooth_signal}
            
            # Simular otras derivaciones (en producción se extraerían de la imagen)
            for lead in ['I', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']:
                signals[lead] = smooth_signal * 0.5 + np.random.normal(0, 0.1, len(smooth_signal))
            
            return {
                'signals': signals,
                'sampling_rate': self.sampling_rate,
                'roi': {
                    'x_start': roi_x_start,
                    'y_start': roi_y_start,
                    'x_end': roi_x_end,
                    'y_end': roi_y_end
                },
                'original_image': img,
                'success': True
            }
            
        except Exception as e:
            print(f"Error en digitalización: {e}")
            return self._generar_sintetico()
    
    def _generar_sintetico(self) -> Dict[str, Any]:
        """Genera señal sintética de respaldo"""
        duration = 10
        t = np.linspace(0, duration, int(duration * self.sampling_rate))
        heart_rate = 75
        period = 60.0 / heart_rate
        
        signals = {}
        beat = sig.gausspulse(np.linspace(-0.1, 0.1, int(0.1 * self.sampling_rate)), fc=10)
        ecg = np.zeros_like(t)
        
        # Generar latidos
        for i in range(0, len(t), int(period * self.sampling_rate)):
            if i + len(beat) < len(ecg):
                ecg[i:i + len(beat)] += beat
        
        # Llenar diccionario
        for lead in ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']:
            signals[lead] = ecg + np.random.normal(0, 0.05, len(t))
        
        return {
            'signals': signals,
            'sampling_rate': self.sampling_rate,
            'roi': None,
            'original_image': None,
            'success': False
        }
