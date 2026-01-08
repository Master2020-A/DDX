"""
Servicio de interpretación automática de Electroencefalogramas (EEG)
"""
from typing import Dict, List, Optional


class InterpretadorEEG:
    """Interpretador automático de estudios de EEG"""
    
    def __init__(self):
        # Rangos normales de frecuencias cerebrales
        self.rangos_frecuencias = {
            'delta': (0.5, 4),  # Hz - sueño profundo
            'theta': (4, 8),    # Hz - somnolencia
            'alfa': (8, 13),    # Hz - relajación, ojos cerrados
            'beta': (13, 30)    # Hz - actividad mental, concentración
        }
    
    def interpretar_eeg(self, parametros: Dict) -> Dict:
        """
        Interpreta los hallazgos del EEG y genera un reporte automático
        
        Args:
            parametros: Diccionario con los hallazgos del EEG
            
        Returns:
            Diccionario con interpretación, hallazgos y clasificación
        """
        hallazgos = []
        alteraciones = []
        categorias = []
        clasificacion = 'normal'
        es_critico = False
        requiere_atencion = False
        
        # Analizar actividad de fondo
        actividad_fondo = parametros.get('actividad_fondo', '').lower()
        if 'anormal' in actividad_fondo or 'desorganizada' in actividad_fondo:
            hallazgos.append(f"Actividad de fondo anormal: {actividad_fondo}")
            alteraciones.append({
                'tipo': 'actividad_fondo',
                'descripcion': actividad_fondo,
                'severidad': 'moderado'
            })
            clasificacion = 'anormal_moderado'
            requiere_atencion = True
            categorias.append('actividad_anormal')
        
        # Analizar frecuencia dominante
        freq_dominante = parametros.get('frecuencia_dominante')
        if freq_dominante:
            freq_analisis = self._analizar_frecuencia_dominante(
                freq_dominante, 
                parametros.get('edad_paciente', 30)
            )
            if freq_analisis['hallazgo']:
                hallazgos.append(freq_analisis['hallazgo'])
                alteraciones.append(freq_analisis)
                if freq_analisis['severidad'] in ['moderado', 'severo']:
                    clasificacion = 'anormal_moderado'
                    requiere_atencion = True
                categorias.append(freq_analisis['categoria'])
        
        # Analizar simetría
        simetria = parametros.get('simetria', '').lower()
        if 'asimetrica' in simetria:
            hallazgos.append(f"Asimetría hemisférica detectada")
            alteraciones.append({
                'tipo': 'simetria',
                'descripcion': simetria,
                'severidad': 'moderado'
            })
            if clasificacion == 'normal':
                clasificacion = 'anormal_leve'
            requiere_atencion = True
            categorias.append('asimetria')
        
        # Analizar hallazgos epileptiformes
        if parametros.get('ondas_agudas') or parametros.get('espigas'):
            hallazgos.append("⚠️ Actividad epileptiforme detectada (ondas agudas/espigas)")
            alteraciones.append({
                'tipo': 'epileptiforme',
                'descripcion': 'Ondas agudas o espigas',
                'severidad': 'severo'
            })
            clasificacion = 'anormal_severo'
            requiere_atencion = True
            es_critico = True
            categorias.append('epileptiforme')
        
        if parametros.get('complejos_punta_onda'):
            hallazgos.append("⚠️ Complejos punta-onda detectados")
            alteraciones.append({
                'tipo': 'epileptiforme',
                'descripcion': 'Complejos punta-onda',
                'severidad': 'severo'
            })
            clasificacion = 'anormal_severo'
            requiere_atencion = True
            es_critico = True
            categorias.append('epileptiforme')
        
        if parametros.get('actividad_paroxistica'):
            hallazgos.append("⚠️ Actividad paroxística detectada")
            alteraciones.append({
                'tipo': 'paroxistica',
                'descripcion': 'Actividad paroxística',
                'severidad': 'severo'
            })
            clasificacion = 'anormal_severo'
            requiere_atencion = True
            es_critico = True
            categorias.append('paroxistica')
        
        # Analizar enlentecimiento
        enlentecimiento = parametros.get('enlentecimiento', '').lower()
        if 'focal' in enlentecimiento:
            hallazgos.append(f"Enlentecimiento focal detectado")
            alteraciones.append({
                'tipo': 'enlentecimiento',
                'descripcion': enlentecimiento,
                'severidad': 'moderado'
            })
            if clasificacion == 'normal':
                clasificacion = 'anormal_moderado'
            requiere_atencion = True
            categorias.append('focal')
        elif 'difuso' in enlentecimiento:
            hallazgos.append(f"Enlentecimiento difuso detectado")
            alteraciones.append({
                'tipo': 'enlentecimiento',
                'descripcion': enlentecimiento,
                'severidad': 'moderado'
            })
            if clasificacion == 'normal':
                clasificacion = 'anormal_moderado'
            requiere_atencion = True
            categorias.append('enlentecimiento_difuso')
        
        # Analizar localización de hallazgos
        localizacion = parametros.get('localizacion_hallazgos', [])
        if localizacion:
            loc_texto = ', '.join(localizacion)
            hallazgos.append(f"Localización de hallazgos: {loc_texto}")
            categorias.append('focal')
        
        # Analizar lateralidad
        lateralidad = parametros.get('lateralidad', '').lower()
        if lateralidad and lateralidad != 'bilateral':
            hallazgos.append(f"Lateralidad: {lateralidad}")
        
        # Analizar pruebas de activación
        if parametros.get('fotoestimulacion'):
            foto = parametros['fotoestimulacion'].lower()
            if 'anormal' in foto or 'respuesta' in foto:
                hallazgos.append(f"Fotoestimulación: {parametros['fotoestimulacion']}")
                categorias.append('fotosensibilidad')
        
        if parametros.get('hiperventilacion'):
            hiper = parametros['hiperventilacion'].lower()
            if 'anormal' in hiper or 'respuesta' in hiper:
                hallazgos.append(f"Hiperventilación: {parametros['hiperventilacion']}")
        
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
            'confianza': 0.80  # Confianza del análisis automático
        }
    
    def _analizar_frecuencia_dominante(self, frecuencia: float, edad: int) -> Dict:
        """Analiza la frecuencia dominante según la edad del paciente"""
        
        # Frecuencia alfa normal en adultos: 8-13 Hz
        if edad >= 18:
            if frecuencia < 8:
                return {
                    'parametro': 'frecuencia_dominante',
                    'valor': frecuencia,
                    'hallazgo': f'Frecuencia dominante enlentecida ({frecuencia} Hz)',
                    'severidad': 'moderado',
                    'categoria': 'enlentecimiento'
                }
            elif frecuencia > 13:
                return {
                    'parametro': 'frecuencia_dominante',
                    'valor': frecuencia,
                    'hallazgo': f'Frecuencia dominante acelerada ({frecuencia} Hz)',
                    'severidad': 'leve',
                    'categoria': 'aceleracion'
                }
        
        return {
            'parametro': 'frecuencia_dominante',
            'valor': frecuencia,
            'hallazgo': None,
            'severidad': 'normal',
            'categoria': 'normal'
        }
    
    def _generar_interpretacion(
        self, parametros: Dict, hallazgos: List[str], 
        clasificacion: str, es_critico: bool
    ) -> str:
        """Genera la interpretación textual del EEG"""
        
        interpretacion = "📊 INTERPRETACIÓN AUTOMÁTICA DE ELECTROENCEFALOGRAMA\n\n"
        
        # Información del estudio
        interpretacion += "📌 INFORMACIÓN DEL ESTUDIO:\n"
        if parametros.get('tipo_estudio'):
            interpretacion += f"  • Tipo: {parametros['tipo_estudio']}\n"
        if parametros.get('duracion_minutos'):
            interpretacion += f"  • Duración: {parametros['duracion_minutos']} minutos\n"
        if parametros.get('estado_conciencia'):
            interpretacion += f"  • Estado de conciencia: {parametros['estado_conciencia']}\n"
        
        interpretacion += "\n"
        
        # Actividad de fondo
        interpretacion += "📌 ACTIVIDAD DE FONDO:\n"
        if parametros.get('actividad_fondo'):
            interpretacion += f"  • {parametros['actividad_fondo']}\n"
        if parametros.get('frecuencia_dominante'):
            interpretacion += f"  • Frecuencia dominante: {parametros['frecuencia_dominante']} Hz\n"
        if parametros.get('simetria'):
            interpretacion += f"  • Simetría: {parametros['simetria']}\n"
        if parametros.get('reactividad'):
            interpretacion += f"  • Reactividad: {parametros['reactividad']}\n"
        
        interpretacion += "\n"
        
        # Ritmos cerebrales
        if any([parametros.get('ritmo_alfa'), parametros.get('ritmo_beta'), 
                parametros.get('ritmo_theta'), parametros.get('ritmo_delta')]):
            interpretacion += "📌 RITMOS CEREBRALES:\n"
            if parametros.get('ritmo_alfa'):
                interpretacion += f"  • Alfa (8-13 Hz): {parametros['ritmo_alfa']}\n"
            if parametros.get('ritmo_beta'):
                interpretacion += f"  • Beta (13-30 Hz): {parametros['ritmo_beta']}\n"
            if parametros.get('ritmo_theta'):
                interpretacion += f"  • Theta (4-8 Hz): {parametros['ritmo_theta']}\n"
            if parametros.get('ritmo_delta'):
                interpretacion += f"  • Delta (0.5-4 Hz): {parametros['ritmo_delta']}\n"
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
            interpretacion += "💚 CONCLUSIÓN: Electroencefalograma dentro de límites normales\n"
        elif clasificacion == 'anormal_leve':
            interpretacion += "💛 CONCLUSIÓN: Electroencefalograma con alteraciones leves\n"
        elif clasificacion == 'anormal_moderado':
            interpretacion += "🧡 CONCLUSIÓN: Electroencefalograma con alteraciones moderadas\n"
        elif clasificacion == 'anormal_severo':
            interpretacion += "❤️ CONCLUSIÓN: Electroencefalograma con alteraciones severas\n"
        
        if es_critico:
            interpretacion += "\n🚨 ATENCIÓN: Este EEG muestra actividad epileptiforme - Requiere evaluación neurológica URGENTE\n"
        
        return interpretacion
    
    def _generar_recomendaciones(
        self, clasificacion: str, es_critico: bool, categorias: List[str]
    ) -> str:
        """Genera recomendaciones basadas en los hallazgos"""
        
        recomendaciones = ""
        
        if es_critico or 'epileptiforme' in categorias or 'paroxistica' in categorias:
            recomendaciones += "🚨 URGENTE:\n"
            recomendaciones += "  • Evaluación neurológica inmediata\n"
            recomendaciones += "  • Considerar inicio de tratamiento antiepiléptico\n"
            recomendaciones += "  • Resonancia magnética cerebral\n"
            recomendaciones += "  • Precauciones de seguridad (evitar alturas, conducir, nadar solo)\n\n"
        
        if 'focal' in categorias:
            recomendaciones += "📋 RECOMENDACIONES:\n"
            recomendaciones += "  • Evaluación neurológica\n"
            recomendaciones += "  • Resonancia magnética cerebral con contraste\n"
            recomendaciones += "  • Descartar lesión estructural\n"
            recomendaciones += "  • Considerar EEG prolongado o video-EEG\n\n"
        
        if 'enlentecimiento_difuso' in categorias or 'actividad_anormal' in categorias:
            recomendaciones += "📋 RECOMENDACIONES:\n"
            recomendaciones += "  • Evaluación neurológica\n"
            recomendaciones += "  • Descartar causas metabólicas (glucosa, electrolitos, función hepática/renal)\n"
            recomendaciones += "  • Descartar causas tóxicas (medicamentos, drogas)\n"
            recomendaciones += "  • Considerar neuroimagen (TC o RM cerebral)\n\n"
        
        if 'fotosensibilidad' in categorias:
            recomendaciones += "📋 RECOMENDACIONES:\n"
            recomendaciones += "  • Evaluación neurológica\n"
            recomendaciones += "  • Evitar luces intermitentes, videojuegos, discotecas\n"
            recomendaciones += "  • Usar lentes de sol en ambientes con luces brillantes\n"
            recomendaciones += "  • Considerar tratamiento antiepiléptico profiláctico\n\n"
        
        if 'asimetria' in categorias:
            recomendaciones += "📋 RECOMENDACIONES:\n"
            recomendaciones += "  • Evaluación neurológica\n"
            recomendaciones += "  • Neuroimagen (RM cerebral preferentemente)\n"
            recomendaciones += "  • Descartar lesión estructural\n\n"
        
        if not recomendaciones:
            recomendaciones = "📋 RECOMENDACIONES:\n"
            recomendaciones += "  • Control de rutina según indicación clínica\n"
            recomendaciones += "  • Mantener higiene del sueño adecuada\n"
            recomendaciones += "  • Evitar privación de sueño\n"
        
        return recomendaciones


# Instancia singleton
_interpretador_eeg = None

def get_interpretador_eeg() -> InterpretadorEEG:
    """Obtiene la instancia del interpretador de EEG"""
    global _interpretador_eeg
    if _interpretador_eeg is None:
        _interpretador_eeg = InterpretadorEEG()
    return _interpretador_eeg
