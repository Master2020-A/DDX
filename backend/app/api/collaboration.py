"""
API Endpoints para Colaboración en Tiempo Real
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    Query,
)
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID, uuid4
import json

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.usuario import Usuario
from app.services.collaboration_service import CollaborationService, manager
from app.schemas.collaboration import (
    CollaboratorCreate,
    CollaboratorInDB,
    ChatMessageCreate,
    ChatMessageInDB,
    ChangeHistoryItem,
    ActiveUser,
)

router = APIRouter()


# ============================================================
# WEBSOCKET ENDPOINT
# ============================================================


@router.websocket("/ws/workflows/{workflow_id}/collaborate")
async def websocket_collaborate(
    websocket: WebSocket,
    workflow_id: str,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """
    WebSocket endpoint para colaboración en tiempo real

    Eventos del cliente:
    - cursor_move: {x, y}
    - node_update: {nodeId, changes}
    - node_add: {node}
    - node_delete: {nodeId}
    - edge_add: {edge}
    - edge_delete: {edgeId}
    - chat_message: {message}
    - lock_acquire: {entityType, entityId}
    - lock_release: {entityType, entityId}

    Eventos del servidor:
    - user_joined: {userId, userName, color}
    - user_left: {userId, userName}
    - cursor_position: {userId, x, y}
    - node_updated: {nodeId, changes, userId, userName}
    - chat_message: {messageId, userId, userName, message, timestamp}
    - lock_acquired: {entityType, entityId, userId, userName}
    - lock_released: {entityType, entityId}
    """

    # TODO: Validar token y obtener usuario
    # Por ahora, usar datos de ejemplo
    user_id = str(uuid4())
    user_name = "Usuario Demo"
    connection_id = str(uuid4())

    try:
        # Conectar
        await manager.connect(websocket, workflow_id, user_id, user_name, connection_id)

        # Crear sesión en BD
        session = await CollaborationService.create_session(
            db,
            UUID(workflow_id),
            UUID(user_id),
            connection_id,
            user_name,
            manager.sessions[connection_id]["color"],
        )

        # Notificar a otros usuarios
        await manager.broadcast_to_workflow(
            workflow_id,
            {
                "type": "user_joined",
                "data": {
                    "userId": user_id,
                    "userName": user_name,
                    "color": manager.sessions[connection_id]["color"],
                },
            },
            exclude=websocket,
        )

        # Enviar lista de usuarios activos al nuevo usuario
        active_users = manager.get_active_users(workflow_id)
        await websocket.send_json(
            {"type": "active_users", "data": {"users": active_users}}
        )

        # Loop principal
        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")
            event_data = data.get("data", {})

            # Procesar evento
            if event_type == "cursor_move":
                # Broadcast posición del cursor
                await manager.broadcast_to_workflow(
                    workflow_id,
                    {
                        "type": "cursor_position",
                        "data": {
                            "userId": user_id,
                            "x": event_data.get("x"),
                            "y": event_data.get("y"),
                        },
                    },
                    exclude=websocket,
                )

            elif event_type == "node_update":
                # Registrar cambio
                await CollaborationService.log_change(
                    db,
                    UUID(workflow_id),
                    UUID(user_id),
                    user_name,
                    "node_updated",
                    "node",
                    event_data.get("nodeId"),
                    after_data=event_data.get("changes"),
                    session_id=session.id,
                )

                # Broadcast cambio
                await manager.broadcast_to_workflow(
                    workflow_id,
                    {
                        "type": "node_updated",
                        "data": {
                            "nodeId": event_data.get("nodeId"),
                            "changes": event_data.get("changes"),
                            "userId": user_id,
                            "userName": user_name,
                        },
                    },
                    exclude=websocket,
                )

            elif event_type == "node_add":
                # Registrar cambio
                await CollaborationService.log_change(
                    db,
                    UUID(workflow_id),
                    UUID(user_id),
                    user_name,
                    "node_added",
                    "node",
                    event_data.get("node", {}).get("id"),
                    after_data=event_data.get("node"),
                    session_id=session.id,
                )

                # Broadcast
                await manager.broadcast_to_workflow(
                    workflow_id,
                    {
                        "type": "node_added",
                        "data": {
                            "node": event_data.get("node"),
                            "userId": user_id,
                            "userName": user_name,
                        },
                    },
                    exclude=websocket,
                )

            elif event_type == "node_delete":
                # Registrar cambio
                await CollaborationService.log_change(
                    db,
                    UUID(workflow_id),
                    UUID(user_id),
                    user_name,
                    "node_deleted",
                    "node",
                    event_data.get("nodeId"),
                    session_id=session.id,
                )

                # Broadcast
                await manager.broadcast_to_workflow(
                    workflow_id,
                    {
                        "type": "node_deleted",
                        "data": {
                            "nodeId": event_data.get("nodeId"),
                            "userId": user_id,
                            "userName": user_name,
                        },
                    },
                    exclude=websocket,
                )

            elif event_type == "edge_add":
                # Registrar cambio
                await CollaborationService.log_change(
                    db,
                    UUID(workflow_id),
                    UUID(user_id),
                    user_name,
                    "edge_added",
                    "edge",
                    event_data.get("edge", {}).get("id"),
                    after_data=event_data.get("edge"),
                    session_id=session.id,
                )

                # Broadcast
                await manager.broadcast_to_workflow(
                    workflow_id,
                    {
                        "type": "edge_added",
                        "data": {
                            "edge": event_data.get("edge"),
                            "userId": user_id,
                            "userName": user_name,
                        },
                    },
                    exclude=websocket,
                )

            elif event_type == "edge_delete":
                # Registrar cambio
                await CollaborationService.log_change(
                    db,
                    UUID(workflow_id),
                    UUID(user_id),
                    user_name,
                    "edge_deleted",
                    "edge",
                    event_data.get("edgeId"),
                    session_id=session.id,
                )

                # Broadcast
                await manager.broadcast_to_workflow(
                    workflow_id,
                    {
                        "type": "edge_deleted",
                        "data": {
                            "edgeId": event_data.get("edgeId"),
                            "userId": user_id,
                            "userName": user_name,
                        },
                    },
                    exclude=websocket,
                )

            elif event_type == "chat_message":
                # Guardar mensaje
                message = await CollaborationService.send_chat_message(
                    db,
                    UUID(workflow_id),
                    UUID(user_id),
                    user_name,
                    event_data.get("message"),
                )

                # Broadcast
                await manager.broadcast_to_workflow(
                    workflow_id,
                    {
                        "type": "chat_message",
                        "data": {
                            "messageId": str(message.id),
                            "userId": user_id,
                            "userName": user_name,
                            "message": event_data.get("message"),
                            "timestamp": message.created_at,
                        },
                    },
                )

            elif event_type == "lock_acquire":
                # Intentar adquirir bloqueo
                lock = await CollaborationService.acquire_lock(
                    db,
                    UUID(workflow_id),
                    UUID(user_id),
                    user_name,
                    event_data.get("entityType"),
                    event_data.get("entityId"),
                )

                if lock:
                    # Broadcast bloqueo adquirido
                    await manager.broadcast_to_workflow(
                        workflow_id,
                        {
                            "type": "lock_acquired",
                            "data": {
                                "entityType": event_data.get("entityType"),
                                "entityId": event_data.get("entityId"),
                                "userId": user_id,
                                "userName": user_name,
                            },
                        },
                    )
                else:
                    # Notificar al usuario que no pudo adquirir el bloqueo
                    await websocket.send_json(
                        {
                            "type": "lock_failed",
                            "data": {
                                "entityType": event_data.get("entityType"),
                                "entityId": event_data.get("entityId"),
                            },
                        }
                    )

            elif event_type == "lock_release":
                # Liberar bloqueo
                await CollaborationService.release_lock(
                    db,
                    UUID(workflow_id),
                    UUID(user_id),
                    event_data.get("entityType"),
                    event_data.get("entityId"),
                )

                # Broadcast bloqueo liberado
                await manager.broadcast_to_workflow(
                    workflow_id,
                    {
                        "type": "lock_released",
                        "data": {
                            "entityType": event_data.get("entityType"),
                            "entityId": event_data.get("entityId"),
                        },
                    },
                )

    except WebSocketDisconnect:
        # Desconectar
        session_info = manager.disconnect(websocket)

        if session_info:
            # Finalizar sesión en BD
            await CollaborationService.end_session(db, connection_id)

            # Notificar a otros usuarios
            await manager.broadcast_to_workflow(
                workflow_id,
                {
                    "type": "user_left",
                    "data": {"userId": user_id, "userName": user_name},
                },
            )


# ============================================================
# REST ENDPOINTS
# ============================================================


@router.post("/workflows/{workflow_id}/collaborators")
async def add_collaborator(
    workflow_id: UUID,
    user_id: UUID = Query(...),
    role: str = Query("viewer"),
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Agregar colaborador a un workflow"""
    # Verificar permisos
    has_permission = await CollaborationService.check_permission(
        db, workflow_id, current_user.id, "share"
    )

    if not has_permission:
        raise HTTPException(status_code=403, detail="No tienes permisos para compartir")

    # Definir permisos según rol
    permissions_map = {
        "owner": ["read", "write", "delete", "share"],
        "editor": ["read", "write"],
        "viewer": ["read"],
    }
    permissions = permissions_map.get(role, ["read"])

    collaborator = await CollaborationService.add_collaborator(
        db, workflow_id, user_id, role, permissions, current_user.id
    )

    return collaborator


@router.get("/workflows/{workflow_id}/collaborators")
async def get_collaborators(
    workflow_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtener colaboradores de un workflow"""
    collaborators = await CollaborationService.get_collaborators(db, workflow_id)
    return collaborators


@router.get("/workflows/{workflow_id}/history")
async def get_change_history(
    workflow_id: UUID,
    limit: int = 50,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtener historial de cambios"""
    changes = await CollaborationService.get_change_history(db, workflow_id, limit)
    return changes


@router.get("/workflows/{workflow_id}/chat")
async def get_chat_messages(
    workflow_id: UUID,
    limit: int = 100,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtener mensajes de chat"""
    messages = await CollaborationService.get_chat_messages(db, workflow_id, limit)
    return messages


@router.get("/workflows/{workflow_id}/active-users")
async def get_active_users(
    workflow_id: UUID, current_user: Usuario = Depends(get_current_user)
):
    """Obtener usuarios activos en un workflow"""
    users = manager.get_active_users(str(workflow_id))
    return {"users": users}
