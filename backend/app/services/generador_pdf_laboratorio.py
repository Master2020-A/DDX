"""
Servicio para generar reportes PDF de resultados de laboratorio
"""
from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

class GeneradorPDFLaboratorio:
    """Generador de reportes PDF para resultados de laboratorio"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._crear_estilos_personalizados()
    
    def _crear_estilos_personalizados(self):
        """Crear estilos personalizados para el PDF"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#3b82f6'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))
        
        # Texto normal
        self.styles.add(ParagraphStyle(
            name='TextoNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))
        
        # Alerta
        self.styles.add(ParagraphStyle(
            name='Alerta',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#dc2626'),
            fontName='Helvetica-Bold',
            spaceAfter=8
        ))
    
    def generar_reporte_laboratorio(self, prueba_data: dict, paciente_data: dict) -> BytesIO:
        """
        Generar reporte PDF de una prueba de laboratorio
        
        Args:
            prueba_data: Datos de la prueba de laboratorio
            paciente_data: Datos del paciente
            
        Returns:
            BytesIO con el contenido del PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Contenido del PDF
        story = []
        
        # ===== ENCABEZADO =====
        story.append(Paragraph("REPORTE DE LABORATORIO CLÍNICO", self.styles['TituloPrincipal']))
        story.append(Spacer(1, 0.2*inch))
        
        # ===== INFORMACIÓN DEL PACIENTE =====
        story.append(Paragraph("Información del Paciente", self.styles['Subtitulo']))
        
        info_paciente = [
            ['Nombre:', paciente_data.get('nombre_completo', 'N/A')],
            ['Expediente:', paciente_data.get('numero_expediente', 'N/A')],
            ['Fecha de Nacimiento:', paciente_data.get('fecha_nacimiento', 'N/A')],
            ['Edad:', f"{paciente_data.get('edad', 'N/A')} años"],
            ['Sexo:', paciente_data.get('sexo', 'N/A').upper()]
        ]
        
        tabla_paciente = Table(info_paciente, colWidths=[1.5*inch, 4*inch])
        tabla_paciente.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e7ff')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1e40af')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(tabla_paciente)
        story.append(Spacer(1, 0.3*inch))
        
        # ===== INFORMACIÓN DE LA PRUEBA =====
        story.append(Paragraph("Información de la Prueba", self.styles['Subtitulo']))
        
        fecha_prueba = prueba_data.get('fecha', 'N/A')
        if isinstance(fecha_prueba, str):
            try:
                fecha_obj = datetime.fromisoformat(fecha_prueba.replace('Z', '+00:00'))
                fecha_prueba = fecha_obj.strftime('%d/%m/%Y %H:%M')
            except:
                pass
        
        info_prueba = [
            ['Área:', prueba_data.get('area', 'N/A').replace('_', ' ').title()],
            ['Tipo de Prueba:', prueba_data.get('tipo_prueba', 'N/A').replace('_', ' ').title()],
            ['Fecha:', fecha_prueba],
            ['Estado:', prueba_data.get('estado', 'N/A').upper()]
        ]
        
        if prueba_data.get('laboratorio_externo'):
            info_prueba.append(['Laboratorio:', prueba_data['laboratorio_externo']])
        if prueba_data.get('numero_orden'):
            info_prueba.append(['No. Orden:', prueba_data['numero_orden']])
        
        tabla_prueba = Table(info_prueba, colWidths=[1.5*inch, 4*inch])
        tabla_prueba.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e7ff')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1e40af')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(tabla_prueba)
        story.append(Spacer(1, 0.3*inch))
        
        # ===== ALERTAS CRÍTICAS =====
        alertas = prueba_data.get('alertas', [])
        if alertas:
            story.append(Paragraph("⚠️ ALERTAS IMPORTANTES", self.styles['Alerta']))
            for alerta in alertas:
                story.append(Paragraph(f"• {alerta}", self.styles['TextoNormal']))
            story.append(Spacer(1, 0.2*inch))
        
        # ===== RESULTADOS =====
        story.append(Paragraph("Resultados de Laboratorio", self.styles['Subtitulo']))
        
        resultados = prueba_data.get('resultados', [])
        if resultados:
            # Encabezados de la tabla
            datos_tabla = [['Parámetro', 'Valor', 'Unidad', 'Rango de Referencia', 'Estado']]
            
            for resultado in resultados:
                parametro = resultado.get('parametro', 'N/A')
                valor = str(resultado.get('valor', 'N/A'))
                unidad = resultado.get('unidad', '')
                
                # Rango de referencia
                rango_min = resultado.get('rango_min')
                rango_max = resultado.get('rango_max')
                if rango_min is not None and rango_max is not None:
                    rango = f"{rango_min} - {rango_max}"
                else:
                    rango = 'N/A'
                
                # Estado
                estado = resultado.get('estado', 'normal')
                if estado == 'critico':
                    estado_texto = '🔴 CRÍTICO'
                elif estado == 'anormal':
                    estado_texto = '🟡 ANORMAL'
                else:
                    estado_texto = '🟢 NORMAL'
                
                datos_tabla.append([parametro, valor, unidad, rango, estado_texto])
            
            tabla_resultados = Table(datos_tabla, colWidths=[1.8*inch, 1*inch, 0.8*inch, 1.5*inch, 1.2*inch])
            tabla_resultados.setStyle(TableStyle([
                # Encabezado
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                
                # Cuerpo
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (1, 1), (1, -1), 'CENTER'),  # Valor
                ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Unidad
                ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Rango
                ('ALIGN', (4, 1), (4, -1), 'CENTER'),  # Estado
                
                # Bordes y padding
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 6),
                
                # Alternar colores de filas
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')])
            ]))
            story.append(tabla_resultados)
        else:
            story.append(Paragraph("No hay resultados disponibles.", self.styles['TextoNormal']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # ===== INTERPRETACIÓN CLÍNICA =====
        interpretacion = prueba_data.get('interpretacion_clinica')
        if interpretacion:
            story.append(Paragraph("Interpretación Clínica", self.styles['Subtitulo']))
            
            # Dividir interpretación en párrafos
            parrafos = interpretacion.split('\n\n')
            for parrafo in parrafos:
                if parrafo.strip():
                    # Reemplazar saltos de línea simples con <br/>
                    parrafo_html = parrafo.replace('\n', '<br/>')
                    story.append(Paragraph(parrafo_html, self.styles['TextoNormal']))
                    story.append(Spacer(1, 0.1*inch))
        
        # ===== NOTAS DEL MÉDICO =====
        notas = prueba_data.get('notas_medico')
        if notas:
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("Notas del Médico", self.styles['Subtitulo']))
            story.append(Paragraph(notas, self.styles['TextoNormal']))
        
        # ===== PIE DE PÁGINA =====
        story.append(Spacer(1, 0.5*inch))
        fecha_generacion = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        pie = Paragraph(
            f"<i>Reporte generado el {fecha_generacion} por Sistema DDX</i>",
            self.styles['TextoNormal']
        )
        story.append(pie)
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer


# Instancia global del generador
_generador_pdf_laboratorio = None

def get_generador_pdf_laboratorio() -> GeneradorPDFLaboratorio:
    """Obtener instancia del generador de PDF de laboratorio"""
    global _generador_pdf_laboratorio
    if _generador_pdf_laboratorio is None:
        _generador_pdf_laboratorio = GeneradorPDFLaboratorio()
    return _generador_pdf_laboratorio
