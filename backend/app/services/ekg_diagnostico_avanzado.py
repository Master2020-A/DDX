"""
Servicio de diagnóstico avanzado de EKG
Genera interpretación médica narrativa detallada
"""

import numpy as np
import math
from typing import Dict, List, Any, Optional


class EKGDiagnosticoAvanzado:
    """Motor de diagnóstico avanzado con interpretación narrativa"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reinicia el estado del diagnóstico"""
        self.diagnoses = []
        self.findings = []
        self.risk_score = 0
        self.affected_territories = []
        self.rhythm_diagnosis = "Ritmo Sinusal"
    
    def analizar(self, intervals: Dict, waves: Dict, signals: Dict) -> Dict[str, Any]:
        """
        Realiza análisis diagnóstico completo
        
        Args:
            intervals: Mediciones de intervalos
            waves: Ondas detectadas
            signals: Señales de todas las derivaciones
            
        Returns:
            Dict con diagnóstico completo e interpretación
        """
        self.reset()
        
        if not intervals:
            return {
                'diagnoses': [],
                'summary': 'Error en análisis',
                'risk_score': 0
            }
        
        # 1. Calcular Eje
        axis = self._calcular_eje(signals, waves)
        intervals['QRS_Axis'] = axis
        
        # 2. Análisis Clínico Base
        self._analizar_ritmo_avanzado(intervals, waves)
        self._analizar_bloqueos_conduccion(intervals, signals)
        self._analizar_isquemia_territorios(intervals, signals)
        self._analizar_hipertrofia(intervals, signals)
        
        # 3. Generación de Interpretación Detallada
        interpretation = self._generar_interpretacion_detallada(intervals, waves)
        
        # 4. Pronóstico
        prognosis = self._calcular_pronostico()
        
        return {
            'diagnoses': self.diagnoses,
            'findings': self.findings,
            'rhythm': self.rhythm_diagnosis,
            'rhythm_type': 'Regular' if intervals.get('RR_std', 0) < 20 else 'Irregular',
            'territories': self.affected_territories,
            'risk_score': self.risk_score,
            'prognosis_text': prognosis,
            'measurements': intervals,
            'detailed_interpretation': interpretation
        }
    
    def _calcular_eje(self, signals: Dict, waves: Dict) -> int:
        """Calcula el eje QRS"""
        try:
            lead_I = signals.get('I', signals.get('II'))
            lead_aVF = signals.get('aVF', signals.get('II'))
            r_peaks = waves.get('R_peaks', [])
            
            if len(r_peaks) == 0:
                return 45
            
            amp_I = np.mean(lead_I[r_peaks])
            amp_aVF = np.mean(lead_aVF[r_peaks])
            angle = math.degrees(math.atan2(amp_aVF, amp_I))
            return int(angle)
        except:
            return 45
    
    def _generar_interpretacion_detallada(self, m: Dict, waves: Dict) -> Dict[str, str]:
        """
        Genera interpretación médica narrativa por componentes
        
        Args:
            m: Mediciones (measurements)
            waves: Ondas detectadas
            
        Returns:
            Dict con textos de interpretación por componente
        """
        text = {}
        
        # --- A. ANÁLISIS AURICULAR (ONDA P) ---
        p_amp = m.get('P_amplitude', 0)
        p_dur = 100  # Asumimos duración P simulada si no se midió
        
        if len(waves.get('P_peaks', [])) == 0:
            text['P'] = "Ausencia de actividad auricular organizada identificable (Ondas P no visibles). Sugiere ritmo no sinusal."
        elif p_amp > 0.25:
            text['P'] = f"Onda P acuminada (Voltaje: {p_amp:.2f}mV). Sugiere crecimiento auricular derecho (P Pulmonale)."
        elif p_dur > 120:
            text['P'] = "Onda P ensanchada (>120ms) y mellada. Sugiere crecimiento auricular izquierdo (P Mitrale)."
        else:
            text['P'] = "Onda P de morfología, voltaje y duración dentro de límites normales. Eje de P conservado, indicativo de activación auricular sinusal."
        
        # --- B. CONDUCCIÓN AV (INTERVALO PR) ---
        pr = m.get('PR_interval', 0)
        if pr == 0:
            text['PR'] = "No valorable."
        elif pr < 120:
            text['PR'] = f"Intervalo PR corto ({pr:.0f} ms). Posible conducción acelerada o síndrome de preexcitación (WPW)."
        elif pr > 200:
            text['PR'] = f"Intervalo PR prolongado ({pr:.0f} ms). Bloqueo Auriculoventricular de Primer Grado."
        else:
            text['PR'] = f"Conducción auriculoventricular conservada (PR: {pr:.0f} ms), sin retrasos patológicos."
        
        # --- C. DESPOLARIZACIÓN VENTRICULAR (QRS) ---
        qrs = m.get('QRS_duration', 0)
        axis = m.get('QRS_Axis', 0)
        
        axis_txt = "Eje normal"
        if axis < -30:
            axis_txt = f"Desviación del eje a la izquierda ({axis}°)"
        elif axis > 90:
            axis_txt = f"Desviación del eje a la derecha ({axis}°)"
        
        if qrs > 120:
            text['QRS'] = f"Complejo QRS ensanchado ({qrs:.0f} ms). {axis_txt}. Sugiere trastorno de la conducción intraventricular (Bloqueo de Rama)."
        else:
            text['QRS'] = f"Complejo QRS estrecho ({qrs:.0f} ms). {axis_txt}. Activación ventricular sincrónica sin trastornos de conducción mayores."
        
        # --- D. REPOLARIZACIÓN (ST-T) ---
        st = m.get('ST_level', 0)
        t_amp = m.get('T_amplitude', 0)
        
        st_txt = ""
        if st > 0.1:
            st_txt = f"Supradesnivel del segmento ST ({st:.2f} mV). Signo de lesión subepicárdica aguda."
        elif st < -0.1:
            st_txt = f"Infradesnivel del segmento ST ({st:.2f} mV). Signo de isquemia subendocárdica o sobrecarga."
        else:
            st_txt = "Segmento ST isoeléctrico respecto a la línea de base."
        
        t_txt = ""
        if t_amp < 0:
            t_txt = "Onda T invertida. Sugiere isquemia miocárdica o sobrecarga ventricular."
        elif t_amp > 1.0:
            t_txt = "Onda T picuda y simétrica. Posible hiperpotasemia o variante de repolarización precoz."
        else:
            t_txt = "Onda T positiva asimétrica."
        
        text['ST_T'] = f"{st_txt} {t_txt} Sin alteraciones secundarias de la repolarización."
        
        # --- E. INTERVALO QT ---
        qtc = m.get('QTc', 0)
        if qtc > 450:
            text['QT'] = f"Intervalo QTc prolongado ({qtc:.0f} ms). Riesgo aumentado de arritmias ventriculares (Torsade de Pointes)."
        else:
            text['QT'] = f"Intervalo QTc dentro de rangos fisiológicos ({qtc:.0f} ms)."
        
        return text
    
    def _analizar_ritmo_avanzado(self, intervals: Dict, waves: Dict):
        """Analiza el ritmo cardíaco"""
        hr = intervals.get('heart_rate', 0)
        p_waves_present = len(waves.get('P_peaks', [])) > 0
        rr_std = intervals.get('RR_std', 0)
        
        if rr_std > 20 and not p_waves_present:
            self.rhythm_diagnosis = "Fibrilación Auricular"
            self.risk_score += 15
            self.findings.append("Ritmo irregular sin ondas P visibles")
        elif hr > 100:
            self.rhythm_diagnosis = "Taquicardia Sinusal"
            self.findings.append(f"Frecuencia cardíaca elevada: {hr:.0f} bpm")
        elif hr < 60:
            self.rhythm_diagnosis = "Bradicardia Sinusal"
            self.findings.append(f"Frecuencia cardíaca baja: {hr:.0f} bpm")
        else:
            self.rhythm_diagnosis = "Ritmo Sinusal"
    
    def _analizar_bloqueos_conduccion(self, intervals: Dict, signals: Dict):
        """Detecta bloqueos de conducción"""
        qrs_ms = intervals.get('QRS_duration', 0)
        pr_ms = intervals.get('PR_interval', 0)
        
        if qrs_ms > 120:
            self.diagnoses.append({
                'condition': 'Bloqueo de Rama',
                'severity': 'moderate',
                'confidence': 0.8,
                'description': f'QRS ensanchado: {qrs_ms:.0f}ms'
            })
            self.findings.append(f"QRS > 120ms ({qrs_ms:.0f}ms)")
        
        if pr_ms > 200:
            self.diagnoses.append({
                'condition': 'Bloqueo AV de Primer Grado',
                'severity': 'low',
                'confidence': 0.85,
                'description': f'PR prolongado: {pr_ms:.0f}ms'
            })
            self.findings.append(f"PR > 200ms ({pr_ms:.0f}ms)")
    
    def _analizar_isquemia_territorios(self, intervals: Dict, signals: Dict):
        """Detecta signos de isquemia/infarto"""
        st_level = intervals.get('ST_level', 0)
        
        if st_level > 0.15:
            self.diagnoses.append({
                'condition': 'Elevación ST (IAM)',
                'severity': 'high',
                'confidence': 0.85,
                'description': 'Infarto Agudo de Miocardio'
            })
            self.risk_score += 50
            self.affected_territories.append('Anterior')
            self.findings.append(f"Elevación ST: {st_level:.2f}mV")
        elif st_level < -0.1:
            self.diagnoses.append({
                'condition': 'Depresión ST',
                'severity': 'moderate',
                'confidence': 0.75,
                'description': 'Posible isquemia subendocárdica'
            })
            self.risk_score += 25
            self.findings.append(f"Depresión ST: {st_level:.2f}mV")
    
    def _analizar_hipertrofia(self, intervals: Dict, signals: Dict):
        """Detecta signos de hipertrofia ventricular"""
        r_amp = intervals.get('R_amplitude', 0)
        
        # Criterios simplificados de Sokolov-Lyon
        if r_amp > 3.5:
            self.diagnoses.append({
                'condition': 'Posible Hipertrofia Ventricular',
                'severity': 'moderate',
                'confidence': 0.65,
                'description': 'Voltajes aumentados en precordiales'
            })
            self.findings.append(f"Amplitud R elevada: {r_amp:.2f}mV")
    
    def _calcular_pronostico(self) -> str:
        """Calcula pronóstico basado en score de riesgo"""
        score = min(self.risk_score, 100)
        
        if score < 20:
            return "NORMAL / BAJO RIESGO"
        elif score < 50:
            return "RIESGO INTERMEDIO"
        else:
            return "ALTO RIESGO"


class GeneradorReporteEKG:
    """Genera reportes de texto formateados"""
    
    @staticmethod
    def generar_reporte_texto(diag: Dict, p_info: Dict) -> str:
        """
        Genera reporte de texto completo
        
        Args:
            diag: Diagnóstico completo
            p_info: Información del paciente
            
        Returns:
            String con reporte formateado
        """
        m = diag.get('measurements', {})
        interp = diag.get('detailed_interpretation', {})
        
        lines = []
        lines.append("INFORME ELECTROCARDIOGRÁFICO DETALLADO")
        lines.append("=" * 60)
        lines.append(f"PACIENTE: {p_info.get('name', '')} | EDAD: {p_info.get('age', 0)} años")
        lines.append(f"FECHA:    {p_info.get('date_time', '')}")
        lines.append(f"CLÍNICA:  {p_info.get('indication', '')}")
        lines.append("=" * 60)
        lines.append("")
        
        lines.append("1. ANÁLISIS CUANTITATIVO")
        lines.append("-" * 60)
        lines.append(f"FC: {m.get('heart_rate', 0):.0f} bpm | Eje: {m.get('QRS_Axis', 0)}° | PR: {m.get('PR_interval', 0):.0f} ms")
        lines.append(f"QRS: {m.get('QRS_duration', 0):.0f} ms | QT/QTc: {m.get('QT_interval', 0):.0f}/{m.get('QTc', 0):.0f} ms")
        lines.append("")
        
        lines.append("2. INTERPRETACIÓN SECUENCIAL")
        lines.append("-" * 60)
        lines.append(f"A. ONDA P (Auricular):")
        lines.append(f"   {interp.get('P', '-')}")
        lines.append("")
        lines.append(f"B. INTERVALO PR (Conducción AV):")
        lines.append(f"   {interp.get('PR', '-')}")
        lines.append("")
        lines.append(f"C. COMPLEJO QRS (Ventricular):")
        lines.append(f"   {interp.get('QRS', '-')}")
        lines.append("")
        lines.append(f"D. SEGMENTO ST Y ONDA T (Repolarización):")
        lines.append(f"   {interp.get('ST_T', '-')}")
        lines.append("")
        lines.append(f"E. INTERVALO QT:")
        lines.append(f"   {interp.get('QT', '-')}")
        lines.append("")
        
        lines.append("3. CONCLUSIÓN DIAGNÓSTICA")
        lines.append("-" * 60)
        lines.append(f"DIAGNÓSTICO DEL RITMO: {diag.get('rhythm', 'N/A')}")
        
        if diag.get('diagnoses'):
            for d in diag.get('diagnoses'):
                lines.append(f"HALLAZGO: {d['condition']} ({d['description']})")
        else:
            lines.append("HALLAZGO: Trazado sin alteraciones patológicas significativas.")
        
        lines.append("")
        lines.append(f"EVALUACIÓN DE RIESGO: {diag.get('prognosis_text')}")
        lines.append("=" * 60)
        lines.append("Análisis asistido por IA. Requiere validación médica.")
        
        return "\n".join(lines)
