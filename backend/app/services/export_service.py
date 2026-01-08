"""
Servicio para exportar reportes en diferentes formatos
"""

from io import BytesIO
from typing import Dict, List, Any
from datetime import datetime
import csv

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate,
        Table,
        TableStyle,
        Paragraph,
        Spacer,
        PageBreak,
    )
    from reportlab.platypus import Image as RLImage
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.chart import BarChart, PieChart, LineChart, Reference

    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False


class ExportService:
    """Servicio para exportar reportes"""

    @staticmethod
    def export_to_csv(
        data: List[Dict[str, Any]], filename: str = "reporte.csv"
    ) -> BytesIO:
        """Exporta datos a CSV"""
        output = BytesIO()

        if not data:
            return output

        # Usar StringIO temporal para CSV
        from io import StringIO

        string_output = StringIO()

        # Obtener las columnas del primer registro
        fieldnames = list(data[0].keys())

        writer = csv.DictWriter(string_output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

        # Convertir a bytes
        output.write(string_output.getvalue().encode("utf-8-sig"))
        output.seek(0)

        return output

    @staticmethod
    def export_to_excel(
        data: Dict[str, Any],
        filename: str = "reporte.xlsx",
        incluir_graficos: bool = True,
    ) -> BytesIO:
        """Exporta datos a Excel con formato y gráficos"""

        if not OPENPYXL_AVAILABLE:
            raise ImportError(
                "openpyxl no está instalado. Instala con: pip install openpyxl"
            )

        output = BytesIO()
        wb = openpyxl.Workbook()

        # Eliminar hoja por defecto
        wb.remove(wb.active)

        # Estilos
        header_font = Font(bold=True, color="FFFFFF", size=12)
        header_fill = PatternFill(
            start_color="4472C4", end_color="4472C4", fill_type="solid"
        )
        header_alignment = Alignment(horizontal="center", vertical="center")

        border = Border(
            left=Side(style="thin"),
            right=Side(style="thin"),
            top=Side(style="thin"),
            bottom=Side(style="thin"),
        )

        # Hoja de resumen
        ws_resumen = wb.create_sheet("Resumen")
        ws_resumen.append(["REPORTE DE ANALYTICS"])
        ws_resumen.append([f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}"])
        ws_resumen.append([])

        # Estadísticas generales
        if "estadisticas_generales" in data:
            stats = data["estadisticas_generales"]
            ws_resumen.append(["ESTADÍSTICAS GENERALES"])
            ws_resumen.append(["Métrica", "Valor"])

            for key, value in stats.items():
                ws_resumen.append([key.replace("_", " ").title(), value])

        # Aplicar estilos al resumen
        for row in ws_resumen.iter_rows(min_row=1, max_row=ws_resumen.max_row):
            for cell in row:
                cell.border = border

        # Hoja de consultas
        if "estadisticas_consultas" in data:
            ws_consultas = wb.create_sheet("Consultas")
            consultas = data["estadisticas_consultas"]

            ws_consultas.append(["ESTADÍSTICAS DE CONSULTAS"])
            ws_consultas.append([])
            ws_consultas.append(["Total de Consultas", consultas.get("total", 0)])
            ws_consultas.append(
                ["Promedio Diario", consultas.get("promedio_diario", 0)]
            )
            ws_consultas.append(["Tendencia", consultas.get("tendencia", "N/A")])
            ws_consultas.append([])

            # Por tipo
            ws_consultas.append(["Consultas por Tipo"])
            ws_consultas.append(["Tipo", "Cantidad"])
            for tipo, cantidad in consultas.get("por_tipo", {}).items():
                ws_consultas.append([tipo, cantidad])

            # Gráfico de barras si está habilitado
            if incluir_graficos and consultas.get("por_tipo"):
                chart = BarChart()
                chart.title = "Consultas por Tipo"
                chart.x_axis.title = "Tipo"
                chart.y_axis.title = "Cantidad"

                data_ref = Reference(
                    ws_consultas,
                    min_col=2,
                    min_row=8,
                    max_row=8 + len(consultas["por_tipo"]),
                )
                cats_ref = Reference(
                    ws_consultas,
                    min_col=1,
                    min_row=9,
                    max_row=8 + len(consultas["por_tipo"]),
                )

                chart.add_data(data_ref, titles_from_data=False)
                chart.set_categories(cats_ref)

                ws_consultas.add_chart(chart, "E2")

        # Hoja de indicadores de calidad
        if "indicadores_calidad" in data:
            ws_calidad = wb.create_sheet("Indicadores de Calidad")
            calidad = data["indicadores_calidad"]

            ws_calidad.append(["INDICADORES DE CALIDAD"])
            ws_calidad.append([])
            ws_calidad.append(["Indicador", "Valor"])

            for key, value in calidad.items():
                ws_calidad.append([key.replace("_", " ").title(), value])

        # Ajustar anchos de columna
        for ws in wb.worksheets:
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width

        wb.save(output)
        output.seek(0)

        return output

    @staticmethod
    def export_to_pdf(
        data: Dict[str, Any],
        filename: str = "reporte.pdf",
        orientacion: str = "portrait",
    ) -> BytesIO:
        """Exporta datos a PDF"""

        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "reportlab no está instalado. Instala con: pip install reportlab"
            )

        output = BytesIO()

        # Configurar página
        pagesize = landscape(letter) if orientacion == "landscape" else letter
        doc = SimpleDocTemplate(
            output, pagesize=pagesize, topMargin=0.5 * inch, bottomMargin=0.5 * inch
        )

        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#1976d2"),
            spaceAfter=30,
            alignment=TA_CENTER,
        )

        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=16,
            textColor=colors.HexColor("#1976d2"),
            spaceAfter=12,
            spaceBefore=12,
        )

        # Contenido
        story = []

        # Título
        story.append(Paragraph("REPORTE DE ANALYTICS", title_style))
        story.append(
            Paragraph(
                f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 0.3 * inch))

        # Estadísticas generales
        if "estadisticas_generales" in data:
            story.append(Paragraph("Estadísticas Generales", heading_style))

            stats = data["estadisticas_generales"]
            table_data = [["Métrica", "Valor"]]

            for key, value in stats.items():
                table_data.append([key.replace("_", " ").title(), str(value)])

            table = Table(table_data, colWidths=[4 * inch, 2 * inch])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1976d2")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 12),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("FONTSIZE", (0, 1), (-1, -1), 10),
                    ]
                )
            )

            story.append(table)
            story.append(Spacer(1, 0.3 * inch))

        # Estadísticas de consultas
        if "estadisticas_consultas" in data:
            story.append(Paragraph("Estadísticas de Consultas", heading_style))

            consultas = data["estadisticas_consultas"]

            info_data = [
                ["Total de Consultas", str(consultas.get("total", 0))],
                ["Promedio Diario", f"{consultas.get('promedio_diario', 0):.2f}"],
                ["Tendencia", consultas.get("tendencia", "N/A").title()],
            ]

            info_table = Table(info_data, colWidths=[3 * inch, 2 * inch])
            info_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), colors.lightblue),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 10),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ]
                )
            )

            story.append(info_table)
            story.append(Spacer(1, 0.2 * inch))

            # Por tipo
            if consultas.get("por_tipo"):
                story.append(Paragraph("Consultas por Tipo", styles["Heading3"]))

                tipo_data = [["Tipo", "Cantidad"]]
                for tipo, cantidad in consultas["por_tipo"].items():
                    tipo_data.append([tipo.replace("_", " ").title(), str(cantidad)])

                tipo_table = Table(tipo_data, colWidths=[3 * inch, 2 * inch])
                tipo_table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                        ]
                    )
                )

                story.append(tipo_table)
                story.append(Spacer(1, 0.3 * inch))

        # Indicadores de calidad
        if "indicadores_calidad" in data:
            story.append(PageBreak())
            story.append(Paragraph("Indicadores de Calidad", heading_style))

            calidad = data["indicadores_calidad"]
            calidad_data = [["Indicador", "Valor"]]

            for key, value in calidad.items():
                if value is not None:
                    calidad_data.append(
                        [
                            key.replace("_", " ").title(),
                            f"{value:.2f}" if isinstance(value, float) else str(value),
                        ]
                    )

            calidad_table = Table(calidad_data, colWidths=[4 * inch, 2 * inch])
            calidad_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4caf50")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.lightgreen),
                    ]
                )
            )

            story.append(calidad_table)

        # Construir PDF
        doc.build(story)
        output.seek(0)

        return output
