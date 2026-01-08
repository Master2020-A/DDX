"""
Catálogo completo de análisis de laboratorio clínico
Incluye rangos de referencia por sexo y edad (adultos y pediátricos)
Basado en estándares internacionales y guías clínicas
"""

# ============================================================================
# HEMATOLOGÍA - BIOMETRÍA HEMÁTICA COMPLETA
# ============================================================================

BIOMETRIA_HEMATICA = {
    'nombre': 'Biometría Hemática Completa (Hemograma)',
    'area': 'hematologia',
    'tipo_prueba': 'biometria_hematica',
    'descripcion': 'Evaluación completa de células sanguíneas',
    'indicaciones': [
        'Evaluación de anemia',
        'Sospecha de infección',
        'Trastornos de coagulación',
        'Seguimiento de tratamientos',
        'Chequeo de rutina'
    ],
    'preparacion': 'No requiere ayuno',
    'parametros': {
        # SERIE ROJA
        'hemoglobina': {
            'nombre_completo': 'Hemoglobina',
            'abreviatura': 'Hb',
            'unidad': 'g/dL',
            'descripcion': 'Proteína que transporta oxígeno en la sangre',
            'rangos': {
                'hombre_adulto': {'min': 13.5, 'max': 17.5, 'critico_bajo': 7.0, 'critico_alto': 20.0},
                'mujer_adulta': {'min': 12.0, 'max': 16.0, 'critico_bajo': 7.0, 'critico_alto': 20.0},
                'mujer_embarazada': {'min': 10.5, 'max': 14.0, 'critico_bajo': 7.0, 'critico_alto': 20.0},
                'recien_nacido': {'min': 14.0, 'max': 24.0},
                'nino_1_12_anos': {'min': 11.0, 'max': 16.0},
                'adolescente': {'min': 12.0, 'max': 16.0}
            },
            'interpretacion': {
                'bajo': 'Anemia - evaluar tipo (microcítica, macrocítica, normocítica)',
                'alto': 'Policitemia - deshidratación, hipoxia crónica, policitemia vera'
            }
        },
        'hematocrito': {
            'nombre_completo': 'Hematocrito',
            'abreviatura': 'Hto',
            'unidad': '%',
            'descripcion': 'Porcentaje de volumen de eritrocitos en sangre',
            'rangos': {
                'hombre_adulto': {'min': 40.0, 'max': 54.0, 'critico_bajo': 20.0, 'critico_alto': 60.0},
                'mujer_adulta': {'min': 36.0, 'max': 46.0, 'critico_bajo': 20.0, 'critico_alto': 60.0},
                'mujer_embarazada': {'min': 32.0, 'max': 42.0},
                'recien_nacido': {'min': 45.0, 'max': 65.0},
                'nino_1_12_anos': {'min': 33.0, 'max': 47.0}
            }
        },
        'eritrocitos': {
            'nombre_completo': 'Eritrocitos (Glóbulos Rojos)',
            'abreviatura': 'RBC',
            'unidad': 'millones/μL',
            'descripcion': 'Células que transportan oxígeno',
            'rangos': {
                'hombre_adulto': {'min': 4.5, 'max': 5.9, 'critico_bajo': 2.5, 'critico_alto': 7.0},
                'mujer_adulta': {'min': 4.0, 'max': 5.2, 'critico_bajo': 2.5, 'critico_alto': 7.0},
                'recien_nacido': {'min': 4.8, 'max': 7.1},
                'nino_1_12_anos': {'min': 4.0, 'max': 5.5}
            }
        },
        
        # ÍNDICES ERITROCITARIOS
        'vcm': {
            'nombre_completo': 'Volumen Corpuscular Medio',
            'abreviatura': 'VCM/MCV',
            'unidad': 'fL',
            'descripcion': 'Tamaño promedio de los eritrocitos',
            'rangos': {
                'adulto': {'min': 80.0, 'max': 100.0},
                'recien_nacido': {'min': 95.0, 'max': 125.0},
                'nino_1_12_anos': {'min': 78.0, 'max': 92.0}
            },
            'interpretacion': {
                'bajo': 'Microcitosis - anemia ferropénica, talasemia',
                'alto': 'Macrocitosis - deficiencia B12/folato, alcoholismo, hipotiroidismo'
            }
        },
        'hcm': {
            'nombre_completo': 'Hemoglobina Corpuscular Media',
            'abreviatura': 'HCM/MCH',
            'unidad': 'pg',
            'descripcion': 'Cantidad promedio de Hb por eritrocito',
            'rangos': {
                'adulto': {'min': 27.0, 'max': 31.0},
                'recien_nacido': {'min': 30.0, 'max': 38.0},
                'nino_1_12_anos': {'min': 26.0, 'max': 30.0}
            }
        },
        'chcm': {
            'nombre_completo': 'Concentración de Hemoglobina Corpuscular Media',
            'abreviatura': 'CHCM/MCHC',
            'unidad': 'g/dL',
            'descripcion': 'Concentración de Hb en eritrocitos',
            'rangos': {
                'adulto': {'min': 32.0, 'max': 36.0},
                'pediatrico': {'min': 32.0, 'max': 36.0}
            }
        },
        'rdw': {
            'nombre_completo': 'Amplitud de Distribución Eritrocitaria',
            'abreviatura': 'RDW',
            'unidad': '%',
            'descripcion': 'Variación en tamaño de eritrocitos (anisocitosis)',
            'rangos': {
                'adulto': {'min': 11.5, 'max': 14.5},
                'pediatrico': {'min': 11.5, 'max': 14.5}
            },
            'interpretacion': {
                'alto': 'Anisocitosis - anemia ferropénica, deficiencia B12, hemoglobinopatías'
            }
        },
        
        # SERIE BLANCA
        'leucocitos': {
            'nombre_completo': 'Leucocitos (Glóbulos Blancos)',
            'abreviatura': 'WBC',
            'unidad': 'x10³/μL',
            'descripcion': 'Células de defensa del organismo',
            'rangos': {
                'adulto': {'min': 4.0, 'max': 11.0, 'critico_bajo': 2.0, 'critico_alto': 30.0},
                'recien_nacido': {'min': 9.0, 'max': 30.0},
                'nino_1_12_anos': {'min': 5.0, 'max': 15.0},
                'mujer_embarazada': {'min': 6.0, 'max': 16.0}
            },
            'interpretacion': {
                'bajo': 'Leucopenia - infección viral, medicamentos, enfermedades autoinmunes',
                'alto': 'Leucocitosis - infección bacteriana, inflamación, leucemia'
            }
        },
        
        # DIFERENCIAL LEUCOCITARIO (%)
        'neutrofilos': {
            'nombre_completo': 'Neutrófilos',
            'abreviatura': 'NEU',
            'unidad': '%',
            'descripcion': 'Principal defensa contra bacterias',
            'rangos': {
                'adulto': {'min': 40.0, 'max': 70.0},
                'recien_nacido': {'min': 40.0, 'max': 80.0},
                'nino_1_12_anos': {'min': 20.0, 'max': 50.0}
            }
        },
        'linfocitos': {
            'nombre_completo': 'Linfocitos',
            'abreviatura': 'LINF',
            'unidad': '%',
            'descripcion': 'Defensa contra virus y producción de anticuerpos',
            'rangos': {
                'adulto': {'min': 20.0, 'max': 40.0},
                'recien_nacido': {'min': 10.0, 'max': 30.0},
                'nino_1_12_anos': {'min': 30.0, 'max': 60.0}
            }
        },
        'monocitos': {
            'nombre_completo': 'Monocitos',
            'abreviatura': 'MONO',
            'unidad': '%',
            'descripcion': 'Fagocitos que eliminan células muertas',
            'rangos': {
                'adulto': {'min': 2.0, 'max': 10.0},
                'pediatrico': {'min': 2.0, 'max': 10.0}
            }
        },
        'eosinofilos': {
            'nombre_completo': 'Eosinófilos',
            'abreviatura': 'EOS',
            'unidad': '%',
            'descripcion': 'Relacionados con alergias y parásitos',
            'rangos': {
                'adulto': {'min': 1.0, 'max': 6.0},
                'pediatrico': {'min': 1.0, 'max': 6.0}
            }
        },
        'basofilos': {
            'nombre_completo': 'Basófilos',
            'abreviatura': 'BASO',
            'unidad': '%',
            'descripcion': 'Relacionados con reacciones alérgicas',
            'rangos': {
                'adulto': {'min': 0.0, 'max': 2.0},
                'pediatrico': {'min': 0.0, 'max': 2.0}
            }
        },
        
        # VALORES ABSOLUTOS DE LEUCOCITOS
        'neutrofilos_abs': {
            'nombre_completo': 'Neutrófilos Absolutos',
            'abreviatura': 'NEU#',
            'unidad': 'x10³/μL',
            'descripcion': 'Recuento absoluto de neutrófilos',
            'rangos': {
                'adulto': {'min': 1.8, 'max': 7.7, 'critico_bajo': 0.5, 'critico_alto': 20.0},
                'nino_1_12_anos': {'min': 1.0, 'max': 8.0}
            }
        },
        'linfocitos_abs': {
            'nombre_completo': 'Linfocitos Absolutos',
            'abreviatura': 'LINF#',
            'unidad': 'x10³/μL',
            'descripcion': 'Recuento absoluto de linfocitos',
            'rangos': {
                'adulto': {'min': 1.0, 'max': 4.8, 'critico_bajo': 0.5},
                'nino_1_12_anos': {'min': 1.5, 'max': 6.0}
            }
        },
        'monocitos_abs': {
            'nombre_completo': 'Monocitos Absolutos',
            'abreviatura': 'MONO#',
            'unidad': 'x10³/μL',
            'rangos': {
                'adulto': {'min': 0.2, 'max': 1.0},
                'pediatrico': {'min': 0.2, 'max': 1.0}
            }
        },
        'eosinofilos_abs': {
            'nombre_completo': 'Eosinófilos Absolutos',
            'abreviatura': 'EOS#',
            'unidad': 'x10³/μL',
            'rangos': {
                'adulto': {'min': 0.0, 'max': 0.7},
                'pediatrico': {'min': 0.0, 'max': 0.7}
            }
        },
        'basofilos_abs': {
            'nombre_completo': 'Basófilos Absolutos',
            'abreviatura': 'BASO#',
            'unidad': 'x10³/μL',
            'rangos': {
                'adulto': {'min': 0.0, 'max': 0.2},
                'pediatrico': {'min': 0.0, 'max': 0.2}
            }
        },
        
        # DIFERENCIAL DETALLADO
        'bandas': {
            'nombre_completo': 'Neutrófilos en Banda (Cayados)',
            'abreviatura': 'BAND',
            'unidad': '%',
            'descripcion': 'Neutrófilos inmaduros',
            'rangos': {
                'adulto': {'min': 0.0, 'max': 3.0},
                'pediatrico': {'min': 0.0, 'max': 5.0}
            },
            'interpretacion': {
                'alto': 'Desviación a la izquierda - infección bacteriana severa'
            }
        },
        'segmentados': {
            'nombre_completo': 'Neutrófilos Segmentados',
            'abreviatura': 'SEG',
            'unidad': '%',
            'descripcion': 'Neutrófilos maduros',
            'rangos': {
                'adulto': {'min': 40.0, 'max': 70.0},
                'pediatrico': {'min': 35.0, 'max': 65.0}
            }
        },
        
        # PLAQUETAS
        'plaquetas': {
            'nombre_completo': 'Plaquetas (Trombocitos)',
            'abreviatura': 'PLT',
            'unidad': 'x10³/μL',
            'descripcion': 'Células de coagulación',
            'rangos': {
                'adulto': {'min': 150.0, 'max': 450.0, 'critico_bajo': 50.0, 'critico_alto': 1000.0},
                'recien_nacido': {'min': 150.0, 'max': 450.0},
                'mujer_embarazada': {'min': 100.0, 'max': 400.0}
            },
            'interpretacion': {
                'bajo': 'Trombocitopenia - riesgo de sangrado',
                'alto': 'Trombocitosis - riesgo de trombosis'
            }
        },
        'vpm': {
            'nombre_completo': 'Volumen Plaquetario Medio',
            'abreviatura': 'VPM/MPV',
            'unidad': 'fL',
            'descripcion': 'Tamaño promedio de plaquetas',
            'rangos': {
                'adulto': {'min': 7.5, 'max': 11.5},
                'pediatrico': {'min': 7.0, 'max': 11.0}
            }
        }
    }
}

# ============================================================================
# QUÍMICA CLÍNICA - GLUCOSA
# ============================================================================

GLUCOSA = {
    'nombre': 'Glucosa en Ayunas',
    'area': 'quimica_clinica',
    'tipo_prueba': 'glucosa',
    'descripcion': 'Medición de azúcar en sangre',
    'indicaciones': ['Diagnóstico de diabetes', 'Control metabólico', 'Hipoglucemia'],
    'preparacion': 'Ayuno de 8-12 horas',
    'parametros': {
        'glucosa': {
            'nombre_completo': 'Glucosa en Ayunas',
            'abreviatura': 'GLU',
            'unidad': 'mg/dL',
            'descripcion': 'Nivel de azúcar en sangre',
            'rangos': {
                'adulto': {'min': 70.0, 'max': 100.0, 'critico_bajo': 40.0, 'critico_alto': 500.0},
                'nino': {'min': 60.0, 'max': 100.0, 'critico_bajo': 40.0}
            },
            'interpretacion': {
                'bajo': 'Hipoglucemia - requiere atención inmediata',
                'alto_100_125': 'Prediabetes - glucosa alterada en ayunas',
                'alto_126_199': 'Diabetes mellitus (confirmar con segunda medición)',
                'alto_200': 'Diabetes mellitus - criterio diagnóstico'
            },
            'notas': [
                '< 100 mg/dL: Normal',
                '100-125 mg/dL: Prediabetes',
                '≥ 126 mg/dL: Diabetes (2 mediciones)',
                '≥ 200 mg/dL: Diabetes (con síntomas)'
            ]
        }
    }
}

# ============================================================================
# QUÍMICA CLÍNICA - FUNCIÓN RENAL
# ============================================================================

FUNCION_RENAL = {
    'nombre': 'Perfil de Función Renal',
    'area': 'quimica_clinica',
    'tipo_prueba': 'funcion_renal',
    'descripcion': 'Evaluación de la función de los riñones',
    'indicaciones': ['Enfermedad renal', 'Hipertensión', 'Diabetes', 'Control de medicamentos'],
    'preparacion': 'Ayuno de 8 horas recomendado',
    'parametros': {
        'creatinina': {
            'nombre_completo': 'Creatinina Sérica',
            'abreviatura': 'CREAT',
            'unidad': 'mg/dL',
            'descripcion': 'Producto de desecho muscular, indicador de función renal',
            'rangos': {
                'hombre_adulto': {'min': 0.7, 'max': 1.3, 'critico_alto': 5.0},
                'mujer_adulta': {'min': 0.6, 'max': 1.1, 'critico_alto': 5.0},
                'nino_1_12_anos': {'min': 0.3, 'max': 0.7}
            },
            'interpretacion': {
                'alto': 'Función renal disminuida - calcular TFG (Tasa de Filtración Glomerular)'
            },
            'notas': [
                'TFG >90: Normal',
                'TFG 60-89: ERC Estadio 2 (leve)',
                'TFG 30-59: ERC Estadio 3 (moderada)',
                'TFG 15-29: ERC Estadio 4 (severa)',
                'TFG <15: ERC Estadio 5 (falla renal)'
            ]
        },
        'urea': {
            'nombre_completo': 'Urea (BUN)',
            'abreviatura': 'BUN',
            'unidad': 'mg/dL',
            'descripcion': 'Producto final del metabolismo de proteínas',
            'rangos': {
                'adulto': {'min': 15.0, 'max': 40.0, 'critico_alto': 100.0},
                'nino': {'min': 5.0, 'max': 18.0}
            },
            'interpretacion': {
                'alto': 'Azotemia - insuficiencia renal, deshidratación, dieta hiperproteica'
            }
        },
        'acido_urico': {
            'nombre_completo': 'Ácido Úrico',
            'abreviatura': 'UA',
            'unidad': 'mg/dL',
            'descripcion': 'Producto del metabolismo de purinas',
            'rangos': {
                'hombre_adulto': {'min': 3.4, 'max': 7.0},
                'mujer_adulta': {'min': 2.4, 'max': 6.0},
                'nino': {'min': 2.0, 'max': 5.5}
            },
            'interpretacion': {
                'alto': 'Hiperuricemia - riesgo de gota, litiasis renal'
            }
        }
    }
}

# ============================================================================
# QUÍMICA CLÍNICA - PERFIL LIPÍDICO
# ============================================================================

PERFIL_LIPIDICO = {
    'nombre': 'Perfil Lipídico (Lípidos en Sangre)',
    'area': 'quimica_clinica',
    'tipo_prueba': 'perfil_lipidico',
    'descripcion': 'Evaluación de grasas en sangre y riesgo cardiovascular',
    'indicaciones': ['Riesgo cardiovascular', 'Dislipidemia', 'Diabetes', 'Obesidad'],
    'preparacion': 'Ayuno de 12-14 horas obligatorio',
    'parametros': {
        'colesterol_total': {
            'nombre_completo': 'Colesterol Total',
            'abreviatura': 'COL',
            'unidad': 'mg/dL',
            'descripcion': 'Colesterol total en sangre',
            'rangos': {
                'adulto': {'min': 0.0, 'max': 200.0},
                'pediatrico': {'min': 0.0, 'max': 170.0}
            },
            'interpretacion': {
                'deseable': '< 200 mg/dL',
                'limite_alto': '200-239 mg/dL',
                'alto': '≥ 240 mg/dL - Riesgo cardiovascular aumentado'
            }
        },
        'trigliceridos': {
            'nombre_completo': 'Triglicéridos',
            'abreviatura': 'TG',
            'unidad': 'mg/dL',
            'descripcion': 'Grasa en sangre',
            'rangos': {
                'adulto': {'min': 0.0, 'max': 150.0, 'critico_alto': 500.0},
                'pediatrico': {'min': 0.0, 'max': 100.0}
            },
            'interpretacion': {
                'normal': '< 150 mg/dL',
                'limite_alto': '150-199 mg/dL',
                'alto': '200-499 mg/dL',
                'muy_alto': '≥ 500 mg/dL - Riesgo de pancreatitis aguda'
            }
        },
        'hdl': {
            'nombre_completo': 'Colesterol HDL (Bueno)',
            'abreviatura': 'HDL',
            'unidad': 'mg/dL',
            'descripcion': 'Lipoproteína de alta densidad - protector cardiovascular',
            'rangos': {
                'hombre_adulto': {'min': 40.0, 'max': 200.0},
                'mujer_adulta': {'min': 50.0, 'max': 200.0},
                'pediatrico': {'min': 40.0, 'max': 200.0}
            },
            'interpretacion': {
                'bajo': '< 40 mg/dL (hombres) o < 50 mg/dL (mujeres) - Factor de riesgo cardiovascular',
                'optimo': '≥ 60 mg/dL - Factor protector'
            }
        },
        'ldl': {
            'nombre_completo': 'Colesterol LDL (Malo)',
            'abreviatura': 'LDL',
            'unidad': 'mg/dL',
            'descripcion': 'Lipoproteína de baja densidad - principal factor de riesgo',
            'rangos': {
                'adulto': {'min': 0.0, 'max': 100.0},
                'pediatrico': {'min': 0.0, 'max': 110.0}
            },
            'interpretacion': {
                'optimo': '< 100 mg/dL',
                'casi_optimo': '100-129 mg/dL',
                'limite_alto': '130-159 mg/dL',
                'alto': '160-189 mg/dL',
                'muy_alto': '≥ 190 mg/dL'
            },
            'notas': [
                'Meta en riesgo alto: < 70 mg/dL',
                'Meta en riesgo moderado: < 100 mg/dL',
                'Meta en riesgo bajo: < 130 mg/dL'
            ]
        },
        'vldl': {
            'nombre_completo': 'Colesterol VLDL',
            'abreviatura': 'VLDL',
            'unidad': 'mg/dL',
            'descripcion': 'Lipoproteína de muy baja densidad',
            'rangos': {
                'adulto': {'min': 5.0, 'max': 40.0}
            }
        }
    }
}

# ============================================================================
# QUÍMICA CLÍNICA - FUNCIÓN HEPÁTICA
# ============================================================================

FUNCION_HEPATICA = {
    'nombre': 'Perfil de Función Hepática (Pruebas Hepáticas)',
    'area': 'quimica_clinica',
    'tipo_prueba': 'funcion_hepatica',
    'descripcion': 'Evaluación de la función del hígado',
    'indicaciones': ['Enfermedad hepática', 'Ictericia', 'Hepatitis', 'Alcoholismo', 'Medicamentos hepatotóxicos'],
    'preparacion': 'Ayuno de 8 horas',
    'parametros': {
        'tgo': {
            'nombre_completo': 'Transaminasa Glutámico Oxalacética (AST)',
            'abreviatura': 'TGO/AST',
            'unidad': 'U/L',
            'descripcion': 'Enzima presente en hígado, corazón y músculo',
            'rangos': {
                'adulto': {'min': 5.0, 'max': 40.0, 'critico_alto': 1000.0},
                'pediatrico': {'min': 15.0, 'max': 60.0}
            },
            'interpretacion': {
                'alto_leve': '40-100 U/L - Esteatosis, hepatitis crónica',
                'alto_moderado': '100-300 U/L - Hepatitis aguda, medicamentos',
                'alto_severo': '300-1000 U/L - Hepatitis aguda severa',
                'alto_masivo': '> 1000 U/L - Hepatitis fulminante, isquemia hepática, toxicidad'
            },
            'notas': [
                'Ratio TGO/TGP > 2: Hepatopatía alcohólica',
                'Ratio TGO/TGP < 1: Hepatitis viral o NASH'
            ]
        },
        'tgp': {
            'nombre_completo': 'Transaminasa Glutámico Pirúvica (ALT)',
            'abreviatura': 'TGP/ALT',
            'unidad': 'U/L',
            'descripcion': 'Enzima más específica de hígado',
            'rangos': {
                'adulto': {'min': 7.0, 'max': 56.0, 'critico_alto': 1000.0},
                'pediatrico': {'min': 10.0, 'max': 40.0}
            },
            'interpretacion': {
                'alto': 'Daño hepático - más específico que TGO'
            }
        },
        'bilirrubina_total': {
            'nombre_completo': 'Bilirrubina Total',
            'abreviatura': 'BT',
            'unidad': 'mg/dL',
            'descripcion': 'Pigmento producto de degradación de hemoglobina',
            'rangos': {
                'adulto': {'min': 0.1, 'max': 1.2, 'critico_alto': 12.0},
                'recien_nacido': {'min': 0.0, 'max': 12.0}
            },
            'interpretacion': {
                'alto': 'Ictericia - enfermedad hepática, hemólisis, obstrucción biliar'
            }
        },
        'bilirrubina_directa': {
            'nombre_completo': 'Bilirrubina Directa (Conjugada)',
            'abreviatura': 'BD',
            'unidad': 'mg/dL',
            'descripcion': 'Bilirrubina procesada por el hígado',
            'rangos': {
                'adulto': {'min': 0.0, 'max': 0.3}
            }
        },
        'bilirrubina_indirecta': {
            'nombre_completo': 'Bilirrubina Indirecta (No Conjugada)',
            'abreviatura': 'BI',
            'unidad': 'mg/dL',
            'descripcion': 'Bilirrubina antes de procesarse',
            'rangos': {
                'adulto': {'min': 0.1, 'max': 0.9}
            }
        },
        'fosfatasa_alcalina': {
            'nombre_completo': 'Fosfatasa Alcalina',
            'abreviatura': 'FA/ALP',
            'unidad': 'U/L',
            'descripcion': 'Enzima presente en hígado, hueso y otros tejidos',
            'rangos': {
                'adulto': {'min': 30.0, 'max': 120.0},
                'nino_crecimiento': {'min': 100.0, 'max': 400.0}
            },
            'interpretacion': {
                'alto': 'Colestasis, enfermedad ósea, obstrucción biliar'
            }
        },
        'ggt': {
            'nombre_completo': 'Gamma Glutamil Transferasa',
            'abreviatura': 'GGT',
            'unidad': 'U/L',
            'descripcion': 'Enzima sensible a alcohol y medicamentos',
            'rangos': {
                'hombre_adulto': {'min': 8.0, 'max': 61.0},
                'mujer_adulta': {'min': 5.0, 'max': 36.0}
            },
            'interpretacion': {
                'alto': 'Alcoholismo, medicamentos, colestasis'
            }
        },
        'albumina': {
            'nombre_completo': 'Albúmina Sérica',
            'abreviatura': 'ALB',
            'unidad': 'g/dL',
            'descripcion': 'Principal proteína producida por el hígado',
            'rangos': {
                'adulto': {'min': 3.5, 'max': 5.0, 'critico_bajo': 2.0},
                'pediatrico': {'min': 3.8, 'max': 5.4}
            },
            'interpretacion': {
                'bajo': 'Enfermedad hepática crónica, desnutrición, síndrome nefrótico'
            }
        },
        'proteinas_totales': {
            'nombre_completo': 'Proteínas Totales',
            'abreviatura': 'PT',
            'unidad': 'g/dL',
            'descripcion': 'Suma de albúmina y globulinas',
            'rangos': {
                'adulto': {'min': 6.0, 'max': 8.3},
                'pediatrico': {'min': 6.2, 'max': 8.0}
            }
        },
        'globulinas': {
            'nombre_completo': 'Globulinas',
            'abreviatura': 'GLOB',
            'unidad': 'g/dL',
            'descripcion': 'Proteínas incluyendo anticuerpos',
            'rangos': {
                'adulto': {'min': 2.0, 'max': 3.5}
            }
        }
    }
}

# ============================================================================
# ELECTROLITOS Y GASES
# ============================================================================

ELECTROLITOS = {
    'nombre': 'Electrolitos Séricos',
    'area': 'quimica_clinica',
    'tipo_prueba': 'electrolitos',
    'descripcion': 'Minerales esenciales en sangre',
    'parametros': {
        'sodio': {
            'nombre_completo': 'Sodio',
            'abreviatura': 'Na+',
            'unidad': 'mEq/L',
            'rangos': {
                'adulto': {'min': 136.0, 'max': 145.0, 'critico_bajo': 120.0, 'critico_alto': 160.0},
                'pediatrico': {'min': 135.0, 'max': 145.0}
            },
            'interpretacion': {
                'bajo': 'Hiponatremia - deshidratación, SIADH, insuficiencia renal',
                'alto': 'Hipernatremia - deshidratación, diabetes insípida'
            }
        },
        'potasio': {
            'nombre_completo': 'Potasio',
            'abreviatura': 'K+',
            'unidad': 'mEq/L',
            'rangos': {
                'adulto': {'min': 3.5, 'max': 5.0, 'critico_bajo': 2.5, 'critico_alto': 6.5},
                'pediatrico': {'min': 3.5, 'max': 5.0}
            },
            'interpretacion': {
                'bajo': 'Hipopotasemia - arritmias, debilidad muscular',
                'alto': 'Hiperpotasemia - arritmias cardíacas GRAVES'
            }
        },
        'cloro': {
            'nombre_completo': 'Cloro',
            'abreviatura': 'Cl-',
            'unidad': 'mEq/L',
            'rangos': {
                'adulto': {'min': 98.0, 'max': 107.0}
            }
        },
        'calcio': {
            'nombre_completo': 'Calcio Total',
            'abreviatura': 'Ca',
            'unidad': 'mg/dL',
            'rangos': {
                'adulto': {'min': 8.5, 'max': 10.5, 'critico_bajo': 6.0, 'critico_alto': 13.0},
                'pediatrico': {'min': 8.8, 'max': 11.0}
            }
        },
        'magnesio': {
            'nombre_completo': 'Magnesio',
            'abreviatura': 'Mg',
            'unidad': 'mg/dL',
            'rangos': {
                'adulto': {'min': 1.7, 'max': 2.2}
            }
        },
        'fosforo': {
            'nombre_completo': 'Fósforo',
            'abreviatura': 'P',
            'unidad': 'mg/dL',
            'rangos': {
                'adulto': {'min': 2.5, 'max': 4.5},
                'pediatrico': {'min': 4.0, 'max': 7.0}
            }
        }
    }
}

# ============================================================================
# INMUNOLOGÍA
# ============================================================================

MARCADORES_INFLAMATORIOS = {
    'nombre': 'Marcadores Inflamatorios',
    'area': 'inmunologia',
    'tipo_prueba': 'marcadores_inflamatorios',
    'parametros': {
        'proteina_c_reactiva': {
            'nombre_completo': 'Proteína C Reactiva',
            'abreviatura': 'PCR',
            'unidad': 'mg/dL',
            'rangos': {
                'adulto': {'min': 0.0, 'max': 0.5, 'critico_alto': 10.0}
            },
            'interpretacion': {
                'alto': 'Inflamación activa - infección, trauma, enfermedad autoinmune'
            }
        },
        'vsg': {
            'nombre_completo': 'Velocidad de Sedimentación Globular',
            'abreviatura': 'VSG/ESR',
            'unidad': 'mm/h',
            'rangos': {
                'hombre_adulto': {'min': 0.0, 'max': 15.0},
                'mujer_adulta': {'min': 0.0, 'max': 20.0},
                'pediatrico': {'min': 0.0, 'max': 10.0}
            }
        }
    }
}

# ============================================================================
# CATÁLOGO COMPLETO
# ============================================================================

CATALOGO_COMPLETO = {
    'hematologia': {
        'biometria_hematica': BIOMETRIA_HEMATICA,
    },
    'quimica_clinica': {
        'glucosa': GLUCOSA,
        'funcion_renal': FUNCION_RENAL,
        'perfil_lipidico': PERFIL_LIPIDICO,
        'funcion_hepatica': FUNCION_HEPATICA,
        'electrolitos': ELECTROLITOS,
    },
    'inmunologia': {
        'marcadores_inflamatorios': MARCADORES_INFLAMATORIOS,
    }
}

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def obtener_rango_apropiado(parametro_info: dict, sexo: str = None, edad_anos: int = None) -> dict:
    """
    Obtiene el rango de referencia apropiado según sexo y edad
    
    Args:
        parametro_info: Información del parámetro del catálogo
        sexo: 'M' o 'F'
        edad_anos: Edad en años
        
    Returns:
        dict con min, max, critico_bajo, critico_alto
    """
    rangos = parametro_info.get('rangos', {})
    
    # Determinar categoría de edad
    if edad_anos is not None:
        if edad_anos < 1/365:  # Recién nacido (< 1 día)
            if 'recien_nacido' in rangos:
                return rangos['recien_nacido']
        elif edad_anos < 1:  # Menor de 1 año
            if 'lactante' in rangos:
                return rangos['lactante']
        elif edad_anos < 12:  # 1-12 años
            if 'nino_1_12_anos' in rangos:
                return rangos['nino_1_12_anos']
        elif edad_anos < 18:  # 12-18 años
            if 'adolescente' in rangos:
                return rangos['adolescente']
    
    # Rangos por sexo en adultos
    if sexo == 'M' and 'hombre_adulto' in rangos:
        return rangos['hombre_adulto']
    elif sexo == 'F' and 'mujer_adulta' in rangos:
        return rangos['mujer_adulta']
    
    # Rango genérico
    if 'adulto' in rangos:
        return rangos['adulto']
    if 'pediatrico' in rangos:
        return rangos['pediatrico']
    
    # Retornar el primer rango disponible
    return list(rangos.values())[0] if rangos else {}


def obtener_parametros_por_tipo(area: str, tipo_prueba: str) -> dict:
    """
    Obtiene todos los parámetros de un tipo de prueba específico
    """
    if area in CATALOGO_COMPLETO and tipo_prueba in CATALOGO_COMPLETO[area]:
        return CATALOGO_COMPLETO[area][tipo_prueba]['parametros']
    return {}


def listar_todos_parametros() -> list:
    """
    Lista todos los parámetros disponibles en el catálogo
    """
    parametros = []
    for area, tipos in CATALOGO_COMPLETO.items():
        for tipo, info in tipos.items():
            for param_key, param_info in info['parametros'].items():
                parametros.append({
                    'area': area,
                    'tipo_prueba': tipo,
                    'parametro': param_key,
                    'nombre': param_info['nombre_completo'],
                    'unidad': param_info['unidad']
                })
    return parametros
