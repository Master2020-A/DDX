"""
Sistema de A/B Testing para workflows
"""

import random
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.models.workflow import Workflow, WorkflowExecution
from app.models.workflow_advanced import (
    ABTest,
    ABTestStatus,
    ABTestExecution,
    WorkflowVersion,
)


class ABTestingService:
    """Servicio para gestión de tests A/B de workflows"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_ab_test(
        self,
        workflow_id: UUID,
        test_name: str,
        variant_a_version_id: UUID,
        variant_b_version_id: UUID,
        description: Optional[str] = None,
        hypothesis: Optional[str] = None,
        traffic_split: float = 0.5,
        sample_size: Optional[int] = None,
        confidence_level: float = 0.95,
        primary_metric: str = "success_rate",
        secondary_metrics: Optional[List[str]] = None,
        created_by_id: Optional[UUID] = None,
    ) -> ABTest:
        """
        Crea un nuevo test A/B

        Args:
            workflow_id: ID del workflow
            test_name: Nombre del test
            variant_a_version_id: Versión A (control)
            variant_b_version_id: Versión B (variante)
            description: Descripción del test
            hypothesis: Hipótesis a probar
            traffic_split: Distribución de tráfico (0.5 = 50/50)
            sample_size: Número de ejecuciones objetivo
            confidence_level: Nivel de confianza estadística
            primary_metric: Métrica principal a optimizar
            secondary_metrics: Métricas secundarias
            created_by_id: Usuario que crea el test
        """
        # Validar que las versiones existen
        result = await self.db.execute(
            select(WorkflowVersion).where(
                WorkflowVersion.id.in_([variant_a_version_id, variant_b_version_id])
            )
        )
        versions = result.scalars().all()

        if len(versions) != 2:
            raise ValueError("No se encontraron ambas versiones")

        # Validar que pertenecen al mismo workflow
        if not all(v.workflow_id == workflow_id for v in versions):
            raise ValueError("Las versiones deben pertenecer al mismo workflow")

        # Crear el test
        ab_test = ABTest(
            workflow_id=workflow_id,
            test_name=test_name,
            description=description,
            hypothesis=hypothesis,
            status=ABTestStatus.DRAFT.value,
            variant_a_version_id=variant_a_version_id,
            variant_b_version_id=variant_b_version_id,
            traffic_split=traffic_split,
            sample_size=sample_size,
            confidence_level=confidence_level,
            primary_metric=primary_metric,
            secondary_metrics=secondary_metrics or [],
            created_by_id=created_by_id,
        )

        self.db.add(ab_test)
        await self.db.commit()
        await self.db.refresh(ab_test)

        return ab_test

    async def start_ab_test(self, test_id: UUID) -> ABTest:
        """Inicia un test A/B"""
        result = await self.db.execute(select(ABTest).where(ABTest.id == test_id))
        ab_test = result.scalar_one_or_none()

        if not ab_test:
            raise ValueError(f"Test A/B {test_id} no encontrado")

        if ab_test.status != ABTestStatus.DRAFT.value:
            raise ValueError("El test debe estar en estado DRAFT para iniciarse")

        ab_test.status = ABTestStatus.RUNNING.value
        ab_test.started_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(ab_test)

        return ab_test

    async def pause_ab_test(self, test_id: UUID) -> ABTest:
        """Pausa un test A/B"""
        result = await self.db.execute(select(ABTest).where(ABTest.id == test_id))
        ab_test = result.scalar_one_or_none()

        if not ab_test:
            raise ValueError(f"Test A/B {test_id} no encontrado")

        if ab_test.status != ABTestStatus.RUNNING.value:
            raise ValueError("Solo se pueden pausar tests en ejecución")

        ab_test.status = ABTestStatus.PAUSED.value

        await self.db.commit()
        await self.db.refresh(ab_test)

        return ab_test

    async def resume_ab_test(self, test_id: UUID) -> ABTest:
        """Reanuda un test A/B pausado"""
        result = await self.db.execute(select(ABTest).where(ABTest.id == test_id))
        ab_test = result.scalar_one_or_none()

        if not ab_test:
            raise ValueError(f"Test A/B {test_id} no encontrado")

        if ab_test.status != ABTestStatus.PAUSED.value:
            raise ValueError("Solo se pueden reanudar tests pausados")

        ab_test.status = ABTestStatus.RUNNING.value

        await self.db.commit()
        await self.db.refresh(ab_test)

        return ab_test

    async def assign_variant(
        self, workflow_id: UUID, execution_id: UUID
    ) -> Tuple[str, UUID]:
        """
        Asigna una variante (A o B) para una ejecución

        Returns:
            Tuple[variant, version_id]
        """
        # Buscar test A/B activo para este workflow
        result = await self.db.execute(
            select(ABTest).where(
                and_(
                    ABTest.workflow_id == workflow_id,
                    ABTest.status == ABTestStatus.RUNNING.value,
                )
            )
        )
        ab_test = result.scalar_one_or_none()

        if not ab_test:
            # No hay test activo, usar versión actual
            return None, None

        # Verificar si ya alcanzamos el sample size
        if ab_test.sample_size:
            total_executions = (
                ab_test.variant_a_executions + ab_test.variant_b_executions
            )
            if total_executions >= ab_test.sample_size:
                # Test completado, finalizar automáticamente
                await self._auto_complete_test(ab_test.id)
                return None, None

        # Asignar variante según traffic_split
        if random.random() < ab_test.traffic_split:
            variant = "A"
            version_id = ab_test.variant_a_version_id
            ab_test.variant_a_executions += 1
        else:
            variant = "B"
            version_id = ab_test.variant_b_version_id
            ab_test.variant_b_executions += 1

        # Registrar la asignación
        ab_test_execution = ABTestExecution(
            ab_test_id=ab_test.id,
            execution_id=execution_id,
            variant=variant,
            version_id=version_id,
        )

        self.db.add(ab_test_execution)
        await self.db.commit()

        return variant, version_id

    async def record_execution_result(
        self,
        execution_id: UUID,
        duration_ms: int,
        success: bool,
        custom_metrics: Optional[Dict[str, Any]] = None,
    ):
        """Registra el resultado de una ejecución en el test A/B"""
        # Buscar la asignación de test
        result = await self.db.execute(
            select(ABTestExecution).where(ABTestExecution.execution_id == execution_id)
        )
        ab_test_execution = result.scalar_one_or_none()

        if not ab_test_execution:
            return  # No es parte de un test A/B

        # Actualizar métricas
        ab_test_execution.duration_ms = duration_ms
        ab_test_execution.success = success
        ab_test_execution.error_occurred = not success
        ab_test_execution.custom_metrics = custom_metrics or {}

        await self.db.commit()

        # Actualizar métricas agregadas del test
        await self._update_test_metrics(ab_test_execution.ab_test_id)

    async def complete_ab_test(self, test_id: UUID, force: bool = False) -> ABTest:
        """
        Completa un test A/B y calcula el ganador

        Args:
            test_id: ID del test
            force: Forzar completar aunque no se alcance el sample size
        """
        result = await self.db.execute(select(ABTest).where(ABTest.id == test_id))
        ab_test = result.scalar_one_or_none()

        if not ab_test:
            raise ValueError(f"Test A/B {test_id} no encontrado")

        if ab_test.status not in [
            ABTestStatus.RUNNING.value,
            ABTestStatus.PAUSED.value,
        ]:
            raise ValueError("El test debe estar en ejecución o pausado")

        # Verificar sample size
        total_executions = ab_test.variant_a_executions + ab_test.variant_b_executions
        if ab_test.sample_size and total_executions < ab_test.sample_size and not force:
            raise ValueError(
                f"No se ha alcanzado el sample size objetivo ({total_executions}/{ab_test.sample_size})"
            )

        # Calcular ganador
        winner, p_value = await self._calculate_winner(test_id)

        ab_test.status = ABTestStatus.COMPLETED.value
        ab_test.completed_at = datetime.utcnow()
        ab_test.winner = winner
        ab_test.statistical_significance = p_value

        if ab_test.started_at:
            duration = ab_test.completed_at - ab_test.started_at
            ab_test.duration_days = duration.days

        await self.db.commit()
        await self.db.refresh(ab_test)

        return ab_test

    async def get_ab_test_results(self, test_id: UUID) -> Dict[str, Any]:
        """Obtiene los resultados detallados de un test A/B"""
        result = await self.db.execute(select(ABTest).where(ABTest.id == test_id))
        ab_test = result.scalar_one_or_none()

        if not ab_test:
            raise ValueError(f"Test A/B {test_id} no encontrado")

        # Obtener métricas de ambas variantes
        variant_a_metrics = ab_test.variant_a_metrics or {}
        variant_b_metrics = ab_test.variant_b_metrics or {}

        # Calcular mejora relativa
        improvements = {}
        for metric in [ab_test.primary_metric] + ab_test.secondary_metrics:
            if metric in variant_a_metrics and metric in variant_b_metrics:
                a_value = variant_a_metrics[metric]
                b_value = variant_b_metrics[metric]

                if a_value > 0:
                    improvement = ((b_value - a_value) / a_value) * 100
                    improvements[metric] = improvement

        return {
            "test_id": str(ab_test.id),
            "test_name": ab_test.test_name,
            "status": ab_test.status,
            "hypothesis": ab_test.hypothesis,
            "started_at": (
                ab_test.started_at.isoformat() if ab_test.started_at else None
            ),
            "completed_at": (
                ab_test.completed_at.isoformat() if ab_test.completed_at else None
            ),
            "duration_days": ab_test.duration_days,
            "variant_a": {
                "version_id": str(ab_test.variant_a_version_id),
                "executions": ab_test.variant_a_executions,
                "metrics": variant_a_metrics,
            },
            "variant_b": {
                "version_id": str(ab_test.variant_b_version_id),
                "executions": ab_test.variant_b_executions,
                "metrics": variant_b_metrics,
            },
            "winner": ab_test.winner,
            "statistical_significance": ab_test.statistical_significance,
            "confidence_level": ab_test.confidence_level,
            "improvements": improvements,
            "sample_size": ab_test.sample_size,
            "progress": {
                "current": ab_test.variant_a_executions + ab_test.variant_b_executions,
                "target": ab_test.sample_size,
                "percentage": (
                    (
                        (ab_test.variant_a_executions + ab_test.variant_b_executions)
                        / ab_test.sample_size
                        * 100
                    )
                    if ab_test.sample_size
                    else 100
                ),
            },
        }

    async def list_workflow_ab_tests(
        self, workflow_id: UUID, active_only: bool = False
    ) -> List[ABTest]:
        """Lista todos los tests A/B de un workflow"""
        query = select(ABTest).where(ABTest.workflow_id == workflow_id)

        if active_only:
            query = query.where(ABTest.status == ABTestStatus.RUNNING.value)

        query = query.order_by(ABTest.created_at.desc())

        result = await self.db.execute(query)
        return result.scalars().all()

    async def _update_test_metrics(self, test_id: UUID):
        """Actualiza las métricas agregadas de un test"""
        # Obtener todas las ejecuciones del test
        result = await self.db.execute(
            select(ABTestExecution).where(ABTestExecution.ab_test_id == test_id)
        )
        executions = result.scalars().all()

        if not executions:
            return

        # Separar por variante
        variant_a_execs = [e for e in executions if e.variant == "A"]
        variant_b_execs = [e for e in executions if e.variant == "B"]

        # Calcular métricas para variante A
        variant_a_metrics = self._calculate_variant_metrics(variant_a_execs)

        # Calcular métricas para variante B
        variant_b_metrics = self._calculate_variant_metrics(variant_b_execs)

        # Actualizar el test
        result = await self.db.execute(select(ABTest).where(ABTest.id == test_id))
        ab_test = result.scalar_one_or_none()

        if ab_test:
            ab_test.variant_a_metrics = variant_a_metrics
            ab_test.variant_b_metrics = variant_b_metrics
            await self.db.commit()

    def _calculate_variant_metrics(
        self, executions: List[ABTestExecution]
    ) -> Dict[str, Any]:
        """Calcula métricas para una variante"""
        if not executions:
            return {}

        total = len(executions)
        successful = sum(1 for e in executions if e.success)
        failed = total - successful

        durations = [e.duration_ms for e in executions if e.duration_ms is not None]
        avg_duration = sum(durations) / len(durations) if durations else 0

        return {
            "total_executions": total,
            "successful_executions": successful,
            "failed_executions": failed,
            "success_rate": successful / total if total > 0 else 0,
            "error_rate": failed / total if total > 0 else 0,
            "avg_duration_ms": avg_duration,
            "min_duration_ms": min(durations) if durations else 0,
            "max_duration_ms": max(durations) if durations else 0,
        }

    async def _calculate_winner(
        self, test_id: UUID
    ) -> Tuple[Optional[str], Optional[float]]:
        """
        Calcula el ganador usando test estadístico

        Returns:
            Tuple[winner, p_value]
        """
        result = await self.db.execute(select(ABTest).where(ABTest.id == test_id))
        ab_test = result.scalar_one_or_none()

        if not ab_test:
            return None, None

        variant_a_metrics = ab_test.variant_a_metrics or {}
        variant_b_metrics = ab_test.variant_b_metrics or {}

        # Obtener métrica principal
        metric = ab_test.primary_metric

        if metric not in variant_a_metrics or metric not in variant_b_metrics:
            return None, None

        a_value = variant_a_metrics[metric]
        b_value = variant_b_metrics[metric]

        # Determinar ganador (mayor es mejor para success_rate, menor para duration)
        if metric in ["success_rate", "user_satisfaction"]:
            winner = "B" if b_value > a_value else "A"
        elif metric in ["duration_ms", "error_rate"]:
            winner = "B" if b_value < a_value else "A"
        else:
            winner = "B" if b_value > a_value else "A"

        # Calcular significancia estadística (simplificado)
        # En producción, usar scipy.stats para test t o chi-cuadrado
        diff = abs(b_value - a_value)
        avg = (a_value + b_value) / 2

        if avg > 0:
            relative_diff = diff / avg
            # Aproximación simple: si la diferencia es > 5%, considerarlo significativo
            p_value = 0.05 if relative_diff > 0.05 else 0.10
        else:
            p_value = 1.0

        return winner, p_value

    async def _auto_complete_test(self, test_id: UUID):
        """Completa automáticamente un test cuando alcanza el sample size"""
        try:
            await self.complete_ab_test(test_id, force=True)
        except Exception as e:
            print(f"Error al auto-completar test {test_id}: {e}")
