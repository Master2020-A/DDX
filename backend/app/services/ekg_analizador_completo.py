"""
Servicio integrador de análisis completo de EKG
Orquesta todos los módulos de análisis
"""

from typing import Dict, Any, Optional
import numpy as np
from .ekg_digitalizador import EKGDigitalizador
from .ekg_procesador import EKGProcesador
from .ekg_detector_ondas import EKGDetectorOndas
from .ekg_diagnostico_avanzado import EKGDiagnosticoAvanzado, GeneradorReporteEKG


class EKGAnalizadorCompleto:
    """Servicio principal que integra todo el pipeline de análisis"""
    
    def __init__(self, sampling_rate: int = 500):
        self.sampling_rate = sampling_rate
        self.digitalizador = EKGDigitalizador(sampling_rate)
        self.procesador = EKGProcesador(sampling_rate)
        self.detector = EKGDetectorOndas(sampling_rate)
        self.diagnostico = EKGDiagnosticoAvanzado()
    
    def analizar_desde_imagen(self, image_bytes: bytes, paciente_info: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Análisis completo desde imagen de EKG
        
        Args:
            image_bytes: Bytes de la imagen
            paciente_info: Info del paciente (opcional)
            
        Returns:
            Dict con análisis completo
        """
        # 1. Digitalizar imagen
        digitalizacion = self.digitalizador.digitalizar(image_bytes)
        
        if not digitalizacion['success']:
            return {
                'success': False,
                'error': 'No se pudo digitalizar la imagen correctamente'
            }
        
        # 2. Procesar señal principal (Lead II)
        signal = digitalizacion['signals']['II']
        processed_signal = self.procesador.procesar_completo(signal)
        
        # 3. Detectar ondas y calcular mediciones
        analisis_ondas = self.detector.analisis_completo(processed_signal)
        
        # 4. Diagnóstico avanzado
        diagnostico = self.diagnostico.analizar(
            analisis_ondas['intervals'],
            analisis_ondas['waves'],
            digitalizacion['signals']
        )
        
        # 5. Generar reporte si hay info del paciente
        reporte_texto = None
        if paciente_info:
            reporte_texto = GeneradorReporteEKG.generar_reporte_texto(
                diagnostico,
                paciente_info
            )
        
        return {
            'success': True,
            'mediciones': analisis_ondas['intervals'],
            'ondas': analisis_ondas['waves'],
            'diagnostico': diagnostico,
            'interpretacion_detallada': diagnostico['detailed_interpretation'],
            'senal_procesada': processed_signal.tolist()[:1000],  # Primeros 1000 puntos
            'roi': digitalizacion['roi'],
            'reporte_texto': reporte_texto,
            'calidad_senal': self.procesador.calcular_calidad_senal(processed_signal)
        }
    
    def extraer_parametros_automaticos(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Extrae parámetros automáticamente para pre-llenar formulario
        
        Args:
            image_bytes: Bytes de la imagen
            
        Returns:
            Dict con parámetros extraídos
        """
        resultado = self.analizar_desde_imagen(image_bytes)
        
        if not resultado['success']:
            return {'success': False, 'error': resultado.get('error')}
        
        mediciones = resultado['mediciones']
        diagnostico = resultado['diagnostico']
        
        # Formatear para el formulario
        parametros = {
            'frecuencia_cardiaca': int(mediciones.get('heart_rate', 0)),
            'ritmo': diagnostico.get('rhythm', 'sinusal'),
            'intervalo_pr': int(mediciones.get('PR_interval', 0)),
            'duracion_qrs': int(mediciones.get('QRS_duration', 0)),
            'intervalo_qt': int(mediciones.get('QT_interval', 0)),
            'qtc': int(mediciones.get('QTc', 0)),
            'eje_qrs': int(mediciones.get('QRS_Axis', 0)),
            'onda_p': self._clasificar_onda_p(resultado['ondas'].get('P_peaks', []), mediciones),
            'complejo_qrs': self._clasificar_qrs(mediciones.get('QRS_duration', 0)),
            'onda_t': self._clasificar_onda_t(mediciones.get('T_amplitude', 0)),
            'segmento_st': self._clasificar_st(mediciones.get('ST_level', 0)),
            'ritmo_regular': True,  # Por defecto
            'hallazgos': [d['condition'] for d in diagnostico.get('diagnoses', [])],
            'interpretacion_ia': diagnostico.get('detailed_interpretation', {})
        }
        
        return {
            'success': True,
            'parametros': parametros
        }
    
    def _clasificar_onda_p(self, p_peaks: list, mediciones: Dict) -> str:
        """Clasifica la onda P - valores en minúsculas para el formulario"""
        if len(p_peaks) == 0:
            return 'ausente'
        
        pr_interval = mediciones.get('PR_interval', 0)
        if pr_interval < 120:
            return 'anormal'
        elif pr_interval > 200:
            return 'anormal'
        else:
            return 'normal'
    
    def _clasificar_qrs(self, qrs_duration: float) -> str:
        """Clasifica el complejo QRS - valores en minúsculas para el formulario"""
        if qrs_duration == 0:
            return 'normal'
        elif qrs_duration < 80:
            return 'normal'
        elif qrs_duration <= 120:
            return 'normal'
        else:
            return 'ensanchado'
    
    def _clasificar_onda_t(self, t_amplitude: float) -> str:
        """Clasifica la onda T - valores en minúsculas para el formulario"""
        if t_amplitude == 0:
            return 'normal'
        elif t_amplitude < 0:
            return 'invertida'
        elif t_amplitude < 0.1:
            return 'aplanada'
        else:
            return 'normal'
    
    def _clasificar_st(self, st_level: float) -> str:
        """Clasifica el nivel del segmento ST - valores en minúsculas para el formulario"""
        if st_level > 0.1:
            return 'elevado'
        elif st_level < -0.1:
            return 'deprimido'
        else:
            return 'normal'
