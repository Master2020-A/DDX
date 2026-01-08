"""
API Endpoints ultra-simplificados para Workflows
Sin parámetros Query para evitar conflictos con Pydantic
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from typing import Dict, Any, List
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.usuario import Usuario
from app.services.workflow_engine import WorkflowEngine

logger = logging.getLogger(__name__)
router = APIRouter()


class ExecuteRequest(BaseModel):
    input_data: Dict[str, Any]


@router.get("/workflows")
async def list_workflows(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Listar todos los workflows"""
    result = await db.execute(
        text(
            """
            SELECT id, workflow_id, name, description, category, 
                   status, icon, color, version
            FROM workflows 
            ORDER BY created_at DESC
        """
        )
    )
    rows = result.fetchall()

    return [
        {
            "id": str(row.id),
            "workflow_id": row.workflow_id,
            "name": row.name,
            "description": row.description,
            "category": row.category,
            "status": row.status,
            "icon": row.icon,
            "color": row.color,
            "version": row.version,
        }
        for row in rows
    ]


@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    request: ExecuteRequest,
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
