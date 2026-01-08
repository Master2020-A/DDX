"""
Servicio para auditoría completa de acciones
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from uuid import UUID
from fastapi import Request

from app.models.security import AuditLog
from app.models.usuario import Usuario


class AuditService:
    """Servicio para registro y consulta de auditoría"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_action(
        self,
        accion: str,
        recurso: str,
        usuario_id: Optional[UUID] = None,
        recurso_id: Optional[str] = None,
        descripcion: Optional[str] = None,
        datos_anteriores: Optional[Dict[str, Any]] = None,
        datos_nuevos: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metodo_http: Optional[str] = None,
        endpoint: Optional[str] = None,
        exitoso: bool = True,
        codigo_estado: Optional[int] = None,
        mensaje_error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """
        Registra una acción en el log de auditoría
        """
        audit_log = AuditLog(
            usuario_id=usuario_id,
            accion=accion,
            recurso=recurso,
            recurso_id=str(recurso_id) if recurso_id else None,
            descripcion=descripcion,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos,
            ip_address=ip_address,
            user_agent=user_agent,
            metodo_http=metodo_http,
            endpoint=endpoint,
            exitoso=exitoso,
            codigo_estado=codigo_estado,
            mensaje_error=mensaje_error,
            metadata_extra=metadata,
        )

        self.db.add(audit_log)
        await self.db.commit()
        await self.db.refresh(audit_log)

        return audit_log

    async def log_from_request(
        self,
        request: Request,
        accion: str,
        recurso: str,
        usuario_id: Optional[UUID] = None,
        recurso_id: Optional[str] = None,
        descripcion: Optional[str] = None,
        datos_anteriores: Optional[Dict[str, Any]] = None,
        datos_nuevos: Optional[Dict[str, Any]] = None,
        exitoso: bool = True,
        codigo_estado: Optional[int] = None,
        mensaje_error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """
        Registra una acción extrayendo información del request
        """
        # Extraer información del request
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        metodo_http = request.method
        endpoint = str(request.url.path)

        return await self.log_action(
            accion=accion,
            recurso=recurso,
            usuario_id=usuario_id,
            recurso_id=recurso_id,
            descripcion=descripcion,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos,
            ip_address=ip_address,
            user_agent=user_agent,
            metodo_http=metodo_http,
            endpoint=endpoint,
            exitoso=exitoso,
            codigo_estado=codigo_estado,
            mensaje_error=mensaje_error,
            metadata_extra=metadata,
        )

    async def get_logs(
        self,
        usuario_id: Optional[UUID] = None,
        accion: Optional[str] = None,
        recurso: Optional[str] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        exitoso: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditLog]:
        """
        Obtiene logs de auditoría con filtros
        """
        query = select(AuditLog)

        conditions = []

        if usuario_id:
            conditions.append(AuditLog.usuario_id == usuario_id)

        if accion:
            conditions.append(AuditLog.accion == accion)

        if recurso:
            conditions.append(AuditLog.recurso == recurso)

        if fecha_inicio:
            conditions.append(func.date(AuditLog.created_at) >= fecha_inicio)

        if fecha_fin:
            conditions.append(func.date(AuditLog.created_at) <= fecha_fin)

        if exitoso is not None:
            conditions.append(AuditLog.exitoso == exitoso)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_user_activity(
        self,
        usuario_id: UUID,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        limit: int = 50,
    ) -> List[AuditLog]:
        """
        Obtiene la actividad de un usuario específico
        """
        return await self.get_logs(
            usuario_id=usuario_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            limit=limit,
        )

    async def get_resource_history(
        self,
        recurso: str,
        recurso_id: str,
        limit: int = 50,
    ) -> List[AuditLog]:
        """
        Obtiene el historial de cambios de un recurso específico
        """
        query = (
            select(AuditLog)
            .where(
                and_(
                    AuditLog.recurso == recurso,
                    AuditLog.recurso_id == recurso_id,
                )
            )
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_failed_actions(
        self,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        limit: int = 100,
    ) -> List[AuditLog]:
        """
        Obtiene acciones fallidas para análisis de seguridad
        """
        return await self.get_logs(
            exitoso=False,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            limit=limit,
        )

    async def get_statistics(
        self,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de auditoría
        """
        conditions = []

        if fecha_inicio:
            conditions.append(func.date(AuditLog.created_at) >= fecha_inicio)

        if fecha_fin:
            conditions.append(func.date(AuditLog.created_at) <= fecha_fin)

        # Total de acciones
        query = select(func.count(AuditLog.id))
        if conditions:
            query = query.where(and_(*conditions))
        result = await self.db.execute(query)
        total_acciones = result.scalar() or 0

        # Acciones exitosas
        query = select(func.count(AuditLog.id)).where(AuditLog.exitoso == True)
        if conditions:
            query = query.where(and_(*conditions))
        result = await self.db.execute(query)
        acciones_exitosas = result.scalar() or 0

        # Acciones fallidas
        query = select(func.count(AuditLog.id)).where(AuditLog.exitoso == False)
        if conditions:
            query = query.where(and_(*conditions))
        result = await self.db.execute(query)
        acciones_fallidas = result.scalar() or 0

        # Por acción
        query = select(
            AuditLog.accion, func.count(AuditLog.id).label("count")
        ).group_by(AuditLog.accion)
        if conditions:
            query = query.where(and_(*conditions))
        result = await self.db.execute(query)
        por_accion = {row[0]: row[1] for row in result.all()}

        # Por recurso
        query = select(
            AuditLog.recurso, func.count(AuditLog.id).label("count")
        ).group_by(AuditLog.recurso)
        if conditions:
            query = query.where(and_(*conditions))
        result = await self.db.execute(query)
        por_recurso = {row[0]: row[1] for row in result.all()}

        # Usuarios más activos
        query = (
            select(AuditLog.usuario_id, func.count(AuditLog.id).label("count"))
            .where(AuditLog.usuario_id.isnot(None))
            .group_by(AuditLog.usuario_id)
            .order_by(func.count(AuditLog.id).desc())
            .limit(10)
        )
        if conditions:
            query = query.where(and_(*conditions))
        result = await self.db.execute(query)
        usuarios_activos = [
            {"usuario_id": str(row[0]), "acciones": row[1]} for row in result.all()
        ]

        return {
            "total_acciones": total_acciones,
            "acciones_exitosas": acciones_exitosas,
            "acciones_fallidas": acciones_fallidas,
            "tasa_exito": (
                (acciones_exitosas / total_acciones * 100) if total_acciones > 0 else 0
            ),
            "por_accion": por_accion,
            "por_recurso": por_recurso,
            "usuarios_activos": usuarios_activos,
        }
