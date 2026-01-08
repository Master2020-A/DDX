"""
Servicio de detección de ondas en señales de EKG
Detecta ondas P, Q, R, S, T y calcula intervalos
"""

import numpy as np
from scipy import signal as sig
from typing import Dict, List, Any


class EKGDetectorOndas:
    """Detecta ondas y calcula mediciones en señales de EKG"""
    
    def __init__(self, sampling_rate: int = 500):
        self.sampling_rate = sampling_rate
    
    def analisis_completo(self, ecg_signal: np.ndarray) -> Dict[str, Any]:
        """
        Realiza análisis completo de ondas y mediciones
        
        Args:
            ecg_signal: Señal procesada de EKG
            
        Returns:
            Dict con ondas detectadas e intervalos medidos
        """
        # Inicializar diccionario de salida
        measurements = {
            'heart_rate': 0,
            'RR_mean': 0,
            'RR_std': 0,
            'PR_interval': 0,
            'QRS_duration': 0,
            'QT_interval': 0,
            'QTc': 0,
            'P_amplitude': 0,
            'R_amplitude': 0,
            'T_amplitude': 0,
            'ST_level': 0,
            'QRS_Axis': 45  # Valor por defecto
        }
        
        waves = {
            'R_peaks': [],
            'P_peaks': [],
            'T_peaks': [],
            'Q_peaks': [],
            'S_peaks': []
        }
        
        # --- ESTRATEGIA DE DETECCIÓN ADAPTATIVA ---
        # Intentamos buscar picos con diferentes sensibilidades hasta encontrar algo coherente
        
        # Intento 1: Búsqueda estándar (Prominencia 0.4)
        peaks, _ = sig.find_peaks(ecg_signal, prominence=0.4, distance=int(self.sampling_rate * 0.3))
        
        # Intento 2: Si hay pocos picos, bajar exigencia (Prominencia 0.2)
        if len(peaks) < 2:
            peaks, _ = sig.find_peaks(ecg_signal, prominence=0.2, distance=int(self.sampling_rate * 0.3))
        
        # Intento 3: Muy sensible (Prominencia 0.1) - Para señales de bajo voltaje
        if len(peaks) < 2:
            peaks, _ = sig.find_peaks(ecg_signal, prominence=0.1, distance=int(self.sampling_rate * 0.25))
        
        waves['R_peaks'] = peaks.tolist()
        
        # Si tras 3 intentos no hay al menos 2 picos, no podemos calcular FC
        if len(peaks) < 2:
            return {'waves': waves, 'intervals': measurements}
        
        # --- CÁLCULOS PRINCIPALES ---
        
        # 1. Frecuencia Cardíaca (FC)
        rr_intervals = np.diff(peaks)  # en muestras
        rr_ms = rr_intervals * (1000 / self.sampling_rate)  # en ms
        
        # Filtrar intervalos RR locos (ruido)
        # Un RR normal está entre 300ms (200bpm) y 1500ms (40bpm)
        valid_rr = rr_ms[(rr_ms > 300) & (rr_ms < 1500)]
        
        if len(valid_rr) > 0:
            rr_mean = np.mean(valid_rr)
            measurements['RR_mean'] = float(rr_mean)
            measurements['RR_std'] = float(np.std(valid_rr))
            measurements['heart_rate'] = float(60000 / rr_mean)
        else:
            # Si no hay RR válidos, usar el promedio crudo
            measurements['RR_mean'] = float(np.mean(rr_ms))
            measurements['RR_std'] = float(np.std(rr_ms))
            measurements['heart_rate'] = float(60000 / measurements['RR_mean'])
        
        # 2. Análisis de Ondas (P, Q, S, T)
        # Acumuladores para promedios
        qrs_durs = []
        pr_ints = []
        qt_ints = []
        st_levels = []
        p_amps = []
        t_amps = []
        
        for r_idx in peaks:
            # Ventanas de búsqueda (basadas en fisiología normal a 500Hz)
            
            # --- DETECCIÓN QRS ---
            win_q = int(0.05 * self.sampling_rate)  # 50ms
            win_s = int(0.05 * self.sampling_rate)
            
            start_q = max(0, r_idx - win_q)
            end_s = min(len(ecg_signal), r_idx + win_s)
            
            # Q es el mínimo local antes de R
            segment_q = ecg_signal[start_q:r_idx]
            if len(segment_q) > 0:
                q_local = np.argmin(segment_q)
                q_idx = start_q + q_local
                waves['Q_peaks'].append(int(q_idx))
            else:
                q_idx = r_idx
            
            # S es el mínimo local después de R
            segment_s = ecg_signal[r_idx:end_s]
            if len(segment_s) > 0:
                s_local = np.argmin(segment_s)
                s_idx = r_idx + s_local
                waves['S_peaks'].append(int(s_idx))
            else:
                s_idx = r_idx
            
            # Duración QRS
            qrs_ms = (s_idx - q_idx) * (1000 / self.sampling_rate)
            # Corrección: El ancho visual suele ser mayor que el pico-a-pico
            # Agregamos un factor de corrección de ~20ms
            if qrs_ms > 0:
                qrs_durs.append(qrs_ms + 20)
            
            # --- ONDA P ---
            # P: Buscar máximo entre 200ms y 50ms antes de R
            win_p_start = int(0.25 * self.sampling_rate)
            win_p_end = int(0.05 * self.sampling_rate)
            
            p_search_start = max(0, r_idx - win_p_start)
            p_search_end = max(0, r_idx - win_p_end)
            
            segment_p = ecg_signal[p_search_start:p_search_end]
            if len(segment_p) > 0:
                # P debe ser un pico positivo prominente
                p_local = np.argmax(segment_p)
                p_idx = p_search_start + p_local
                waves['P_peaks'].append(int(p_idx))
                
                # Amplitud P
                p_amps.append(ecg_signal[p_idx])
                
                # Intervalo PR
                pr_ms = (r_idx - p_idx) * (1000 / self.sampling_rate)
                if 80 < pr_ms < 300:
                    pr_ints.append(pr_ms)
            
            # --- ONDA T ---
            # T: Buscar máximo entre 100ms y 400ms después de R
            win_t_start = int(0.10 * self.sampling_rate)
            win_t_end = int(0.45 * self.sampling_rate)
            
            t_search_start = min(len(ecg_signal), r_idx + win_t_start)
            t_search_end = min(len(ecg_signal), r_idx + win_t_end)
            
            segment_t = ecg_signal[t_search_start:t_search_end]
            if len(segment_t) > 0:
                t_local = np.argmax(segment_t)
                t_idx = t_search_start + t_local
                waves['T_peaks'].append(int(t_idx))
                
                # Amplitud T
                t_amps.append(ecg_signal[t_idx])
                
                # Intervalo QT (Q a T)
                qt_ms = (t_idx - q_idx) * (1000 / self.sampling_rate)
                # Corrección: QT es hasta el FINAL de la T, no el pico.
                # Sumamos ~60ms estimando el ancho de la T
                if 200 < qt_ms < 600:
                    qt_ints.append(qt_ms + 60)
            
            # --- SEGMENTO ST ---
            # Medir nivel 60ms después del punto J (o pico S)
            st_idx = min(len(ecg_signal) - 1, s_idx + int(0.06 * self.sampling_rate))
            # Nivel ST relativo a la línea base (estimada como el punto Q)
            baseline = ecg_signal[q_idx]
            st_val = ecg_signal[st_idx] - baseline
            st_levels.append(st_val)
        
        # 3. Promediar resultados
        if len(qrs_durs) > 0:
            measurements['QRS_duration'] = float(np.mean(qrs_durs))
        if len(pr_ints) > 0:
            measurements['PR_interval'] = float(np.mean(pr_ints))
        if len(qt_ints) > 0:
            measurements['QT_interval'] = float(np.mean(qt_ints))
        if len(st_levels) > 0:
            measurements['ST_level'] = float(np.mean(st_levels))
        if len(p_amps) > 0:
            measurements['P_amplitude'] = float(np.mean(p_amps))
        if len(t_amps) > 0:
            measurements['T_amplitude'] = float(np.mean(t_amps))
        
        # QTc Bazett
        if measurements['RR_mean'] > 0 and measurements['QT_interval'] > 0:
            measurements['QTc'] = float(
                measurements['QT_interval'] / np.sqrt(measurements['RR_mean'] / 1000)
            )
        
        # Amplitudes (Aproximadas ya que la señal está normalizada 0-1)
        # Asumimos que 1 unidad normalizada ~= 2 mV para escalar a valores 'reales'
        scaling_factor = 2.0
        if len(peaks) > 0:
            measurements['R_amplitude'] = float(np.mean(ecg_signal[peaks]) * scaling_factor)
        
        return {'waves': waves, 'intervals': measurements}
