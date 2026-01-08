"""
Generador de PDFs para Estudios Especiales (EKG, EEG, Ecografías)
Genera dos tipos de reportes:
1. Reporte de Análisis (parámetros extraídos)
2. Reporte de Interpretación (diagnóstico de IA)
"""
import os
from io import BytesIO
from datetime import datetime
from typing import Dict, Any, Optional

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ ReportLab no disponible - PDFs deshabilitados")


class GeneradorPDFEstudiosEspeciales:
    """Generador de reportes PDF para estudios especiales"""

    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab no está instalado. Instalar con: pip install reportlab")

        self.styles = getSampleStyleSheet()
        self._crear_estilos_personalizados()
    
    def _limpiar_texto(self, texto: str) -> str:
        """Limpiar y escapar texto para ReportLab"""
        if not texto:
            return "N/A"
        
        # Convertir a string si no lo es
        texto = str(texto)
        
        # IMPORTANTE: Primero escapar & antes que los demás
        texto = texto.replace('&', '&amp;')
        texto = texto.replace('<', '&lt;')
        texto = texto.replace('>', '&gt;')
        
        # Reemplazar saltos de línea por espacios (no <br/> porque causa problemas)
        texto = texto.replace('\n', ' ')
        texto = texto.replace('\r', ' ')
        
        # Eliminar espacios múltiples
        import re
        texto = re.sub(r'\s+', ' ', texto)
        texto = texto.strip()
        
        return texto

    def _crear_estilos_personalizados(self):
        """Crear estilos personalizados para los reportes"""
        
        # Título principal
        self.styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=self.styles['Title'],
            fontSize=20,
            alignment=TA_CENTER,
            spaceAfter=30,
            textColor=colors.HexColor('#1e40af'),
            fontName='Helvetica-Bold'
        ))

        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading1'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=colors.HexColor('#3b82f6')
        ))

        # Sección
        self.styles.add(ParagraphStyle(
            name='Seccion',
            parent=self.styles['Heading2'],
            fontSize=14,
            alignment=TA_LEFT,
            spaceAfter=12,
            spaceBefore=15,
            textColor=colors.HexColor('#1f2937'),
            fontName='Helvetica-Bold'
        ))

        # Texto normal
        self.styles.add(ParagraphStyle(
            name='TextoNormal',
            parent=self.styles['BodyText'],
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=8,
            textColor=colors.HexColor('#374151')
        ))

        # Texto justificado
        self.styles.add(ParagraphStyle(
            name='TextoJustificado',
            parent=self.styles['BodyText'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=10,
            textColor=colors.HexColor('#111827')
        ))

        # Alerta
        self.styles.add(ParagraphStyle(
            name='Alerta',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_LEFT,
            spaceAfter=10,
            textColor=colors.HexColor('#dc2626'),
            fontName='Helvetica-Bold'
        ))

        # Éxito
        self.styles.add(ParagraphStyle(
            name='Exito',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_LEFT,
            spaceAfter=10,
            textColor=colors.HexColor('#16a34a'),
            fontName='Helvetica-Bold'
        ))

    def _crear_encabezado(self, tipo_estudio: str, tipo_reporte: str) -> list:
        """Crear encabezado del reporte"""
        elementos = []
        
        # Logo/Título del sistema
        elementos.append(Paragraph(
            "🏥 SISTEMA DDX - DIAGNÓSTICO DIFERENCIAL",
            self.styles['TituloPrincipal']
        ))
        
        # Tipo de estudio
        elementos.append(Paragraph(
            f"REPORTE DE {tipo_estudio.upper()}",
            self.styles['Subtitulo']
        ))
        
        # Tipo de reporte
        elementos.append(Paragraph(
            f"<i>{tipo_reporte}</i>",
            self.styles['TextoNormal']
        ))
        
        elementos.append(Spacer(1, 20))
        
        return elementos

    def _crear_info_paciente(self, datos_paciente: Dict[str, Any]) -> list:
        """Crear sección de información del paciente"""
        elementos = []
        
        elementos.append(Paragraph("INFORMACIÓN DEL PACIENTE", self.styles['Seccion']))
        
        data = [
            ['Campo', 'Valor'],
            ['Nombre', datos_paciente.get('nombre_completo', 'N/A')],
            ['Edad', f"{datos_paciente.get('edad', 'N/A')} años"],
            ['Sexo', datos_paciente.get('sexo', 'N/A')],
            ['Fecha del Estudio', datos_paciente.get('fecha_estudio', 'N/A')],
            ['Médico', datos_paciente.get('medico', 'N/A')],
        ]
        
        tabla = Table(data, colWidths=[2*inch, 4*inch])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')])
        ]))
        
        elementos.append(tabla)
        elementos.append(Spacer(1, 20))
        
        return elementos

    def _crear_pie_pagina(self) -> list:
        """Crear pie de página"""
        elementos = []
        
        elementos.append(Spacer(1, 30))
        elementos.append(Paragraph(
            f"<i>Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')}</i>",
            self.styles['TextoNormal']
        ))
        elementos.append(Paragraph(
            "<i>Este reporte fue generado automáticamente por el Sistema DDX</i>",
            self.styles['TextoNormal']
        ))
        
        return elementos

    # ==================== REPORTES DE EKG ====================

    def generar_reporte_analisis_ekg(self, datos: Dict[str, Any]) -> BytesIO:
        """Generar reporte de análisis de EKG (parámetros extraídos)"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )

        elementos = []

        # Encabezado
        elementos.extend(self._crear_encabezado("EKG", "Análisis de Parámetros"))

        # Información del paciente
        elementos.extend(self._crear_info_paciente(datos.get('paciente', {})))

        # Parámetros medidos
        elementos.append(Paragraph("PARÁMETROS MEDIDOS", self.styles['Seccion']))

        parametros_data = [
            ['Parámetro', 'Valor', 'Rango Normal'],
            ['Frecuencia Cardíaca', f"{datos.get('frecuencia_cardiaca', 'N/A')} lpm", '60-100 lpm'],
            ['Intervalo PR', f"{datos.get('intervalo_pr', 'N/A')} ms", '120-200 ms'],
            ['Duración QRS', f"{datos.get('duracion_qrs', 'N/A')} ms", '80-120 ms'],
            ['Intervalo QT', f"{datos.get('intervalo_qt', 'N/A')} ms", '350-450 ms'],
            ['QTc (corregido)', f"{datos.get('intervalo_qtc', 'N/A')} ms", '<440 ms (♂) / <460 ms (♀)'],
            ['Eje QRS', f"{datos.get('eje_qrs', 'N/A')}°", '-30° a +90°'],
        ]

        tabla_parametros = Table(parametros_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
        tabla_parametros.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')])
        ]))

        elementos.append(tabla_parametros)
        elementos.append(Spacer(1, 20))

        # Morfología de ondas
        elementos.append(Paragraph("MORFOLOGÍA DE ONDAS", self.styles['Seccion']))

        morfologia_data = [
            ['Componente', 'Descripción'],
            ['Ritmo', (datos.get('ritmo') or 'N/A').title() if datos.get('ritmo') else 'N/A'],
            ['Onda P', (datos.get('onda_p') or 'N/A').title() if datos.get('onda_p') else 'N/A'],
            ['Complejo QRS', (datos.get('complejo_qrs') or 'N/A').title() if datos.get('complejo_qrs') else 'N/A'],
            ['Segmento ST', (datos.get('segmento_st') or 'N/A').title() if datos.get('segmento_st') else 'N/A'],
            ['Onda T', (datos.get('onda_t') or 'N/A').title() if datos.get('onda_t') else 'N/A'],
        ]

        tabla_morfologia = Table(morfologia_data, colWidths=[2*inch, 4*inch])
        tabla_morfologia.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')])
        ]))

        elementos.append(tabla_morfologia)
        elementos.append(Spacer(1, 20))

        # Nota
        elementos.append(Paragraph(
            "<b>Nota:</b> Este reporte contiene únicamente los parámetros medidos. "
            "Para el diagnóstico y recomendaciones, consulte el Reporte de Interpretación de IA.",
            self.styles['TextoJustificado']
        ))

        # Pie de página
        elementos.extend(self._crear_pie_pagina())

        doc.build(elementos)
        buffer.seek(0)
        return buffer

    def generar_reporte_interpretacion_ekg(self, datos: Dict[str, Any]) -> BytesIO:
        """Generar reporte de interpretación de EKG (diagnóstico de IA)"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )

        elementos = []

        # Encabezado
        elementos.extend(self._crear_encabezado("EKG", "Interpretación con Inteligencia Artificial"))

        # Información del paciente
        elementos.extend(self._crear_info_paciente(datos.get('paciente', {})))

        # Clasificación
        clasificacion = datos.get('clasificacion', 'Normal')
        requiere_atencion = datos.get('requiere_atencion', False)
        es_critico = datos.get('es_critico', False)

        elementos.append(Paragraph("CLASIFICACIÓN", self.styles['Seccion']))

        if es_critico:
            elementos.append(Paragraph(
                f"🚨 CRÍTICO: {clasificacion}",
                self.styles['Alerta']
            ))
        elif requiere_atencion:
            elementos.append(Paragraph(
                f"⚠️ REQUIERE ATENCIÓN: {clasificacion}",
                self.styles['Alerta']
            ))
        else:
            elementos.append(Paragraph(
                f"✅ {clasificacion}",
                self.styles['Exito']
            ))

        elementos.append(Spacer(1, 15))

        # Interpretación
        elementos.append(Paragraph("INTERPRETACIÓN", self.styles['Seccion']))
        interpretacion_raw = datos.get('interpretacion', 'No disponible')
        # Convertir a string y asegurar que no sea None
        if interpretacion_raw is None or interpretacion_raw == '':
            interpretacion_raw = 'No disponible'
        # CRÍTICO: Forzar que sea un string y reemplazar caracteres problemáticos
        texto_limpio = str(interpretacion_raw)
        # Escapar solo los caracteres que ReportLab necesita
        texto_limpio = texto_limpio.replace('&', '&amp;')
        texto_limpio = texto_limpio.replace('<', '&lt;')
        texto_limpio = texto_limpio.replace('>', '&gt;')
        # Crear el párrafo con el texto limpio
        elementos.append(Paragraph(texto_limpio, self.styles['TextoJustificado']))
        elementos.append(Spacer(1, 15))

        # Hallazgos
        hallazgos = datos.get('hallazgos', [])
        if hallazgos:
            elementos.append(Paragraph("HALLAZGOS DETECTADOS", self.styles['Seccion']))
            for i, hallazgo in enumerate(hallazgos, 1):
                elementos.append(Paragraph(
                    f"{i}. {str(hallazgo)}",
                    self.styles['TextoNormal']
                ))
            elementos.append(Spacer(1, 15))

        # Recomendaciones
        recomendaciones = datos.get('recomendaciones', [])
        if recomendaciones:
            elementos.append(Paragraph("RECOMENDACIONES", self.styles['Seccion']))
            for i, recomendacion in enumerate(recomendaciones, 1):
                elementos.append(Paragraph(
                    f"{i}. {str(recomendacion)}",
                    self.styles['TextoNormal']
                ))
            elementos.append(Spacer(1, 15))

        # Confianza de IA
        confianza = datos.get('confianza_ia', 0)
        elementos.append(Paragraph("NIVEL DE CONFIANZA DE IA", self.styles['Seccion']))
        elementos.append(Paragraph(
            f"Confianza: {confianza}%",
            self.styles['TextoNormal']
        ))
        elementos.append(Spacer(1, 15))

        # Disclaimer
        elementos.append(Paragraph(
            "<b>IMPORTANTE:</b> Esta interpretación fue generada por Inteligencia Artificial y debe ser "
            "validada por un médico especialista. No sustituye el criterio clínico profesional.",
            self.styles['Alerta']
        ))

        # Pie de página
        elementos.extend(self._crear_pie_pagina())

        doc.build(elementos)
        buffer.seek(0)
        return buffer

    # ==================== REPORTES DE EEG ====================

    def generar_reporte_analisis_eeg(self, datos: Dict[str, Any]) -> BytesIO:
        """Generar reporte de análisis de EEG (parámetros extraídos)"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )

        elementos = []

        # Encabezado
        elementos.extend(self._crear_encabezado("EEG", "Análisis de Parámetros"))

        # Información del paciente
        elementos.extend(self._crear_info_paciente(datos.get('paciente', {})))

        # Parámetros del estudio
        elementos.append(Paragraph("PARÁMETROS DEL ESTUDIO", self.styles['Seccion']))

        estudio_data = [
            ['Parámetro', 'Valor'],
            ['Tipo de Estudio', (datos.get('tipo_estudio') or 'N/A').title() if datos.get('tipo_estudio') else 'N/A'],
            ['Duración', f"{datos.get('duracion_minutos', 'N/A')} minutos"],
            ['Estado de Conciencia', (datos.get('estado_conciencia') or 'N/A').title() if datos.get('estado_conciencia') else 'N/A'],
            ['Cooperación', (datos.get('cooperacion_paciente') or 'N/A').title() if datos.get('cooperacion_paciente') else 'N/A'],
        ]

        tabla_estudio = Table(estudio_data, colWidths=[2.5*inch, 3.5*inch])
        tabla_estudio.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')])
        ]))

        elementos.append(tabla_estudio)
        elementos.append(Spacer(1, 20))

        # Actividad de fondo
        elementos.append(Paragraph("ACTIVIDAD DE FONDO", self.styles['Seccion']))

        fondo_data = [
            ['Parámetro', 'Valor', 'Rango Normal'],
            ['Actividad', (datos.get('actividad_fondo') or 'N/A').replace('_', ' ').title() if datos.get('actividad_fondo') else 'N/A', '-'],
            ['Frecuencia Dominante', f"{datos.get('frecuencia_dominante', 'N/A')} Hz", '8-13 Hz (Alfa)'],
            ['Amplitud Promedio', f"{datos.get('amplitud_promedio', 'N/A')} μV", '10-100 μV'],
            ['Simetría', (datos.get('simetria') or 'N/A').title() if datos.get('simetria') else 'N/A', 'Simétrica'],
        ]

        tabla_fondo = Table(fondo_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
        tabla_fondo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')])
        ]))

        elementos.append(tabla_fondo)
        elementos.append(Spacer(1, 20))

        # Ritmos cerebrales
        elementos.append(Paragraph("RITMOS CEREBRALES", self.styles['Seccion']))

        ritmos_data = [
            ['Ritmo', 'Estado', 'Frecuencia'],
            ['Delta (0.5-4 Hz)', (datos.get('ritmo_delta') or 'N/A').title() if datos.get('ritmo_delta') else 'N/A', '0.5-4 Hz'],
            ['Theta (4-8 Hz)', (datos.get('ritmo_theta') or 'N/A').title() if datos.get('ritmo_theta') else 'N/A', '4-8 Hz'],
            ['Alfa (8-13 Hz)', (datos.get('ritmo_alfa') or 'N/A').title() if datos.get('ritmo_alfa') else 'N/A', '8-13 Hz'],
            ['Beta (13-30 Hz)', (datos.get('ritmo_beta') or 'N/A').title() if datos.get('ritmo_beta') else 'N/A', '13-30 Hz'],
        ]

        tabla_ritmos = Table(ritmos_data, colWidths=[2*inch, 2*inch, 2*inch])
        tabla_ritmos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')])
        ]))

        elementos.append(tabla_ritmos)
        elementos.append(Spacer(1, 20))

        # Nota
        elementos.append(Paragraph(
            "<b>Nota:</b> Este reporte contiene únicamente los parámetros medidos. "
            "Para el diagnóstico y recomendaciones, consulte el Reporte de Interpretación de IA.",
            self.styles['TextoJustificado']
        ))

        # Pie de página
        elementos.extend(self._crear_pie_pagina())

        doc.build(elementos)
        buffer.seek(0)
        return buffer

    def generar_reporte_interpretacion_eeg(self, datos: Dict[str, Any]) -> BytesIO:
        """Generar reporte de interpretación de EEG (diagnóstico de IA)"""
        # Similar al de EKG pero adaptado para EEG
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )

        elementos = []

        # Encabezado
        elementos.extend(self._crear_encabezado("EEG", "Interpretación con Inteligencia Artificial"))

        # Información del paciente
        elementos.extend(self._crear_info_paciente(datos.get('paciente', {})))

        # Clasificación
        clasificacion = datos.get('clasificacion', 'Normal')
        requiere_atencion = datos.get('requiere_atencion', False)
        es_critico = datos.get('es_critico', False)

        elementos.append(Paragraph("CLASIFICACIÓN", self.styles['Seccion']))

        if es_critico:
            elementos.append(Paragraph(
                f"🚨 CRÍTICO: {clasificacion}",
                self.styles['Alerta']
            ))
        elif requiere_atencion:
            elementos.append(Paragraph(
                f"⚠️ REQUIERE ATENCIÓN: {clasificacion}",
                self.styles['Alerta']
            ))
        else:
            elementos.append(Paragraph(
                f"✅ {clasificacion}",
                self.styles['Exito']
            ))

        elementos.append(Spacer(1, 15))

        # Interpretación
        elementos.append(Paragraph("INTERPRETACIÓN", self.styles['Seccion']))
        interpretacion_raw = datos.get('interpretacion', 'No disponible')
        # Convertir a string y asegurar que no sea None
        if interpretacion_raw is None or interpretacion_raw == '':
            interpretacion_raw = 'No disponible'
        # CRÍTICO: Forzar que sea un string y reemplazar caracteres problemáticos
        texto_limpio = str(interpretacion_raw)
        # Escapar solo los caracteres que ReportLab necesita
        texto_limpio = texto_limpio.replace('&', '&amp;')
        texto_limpio = texto_limpio.replace('<', '&lt;')
        texto_limpio = texto_limpio.replace('>', '&gt;')
        # Crear el párrafo con el texto limpio
        elementos.append(Paragraph(texto_limpio, self.styles['TextoJustificado']))
        elementos.append(Spacer(1, 15))

        # Hallazgos
        hallazgos = datos.get('hallazgos', [])
        if hallazgos:
            elementos.append(Paragraph("HALLAZGOS DETECTADOS", self.styles['Seccion']))
            for i, hallazgo in enumerate(hallazgos, 1):
                elementos.append(Paragraph(
                    f"{i}. {str(hallazgo)}",
                    self.styles['TextoNormal']
                ))
            elementos.append(Spacer(1, 15))

        # Recomendaciones
        recomendaciones = datos.get('recomendaciones', [])
        if recomendaciones:
            elementos.append(Paragraph("RECOMENDACIONES", self.styles['Seccion']))
            for i, recomendacion in enumerate(recomendaciones, 1):
                elementos.append(Paragraph(
                    f"{i}. {str(recomendacion)}",
                    self.styles['TextoNormal']
                ))
            elementos.append(Spacer(1, 15))

        # Confianza de IA
        confianza = datos.get('confianza_ia', 0)
        elementos.append(Paragraph("NIVEL DE CONFIANZA DE IA", self.styles['Seccion']))
        elementos.append(Paragraph(
            f"Confianza: {confianza}%",
            self.styles['TextoNormal']
        ))

        # Disclaimer
        elementos.append(Spacer(1, 15))
        elementos.append(Paragraph(
            "<b>IMPORTANTE:</b> Esta interpretación fue generada por Inteligencia Artificial y debe ser "
            "validada por un médico especialista. No sustituye el criterio clínico profesional.",
            self.styles['Alerta']
        ))

        # Pie de página
        elementos.extend(self._crear_pie_pagina())

        doc.build(elementos)
        buffer.seek(0)
        return buffer

    # ==================== REPORTES DE ECOGRAFÍAS ====================

    def generar_reporte_analisis_ecografia(self, datos: Dict[str, Any]) -> BytesIO:
        """Generar reporte de análisis de Ecografía (parámetros extraídos)"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )

        elementos = []

        # Encabezado
        elementos.extend(self._crear_encabezado("ECOGRAFÍA", "Análisis de Parámetros"))

        # Información del paciente
        elementos.extend(self._crear_info_paciente(datos.get('paciente', {})))

        # Información técnica
        elementos.append(Paragraph("INFORMACIÓN TÉCNICA", self.styles['Seccion']))

        tecnica_data = [
            ['Parámetro', 'Valor'],
            ['Tipo de Ecografía', (datos.get('tipo_ecografia') or 'N/A').title() if datos.get('tipo_ecografia') else 'N/A'],
            ['Región Anatómica', datos.get('region_anatomica', 'N/A')],
            ['Modo', (datos.get('modo') or 'N/A').upper() if datos.get('modo') else 'N/A'],
            ['Vía de Acceso', (datos.get('via_acceso') or 'N/A').title() if datos.get('via_acceso') else 'N/A'],
            ['Transductor', datos.get('transductor', 'N/A')],
            ['Equipo', datos.get('equipo_utilizado', 'N/A')],
            ['Calidad del Estudio', (datos.get('calidad_estudio') or 'N/A').title() if datos.get('calidad_estudio') else 'N/A'],
        ]

        tabla_tecnica = Table(tecnica_data, colWidths=[2.5*inch, 3.5*inch])
        tabla_tecnica.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')])
        ]))

        elementos.append(tabla_tecnica)
        elementos.append(Spacer(1, 20))

        # Nota
        elementos.append(Paragraph(
            "<b>Nota:</b> Este reporte contiene únicamente los parámetros técnicos del estudio. "
            "Para el diagnóstico y recomendaciones, consulte el Reporte de Interpretación de IA.",
            self.styles['TextoJustificado']
        ))

        # Pie de página
        elementos.extend(self._crear_pie_pagina())

        doc.build(elementos)
        buffer.seek(0)
        return buffer

    def generar_reporte_interpretacion_ecografia(self, datos: Dict[str, Any]) -> BytesIO:
        """Generar reporte de interpretación de Ecografía (diagnóstico de IA)"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )

        elementos = []

        # Encabezado
        elementos.extend(self._crear_encabezado("ECOGRAFÍA", "Interpretación con Inteligencia Artificial"))

        # Información del paciente
        elementos.extend(self._crear_info_paciente(datos.get('paciente', {})))

        # Clasificación
        clasificacion = datos.get('clasificacion', 'Normal')
        requiere_atencion = datos.get('requiere_atencion', False)
        requiere_seguimiento = datos.get('requiere_seguimiento', False)

        elementos.append(Paragraph("CLASIFICACIÓN", self.styles['Seccion']))

        if requiere_atencion:
            elementos.append(Paragraph(
                f"⚠️ REQUIERE ATENCIÓN: {clasificacion}",
                self.styles['Alerta']
            ))
        elif requiere_seguimiento:
            elementos.append(Paragraph(
                f"📋 REQUIERE SEGUIMIENTO: {clasificacion}",
                self.styles['TextoNormal']
            ))
        else:
            elementos.append(Paragraph(
                f"✅ {clasificacion}",
                self.styles['Exito']
            ))

        elementos.append(Spacer(1, 15))

        # Interpretación
        elementos.append(Paragraph("INTERPRETACIÓN", self.styles['Seccion']))
        interpretacion_raw = datos.get('interpretacion', 'No disponible')
        # Convertir a string y asegurar que no sea None
        if interpretacion_raw is None or interpretacion_raw == '':
            interpretacion_raw = 'No disponible'
        # CRÍTICO: Forzar que sea un string y reemplazar caracteres problemáticos
        texto_limpio = str(interpretacion_raw)
        # Escapar solo los caracteres que ReportLab necesita
        texto_limpio = texto_limpio.replace('&', '&amp;')
        texto_limpio = texto_limpio.replace('<', '&lt;')
        texto_limpio = texto_limpio.replace('>', '&gt;')
        # Crear el párrafo con el texto limpio
        elementos.append(Paragraph(texto_limpio, self.styles['TextoJustificado']))
        elementos.append(Spacer(1, 15))

        # Hallazgos
        hallazgos = datos.get('hallazgos', [])
        if hallazgos:
            elementos.append(Paragraph("HALLAZGOS DETECTADOS", self.styles['Seccion']))
            for i, hallazgo in enumerate(hallazgos, 1):
                elementos.append(Paragraph(
                    f"{i}. {str(hallazgo)}",
                    self.styles['TextoNormal']
                ))
            elementos.append(Spacer(1, 15))

        # Recomendaciones
        recomendaciones = datos.get('recomendaciones', [])
        if recomendaciones:
            elementos.append(Paragraph("RECOMENDACIONES", self.styles['Seccion']))
            for i, recomendacion in enumerate(recomendaciones, 1):
                elementos.append(Paragraph(
                    f"{i}. {str(recomendacion)}",
                    self.styles['TextoNormal']
                ))
            elementos.append(Spacer(1, 15))

        # Confianza de IA
        confianza = datos.get('confianza_ia', 0)
        elementos.append(Paragraph("NIVEL DE CONFIANZA DE IA", self.styles['Seccion']))
        elementos.append(Paragraph(
            f"Confianza: {confianza}%",
            self.styles['TextoNormal']
        ))

        # Disclaimer
        elementos.append(Spacer(1, 15))
        elementos.append(Paragraph(
            "<b>IMPORTANTE:</b> Esta interpretación fue generada por Inteligencia Artificial y debe ser "
            "validada por un médico especialista. No sustituye el criterio clínico profesional.",
            self.styles['Alerta']
        ))

        # Pie de página
        elementos.extend(self._crear_pie_pagina())

        doc.build(elementos)
        buffer.seek(0)
        return buffer


# Instancia global
_generador_pdf = None

def get_generador_pdf() -> GeneradorPDFEstudiosEspeciales:
    """Obtener instancia del generador de PDFs"""
    global _generador_pdf
    if _generador_pdf is None:
        _generador_pdf = GeneradorPDFEstudiosEspeciales()
    return _generador_pdf
