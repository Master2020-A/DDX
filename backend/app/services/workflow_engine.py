"""
Motor de Ejecución de Workflows
Orquesta la ejecución de flujos de trabajo visuales con agentes IA
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.workflow import (
    Workflow,
    WorkflowExecution,
    AIAgent,
    ExecutionStatus,
    NodeType,
)
from app.services.ai_agent_service import AIAgentService

logger = logging.getLogger(__name__)

MAX_NODE_VISITS = 10
MAX_EXECUTION_DEPTH = 200


class WorkflowEngine:
    """Motor de ejecución de workflows"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_service = AIAgentService()

    async def execute_workflow(
        self,
        workflow_id: str,
        input_data: Dict[str, Any],
        triggered_by: str = "manual",
        user_id: Optional[UUID] = None,
    ) -> WorkflowExecution:
        """
        Ejecuta un workflow completo

        Args:
            workflow_id: ID del workflow a ejecutar
            input_data: Datos de entrada
            triggered_by: Origen de la ejecución
            user_id: ID del usuario que ejecuta

        Returns:
            WorkflowExecution con los resultados
        """
        # Cargar workflow usando SQL directo para evitar problemas de relaciones ORM
        from sqlalchemy import text

        result = await self.db.execute(
            text(
                """
                SELECT id, workflow_id, name, nodes, edges, variables, config
                FROM workflows 
                WHERE workflow_id = :wid
            """
            ),
            {"wid": workflow_id},
        )
        workflow_row = result.fetchone()

        if not workflow_row:
            raise ValueError(f"Workflow '{workflow_id}' no encontrado")

        # Crear objeto simple con los datos del workflow
        import json

        class WorkflowData:
            def __init__(self, row):
                self.id = row.id
                self.workflow_id = row.workflow_id
                self.name = row.name
                self.nodes = (
                    row.nodes
                    if isinstance(row.nodes, list)
                    else json.loads(row.nodes)
                    if row.nodes
                    else []
                )
                self.edges = (
                    row.edges
                    if isinstance(row.edges, list)
                    else json.loads(row.edges)
                    if row.edges
                    else []
                )
                self.variables = (
                    row.variables
                    if isinstance(row.variables, dict)
                    else json.loads(row.variables)
                    if row.variables
                    else {}
                )
                self.config = (
                    row.config
                    if isinstance(row.config, dict)
                    else json.loads(row.config)
                    if row.config
                    else {}
                )

        workflow = WorkflowData(workflow_row)

        # Crear registro de ejecución
        execution = WorkflowExecution(
            workflow_id=workflow.id,
            input_data=input_data,
            status=ExecutionStatus.RUNNING,
            triggered_by=triggered_by,
            triggered_by_user_id=user_id,
            context={"variables": workflow.variables or {}},
        )

        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)

        start_time = datetime.utcnow()

        try:
            # Ejecutar workflow
            logger.info(f"Iniciando ejecución de workflow '{workflow_id}'")

            # Encontrar nodo de inicio
            start_node = self._find_start_node(workflow.nodes)
            if not start_node:
                raise ValueError("No se encontró nodo de inicio en el workflow")

            # Ejecutar desde el nodo de inicio
            context = {
                "input": input_data,
                "variables": workflow.variables or {},
                "results": {},
            }

            await self._execute_from_node(
                workflow=workflow,
                execution=execution,
                current_node=start_node,
                context=context,
            )

            # Marcar como completado
            execution.status = ExecutionStatus.COMPLETED
            execution.output_data = context.get("output", {})

            logger.info(f"Workflow '{workflow_id}' completado exitosamente")

        except Exception as e:
            logger.error(
                f"Error ejecutando workflow '{workflow_id}': {e}", exc_info=True
            )
            execution.status = ExecutionStatus.FAILED
            execution.error = str(e)

        finally:
            # Calcular duración
            end_time = datetime.utcnow()
            execution.completed_at = end_time
            execution.duration_ms = int((end_time - start_time).total_seconds() * 1000)
            execution.context = self._sanitize_context(context)

            await self.db.commit()
            await self.db.refresh(execution)

        return execution

    async def _execute_from_node(
        self,
        workflow: Workflow,
        execution: WorkflowExecution,
        current_node: Dict[str, Any],
        context: Dict[str, Any],
        depth: int = 0,
    ):
        """Ejecuta un nodo y continúa con los siguientes"""

        if depth > MAX_EXECUTION_DEPTH:
            raise ValueError("Límite de profundidad de workflow excedido")

        node_id = current_node["id"]
        node_type = current_node["type"]

        visit_counts = context.setdefault("_visit_counts", {})
        visit_counts[node_id] = visit_counts.get(node_id, 0) + 1
        if visit_counts[node_id] > MAX_NODE_VISITS:
            raise ValueError(
                f"Detección de bucle en nodo '{node_id}'. Revisa las conexiones del workflow"
            )

        logger.info(f"Ejecutando nodo '{node_id}' de tipo '{node_type}'")

        # Actualizar nodo actual en ejecución
        execution.current_node_id = node_id
        await self.db.commit()

        # Ejecutar según tipo de nodo
        if node_type == NodeType.START.value:
            result = {"status": "started"}

        elif node_type == NodeType.END.value:
            result = {"status": "completed"}
            context["output"] = context.get("results", {})
            return  # Fin del workflow

        elif node_type == NodeType.AGENT.value:
            result = await self._execute_agent_node(current_node, context, workflow)

        elif node_type == NodeType.CONDITION.value:
            result = await self._execute_condition_node(current_node, context)

        elif node_type == NodeType.ACTION.value:
            result = await self._execute_action_node(current_node, context)

        elif node_type == NodeType.FORM.value:
            result = await self._execute_form_node(current_node, context)

        elif node_type == NodeType.API_CALL.value:
            result = await self._execute_api_call_node(current_node, context)

        elif node_type == NodeType.NOTIFICATION.value:
            result = await self._execute_notification_node(current_node, context)

        elif node_type == NodeType.DELAY.value:
            result = await self._execute_delay_node(current_node, context)

        else:
            result = {
                "status": "skipped",
                "reason": f"Tipo de nodo '{node_type}' no soportado",
            }

        # Guardar resultado del nodo
        if execution.node_results is None:
            execution.node_results = {}
        execution.node_results[node_id] = result
        context["results"][node_id] = result

        # Agregar log
        if execution.logs is None:
            execution.logs = []
        execution.logs.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "node_id": node_id,
                "node_type": node_type,
                "result": result,
            }
        )

        await self.db.commit()

        # Encontrar siguiente(s) nodo(s)
        next_nodes = self._find_next_nodes(workflow.edges, node_id, result)

        # Ejecutar siguiente(s) nodo(s)
        for next_node_id in next_nodes:
            next_node = self._find_node_by_id(workflow.nodes, next_node_id)
            if next_node:
                await self._execute_from_node(
                    workflow, execution, next_node, context, depth + 1
                )

    async def _execute_agent_node(
        self, node: Dict[str, Any], context: Dict[str, Any], workflow: Workflow
    ) -> Dict[str, Any]:
        """Ejecuta un nodo de agente IA"""

        node_data = node.get("data", {})
        agent_id = node_data.get("agent_id")

        if not agent_id:
            return {"error": "No se especificó agent_id"}

        # Cargar configuración del agente usando SQL directo
        from sqlalchemy import text

        result = await self.db.execute(
            text(
                """
                SELECT id, agent_id, name, model, temperature, max_tokens,
                       system_prompt, user_prompt_template, role
                FROM ai_agents
                WHERE workflow_id = :wid AND agent_id = :aid
            """
            ),
            {"wid": workflow.id, "aid": agent_id},
        )
        agent_row = result.fetchone()

        if not agent_row:
            return {"error": f"Agente '{agent_id}' no encontrado"}

        # Crear objeto simple con los datos del agente
        class AgentData:
            def __init__(self, row):
                self.id = row.id
                self.agent_id = row.agent_id
                self.name = row.name
                self.model = type("Model", (), {"value": row.model})()  # Mock enum
                self.temperature = row.temperature
                self.max_tokens = row.max_tokens
                self.system_prompt = row.system_prompt
                self.user_prompt_template = row.user_prompt_template
                self.role = row.role

        agent = AgentData(agent_row)

        # Preparar input para el agente
        agent_input = node_data.get("input", context.get("input", {}))

        # Ejecutar agente
        try:
            response = await self.ai_service.execute_agent(
                agent=agent, input_data=agent_input, context=context
            )

            return {
                "status": "success",
                "output": response,
                "agent_id": agent_id,
                "model": agent.model.value,
            }

        except Exception as e:
            logger.error(f"Error ejecutando agente '{agent_id}': {e}")
            return {"status": "error", "error": str(e), "agent_id": agent_id}

    async def _execute_condition_node(
        self, node: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ejecuta un nodo de condición"""

        node_data = node.get("data", {})
        condition_type = node_data.get("condition_type", "simple")

        if condition_type == "simple":
            # Condición simple: comparar un campo
            field = node_data.get("field")
            operator = node_data.get("operator", "==")
            value = node_data.get("value")

            # Obtener valor del campo del contexto
            field_value = self._get_field_value(context, field)

            # Evaluar condición
            result = self._evaluate_condition(field_value, operator, value)

            return {
                "status": "success",
                "result": result,
                "field": field,
                "operator": operator,
                "value": value,
                "field_value": field_value,
            }

        elif condition_type == "expression":
            # Condición con expresión
            expression = node_data.get("expression")
            # TODO: Evaluar expresión de forma segura
            return {"status": "not_implemented", "type": "expression"}

        return {"status": "error", "error": "Tipo de condición no soportado"}

    async def _execute_action_node(
        self, node: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ejecuta un nodo de acción"""

        node_data = node.get("data", {})
        action_type = node_data.get("action_type")

        # Acciones disponibles
        if action_type == "set_variable":
            variable_name = node_data.get("variable_name")
            variable_value = node_data.get("variable_value")
            context["variables"][variable_name] = variable_value
            return {
                "status": "success",
                "action": "set_variable",
                "variable": variable_name,
            }

        elif action_type == "create_record":
            # TODO: Crear registro en base de datos
            return {"status": "not_implemented", "action": "create_record"}

        elif action_type == "update_record":
            # TODO: Actualizar registro
            return {"status": "not_implemented", "action": "update_record"}

        elif action_type == "send_notification":
            # TODO: Enviar notificación
            return {"status": "not_implemented", "action": "send_notification"}

        return {"status": "error", "error": f"Acción '{action_type}' no soportada"}

    async def _execute_form_node(
        self, node: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ejecuta un nodo de formulario"""
        # Los formularios requieren interacción del usuario
        # Por ahora retornamos los datos del formulario del contexto
        node_data = node.get("data", {})
        form_id = node_data.get("form_id")

        # Buscar datos del formulario en el input
        form_data = context.get("input", {}).get(f"form_{form_id}", {})

        return {"status": "success", "form_id": form_id, "data": form_data}

    async def _execute_api_call_node(
        self, node: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ejecuta un nodo de llamada API"""
        # TODO: Implementar llamadas HTTP
        return {"status": "not_implemented", "type": "api_call"}

    async def _execute_notification_node(
        self, node: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ejecuta un nodo de notificación"""
        node_data = node.get("data", {})
        notification_type = node_data.get("notification_type", "email")

        # TODO: Implementar envío de notificaciones
        return {"status": "not_implemented", "type": notification_type}

    async def _execute_delay_node(
        self, node: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ejecuta un nodo de delay"""
        node_data = node.get("data", {})
        delay_ms = node_data.get("delay_ms", 1000)

        await asyncio.sleep(delay_ms / 1000)

        return {"status": "success", "delay_ms": delay_ms}

    def _find_start_node(self, nodes: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Encuentra el nodo de inicio"""
        for node in nodes:
            if node.get("type") == NodeType.START.value:
                return node
        return None

    def _find_node_by_id(
        self, nodes: List[Dict[str, Any]], node_id: str
    ) -> Optional[Dict[str, Any]]:
        """Encuentra un nodo por su ID"""
        for node in nodes:
            if node.get("id") == node_id:
                return node
        return None

    def _find_next_nodes(
        self,
        edges: List[Dict[str, Any]],
        current_node_id: str,
        current_result: Dict[str, Any],
    ) -> List[str]:
        """Encuentra los siguientes nodos a ejecutar"""
        next_nodes = []

        for edge in edges:
            if edge.get("source") == current_node_id:
                # Verificar si hay condición en el edge
                edge_condition = edge.get("condition")

                if edge_condition:
                    # Evaluar condición del edge
                    if self._evaluate_edge_condition(edge_condition, current_result):
                        next_nodes.append(edge.get("target"))
                else:
                    # Sin condición, siempre seguir
                    next_nodes.append(edge.get("target"))

        return next_nodes

    def _evaluate_edge_condition(self, condition: str, result: Dict[str, Any]) -> bool:
        """Evalúa la condición de un edge"""
        # Condiciones simples basadas en el resultado del nodo
        if condition == "success":
            return result.get("status") == "success"
        elif condition == "error":
            return result.get("status") == "error"
        elif condition == "true":
            return result.get("result") is True
        elif condition == "false":
            return result.get("result") is False

        # Por defecto, siempre continuar
        return True

    def _get_field_value(self, context: Dict[str, Any], field_path: str) -> Any:
        """Obtiene el valor de un campo del contexto usando dot notation"""
        if not field_path:
            return None

        parts = field_path.split(".")
        value = context

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None

        return value

    def _evaluate_condition(self, left: Any, operator: str, right: Any) -> bool:
        """Evalúa una condición simple"""
        if operator == "==":
            return left == right
        elif operator == "!=":
            return left != right
        elif operator == ">":
            return left > right
        elif operator == ">=":
            return left >= right
        elif operator == "<":
            return left < right
        elif operator == "<=":
            return left <= right
        elif operator == "contains":
            return right in left if left else False
        elif operator == "not_contains":
            return right not in left if left else True

        return False

    def _sanitize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(context, dict):
            return {}
        sanitized = dict(context)
        sanitized.pop("_visit_counts", None)
        return sanitized
