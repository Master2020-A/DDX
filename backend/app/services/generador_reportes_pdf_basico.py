"""
Generador de Reportes PDF Simplificado para Análisis de Imágenes Médicas
Versión básica sin conflictos de estilos
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
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("ReportLab no disponible")

class GeneradorReportesPDFBasico:
    """
    Generador básico de reportes PDF sin conflictos de estilos
    """

    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab no está instalado")

        # Usar solo estilos por defecto
        self.styles = getSampleStyleSheet()

        # Crear estilos personalizados únicos
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=colors.HexColor('#1f2937')
        ))

        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=14,
            alignment=TA_LEFT,
            spaceAfter=15,
            textColor=colors.HexColor('#374151')
        ))

        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=10,
            textColor=colors.HexColor('#111827')
        ))

    def generar_reporte_ia(self, imagen_info: Dict[str, Any], ruta_imagen: Optional[str] = None) -> BytesIO:
        """
        Genera un reporte PDF básico
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)

        elementos = []

        # Título
        elementos.append(Paragraph("REPORTE DE ANÁLISIS IA - SISTEMA DDX", self.styles['CustomTitle']))
        elementos.append(Spacer(1, 20))

        # Información básica
        elementos.append(Paragraph("INFORMACIÓN DE LA IMAGEN", self.styles['CustomHeading']))

        data = [
            ['Campo', 'Valor'],
            ['Título', imagen_info.get('titulo', 'N/A')],
            ['Tipo', imagen_info.get('tipo_imagen', 'N/A')],
            ['Región', imagen_info.get('region_anatomica', 'N/A')],
        ]

        tabla = Table(data, colWidths=[2*inch, 4*inch])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elementos.append(tabla)
        elementos.append(Spacer(1, 20))

        # Resultados IA
        if imagen_info.get('analisis_ia_completado'):
            elementos.append(Paragraph("RESULTADOS DEL ANÁLISIS", self.styles['CustomHeading']))

            # Obtener resultados IA de forma segura
            resultados = imagen_info.get('resultados_ia')
            if resultados is None:
                resultados = {}
            elif isinstance(resultados, str):
                # Si es string, intentar parsearlo o usar como está
                resultados = {'notas': resultados}

            # Intentar obtener hallazgos de múltiples fuentes
            hallazgos = []
            if 'hallazgos' in resultados and resultados['hallazgos']:
                hallazgos = resultados['hallazgos']
            elif 'hallazgos' in imagen_info and imagen_info['hallazgos']:
                hallazgos = imagen_info['hallazgos']

            # Asegurar que hallazgos es una lista
            if not isinstance(hallazgos, list):
                if isinstance(hallazgos, str):
                    hallazgos = [hallazgos]
                else:
                    hallazgos = []

            if hallazgos:
                elementos.append(Paragraph("Hallazgos principales:", self.styles['CustomBody']))
                for hallazgo in hallazgos[:5]:  # Máximo 5 hallazgos
                    if hallazgo:  # Verificar que no sea None o vacío
                        elementos.append(Paragraph(f"• {str(hallazgo)}", self.styles['CustomBody']))
            else:
                elementos.append(Paragraph("No se encontraron hallazgos significativos.", self.styles['CustomBody']))

            elementos.append(Spacer(1, 15))

            # Modelo usado
            modelo = resultados.get('modelo', 'N/A') if isinstance(resultados, dict) else 'N/A'
            confianza = resultados.get('confianza_global', 0) if isinstance(resultados, dict) else 0
            
            # Manejar diferentes tipos de confianza
            try:
                if isinstance(confianza, (int, float)):
                    confianza_str = f"{confianza:.1%}"
                else:
                    confianza_str = str(confianza)
            except:
                confianza_str = "N/A"

            elementos.append(Paragraph(f"Modelo: {modelo}", self.styles['CustomBody']))
            elementos.append(Paragraph(f"Confianza global: {confianza_str}", self.styles['CustomBody']))
        else:
            elementos.append(Paragraph("Esta imagen aún no ha sido analizada por IA.", self.styles['CustomBody']))

        elementos.append(Spacer(1, 30))

        # Disclaimer
        elementos.append(Paragraph("DISCLAIMER MÉDICO", self.styles['CustomHeading']))
        disclaimer = (
            "Este reporte es generado por IA y debe ser validado por un profesional médico calificado. "
            "No constituye diagnóstico médico definitivo."
        )
        elementos.append(Paragraph(disclaimer, self.styles['CustomBody']))

        # Generar PDF
        doc.build(elementos)

        buffer.seek(0)
        return buffer


# Instancia global
_generador_basico = None

def get_generador_pdf() -> GeneradorReportesPDFBasico:
    """Obtener instancia del generador básico"""
    global _generador_basico
    if _generador_basico is None:
        _generador_basico = GeneradorReportesPDFBasico()
    return _generador_basico
