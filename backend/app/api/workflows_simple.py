"""
API Endpoints simplificados para Workflows y Agentes IA
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from uuid import UUID
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.usuario import Usuario
from app.services.workflow_engine import WorkflowEngine

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================
# SCHEMAS SIMPLIFICADOS
# ============================================================


class WorkflowListItem(BaseModel):
    id: str
    workflow_id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    status: str
    icon: Optional[str] = None
    color: Optional[str] = None

    class Config:
        from_attributes = True


class WorkflowExecuteRequest(BaseModel):
    input_data: Dict[str, Any]


class WorkflowExecuteResponse(BaseModel):
    execution_id: str
    status: str
    output_data: Optional[Dict[str, Any]] = None
    logs: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


# ============================================================
# ENDPOINTS
# ============================================================


@router.get("/workflows")
async def list_workflows(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Listar workflows"""
    result = await db.execute(
        text(
            "SELECT id, workflow_id, name, description, category, status, icon, color FROM workflows ORDER BY created_at DESC"
        )
    )
    rows = result.fetchall()

    workflows = []
    for row in rows:
        workflows.append(
            {
                "id": str(row.id),
                "workflow_id": row.workflow_id,
                "name": row.name,
                "description": row.description,
                "category": row.category,
                "status": row.status,
                "icon": row.icon,
                "color": row.color,
            }
        )

    return workflows


@router.get("/workflows/{workflow_id}")
async def get_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener un workflow por ID"""
    result = await db.execute(
        text("SELECT * FROM workflows WHERE workflow_id = :wid"), {"wid": workflow_id}
    )
    row = result.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Workflow no encontrado")

    return {
        "id": str(row.id),
        "workflow_id": row.workflow_id,
        "name": row.name,
        "description": row.description,
        "category": row.category,
        "status": row.status,
        "version": row.version,
        "nodes": row.nodes,
        "edges": row.edges,
        "config": row.config,
        "variables": row.variables,
        "icon": row.icon,
        "color": row.color,
        "tags": row.tags,
    }


@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    request: WorkflowExecuteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Ejecutar un workflow"""
    try:
        engine = WorkflowEngine(db)
        execution = await engine.execute_workflow(
            workflow_id=workflow_id,
            input_data=request.input_data,
            triggered_by="manual",
            user_id=current_user.id,
        )

        return {
            "execution_id": str(execution.id),
            "status": execution.status.value,
            "output_data": execution.output_data,
            "logs": execution.logs,
            "error": execution.error,
            "duration_ms": execution.duration_ms,
        }
    except Exception as e:
        logger.error(f"Error ejecutando workflow: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/{workflow_id}/executions")
async def list_executions(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Listar ejecuciones de un workflow"""
    # Primero obtener el UUID del workflow
    result = await db.execute(
        text("SELECT id FROM workflows WHERE workflow_id = :wid"), {"wid": workflow_id}
    )
    workflow = result.fetchone()

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow no encontrado")

    # Obtener ejecuciones
    result = await db.execute(
        text(
            """
            SELECT id, status, started_at, completed_at, duration_ms, error
            FROM workflow_executions 
            WHERE workflow_id = :wid 
            ORDER BY started_at DESC 
            LIMIT 50
        """
        ),
        {"wid": workflow.id},
    )
    rows = result.fetchall()

    executions = []
    for row in rows:
        executions.append(
            {
                "id": str(row.id),
                "status": row.status,
                "started_at": row.started_at,
                "completed_at": row.completed_at,
                "duration_ms": row.duration_ms,
                "error": row.error,
            }
        )

    return executions
