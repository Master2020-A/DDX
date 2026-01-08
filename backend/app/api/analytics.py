"""
API endpoints para Analytics y Reportes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date, datetime, timedelta
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.usuario import Usuario
from app.services.analytics_service import AnalyticsService
from app.services.export_service import ExportService
from app.schemas.analytics import (
    DashboardData,
    FiltrosReporte,
    EstadisticasGenerales,
    EstadisticasConsultas,
    IndicadoresCalidad,
    TiemposAtencion,
    ExportConfig,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard(
    fecha_inicio: Optional[date] = Query(
        None, description="Fecha de inicio del período"
    ),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin del período"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtiene todos los datos para el dashboard de analytics
    """
    try:
        service = AnalyticsService(db)

        # Si no se especifican fechas, usar últimos 30 días
        if not fecha_inicio:
            fecha_inicio = date.today() - timedelta(days=30)
        if not fecha_fin:
            fecha_fin = date.today()

        dashboard_data = await service.get_dashboard_data(fecha_inicio, fecha_fin)
        return dashboard_data

    except Exception as e:
        print(f"❌ Error al obtener dashboard: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error al obtener dashboard: {str(e)}"
        )


@router.get("/estadisticas-generales", response_model=EstadisticasGenerales)
async def get_estadisticas_generales(
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtiene estadísticas generales del sistema
    """
    try:
        service = AnalyticsService(db)

        if not fecha_inicio:
            fecha_inicio = date.today() - timedelta(days=30)
        if not fecha_fin:
            fecha_fin = date.today()

        stats = await service._get_estadisticas_generales(fecha_inicio, fecha_fin)
        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/estadisticas-consultas", response_model=EstadisticasConsultas)
async def get_estadisticas_consultas(
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtiene estadísticas detalladas de consultas
    """
    try:
        service = AnalyticsService(db)

        if not fecha_inicio:
            fecha_inicio = date.today() - timedelta(days=30)
        if not fecha_fin:
            fecha_fin = date.today()

        stats = await service._get_estadisticas_consultas(fecha_inicio, fecha_fin)
        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/indicadores-calidad", response_model=IndicadoresCalidad)
async def get_indicadores_calidad(
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtiene indicadores de calidad de atención
    """
    try:
        service = AnalyticsService(db)

        if not fecha_inicio:
            fecha_inicio = date.today() - timedelta(days=30)
        if not fecha_fin:
            fecha_fin = date.today()

        indicadores = await service._get_indicadores_calidad(fecha_inicio, fecha_fin)
        return indicadores

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tiempos-atencion", response_model=TiemposAtencion)
async def get_tiempos_atencion(
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtiene métricas de tiempos de atención
    """
    try:
        service = AnalyticsService(db)

        if not fecha_inicio:
            fecha_inicio = date.today() - timedelta(days=30)
        if not fecha_fin:
            fecha_fin = date.today()

        tiempos = await service._get_tiempos_atencion(fecha_inicio, fecha_fin)
        return tiempos

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exportar/csv")
async def exportar_csv(
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Exporta reporte en formato CSV
    """
    try:
        service = AnalyticsService(db)

        if not fecha_inicio:
            fecha_inicio = date.today() - timedelta(days=30)
        if not fecha_fin:
            fecha_fin = date.today()

        # Obtener datos
        dashboard_data = await service.get_dashboard_data(fecha_inicio, fecha_fin)

        # Preparar datos para CSV (aplanar estructura)
        csv_data = []
        stats = dashboard_data.estadisticas_generales
        csv_data.append(
            {
                "Métrica": "Total Consultas",
                "Valor": stats.total_consultas,
                "Categoría": "General",
            }
        )
        csv_data.append(
            {
                "Métrica": "Total Pacientes",
                "Valor": stats.total_pacientes,
                "Categoría": "General",
            }
        )
        csv_data.append(
            {
                "Métrica": "Total Diagnósticos",
                "Valor": stats.total_diagnosticos,
                "Categoría": "General",
            }
        )

        # Exportar
        export_service = ExportService()
        output = export_service.export_to_csv(csv_data)

        filename = f"reporte_analytics_{fecha_inicio}_{fecha_fin}.csv"

        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        print(f"❌ Error al exportar CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exportar/excel")
async def exportar_excel(
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    incluir_graficos: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Exporta reporte en formato Excel con gráficos
    """
    try:
        service = AnalyticsService(db)

        if not fecha_inicio:
            fecha_inicio = date.today() - timedelta(days=30)
        if not fecha_fin:
            fecha_fin = date.today()

        # Obtener datos
        dashboard_data = await service.get_dashboard_data(fecha_inicio, fecha_fin)

        # Convertir a dict
        data_dict = {
            "estadisticas_generales": dashboard_data.estadisticas_generales.model_dump(),
            "estadisticas_consultas": dashboard_data.estadisticas_consultas.model_dump(),
            "indicadores_calidad": dashboard_data.indicadores_calidad.model_dump(),
        }

        # Exportar
        export_service = ExportService()
        output = export_service.export_to_excel(
            data_dict, incluir_graficos=incluir_graficos
        )

        filename = f"reporte_analytics_{fecha_inicio}_{fecha_fin}.xlsx"

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail="Librería openpyxl no disponible. Contacte al administrador.",
        )
    except Exception as e:
        print(f"❌ Error al exportar Excel: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exportar/pdf")
async def exportar_pdf(
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    orientacion: str = Query("portrait", description="portrait o landscape"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Exporta reporte en formato PDF
    """
    try:
        service = AnalyticsService(db)

        if not fecha_inicio:
            fecha_inicio = date.today() - timedelta(days=30)
        if not fecha_fin:
            fecha_fin = date.today()

        # Obtener datos
        dashboard_data = await service.get_dashboard_data(fecha_inicio, fecha_fin)

        # Convertir a dict
        data_dict = {
            "estadisticas_generales": dashboard_data.estadisticas_generales.model_dump(),
            "estadisticas_consultas": dashboard_data.estadisticas_consultas.model_dump(),
            "indicadores_calidad": dashboard_data.indicadores_calidad.model_dump(),
        }

        # Exportar
        export_service = ExportService()
        output = export_service.export_to_pdf(data_dict, orientacion=orientacion)

        filename = f"reporte_analytics_{fecha_inicio}_{fecha_fin}.pdf"

        return StreamingResponse(
            output,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail="Librería reportlab no disponible. Contacte al administrador.",
        )
    except Exception as e:
        print(f"❌ Error al exportar PDF: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
