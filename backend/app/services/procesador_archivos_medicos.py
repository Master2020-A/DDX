"""
Procesador avanzado de archivos médicos
Soporta: .ecg, .mat, PDF, imágenes, CSV
Incluye análisis mejorado de anomalías + IA + conversión CSV a imagen
"""
import re
import struct
import numpy as np
import csv
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Procesamiento de archivos
try:
    import scipy.io
    from PIL import Image
    import pytesseract
    import PyPDF2
    from pdf2image import convert_from_path
    DEPENDENCIAS_DISPONIBLES = True
except ImportError:
    DEPENDENCIAS_DISPONIBLES = False
    print("⚠️ Advertencia: Faltan dependencias (scipy, pytesseract, Pillow, PyPDF2)")

# Utilidad de conversión CSV a imagen
try:
    from app.utils.csv_to_image_converter import CSVToImageConverter
    CSV_CONVERTER_DISPONIBLE = True
except ImportError:
    CSV_CONVERTER_DISPONIBLE = False
    print("⚠️ Advertencia: Conversor CSV a imagen no disponible")


class ProcesadorArchivosMedicos:
    """
    Procesador avanzado de archivos médicos con soporte para:
    - Archivos ECG (.ecg, .dat)
    - Archivos MATLAB (.mat)
    - PDF e imágenes (con OCR)
    """
    
    def __init__(self):
        if not DEPENDENCIAS_DISPONIBLES:
            raise ImportError(
                "Faltan dependencias. Ejecuta: "
                "pip install scipy pytesseract Pillow PyPDF2 pdf2image"
            )
        
        # Inicializar conversor CSV a imagen si está disponible
        self.csv_converter = CSVToImageConverter() if CSV_CONVERTER_DISPONIBLE else None
    
    # ==================== PATRONES MEJORADOS ====================
    
    # Patrones para detectar ANOMALÍAS en texto (MEJORADOS)
    PATRONES_ANOMALIAS_EKG = {
        'bradicardia': [
            r'bradicardia',
            r'FC.*?(?:baja|bajo|lenta)',
            r'(?:FC|Heart\s+Rate)[:\s]*([1-5]\d)\s*(?:lpm|bpm)',  # FC < 60
        ],
        'taquicardia': [
            r'taquicardia',
            r'FC.*?(?:alta|alto|elevada|rápida)',
            r'(?:FC|Heart\s+Rate)[:\s]*(1[0-9]{2,}|[2-9]\d{2})\s*(?:lpm|bpm)',  # FC > 100
        ],
        'arritmia': [
            r'arritmia',
            r'fibrilaci[oó]n',
            r'extrasístole',
            r'ritmo\s+irregular',
            r'flutter',
            r'bloqueo\s+av\s+ocasional',
        ],
        'bloqueo_av': [
            r'bloqueo\s+(?:AV|auriculoventricular)',
            r'PR\s+prolongado',
            r'(?:PR)[:\s]*(2[0-9]{2,})\s*ms',  # PR > 200ms
            r'bloqueo\s+av.*?grado',
        ],
        'bloqueo_rama': [
            r'bloqueo.*?rama.*?(?:derecha|izquierda)',
            r'(?:BRDHH|BRIHH|RBBB|LBBB)',
            r'QRS.*?(?:ensanchado|ancho)',
            r'bloqueo.*?incompleto',
        ],
        'desviacion_eje': [
            r'desviaci[oó]n.*?eje',
            r'eje.*?(?:derecho|izquierdo|extremo)',
            r'axis.*?deviation',
        ],
        'isquemia': [
            r'isquemia',
            r'infarto',
            r'ST\s+(?:elevado|deprimido)',
            r'onda\s+Q\s+patol[oó]gica',
            r'infarto.*?(?:anterior|inferior|lateral|posterior)',
            r'(?:STEMI|NSTEMI)',
        ],
        'hipertrofia': [
            r'hipertrofia.*?(?:ventricular|auricular)',
            r'(?:HVI|HVD|HAI|HAD)',
            r'crecimiento.*?(?:ventricular|auricular)',
        ],
        'qt_prolongado': [
            r'QT\s+prolongado',
            r'(?:QTc)[:\s]*([4-9]\d{2,})\s*ms',  # QTc > 440ms
        ],
        'alteraciones_repolarizacion': [
            r'alteraci[oó]n.*?repolarizaci[oó]n',
            r'cambios.*?(?:ST|onda\s+T)',
            r'onda\s+T.*?(?:invertida|negativa|aplanada)',
        ],
    }
    
    PATRONES_ANOMALIAS_EEG = {
        'epileptiforme': [
            r'epileptiforme',
            r'espiga',
            r'punta[\s-]onda',
            r'onda\s+aguda',
            r'parox[ií]stica',
        ],
        'enlentecimiento': [
            r'enlentecimiento',
            r'actividad\s+lenta',
            r'delta\s+(?:difusa|focal)',
        ],
        'asimetria': [
            r'asimetr[ií]a',
            r'asim[eé]trica',
            r'lateralizada',
        ],
    }
    
    # Rangos normales para validación (MEJORADOS)
    RANGOS_NORMALES = {
        'ekg': {
            'frecuencia_cardiaca': (60, 100),
            'intervalo_pr': (120, 200),
            'duracion_qrs': (60, 100),  # >120 = bloqueo de rama
            'intervalo_qt': (350, 450),
            'intervalo_qtc': (350, 440),  # Hombres <440, Mujeres <460
            'eje_qrs': (-30, 90),  # Normal: -30 a +90
            # Desviaciones:
            # Eje derecho: +90 a +180
            # Eje izquierdo: -30 a -90
            # Eje extremo: -90 a -180
        },
        'eeg': {
            'frecuencia_dominante': (8, 13),  # Ritmo alfa normal
        }
    }
    
    # Criterios adicionales de anomalías
    CRITERIOS_ANOMALIAS = {
        'taquicardia_leve': (100, 120),
        'taquicardia_moderada': (120, 150),
        'taquicardia_severa': (150, 999),
        'bradicardia_leve': (50, 60),
        'bradicardia_moderada': (40, 50),
        'bradicardia_severa': (0, 40),
        'eje_derecho': (90, 180),
        'eje_izquierdo': (-90, -30),
        'eje_extremo': (-180, -90),
    }
    
    # ==================== PROCESAMIENTO POR TIPO ====================
    
    def procesar_archivo(self, archivo_path: str) -> Dict[str, Any]:
        """
        Procesa un archivo médico y extrae datos + análisis de anomalías
        """
        extension = Path(archivo_path).suffix.lower()
        
        if extension == '.ecg':
            return self._procesar_ecg(archivo_path)
        elif extension == '.mat':
            return self._procesar_mat(archivo_path)
        elif extension == '.csv':
            return self._procesar_csv(archivo_path)
        elif extension == '.pdf':
            return self._procesar_pdf(archivo_path)
        elif extension in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
            return self._procesar_imagen(archivo_path)
        else:
            raise ValueError(f"Formato no soportado: {extension}")
    
    # ==================== ARCHIVOS ECG ====================
    
    def _procesar_ecg(self, archivo_path: str) -> Dict[str, Any]:
        """
        Procesa archivos .ecg (formato binario de ECG)
        """
        try:
            # Leer archivo binario
            with open(archivo_path, 'rb') as f:
                datos = f.read()
            
            # Intentar detectar formato
            # Muchos archivos .ecg son XML o texto
            try:
                texto = datos.decode('utf-8', errors='ignore')
                if '<' in texto and '>' in texto:  # Parece XML
                    return self._procesar_ecg_xml(texto)
                else:
                    return self._procesar_ecg_texto(texto)
            except:
                # Si no es texto, intentar como binario
                return self._procesar_ecg_binario(datos)
        
        except Exception as e:
            return {
                'tipo_estudio': 'ekg',
                'datos': {},
                'anomalias': [],
                'error': f'Error procesando archivo ECG: {str(e)}'
            }
    
    def _procesar_ecg_xml(self, xml_texto: str) -> Dict[str, Any]:
        """Procesa archivos ECG en formato XML"""
        datos = {}
        anomalias = []
        
        # Extraer datos comunes de XML ECG
        # Frecuencia cardíaca
        match = re.search(r'<VentricularRate.*?>(\d+)</VentricularRate>', xml_texto)
        if match:
            fc = int(match.group(1))
            datos['frecuencia_cardiaca'] = fc
            anomalias.extend(self._analizar_fc(fc))
        
        # Intervalos
        match = re.search(r'<PRInterval.*?>(\d+)</PRInterval>', xml_texto)
        if match:
            pr = int(match.group(1))
            datos['intervalo_pr'] = pr
            anomalias.extend(self._analizar_pr(pr))
        
        match = re.search(r'<QRSDuration.*?>(\d+)</QRSDuration>', xml_texto)
        if match:
            qrs = int(match.group(1))
            datos['duracion_qrs'] = qrs
            anomalias.extend(self._analizar_qrs(qrs))
        
        match = re.search(r'<QTInterval.*?>(\d+)</QTInterval>', xml_texto)
        if match:
            datos['intervalo_qt'] = int(match.group(1))
        
        match = re.search(r'<QTCorrected.*?>(\d+)</QTCorrected>', xml_texto)
        if match:
            qtc = int(match.group(1))
            datos['intervalo_qtc'] = qtc
            anomalias.extend(self._analizar_qtc(qtc))
        
        # Buscar diagnóstico en el XML
        match = re.search(r'<Diagnosis.*?>(.*?)</Diagnosis>', xml_texto, re.DOTALL)
        if match:
            diagnostico = match.group(1)
            anomalias.extend(self._detectar_anomalias_texto(diagnostico, 'ekg'))
        
        return {
            'tipo_estudio': 'ekg',
            'datos': datos,
            'anomalias': list(set(anomalias)),  # Eliminar duplicados
            'confianza': 0.9 if datos else 0.3
        }
    
    def _procesar_ecg_texto(self, texto: str) -> Dict[str, Any]:
        """Procesa archivos ECG en formato texto"""
        datos = {}
        anomalias = []
        
        # Buscar parámetros con regex
        # FC
        match = re.search(r'(?:HR|Heart\s+Rate|Ventricular\s+Rate)[:\s]*(\d+)', texto, re.IGNORECASE)
        if match:
            fc = int(match.group(1))
            datos['frecuencia_cardiaca'] = fc
            anomalias.extend(self._analizar_fc(fc))
        
        # PR
        match = re.search(r'PR[:\s]*(\d+)', texto, re.IGNORECASE)
        if match:
            pr = int(match.group(1))
            datos['intervalo_pr'] = pr
            anomalias.extend(self._analizar_pr(pr))
        
        # QRS
        match = re.search(r'QRS[:\s]*(\d+)', texto, re.IGNORECASE)
        if match:
            qrs = int(match.group(1))
            datos['duracion_qrs'] = qrs
            anomalias.extend(self._analizar_qrs(qrs))
        
        # QTc
        match = re.search(r'QTc[:\s]*(\d+)', texto, re.IGNORECASE)
        if match:
            qtc = int(match.group(1))
            datos['intervalo_qtc'] = qtc
            anomalias.extend(self._analizar_qtc(qtc))
        
        # Detectar anomalías en el texto
        anomalias.extend(self._detectar_anomalias_texto(texto, 'ekg'))
        
        return {
            'tipo_estudio': 'ekg',
            'datos': datos,
            'anomalias': list(set(anomalias)),
            'confianza': 0.85 if datos else 0.4
        }
    
    def _procesar_ecg_binario(self, datos_binarios: bytes) -> Dict[str, Any]:
        """Procesa archivos ECG en formato binario"""
        # Intentar extraer señales si es posible
        # Esto es muy dependiente del formato específico
        return {
            'tipo_estudio': 'ekg',
            'datos': {},
            'anomalias': [],
            'confianza': 0.2,
            'nota': 'Archivo binario ECG detectado. Se requiere formato específico para análisis completo.'
        }
    
    # ==================== ARCHIVOS MATLAB ====================
    
    def _procesar_mat(self, archivo_path: str) -> Dict[str, Any]:
        """
        Procesa archivos .mat (MATLAB)
        Comúnmente usados para datos de ECG/EEG
        """
        try:
            # Cargar archivo MATLAB
            mat_data = scipy.io.loadmat(archivo_path)
            
            datos = {}
            anomalias = []
            tipo_estudio = 'desconocido'
            
            # Buscar variables comunes
            # Para ECG
            if 'ecg' in mat_data or 'ECG' in mat_data:
                tipo_estudio = 'ekg'
                señal = mat_data.get('ecg') or mat_data.get('ECG')
                if señal is not None:
                    datos.update(self._analizar_señal_ecg(señal))
                    anomalias.extend(self._detectar_anomalias_señal_ecg(señal))
            
            # Para EEG
            elif 'eeg' in mat_data or 'EEG' in mat_data:
                tipo_estudio = 'eeg'
                señal = mat_data.get('eeg') or mat_data.get('EEG')
                if señal is not None:
                    datos.update(self._analizar_señal_eeg(señal))
            
            # Buscar frecuencia de muestreo
            if 'fs' in mat_data or 'Fs' in mat_data:
                datos['frecuencia_muestreo'] = float(mat_data.get('fs') or mat_data.get('Fs'))
            
            return {
                'tipo_estudio': tipo_estudio,
                'datos': datos,
                'anomalias': list(set(anomalias)),
                'confianza': 0.8 if datos else 0.3
            }
        
        except Exception as e:
            return {
                'tipo_estudio': 'desconocido',
                'datos': {},
                'anomalias': [],
                'error': f'Error procesando archivo MAT: {str(e)}'
            }
    
    def _analizar_señal_ecg(self, señal: np.ndarray) -> Dict[str, Any]:
        """Analiza señal de ECG y extrae parámetros"""
        datos = {}
        
        try:
            # Aplanar si es multidimensional
            if señal.ndim > 1:
                señal = señal.flatten()
            
            # Estimar frecuencia cardíaca (muy simplificado)
            # Esto requeriría algoritmos más complejos para ser preciso
            # Por ahora, solo guardamos info básica
            datos['muestras'] = len(señal)
            datos['amplitud_max'] = float(np.max(señal))
            datos['amplitud_min'] = float(np.min(señal))
            
        except Exception as e:
            print(f"Error analizando señal ECG: {e}")
        
        return datos
    
    def _detectar_anomalias_señal_ecg(self, señal: np.ndarray) -> List[str]:
        """Detecta anomalías en la señal de ECG"""
        anomalias = []
        
        try:
            if señal.ndim > 1:
                señal = señal.flatten()
            
            # Detectar valores extremos
            if np.max(np.abs(señal)) > 5:  # Umbral arbitrario
                anomalias.append('amplitud_anormal')
            
            # Detectar saturación
            if np.sum(señal == np.max(señal)) > len(señal) * 0.01:
                anomalias.append('señal_saturada')
        
        except Exception as e:
            print(f"Error detectando anomalías: {e}")
        
        return anomalias
    
    def _analizar_señal_eeg(self, señal: np.ndarray) -> Dict[str, Any]:
        """Analiza señal de EEG"""
        datos = {}
        
        try:
            if señal.ndim > 1:
                señal = señal.flatten()
            
            datos['muestras'] = len(señal)
            datos['canales'] = señal.shape[0] if señal.ndim > 1 else 1
        
        except Exception as e:
            print(f"Error analizando señal EEG: {e}")
        
        return datos
    
    # ==================== ARCHIVOS CSV ====================
    
    def _procesar_csv(self, archivo_path: str) -> Dict[str, Any]:
        """
        Procesa archivos CSV con datos médicos
        Formatos comunes:
        - Columnas: Parámetro, Valor, Unidad
        - Series temporales de señales
        - Resultados de laboratorio
        """
        try:
            datos = {}
            anomalias = []
            tipo_estudio = 'desconocido'
            
            with open(archivo_path, 'r', encoding='utf-8-sig') as f:
                # Detectar delimitador
                muestra = f.read(1024)
                f.seek(0)
                sniffer = csv.Sniffer()
                try:
                    delimiter = sniffer.sniff(muestra).delimiter
                except:
                    delimiter = ','
                
                reader = csv.reader(f, delimiter=delimiter)
                filas = list(reader)
            
            if not filas:
                return {
                    'tipo_estudio': 'desconocido',
                    'datos': {},
                    'anomalias': [],
                    'error': 'Archivo CSV vacío'
                }
            
            # Detectar formato del CSV
            # Verificar si la primera fila son números (sin encabezados)
            primera_fila_es_numerica = True
            try:
                for val in filas[0][:5]:  # Verificar primeros 5 valores
                    float(val.strip())
            except:
                primera_fila_es_numerica = False
            
            # Si la primera fila es numérica, es serie temporal sin encabezados
            if primera_fila_es_numerica:
                resultado = self._procesar_csv_serie_temporal_sin_encabezados(filas)
                datos = resultado['datos']
                tipo_estudio = resultado['tipo']
                anomalias = []
                
                # Agregar opción de conversión a imagen para análisis con IA
                if CSV_CONVERTER_DISPONIBLE:
                    datos['conversion_imagen_disponible'] = True
                    datos['sugerencia'] = 'Puedes convertir este CSV a imagen para análisis con IA'
            else:
                encabezados = [h.lower().strip() for h in filas[0]]
                
                # Formato 1: Parámetro, Valor, Unidad
                if any(term in ' '.join(encabezados) for term in ['parametro', 'parameter', 'valor', 'value']):
                    resultado = self._procesar_csv_parametros(filas, encabezados)
                    datos = resultado['datos']
                    tipo_estudio = resultado['tipo']
                    anomalias = resultado['anomalias']
                
                # Formato 2: Serie temporal (columnas: tiempo, derivación1, derivación2, ...)
                elif 'tiempo' in encabezados or 'time' in encabezados or encabezados[0] in ['', 'index', 'sample']:
                    resultado = self._procesar_csv_serie_temporal(filas, encabezados)
                    datos = resultado['datos']
                    tipo_estudio = resultado['tipo']
                    anomalias = []
                
                # Formato 3: Tabla simple con parámetros en filas
                else:
                    resultado = self._procesar_csv_tabla_simple(filas)
                    datos = resultado['datos']
                    tipo_estudio = resultado['tipo']
                    anomalias = resultado['anomalias']
            
            return {
                'tipo_estudio': tipo_estudio,
                'datos': datos,
                'anomalias': list(set(anomalias)),
                'confianza': 0.85 if datos else 0.3
            }
        
        except Exception as e:
            return {
                'tipo_estudio': 'desconocido',
                'datos': {},
                'anomalias': [],
                'error': f'Error procesando CSV: {str(e)}'
            }
    
    def _procesar_csv_parametros(self, filas: List[List[str]], encabezados: List[str]) -> Dict[str, Any]:
        """Procesa CSV con formato: Parámetro, Valor, Unidad"""
        datos = {}
        anomalias = []
        tipo_estudio = 'desconocido'
        
        # Encontrar índices de columnas
        idx_parametro = next((i for i, h in enumerate(encabezados) if 'parametro' in h or 'parameter' in h), 0)
        idx_valor = next((i for i, h in enumerate(encabezados) if 'valor' in h or 'value' in h), 1)
        
        # Procesar filas
        for fila in filas[1:]:  # Saltar encabezados
            if len(fila) <= idx_valor:
                continue
            
            parametro = fila[idx_parametro].lower().strip()
            valor_str = fila[idx_valor].strip()
            
            # Extraer valor numérico
            try:
                valor = float(re.sub(r'[^\d.-]', '', valor_str))
            except:
                continue
            
            # Mapear parámetros comunes de EKG
            if any(term in parametro for term in ['fc', 'frecuencia', 'heart rate', 'hr']):
                datos['frecuencia_cardiaca'] = int(valor)
                anomalias.extend(self._analizar_fc(int(valor)))
                tipo_estudio = 'ekg'
            
            elif 'pr' in parametro and 'intervalo' in parametro:
                datos['intervalo_pr'] = int(valor)
                anomalias.extend(self._analizar_pr(int(valor)))
                tipo_estudio = 'ekg'
            
            elif 'qrs' in parametro:
                datos['duracion_qrs'] = int(valor)
                anomalias.extend(self._analizar_qrs(int(valor)))
                tipo_estudio = 'ekg'
            
            elif 'qtc' in parametro or 'qt corregido' in parametro:
                datos['intervalo_qtc'] = int(valor)
                anomalias.extend(self._analizar_qtc(int(valor)))
                tipo_estudio = 'ekg'
            
            elif 'qt' in parametro and 'qtc' not in parametro:
                datos['intervalo_qt'] = int(valor)
                tipo_estudio = 'ekg'
            
            elif 'eje' in parametro or 'axis' in parametro:
                datos['eje_qrs'] = int(valor)
                tipo_estudio = 'ekg'
        
        return {
            'datos': datos,
            'tipo': tipo_estudio,
            'anomalias': anomalias
        }
    
    def _procesar_csv_serie_temporal(self, filas: List[List[str]], encabezados: List[str]) -> Dict[str, Any]:
        """Procesa CSV con series temporales (señales ECG/EEG) con encabezados"""
        datos = {}
        tipo_estudio = 'desconocido'
        
        try:
            # Determinar tipo por nombres de columnas
            columnas_texto = ' '.join(encabezados).lower()
            
            if any(term in columnas_texto for term in ['ecg', 'derivacion', 'lead', 'v1', 'v2', 'avr']):
                tipo_estudio = 'ekg'
            elif any(term in columnas_texto for term in ['eeg', 'canal', 'channel', 'fp1', 'fp2']):
                tipo_estudio = 'eeg'
            
            # Contar muestras y canales
            datos['muestras'] = len(filas) - 1  # Menos encabezados
            datos['canales'] = len(encabezados) - 1  # Menos columna de tiempo
            
            # Intentar extraer frecuencia de muestreo
            if len(filas) > 2:
                try:
                    t1 = float(filas[1][0])
                    t2 = float(filas[2][0])
                    dt = t2 - t1
                    if dt > 0:
                        datos['frecuencia_muestreo'] = round(1.0 / dt, 2)
                except:
                    pass
        
        except Exception as e:
            print(f"Error procesando serie temporal: {e}")
        
        return {
            'datos': datos,
            'tipo': tipo_estudio,
            'anomalias': []
        }
    
    def _procesar_csv_serie_temporal_sin_encabezados(self, filas: List[List[str]]) -> Dict[str, Any]:
        """
        Procesa CSV con series temporales sin encabezados (solo datos numéricos)
        Formato: Cada fila es una muestra de tiempo, cada columna es una derivación/canal
        """
        datos = {}
        tipo_estudio = 'ekg'  # Asumir ECG por defecto
        
        try:
            # Contar muestras y canales
            num_muestras = len(filas)
            num_canales = len(filas[0]) if filas else 0
            
            datos['muestras'] = num_muestras
            datos['canales'] = num_canales
            datos['formato'] = 'serie_temporal_sin_encabezados'
            
            # Calcular estadísticas básicas de la señal
            if num_muestras > 0 and num_canales > 0:
                # Tomar primera derivación para análisis
                try:
                    primera_derivacion = [float(filas[i][0]) for i in range(min(1000, num_muestras))]
                    
                    # Calcular amplitud promedio y rango
                    amplitud_min = min(primera_derivacion)
                    amplitud_max = max(primera_derivacion)
                    amplitud_rango = amplitud_max - amplitud_min
                    
                    datos['amplitud_min'] = round(amplitud_min, 3)
                    datos['amplitud_max'] = round(amplitud_max, 3)
                    datos['amplitud_rango'] = round(amplitud_rango, 3)
                    
                    # Si el rango es típico de ECG (0.5-5 mV), confirmar tipo
                    if 0.5 <= amplitud_rango <= 10:
                        tipo_estudio = 'ekg'
                        datos['unidad'] = 'mV'
                    elif amplitud_rango > 10:
                        # Podría ser EEG (amplitudes mayores en µV)
                        tipo_estudio = 'eeg'
                        datos['unidad'] = 'µV'
                    
                    # Estimar frecuencia de muestreo si hay suficientes muestras
                    # Asumir frecuencia estándar de ECG: 500 Hz
                    if num_muestras >= 500:
                        datos['frecuencia_muestreo_estimada'] = 500  # Hz típico para ECG
                        duracion_segundos = num_muestras / 500
                        datos['duracion_segundos'] = round(duracion_segundos, 2)
                        
                        # Estimar FC si es ECG
                        if tipo_estudio == 'ekg' and duracion_segundos >= 2:
                            # Contar picos (simplificado)
                            # En un ECG real, buscaríamos complejos QRS
                            # Aquí solo damos info básica
                            datos['info'] = f'Señal ECG de {duracion_segundos:.1f}s con {num_canales} derivaciones'
                
                except Exception as e:
                    print(f"Error calculando estadísticas: {e}")
            
            # Información adicional
            datos['descripcion'] = f'Serie temporal de {num_muestras} muestras × {num_canales} canales'
            
        except Exception as e:
            print(f"Error procesando serie temporal sin encabezados: {e}")
        
        return {
            'datos': datos,
            'tipo': tipo_estudio,
            'anomalias': []
        }
    
    def _procesar_csv_tabla_simple(self, filas: List[List[str]]) -> Dict[str, Any]:
        """Procesa CSV con tabla simple (parámetros en filas, valores en columnas)"""
        datos = {}
        anomalias = []
        tipo_estudio = 'desconocido'
        
        for fila in filas:
            if len(fila) < 2:
                continue
            
            parametro = fila[0].lower().strip()
            valor_str = fila[1].strip()
            
            # Buscar patrones de EKG
            if 'fc' in parametro or 'heart rate' in parametro:
                try:
                    fc = int(re.sub(r'[^\d]', '', valor_str))
                    datos['frecuencia_cardiaca'] = fc
                    anomalias.extend(self._analizar_fc(fc))
                    tipo_estudio = 'ekg'
                except:
                    pass
            
            elif 'pr' in parametro:
                try:
                    pr = int(re.sub(r'[^\d]', '', valor_str))
                    datos['intervalo_pr'] = pr
                    anomalias.extend(self._analizar_pr(pr))
                    tipo_estudio = 'ekg'
                except:
                    pass
        
        return {
            'datos': datos,
            'tipo': tipo_estudio,
            'anomalias': anomalias
        }
    
    # ==================== PDF E IMÁGENES ====================
    
    def _procesar_pdf(self, archivo_path: str) -> Dict[str, Any]:
        """Procesa PDF con OCR mejorado"""
        texto = ""
        
        try:
            # Intentar extraer texto directo
            with open(archivo_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    texto += page.extract_text() + "\n"
            
            # Si no hay texto, usar OCR
            if len(texto.strip()) < 50:
                imagenes = convert_from_path(archivo_path, dpi=300)
                for imagen in imagenes:
                    texto += pytesseract.image_to_string(imagen, lang='spa+eng') + "\n"
        
        except Exception as e:
            print(f"Error procesando PDF: {e}")
        
        return self._analizar_texto_medico(texto)
    
    def _procesar_imagen(self, archivo_path: str) -> Dict[str, Any]:
        """Procesa imagen con OCR mejorado, análisis visual básico y opcionalmente IA"""
        try:
            imagen = Image.open(archivo_path)
            
            # Preprocesar imagen para mejor OCR
            imagen_procesada = self._preprocesar_imagen_ecg(imagen)
            
            # OCR con español e inglés
            texto = pytesseract.image_to_string(imagen_procesada, lang='spa+eng')
            
            # Analizar texto extraído
            resultado = self._analizar_texto_medico(texto)
            
            # Si es ECG y no se extrajeron datos suficientes
            if resultado['tipo_estudio'] == 'ekg' and len(resultado['datos']) < 3:
                # Intentar análisis visual básico primero
                datos_visuales = self._analisis_visual_basico_ecg(imagen, texto)
                resultado['datos'].update(datos_visuales)
                
                # Si aún no hay datos suficientes, intentar IA (si está configurada)
                if len(resultado['datos']) < 3 and os.getenv('OPENAI_API_KEY'):
                    try:
                        resultado_ia = self._analizar_con_ia(archivo_path)
                        if resultado_ia and resultado_ia.get('datos'):
                            resultado['datos'].update(resultado_ia['datos'])
                            resultado['anomalias'].extend(resultado_ia.get('anomalias', []))
                            resultado['interpretacion_ia'] = resultado_ia.get('interpretacion', '')
                            resultado['confianza'] = resultado_ia.get('confianza', 0.7)
                            resultado['metodo'] = 'ia_vision'
                    except Exception as e:
                        print(f"Error en análisis con IA: {e}")
                        resultado['confianza'] = 0.4
                        resultado['requiere_revision'] = True
                else:
                    resultado['confianza'] = 0.4
                    resultado['requiere_revision'] = True
            
            return resultado
        except Exception as e:
            return {
                'tipo_estudio': 'desconocido',
                'datos': {},
                'anomalias': [],
                'error': f'Error procesando imagen: {str(e)}'
            }
    
    def _analizar_con_ia(self, imagen_path: str) -> Optional[Dict[str, Any]]:
        """Analiza imagen con IA si está disponible"""
        try:
            import os
            from app.services.analizador_ecg_ia import AnalizadorECGIA
            
            # Obtener API key del entorno
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                print("⚠️ API Key de OpenAI no configurada")
                return None
            
            print(f"✅ API Key encontrada (longitud: {len(api_key)})")
            print(f"📁 Analizando imagen: {imagen_path}")
            
            # Crear analizador pasando explícitamente la API key
            print("🔧 Inicializando AnalizadorECGIA...")
            analizador = AnalizadorECGIA(api_key=api_key)
            print("✅ AnalizadorECGIA inicializado correctamente")
            
            print("🤖 Llamando a OpenAI Vision API...")
            resultado = analizador.analizar_ecg(imagen_path)
            print(f"✅ Análisis completado: {len(resultado.get('datos', {}))} parámetros extraídos")
            
            return resultado
        except ImportError as e:
            print(f"⚠️ Analizador de IA no disponible: {e}")
            return None
        except Exception as e:
            print(f"❌ Error en análisis con IA: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _preprocesar_imagen_ecg(self, imagen: Image.Image) -> Image.Image:
        """Preprocesa imagen de ECG para mejorar OCR"""
        try:
            # Convertir a escala de grises
            if imagen.mode != 'L':
                imagen = imagen.convert('L')
            
            # Aumentar contraste (ayuda a leer texto pequeño)
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(imagen)
            imagen = enhancer.enhance(2.0)
            
            return imagen
        except:
            return imagen
    
    def _analisis_visual_basico_ecg(self, imagen: Image.Image, texto: str) -> Dict[str, Any]:
        """
        Análisis visual básico de ECG cuando OCR no extrae datos numéricos.
        Busca patrones visuales y texto en áreas específicas.
        """
        datos = {}
        
        try:
            # Buscar en el texto cualquier número que pueda ser FC
            # Formato común: "AC50 25mm/s 10mm/mV 47.2-5e-ly W2"
            # Buscar patrones como "XX-XXHz" o "XXbpm"
            
            # Patrón para frecuencia en el formato "0.67-25Hz"
            match_freq = re.search(r'(\d+\.?\d*)-(\d+)Hz', texto)
            if match_freq:
                # Convertir Hz a bpm si es necesario
                freq_hz = float(match_freq.group(1))
                if freq_hz < 5:  # Probablemente en Hz
                    fc = int(freq_hz * 60)
                    datos['frecuencia_cardiaca'] = fc
            
            # Buscar "XXbpm" o "XX lpm"
            match_bpm = re.search(r'(\d{2,3})\s*(?:bpm|lpm)', texto, re.IGNORECASE)
            if match_bpm:
                datos['frecuencia_cardiaca'] = int(match_bpm.group(1))
            
            # Buscar velocidad de papel (25mm/s es estándar)
            match_velocidad = re.search(r'(\d+)mm/s', texto)
            if match_velocidad:
                datos['velocidad_papel'] = int(match_velocidad.group(1))
            
            # Buscar calibración (10mm/mV es estándar)
            match_calibracion = re.search(r'(\d+)mm/mV', texto)
            if match_calibracion:
                datos['calibracion'] = int(match_calibracion.group(1))
            
            # Si no se encontró FC, intentar estimarla visualmente
            # (esto requeriría análisis de imagen más avanzado)
            if 'frecuencia_cardiaca' not in datos:
                # Buscar cualquier número de 2-3 dígitos que pueda ser FC
                numeros = re.findall(r'\b([4-9]\d|1[0-9]{2})\b', texto)
                if numeros:
                    # Tomar el primero que esté en rango razonable (40-200)
                    for num in numeros:
                        fc = int(num)
                        if 40 <= fc <= 200:
                            datos['frecuencia_cardiaca'] = fc
                            datos['fc_estimada'] = True
                            break
        
        except Exception as e:
            print(f"Error en análisis visual: {e}")
        
        return datos
    
    def _analizar_texto_medico(self, texto: str) -> Dict[str, Any]:
        """Analiza texto médico extraído"""
        # Detectar tipo
        tipo = self._detectar_tipo_estudio(texto)
        
        # Extraer datos según tipo
        if tipo == 'ekg':
            datos = self._extraer_datos_ekg_texto(texto)
        elif tipo == 'eeg':
            datos = self._extraer_datos_eeg_texto(texto)
        elif tipo == 'ecografia':
            datos = self._extraer_datos_eco_texto(texto)
        else:
            datos = {}
        
        # Detectar anomalías
        anomalias = self._detectar_anomalias_texto(texto, tipo)
        
        return {
            'tipo_estudio': tipo,
            'datos': datos,
            'anomalias': list(set(anomalias)),
            'confianza': self._calcular_confianza(datos, anomalias),
            'texto_muestra': texto[:500]
        }
    
    # ==================== ANÁLISIS DE ANOMALÍAS ====================
    
    def _analizar_fc(self, fc: int) -> List[str]:
        """Analiza frecuencia cardíaca"""
        anomalias = []
        if fc < 60:
            if fc < 40:
                anomalias.append('bradicardia_severa')
            else:
                anomalias.append('bradicardia')
        elif fc > 100:
            if fc > 150:
                anomalias.append('taquicardia_severa')
            else:
                anomalias.append('taquicardia')
        return anomalias
    
    def _analizar_pr(self, pr: int) -> List[str]:
        """Analiza intervalo PR"""
        anomalias = []
        if pr > 200:
            anomalias.append('bloqueo_av_primer_grado')
        elif pr < 120:
            anomalias.append('pr_corto')
        return anomalias
    
    def _analizar_qrs(self, qrs: int) -> List[str]:
        """Analiza duración QRS"""
        anomalias = []
        if qrs > 120:
            anomalias.append('qrs_ensanchado')
            anomalias.append('bloqueo_rama')  # QRS >120ms sugiere bloqueo de rama
        elif qrs > 100:
            anomalias.append('qrs_limite_superior')
        return anomalias
    
    def _analizar_eje(self, eje: int) -> List[str]:
        """Analiza eje QRS"""
        anomalias = []
        if eje > 90:
            anomalias.append('desviacion_eje')
            anomalias.append('eje_derecho')
        elif eje < -30:
            anomalias.append('desviacion_eje')
            if eje < -90:
                anomalias.append('eje_extremo')
            else:
                anomalias.append('eje_izquierdo')
        return anomalias
    
    def _analizar_qtc(self, qtc: int) -> List[str]:
        """Analiza QTc"""
        anomalias = []
        if qtc > 440:
            if qtc > 500:
                anomalias.append('qt_prolongado_severo')
            else:
                anomalias.append('qt_prolongado')
        return anomalias
    
    def _detectar_anomalias_texto(self, texto: str, tipo: str) -> List[str]:
        """Detecta anomalías mencionadas en el texto"""
        anomalias = []
        texto_lower = texto.lower()
        
        if tipo == 'ekg':
            for anomalia, patrones in self.PATRONES_ANOMALIAS_EKG.items():
                for patron in patrones:
                    if re.search(patron, texto_lower):
                        anomalias.append(anomalia)
                        break
        
        elif tipo == 'eeg':
            for anomalia, patrones in self.PATRONES_ANOMALIAS_EEG.items():
                for patron in patrones:
                    if re.search(patron, texto_lower):
                        anomalias.append(anomalia)
                        break
        
        return anomalias
    
    # ==================== CONVERSIÓN CSV A IMAGEN ====================
    
    def convertir_csv_a_imagen_y_analizar(
        self,
        csv_path: str,
        num_derivaciones: int = 12,
        usar_ia: bool = True
    ) -> Dict[str, Any]:
        """
        Convierte un archivo CSV de señales a imagen y opcionalmente lo analiza con IA
        
        Args:
            csv_path: Ruta al archivo CSV
            num_derivaciones: Número de derivaciones a graficar (default: 12)
            usar_ia: Si True, analiza la imagen generada con IA
        
        Returns:
            Diccionario con resultado de la conversión y análisis
        """
        if not self.csv_converter:
            return {
                'error': 'Conversor CSV no disponible. Instalar matplotlib: pip install matplotlib',
                'tipo_estudio': 'desconocido',
                'datos': {},
                'anomalias': []
            }
        
        try:
            # Convertir CSV a imagen
            imagen_bytes, error = self.csv_converter.convertir_csv_a_imagen(
                csv_path=csv_path,
                num_derivaciones=num_derivaciones
            )
            
            if error:
                return {
                    'error': error,
                    'tipo_estudio': 'desconocido',
                    'datos': {},
                    'anomalias': []
                }
            
            # Guardar imagen temporalmente
            temp_image = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            temp_image.write(imagen_bytes)
            temp_image.close()
            
            resultado = {
                'tipo_estudio': 'ekg',
                'datos': {
                    'conversion_exitosa': True,
                    'imagen_generada': True,
                    'num_derivaciones': num_derivaciones
                },
                'anomalias': [],
                'imagen_path': temp_image.name
            }
            
            # Si se solicita análisis con IA
            if usar_ia:
                try:
                    resultado_ia = self._analizar_con_ia(temp_image.name)
                    if resultado_ia:
                        resultado['datos'].update(resultado_ia.get('datos', {}))
                        resultado['anomalias'] = resultado_ia.get('anomalias', [])
                        resultado['interpretacion_ia'] = resultado_ia.get('interpretacion', '')
                        resultado['confianza'] = resultado_ia.get('confianza', 0.7)
                        resultado['metodo'] = 'csv_convertido_a_imagen_con_ia'
                except Exception as e:
                    resultado['advertencia_ia'] = f'No se pudo analizar con IA: {str(e)}'
                    resultado['metodo'] = 'csv_convertido_a_imagen_sin_ia'
            else:
                resultado['metodo'] = 'csv_convertido_a_imagen_sin_ia'
            
            return resultado
        
        except Exception as e:
            return {
                'error': f'Error convirtiendo CSV a imagen: {str(e)}',
                'tipo_estudio': 'desconocido',
                'datos': {},
                'anomalias': []
            }
    
    # ==================== MÉTODOS AUXILIARES ====================
    
    def _detectar_tipo_estudio(self, texto: str) -> str:
        """Detecta el tipo de estudio"""
        texto_lower = texto.lower()
        
        puntuaciones = {'ekg': 0, 'eeg': 0, 'ecografia': 0}
        
        palabras_clave = {
            'ekg': ['electrocardiograma', 'ekg', 'ecg', 'cardiaco', 'corazón'],
            'eeg': ['electroencefalograma', 'eeg', 'cerebral', 'epilepsia'],
            'ecografia': ['ecografía', 'ultrasonido', 'doppler']
        }
        
        for tipo, palabras in palabras_clave.items():
            for palabra in palabras:
                if palabra in texto_lower:
                    puntuaciones[tipo] += 1
        
        tipo_detectado = max(puntuaciones, key=puntuaciones.get)
        return tipo_detectado if puntuaciones[tipo_detectado] > 0 else 'desconocido'
    
    def _extraer_datos_ekg_texto(self, texto: str) -> Dict[str, Any]:
        """Extrae datos de EKG del texto"""
        datos = {}
        
        # FC
        match = re.search(r'(?:FC|Heart\s+Rate)[:\s]*(\d+)', texto, re.IGNORECASE)
        if match:
            datos['frecuencia_cardiaca'] = int(match.group(1))
        
        # PR
        match = re.search(r'PR[:\s]*(\d+)', texto, re.IGNORECASE)
        if match:
            datos['intervalo_pr'] = int(match.group(1))
        
        # QRS
        match = re.search(r'QRS[:\s]*(\d+)', texto, re.IGNORECASE)
        if match:
            datos['duracion_qrs'] = int(match.group(1))
        
        # QTc
        match = re.search(r'QTc[:\s]*(\d+)', texto, re.IGNORECASE)
        if match:
            datos['intervalo_qtc'] = int(match.group(1))
        
        return datos
    
    def _extraer_datos_eeg_texto(self, texto: str) -> Dict[str, Any]:
        """Extrae datos de EEG del texto"""
        datos = {}
        
        match = re.search(r'(?:Duración|Duration)[:\s]*(\d+)', texto, re.IGNORECASE)
        if match:
            datos['duracion_minutos'] = int(match.group(1))
        
        return datos
    
    def _extraer_datos_eco_texto(self, texto: str) -> Dict[str, Any]:
        """Extrae datos de ecografía del texto"""
        datos = {}
        
        match = re.search(r'(?:Profundidad|Depth)[:\s]*(\d+\.?\d*)', texto, re.IGNORECASE)
        if match:
            datos['profundidad_cm'] = float(match.group(1))
        
        return datos
    
    def _calcular_confianza(self, datos: Dict, anomalias: List) -> float:
        """Calcula confianza del análisis"""
        score = 0.5
        
        if datos:
            score += 0.2 * min(len(datos), 5) / 5
        
        if anomalias:
            score += 0.2
        
        return min(score, 0.95)
