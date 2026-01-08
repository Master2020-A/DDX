"""
Servicio para Analytics y Reportes
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, extract, case
from sqlalchemy.sql import text
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
from uuid import UUID
import statistics

from app.models.consulta import Consulta, TipoConsultaEnum, EstadoConsultaEnum
from app.models.paciente import Paciente
from app.models.diagnostico import Diagnostico
from app.models.hospitalizacion import Hospitalizacion, Cama
from app.models.interconsulta import Interconsulta
from app.schemas.analytics import (
    EstadisticasGenerales,
    EstadisticasConsultas,
    IndicadoresCalidad,
    TiemposAtencion,
    EstadisticasDiagnosticos,
    EstadisticasHospitalizacion,
    DashboardData,
    FiltrosReporte,
)


class AnalyticsService:
    """Servicio para generar analytics y reportes"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_data(
        self, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None
    ) -> DashboardData:
        """Obtiene todos los datos para el dashboard"""

        if not fecha_inicio:
            fecha_inicio = date.today() - timedelta(days=30)
        if not fecha_fin:
            fecha_fin = date.today()

        estadisticas_generales = await self._get_estadisticas_generales(
            fecha_inicio, fecha_fin
        )
        estadisticas_consultas = await self._get_estadisticas_consultas(
            fecha_inicio, fecha_fin
        )
        indicadores_calidad = await self._get_indicadores_calidad(
            fecha_inicio, fecha_fin
        )
        tiempos_atencion = await self._get_tiempos_atencion(fecha_inicio, fecha_fin)
        estadisticas_diagnosticos = await self._get_estadisticas_diagnosticos(
            fecha_inicio, fecha_fin
        )
        estadisticas_hospitalizacion = await self._get_estadisticas_hospitalizacion(
            fecha_inicio, fecha_fin
        )

        return DashboardData(
            estadisticas_generales=estadisticas_generales,
            estadisticas_consultas=estadisticas_consultas,
            indicadores_calidad=indicadores_calidad,
            tiempos_atencion=tiempos_atencion,
            estadisticas_diagnosticos=estadisticas_diagnosticos,
            estadisticas_hospitalizacion=estadisticas_hospitalizacion,
            ultima_actualizacion=datetime.now(),
        )

    async def _get_estadisticas_generales(
        self, fecha_inicio: date, fecha_fin: date
    ) -> EstadisticasGenerales:
        """Obtiene estadísticas generales del sistema"""

        # Total de consultas en el período
        result = await self.db.execute(
            select(func.count(Consulta.id)).where(
                and_(
                    func.date(Consulta.fecha_hora) >= fecha_inicio,
                    func.date(Consulta.fecha_hora) <= fecha_fin,
                )
            )
        )
        total_consultas = result.scalar() or 0

        # Total de pacientes únicos
        result = await self.db.execute(
            select(func.count(func.distinct(Consulta.paciente_id))).where(
                and_(
                    func.date(Consulta.fecha_hora) >= fecha_inicio,
                    func.date(Consulta.fecha_hora) <= fecha_fin,
                )
            )
        )
        total_pacientes = result.scalar() or 0

        # Total de diagnósticos
        result = await self.db.execute(
            select(func.count(Diagnostico.id)).where(
                and_(
                    func.date(Diagnostico.created_at) >= fecha_inicio,
                    func.date(Diagnostico.created_at) <= fecha_fin,
                )
            )
        )
        total_diagnosticos = result.scalar() or 0

        # Total de hospitalizaciones
        result = await self.db.execute(
            select(func.count(Hospitalizacion.id)).where(
                and_(
                    func.date(Hospitalizacion.fecha_ingreso) >= fecha_inicio,
                    func.date(Hospitalizacion.fecha_ingreso) <= fecha_fin,
                )
            )
        )
        total_hospitalizaciones = result.scalar() or 0

        # Total de interconsultas
        result = await self.db.execute(
            select(func.count(Interconsulta.id)).where(
                and_(
                    func.date(Interconsulta.fecha_solicitud) >= fecha_inicio,
                    func.date(Interconsulta.fecha_solicitud) <= fecha_fin,
                )
            )
        )
        total_interconsultas = result.scalar() or 0

        # Consultas hoy
        result = await self.db.execute(
            select(func.count(Consulta.id)).where(
                func.date(Consulta.fecha_hora) == date.today()
            )
        )
        consultas_hoy = result.scalar() or 0

        # Pacientes nuevos este mes
        primer_dia_mes = date.today().replace(day=1)
        result = await self.db.execute(
            select(func.count(Paciente.id)).where(
                func.date(Paciente.created_at) >= primer_dia_mes
            )
        )
        pacientes_nuevos_mes = result.scalar() or 0

        # Tasa de hospitalización
        tasa_hospitalizacion = (
            (total_hospitalizaciones / total_consultas * 100)
            if total_consultas > 0
            else 0
        )

        return EstadisticasGenerales(
            total_consultas=total_consultas,
            total_pacientes=total_pacientes,
            total_diagnosticos=total_diagnosticos,
            total_hospitalizaciones=total_hospitalizaciones,
            total_interconsultas=total_interconsultas,
            consultas_hoy=consultas_hoy,
            pacientes_nuevos_mes=pacientes_nuevos_mes,
            tasa_hospitalizacion=round(tasa_hospitalizacion, 2),
        )

    async def _get_estadisticas_consultas(
        self, fecha_inicio: date, fecha_fin: date
    ) -> EstadisticasConsultas:
        """Obtiene estadísticas detalladas de consultas"""

        # Total de consultas
        result = await self.db.execute(
            select(func.count(Consulta.id)).where(
                and_(
                    func.date(Consulta.fecha_hora) >= fecha_inicio,
                    func.date(Consulta.fecha_hora) <= fecha_fin,
                )
            )
        )
        total = result.scalar() or 0

        # Por tipo
        result = await self.db.execute(
            select(Consulta.tipo_consulta, func.count(Consulta.id).label("count"))
            .where(
                and_(
                    func.date(Consulta.fecha_hora) >= fecha_inicio,
                    func.date(Consulta.fecha_hora) <= fecha_fin,
                )
            )
            .group_by(Consulta.tipo_consulta)
        )
        por_tipo = {row[0] or "sin_tipo": row[1] for row in result.all()}

        # Por estado
        result = await self.db.execute(
            select(Consulta.estado, func.count(Consulta.id).label("count"))
            .where(
                and_(
                    func.date(Consulta.fecha_hora) >= fecha_inicio,
                    func.date(Consulta.fecha_hora) <= fecha_fin,
                )
            )
            .group_by(Consulta.estado)
        )
        por_estado = {row[0] or "sin_estado": row[1] for row in result.all()}

        # Por mes (últimos 12 meses)
        result = await self.db.execute(
            select(
                extract("year", Consulta.fecha_hora).label("year"),
                extract("month", Consulta.fecha_hora).label("month"),
                func.count(Consulta.id).label("count"),
            )
            .where(func.date(Consulta.fecha_hora) >= fecha_inicio)
            .group_by("year", "month")
            .order_by("year", "month")
        )
        por_mes = [
            {"mes": f"{int(row[0])}-{int(row[1]):02d}", "count": row[2]}
            for row in result.all()
        ]

        # Promedio diario
        dias = (fecha_fin - fecha_inicio).days + 1
        promedio_diario = total / dias if dias > 0 else 0

        # Tendencia (comparar con período anterior)
        dias_periodo = (fecha_fin - fecha_inicio).days + 1
        fecha_inicio_anterior = fecha_inicio - timedelta(days=dias_periodo)
        fecha_fin_anterior = fecha_inicio - timedelta(days=1)

        result = await self.db.execute(
            select(func.count(Consulta.id)).where(
                and_(
                    func.date(Consulta.fecha_hora) >= fecha_inicio_anterior,
                    func.date(Consulta.fecha_hora) <= fecha_fin_anterior,
                )
            )
        )
        total_anterior = result.scalar() or 0

        if total_anterior == 0:
            tendencia = "estable"
        elif total > total_anterior * 1.1:
            tendencia = "ascendente"
        elif total < total_anterior * 0.9:
            tendencia = "descendente"
        else:
            tendencia = "estable"

        return EstadisticasConsultas(
            total=total,
            por_tipo=por_tipo,
            por_estado=por_estado,
            por_mes=por_mes,
            promedio_diario=round(promedio_diario, 2),
            tendencia=tendencia,
        )

    async def _get_indicadores_calidad(
        self, fecha_inicio: date, fecha_fin: date
    ) -> IndicadoresCalidad:
        """Calcula indicadores de calidad de atención"""

        # Tiempo promedio de atención (simulado - en producción vendría de logs)
        tiempo_promedio_atencion = 25.5  # minutos
        tiempo_espera_promedio = 15.3  # minutos

        # Tasa de reingreso (pacientes que vuelven en 30 días)
        result = await self.db.execute(
            select(func.count(func.distinct(Consulta.paciente_id))).where(
                and_(
                    func.date(Consulta.fecha_hora) >= fecha_inicio,
                    func.date(Consulta.fecha_hora) <= fecha_fin,
                )
            )
        )
        total_pacientes = result.scalar() or 1

        # Pacientes con más de una consulta en 30 días
        subquery = (
            select(Consulta.paciente_id, func.count(Consulta.id).label("num_consultas"))
            .where(
                and_(
                    func.date(Consulta.fecha_hora) >= fecha_inicio,
                    func.date(Consulta.fecha_hora) <= fecha_fin,
                )
            )
            .group_by(Consulta.paciente_id)
            .having(func.count(Consulta.id) > 1)
            .subquery()
        )

        result = await self.db.execute(select(func.count()).select_from(subquery))
        reingresos = result.scalar() or 0
        tasa_reingreso = (
            (reingresos / total_pacientes * 100) if total_pacientes > 0 else 0
        )

        # Tasa de complicaciones (simulado)
        tasa_complicaciones = 2.5

        # Adherencia a protocolos (simulado)
        adherencia_protocolos = 92.3

        # Diagnósticos confirmados
        result = await self.db.execute(
            select(func.count(Diagnostico.id)).where(
                and_(
                    func.date(Diagnostico.created_at) >= fecha_inicio,
                    func.date(Diagnostico.created_at) <= fecha_fin,
                )
            )
        )
        total_diagnosticos = result.scalar() or 1

        result = await self.db.execute(
            select(func.count(Diagnostico.id)).where(
                and_(
                    func.date(Diagnostico.created_at) >= fecha_inicio,
                    func.date(Diagnostico.created_at) <= fecha_fin,
                    Diagnostico.estado == "confirmado",
                )
            )
        )
        diagnosticos_confirmados_count = result.scalar() or 0
        diagnosticos_confirmados = (
            (diagnosticos_confirmados_count / total_diagnosticos * 100)
            if total_diagnosticos > 0
            else 0
        )

        return IndicadoresCalidad(
            tiempo_promedio_atencion=tiempo_promedio_atencion,
            tiempo_espera_promedio=tiempo_espera_promedio,
            satisfaccion_paciente=None,
            tasa_reingreso=round(tasa_reingreso, 2),
            tasa_complicaciones=tasa_complicaciones,
            adherencia_protocolos=adherencia_protocolos,
            diagnosticos_confirmados=round(diagnosticos_confirmados, 2),
        )

    async def _get_tiempos_atencion(
        self, fecha_inicio: date, fecha_fin: date
    ) -> TiemposAtencion:
        """Calcula métricas de tiempos de atención"""

        # En producción, estos datos vendrían de logs de tiempo real
        # Por ahora simulamos datos realistas

        tiempo_promedio_consulta = 25.5
        tiempo_minimo = 10.0
        tiempo_maximo = 60.0
        tiempo_mediano = 23.0

        por_tipo_consulta = {
            "primera_vez": 35.2,
            "seguimiento": 18.5,
            "urgencia": 28.7,
            "interconsulta": 22.3,
        }

        por_medico = [
            {"medico": "Dr. García", "tiempo_promedio": 24.5, "consultas": 45},
            {"medico": "Dra. Martínez", "tiempo_promedio": 26.8, "consultas": 38},
            {"medico": "Dr. López", "tiempo_promedio": 23.2, "consultas": 52},
        ]

        distribucion_horaria = [
            {"hora": "08:00", "consultas": 5, "tiempo_promedio": 22.0},
            {"hora": "09:00", "consultas": 8, "tiempo_promedio": 24.5},
            {"hora": "10:00", "consultas": 12, "tiempo_promedio": 26.3},
            {"hora": "11:00", "consultas": 10, "tiempo_promedio": 25.8},
            {"hora": "12:00", "consultas": 7, "tiempo_promedio": 23.5},
            {"hora": "14:00", "consultas": 9, "tiempo_promedio": 24.2},
            {"hora": "15:00", "consultas": 11, "tiempo_promedio": 27.1},
            {"hora": "16:00", "consultas": 8, "tiempo_promedio": 25.5},
        ]

        return TiemposAtencion(
            tiempo_promedio_consulta=tiempo_promedio_consulta,
            tiempo_minimo=tiempo_minimo,
            tiempo_maximo=tiempo_maximo,
            tiempo_mediano=tiempo_mediano,
            por_tipo_consulta=por_tipo_consulta,
            por_medico=por_medico,
            distribucion_horaria=distribucion_horaria,
        )

    async def _get_estadisticas_diagnosticos(
        self, fecha_inicio: date, fecha_fin: date
    ) -> EstadisticasDiagnosticos:
        """Obtiene estadísticas de diagnósticos"""

        # Total de diagnósticos
        result = await self.db.execute(
            select(func.count(Diagnostico.id)).where(
                and_(
                    func.date(Diagnostico.created_at) >= fecha_inicio,
                    func.date(Diagnostico.created_at) <= fecha_fin,
                )
            )
        )
        total = result.scalar() or 0

        # Por tipo
        result = await self.db.execute(
            select(Diagnostico.tipo, func.count(Diagnostico.id).label("count"))
            .where(
                and_(
                    func.date(Diagnostico.created_at) >= fecha_inicio,
                    func.date(Diagnostico.created_at) <= fecha_fin,
                )
            )
            .group_by(Diagnostico.tipo)
        )
        por_tipo = {row[0] or "sin_tipo": row[1] for row in result.all()}

        # Top diagnósticos
        result = await self.db.execute(
            select(
                Diagnostico.descripcion,
                Diagnostico.codigo_cie10,
                func.count(Diagnostico.id).label("count"),
            )
            .where(
                and_(
                    func.date(Diagnostico.created_at) >= fecha_inicio,
                    func.date(Diagnostico.created_at) <= fecha_fin,
                )
            )
            .group_by(Diagnostico.descripcion, Diagnostico.codigo_cie10)
            .order_by(func.count(Diagnostico.id).desc())
            .limit(10)
        )
        top_diagnosticos = [
            {"descripcion": row[0], "codigo_cie10": row[1], "count": row[2]}
            for row in result.all()
        ]

        # Por categoría CIE-10 (primera letra del código)
        result = await self.db.execute(
            select(
                func.substr(Diagnostico.codigo_cie10, 1, 1).label("categoria"),
                func.count(Diagnostico.id).label("count"),
            )
            .where(
                and_(
                    func.date(Diagnostico.created_at) >= fecha_inicio,
                    func.date(Diagnostico.created_at) <= fecha_fin,
                    Diagnostico.codigo_cie10.isnot(None),
                )
            )
            .group_by("categoria")
        )
        por_categoria_cie10 = {row[0]: row[1] for row in result.all()}

        # Tasa de confirmación
        result = await self.db.execute(
            select(func.count(Diagnostico.id)).where(
                and_(
                    func.date(Diagnostico.created_at) >= fecha_inicio,
                    func.date(Diagnostico.created_at) <= fecha_fin,
                    Diagnostico.estado == "confirmado",
                )
            )
        )
        confirmados = result.scalar() or 0
        tasa_confirmacion = (confirmados / total * 100) if total > 0 else 0

        return EstadisticasDiagnosticos(
            total=total,
            por_tipo=por_tipo,
            top_diagnosticos=top_diagnosticos,
            por_categoria_cie10=por_categoria_cie10,
            tasa_confirmacion=round(tasa_confirmacion, 2),
        )

    async def _get_estadisticas_hospitalizacion(
        self, fecha_inicio: date, fecha_fin: date
    ) -> EstadisticasHospitalizacion:
        """Obtiene estadísticas de hospitalización"""

        # Total de hospitalizaciones
        result = await self.db.execute(
            select(func.count(Hospitalizacion.id)).where(
                and_(
                    func.date(Hospitalizacion.fecha_ingreso) >= fecha_inicio,
                    func.date(Hospitalizacion.fecha_ingreso) <= fecha_fin,
                )
            )
        )
        total_hospitalizaciones = result.scalar() or 0

        # Ocupación actual de camas
        result = await self.db.execute(select(func.count(Cama.id)))
        total_camas = result.scalar() or 1

        result = await self.db.execute(
            select(func.count(Cama.id)).where(Cama.estado == "ocupada")
        )
        camas_ocupadas = result.scalar() or 0
        ocupacion_actual = (
            (camas_ocupadas / total_camas * 100) if total_camas > 0 else 0
        )

        # Estancia promedio
        result = await self.db.execute(
            select(
                func.avg(
                    func.extract(
                        "epoch",
                        func.coalesce(Hospitalizacion.fecha_alta, func.now())
                        - Hospitalizacion.fecha_ingreso,
                    )
                    / 86400
                )
            ).where(
                and_(
                    func.date(Hospitalizacion.fecha_ingreso) >= fecha_inicio,
                    func.date(Hospitalizacion.fecha_ingreso) <= fecha_fin,
                )
            )
        )
        estancia_promedio = result.scalar() or 0

        # Por servicio (usando area_hospitalizacion)
        result = await self.db.execute(
            select(
                Hospitalizacion.area_hospitalizacion,
                func.count(Hospitalizacion.id).label("count"),
            )
            .where(
                and_(
                    func.date(Hospitalizacion.fecha_ingreso) >= fecha_inicio,
                    func.date(Hospitalizacion.fecha_ingreso) <= fecha_fin,
                )
            )
            .group_by(Hospitalizacion.area_hospitalizacion)
        )
        por_servicio = {row[0] or "sin_area": row[1] for row in result.all()}

        # Altas del mes
        primer_dia_mes = date.today().replace(day=1)
        result = await self.db.execute(
            select(func.count(Hospitalizacion.id)).where(
                and_(
                    Hospitalizacion.fecha_alta.isnot(None),
                    func.date(Hospitalizacion.fecha_alta) >= primer_dia_mes,
                )
            )
        )
        altas_mes = result.scalar() or 0

        # Reingresos (simulado)
        reingresos = int(total_hospitalizaciones * 0.08)

        return EstadisticasHospitalizacion(
            total_hospitalizaciones=total_hospitalizaciones,
            ocupacion_actual=round(ocupacion_actual, 2),
            estancia_promedio=round(estancia_promedio, 2),
            por_servicio=por_servicio,
            altas_mes=altas_mes,
            reingresos=reingresos,
        )
