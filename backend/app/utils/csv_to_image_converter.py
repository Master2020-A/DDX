"""
Utilidad para convertir archivos CSV de ECG/EEG a imágenes
Permite análisis visual con IA cuando el CSV contiene solo señales temporales
"""
import csv
import io
from typing import Optional, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFont

try:
    import matplotlib
    matplotlib.use('Agg')  # Backend sin GUI
    import matplotlib.pyplot as plt
    MATPLOTLIB_DISPONIBLE = True
except ImportError:
    MATPLOTLIB_DISPONIBLE = False
    print("⚠️ Matplotlib no disponible. Instalar con: pip install matplotlib")


class CSVToImageConverter:
    """Convierte archivos CSV de señales ECG/EEG a imágenes para análisis con IA"""
    
    def __init__(self):
        self.matplotlib_disponible = MATPLOTLIB_DISPONIBLE
    
    def convertir_csv_a_imagen(
        self, 
        csv_path: str,
        num_derivaciones: int = 12,
        duracion_segundos: Optional[float] = None,
        frecuencia_muestreo: int = 500,
        titulo: str = "Electrocardiograma",
        output_path: Optional[str] = None
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Convierte CSV de señales a imagen
        
        Args:
            csv_path: Ruta al archivo CSV
            num_derivaciones: Número de derivaciones a graficar (default: 12)
            duracion_segundos: Duración a graficar (None = todo)
            frecuencia_muestreo: Frecuencia de muestreo en Hz
            titulo: Título de la gráfica
            output_path: Ruta para guardar (None = retorna bytes)
        
        Returns:
            (imagen_bytes, error_mensaje)
        """
        if not self.matplotlib_disponible:
            return None, "Matplotlib no está instalado. Instalar con: pip install matplotlib"
        
        try:
            # Leer CSV
            with open(csv_path, 'r') as f:
                reader = csv.reader(f)
                filas = list(reader)
            
            if not filas:
                return None, "Archivo CSV vacío"
            
            # Verificar si tiene encabezados
            primera_fila_numerica = True
            try:
                for val in filas[0][:5]:
                    float(val.strip())
            except:
                primera_fila_numerica = False
                filas = filas[1:]  # Saltar encabezados
            
            # Convertir a numpy array
            try:
                data = np.array([[float(val) for val in fila] for fila in filas])
            except Exception as e:
                return None, f"Error convirtiendo datos a números: {e}"
            
            num_muestras, num_canales = data.shape
            
            # Limitar número de derivaciones
            num_derivaciones = min(num_derivaciones, num_canales)
            
            # Calcular muestras a mostrar
            if duracion_segundos:
                muestras_a_mostrar = int(duracion_segundos * frecuencia_muestreo)
                muestras_a_mostrar = min(muestras_a_mostrar, num_muestras)
            else:
                muestras_a_mostrar = num_muestras
            
            # Crear figura
            fig, axes = plt.subplots(
                num_derivaciones, 1, 
                figsize=(15, num_derivaciones * 1.5),
                sharex=True
            )
            
            if num_derivaciones == 1:
                axes = [axes]
            
            fig.suptitle(titulo, fontsize=16, fontweight='bold')
            
            # Nombres de derivaciones estándar
            nombres_derivaciones = [
                'I', 'II', 'III', 'aVR', 'aVL', 'aVF',
                'V1', 'V2', 'V3', 'V4', 'V5', 'V6'
            ]
            
            # Graficar cada derivación
            tiempo = np.arange(muestras_a_mostrar) / frecuencia_muestreo
            
            for i in range(num_derivaciones):
                ax = axes[i]
                señal = data[:muestras_a_mostrar, i]
                
                # Graficar señal
                ax.plot(tiempo, señal, linewidth=0.8, color='black')
                
                # Etiqueta de derivación
                nombre_derivacion = nombres_derivaciones[i] if i < len(nombres_derivaciones) else f'Lead {i+1}'
                ax.set_ylabel(nombre_derivacion, fontsize=10, fontweight='bold')
                
                # Grid estilo ECG
                ax.grid(True, which='both', linestyle='-', linewidth=0.5, alpha=0.3, color='red')
                ax.grid(True, which='minor', linestyle='-', linewidth=0.3, alpha=0.2, color='red')
                
                # Configurar ejes
                ax.set_xlim(0, tiempo[-1])
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                
                # Ocultar etiquetas de eje Y excepto la última
                if i < num_derivaciones - 1:
                    ax.set_xticklabels([])
            
            # Etiqueta del eje X solo en el último subplot
            axes[-1].set_xlabel('Tiempo (segundos)', fontsize=12)
            
            # Información adicional
            info_text = f'Frecuencia: {frecuencia_muestreo} Hz | Duración: {tiempo[-1]:.2f}s | Derivaciones: {num_derivaciones}'
            fig.text(0.5, 0.02, info_text, ha='center', fontsize=10, style='italic')
            
            # Ajustar layout
            plt.tight_layout(rect=[0, 0.03, 1, 0.97])
            
            # Guardar o retornar bytes
            if output_path:
                plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
                plt.close()
                return None, None
            else:
                # Guardar en buffer
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor='white')
                buf.seek(0)
                imagen_bytes = buf.read()
                plt.close()
                return imagen_bytes, None
        
        except Exception as e:
            return None, f"Error convirtiendo CSV a imagen: {str(e)}"
    
    def crear_imagen_simple(
        self,
        csv_path: str,
        num_derivaciones: int = 4
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Crea una imagen simple sin matplotlib (fallback)
        Solo muestra información básica del CSV
        """
        try:
            # Leer CSV
            with open(csv_path, 'r') as f:
                reader = csv.reader(f)
                filas = list(reader)
            
            if not filas:
                return None, "Archivo CSV vacío"
            
            num_muestras = len(filas)
            num_canales = len(filas[0])
            
            # Crear imagen con información
            img = Image.new('RGB', (800, 600), color='white')
            draw = ImageDraw.Draw(img)
            
            # Título
            draw.text((400, 50), "Archivo CSV de ECG", fill='black', anchor='mm')
            draw.text((400, 100), f"Muestras: {num_muestras}", fill='black', anchor='mm')
            draw.text((400, 130), f"Canales: {num_canales}", fill='black', anchor='mm')
            draw.text((400, 160), f"Formato: Serie temporal", fill='black', anchor='mm')
            
            draw.text((400, 250), "⚠️ Matplotlib no disponible", fill='red', anchor='mm')
            draw.text((400, 280), "Instalar para ver gráficas:", fill='black', anchor='mm')
            draw.text((400, 310), "pip install matplotlib", fill='blue', anchor='mm')
            
            # Guardar en buffer
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            return buf.read(), None
        
        except Exception as e:
            return None, f"Error creando imagen simple: {str(e)}"


def convertir_csv_ecg_a_imagen(
    csv_path: str,
    num_derivaciones: int = 12,
    output_path: Optional[str] = None
) -> Tuple[Optional[bytes], Optional[str]]:
    """
    Función de conveniencia para convertir CSV de ECG a imagen
    
    Args:
        csv_path: Ruta al archivo CSV
        num_derivaciones: Número de derivaciones a graficar (default: 12)
        output_path: Ruta para guardar (None = retorna bytes)
    
    Returns:
        (imagen_bytes, error_mensaje)
    
    Ejemplo:
        >>> imagen_bytes, error = convertir_csv_ecg_a_imagen('ecg.csv')
        >>> if imagen_bytes:
        >>>     with open('ecg.png', 'wb') as f:
        >>>         f.write(imagen_bytes)
    """
    converter = CSVToImageConverter()
    
    if converter.matplotlib_disponible:
        return converter.convertir_csv_a_imagen(
            csv_path=csv_path,
            num_derivaciones=num_derivaciones,
            output_path=output_path
        )
    else:
        return converter.crear_imagen_simple(csv_path, num_derivaciones)
