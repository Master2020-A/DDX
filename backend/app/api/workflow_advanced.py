"""
API endpoints para funcionalidades avanzadas de workflows
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.usuario import Usuario
from app.schemas.workflow_advanced import (
    WorkflowVersionCreate,
    WorkflowVersionResponse,
    VersionComparisonResponse,
    RollbackRequest,
    ABTestCreate,
    ABTestResponse,
    ABTestResultsResponse,
    ABTestCompleteRequest,
    WorkflowUpdateAdvanced,
    WorkflowExecuteWithVersion,
    WorkflowStatistics,
)
from app.services.workflow_versioning import WorkflowVersioningService
from app.services.workflow_ab_testing import ABTestingService

router = APIRouter(prefix="/api/workflows", tags=["workflows-advanced"])


# ============= VERSIONING ENDPOINTS =============


@router.post("/{workflow_id}/versions", response_model=WorkflowVersionResponse)
async def create_workflow_version(
    workflow_id: UUID,
    version_data: WorkflowVersionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea una nueva versión del workflow"""
    try:
        versioning_service = WorkflowVersioningService(db)
        version = await versioning_service.create_version(
            workflow_id=workflow_id,
            version_number=version_data.version_number,
            version_name=version_data.version_name,
            changes_description=version_data.changes_description,
            breaking_changes=version_data.breaking_changes,
            created_by_id=current_user.id,
            auto_publish=version_data.auto_publish,
        )
        return version
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear versión: {str(e)}")


@router.get("/{workflow_id}/versions", response_model=List[WorkflowVersionResponse])
async def list_workflow_versions(
    workflow_id: UUID,
    published_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista todas las versiones de un workflow"""
    try:
        versioning_service = WorkflowVersioningService(db)
        versions = await versioning_service.get_workflow_versions(
            workflow_id=workflow_id, published_only=published_only
        )
        return versions
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al listar versiones: {str(e)}"
        )


@router.get("/{workflow_id}/versions/current", response_model=WorkflowVersionResponse)
async def get_current_version(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene la versión actual del workflow"""
    try:
        versioning_service = WorkflowVersioningService(db)
        version = await versioning_service.get_current_version(workflow_id)
        if not version:
            raise HTTPException(status_code=404, detail="No hay versión actual")
        return version
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener versión actual: {str(e)}"
        )


@router.get("/versions/{version_id}", response_model=WorkflowVersionResponse)
async def get_version(
    version_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene una versión específica"""
    try:
        versioning_service = WorkflowVersioningService(db)
        version = await versioning_service.get_version(version_id)
        if not version:
            raise HTTPException(status_code=404, detail="Versión no encontrada")
        return version
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener versión: {str(e)}"
        )


@router.post("/versions/{version_id}/publish", response_model=WorkflowVersionResponse)
async def publish_version(
    version_id: UUID,
    set_as_current: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Publica una versión"""
    try:
        versioning_service = WorkflowVersioningService(db)
        version = await versioning_service.publish_version(version_id, set_as_current)
        return version
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al publicar versión: {str(e)}"
        )


@router.post("/versions/{version_id}/deprecate", response_model=WorkflowVersionResponse)
async def deprecate_version(
    version_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Marca una versión como deprecada"""
    try:
        versioning_service = WorkflowVersioningService(db)
        version = await versioning_service.deprecate_version(version_id)
        return version
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al deprecar versión: {str(e)}"
        )


@router.post("/{workflow_id}/rollback", response_model=dict)
async def rollback_workflow(
    workflow_id: UUID,
    rollback_data: RollbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Revierte el workflow a una versión anterior"""
    try:
        versioning_service = WorkflowVersioningService(db)
        workflow = await versioning_service.rollback_to_version(
            workflow_id=workflow_id, version_id=rollback_data.version_id
        )
        return {
            "message": "Rollback exitoso",
            "workflow_id": str(workflow.id),
            "version_id": str(rollback_data.version_id),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en rollback: {str(e)}")


@router.get(
    "/versions/{version_a_id}/compare/{version_b_id}",
    response_model=VersionComparisonResponse,
)
async def compare_versions(
    version_a_id: UUID,
    version_b_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Compara dos versiones"""
    try:
        versioning_service = WorkflowVersioningService(db)
        comparison = await versioning_service.compare_versions(
            version_a_id, version_b_id
        )
        return comparison
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al comparar versiones: {str(e)}"
        )


@router.post("/{workflow_id}/auto-version", response_model=WorkflowVersionResponse)
async def auto_version_workflow(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea automáticamente una nueva versión incrementando el número"""
    try:
        versioning_service = WorkflowVersioningService(db)
        version = await versioning_service.auto_version(
            workflow_id=workflow_id, created_by_id=current_user.id
        )
        return version
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al crear versión automática: {str(e)}"
        )


# ============= A/B TESTING ENDPOINTS =============


@router.post("/{workflow_id}/ab-tests", response_model=ABTestResponse)
async def create_ab_test(
    workflow_id: UUID,
    test_data: ABTestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea un nuevo test A/B"""
    try:
        ab_testing_service = ABTestingService(db)
        ab_test = await ab_testing_service.create_ab_test(
            workflow_id=workflow_id,
            test_name=test_data.test_name,
            variant_a_version_id=test_data.variant_a_version_id,
            variant_b_version_id=test_data.variant_b_version_id,
            description=test_data.description,
            hypothesis=test_data.hypothesis,
            traffic_split=test_data.traffic_split,
            sample_size=test_data.sample_size,
            confidence_level=test_data.confidence_level,
            primary_metric=test_data.primary_metric,
            secondary_metrics=test_data.secondary_metrics,
            created_by_id=current_user.id,
        )
        return ab_test
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al crear test A/B: {str(e)}"
        )


@router.get("/{workflow_id}/ab-tests", response_model=List[ABTestResponse])
async def list_ab_tests(
    workflow_id: UUID,
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista todos los tests A/B de un workflow"""
    try:
        ab_testing_service = ABTestingService(db)
        tests = await ab_testing_service.list_workflow_ab_tests(
            workflow_id=workflow_id, active_only=active_only
        )
        return tests
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al listar tests A/B: {str(e)}"
        )


@router.get("/ab-tests/{test_id}", response_model=ABTestResponse)
async def get_ab_test(
    test_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene un test A/B específico"""
    try:
        from sqlalchemy import select
        from app.models.workflow_advanced import ABTest

        result = await db.execute(select(ABTest).where(ABTest.id == test_id))
        ab_test = result.scalar_one_or_none()

        if not ab_test:
            raise HTTPException(status_code=404, detail="Test A/B no encontrado")

        return ab_test
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener test A/B: {str(e)}"
        )


@router.get("/ab-tests/{test_id}/results", response_model=ABTestResultsResponse)
async def get_ab_test_results(
    test_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene los resultados detallados de un test A/B"""
    try:
        ab_testing_service = ABTestingService(db)
        results = await ab_testing_service.get_ab_test_results(test_id)
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener resultados: {str(e)}"
        )


@router.post("/ab-tests/{test_id}/start", response_model=ABTestResponse)
async def start_ab_test(
    test_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Inicia un test A/B"""
    try:
        ab_testing_service = ABTestingService(db)
        ab_test = await ab_testing_service.start_ab_test(test_id)
        return ab_test
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al iniciar test: {str(e)}")


@router.post("/ab-tests/{test_id}/pause", response_model=ABTestResponse)
async def pause_ab_test(
    test_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Pausa un test A/B"""
    try:
        ab_testing_service = ABTestingService(db)
        ab_test = await ab_testing_service.pause_ab_test(test_id)
        return ab_test
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al pausar test: {str(e)}")


@router.post("/ab-tests/{test_id}/resume", response_model=ABTestResponse)
async def resume_ab_test(
    test_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Reanuda un test A/B pausado"""
    try:
        ab_testing_service = ABTestingService(db)
        ab_test = await ab_testing_service.resume_ab_test(test_id)
        return ab_test
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al reanudar test: {str(e)}")


@router.post("/ab-tests/{test_id}/complete", response_model=ABTestResponse)
async def complete_ab_test(
    test_id: UUID,
    complete_data: ABTestCompleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Completa un test A/B y calcula el ganador"""
    try:
        ab_testing_service = ABTestingService(db)
        ab_test = await ab_testing_service.complete_ab_test(
            test_id, complete_data.force
        )
        return ab_test
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al completar test: {str(e)}"
        )


# ============= STATISTICS ENDPOINTS =============


@router.get("/{workflow_id}/statistics", response_model=WorkflowStatistics)
async def get_workflow_statistics(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene estadísticas completas del workflow"""
    try:
        from sqlalchemy import select, func
        from app.models.workflow import Workflow, WorkflowExecution
        from app.models.workflow_advanced import WorkflowVersion, ABTest

        # Obtener workflow
        result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
        workflow = result.scalar_one_or_none()

        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow no encontrado")

        # Obtener versiones
        versioning_service = WorkflowVersioningService(db)
        versions = await versioning_service.get_workflow_versions(workflow_id)
        current_version = await versioning_service.get_current_version(workflow_id)

        # Contar tests A/B activos
        result = await db.execute(
            select(func.count(ABTest.id)).where(
                ABTest.workflow_id == workflow_id, ABTest.status == "running"
            )
        )
        active_ab_tests = result.scalar() or 0

        # Contar ejecuciones totales
        result = await db.execute(
            select(func.count(WorkflowExecution.id)).where(
                WorkflowExecution.workflow_id == workflow_id
            )
        )
        total_executions = result.scalar() or 0

        # Calcular success rate general
        result = await db.execute(
            select(func.count(WorkflowExecution.id)).where(
                WorkflowExecution.workflow_id == workflow_id,
                WorkflowExecution.status == "completed",
            )
        )
        successful_executions = result.scalar() or 0
        overall_success_rate = (
            successful_executions / total_executions if total_executions > 0 else 0
        )

        # Preparar estadísticas de versiones
        from app.schemas.workflow_advanced import VersionStatistics

        version_stats = [
            VersionStatistics(
                version_id=v.id,
                version_number=v.version_number,
                execution_count=v.execution_count,
                success_rate=v.success_rate,
                avg_duration_ms=v.avg_duration_ms,
                error_count=v.error_count,
                is_current=v.is_current,
            )
            for v in versions
        ]

        current_version_stats = None
        if current_version:
            current_version_stats = VersionStatistics(
                version_id=current_version.id,
                version_number=current_version.version_number,
                execution_count=current_version.execution_count,
                success_rate=current_version.success_rate,
                avg_duration_ms=current_version.avg_duration_ms,
                error_count=current_version.error_count,
                is_current=True,
            )

        return WorkflowStatistics(
            workflow_id=workflow_id,
            workflow_name=workflow.name,
            total_versions=len(versions),
            current_version=current_version_stats,
            all_versions=version_stats,
            active_ab_tests=active_ab_tests,
            total_executions=total_executions,
            overall_success_rate=overall_success_rate,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener estadísticas: {str(e)}"
        )
