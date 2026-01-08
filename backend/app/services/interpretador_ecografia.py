"""
Servicio de interpretación automática de Ecografías/Ultrasonidos
"""
from typing import Dict, List, Optional


class InterpretadorEcografia:
    """Interpretador automático de estudios de ecografía"""
    
    def __init__(self):
        # Tipos de ecografía soportados
        self.tipos_ecografia = [
            'abdominal', 'pelvica', 'obstetrica', 'cardiaca', 'renal',
            'hepatica', 'vesicula', 'tiroides', 'mamaria', 'escrotal',
            'musculoesqueletica', 'vascular'
        ]
    
    def interpretar_ecografia(self, parametros: Dict) -> Dict:
        """
        Interpreta los hallazgos de la ecografía y genera un reporte automático
        
        Args:
            parametros: Diccionario con los hallazgos de la ecografía
            
        Returns:
            Diccionario con interpretación, hallazgos y clasificación
        """
        hallazgos = []
        alteraciones = []
        categorias = []
        clasificacion = 'normal'
        requiere_atencion = False
        requiere_seguimiento = False
        
        tipo_eco = parametros.get('tipo_ecografia', '').lower()
        
        # Analizar masas detectadas
        masas = parametros.get('masas_detectadas', [])
        if masas:
            for masa in masas:
                masa_analisis = self._analizar_masa(masa, tipo_eco)
                hallazgos.append(masa_analisis['hallazgo'])
                alteraciones.append(masa_analisis)
                
                if masa_analisis['severidad'] == 'sospechoso':
                    clasificacion = 'sospechoso'
                    requiere_atencion = True
                    requiere_seguimiento = True
                elif masa_analisis['severidad'] == 'benigno' and clasificacion == 'normal':
                    clasificacion = 'hallazgos_benignos'
                    requiere_seguimiento = True
                
                categorias.append(masa_analisis['categoria'])
        
        # Analizar líquido libre
        if parametros.get('liquido_libre'):
            cantidad = parametros.get('cantidad_liquido', 'indeterminada')
            hallazgo_liquido = self._analizar_liquido_libre(cantidad, tipo_eco)
            hallazgos.append(hallazgo_liquido['hallazgo'])
            alteraciones.append(hallazgo_liquido)
            
            if hallazgo_liquido['severidad'] in ['moderado', 'severo']:
                if clasificacion == 'normal':
                    clasificacion = 'patologico'
                requiere_atencion = True
            
            categorias.append('liquido_libre')
        
        # Analizar hallazgos por órgano
        hallazgos_organos = parametros.get('hallazgos_organos', {})
        for organo, descripcion in hallazgos_organos.items():
            if descripcion and descripcion.lower() not in ['normal', 'sin alteraciones']:
                hallazgos.append(f"{organo.capitalize()}: {descripcion}")
                alteraciones.append({
                    'tipo': 'hallazgo_organico',
                    'organo': organo,
                    'descripcion': descripcion,
                    'severidad': 'leve'
                })
                if clasificacion == 'normal':
                    clasificacion = 'hallazgos_benignos'
                categorias.append(f'hallazgo_{organo}')
        
        # Analizar mediciones
        mediciones = parametros.get('mediciones', [])
        for medicion in mediciones:
            med_analisis = self._analizar_medicion(medicion, tipo_eco)
            if med_analisis and med_analisis['hallazgo']:
                hallazgos.append(med_analisis['hallazgo'])
                alteraciones.append(med_analisis)
                if med_analisis['severidad'] in ['moderado', 'severo']:
                    if clasificacion == 'normal':
                        clasificacion = 'hallazgos_benignos'
                categorias.append('medicion_anormal')
        
        # Análisis específico obstétrico
        if parametros.get('es_obstetrica'):
            obs_analisis = self._analizar_obstetrico(parametros)
            if obs_analisis['hallazgos']:
                hallazgos.extend(obs_analisis['hallazgos'])
                alteraciones.extend(obs_analisis['alteraciones'])
                if obs_analisis['requiere_atencion']:
                    requiere_atencion = True
                    if clasificacion == 'normal':
                        clasificacion = 'hallazgos_benignos'
                categorias.append('obstetrico')
        
        # Analizar BI-RADS (para ecografías mamarias)
        birads = parametros.get('birads')
        if birads:
            birads_analisis = self._analizar_birads(birads)
            hallazgos.append(birads_analisis['hallazgo'])
            clasificacion = birads_analisis['clasificacion']
            requiere_atencion = birads_analisis['requiere_atencion']
            requiere_seguimiento = birads_analisis['requiere_seguimiento']
            categorias.append('birads')
        
        # Generar interpretación textual
        interpretacion = self._generar_interpretacion(
            parametros, hallazgos, clasificacion
        )
        
        # Generar recomendaciones
        recomendaciones = self._generar_recomendaciones(
            clasificacion, tipo_eco, categorias, parametros
        )
        
        return {
            'interpretacion': interpretacion,
            'hallazgos': hallazgos,
            'alteraciones': alteraciones,
            'categorias_detectadas': list(set(categorias)),
            'clasificacion': clasificacion,
            'requiere_atencion': requiere_atencion,
            'requiere_seguimiento': requiere_seguimiento,
            'recomendaciones': recomendaciones,
            'confianza': 0.75  # Confianza del análisis automático
        }
    
    def _analizar_masa(self, masa: Dict, tipo_eco: str) -> Dict:
        """Analiza una masa detectada"""
        
        ubicacion = masa.get('ubicacion', 'no especificada')
        tamano = masa.get('tamano_cm', 0)
        caracteristicas = masa.get('caracteristicas', '').lower()
        
        # Determinar severidad según características
        severidad = 'benigno'
        categoria = 'masa_benigna'
        
        # Características sospechosas
        if any(palabra in caracteristicas for palabra in [
            'irregular', 'heterogenea', 'vascularizada', 'solida',
            'bordes irregulares', 'sombra acustica posterior'
        ]):
            severidad = 'sospechoso'
            categoria = 'masa_sospechosa'
        
        # Características benignas
        elif any(palabra in caracteristicas for palabra in [
            'quiste simple', 'anecoica', 'bordes regulares', 
            'refuerzo acustico posterior', 'homogenea'
        ]):
            severidad = 'benigno'
            categoria = 'quiste_simple'
        
        hallazgo = f"Masa en {ubicacion} de {tamano} cm - {caracteristicas}"
        
        return {
            'tipo': 'masa',
            'ubicacion': ubicacion,
            'tamano_cm': tamano,
            'caracteristicas': caracteristicas,
            'hallazgo': hallazgo,
            'severidad': severidad,
            'categoria': categoria
        }
    
    def _analizar_liquido_libre(self, cantidad: str, tipo_eco: str) -> Dict:
        """Analiza líquido libre detectado"""
        
        cantidad_lower = cantidad.lower()
        
        if 'abundante' in cantidad_lower or 'moderado' in cantidad_lower:
            severidad = 'moderado'
            hallazgo = f"Líquido libre {cantidad} - Requiere evaluación"
        elif 'escaso' in cantidad_lower or 'minimo' in cantidad_lower:
            severidad = 'leve'
            hallazgo = f"Líquido libre {cantidad} - Puede ser fisiológico"
        else:
            severidad = 'leve'
            hallazgo = f"Líquido libre detectado"
        
        return {
            'tipo': 'liquido_libre',
            'cantidad': cantidad,
            'hallazgo': hallazgo,
            'severidad': severidad
        }
    
    def _analizar_medicion(self, medicion: Dict, tipo_eco: str) -> Optional[Dict]:
        """Analiza una medición específica"""
        
        nombre = medicion.get('nombre', '')
        valor = medicion.get('valor', 0)
        unidad = medicion.get('unidad', '')
        
        # Rangos normales según tipo de medición
        rangos = {
            'vesicula_pared': (0, 3),  # mm
            'higado_lobulo_derecho': (12, 15),  # cm
            'bazo_longitudinal': (8, 13),  # cm
            'rinon_longitudinal': (9, 12),  # cm
            'prostata_volumen': (20, 30),  # ml
        }
        
        nombre_lower = nombre.lower().replace(' ', '_')
        
        if nombre_lower in rangos:
            min_normal, max_normal = rangos[nombre_lower]
            
            if valor < min_normal:
                return {
                    'tipo': 'medicion',
                    'nombre': nombre,
                    'valor': valor,
                    'unidad': unidad,
                    'hallazgo': f"{nombre}: {valor} {unidad} (disminuido)",
                    'severidad': 'leve'
                }
            elif valor > max_normal:
                return {
                    'tipo': 'medicion',
                    'nombre': nombre,
                    'valor': valor,
                    'unidad': unidad,
                    'hallazgo': f"{nombre}: {valor} {unidad} (aumentado)",
                    'severidad': 'moderado'
                }
        
        return None
    
    def _analizar_obstetrico(self, parametros: Dict) -> Dict:
        """Analiza parámetros obstétricos"""
        
        hallazgos = []
        alteraciones = []
        requiere_atencion = False
        
        edad_gestacional = parametros.get('edad_gestacional_semanas', 0)
        numero_fetos = parametros.get('numero_fetos', 1)
        
        if numero_fetos > 1:
            hallazgos.append(f"Embarazo múltiple: {numero_fetos} fetos")
            alteraciones.append({
                'tipo': 'embarazo_multiple',
                'numero_fetos': numero_fetos,
                'severidad': 'leve'
            })
        
        if edad_gestacional > 0:
            hallazgos.append(f"Edad gestacional: {edad_gestacional} semanas")
        
        # Aquí se pueden agregar más análisis obstétricos específicos
        # como biometría fetal, líquido amniótico, placenta, etc.
        
        return {
            'hallazgos': hallazgos,
            'alteraciones': alteraciones,
            'requiere_atencion': requiere_atencion
        }
    
    def _analizar_birads(self, birads: str) -> Dict:
        """Analiza clasificación BI-RADS para ecografías mamarias"""
        
        birads_num = birads.strip().upper()
        
        clasificaciones = {
            '0': {
                'hallazgo': 'BI-RADS 0: Estudio incompleto - Se requieren estudios adicionales',
                'clasificacion': 'hallazgos_benignos',
                'requiere_atencion': True,
                'requiere_seguimiento': True
            },
            '1': {
                'hallazgo': 'BI-RADS 1: Negativo - Sin hallazgos',
                'clasificacion': 'normal',
                'requiere_atencion': False,
                'requiere_seguimiento': False
            },
            '2': {
                'hallazgo': 'BI-RADS 2: Hallazgos benignos',
                'clasificacion': 'hallazgos_benignos',
                'requiere_atencion': False,
                'requiere_seguimiento': False
            },
            '3': {
                'hallazgo': 'BI-RADS 3: Probablemente benigno - Seguimiento a corto plazo',
                'clasificacion': 'hallazgos_benignos',
                'requiere_atencion': False,
                'requiere_seguimiento': True
            },
            '4': {
                'hallazgo': 'BI-RADS 4: Sospechoso - Se recomienda biopsia',
                'clasificacion': 'sospechoso',
                'requiere_atencion': True,
                'requiere_seguimiento': True
            },
            '5': {
                'hallazgo': 'BI-RADS 5: Altamente sugestivo de malignidad - Biopsia urgente',
                'clasificacion': 'patologico',
                'requiere_atencion': True,
                'requiere_seguimiento': True
            },
            '6': {
                'hallazgo': 'BI-RADS 6: Malignidad comprobada por biopsia',
                'clasificacion': 'patologico',
                'requiere_atencion': True,
                'requiere_seguimiento': True
            }
        }
        
        return clasificaciones.get(birads_num, {
            'hallazgo': f'BI-RADS {birads_num}',
            'clasificacion': 'hallazgos_benignos',
            'requiere_atencion': False,
            'requiere_seguimiento': False
        })
    
    def _generar_interpretacion(
        self, parametros: Dict, hallazgos: List[str], clasificacion: str
    ) -> str:
        """Genera la interpretación textual de la ecografía"""
        
        interpretacion = "📊 INTERPRETACIÓN AUTOMÁTICA DE ECOGRAFÍA\n\n"
        
        # Información del estudio
        interpretacion += "📌 INFORMACIÓN DEL ESTUDIO:\n"
        if parametros.get('tipo_ecografia'):
            interpretacion += f"  • Tipo: Ecografía {parametros['tipo_ecografia']}\n"
        if parametros.get('region_anatomica'):
            interpretacion += f"  • Región: {parametros['region_anatomica']}\n"
        if parametros.get('via_acceso'):
            interpretacion += f"  • Vía de acceso: {parametros['via_acceso']}\n"
        if parametros.get('modo'):
            interpretacion += f"  • Modo: {parametros['modo']}\n"
        
        interpretacion += "\n"
        
        # Calidad del estudio
        if parametros.get('calidad_estudio'):
            interpretacion += f"📌 CALIDAD DEL ESTUDIO: {parametros['calidad_estudio']}\n"
            if parametros.get('limitaciones'):
                interpretacion += f"  • Limitaciones: {parametros['limitaciones']}\n"
            interpretacion += "\n"
        
        # Hallazgos
        if hallazgos:
            interpretacion += "⚠️ HALLAZGOS:\n"
            for hallazgo in hallazgos:
                interpretacion += f"  • {hallazgo}\n"
            interpretacion += "\n"
        else:
            interpretacion += "✅ No se detectaron alteraciones significativas\n\n"
        
        # Clasificación
        if clasificacion == 'normal':
            interpretacion += "💚 CONCLUSIÓN: Estudio dentro de límites normales\n"
        elif clasificacion == 'hallazgos_benignos':
            interpretacion += "💛 CONCLUSIÓN: Hallazgos benignos\n"
        elif clasificacion == 'sospechoso':
            interpretacion += "🧡 CONCLUSIÓN: Hallazgos sospechosos - Requiere evaluación adicional\n"
        elif clasificacion == 'patologico':
            interpretacion += "❤️ CONCLUSIÓN: Hallazgos patológicos\n"
        
        return interpretacion
    
    def _generar_recomendaciones(
        self, clasificacion: str, tipo_eco: str, categorias: List[str], parametros: Dict
    ) -> str:
        """Genera recomendaciones basadas en los hallazgos"""
        
        recomendaciones = "📋 RECOMENDACIONES:\n"
        
        if clasificacion == 'patologico':
            recomendaciones += "  • Evaluación médica urgente\n"
            recomendaciones += "  • Considerar estudios complementarios (TC, RM)\n"
            recomendaciones += "  • Valorar biopsia según hallazgos\n"
        
        elif clasificacion == 'sospechoso':
            recomendaciones += "  • Evaluación por especialista\n"
            recomendaciones += "  • Estudios complementarios según hallazgos\n"
            recomendaciones += "  • Seguimiento estrecho\n"
            
            if 'birads' in categorias:
                birads = parametros.get('birads', '')
                if birads in ['4', '5']:
                    recomendaciones += "  • Biopsia mamaria recomendada\n"
        
        elif clasificacion == 'hallazgos_benignos':
            recomendaciones += "  • Seguimiento según indicación clínica\n"
            recomendaciones += "  • Control ecográfico en 6-12 meses\n"
        
        else:  # normal
            recomendaciones += "  • Control de rutina según indicación clínica\n"
        
        # Recomendaciones específicas por tipo
        if tipo_eco == 'obstetrica':
            recomendaciones += "  • Continuar controles prenatales\n"
            recomendaciones += "  • Próximo ultrasonido según protocolo obstétrico\n"
        
        if 'liquido_libre' in categorias:
            recomendaciones += "  • Descartar causas de ascitis/derrame\n"
            recomendaciones += "  • Estudios de laboratorio (función hepática, renal, cardiaca)\n"
        
        if 'masa_sospechosa' in categorias:
            recomendaciones += "  • TC o RM con contraste\n"
            recomendaciones += "  • Marcadores tumorales según ubicación\n"
            recomendaciones += "  • Valoración quirúrgica\n"
        
        return recomendaciones


# Instancia singleton
_interpretador_ecografia = None

def get_interpretador_ecografia() -> InterpretadorEcografia:
    """Obtiene la instancia del interpretador de ecografía"""
    global _interpretador_ecografia
    if _interpretador_ecografia is None:
        _interpretador_ecografia = InterpretadorEcografia()
    return _interpretador_ecografia
