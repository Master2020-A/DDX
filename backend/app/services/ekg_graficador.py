"""
Servicio de graficación de EKG con anotaciones
Genera imágenes con marcadores de ondas
"""

import matplotlib
matplotlib.use('Agg')  # Backend sin GUI
import matplotlib.pyplot as plt
import numpy as np
import io
from typing import Dict, List, Any
import base64


class EKGGraficador:
    """Genera gráficas anotadas de EKG"""
    
    @staticmethod
    def crear_imagen_anotada(
        signal: np.ndarray,
        waves: Dict,
        measurements: Dict,
        sampling_rate: int = 500
    ) -> bytes:
        """
        Crea imagen de EKG con anotaciones
        
        Args:
            signal: Señal procesada
            waves: Ondas detectadas
            measurements: Mediciones
            sampling_rate: Frecuencia de muestreo
            
        Returns:
            Bytes de la imagen PNG
        """
        # Configuración de estilo médico
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(14, 7))
        
        # Crear eje de tiempo (segundos)
        t = np.arange(len(signal)) / sampling_rate
        
        # 1. Dibujar Cuadrícula Médica (Grid)
        ax.set_xticks(np.arange(0, t[-1], 0.2))
        ax.set_yticks(np.arange(np.min(signal), np.max(signal), 0.5))
        ax.grid(which='major', linestyle='-', linewidth='0.5', color='red', alpha=0.3)
        ax.minorticks_on()
        ax.grid(which='minor', linestyle=':', linewidth='0.5', color='red', alpha=0.2)
        
        # 2. Dibujar Señal Limpia
        ax.plot(t, signal, color='black', linewidth=1.5, label='ECG Digitalizado')
        
        # 3. Anotar Picos Detectados
        EKGGraficador._plot_wave_points(
            ax, signal, waves.get('R_peaks', []), sampling_rate,
            '#e74c3c', 'v', 'R Peak', 10
        )
        EKGGraficador._plot_wave_points(
            ax, signal, waves.get('P_peaks', []), sampling_rate,
            '#2ecc71', 'o', 'P Wave', 8
        )
        EKGGraficador._plot_wave_points(
            ax, signal, waves.get('T_peaks', []), sampling_rate,
            '#3498db', 's', 'T Wave', 8
        )
        EKGGraficador._plot_wave_points(
            ax, signal, waves.get('Q_peaks', []), sampling_rate,
            '#9b59b6', '.', 'Q Wave', 6
        )
        EKGGraficador._plot_wave_points(
            ax, signal, waves.get('S_peaks', []), sampling_rate,
            '#e67e22', '.', 'S Wave', 6
        )
        
        # 4. Caja de Información
        info_text = (
            f"FC:  {measurements.get('heart_rate', 0):.0f} bpm\n"
            f"PR:  {measurements.get('PR_interval', 0):.0f} ms\n"
            f"QRS: {measurements.get('QRS_duration', 0):.0f} ms\n"
            f"QTc: {measurements.get('QTc', 0):.0f} ms\n"
            f"ST:  {measurements.get('ST_level', 0):.2f} mV\n"
            f"Eje: {measurements.get('QRS_Axis', 0)}°"
        )
        
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)
        ax.text(0.02, 0.95, info_text, transform=ax.transAxes, fontsize=12,
                verticalalignment='top', bbox=props, fontfamily='monospace')
        
        # Títulos
        ax.set_title("ANÁLISIS DIGITALIZADO CON MARCADORES DE ONDAS", 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel("Tiempo (s)", fontsize=12)
        ax.set_ylabel("Amplitud (mV)", fontsize=12)
        ax.legend(loc='upper right', fontsize=10)
        
        plt.tight_layout()
        
        # Guardar en buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        return buf.getvalue()
    
    @staticmethod
    def _plot_wave_points(
        ax, signal, indices, sampling_rate, color, marker, label, markersize
    ):
        """Función auxiliar para graficar puntos de ondas"""
        if indices is None or len(indices) == 0:
            return
        
        # Convertir a numpy array
        idx_arr = np.array(indices, dtype=int)
        
        # Filtrar índices fuera de rango
        idx_arr = idx_arr[idx_arr < len(signal)]
        
        if len(idx_arr) > 0:
            x_vals = idx_arr / sampling_rate
            y_vals = signal[idx_arr]
            ax.plot(x_vals, y_vals, marker, color=color, 
                   markersize=markersize, label=label, linestyle='None')
    
    @staticmethod
    def crear_imagen_base64(
        signal: np.ndarray,
        waves: Dict,
        measurements: Dict,
        sampling_rate: int = 500
    ) -> str:
        """
        Crea imagen en formato base64 para web
        
        Returns:
            String base64 de la imagen
        """
        image_bytes = EKGGraficador.crear_imagen_anotada(
            signal, waves, measurements, sampling_rate
        )
        return base64.b64encode(image_bytes).decode('utf-8')
