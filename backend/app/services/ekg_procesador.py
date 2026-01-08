"""
Servicio de procesamiento de señales de EKG
Limpia y prepara señales para análisis
"""

import numpy as np
from scipy import signal as sig
from scipy.ndimage import gaussian_filter1d


class EKGProcesador:
    """Procesa y limpia señales de EKG"""
    
    def __init__(self, sampling_rate: int = 500):
        self.sampling_rate = sampling_rate
    
    def procesar_completo(self, ecg_signal: np.ndarray) -> np.ndarray:
        """
        Procesa señal de EKG completa
        
        Args:
            ecg_signal: Array numpy con señal cruda
            
        Returns:
            Señal procesada y normalizada
        """
        # 1. Eliminar NaN o Infinitos
        ecg_signal = np.nan_to_num(ecg_signal)
        
        # 2. Suavizado (Gaussian Filter) para reducir ruido de alta frecuencia
        # Sigma 2 ayuda a quitar los picos 'sucios' que confunden al detector
        smooth_signal = gaussian_filter1d(ecg_signal, sigma=2)
        
        # 3. Eliminar deriva de línea base (Detrend)
        smooth_signal = sig.detrend(smooth_signal)
        
        # 4. Normalización Min-Max (0 a 1)
        # Esto es CRÍTICO para que los umbrales de detección funcionen igual en cualquier imagen
        min_val = np.min(smooth_signal)
        max_val = np.max(smooth_signal)
        
        if max_val - min_val > 0:
            normalized_signal = (smooth_signal - min_val) / (max_val - min_val)
        else:
            normalized_signal = smooth_signal
        
        return normalized_signal
    
    def calcular_calidad_senal(self, ecg_signal: np.ndarray) -> float:
        """
        Calcula índice de calidad de la señal (0-100)
        
        Args:
            ecg_signal: Señal de EKG
            
        Returns:
            Score de calidad (0-100)
        """
        # Por ahora retorna 100, se puede mejorar con métricas SNR
        return 100.0
