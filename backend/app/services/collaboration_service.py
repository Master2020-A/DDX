"""
Servicio de Colaboración en Tiempo Real con WebSockets
"""

from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import Dict, List, Set, Optional
from uuid import UUID
from datetime import datetime, timedelta
import json
import asyncio

from app.models.collaboration import (
    WorkflowCollaborator,
    CollaborationSession,
    WorkflowChange,
    ChatMessage,
    WorkflowLock,
)


class ConnectionManager:
    """Gestor de conexiones WebSocket"""

    def __init__(self):
        # workflow_id -> set of websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # connection_id -> session info
        self.sessions: Dict[str, dict] = {}
        # websocket -> connection_id
        self.ws_to_connection: Dict[WebSocket, str] = {}

    async def connect(
        self,
        websocket: WebSocket,
        workflow_id: str,
        user_id: str,
        user_name: str,
        connection_id: str,
    ):
        """Conectar un nuevo cliente"""
        await websocket.accept()

        # Agregar a conexiones activas
        if workflow_id not in self.active_connections:
            self.active_connections[workflow_id] = set()
        self.active_connections[workflow_id].add(websocket)

        # Guardar sesión
        self.sessions[connection_id] = {
            "workflow_id": workflow_id,
            "user_id": user_id,
            "user_name": user_name,
            "websocket": websocket,
            "connected_at": datetime.utcnow().isoformat(),
            "color": self._generate_color(user_id),
        }
        self.ws_to_connection[websocket] = connection_id

    def disconnect(self, websocket: WebSocket):
        """Desconectar un cliente"""
        connection_id = self.ws_to_connection.get(websocket)
        if not connection_id:
            return None

        session = self.sessions.get(connection_id)
        if not session:
            return None

        workflow_id = session["workflow_id"]

        # Remover de conexiones activas
        if workflow_id in self.active_connections:
            self.active_connections[workflow_id].discard(websocket)
            if not self.active_connections[workflow_id]:
                del self.active_connections[workflow_id]

        # Limpiar sesión
        del self.ws_to_connection[websocket]
        del self.sessions[connection_id]

        return session

    async def broadcast_to_workflow(
        self, workflow_id: str, message: dict, exclude: Optional[WebSocket] = None
    ):
        """Enviar mensaje a todos los clientes de un workflow"""
        if workflow_id not in self.active_connections:
            return

        disconnected = []
        for connection in self.active_connections[workflow_id]:
            if connection == exclude:
                continue

            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)

        # Limpiar conexiones muertas
        for ws in disconnected:
            self.disconnect(ws)

    async def send_to_user(self, workflow_id: str, user_id: str, message: dict):
        """Enviar mensaje a un usuario específico"""
        for connection_id, session in self.sessions.items():
            if session["workflow_id"] == workflow_id and session["user_id"] == user_id:
                try:
                    await session["websocket"].send_json(message)
                except Exception:
                    pass

    def get_active_users(self, workflow_id: str) -> List[dict]:
        """Obtener usuarios activos en un workflow"""
        users = []
        for connection_id, session in self.sessions.items():
            if session["workflow_id"] == workflow_id:
                users.append(
                    {
                        "user_id": session["user_id"],
                        "user_name": session["user_name"],
                        "color": session["color"],
                        "connected_at": session["connected_at"],
                    }
                )
        return users

    def _generate_color(self, user_id: str) -> str:
        """Generar color único para un usuario"""
        colors = [
            "#3b82f6",
            "#ef4444",
            "#10b981",
            "#f59e0b",
            "#8b5cf6",
            "#ec4899",
            "#06b6d4",
            "#f97316",
        ]
        # Usar hash del user_id para asignar color consistente
        index = hash(user_id) % len(colors)
        return colors[index]


# Instancia global del gestor
manager = ConnectionManager()


class CollaborationService:
    """Servicio para gestionar colaboración"""

    @staticmethod
    async def add_collaborator(
        db: AsyncSession,
        workflow_id: UUID,
        user_id: UUID,
        role: str,
        permissions: List[str],
        invited_by_id: UUID,
    ) -> WorkflowCollaborator:
        """Agregar colaborador a un workflow"""
        collaborator = WorkflowCollaborator(
            workflow_id=workflow_id,
            user_id=user_id,
            role=role,
            permissions=permissions,
            invited_by_id=invited_by_id,
        )
        db.add(collaborator)
        await db.commit()
        await db.refresh(collaborator)
        return collaborator

    @staticmethod
    async def get_collaborators(
        db: AsyncSession, workflow_id: UUID
    ) -> List[WorkflowCollaborator]:
        """Obtener colaboradores de un workflow"""
        result = await db.execute(
            select(WorkflowCollaborator).where(
                and_(
                    WorkflowCollaborator.workflow_id == workflow_id,
                    WorkflowCollaborator.is_active == True,
                )
            )
        )
        return list(result.scalars().all())

    @staticmethod
    async def check_permission(
        db: AsyncSession, workflow_id: UUID, user_id: UUID, permission: str
    ) -> bool:
        """Verificar si un usuario tiene un permiso"""
        result = await db.execute(
            select(WorkflowCollaborator).where(
                and_(
                    WorkflowCollaborator.workflow_id == workflow_id,
                    WorkflowCollaborator.user_id == user_id,
                    WorkflowCollaborator.is_active == True,
                )
            )
        )
        collaborator = result.scalar_one_or_none()

        if not collaborator:
            return False

        return permission in collaborator.permissions

    @staticmethod
    async def create_session(
        db: AsyncSession,
        workflow_id: UUID,
        user_id: UUID,
        connection_id: str,
        user_name: str,
        user_color: str,
        user_agent: str = None,
        ip_address: str = None,
    ) -> CollaborationSession:
        """Crear sesión de colaboración"""
        session = CollaborationSession(
            workflow_id=workflow_id,
            user_id=user_id,
            connection_id=connection_id,
            user_name=user_name,
            user_color=user_color,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def end_session(db: AsyncSession, connection_id: str):
        """Finalizar sesión de colaboración"""
        result = await db.execute(
            select(CollaborationSession).where(
                CollaborationSession.connection_id == connection_id
            )
        )
        session = result.scalar_one_or_none()

        if session:
            session.is_active = False
            session.disconnected_at = datetime.utcnow().isoformat()
            await db.commit()

    @staticmethod
    async def log_change(
        db: AsyncSession,
        workflow_id: UUID,
        user_id: UUID,
        user_name: str,
        change_type: str,
        entity_type: str,
        entity_id: str,
        before_data: dict = None,
        after_data: dict = None,
        session_id: UUID = None,
    ) -> WorkflowChange:
        """Registrar cambio en el historial"""
        change = WorkflowChange(
            workflow_id=workflow_id,
            user_id=user_id,
            user_name=user_name,
            change_type=change_type,
            entity_type=entity_type,
            entity_id=entity_id,
            before_data=before_data,
            after_data=after_data,
            session_id=session_id,
        )
        db.add(change)
        await db.commit()
        await db.refresh(change)
        return change

    @staticmethod
    async def get_change_history(
        db: AsyncSession, workflow_id: UUID, limit: int = 50
    ) -> List[WorkflowChange]:
        """Obtener historial de cambios"""
        result = await db.execute(
            select(WorkflowChange)
            .where(WorkflowChange.workflow_id == workflow_id)
            .order_by(WorkflowChange.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def send_chat_message(
        db: AsyncSession,
        workflow_id: UUID,
        user_id: UUID,
        user_name: str,
        message: str,
        message_type: str = "text",
        reply_to_id: UUID = None,
        mentioned_user_ids: List[UUID] = None,
    ) -> ChatMessage:
        """Enviar mensaje de chat"""
        chat_message = ChatMessage(
            workflow_id=workflow_id,
            user_id=user_id,
            user_name=user_name,
            message=message,
            message_type=message_type,
            reply_to_id=reply_to_id,
            mentioned_user_ids=mentioned_user_ids or [],
        )
        db.add(chat_message)
        await db.commit()
        await db.refresh(chat_message)
        return chat_message

    @staticmethod
    async def get_chat_messages(
        db: AsyncSession, workflow_id: UUID, limit: int = 100
    ) -> List[ChatMessage]:
        """Obtener mensajes de chat"""
        result = await db.execute(
            select(ChatMessage)
            .where(
                and_(
                    ChatMessage.workflow_id == workflow_id,
                    ChatMessage.is_deleted == False,
                )
            )
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def acquire_lock(
        db: AsyncSession,
        workflow_id: UUID,
        user_id: UUID,
        user_name: str,
        entity_type: str,
        entity_id: str,
        duration_seconds: int = 30,
    ) -> Optional[WorkflowLock]:
        """Adquirir bloqueo sobre un elemento"""
        # Verificar si ya está bloqueado
        result = await db.execute(
            select(WorkflowLock).where(
                and_(
                    WorkflowLock.workflow_id == workflow_id,
                    WorkflowLock.entity_type == entity_type,
                    WorkflowLock.entity_id == entity_id,
                    WorkflowLock.is_active == True,
                )
            )
        )
        existing_lock = result.scalar_one_or_none()

        if existing_lock:
            # Verificar si expiró
            expires_at = datetime.fromisoformat(existing_lock.expires_at)
            if expires_at > datetime.utcnow():
                return None  # Aún bloqueado
            else:
                # Expiró, desactivar
                existing_lock.is_active = False

        # Crear nuevo bloqueo
        expires_at = datetime.utcnow() + timedelta(seconds=duration_seconds)
        lock = WorkflowLock(
            workflow_id=workflow_id,
            user_id=user_id,
            user_name=user_name,
            entity_type=entity_type,
            entity_id=entity_id,
            expires_at=expires_at.isoformat(),
        )
        db.add(lock)
        await db.commit()
        await db.refresh(lock)
        return lock

    @staticmethod
    async def release_lock(
        db: AsyncSession,
        workflow_id: UUID,
        user_id: UUID,
        entity_type: str,
        entity_id: str,
    ):
        """Liberar bloqueo"""
        result = await db.execute(
            select(WorkflowLock).where(
                and_(
                    WorkflowLock.workflow_id == workflow_id,
                    WorkflowLock.user_id == user_id,
                    WorkflowLock.entity_type == entity_type,
                    WorkflowLock.entity_id == entity_id,
                    WorkflowLock.is_active == True,
                )
            )
        )
        lock = result.scalar_one_or_none()

        if lock:
            lock.is_active = False
            await db.commit()
