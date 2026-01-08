"""
Schemas de Pydantic para Colaboración en Tiempo Real
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


# ============================================================
# COLLABORATOR SCHEMAS
# ============================================================


class CollaboratorCreate(BaseModel):
    user_id: UUID
    role: str = "viewer"  # owner, editor, viewer
    permissions: List[str] = ["read"]


class CollaboratorUpdate(BaseModel):
    role: Optional[str] = None
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None


class CollaboratorInDB(BaseModel):
    id: UUID
    workflow_id: UUID
    user_id: UUID
    role: str
    permissions: List[str]
    is_active: bool
    last_seen_at: Optional[str]
    color: Optional[str]
    nickname: Optional[str]
    invited_by_id: Optional[UUID]
    invited_at: str
    accepted_at: Optional[str]

    class Config:
        from_attributes = True


# ============================================================
# SESSION SCHEMAS
# ============================================================


class CollaborationSessionCreate(BaseModel):
    workflow_id: UUID
    user_id: UUID
    connection_id: str
    user_name: str
    user_color: str


class CollaborationSessionInDB(BaseModel):
    id: UUID
    workflow_id: UUID
    user_id: UUID
    connection_id: str
    user_name: str
    user_color: str
    is_active: bool
    cursor_x: int
    cursor_y: int
    last_activity_at: str
    connected_at: str
    disconnected_at: Optional[str]

    class Config:
        from_attributes = True


class ActiveUser(BaseModel):
    user_id: str
    user_name: str
    color: str
    connected_at: str
    cursor_x: Optional[int] = 0
    cursor_y: Optional[int] = 0


# ============================================================
# CHANGE HISTORY SCHEMAS
# ============================================================


class WorkflowChangeCreate(BaseModel):
    workflow_id: UUID
    user_id: UUID
    change_type: str
    entity_type: str
    entity_id: str
    before_data: Optional[Dict[str, Any]] = None
    after_data: Optional[Dict[str, Any]] = None


class WorkflowChangeInDB(BaseModel):
    id: UUID
    workflow_id: UUID
    user_id: UUID
    change_type: str
    entity_type: str
    entity_id: str
    before_data: Optional[Dict[str, Any]]
    after_data: Optional[Dict[str, Any]]
    diff: Optional[Dict[str, Any]]
    session_id: Optional[UUID]
    user_name: str
    created_at: str

    class Config:
        from_attributes = True


class ChangeHistoryItem(BaseModel):
    id: UUID
    change_type: str
    entity_type: str
    entity_id: str
    user_name: str
    timestamp: str
    changes: Optional[Dict[str, Any]]


# ============================================================
# CHAT MESSAGE SCHEMAS
# ============================================================


class ChatMessageCreate(BaseModel):
    workflow_id: UUID
    message: str
    message_type: str = "text"
    reply_to_id: Optional[UUID] = None
    mentioned_user_ids: List[UUID] = []


class ChatMessageUpdate(BaseModel):
    message: Optional[str] = None
    is_deleted: Optional[bool] = None


class ChatMessageInDB(BaseModel):
    id: UUID
    workflow_id: UUID
    user_id: UUID
    message: str
    message_type: str
    reply_to_id: Optional[UUID]
    mentioned_user_ids: List[UUID]
    is_edited: bool
    is_deleted: bool
    user_name: str
    created_at: str
    edited_at: Optional[str]

    class Config:
        from_attributes = True


# ============================================================
# LOCK SCHEMAS
# ============================================================


class WorkflowLockCreate(BaseModel):
    workflow_id: UUID
    user_id: UUID
    entity_type: str
    entity_id: str


class WorkflowLockInDB(BaseModel):
    id: UUID
    workflow_id: UUID
    user_id: UUID
    entity_type: str
    entity_id: str
    is_active: bool
    user_name: str
    locked_at: str
    expires_at: Optional[str]

    class Config:
        from_attributes = True


# ============================================================
# WEBSOCKET MESSAGE SCHEMAS
# ============================================================


class WSMessage(BaseModel):
    """Mensaje genérico de WebSocket"""

    type: str
    data: Dict[str, Any]


class CursorMoveEvent(BaseModel):
    x: int
    y: int


class NodeUpdateEvent(BaseModel):
    nodeId: str
    changes: Dict[str, Any]


class NodeAddEvent(BaseModel):
    node: Dict[str, Any]


class NodeDeleteEvent(BaseModel):
    nodeId: str


class EdgeAddEvent(BaseModel):
    edge: Dict[str, Any]


class EdgeDeleteEvent(BaseModel):
    edgeId: str


class ChatMessageEvent(BaseModel):
    message: str


class LockAcquireEvent(BaseModel):
    entityType: str
    entityId: str


class LockReleaseEvent(BaseModel):
    entityType: str
    entityId: str


# ============================================================
# RESPONSE SCHEMAS
# ============================================================


class CollaborationStats(BaseModel):
    total_collaborators: int
    active_users: int
    total_changes: int
    total_messages: int
    recent_activity: List[ChangeHistoryItem]


class WorkflowCollaborationInfo(BaseModel):
    workflow_id: UUID
    collaborators: List[CollaboratorInDB]
    active_users: List[ActiveUser]
    recent_changes: List[WorkflowChangeInDB]
    recent_messages: List[ChatMessageInDB]
