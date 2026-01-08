"""
Servicio de interpretación automática de Electrocardiogramas (EKG)
"""
from typing import Dict, List, Optional, Tuple


class InterpretadorEKG:
    """Interpretador automático de parámetros de EKG"""
    
    def __init__(self):
        # Rangos normales de referencia
        self.rangos_normales = {
            'frecuencia_cardiaca': (60, 100),  # latidos por minuto
            'intervalo_pr': (120, 200),  # milisegundos
            'duracion_qrs': (80, 120),  # milisegundos
            'intervalo_qt': (350, 450),  # milisegundos (varía con FC)
            'intervalo_qtc': (350, 450),  # QT corregido
            'eje_qrs': (-30, 90)  # grados
        }
    
    def interpretar_ekg(self, parametros: Dict) -> Dict:
        """
        Interpreta los parámetros del EKG y genera un reporte automático
        
        Args:
            parametros: Diccionario con los valores medidos del EKG
            
        Returns:
            Diccionario con interpretación, hallazgos y clasificación
        """
        hallazgos = []
        alteraciones = []
        categorias = []
        clasificacion = 'normal'
        es_critico = False
        requiere_atencion = False
        
        # Analizar frecuencia cardíaca
        fc = parametros.get('frecuencia_cardiaca')
        if fc:
            fc_analisis = self._analizar_frecuencia_cardiaca(fc)
            if fc_analisis['hallazgo']:
                hallazgos.append(fc_analisis['hallazgo'])
                alteraciones.append(fc_analisis)
                if fc_analisis['severidad'] in ['moderado', 'severo']:
                    clasificacion = 'anormal_moderado'
                    requiere_atencion = True
                if fc_analisis['es_critico']:
                    es_critico = True
                    clasificacion = 'anormal_severo'
                categorias.append(fc_analisis['categoria'])
        
        # Analizar intervalo PR
        pr = parametros.get('intervalo_pr')
        if pr:
            pr_analisis = self._analizar_intervalo_pr(pr)
            if pr_analisis['hallazgo']:
                hallazgos.append(pr_analisis['hallazgo'])
                alteraciones.append(pr_analisis)
                if pr_analisis['severidad'] in ['moderado', 'severo']:
                    if clasificacion == 'normal':
                        clasificacion = 'anormal_moderado'
                    requiere_atencion = True
                categorias.append(pr_analisis['categoria'])
        
        # Analizar duración QRS
        qrs = parametros.get('duracion_qrs')
        if qrs:
            qrs_analisis = self._analizar_duracion_qrs(qrs)
            if qrs_analisis['hallazgo']:
                hallazgos.append(qrs_analisis['hallazgo'])
                alteraciones.append(qrs_analisis)
                if qrs_analisis['severidad'] in ['moderado', 'severo']:
                    if clasificacion == 'normal':
                        clasificacion = 'anormal_moderado'
                    requiere_atencion = True
                categorias.append(qrs_analisis['categoria'])
        
        # Analizar intervalo QTc
        qtc = parametros.get('intervalo_qtc')
        if qtc:
            qtc_analisis = self._analizar_intervalo_qtc(qtc)
            if qtc_analisis['hallazgo']:
                hallazgos.append(qtc_analisis['hallazgo'])
                alteraciones.append(qtc_analisis)
                if qtc_analisis['severidad'] in ['moderado', 'severo']:
                    if clasificacion != 'anormal_severo':
                        clasificacion = 'anormal_moderado'
                    requiere_atencion = True
                if qtc_analisis['es_critico']:
                    es_critico = True
                    clasificacion = 'anormal_severo'
                categorias.append(qtc_analisis['categoria'])
        
        # Analizar eje QRS
        eje = parametros.get('eje_qrs')
        if eje is not None:
            eje_analisis = self._analizar_eje_qrs(eje)
            if eje_analisis['hallazgo']:
                hallazgos.append(eje_analisis['hallazgo'])
                alteraciones.append(eje_analisis)
                if eje_analisis['severidad'] in ['moderado', 'severo']:
                    if clasificacion == 'normal':
                        clasificacion = 'anormal_leve'
                categorias.append(eje_analisis['categoria'])
        
        # Analizar ritmo
        ritmo = parametros.get('ritmo', '').lower()
        ritmo_analisis = self._analizar_ritmo(ritmo, parametros.get('ritmo_regular', True))
        if ritmo_analisis['hallazgo']:
            hallazgos.append(ritmo_analisis['hallazgo'])
            alteraciones.append(ritmo_analisis)
            if ritmo_analisis['severidad'] in ['moderado', 'severo']:
                clasificacion = 'anormal_moderado'
                requiere_atencion = True
            if ritmo_analisis['es_critico']:
                es_critico = True
                clasificacion = 'anormal_severo'
            categorias.append(ritmo_analisis['categoria'])
        
        # Generar interpretación textual
        interpretacion = self._generar_interpretacion(
            parametros, hallazgos, clasificacion, es_critico
        )
        
        # Generar recomendaciones
        recomendaciones = self._generar_recomendaciones(
            clasificacion, es_critico, categorias
        )
        
        return {
            'interpretacion': interpretacion,
            'hallazgos': hallazgos,
            'alteraciones': alteraciones,
            'categorias_detectadas': list(set(categorias)),
            'clasificacion': clasificacion,
            'requiere_atencion': requiere_atencion,
            'es_critico': es_critico,
            'recomendaciones': recomendaciones,
            'confianza': 0.85  # Confianza del análisis automático
        }
    
    def _analizar_frecuencia_cardiaca(self, fc: int) -> Dict:
        """Analiza la frecuencia cardíaca"""
        min_normal, max_normal = self.rangos_normales['frecuencia_cardiaca']
        
        if fc < 40:
            return {
                'parametro': 'frecuencia_cardiaca',
                'valor': fc,
                'hallazgo': f'Bradicardia severa ({fc} lpm)',
                'severidad': 'severo',
                'es_critico': True,
                'categoria': 'bradicardia'
            }
        elif fc < min_normal:
            return {
                'parametro': 'frecuencia_cardiaca',
                'valor': fc,
                'hallazgo': f'Bradicardia ({fc} lpm)',
                'severidad': 'leve',
                'es_critico': False,
                'categoria': 'bradicardia'
            }
        elif fc > 150:
            return {
                'parametro': 'frecuencia_cardiaca',
                'valor': fc,
                'hallazgo': f'Taquicardia severa ({fc} lpm)',
                'severidad': 'severo',
                'es_critico': True,
                'categoria': 'taquicardia'
            }
        elif fc > max_normal:
            return {
                'parametro': 'frecuencia_cardiaca',
                'valor': fc,
                'hallazgo': f'Taquicardia ({fc} lpm)',
                'severidad': 'leve',
                'es_critico': False,
                'categoria': 'taquicardia'
            }
        else:
            return {
                'parametro': 'frecuencia_cardiaca',
                'valor': fc,
                'hallazgo': None,
                'severidad': 'normal',
                'es_critico': False,
                'categoria': 'normal'
            }
    
    def _analizar_intervalo_pr(self, pr: int) -> Dict:
        """Analiza el intervalo PR"""
        min_normal, max_normal = self.rangos_normales['intervalo_pr']
        
        if pr < min_normal:
            return {
                'parametro': 'intervalo_pr',
                'valor': pr,
                'hallazgo': f'Intervalo PR corto ({pr} ms) - Posible síndrome de preexcitación',
                'severidad': 'moderado',
                'es_critico': False,
                'categoria': 'preexcitacion'
            }
        elif pr > 200 and pr <= 300:
            return {
                'parametro': 'intervalo_pr',
                'valor': pr,
                'hallazgo': f'Bloqueo AV de primer grado ({pr} ms)',
                'severidad': 'leve',
                'es_critico': False,
                'categoria': 'bloqueo_av'
            }
        elif pr > 300:
            return {
                'parametro': 'intervalo_pr',
                'valor': pr,
                'hallazgo': f'Intervalo PR muy prolongado ({pr} ms) - Posible bloqueo AV avanzado',
                'severidad': 'severo',
                'es_critico': False,
                'categoria': 'bloqueo_av'
            }
        else:
            return {
                'parametro': 'intervalo_pr',
                'valor': pr,
                'hallazgo': None,
                'severidad': 'normal',
                'es_critico': False,
                'categoria': 'normal'
            }
    
    def _analizar_duracion_qrs(self, qrs: int) -> Dict:
        """Analiza la duración del complejo QRS"""
        min_normal, max_normal = self.rangos_normales['duracion_qrs']
        
        if qrs > 120:
            if qrs > 140:
                severidad = 'moderado'
                hallazgo = f'QRS muy ensanchado ({qrs} ms) - Bloqueo de rama completo'
            else:
                severidad = 'leve'
                hallazgo = f'QRS ensanchado ({qrs} ms) - Posible bloqueo de rama'
            
            return {
                'parametro': 'duracion_qrs',
                'valor': qrs,
                'hallazgo': hallazgo,
                'severidad': severidad,
                'es_critico': False,
                'categoria': 'bloqueo_rama'
            }
        else:
            return {
                'parametro': 'duracion_qrs',
                'valor': qrs,
                'hallazgo': None,
                'severidad': 'normal',
                'es_critico': False,
                'categoria': 'normal'
            }
    
    def _analizar_intervalo_qtc(self, qtc: int) -> Dict:
        """Analiza el intervalo QT corregido"""
        
        if qtc > 500:
            return {
                'parametro': 'intervalo_qtc',
                'valor': qtc,
                'hallazgo': f'QTc muy prolongado ({qtc} ms) - RIESGO DE TORSADES DE POINTES',
                'severidad': 'severo',
                'es_critico': True,
                'categoria': 'qt_prolongado'
            }
        elif qtc > 450:
            return {
                'parametro': 'intervalo_qtc',
                'valor': qtc,
                'hallazgo': f'QTc prolongado ({qtc} ms) - Riesgo arrítmico',
                'severidad': 'moderado',
                'es_critico': False,
                'categoria': 'qt_prolongado'
            }
        elif qtc < 340:
            return {
                'parametro': 'intervalo_qtc',
                'valor': qtc,
                'hallazgo': f'QTc corto ({qtc} ms) - Posible síndrome de QT corto',
                'severidad': 'moderado',
                'es_critico': False,
                'categoria': 'qt_corto'
            }
        else:
            return {
                'parametro': 'intervalo_qtc',
                'valor': qtc,
                'hallazgo': None,
                'severidad': 'normal',
                'es_critico': False,
                'categoria': 'normal'
            }
    
    def _analizar_eje_qrs(self, eje: int) -> Dict:
        """Analiza el eje eléctrico del QRS"""
        
        if eje < -30:
            return {
                'parametro': 'eje_qrs',
                'valor': eje,
                'hallazgo': f'Desviación del eje a la izquierda ({eje}°)',
                'severidad': 'leve',
                'es_critico': False,
                'categoria': 'desviacion_eje'
            }
        elif eje > 90:
            return {
                'parametro': 'eje_qrs',
                'valor': eje,
                'hallazgo': f'Desviación del eje a la derecha ({eje}°)',
                'severidad': 'leve',
                'es_critico': False,
                'categoria': 'desviacion_eje'
            }
        else:
            return {
                'parametro': 'eje_qrs',
                'valor': eje,
                'hallazgo': None,
                'severidad': 'normal',
                'es_critico': False,
                'categoria': 'normal'
            }
    
    def _analizar_ritmo(self, ritmo: str, regular: bool) -> Dict:
        """Analiza el ritmo cardíaco"""
        
        if 'fibrilacion' in ritmo and 'auricular' in ritmo:
            return {
                'parametro': 'ritmo',
                'valor': ritmo,
                'hallazgo': 'Fibrilación auricular detectada',
                'severidad': 'moderado',
                'es_critico': False,
                'categoria': 'arritmia'
            }
        elif 'flutter' in ritmo:
            return {
                'parametro': 'ritmo',
                'valor': ritmo,
                'hallazgo': 'Flutter auricular detectado',
                'severidad': 'moderado',
                'es_critico': False,
                'categoria': 'arritmia'
            }
        elif 'taquicardia' in ritmo and 'ventricular' in ritmo:
            return {
                'parametro': 'ritmo',
                'valor': ritmo,
                'hallazgo': 'TAQUICARDIA VENTRICULAR - EMERGENCIA',
                'severidad': 'severo',
                'es_critico': True,
                'categoria': 'arritmia'
            }
        elif 'bloqueo' in ritmo and ('segundo' in ritmo or '2' in ritmo):
            return {
                'parametro': 'ritmo',
                'valor': ritmo,
                'hallazgo': 'Bloqueo AV de segundo grado',
                'severidad': 'moderado',
                'es_critico': False,
                'categoria': 'bloqueo_av'
            }
        elif 'bloqueo' in ritmo and ('tercer' in ritmo or '3' in ritmo or 'completo' in ritmo):
            return {
                'parametro': 'ritmo',
                'valor': ritmo,
                'hallazgo': 'Bloqueo AV completo (tercer grado)',
                'severidad': 'severo',
                'es_critico': True,
                'categoria': 'bloqueo_av'
            }
        elif 'sinusal' in ritmo:
            if not regular:
                return {
                    'parametro': 'ritmo',
                    'valor': ritmo,
                    'hallazgo': 'Arritmia sinusal',
                    'severidad': 'leve',
                    'es_critico': False,
                    'categoria': 'arritmia'
                }
            else:
                return {
                    'parametro': 'ritmo',
                    'valor': ritmo,
                    'hallazgo': None,
                    'severidad': 'normal',
                    'es_critico': False,
                    'categoria': 'normal'
                }
        else:
            return {
                'parametro': 'ritmo',
                'valor': ritmo,
                'hallazgo': None,
                'severidad': 'normal',
                'es_critico': False,
                'categoria': 'normal'
            }
    
    def _generar_interpretacion(
        self, parametros: Dict, hallazgos: List[str], 
        clasificacion: str, es_critico: bool
    ) -> str:
        """Genera la interpretación textual del EKG"""
        
        interpretacion = "📊 INTERPRETACIÓN AUTOMÁTICA DE ELECTROCARDIOGRAMA\n\n"
        
        # Parámetros medidos
        interpretacion += "📌 PARÁMETROS MEDIDOS:\n"
        if parametros.get('frecuencia_cardiaca'):
            interpretacion += f"  • Frecuencia cardíaca: {parametros['frecuencia_cardiaca']} lpm\n"
        if parametros.get('intervalo_pr'):
            interpretacion += f"  • Intervalo PR: {parametros['intervalo_pr']} ms\n"
        if parametros.get('duracion_qrs'):
            interpretacion += f"  • Duración QRS: {parametros['duracion_qrs']} ms\n"
        if parametros.get('intervalo_qtc'):
            interpretacion += f"  • Intervalo QTc: {parametros['intervalo_qtc']} ms\n"
        if parametros.get('eje_qrs') is not None:
            interpretacion += f"  • Eje QRS: {parametros['eje_qrs']}°\n"
        if parametros.get('ritmo'):
            interpretacion += f"  • Ritmo: {parametros['ritmo']}\n"
        
        interpretacion += "\n"
        
        # Hallazgos
        if hallazgos:
            if es_critico:
                interpretacion += "🚨 HALLAZGOS CRÍTICOS:\n"
            else:
                interpretacion += "⚠️ HALLAZGOS:\n"
            
            for hallazgo in hallazgos:
                interpretacion += f"  • {hallazgo}\n"
            interpretacion += "\n"
        else:
            interpretacion += "✅ No se detectaron alteraciones significativas\n\n"
        
        # Clasificación
        if clasificacion == 'normal':
            interpretacion += "💚 CONCLUSIÓN: Electrocardiograma dentro de límites normales\n"
        elif clasificacion == 'anormal_leve':
            interpretacion += "💛 CONCLUSIÓN: Electrocardiograma con alteraciones leves\n"
        elif clasificacion == 'anormal_moderado':
            interpretacion += "🧡 CONCLUSIÓN: Electrocardiograma con alteraciones moderadas\n"
        elif clasificacion == 'anormal_severo':
            interpretacion += "❤️ CONCLUSIÓN: Electrocardiograma con alteraciones severas\n"
        
        if es_critico:
            interpretacion += "\n🚨 ATENCIÓN: Este EKG requiere evaluación médica URGENTE\n"
        
        return interpretacion
    
    def _generar_recomendaciones(
        self, clasificacion: str, es_critico: bool, categorias: List[str]
    ) -> str:
        """Genera recomendaciones basadas en los hallazgos"""
        
        recomendaciones = ""
        
        if es_critico:
            recomendaciones += "🚨 URGENTE:\n"
            recomendaciones += "  • Evaluación cardiológica inmediata\n"
            recomendaciones += "  • Monitoreo cardíaco continuo\n"
            recomendaciones += "  • Considerar hospitalización\n\n"
        
        if 'taquicardia' in categorias or 'bradicardia' in categorias:
            recomendaciones += "📋 RECOMENDACIONES:\n"
            recomendaciones += "  • Evaluación por cardiología\n"
            recomendaciones += "  • Descartar causas secundarias (medicamentos, electrolitos, tiroides)\n"
            recomendaciones += "  • Considerar Holter de 24 horas\n\n"
        
        if 'arritmia' in categorias:
            recomendaciones += "📋 RECOMENDACIONES:\n"
            recomendaciones += "  • Evaluación cardiológica\n"
            recomendaciones += "  • Ecocardiograma\n"
            recomendaciones += "  • Perfil tiroideo\n"
            recomendaciones += "  • Electrolitos séricos\n"
            recomendaciones += "  • Considerar anticoagulación (si fibrilación auricular)\n\n"
        
        if 'bloqueo_av' in categorias or 'bloqueo_rama' in categorias:
            recomendaciones += "📋 RECOMENDACIONES:\n"
            recomendaciones += "  • Evaluación cardiológica\n"
            recomendaciones += "  • Ecocardiograma\n"
            recomendaciones += "  • Considerar marcapasos (según grado de bloqueo)\n\n"
        
        if 'qt_prolongado' in categorias:
            recomendaciones += "📋 RECOMENDACIONES:\n"
            recomendaciones += "  • Evaluación cardiológica urgente\n"
            recomendaciones += "  • Revisar medicamentos (suspender QT-prolongadores)\n"
            recomendaciones += "  • Electrolitos séricos (K+, Mg2+, Ca2+)\n"
            recomendaciones += "  • Evitar ejercicio intenso\n"
            recomendaciones += "  • Considerar betabloqueadores\n\n"
        
        if not recomendaciones:
            recomendaciones = "📋 RECOMENDACIONES:\n"
            recomendaciones += "  • Control de rutina según indicación clínica\n"
            recomendaciones += "  • Mantener hábitos cardiovasculares saludables\n"
        
        return recomendaciones


# Instancia singleton
_interpretador_ekg = None

def get_interpretador_ekg() -> InterpretadorEKG:
    """Obtiene la instancia del interpretador de EKG"""
    global _interpretador_ekg
    if _interpretador_ekg is None:
        _interpretador_ekg = InterpretadorEKG()
    return _interpretador_ekg
