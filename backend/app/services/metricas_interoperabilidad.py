"""
Servicio de Métricas en Tiempo Real para Interoperabilidad
Calcula y proporciona métricas avanzadas del sistema
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case
from app.models.interoperabilidad import (
    InstitucionExterna,
    SolicitudIntercambio,
    HistoriaClinicaUnificada,
    ConsentimientoIntercambio,
    LogIntercambio,
)


class MetricasInteroperabilidadService:
    """Servicio para calcular métricas del sistema de interoperabilidad"""

    @staticmethod
    async def obtener_metricas_tiempo_real(
        db: AsyncSession, periodo_dias: int = 7
    ) -> Dict[str, Any]:
        """
        Obtiene métricas en tiempo real del sistema

        Args:
            db: Sesión de base de datos
            periodo_dias: Días hacia atrás para calcular métricas

        Returns:
            Diccionario con todas las métricas
        """
        fecha_inicio = datetime.utcnow() - timedelta(days=periodo_dias)

        # Métricas de solicitudes
        metricas_solicitudes = (
            await MetricasInteroperabilidadService._metricas_solicitudes(
                db, fecha_inicio
            )
        )

        # Métricas de instituciones
        metricas_instituciones = (
            await MetricasInteroperabilidadService._metricas_instituciones(db)
        )

        # Métricas de rendimiento
        metricas_rendimiento = (
            await MetricasInteroperabilidadService._metricas_rendimiento(
                db, fecha_inicio
            )
        )

        # Métricas de seguridad
        metricas_seguridad = await MetricasInteroperabilidadService._metricas_seguridad(
            db, fecha_inicio
        )

        # Métricas de volumen
        metricas_volumen = await MetricasInteroperabilidadService._metricas_volumen(
            db, fecha_inicio
        )

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "periodo_dias": periodo_dias,
            "solicitudes": metricas_solicitudes,
            "instituciones": metricas_instituciones,
            "rendimiento": metricas_rendimiento,
            "seguridad": metricas_seguridad,
            "volumen": metricas_volumen,
        }

    @staticmethod
    async def _metricas_solicitudes(
        db: AsyncSession, fecha_inicio: datetime
    ) -> Dict[str, Any]:
        """Calcula métricas de solicitudes de intercambio"""

        # Total de solicitudes
        query_total = select(func.count(SolicitudIntercambio.id)).where(
            SolicitudIntercambio.created_at >= fecha_inicio
        )
        total = (await db.execute(query_total)).scalar() or 0

        # Solicitudes por estado
        query_estados = (
            select(SolicitudIntercambio.estado, func.count(SolicitudIntercambio.id))
            .where(SolicitudIntercambio.created_at >= fecha_inicio)
            .group_by(SolicitudIntercambio.estado)
        )

        estados_result = await db.execute(query_estados)
        por_estado = {estado: count for estado, count in estados_result}

        # Solicitudes por prioridad
        query_prioridad = (
            select(SolicitudIntercambio.prioridad, func.count(SolicitudIntercambio.id))
            .where(SolicitudIntercambio.created_at >= fecha_inicio)
            .group_by(SolicitudIntercambio.prioridad)
        )

        prioridad_result = await db.execute(query_prioridad)
        por_prioridad = {prioridad: count for prioridad, count in prioridad_result}

        # Tiempo promedio de procesamiento (pendiente -> completada)
        query_tiempo = select(
            func.avg(
                func.extract(
                    "epoch",
                    SolicitudIntercambio.updated_at - SolicitudIntercambio.created_at,
                )
            )
        ).where(
            and_(
                SolicitudIntercambio.estado == "completada",
                SolicitudIntercambio.created_at >= fecha_inicio,
            )
        )
        tiempo_promedio_segundos = (await db.execute(query_tiempo)).scalar() or 0

        # Tasa de éxito
        completadas = por_estado.get("completada", 0)
        tasa_exito = (completadas / total * 100) if total > 0 else 0

        return {
            "total": total,
            "por_estado": por_estado,
            "por_prioridad": por_prioridad,
            "tiempo_promedio_procesamiento_horas": round(
                tiempo_promedio_segundos / 3600, 2
            ),
            "tasa_exito_porcentaje": round(tasa_exito, 2),
            "pendientes": por_estado.get("pendiente", 0),
            "en_proceso": por_estado.get("en_proceso", 0),
            "completadas": completadas,
            "rechazadas": por_estado.get("rechazada", 0),
            "con_error": por_estado.get("error", 0),
        }

    @staticmethod
    async def _metricas_instituciones(db: AsyncSession) -> Dict[str, Any]:
        """Calcula métricas de instituciones"""

        # Total de instituciones
        query_total = select(func.count(InstitucionExterna.id))
        total = (await db.execute(query_total)).scalar() or 0

        # Instituciones activas
        query_activas = select(func.count(InstitucionExterna.id)).where(
            InstitucionExterna.activa == True
        )
        activas = (await db.execute(query_activas)).scalar() or 0

        # Por nivel de atención
        query_nivel = select(
            InstitucionExterna.nivel_atencion, func.count(InstitucionExterna.id)
        ).group_by(InstitucionExterna.nivel_atencion)

        nivel_result = await db.execute(query_nivel)
        por_nivel = {nivel: count for nivel, count in nivel_result}

        # Por tipo
        query_tipo = select(
            InstitucionExterna.tipo_institucion, func.count(InstitucionExterna.id)
        ).group_by(InstitucionExterna.tipo_institucion)

        tipo_result = await db.execute(query_tipo)
        por_tipo = {tipo: count for tipo, count in tipo_result}

        # Top 5 instituciones por volumen de solicitudes
        query_top = (
            select(
                InstitucionExterna.nombre,
                func.count(SolicitudIntercambio.id).label("total_solicitudes"),
            )
            .join(
                SolicitudIntercambio,
                InstitucionExterna.id == SolicitudIntercambio.institucion_destino_id,
            )
            .group_by(InstitucionExterna.id, InstitucionExterna.nombre)
            .order_by(func.count(SolicitudIntercambio.id).desc())
            .limit(5)
        )

        top_result = await db.execute(query_top)
        top_instituciones = [
            {"nombre": nombre, "solicitudes": count} for nombre, count in top_result
        ]

        return {
            "total": total,
            "activas": activas,
            "inactivas": total - activas,
            "por_nivel_atencion": por_nivel,
            "por_tipo": por_tipo,
            "top_instituciones": top_instituciones,
        }

    @staticmethod
    async def _metricas_rendimiento(
        db: AsyncSession, fecha_inicio: datetime
    ) -> Dict[str, Any]:
        """Calcula métricas de rendimiento del sistema"""

        # Solicitudes por día
        query_por_dia = (
            select(
                func.date(SolicitudIntercambio.created_at).label("fecha"),
                func.count(SolicitudIntercambio.id).label("total"),
            )
            .where(SolicitudIntercambio.created_at >= fecha_inicio)
            .group_by(func.date(SolicitudIntercambio.created_at))
            .order_by(func.date(SolicitudIntercambio.created_at))
        )

        por_dia_result = await db.execute(query_por_dia)
        solicitudes_por_dia = [
            {"fecha": str(fecha), "total": total} for fecha, total in por_dia_result
        ]

        # Promedio diario
        promedio_diario = (
            sum(item["total"] for item in solicitudes_por_dia)
            / len(solicitudes_por_dia)
            if solicitudes_por_dia
            else 0
        )

        # Pico de carga (día con más solicitudes)
        pico_carga = (
            max(solicitudes_por_dia, key=lambda x: x["total"])
            if solicitudes_por_dia
            else None
        )

        # Disponibilidad del sistema (basado en auditoría)
        query_eventos = select(func.count(LogIntercambio.id)).where(
            LogIntercambio.timestamp >= fecha_inicio
        )
        total_eventos = (await db.execute(query_eventos)).scalar() or 0

        query_errores = select(func.count(LogIntercambio.id)).where(
            and_(
                LogIntercambio.timestamp >= fecha_inicio,
                LogIntercambio.error.isnot(None),
            )
        )
        total_errores = (await db.execute(query_errores)).scalar() or 0

        disponibilidad = (
            ((total_eventos - total_errores) / total_eventos * 100)
            if total_eventos > 0
            else 100
        )

        return {
            "solicitudes_por_dia": solicitudes_por_dia,
            "promedio_diario": round(promedio_diario, 2),
            "pico_carga": pico_carga,
            "disponibilidad_porcentaje": round(disponibilidad, 2),
            "total_eventos_auditoria": total_eventos,
            "total_errores": total_errores,
        }

    @staticmethod
    async def _metricas_seguridad(
        db: AsyncSession, fecha_inicio: datetime
    ) -> Dict[str, Any]:
        """Calcula métricas de seguridad"""

        # Total de consentimientos
        query_consentimientos = select(func.count(ConsentimientoIntercambio.id))
        total_consentimientos = (await db.execute(query_consentimientos)).scalar() or 0

        # Consentimientos activos
        query_activos = select(func.count(ConsentimientoIntercambio.id)).where(
            and_(
                ConsentimientoIntercambio.activo == True,
                ConsentimientoIntercambio.fecha_expiracion > datetime.utcnow(),
            )
        )
        consentimientos_activos = (await db.execute(query_activos)).scalar() or 0

        # Eventos de auditoría por tipo
        query_auditoria = (
            select(LogIntercambio.accion, func.count(LogIntercambio.id))
            .where(LogIntercambio.timestamp >= fecha_inicio)
            .group_by(LogIntercambio.accion)
        )

        auditoria_result = await db.execute(query_auditoria)
        eventos_por_tipo = {accion: count for accion, count in auditoria_result}

        # Intentos de acceso denegados
        accesos_denegados = eventos_por_tipo.get("acceso_denegado", 0)

        return {
            "total_consentimientos": total_consentimientos,
            "consentimientos_activos": consentimientos_activos,
            "consentimientos_expirados": total_consentimientos
            - consentimientos_activos,
            "eventos_auditoria_por_tipo": eventos_por_tipo,
            "accesos_denegados": accesos_denegados,
            "tasa_cumplimiento_porcentaje": round(
                (
                    (consentimientos_activos / total_consentimientos * 100)
                    if total_consentimientos > 0
                    else 0
                ),
                2,
            ),
        }

    @staticmethod
    async def _metricas_volumen(
        db: AsyncSession, fecha_inicio: datetime
    ) -> Dict[str, Any]:
        """Calcula métricas de volumen de datos"""

        # Total de historias clínicas unificadas
        query_historias = select(func.count(HistoriaClinicaUnificada.id))
        total_historias = (await db.execute(query_historias)).scalar() or 0

        # Historias creadas en el periodo
        query_nuevas = select(func.count(HistoriaClinicaUnificada.id)).where(
            HistoriaClinicaUnificada.created_at >= fecha_inicio
        )
        historias_nuevas = (await db.execute(query_nuevas)).scalar() or 0

        # Tamaño promedio de bundles FHIR (estimado)
        query_solicitudes_completadas = select(
            func.count(SolicitudIntercambio.id)
        ).where(
            and_(
                SolicitudIntercambio.estado == "completada",
                SolicitudIntercambio.created_at >= fecha_inicio,
            )
        )
        bundles_generados = (
            await db.execute(query_solicitudes_completadas)
        ).scalar() or 0

        # Estimación de datos transferidos (cada bundle ~50KB promedio)
        datos_transferidos_mb = round(bundles_generados * 0.05, 2)

        return {
            "total_historias_unificadas": total_historias,
            "historias_nuevas_periodo": historias_nuevas,
            "bundles_fhir_generados": bundles_generados,
            "datos_transferidos_mb": datos_transferidos_mb,
            "promedio_bundle_kb": 50,
        }

    @staticmethod
    async def obtener_alertas_sistema(db: AsyncSession) -> List[Dict[str, Any]]:
        """
        Obtiene alertas del sistema que requieren atención

        Returns:
            Lista de alertas con nivel de severidad
        """
        alertas = []

        # Solicitudes pendientes por más de 24 horas
        hace_24h = datetime.utcnow() - timedelta(hours=24)
        query_pendientes = select(func.count(SolicitudIntercambio.id)).where(
            and_(
                SolicitudIntercambio.estado == "pendiente",
                SolicitudIntercambio.created_at < hace_24h,
            )
        )
        pendientes_antiguas = (await db.execute(query_pendientes)).scalar() or 0

        if pendientes_antiguas > 0:
            alertas.append(
                {
                    "tipo": "solicitudes_pendientes",
                    "severidad": "alta" if pendientes_antiguas > 10 else "media",
                    "mensaje": f"{pendientes_antiguas} solicitudes pendientes por más de 24 horas",
                    "count": pendientes_antiguas,
                }
            )

        # Instituciones inactivas
        query_inactivas = select(func.count(InstitucionExterna.id)).where(
            InstitucionExterna.activa == False
        )
        instituciones_inactivas = (await db.execute(query_inactivas)).scalar() or 0

        if instituciones_inactivas > 0:
            alertas.append(
                {
                    "tipo": "instituciones_inactivas",
                    "severidad": "baja",
                    "mensaje": f"{instituciones_inactivas} instituciones inactivas en la red",
                    "count": instituciones_inactivas,
                }
            )

        # Consentimientos próximos a expirar (7 días)
        en_7_dias = datetime.utcnow() + timedelta(days=7)
        query_expiran = select(func.count(ConsentimientoIntercambio.id)).where(
            and_(
                ConsentimientoIntercambio.activo == True,
                ConsentimientoIntercambio.fecha_expiracion <= en_7_dias,
                ConsentimientoIntercambio.fecha_expiracion > datetime.utcnow(),
            )
        )
        consentimientos_expiran = (await db.execute(query_expiran)).scalar() or 0

        if consentimientos_expiran > 0:
            alertas.append(
                {
                    "tipo": "consentimientos_expiran",
                    "severidad": "media",
                    "mensaje": f"{consentimientos_expiran} consentimientos expiran en los próximos 7 días",
                    "count": consentimientos_expiran,
                }
            )

        # Solicitudes con errores
        query_errores = select(func.count(SolicitudIntercambio.id)).where(
            SolicitudIntercambio.estado == "error"
        )
        solicitudes_error = (await db.execute(query_errores)).scalar() or 0

        if solicitudes_error > 0:
            alertas.append(
                {
                    "tipo": "solicitudes_error",
                    "severidad": "alta",
                    "mensaje": f"{solicitudes_error} solicitudes en estado de error",
                    "count": solicitudes_error,
                }
            )

        return alertas
