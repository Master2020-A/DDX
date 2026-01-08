"""
API Endpoints para Workflows y Agentes IA
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
import logging

from app.core.database import get_db
from app.api.dependencies import get_current_user  # ✅ correcto
from app.models.usuario import Usuario
from app.models.workflow import (
    Workflow,
    AIAgent,
    WorkflowExecution,
    WorkflowTemplate,
    AgentModel,
)
from app.services.workflow_engine import WorkflowEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflows", tags=["🤖 Workflows & AI Agents"])


class NodeSchema(BaseModel):
    id: str
    type: str
    position: Dict[str, float]
    data: Dict[str, Any]


class EdgeSchema(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None
    condition: Optional[str] = None


class WorkflowCreate(BaseModel):
    workflow_id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    nodes: List[NodeSchema]
    edges: List[EdgeSchema]
    config: Optional[Dict[str, Any]] = None
    variables: Optional[Dict[str, Any]] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    tags: Optional[List[str]] = None


class WorkflowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workflow_id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    status: str
    version: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    config: Optional[Dict[str, Any]] = None
    variables: Optional[Dict[str, Any]] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime


class ExecuteWorkflowRequest(BaseModel):
    input_data: Dict[str, Any]


class ExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workflow_id: UUID
    status: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


@router.get("", response_model=List[WorkflowResponse])
async def list_workflows(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Workflow).order_by(Workflow.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow_def: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(
        select(Workflow).where(Workflow.workflow_id == workflow_def.workflow_id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400, detail=f"Workflow '{workflow_def.workflow_id}' ya existe"
        )

    wf = Workflow(
        workflow_id=workflow_def.workflow_id,
        name=workflow_def.name,
        description=workflow_def.description,
        category=workflow_def.category,
        nodes=[n.model_dump() for n in workflow_def.nodes],
        edges=[e.model_dump() for e in workflow_def.edges],
        config=workflow_def.config or {},
        variables=workflow_def.variables or {},
        icon=workflow_def.icon,
        color=workflow_def.color,
        tags=workflow_def.tags or [],
        created_by_id=current_user.id,
    )

    db.add(wf)
    await db.commit()
    await db.refresh(wf)
    return wf


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(
        select(Workflow).where(Workflow.workflow_id == workflow_id)
    )
    wf = result.scalar_one_or_none()
    if not wf:
        raise HTTPException(
            status_code=404, detail=f"Workflow '{workflow_id}' no encontrado"
        )
    return wf


@router.post("/{workflow_id}/execute", response_model=ExecutionResponse)
async def execute_workflow(
    workflow_id: str,
    req: ExecuteWorkflowRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    engine = WorkflowEngine(db)
    execution = await engine.execute_workflow(
        workflow_id=workflow_id,
        input_data=req.input_data,
        triggered_by="manual",
        user_id=current_user.id,
    )
    return execution
