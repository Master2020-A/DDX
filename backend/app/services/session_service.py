"""
Servicio para gestión de sesiones y control de sesiones concurrentes
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
import secrets

from app.models.security import UserSession
from app.models.usuario import Usuario


class SessionService:
    """Servicio para gestión de sesiones de usuario"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.max_concurrent_sessions = 3  # Límite de sesiones concurrentes

    async def create_session(
        self,
        usuario_id: UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_info: Optional[Dict[str, Any]] = None,
        location: Optional[str] = None,
        expires_in_hours: int = 24,
    ) -> UserSession:
        """
        Crea una nueva sesión para un usuario
        """
        # Verificar límite de sesiones concurrentes
        await self._enforce_session_limit(usuario_id)

        # Generar tokens
        session_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)

        # Calcular expiración
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)

        # Crear sesión
        session = UserSession(
            usuario_id=usuario_id,
            session_token=session_token,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
            device_info=device_info,
            location=location,
            activa=True,
            expires_at=expires_at,
        )

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        return session

    async def _enforce_session_limit(self, usuario_id: UUID):
        """
        Revoca sesiones antiguas si se excede el límite
        """
        # Obtener sesiones activas
        result = await self.db.execute(
            select(UserSession)
            .where(
                and_(
                    UserSession.usuario_id == usuario_id,
                    UserSession.activa == True,
                    UserSession.revocada == False,
                    UserSession.expires_at > datetime.utcnow(),
                )
            )
            .order_by(UserSession.last_activity_at.desc())
        )
        sessions = result.scalars().all()

        # Si hay más sesiones que el límite, revocar las más antiguas
        if len(sessions) >= self.max_concurrent_sessions:
            sessions_to_revoke = sessions[self.max_concurrent_sessions - 1 :]
            for session in sessions_to_revoke:
                session.activa = False
                session.revocada = True
                session.motivo_revocacion = "Límite de sesiones concurrentes excedido"
                session.revoked_at = datetime.utcnow()

            await self.db.commit()

    async def get_session(self, session_token: str) -> Optional[UserSession]:
        """
        Obtiene una sesión por su token
        """
        result = await self.db.execute(
            select(UserSession).where(UserSession.session_token == session_token)
        )
        return result.scalar_one_or_none()

    async def validate_session(self, session_token: str) -> Optional[UserSession]:
        """
        Valida una sesión y actualiza su última actividad
        """
        session = await self.get_session(session_token)

        if not session:
            return None

        # Verificar si la sesión está activa y no ha expirado
        if (
            not session.activa
            or session.revocada
            or session.expires_at < datetime.utcnow()
        ):
            return None

        # Actualizar última actividad
        session.last_activity_at = datetime.utcnow()
        await self.db.commit()

        return session

    async def revoke_session(
        self, session_token: str, motivo: str = "Revocada por usuario"
    ) -> bool:
        """
        Revoca una sesión específica
        """
        session = await self.get_session(session_token)

        if not session:
            return False

        session.activa = False
        session.revocada = True
        session.motivo_revocacion = motivo
        session.revoked_at = datetime.utcnow()

        await self.db.commit()
        return True

    async def revoke_all_user_sessions(
        self, usuario_id: UUID, except_token: Optional[str] = None
    ) -> int:
        """
        Revoca todas las sesiones de un usuario excepto una opcional
        """
        query = select(UserSession).where(
            and_(
                UserSession.usuario_id == usuario_id,
                UserSession.activa == True,
                UserSession.revocada == False,
            )
        )

        if except_token:
            query = query.where(UserSession.session_token != except_token)

        result = await self.db.execute(query)
        sessions = result.scalars().all()

        count = 0
        for session in sessions:
            session.activa = False
            session.revocada = True
            session.motivo_revocacion = "Revocada por usuario"
            session.revoked_at = datetime.utcnow()
            count += 1

        await self.db.commit()
        return count

    async def get_user_sessions(
        self, usuario_id: UUID, include_inactive: bool = False
    ) -> List[UserSession]:
        """
        Obtiene todas las sesiones de un usuario
        """
        query = select(UserSession).where(UserSession.usuario_id == usuario_id)

        if not include_inactive:
            query = query.where(
                and_(
                    UserSession.activa == True,
                    UserSession.revocada == False,
                    UserSession.expires_at > datetime.utcnow(),
                )
            )

        query = query.order_by(UserSession.last_activity_at.desc())

        result = await self.db.execute(query)
        return result.scalars().all()

    async def refresh_session(self, refresh_token: str) -> Optional[UserSession]:
        """
        Renueva una sesión usando el refresh token
        """
        result = await self.db.execute(
            select(UserSession).where(UserSession.refresh_token == refresh_token)
        )
        session = result.scalar_one_or_none()

        if not session or not session.activa or session.revocada:
            return None

        # Generar nuevos tokens
        session.session_token = secrets.token_urlsafe(32)
        session.refresh_token = secrets.token_urlsafe(32)

        # Extender expiración
        session.expires_at = datetime.utcnow() + timedelta(hours=24)
        session.last_activity_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(session)

        return session

    async def cleanup_expired_sessions(self) -> int:
        """
        Limpia sesiones expiradas
        """
        result = await self.db.execute(
            select(UserSession).where(
                and_(
                    UserSession.activa == True,
                    UserSession.expires_at < datetime.utcnow(),
                )
            )
        )
        sessions = result.scalars().all()

        count = 0
        for session in sessions:
            session.activa = False
            session.revocada = True
            session.motivo_revocacion = "Sesión expirada"
            session.revoked_at = datetime.utcnow()
            count += 1

        await self.db.commit()
        return count

    async def get_session_statistics(self, usuario_id: UUID) -> Dict[str, Any]:
        """
        Obtiene estadísticas de sesiones de un usuario
        """
        # Total de sesiones
        result = await self.db.execute(
            select(func.count(UserSession.id)).where(
                UserSession.usuario_id == usuario_id
            )
        )
        total_sessions = result.scalar() or 0

        # Sesiones activas
        result = await self.db.execute(
            select(func.count(UserSession.id)).where(
                and_(
                    UserSession.usuario_id == usuario_id,
                    UserSession.activa == True,
                    UserSession.revocada == False,
                    UserSession.expires_at > datetime.utcnow(),
                )
            )
        )
        active_sessions = result.scalar() or 0

        # Última actividad
        result = await self.db.execute(
            select(func.max(UserSession.last_activity_at)).where(
                UserSession.usuario_id == usuario_id
            )
        )
        last_activity = result.scalar()

        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "last_activity": last_activity.isoformat() if last_activity else None,
            "max_concurrent_sessions": self.max_concurrent_sessions,
        }
