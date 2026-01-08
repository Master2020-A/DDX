"""
Servicio para análisis de resultados de laboratorio clínico
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AnalizadorLaboratorio:
    """
    Analiza resultados de laboratorio y detecta valores anormales
    """
    
    def analizar_resultados(
        self,
        area: str,
        tipo_prueba: str,
        resultados: Dict[str, float],
        rangos: List[Dict],
        sexo: str,
        edad: float
    ) -> Dict[str, Any]:
        """
        Analiza resultados de laboratorio contra rangos de referencia
        
        Args:
            area: Área del laboratorio (hematologia, quimica_clinica, etc.)
            tipo_prueba: Tipo de prueba realizada
            resultados: Diccionario con parámetro -> valor
            rangos: Lista de rangos de referencia
            sexo: Sexo del paciente (M/F)
            edad: Edad del paciente en años
            
        Returns:
            Diccionario con análisis completo
        """
        valores_anormales = []
        valores_criticos = []
        interpretaciones = []
        
        for parametro, valor in resultados.items():
            # Buscar rango de referencia apropiado
            rango = self._obtener_rango_apropiado(
                parametro, rangos, sexo, edad
            )
            
            if not rango:
                logger.warning(f"No se encontró rango de referencia para {parametro}")
                continue
            
            # Analizar valor
            analisis = self._analizar_valor(parametro, valor, rango)
            
            if analisis['estado'] != 'normal':
                valores_anormales.append(analisis)
                
            if analisis.get('critico'):
                valores_criticos.append(analisis)
                
            if analisis.get('interpretacion'):
                interpretaciones.append(analisis['interpretacion'])
        
        # Generar interpretación general
        interpretacion_general = self._generar_interpretacion_general(
            area, tipo_prueba, valores_anormales, valores_criticos
        )
        
        return {
            'estado': 'anormal' if valores_anormales else 'normal',
            'valores_anormales': valores_anormales,
            'valores_criticos': valores_criticos,
            'interpretacion': interpretacion_general,
            'requiere_atencion': len(valores_criticos) > 0,
            'fecha_analisis': datetime.utcnow().isoformat()
        }
    
    def _obtener_rango_apropiado(
        self,
        parametro: str,
        rangos: List[Dict],
        sexo: str,
        edad: float
    ) -> Optional[Dict]:
        """Encuentra el rango de referencia apropiado"""
        for rango in rangos:
            if rango['parametro'].lower() != parametro.lower():
                continue
            
            # Verificar sexo
            if rango.get('sexo') and rango['sexo'] != sexo:
                continue
            
            # Verificar edad
            if rango.get('edad_min') and edad < rango['edad_min']:
                continue
            if rango.get('edad_max') and edad > rango['edad_max']:
                continue
            
            return rango
        
        return None
    
    def _analizar_valor(
        self,
        parametro: str,
        valor: float,
        rango: Dict
    ) -> Dict[str, Any]:
        """Analiza un valor individual contra su rango"""
        resultado = {
            'parametro': parametro,
            'valor': valor,
            'unidad': rango.get('unidad', ''),
            'rango_min': rango.get('valor_min'),
            'rango_max': rango.get('valor_max'),
            'estado': 'normal',
            'critico': False,
            'interpretacion': None
        }
        
        # Verificar si es crítico
        if rango.get('critico_bajo') and valor <= rango['critico_bajo']:
            resultado['estado'] = 'critico_bajo'
            resultado['critico'] = True
            resultado['interpretacion'] = f"⚠️ CRÍTICO: {parametro} muy bajo ({valor} {rango.get('unidad', '')})"
            if rango.get('interpretacion_bajo'):
                resultado['interpretacion'] += f". {rango['interpretacion_bajo']}"
        
        elif rango.get('critico_alto') and valor >= rango['critico_alto']:
            resultado['estado'] = 'critico_alto'
            resultado['critico'] = True
            resultado['interpretacion'] = f"⚠️ CRÍTICO: {parametro} muy alto ({valor} {rango.get('unidad', '')})"
            if rango.get('interpretacion_alto'):
                resultado['interpretacion'] += f". {rango['interpretacion_alto']}"
        
        # Verificar si está fuera de rango normal
        elif rango.get('valor_min') and valor < rango['valor_min']:
            resultado['estado'] = 'bajo'
            resultado['interpretacion'] = f"↓ {parametro} bajo ({valor} {rango.get('unidad', '')}, normal: {rango['valor_min']}-{rango['valor_max']})"
            if rango.get('interpretacion_bajo'):
                resultado['interpretacion'] += f". {rango['interpretacion_bajo']}"
        
        elif rango.get('valor_max') and valor > rango['valor_max']:
            resultado['estado'] = 'alto'
            resultado['interpretacion'] = f"↑ {parametro} alto ({valor} {rango.get('unidad', '')}, normal: {rango['valor_min']}-{rango['valor_max']})"
            if rango.get('interpretacion_alto'):
                resultado['interpretacion'] += f". {rango['interpretacion_alto']}"
        
        return resultado
    
    def _generar_interpretacion_general(
        self,
        area: str,
        tipo_prueba: str,
        valores_anormales: List[Dict],
        valores_criticos: List[Dict]
    ) -> str:
        """Genera interpretación general de los resultados"""
        interpretacion = []
        
        # Título
        interpretacion.append(f"📊 Análisis de {tipo_prueba} ({area})\n")
        
        # Valores críticos
        if valores_criticos:
            interpretacion.append("🚨 VALORES CRÍTICOS - REQUIERE ATENCIÓN INMEDIATA:")
            for vc in valores_criticos:
                interpretacion.append(f"  • {vc['interpretacion']}")
            interpretacion.append("")
        
        # Valores anormales no críticos
        valores_no_criticos = [v for v in valores_anormales if not v.get('critico')]
        if valores_no_criticos:
            interpretacion.append("⚠️ Valores fuera de rango normal:")
            for va in valores_no_criticos:
                interpretacion.append(f"  • {va['interpretacion']}")
            interpretacion.append("")
        
        # Interpretación por área
        interpretacion_area = self._interpretacion_por_area(
            area, tipo_prueba, valores_anormales
        )
        if interpretacion_area:
            interpretacion.append(interpretacion_area)
        
        # Estado general
        if not valores_anormales:
            interpretacion.append("✅ Todos los valores dentro de rangos normales.")
        
        return "\n".join(interpretacion)
    
    def _interpretacion_por_area(
        self,
        area: str,
        tipo_prueba: str,
        valores_anormales: List[Dict]
    ) -> str:
        """Genera interpretación específica por área"""
        if not valores_anormales:
            return ""
        
        interpretaciones_especiales = {
            'hematologia': self._interpretar_hematologia,
            'quimica_clinica': self._interpretar_quimica,
            'inmunologia': self._interpretar_inmunologia,
            'uroanalisis': self._interpretar_uroanalisis,
        }
        
        func = interpretaciones_especiales.get(area)
        if func:
            return func(tipo_prueba, valores_anormales)
        
        return ""
    
    def _interpretar_hematologia(
        self,
        tipo_prueba: str,
        valores_anormales: List[Dict]
    ) -> str:
        """Interpretación para estudios hematológicos"""
        interpretacion = ["💡 Interpretación clínica:"]
        
        parametros_dict = {v['parametro'].lower(): v for v in valores_anormales}
        parametros_bajos = [v['parametro'] for v in valores_anormales if v['estado'] in ['bajo', 'critico_bajo']]
        parametros_altos = [v['parametro'] for v in valores_anormales if v['estado'] in ['alto', 'critico_alto']]
        
        # Análisis de Serie Roja (Anemia)
        hb_bajo = any(p.lower() in ['hemoglobina'] for p in parametros_bajos)
        hto_bajo = any(p.lower() in ['hematocrito'] for p in parametros_bajos)
        eritrocitos_bajo = any(p.lower() in ['eritrocitos'] for p in parametros_bajos)
        
        if hb_bajo or hto_bajo or eritrocitos_bajo:
            interpretacion.append("\n📌 SERIE ROJA:")
            interpretacion.append("  • ANEMIA detectada")
            
            # Clasificar tipo de anemia por VCM
            vcm = parametros_dict.get('vcm')
            if vcm:
                if vcm['estado'] == 'bajo':
                    interpretacion.append("  • Anemia MICROCÍTICA (VCM bajo)")
                    interpretacion.append("    - Causas probables: Deficiencia de hierro, talasemia, anemia de enfermedad crónica")
                    interpretacion.append("    - Estudios sugeridos: Ferritina, hierro sérico, TIBC, electroforesis de hemoglobina")
                elif vcm['estado'] == 'alto':
                    interpretacion.append("  • Anemia MACROCÍTICA (VCM alto)")
                    interpretacion.append("    - Causas probables: Deficiencia de B12/folato, alcoholismo, hipotiroidismo")
                    interpretacion.append("    - Estudios sugeridos: Vitamina B12, ácido fólico, TSH, función hepática")
                else:
                    interpretacion.append("  • Anemia NORMOCÍTICA (VCM normal)")
                    interpretacion.append("    - Causas probables: Hemorragia aguda, anemia de enfermedad crónica, hemólisis")
                    interpretacion.append("    - Estudios sugeridos: Reticulocitos, bilirrubinas, LDH, haptoglobina")
            else:
                interpretacion.append("    - Recomendación: Solicitar índices eritrocitarios (VCM, HCM, CHCM) para clasificar")
        
        # Policitemia
        if any(p.lower() in ['hemoglobina', 'hematocrito'] for p in parametros_altos):
            interpretacion.append("\n📌 SERIE ROJA:")
            interpretacion.append("  • POLICITEMIA/ERITROCITOSIS detectada")
            interpretacion.append("    - Causas probables: Deshidratación, hipoxia crónica, policitemia vera")
            interpretacion.append("    - Recomendación: Hidratación, gasometría, evaluación de saturación de O2")
        
        # Análisis de Serie Blanca
        if 'leucocitos' in [p.lower() for p in parametros_altos]:
            interpretacion.append("\n📌 SERIE BLANCA:")
            interpretacion.append("  • LEUCOCITOSIS detectada")
            
            # Analizar diferencial
            if 'neutrofilos' in [p.lower() for p in parametros_altos] or 'segmentados' in [p.lower() for p in parametros_altos]:
                interpretacion.append("  • Neutrofilia predominante")
                bandas = parametros_dict.get('bandas')
                if bandas and bandas['estado'] == 'alto':
                    interpretacion.append("    - DESVIACIÓN A LA IZQUIERDA (bandas elevadas)")
                    interpretacion.append("    - Sugiere: Infección bacteriana aguda severa")
                else:
                    interpretacion.append("    - Causas: Infección bacteriana, inflamación, estrés, corticoides")
            
            if 'linfocitos' in [p.lower() for p in parametros_altos]:
                interpretacion.append("  • Linfocitosis")
                interpretacion.append("    - Causas: Infección viral, leucemia linfocítica crónica")
            
            if 'monocitos' in [p.lower() for p in parametros_altos]:
                interpretacion.append("  • Monocitosis")
                interpretacion.append("    - Causas: Infecciones crónicas, tuberculosis, enfermedades autoinmunes")
            
            if 'eosinofilos' in [p.lower() for p in parametros_altos]:
                interpretacion.append("  • Eosinofilia")
                interpretacion.append("    - Causas: Parasitosis, alergias, asma, enfermedades autoinmunes")
        
        if 'leucocitos' in [p.lower() for p in parametros_bajos]:
            interpretacion.append("\n📌 SERIE BLANCA:")
            interpretacion.append("  • LEUCOPENIA detectada")
            interpretacion.append("    - Causas: Infección viral, medicamentos, enfermedades autoinmunes")
            interpretacion.append("    - ⚠️ PRECAUCIÓN: Riesgo aumentado de infecciones")
            interpretacion.append("    - Recomendación: Evitar contacto con personas enfermas, vigilar fiebre")
        
        # Análisis de Plaquetas
        if 'plaquetas' in [p.lower() for p in parametros_bajos]:
            interpretacion.append("\n📌 PLAQUETAS:")
            interpretacion.append("  • TROMBOCITOPENIA detectada")
            plaquetas_val = parametros_dict.get('plaquetas', {}).get('valor', 0)
            if plaquetas_val < 50:
                interpretacion.append("    - ⚠️ SEVERA: Alto riesgo de sangrado")
                interpretacion.append("    - Precauciones: Evitar traumatismos, no AINEs, no IM")
            elif plaquetas_val < 100:
                interpretacion.append("    - MODERADA: Riesgo moderado de sangrado")
            interpretacion.append("    - Causas: Destrucción periférica (PTI), producción disminuida, secuestro esplénico")
            interpretacion.append("    - Estudios: Frotis de sangre periférica, anticuerpos antiplaquetarios")
        
        if 'plaquetas' in [p.lower() for p in parametros_altos]:
            interpretacion.append("\n📌 PLAQUETAS:")
            interpretacion.append("  • TROMBOCITOSIS detectada")
            interpretacion.append("    - Causas: Reactiva (infección, inflamación), esencial, post-esplenectomía")
            interpretacion.append("    - Riesgo: Trombosis si >1,000,000/μL")
        
        return "\n".join(interpretacion)
    
    def _interpretar_quimica(
        self,
        tipo_prueba: str,
        valores_anormales: List[Dict]
    ) -> str:
        """Interpretación para química clínica"""
        interpretacion = ["💡 Interpretación clínica:"]
        
        parametros = {v['parametro'].lower(): v for v in valores_anormales}
        
        # Glucosa
        if 'glucosa' in parametros:
            interpretacion.append("\n📌 METABOLISMO DE GLUCOSA:")
            estado = parametros['glucosa']['estado']
            valor = parametros['glucosa']['valor']
            
            if estado in ['alto', 'critico_alto']:
                interpretacion.append("  • HIPERGLUCEMIA detectada")
                if valor >= 200:
                    interpretacion.append("    - Criterio diagnóstico de DIABETES MELLITUS")
                    interpretacion.append("    - Recomendación: HbA1c, glucosa en ayunas, curva de tolerancia")
                elif valor >= 126:
                    interpretacion.append("    - Sugestivo de DIABETES MELLITUS (confirmar con segunda medición)")
                    interpretacion.append("    - Estudios: HbA1c, glucosa en ayunas repetida")
                elif valor >= 100:
                    interpretacion.append("    - PREDIABETES / Glucosa alterada en ayunas")
                    interpretacion.append("    - Recomendación: Cambios en estilo de vida, HbA1c")
                interpretacion.append("    - Manejo: Dieta, ejercicio, posible tratamiento farmacológico")
            
            elif estado in ['bajo', 'critico_bajo']:
                interpretacion.append("  • ⚠️ HIPOGLUCEMIA detectada")
                if valor < 50:
                    interpretacion.append("    - 🚨 SEVERA: Requiere atención inmediata")
                    interpretacion.append("    - Riesgo: Pérdida de conciencia, convulsiones")
                interpretacion.append("    - Causas: Exceso de insulina, ayuno prolongado, insulinoma")
                interpretacion.append("    - Acción inmediata: Administrar glucosa oral/IV")
        
        # Función Renal
        if any(p in parametros for p in ['creatinina', 'urea', 'acido_urico']):
            interpretacion.append("\n📌 FUNCIÓN RENAL:")
            
            if 'creatinina' in parametros:
                creat = parametros['creatinina']
                if creat['estado'] in ['alto', 'critico_alto']:
                    interpretacion.append("  • CREATININA ELEVADA")
                    interpretacion.append("    - Indica: Disminución de la filtración glomerular")
                    interpretacion.append("    - Calcular: TFG (Tasa de Filtración Glomerular)")
                    interpretacion.append("    - Clasificación ERC:")
                    interpretacion.append("      * TFG >90: Normal")
                    interpretacion.append("      * TFG 60-89: ERC Estadio 2 (leve)")
                    interpretacion.append("      * TFG 30-59: ERC Estadio 3 (moderada)")
                    interpretacion.append("      * TFG 15-29: ERC Estadio 4 (severa)")
                    interpretacion.append("      * TFG <15: ERC Estadio 5 (falla renal)")
            
            if 'urea' in parametros and parametros['urea']['estado'] in ['alto', 'critico_alto']:
                interpretacion.append("  • UREA ELEVADA (Azotemia)")
                interpretacion.append("    - Causas: Insuficiencia renal, deshidratación, dieta hiperproteica")
            
            if 'acido_urico' in parametros and parametros['acido_urico']['estado'] in ['alto', 'critico_alto']:
                interpretacion.append("  • HIPERURICEMIA")
                interpretacion.append("    - Riesgo: Gota, litiasis renal")
                interpretacion.append("    - Manejo: Dieta baja en purinas, hidratación, alopurinol")
            
            interpretacion.append("    - Estudios complementarios: EGO, ultrasonido renal, electrolitos")
        
        # Perfil Lipídico
        if any(p in parametros for p in ['colesterol_total', 'trigliceridos', 'ldl', 'hdl']):
            interpretacion.append("\n📌 PERFIL LIPÍDICO:")
            interpretacion.append("  • DISLIPIDEMIA detectada")
            
            if 'colesterol_total' in parametros and parametros['colesterol_total']['estado'] in ['alto', 'critico_alto']:
                valor = parametros['colesterol_total']['valor']
                if valor >= 240:
                    interpretacion.append("    - Colesterol total ALTO (>240 mg/dL)")
                elif valor >= 200:
                    interpretacion.append("    - Colesterol total LÍMITE ALTO (200-239 mg/dL)")
            
            if 'ldl' in parametros and parametros['ldl']['estado'] in ['alto', 'critico_alto']:
                interpretacion.append("    - LDL elevado (colesterol 'malo')")
                interpretacion.append("    - Mayor riesgo cardiovascular")
            
            if 'hdl' in parametros and parametros['hdl']['estado'] in ['bajo', 'critico_bajo']:
                interpretacion.append("    - HDL bajo (colesterol 'bueno')")
                interpretacion.append("    - Factor de riesgo cardiovascular")
            
            if 'trigliceridos' in parametros and parametros['trigliceridos']['estado'] in ['alto', 'critico_alto']:
                valor = parametros['trigliceridos']['valor']
                if valor >= 500:
                    interpretacion.append("    - Triglicéridos MUY ALTOS (>500 mg/dL)")
                    interpretacion.append("    - ⚠️ Riesgo de pancreatitis aguda")
                elif valor >= 200:
                    interpretacion.append("    - Triglicéridos ALTOS (>200 mg/dL)")
            
            interpretacion.append("    - Calcular: Riesgo cardiovascular (Score de Framingham)")
            interpretacion.append("    - Manejo: Dieta, ejercicio, estatinas, fibratos")
            interpretacion.append("    - Meta LDL: <100 mg/dL (riesgo alto: <70 mg/dL)")
        
        # Función Hepática
        if any(p in parametros for p in ['tgo', 'tgp', 'bilirrubina_total', 'fosfatasa_alcalina']):
            interpretacion.append("\n📌 FUNCIÓN HEPÁTICA:")
            interpretacion.append("  • ALTERACIÓN HEPÁTICA detectada")
            
            tgo_alto = 'tgo' in parametros and parametros['tgo']['estado'] in ['alto', 'critico_alto']
            tgp_alto = 'tgp' in parametros and parametros['tgp']['estado'] in ['alto', 'critico_alto']
            
            if tgo_alto and tgp_alto:
                tgo_val = parametros['tgo']['valor']
                tgp_val = parametros['tgp']['valor']
                ratio = tgo_val / tgp_val if tgp_val > 0 else 0
                
                interpretacion.append("    - Transaminasas elevadas (TGO/TGP)")
                if ratio > 2:
                    interpretacion.append("    - Ratio TGO/TGP >2: Sugiere hepatopatía alcohólica")
                elif ratio < 1:
                    interpretacion.append("    - Ratio TGO/TGP <1: Sugiere hepatitis viral o NASH")
                
                if tgo_val > 1000 or tgp_val > 1000:
                    interpretacion.append("    - Elevación MASIVA: Hepatitis aguda, isquemia hepática, toxicidad")
                elif tgo_val > 300 or tgp_val > 300:
                    interpretacion.append("    - Elevación SEVERA: Hepatitis aguda, medicamentos")
                else:
                    interpretacion.append("    - Elevación LEVE-MODERADA: Esteatosis, hepatitis crónica")
            
            if 'bilirrubina_total' in parametros and parametros['bilirrubina_total']['estado'] in ['alto', 'critico_alto']:
                interpretacion.append("    - Hiperbilirrubinemia (Ictericia)")
                interpretacion.append("    - Causas: Hemólisis, hepatocelular, colestasis")
            
            if 'fosfatasa_alcalina' in parametros and parametros['fosfatasa_alcalina']['estado'] in ['alto', 'critico_alto']:
                interpretacion.append("    - Fosfatasa alcalina elevada")
                interpretacion.append("    - Sugiere: Colestasis, enfermedad ósea")
            
            interpretacion.append("    - Estudios: Perfil viral (VHA, VHB, VHC), ultrasonido hepático")
            interpretacion.append("    - Evaluar: Consumo de alcohol, medicamentos hepatotóxicos")
        
        return "\n".join(interpretacion)
    
    def _interpretar_inmunologia(
        self,
        tipo_prueba: str,
        valores_anormales: List[Dict]
    ) -> str:
        """Interpretación para inmunología"""
        interpretacion = ["💡 Interpretación clínica:"]
        
        parametros = [v['parametro'].lower() for v in valores_anormales]
        
        if 'proteina_c_reactiva' in parametros or 'pcr' in parametros:
            interpretacion.append("\n📌 MARCADORES INFLAMATORIOS:")
            interpretacion.append("  • PCR elevada")
            interpretacion.append("    - Indica: Proceso inflamatorio o infeccioso activo")
            interpretacion.append("    - Causas: Infección, trauma, infarto, enfermedades autoinmunes")
            interpretacion.append("    - Seguimiento: Repetir en 1-2 semanas para evaluar evolución")
        
        if any(p in parametros for p in ['vih', 'vdrl', 'hepatitis']):
            interpretacion.append("  • Resultado positivo - Requiere confirmación y seguimiento especializado")
        
        return "\n".join(interpretacion)
    
    def _interpretar_uroanalisis(
        self,
        tipo_prueba: str,
        valores_anormales: List[Dict]
    ) -> str:
        """Interpretación para uroanálisis (EGO)"""
        interpretacion = ["💡 Interpretación clínica:"]
        
        parametros = {v['parametro'].lower(): v for v in valores_anormales}
        
        # Análisis de infección urinaria
        tiene_leucocitos = 'leucocitos_orina' in parametros
        tiene_nitritos = 'nitritos_orina' in parametros
        tiene_bacterias = 'bacterias_orina' in parametros
        
        if tiene_leucocitos or tiene_nitritos or tiene_bacterias:
            interpretacion.append("\n📌 INFECCIÓN URINARIA:")
            interpretacion.append("  • Hallazgos sugestivos de INFECCIÓN DEL TRACTO URINARIO (ITU)")
            
            if tiene_nitritos:
                interpretacion.append("    - Nitritos POSITIVOS: Alta especificidad para bacterias gram negativas")
            if tiene_leucocitos:
                interpretacion.append("    - Leucocitos elevados: Respuesta inflamatoria activa")
            if tiene_bacterias:
                interpretacion.append("    - Bacteriuria presente")
            
            interpretacion.append("    - Recomendación: Urocultivo con antibiograma")
            interpretacion.append("    - Tratamiento empírico: Considerar según síntomas clínicos")
            interpretacion.append("    - Seguimiento: EGO de control post-tratamiento")
        
        # Hematuria
        tiene_sangre = 'hemoglobina_orina' in parametros
        tiene_eritrocitos = 'eritrocitos_orina' in parametros
        
        if tiene_sangre or tiene_eritrocitos:
            interpretacion.append("\n📌 HEMATURIA:")
            interpretacion.append("  • SANGRE EN ORINA detectada")
            interpretacion.append("    - Causas:")
            interpretacion.append("      * Infección urinaria")
            interpretacion.append("      * Litiasis renal (cálculos)")
            interpretacion.append("      * Trauma")
            interpretacion.append("      * Glomerulonefritis")
            interpretacion.append("      * Tumores (vejiga, riñón)")
            interpretacion.append("    - Estudios: Ultrasonido renal, cistoscopia si persiste")
            interpretacion.append("    - ⚠️ Hematuria persistente requiere evaluación urológica")
        
        # Proteinuria
        if 'proteinas_orina' in parametros:
            interpretacion.append("\n📌 PROTEINURIA:")
            interpretacion.append("  • PROTEÍNAS EN ORINA detectadas")
            interpretacion.append("    - Indica: Daño glomerular o tubular")
            interpretacion.append("    - Causas:")
            interpretacion.append("      * Enfermedad renal crónica")
            interpretacion.append("      * Diabetes mellitus (nefropatía diabética)")
            interpretacion.append("      * Hipertensión arterial")
            interpretacion.append("      * Glomerulonefritis")
            interpretacion.append("      * Proteinuria ortostática (benigna)")
            interpretacion.append("    - Cuantificar: Proteínas en orina de 24 horas")
            interpretacion.append("    - Estudios: Creatinina sérica, TFG, relación proteína/creatinina")
        
        # Glucosuria
        if 'glucosa_orina' in parametros:
            interpretacion.append("\n📌 GLUCOSURIA:")
            interpretacion.append("  • GLUCOSA EN ORINA detectada")
            interpretacion.append("    - Causas:")
            interpretacion.append("      * Diabetes mellitus descontrolada (glucosa >180 mg/dL)")
            interpretacion.append("      * Glucosuria renal (defecto tubular)")
            interpretacion.append("      * Embarazo")
            interpretacion.append("    - Estudios: Glucosa sérica, HbA1c")
            interpretacion.append("    - Si diabético: Ajustar tratamiento")
        
        # Cetonas
        if 'cetonas_orina' in parametros:
            interpretacion.append("\n📌 CETONURIA:")
            interpretacion.append("  • CETONAS EN ORINA detectadas")
            interpretacion.append("    - Causas:")
            interpretacion.append("      * Cetoacidosis diabética (emergencia)")
            interpretacion.append("      * Ayuno prolongado")
            interpretacion.append("      * Dieta cetogénica")
            interpretacion.append("      * Vómito persistente")
            interpretacion.append("    - ⚠️ Si diabético + cetonas: Evaluar cetoacidosis (emergencia)")
            interpretacion.append("    - Estudios: Glucosa, gasometría, electrolitos")
        
        # Bilirrubina
        if 'bilirrubina_orina' in parametros:
            interpretacion.append("\n📌 BILIRRUBINURIA:")
            interpretacion.append("  • BILIRRUBINA EN ORINA detectada")
            interpretacion.append("    - Indica: Enfermedad hepática o biliar")
            interpretacion.append("    - Causas: Hepatitis, cirrosis, obstrucción biliar")
            interpretacion.append("    - Estudios: Bilirrubinas séricas, transaminasas, ultrasonido hepático")
        
        # pH anormal
        if 'ph_orina' in parametros:
            ph_val = parametros['ph_orina'].get('valor', 0)
            if ph_val > 0:
                interpretacion.append("\n📌 pH URINARIO:")
                if ph_val > 7.5:
                    interpretacion.append("  • pH ALCALINO (>7.5)")
                    interpretacion.append("    - Causas: ITU por Proteus, dieta vegetariana, alcalosis")
                    interpretacion.append("    - Riesgo: Litiasis de fosfato")
                elif ph_val < 5.5:
                    interpretacion.append("  • pH ÁCIDO (<5.5)")
                    interpretacion.append("    - Causas: Dieta rica en proteínas, acidosis, diabetes")
                    interpretacion.append("    - Riesgo: Litiasis de ácido úrico")
        
        # Densidad anormal
        if 'densidad_orina' in parametros:
            dens_val = parametros['densidad_orina'].get('valor', 0)
            if dens_val > 0:
                interpretacion.append("\n📌 DENSIDAD URINARIA:")
                if dens_val > 1.030:
                    interpretacion.append("  • DENSIDAD ALTA (>1.030)")
                    interpretacion.append("    - Indica: Deshidratación, glucosuria, proteinuria")
                elif dens_val < 1.010:
                    interpretacion.append("  • DENSIDAD BAJA (<1.010)")
                    interpretacion.append("    - Indica: Sobrehidratación, diabetes insípida, insuficiencia renal")
        
        # Cristales
        if 'cristales_orina' in parametros:
            interpretacion.append("\n📌 CRISTALURIA:")
            interpretacion.append("  • CRISTALES detectados")
            interpretacion.append("    - Riesgo: Litiasis renal (cálculos)")
            interpretacion.append("    - Recomendación: Aumentar ingesta de líquidos (2-3 L/día)")
            interpretacion.append("    - Tipo de cristales determina manejo específico")
        
        # Cilindros
        if 'cilindros_orina' in parametros:
            interpretacion.append("\n📌 CILINDROS:")
            interpretacion.append("  • CILINDROS detectados")
            interpretacion.append("    - Indica: Daño renal tubular")
            interpretacion.append("    - Tipos:")
            interpretacion.append("      * Hialinos: Normales en pequeña cantidad")
            interpretacion.append("      * Granulosos: Daño tubular")
            interpretacion.append("      * Leucocitarios: Pielonefritis")
            interpretacion.append("      * Eritrocitarios: Glomerulonefritis")
            interpretacion.append("    - Requiere: Evaluación nefrológica")
        
        # Células epiteliales
        if 'celulas_epiteliales' in parametros:
            interpretacion.append("\n📌 CÉLULAS EPITELIALES:")
            interpretacion.append("  • Células epiteliales aumentadas")
            interpretacion.append("    - Puede indicar: Contaminación de muestra")
            interpretacion.append("    - Recomendación: Repetir con técnica de recolección adecuada")
        
        return "\n".join(interpretacion)


# Singleton
_analizador = None

def get_analizador() -> AnalizadorLaboratorio:
    """Obtiene instancia del analizador"""
    global _analizador
    if _analizador is None:
        _analizador = AnalizadorLaboratorio()
    return _analizador
