"""
Ejecutor avanzado de workflows: Loops y Subworkflows
"""

import asyncio
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.workflow import Workflow, WorkflowExecution, ExecutionStatus


class LoopExecutor:
    """Ejecutor de nodos tipo Loop"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute_loop(self, node: dict, context: dict, execute_node_func) -> dict:
        """
        Ejecuta un nodo de tipo loop

        Tipos de loop:
        1. for_each: Itera sobre una lista
        2. while: Ejecuta mientras una condición sea verdadera
        3. count: Ejecuta N veces
        """
        loop_config = node.get("data", {})
        loop_type = loop_config.get("loopType", "for_each")
        max_iterations = loop_config.get("maxIterations", 100)  # Límite de seguridad

        results = []
        iteration_count = 0

        if loop_type == "for_each":
            # Iterar sobre una lista del contexto
            items_key = loop_config.get("itemsVariable")
            items = context.get(items_key, [])

            if not isinstance(items, list):
                raise ValueError(f"Variable '{items_key}' no es una lista")

            for index, item in enumerate(items):
                if iteration_count >= max_iterations:
                    break

                # Crear contexto de iteración
                iteration_context = context.copy()
                iteration_context["loop_item"] = item
                iteration_context["loop_index"] = index
                iteration_context["loop_count"] = len(items)

                # Ejecutar nodos internos del loop
                iteration_result = await self._execute_loop_body(
                    node, iteration_context, execute_node_func
                )

                results.append(
                    {"index": index, "item": item, "result": iteration_result}
                )

                iteration_count += 1

        elif loop_type == "while":
            # Ejecutar mientras la condición sea verdadera
            condition_var = loop_config.get("conditionVariable")
            condition_operator = loop_config.get("conditionOperator", "==")
            condition_value = loop_config.get("conditionValue")

            while iteration_count < max_iterations:
                # Evaluar condición
                current_value = context.get(condition_var)

                if not self._evaluate_condition(
                    current_value, condition_operator, condition_value
                ):
                    break

                # Crear contexto de iteración
                iteration_context = context.copy()
                iteration_context["loop_iteration"] = iteration_count

                # Ejecutar nodos internos
                iteration_result = await self._execute_loop_body(
                    node, iteration_context, execute_node_func
                )

                results.append(
                    {"iteration": iteration_count, "result": iteration_result}
                )

                # Actualizar contexto con resultados
                context.update(iteration_result)
                iteration_count += 1

        elif loop_type == "count":
            # Ejecutar N veces
            count = min(loop_config.get("count", 1), max_iterations)

            for i in range(count):
                iteration_context = context.copy()
                iteration_context["loop_iteration"] = i
                iteration_context["loop_count"] = count

                iteration_result = await self._execute_loop_body(
                    node, iteration_context, execute_node_func
                )

                results.append({"iteration": i, "result": iteration_result})

                iteration_count += 1

        return {
            "loop_type": loop_type,
            "iterations": iteration_count,
            "results": results,
            "completed": True,
        }

    async def _execute_loop_body(
        self, loop_node: dict, context: dict, execute_node_func
    ) -> dict:
        """Ejecuta los nodos internos del loop"""
        # Los nodos internos están en loop_node["data"]["bodyNodes"]
        body_nodes = loop_node.get("data", {}).get("bodyNodes", [])

        if not body_nodes:
            return {}

        # Ejecutar cada nodo del body secuencialmente
        body_results = {}
        for body_node in body_nodes:
            node_result = await execute_node_func(body_node, context)
            body_results[body_node["id"]] = node_result
            context.update(node_result)

        return body_results

    def _evaluate_condition(self, value: Any, operator: str, target: Any) -> bool:
        """Evalúa una condición"""
        if operator == "==":
            return value == target
        elif operator == "!=":
            return value != target
        elif operator == ">":
            return value > target
        elif operator == "<":
            return value < target
        elif operator == ">=":
            return value >= target
        elif operator == "<=":
            return value <= target
        elif operator == "contains":
            return target in str(value)
        elif operator == "not_contains":
            return target not in str(value)
        else:
            return False


class SubworkflowExecutor:
    """Ejecutor de nodos tipo Subworkflow"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute_subworkflow(
        self, node: dict, context: dict, workflow_engine
    ) -> dict:
        """
        Ejecuta un subworkflow

        El subworkflow es otro workflow completo que se ejecuta como un nodo
        """
        subworkflow_config = node.get("data", {})
        subworkflow_id = subworkflow_config.get("subworkflowId")

        if not subworkflow_id:
            raise ValueError("No se especificó el ID del subworkflow")

        # Obtener el workflow a ejecutar
        result = await self.db.execute(
            select(Workflow).where(Workflow.id == UUID(subworkflow_id))
        )
        subworkflow = result.scalar_one_or_none()

        if not subworkflow:
            raise ValueError(f"Subworkflow {subworkflow_id} no encontrado")

        if subworkflow.status != "active":
            raise ValueError(f"Subworkflow {subworkflow_id} no está activo")

        # Preparar input data para el subworkflow
        input_mapping = subworkflow_config.get("inputMapping", {})
        subworkflow_input = {}

        for sub_var, context_var in input_mapping.items():
            if context_var in context:
                subworkflow_input[sub_var] = context[context_var]

        # Si no hay mapping, pasar todo el contexto
        if not input_mapping:
            subworkflow_input = context.copy()

        # Ejecutar el subworkflow
        try:
            execution_result = await workflow_engine.execute(
                workflow_id=str(subworkflow.id),
                input_data=subworkflow_input,
                parent_execution_id=context.get("execution_id"),
            )

            # Mapear output del subworkflow al contexto
            output_mapping = subworkflow_config.get("outputMapping", {})
            mapped_output = {}

            if output_mapping:
                for context_var, sub_var in output_mapping.items():
                    if sub_var in execution_result.get("output_data", {}):
                        mapped_output[context_var] = execution_result["output_data"][
                            sub_var
                        ]
            else:
                # Si no hay mapping, retornar todo el output
                mapped_output = execution_result.get("output_data", {})

            return {
                "subworkflow_id": subworkflow_id,
                "subworkflow_name": subworkflow.name,
                "execution_id": str(execution_result.get("execution_id")),
                "status": execution_result.get("status"),
                "output": mapped_output,
                "duration_ms": execution_result.get("duration_ms"),
                "completed": True,
            }

        except Exception as e:
            return {
                "subworkflow_id": subworkflow_id,
                "error": str(e),
                "completed": False,
            }


class AdvancedWorkflowExecutor:
    """Ejecutor principal que maneja loops y subworkflows"""

    def __init__(self, db: AsyncSession, workflow_engine):
        self.db = db
        self.workflow_engine = workflow_engine
        self.loop_executor = LoopExecutor(db)
        self.subworkflow_executor = SubworkflowExecutor(db)

    async def execute_node(self, node: dict, context: dict) -> dict:
        """
        Ejecuta un nodo, manejando tipos avanzados
        """
        node_type = node.get("type")

        if node_type == "loop":
            return await self.loop_executor.execute_loop(
                node, context, self._execute_simple_node
            )

        elif node_type == "subworkflow":
            return await self.subworkflow_executor.execute_subworkflow(
                node, context, self.workflow_engine
            )

        else:
            # Delegar a la ejecución normal
            return await self._execute_simple_node(node, context)

    async def _execute_simple_node(self, node: dict, context: dict) -> dict:
        """Ejecuta un nodo simple (no loop ni subworkflow)"""
        # Esta función será llamada por el workflow engine principal
        # Por ahora retornamos un placeholder
        return {"executed": True, "node_type": node.get("type")}


class ParallelExecutor:
    """Ejecutor para nodos en paralelo"""

    @staticmethod
    async def execute_parallel(
        nodes: List[dict], context: dict, execute_func
    ) -> Dict[str, Any]:
        """
        Ejecuta múltiples nodos en paralelo
        """
        tasks = [execute_func(node, context.copy()) for node in nodes]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        combined_results = {}
        errors = []

        for node, result in zip(nodes, results):
            if isinstance(result, Exception):
                errors.append({"node_id": node["id"], "error": str(result)})
            else:
                combined_results[node["id"]] = result

        return {
            "results": combined_results,
            "errors": errors,
            "success": len(errors) == 0,
        }
