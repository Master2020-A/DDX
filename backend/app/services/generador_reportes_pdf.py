"""
Generador de Reportes PDF para Análisis de Imágenes Médicas
Crea reportes profesionales con resultados del análisis IA
"""
import os
from io import BytesIO
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    from reportlab.lib.fonts import tt2ps
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ ReportLab no disponible - PDFs no funcionarán")

class GeneradorReportesPDF:
    """
    Generador de reportes PDF profesionales para análisis de imágenes médicas
    """

    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab no está instalado. Instale con: pip install reportlab")

        self.styles = getSampleStyleSheet()

        # Estilos personalizados
        self.styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=self.styles['Heading1'],
            fontSize=20,
            alignment=TA_CENTER,
            spaceAfter=30,
            textColor=colors.HexColor('#1f2937')
        ))

        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading2'],
            fontSize=16,
            alignment=TA_LEFT,
            spaceAfter=20,
            textColor=colors.HexColor('#374151')
        ))

        self.styles.add(ParagraphStyle(
            name='Seccion',
            parent=self.styles['Heading3'],
            fontSize=14,
            alignment=TA_LEFT,
            spaceAfter=15,
            textColor=colors.HexColor('#4b5563')
        ))

        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_LEFT,
            spaceAfter=10,
            textColor=colors.HexColor('#111827')
        ))

        self.styles.add(ParagraphStyle(
            name='CustomPiePagina',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#6b7280')
        ))

    def generar_reporte_ia(
        self,
        imagen_info: Dict[str, Any],
        ruta_imagen: Optional[str] = None
    ) -> BytesIO:
        """
        Genera un reporte PDF completo del análisis IA

        Args:
            imagen_info: Información de la imagen y resultados IA
            ruta_imagen: Ruta opcional a la imagen para incluir en el PDF

        Returns:
            BytesIO con el PDF generado
        """

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Contenido del documento
        elementos = []

        # Encabezado
        elementos.extend(self._crear_encabezado())

        # Información del paciente e imagen
        elementos.extend(self._crear_info_paciente_imagen(imagen_info))

        # Resultados del análisis IA
        elementos.extend(self._crear_resultados_ia(imagen_info))

        # Imagen si está disponible
        if ruta_imagen and os.path.exists(ruta_imagen):
            elementos.extend(self._crear_seccion_imagen(ruta_imagen))

        # Interpretación clínica
        elementos.extend(self._crear_interpretacion_clinica(imagen_info))

        # Disclaimer médico
        elementos.extend(self._crear_disclaimer_medico())

        # Pie de página
        elementos.extend(self._crear_pie_pagina(imagen_info))

        # Generar PDF
        doc.build(elementos, onFirstPage=self._agregar_marca_agua, onLaterPages=self._agregar_marca_agua)

        buffer.seek(0)
        return buffer

    def _crear_encabezado(self) -> list:
        """Crea el encabezado del reporte"""
        elementos = []

        # Título principal
        elementos.append(Paragraph("REPORTE DE ANÁLISIS DE INTELIGENCIA ARTIFICIAL", self.styles['TituloPrincipal']))

        # Subtítulo
        elementos.append(Paragraph("Imagen Médica - Sistema DDX", self.styles['Subtitulo']))

        # Fecha de generación
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        elementos.append(Paragraph(f"Fecha de generación: {fecha_actual}", self.styles['CustomNormal']))
        elementos.append(Spacer(1, 20))

        return elementos

    def _crear_info_paciente_imagen(self, imagen_info: Dict[str, Any]) -> list:
        """Crea la sección de información del paciente e imagen"""
        elementos = []

        elementos.append(Paragraph("INFORMACIÓN DEL PACIENTE E IMAGEN", self.styles['Seccion']))

        # Crear tabla con información
        data = [
            ['Campo', 'Valor'],
            ['Título de la Imagen', imagen_info.get('titulo', 'N/A')],
            ['Tipo de Imagen', self._formatear_tipo_imagen(imagen_info.get('tipo_imagen', ''))],
            ['Región Anatómica', imagen_info.get('region_anatomica', 'N/A').title() if imagen_info.get('region_anatomica') else 'N/A'],
            ['Lateralidad', imagen_info.get('lateralidad', 'N/A').title() if imagen_info.get('lateralidad') else 'No especificada'],
            ['Fecha de Creación', self._formatear_fecha(imagen_info.get('created_at'))],
            ['Tamaño del Archivo', self._formatear_bytes(imagen_info.get('tamanio_bytes', 0))],
        ]

        # Agregar descripción si existe
        if imagen_info.get('descripcion'):
            data.append(['Descripción', imagen_info['descripcion']])

        tabla = Table(data, colWidths=[2*inch, 4*inch])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#111827')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))

        elementos.append(tabla)
        elementos.append(Spacer(1, 20))

        return elementos

    def _crear_resultados_ia(self, imagen_info: Dict[str, Any]) -> list:
        """Crea la sección de resultados del análisis IA"""
        elementos = []

        elementos.append(Paragraph("RESULTADOS DEL ANÁLISIS DE INTELIGENCIA ARTIFICIAL", self.styles['Seccion']))

        # Verificar si hay resultados IA
        if not imagen_info.get('analisis_ia_completado'):
            elementos.append(Paragraph(
                "⚠️ Esta imagen aún no ha sido analizada por IA.",
                self.styles['Normal']
            ))
            elementos.append(Spacer(1, 20))
            return elementos

        resultados_ia = imagen_info.get('resultados_ia', {})

        # Información del modelo
        elementos.append(Paragraph("Información del Modelo IA", self.styles['Seccion']))
        info_modelo = [
            ['Campo', 'Valor'],
            ['Modelo Utilizado', resultados_ia.get('modelo', 'N/A')],
            ['Versión', resultados_ia.get('version', 'N/A')],
            ['Modalidad', resultados_ia.get('modalidad', 'N/A')],
            ['Confianza Global', f"{resultados_ia.get('confianza_global', 0):.1%}"],
            ['Umbral Utilizado', f"{resultados_ia.get('umbral_usado', 0):.1%}"],
            ['Tiempo de Procesamiento', f"{resultados_ia.get('tiempo_procesamiento', 0):.1f}s"],
        ]

        tabla_modelo = Table(info_modelo, colWidths=[2*inch, 4*inch])
        tabla_modelo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fef3c7')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#92400e')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#f59e0b')),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))

        elementos.append(tabla_modelo)
        elementos.append(Spacer(1, 15))

        # Hallazgos principales
        elementos.append(Paragraph("Hallazgos Principales", self.styles['Seccion']))

        hallazgos = resultados_ia.get('hallazgos', [])
        if hallazgos:
            for hallazgo in hallazgos:
                elementos.append(Paragraph(f"• {hallazgo}", self.styles['CustomNormal']))
        else:
            elementos.append(Paragraph("No se encontraron hallazgos patológicos significativos.", self.styles['CustomNormal']))

        elementos.append(Spacer(1, 15))

        # Predicciones detalladas (si están disponibles)
        predicciones = resultados_ia.get('predicciones', {})
        if predicciones:
            elementos.append(Paragraph("Predicciones Detalladas", self.styles['Seccion']))

            # Ordenar por probabilidad descendente
            preds_ordenadas = sorted(predicciones.items(), key=lambda x: x[1], reverse=True)

            data_preds = [['Hallazgo', 'Confianza']]
            for hallazgo, confianza in preds_ordenadas[:10]:  # Top 10
                data_preds.append([
                    hallazgo.replace('_', ' ').title(),
                    f"{confianza:.1%}"
                ])

            tabla_preds = Table(data_preds, colWidths=[4*inch, 1.5*inch])
            tabla_preds.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dbeafe')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bfdbfe')),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))

            elementos.append(tabla_preds)

        elementos.append(Spacer(1, 20))
        return elementos

    def _crear_seccion_imagen(self, ruta_imagen: str) -> list:
        """Crea la sección con la imagen si está disponible"""
        elementos = []

        try:
            elementos.append(Paragraph("IMAGEN ANALIZADA", self.styles['Seccion']))

            # Incluir imagen (escalada para caber en la página)
            img = RLImage(ruta_imagen, width=6*inch, height=4*inch)
            elementos.append(img)
            elementos.append(Spacer(1, 15))

        except Exception as e:
            elementos.append(Paragraph(f"Error al cargar imagen: {str(e)}", self.styles['CustomNormal']))

        return elementos

    def _crear_interpretacion_clinica(self, imagen_info: Dict[str, Any]) -> list:
        """Crea la sección de interpretación clínica"""
        elementos = []

        elementos.append(Paragraph("INTERPRETACIÓN CLÍNICA", self.styles['Seccion']))

        elementos.append(Paragraph(
            "IMPORTANTE: Este reporte es generado por un sistema de inteligencia artificial y "
            "debe ser interpretado y validado por un profesional médico calificado. "
            "Los resultados presentados son de carácter informativo y no constituyen "
            "un diagnóstico médico definitivo.",
            self.styles['CustomNormal']
        ))

        elementos.append(Spacer(1, 10))

        elementos.append(Paragraph(
            "Recomendaciones:",
            self.styles['CustomNormal']
        ))

        recomendaciones = [
            "• Correlacionar los hallazgos con la clínica del paciente",
            "• Considerar estudios adicionales si es necesario",
            "• Evaluar la necesidad de intervención terapéutica",
            "• Consultar con especialista en el área correspondiente"
        ]

        for rec in recomendaciones:
            elementos.append(Paragraph(rec, self.styles['CustomNormal']))

        elementos.append(Spacer(1, 20))
        return elementos

    def _crear_disclaimer_medico(self) -> list:
        """Crea el disclaimer médico legal"""
        elementos = []

        elementos.append(Paragraph("DECLARACIÓN DE RESPONSABILIDAD MÉDICA", self.styles['Seccion']))

        disclaimer = (
            "Este sistema de inteligencia artificial es una herramienta de apoyo diagnóstico "
            "desarrollada con fines educativos y de investigación. NO reemplaza el criterio "
            "clínico profesional ni constituye consejo médico. El uso de esta herramienta "
            "es responsabilidad exclusiva del usuario médico. Los desarrolladores no asumen "
            "ninguna responsabilidad por el uso inadecuado de los resultados presentados."
        )

        elementos.append(Paragraph(disclaimer, self.styles['CustomNormal']))
        elementos.append(Spacer(1, 20))

        return elementos

    def _crear_pie_pagina(self, imagen_info: Dict[str, Any]) -> list:
        """Crea el pie de página"""
        elementos = []

        elementos.append(Paragraph(
            f"Sistema DDX - Diagnóstico Diferencial Inteligente | "
            f"Imagen ID: {imagen_info.get('id', 'N/A')} | "
            f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            self.styles['CustomPiePagina']
        ))

        return elementos

    def _agregar_marca_agua(self, canvas, doc):
        """Agrega marca de agua a todas las páginas"""
        canvas.saveState()
        canvas.setFont('Helvetica', 50)
        canvas.setFillColor(colors.HexColor('#f3f4f6'))
        canvas.translate(inch, inch)
        canvas.rotate(45)
        canvas.drawCentredString(4*inch, 0, "DX IA REPORT")
        canvas.restoreState()

    # Funciones auxiliares
    def _formatear_tipo_imagen(self, tipo: str) -> str:
        """Formatea el tipo de imagen para mostrar"""
        tipos = {
            'rayos_x': 'Rayos X',
            'tomografia': 'Tomografía (CT)',
            'resonancia': 'Resonancia Magnética (MRI)',
            'ecografia': 'Ecografía (US)',
            'mamografia': 'Mamografía',
            'endoscopia': 'Endoscopia',
            'fotografia': 'Fotografía Médica'
        }
        return tipos.get(tipo, tipo.title())

    def _formatear_fecha(self, fecha_str: Optional[str]) -> str:
        """Formatea fecha para mostrar"""
        if not fecha_str:
            return "N/A"
        try:
            fecha = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
            return fecha.strftime("%d/%m/%Y %H:%M")
        except:
            return fecha_str

    def _formatear_bytes(self, bytes_val: int) -> str:
        """Formatea bytes a formato legible"""
        if bytes_val == 0:
            return "0 Bytes"

        for unit in ['Bytes', 'KB', 'MB', 'GB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024.0

        return f"{bytes_val:.1f} TB"


# Instancia global del generador
_generador_pdf = None

def get_generador_pdf() -> GeneradorReportesPDF:
    """Obtener instancia única del generador de PDF"""
    global _generador_pdf
    if _generador_pdf is None:
        _generador_pdf = GeneradorReportesPDF()
    return _generador_pdf
