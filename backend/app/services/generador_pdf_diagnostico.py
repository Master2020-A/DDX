"""
Servicio para generar PDF del diagnóstico sugerido por IA
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
from typing import Dict, Any
import io


class GeneradorPDFDiagnostico:
    """Genera PDF profesional del diagnóstico sugerido"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._configurar_estilos()
    
    def _configurar_estilos(self):
        """Configura estilos personalizados"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#9333ea'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#6d28d9'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Texto normal
        self.styles.add(ParagraphStyle(
            name='Normal',
            parent=self.styles['BodyText'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=6
        ))
        
        # Alerta
        self.styles.add(ParagraphStyle(
            name='Alerta',
            parent=self.styles['BodyText'],
            fontSize=10,
            textColor=colors.red,
            leftIndent=20,
            spaceAfter=6
        ))
    
    def generar_pdf(self, resultado: Dict[str, Any], paciente_data: Dict[str, Any]) -> bytes:
        """
        Genera el PDF del diagnóstico sugerido
        
        Args:
            resultado: Resultado del diagnóstico sugerido
            paciente_data: Información del paciente
            
        Returns:
            bytes: PDF generado
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        
        # ===== ENCABEZADO =====
        story.append(Paragraph("🧠 DIAGNÓSTICO SUGERIDO POR IA", self.styles['TituloPrincipal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Información del paciente
        info_paciente = [
            ['<b>Paciente:</b>', paciente_data.get('nombre_completo', 'N/A')],
            ['<b>Expediente:</b>', paciente_data.get('numero_expediente', 'N/A')],
            ['<b>Edad:</b>', f"{paciente_data.get('edad', 'N/A')} años"],
            ['<b>Fecha de Análisis:</b>', datetime.fromisoformat(resultado.get('fecha_analisis', datetime.utcnow().isoformat())).strftime('%d/%m/%Y %H:%M')]
        ]
        
        tabla_paciente = Table(info_paciente, colWidths=[2*inch, 4*inch])
        tabla_paciente.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(tabla_paciente)
        story.append(Spacer(1, 0.3*inch))
        
        # Datos analizados
        datos_analizados = resultado.get('datos_analizados', {})
        story.append(Paragraph("📊 Datos Analizados", self.styles['Subtitulo']))
        datos_info = f"""
        • {datos_analizados.get('consultas', 0)} Consulta(s)<br/>
        • {datos_analizados.get('laboratorios', 0)} Laboratorio(s)<br/>
        • {datos_analizados.get('estudios_ekg', 0)} EKG(s)<br/>
        • {datos_analizados.get('estudios_eeg', 0)} EEG(s)<br/>
        • {datos_analizados.get('ecografias', 0)} Ecografía(s)
        """
        story.append(Paragraph(datos_info, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Resumen clínico
        if resultado.get('resumen_clinico'):
            story.append(Paragraph("📋 Resumen Clínico", self.styles['Subtitulo']))
            story.append(Paragraph(resultado['resumen_clinico'], self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Alertas
        if resultado.get('alertas'):
            story.append(Paragraph("⚠️ Alertas Clínicas", self.styles['Subtitulo']))
            for alerta in resultado['alertas']:
                story.append(Paragraph(f"• {alerta}", self.styles['Alerta']))
            story.append(Spacer(1, 0.2*inch))
        
        # ===== DIAGNÓSTICOS DIFERENCIALES =====
        story.append(Paragraph("🎯 Diagnósticos Diferenciales", self.styles['Subtitulo']))
        story.append(Spacer(1, 0.1*inch))
        
        for idx, diagnostico in enumerate(resultado.get('diagnosticos', []), 1):
            # Encabezado del diagnóstico
            nombre = diagnostico.get('nombre', 'N/A')
            codigo = diagnostico.get('codigo_cie10', '')
            probabilidad = diagnostico.get('probabilidad', 0)
            urgencia = diagnostico.get('urgencia', 'bajo')
            
            titulo_diag = f"<b>{idx}. {nombre}</b>"
            if codigo:
                titulo_diag += f" <i>(CIE-10: {codigo})</i>"
            
            story.append(Paragraph(titulo_diag, self.styles['Heading3']))
            
            # Tabla de información
            info_diag = [
                ['Probabilidad:', f"{probabilidad}%"],
                ['Urgencia:', urgencia.upper()]
            ]
            
            tabla_diag = Table(info_diag, colWidths=[1.5*inch, 2*inch])
            tabla_diag.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            story.append(tabla_diag)
            story.append(Spacer(1, 0.1*inch))
            
            # Evidencia
            story.append(Paragraph("<b>Evidencia:</b>", self.styles['Normal']))
            for evidencia in diagnostico.get('evidencia', []):
                story.append(Paragraph(f"✓ {evidencia}", self.styles['Normal']))
            
            story.append(Spacer(1, 0.2*inch))
        
        # ===== RECOMENDACIONES =====
        story.append(PageBreak())
        story.append(Paragraph("💡 Recomendaciones", self.styles['Subtitulo']))
        story.append(Spacer(1, 0.1*inch))
        
        # Estudios adicionales
        if resultado.get('recomendaciones_estudios'):
            story.append(Paragraph("<b>🔬 Estudios Adicionales:</b>", self.styles['Normal']))
            for estudio in resultado['recomendaciones_estudios']:
                story.append(Paragraph(f"• {estudio}", self.styles['Normal']))
            story.append(Spacer(1, 0.15*inch))
        
        # Tratamiento
        if resultado.get('recomendaciones_tratamiento'):
            story.append(Paragraph("<b>💊 Tratamiento y Seguimiento:</b>", self.styles['Normal']))
            for tratamiento in resultado['recomendaciones_tratamiento']:
                story.append(Paragraph(f"• {tratamiento}", self.styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
        
        # ===== DISCLAIMER =====
        disclaimer = """
        <b>NOTA IMPORTANTE:</b> Este diagnóstico es una sugerencia generada por inteligencia artificial 
        basada en la información disponible del paciente. Debe ser revisado y confirmado por el médico 
        tratante considerando el contexto clínico completo. No reemplaza el juicio clínico profesional.
        """
        story.append(Paragraph(disclaimer, ParagraphStyle(
            name='Disclaimer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_JUSTIFY,
            borderWidth=1,
            borderColor=colors.grey,
            borderPadding=10,
            backColor=colors.HexColor('#f9fafb')
        )))
        
        # Generar PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
