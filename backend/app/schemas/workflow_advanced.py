"""
Schemas para funcionalidades avanzadas de workflows
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


# ============= VERSIONING SCHEMAS =============


class WorkflowVersionBase(BaseModel):
    version_number: str = Field(..., description="Número de versión (ej: 1.0.0)")
    version_name: Optional[str] = Field(None, description="Nombre descriptivo")
    changes_description: Optional[str] = Field(
        None, description="Descripción de cambios"
    )
    breaking_changes: bool = Field(False, description="¿Rompe compatibilidad?")


class WorkflowVersionCreate(WorkflowVersionBase):
    auto_publish: bool = Field(False, description="Publicar automáticamente")


class WorkflowVersionResponse(WorkflowVersionBase):
    id: UUID
    workflow_id: UUID
    is_current: bool
    is_published: bool
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    config: Dict[str, Any]
    variables: Dict[str, Any]
    execution_count: int
    success_rate: float
    avg_duration_ms: int
    error_count: int
    created_at: datetime
    published_at: Optional[datetime]
    deprecated_at: Optional[datetime]

    class Config:
        from_attributes = True


class VersionComparisonResponse(BaseModel):
    version_a: Dict[str, Any]
    version_b: Dict[str, Any]
    nodes: Dict[str, List[Dict[str, Any]]]
    edges: Dict[str, List[Dict[str, Any]]]
    summary: Dict[str, int]


class RollbackRequest(BaseModel):
    version_id: UUID = Field(..., description="ID de la versión a restaurar")


# ============= A/B TESTING SCHEMAS =============


class ABTestBase(BaseModel):
    test_name: str = Field(..., description="Nombre del test")
    description: Optional[str] = None
    hypothesis: Optional[str] = Field(None, description="Hipótesis a probar")
    traffic_split: float = Field(
        0.5, ge=0.0, le=1.0, description="Distribución de tráfico"
    )
    sample_size: Optional[int] = Field(
        None, gt=0, description="Tamaño de muestra objetivo"
    )
    confidence_level: float = Field(0.95, ge=0.0, le=1.0)
    primary_metric: str = Field("success_rate", description="Métrica principal")
    secondary_metrics: List[str] = Field(default_factory=list)


class ABTestCreate(ABTestBase):
    variant_a_version_id: UUID = Field(..., description="Versión A (control)")
    variant_b_version_id: UUID = Field(..., description="Versión B (variante)")


class ABTestResponse(ABTestBase):
    id: UUID
    workflow_id: UUID
    status: str
    variant_a_version_id: UUID
    variant_b_version_id: UUID
    variant_a_executions: int
    variant_b_executions: int
    variant_a_metrics: Dict[str, Any]
    variant_b_metrics: Dict[str, Any]
    winner: Optional[str]
    statistical_significance: Optional[float]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_days: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class ABTestResultsResponse(BaseModel):
    test_id: str
    test_name: str
    status: str
    hypothesis: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    duration_days: Optional[int]
    variant_a: Dict[str, Any]
    variant_b: Dict[str, Any]
    winner: Optional[str]
    statistical_significance: Optional[float]
    confidence_level: float
    improvements: Dict[str, float]
    sample_size: Optional[int]
    progress: Dict[str, Any]


class ABTestCompleteRequest(BaseModel):
    force: bool = Field(False, description="Forzar completar sin alcanzar sample size")


# ============= LOOP NODE SCHEMAS =============


class LoopNodeConfig(BaseModel):
    loopType: str = Field(..., description="Tipo: for_each, while, count")
    maxIterations: int = Field(100, description="Límite de iteraciones")

    # For each
    itemsVariable: Optional[str] = Field(None, description="Variable con la lista")

    # While
    conditionVariable: Optional[str] = None
    conditionOperator: Optional[str] = None
    conditionValue: Optional[Any] = None

    # Count
    count: Optional[int] = None

    # Nodos internos del loop
    bodyNodes: List[Dict[str, Any]] = Field(default_factory=list)


class LoopExecutionResult(BaseModel):
    loop_type: str
    iterations: int
    results: List[Dict[str, Any]]
    completed: bool


# ============= SUBWORKFLOW NODE SCHEMAS =============


class SubworkflowNodeConfig(BaseModel):
    subworkflowId: str = Field(..., description="ID del workflow a ejecutar")
    inputMapping: Dict[str, str] = Field(
        default_factory=dict,
        description="Mapeo de variables: {subworkflow_var: context_var}",
    )
    outputMapping: Dict[str, str] = Field(
        default_factory=dict,
        description="Mapeo de salida: {context_var: subworkflow_var}",
    )
    timeout: Optional[int] = Field(None, description="Timeout en segundos")


class SubworkflowExecutionResult(BaseModel):
    subworkflow_id: str
    subworkflow_name: str
    execution_id: str
    status: str
    output: Dict[str, Any]
    duration_ms: int
    completed: bool
    error: Optional[str] = None


# ============= WORKFLOW UPDATE WITH ADVANCED FEATURES =============


class WorkflowUpdateAdvanced(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    nodes: Optional[List[Dict[str, Any]]] = None
    edges: Optional[List[Dict[str, Any]]] = None
    config: Optional[Dict[str, Any]] = None
    variables: Optional[Dict[str, Any]] = None
    create_version: bool = Field(False, description="Crear versión automáticamente")
    version_name: Optional[str] = None
    changes_description: Optional[str] = None


# ============= EXECUTION WITH VERSION =============


class WorkflowExecuteWithVersion(BaseModel):
    input_data: Dict[str, Any] = Field(default_factory=dict)
    version_id: Optional[UUID] = Field(
        None, description="Versión específica a ejecutar"
    )
    use_ab_test: bool = Field(True, description="Participar en test A/B si existe")


# ============= STATISTICS =============


class VersionStatistics(BaseModel):
    version_id: UUID
    version_number: str
    execution_count: int
    success_rate: float
    avg_duration_ms: int
    error_count: int
    is_current: bool


class WorkflowStatistics(BaseModel):
    workflow_id: UUID
    workflow_name: str
    total_versions: int
    current_version: Optional[VersionStatistics]
    all_versions: List[VersionStatistics]
    active_ab_tests: int
    total_executions: int
    overall_success_rate: float
