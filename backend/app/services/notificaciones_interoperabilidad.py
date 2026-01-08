"""
Servicio de Notificaciones para Interoperabilidad
Gestión de notificaciones push en tiempo real
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func

from app.models.notificacion_interoperabilidad import (
    NotificacionInteroperabilidad,
    TipoNotificacion,
    PrioridadNotificacion,
)
from app.models.interoperabilidad import SolicitudIntercambio, InstitucionExterna
from app.models.usuario import Usuario


class NotificacionesInteroperabilidadService:
    """Servicio para gestionar notificaciones de interoperabilidad"""

    @staticmethod
    async def crear_notificacion(
        db: AsyncSession,
        tipo: TipoNotificacion,
        titulo: str,
        mensaje: str,
        usuario_id: UUID,
        prioridad: PrioridadNotificacion = PrioridadNotificacion.MEDIA,
        solicitud_id: Optional[UUID] = None,
        institucion_id: Optional[UUID] = None,
        accion_url: Optional[str] = None,
        accion_texto: Optional[str] = None,
        datos_adicionales: Optional[str] = None,
    ) -> NotificacionInteroperabilidad:
        """
        Crea una nueva notificación

        Args:
            db: Sesión de base de datos
            tipo: Tipo de notificación
            titulo: Título de la notificación
            mensaje: Mensaje de la notificación
            usuario_id: ID del usuario destinatario
            prioridad: Prioridad de la notificación
            solicitud_id: ID de la solicitud relacionada (opcional)
            institucion_id: ID de la institución relacionada (opcional)
            accion_url: URL para acción relacionada (opcional)
            accion_texto: Texto del botón de acción (opcional)
            datos_adicionales: Datos adicionales en JSON (opcional)

        Returns:
            Notificación creada
        """
        notificacion = NotificacionInteroperabilidad(
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            usuario_id=usuario_id,
            prioridad=prioridad,
            solicitud_id=solicitud_id,
            institucion_id=institucion_id,
            accion_url=accion_url,
            accion_texto=accion_texto,
            datos_adicionales=datos_adicionales,
        )

        db.add(notificacion)
        await db.commit()
        await db.refresh(notificacion)

        return notificacion

    @staticmethod
    async def notificar_solicitud_nueva(
        db: AsyncSession,
        solicitud: SolicitudIntercambio,
        usuarios_notificar: List[UUID],
    ) -> List[NotificacionInteroperabilidad]:
        """
        Notifica sobre una nueva solicitud de intercambio

        Args:
            db: Sesión de base de datos
            solicitud: Solicitud creada
            usuarios_notificar: Lista de IDs de usuarios a notificar

        Returns:
            Lista de notificaciones creadas
        """
        notificaciones = []

        for usuario_id in usuarios_notificar:
            notificacion = await NotificacionesInteroperabilidadService.crear_notificacion(
                db=db,
                tipo=TipoNotificacion.SOLICITUD_NUEVA,
                titulo="Nueva Solicitud de Intercambio",
                mensaje=f"Se ha recibido una nueva solicitud de intercambio de tipo {solicitud.tipo_intercambio}",
                usuario_id=usuario_id,
                prioridad=(
                    PrioridadNotificacion.ALTA
                    if solicitud.prioridad == "urgente"
                    else PrioridadNotificacion.MEDIA
                ),
                solicitud_id=solicitud.id,
                accion_url=f"/interoperabilidad?tab=solicitudes&id={solicitud.id}",
                accion_texto="Ver Solicitud",
            )
            notificaciones.append(notificacion)

        return notificaciones

    @staticmethod
    async def notificar_solicitud_aprobada(
        db: AsyncSession, solicitud: SolicitudIntercambio, usuario_id: UUID
    ) -> NotificacionInteroperabilidad:
        """Notifica que una solicitud fue aprobada"""
        return await NotificacionesInteroperabilidadService.crear_notificacion(
            db=db,
            tipo=TipoNotificacion.SOLICITUD_APROBADA,
            titulo="Solicitud Aprobada",
            mensaje=f"La solicitud de intercambio ha sido aprobada",
            usuario_id=usuario_id,
            prioridad=PrioridadNotificacion.MEDIA,
            solicitud_id=solicitud.id,
            accion_url=f"/interoperabilidad?tab=solicitudes&id={solicitud.id}",
            accion_texto="Ver Solicitud",
        )

    @staticmethod
    async def notificar_solicitud_rechazada(
        db: AsyncSession, solicitud: SolicitudIntercambio, usuario_id: UUID, motivo: str
    ) -> NotificacionInteroperabilidad:
        """Notifica que una solicitud fue rechazada"""
        return await NotificacionesInteroperabilidadService.crear_notificacion(
            db=db,
            tipo=TipoNotificacion.SOLICITUD_RECHAZADA,
            titulo="Solicitud Rechazada",
            mensaje=f"La solicitud de intercambio ha sido rechazada. Motivo: {motivo}",
            usuario_id=usuario_id,
            prioridad=PrioridadNotificacion.ALTA,
            solicitud_id=solicitud.id,
            accion_url=f"/interoperabilidad?tab=solicitudes&id={solicitud.id}",
            accion_texto="Ver Solicitud",
        )

    @staticmethod
    async def notificar_solicitud_completada(
        db: AsyncSession, solicitud: SolicitudIntercambio, usuario_id: UUID
    ) -> NotificacionInteroperabilidad:
        """Notifica que una solicitud fue completada"""
        return await NotificacionesInteroperabilidadService.crear_notificacion(
            db=db,
            tipo=TipoNotificacion.SOLICITUD_COMPLETADA,
            titulo="Solicitud Completada",
            mensaje=f"La solicitud de intercambio ha sido completada exitosamente",
            usuario_id=usuario_id,
            prioridad=PrioridadNotificacion.MEDIA,
            solicitud_id=solicitud.id,
            accion_url=f"/interoperabilidad?tab=solicitudes&id={solicitud.id}",
            accion_texto="Ver Solicitud",
        )

    @staticmethod
    async def notificar_solicitud_error(
        db: AsyncSession, solicitud: SolicitudIntercambio, usuario_id: UUID, error: str
    ) -> NotificacionInteroperabilidad:
        """Notifica que una solicitud tuvo un error"""
        return await NotificacionesInteroperabilidadService.crear_notificacion(
            db=db,
            tipo=TipoNotificacion.SOLICITUD_ERROR,
            titulo="Error en Solicitud",
            mensaje=f"Ha ocurrido un error en la solicitud de intercambio: {error}",
            usuario_id=usuario_id,
            prioridad=PrioridadNotificacion.URGENTE,
            solicitud_id=solicitud.id,
            accion_url=f"/interoperabilidad?tab=solicitudes&id={solicitud.id}",
            accion_texto="Ver Solicitud",
        )

    @staticmethod
    async def notificar_consentimiento_expira(
        db: AsyncSession, paciente_nombre: str, dias_restantes: int, usuario_id: UUID
    ) -> NotificacionInteroperabilidad:
        """Notifica que un consentimiento está próximo a expirar"""
        return await NotificacionesInteroperabilidadService.crear_notificacion(
            db=db,
            tipo=TipoNotificacion.CONSENTIMIENTO_EXPIRA,
            titulo="Consentimiento Próximo a Expirar",
            mensaje=f"El consentimiento del paciente {paciente_nombre} expira en {dias_restantes} días",
            usuario_id=usuario_id,
            prioridad=PrioridadNotificacion.MEDIA,
            accion_url="/interoperabilidad?tab=consentimientos",
            accion_texto="Ver Consentimientos",
        )

    @staticmethod
    async def obtener_notificaciones_usuario(
        db: AsyncSession,
        usuario_id: UUID,
        solo_no_leidas: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> List[NotificacionInteroperabilidad]:
        """
        Obtiene las notificaciones de un usuario

        Args:
            db: Sesión de base de datos
            usuario_id: ID del usuario
            solo_no_leidas: Si True, solo retorna notificaciones no leídas
            limit: Límite de resultados
            offset: Offset para paginación

        Returns:
            Lista de notificaciones
        """
        query = select(NotificacionInteroperabilidad).where(
            NotificacionInteroperabilidad.usuario_id == usuario_id
        )

        if solo_no_leidas:
            query = query.where(NotificacionInteroperabilidad.leida == False)

        query = query.order_by(desc(NotificacionInteroperabilidad.created_at))
        query = query.limit(limit).offset(offset)

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def contar_notificaciones_no_leidas(
        db: AsyncSession, usuario_id: UUID
    ) -> int:
        """
        Cuenta las notificaciones no leídas de un usuario

        Args:
            db: Sesión de base de datos
            usuario_id: ID del usuario

        Returns:
            Número de notificaciones no leídas
        """
        query = select(func.count(NotificacionInteroperabilidad.id)).where(
            and_(
                NotificacionInteroperabilidad.usuario_id == usuario_id,
                NotificacionInteroperabilidad.leida == False,
            )
        )

        result = await db.execute(query)
        return result.scalar() or 0

    @staticmethod
    async def marcar_como_leida(
        db: AsyncSession, notificacion_id: UUID, usuario_id: UUID
    ) -> Optional[NotificacionInteroperabilidad]:
        """
        Marca una notificación como leída

        Args:
            db: Sesión de base de datos
            notificacion_id: ID de la notificación
            usuario_id: ID del usuario (para verificar permisos)

        Returns:
            Notificación actualizada o None si no se encontró
        """
        query = select(NotificacionInteroperabilidad).where(
            and_(
                NotificacionInteroperabilidad.id == notificacion_id,
                NotificacionInteroperabilidad.usuario_id == usuario_id,
            )
        )

        result = await db.execute(query)
        notificacion = result.scalar_one_or_none()

        if notificacion:
            notificacion.marcar_como_leida()
            await db.commit()
            await db.refresh(notificacion)

        return notificacion

    @staticmethod
    async def marcar_todas_como_leidas(db: AsyncSession, usuario_id: UUID) -> int:
        """
        Marca todas las notificaciones de un usuario como leídas

        Args:
            db: Sesión de base de datos
            usuario_id: ID del usuario

        Returns:
            Número de notificaciones marcadas
        """
        query = select(NotificacionInteroperabilidad).where(
            and_(
                NotificacionInteroperabilidad.usuario_id == usuario_id,
                NotificacionInteroperabilidad.leida == False,
            )
        )

        result = await db.execute(query)
        notificaciones = result.scalars().all()

        for notificacion in notificaciones:
            notificacion.marcar_como_leida()

        await db.commit()

        return len(notificaciones)

    @staticmethod
    async def eliminar_notificacion(
        db: AsyncSession, notificacion_id: UUID, usuario_id: UUID
    ) -> bool:
        """
        Elimina una notificación

        Args:
            db: Sesión de base de datos
            notificacion_id: ID de la notificación
            usuario_id: ID del usuario (para verificar permisos)

        Returns:
            True si se eliminó, False si no se encontró
        """
        query = select(NotificacionInteroperabilidad).where(
            and_(
                NotificacionInteroperabilidad.id == notificacion_id,
                NotificacionInteroperabilidad.usuario_id == usuario_id,
            )
        )

        result = await db.execute(query)
        notificacion = result.scalar_one_or_none()

        if notificacion:
            await db.delete(notificacion)
            await db.commit()
            return True

        return False

    @staticmethod
    async def limpiar_notificaciones_antiguas(db: AsyncSession, dias: int = 30) -> int:
        """
        Elimina notificaciones leídas más antiguas que X días

        Args:
            db: Sesión de base de datos
            dias: Días de antigüedad

        Returns:
            Número de notificaciones eliminadas
        """
        fecha_limite = datetime.utcnow() - timedelta(days=dias)

        query = select(NotificacionInteroperabilidad).where(
            and_(
                NotificacionInteroperabilidad.leida == True,
                NotificacionInteroperabilidad.created_at < fecha_limite,
            )
        )

        result = await db.execute(query)
        notificaciones = result.scalars().all()

        for notificacion in notificaciones:
            await db.delete(notificacion)

        await db.commit()

        return len(notificaciones)
