import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal
import json


async def crear_workflow_ejemplo():
    """Crear un workflow de ejemplo: Triaje Inteligente"""

    async with AsyncSessionLocal() as db:
        # Definir el workflow de triaje inteligente
        workflow_data = {
            "workflow_id": "triaje-inteligente-demo",
            "name": "Triaje Inteligente - Demo",
            "description": "Sistema de clasificación automática de urgencia de pacientes usando IA",
            "category": "clinical",
            "status": "active",
            "version": "1.0.0",
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start",
                    "position": {"x": 100, "y": 200},
                    "data": {"label": "Inicio"},
                },
                {
                    "id": "agent-triaje",
                    "type": "agent",
                    "position": {"x": 300, "y": 200},
                    "data": {
                        "label": "Agente de Triaje",
                        "agent_id": "triaje-gpt4",
                        "model": "gpt-4",
                        "temperature": 70,
                        "max_tokens": 1000,
                    },
                },
                {
                    "id": "condition-urgencia",
                    "type": "condition",
                    "position": {"x": 550, "y": 200},
                    "data": {
                        "label": "¿Urgencia Alta?",
                        "field": "urgencia",
                        "operator": "==",
                        "value": "alta",
                        "condition": "urgencia === 'alta'",
                    },
                },
                {
                    "id": "action-urgente",
                    "type": "action",
                    "position": {"x": 800, "y": 100},
                    "data": {
                        "label": "Crear Consulta Urgente",
                        "action_type": "create_record",
                        "config": {"table": "consultas", "priority": "urgente"},
                    },
                },
                {
                    "id": "action-normal",
                    "type": "action",
                    "position": {"x": 800, "y": 300},
                    "data": {
                        "label": "Agendar Consulta Normal",
                        "action_type": "create_record",
                        "config": {"table": "consultas", "priority": "normal"},
                    },
                },
                {
                    "id": "end-1",
                    "type": "end",
                    "position": {"x": 1050, "y": 200},
                    "data": {"label": "Fin"},
                },
            ],
            "edges": [
                {
                    "id": "e1",
                    "source": "start-1",
                    "target": "agent-triaje",
                    "label": "",
                },
                {
                    "id": "e2",
                    "source": "agent-triaje",
                    "target": "condition-urgencia",
                    "label": "",
                },
                {
                    "id": "e3",
                    "source": "condition-urgencia",
                    "target": "action-urgente",
                    "label": "Sí",
                    "condition": "true",
                },
                {
                    "id": "e4",
                    "source": "condition-urgencia",
                    "target": "action-normal",
                    "label": "No",
                    "condition": "false",
                },
                {
                    "id": "e5",
                    "source": "action-urgente",
                    "target": "end-1",
                    "label": "",
                },
                {"id": "e6", "source": "action-normal", "target": "end-1", "label": ""},
            ],
            "config": {"timeout": 300, "retry_on_error": True, "max_retries": 3},
            "variables": {"default_priority": "normal", "notification_enabled": True},
            "icon": "🏥",
            "color": "#3b82f6",
            "tags": ["triaje", "urgencias", "ia", "gpt-4"],
        }

        # Verificar si ya existe
        check_result = await db.execute(
            text("SELECT COUNT(*) as count FROM workflows WHERE workflow_id = :wid"),
            {"wid": workflow_data["workflow_id"]},
        )
        exists = check_result.fetchone().count > 0

        if exists:
            print(
                f"⚠️  Workflow '{workflow_data['workflow_id']}' ya existe. Actualizando..."
            )

            # Actualizar workflow existente
            await db.execute(
                text(
                    """
                    UPDATE workflows 
                    SET name = :name,
                        description = :description,
                        category = :category,
                        status = :status,
                        version = :version,
                        nodes = CAST(:nodes AS jsonb),
                        edges = CAST(:edges AS jsonb),
                        config = CAST(:config AS jsonb),
                        variables = CAST(:variables AS jsonb),
                        icon = :icon,
                        color = :color,
                        tags = CAST(:tags AS jsonb),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE workflow_id = :workflow_id
                """
                ),
                {
                    "workflow_id": workflow_data["workflow_id"],
                    "name": workflow_data["name"],
                    "description": workflow_data["description"],
                    "category": workflow_data["category"],
                    "status": workflow_data["status"],
                    "version": workflow_data["version"],
                    "nodes": json.dumps(workflow_data["nodes"]),
                    "edges": json.dumps(workflow_data["edges"]),
                    "config": json.dumps(workflow_data["config"]),
                    "variables": json.dumps(workflow_data["variables"]),
                    "icon": workflow_data["icon"],
                    "color": workflow_data["color"],
                    "tags": json.dumps(workflow_data["tags"]),
                },
            )
        else:
            # Crear nuevo workflow
            await db.execute(
                text(
                    """
                    INSERT INTO workflows (
                        id, workflow_id, name, description, category, status, version,
                        nodes, edges, config, variables, icon, color, tags,
                        created_at, updated_at
                    ) VALUES (
                        gen_random_uuid(), :workflow_id, :name, :description, :category, 
                        :status, :version, CAST(:nodes AS jsonb), CAST(:edges AS jsonb), 
                        CAST(:config AS jsonb), CAST(:variables AS jsonb), :icon, :color, CAST(:tags AS jsonb),
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                """
                ),
                {
                    "workflow_id": workflow_data["workflow_id"],
                    "name": workflow_data["name"],
                    "description": workflow_data["description"],
                    "category": workflow_data["category"],
                    "status": workflow_data["status"],
                    "version": workflow_data["version"],
                    "nodes": json.dumps(workflow_data["nodes"]),
                    "edges": json.dumps(workflow_data["edges"]),
                    "config": json.dumps(workflow_data["config"]),
                    "variables": json.dumps(workflow_data["variables"]),
                    "icon": workflow_data["icon"],
                    "color": workflow_data["color"],
                    "tags": json.dumps(workflow_data["tags"]),
                },
            )

        await db.commit()

        # Obtener el UUID del workflow recién creado
        workflow_uuid_result = await db.execute(
            text("SELECT id FROM workflows WHERE workflow_id = :wid"),
            {"wid": workflow_data["workflow_id"]},
        )
        workflow_uuid = workflow_uuid_result.fetchone().id

        # Crear el agente IA asociado
        agent_data = {
            "workflow_uuid": workflow_uuid,
            "agent_id": "triaje-gpt4",
            "name": "Agente de Triaje GPT-4",
            "description": "Analiza síntomas y clasifica la urgencia del paciente",
            "model": "gpt-4",
            "temperature": 70,
            "max_tokens": 1000,
            "system_prompt": """Eres un médico experto en triaje de urgencias.

Tu tarea es analizar los síntomas del paciente y clasificar la urgencia en:
- alta: Requiere atención inmediata (riesgo vital, dolor intenso, trauma severo)
- media: Puede esperar 30-60 minutos
- baja: No urgente, puede esperar más de 1 hora

Considera:
- Signos vitales (presión, frecuencia cardíaca, temperatura)
- Síntomas reportados
- Antecedentes médicos
- Edad del paciente

Responde SIEMPRE en formato JSON:
{
  "urgencia": "alta|media|baja",
  "razon": "Explicación breve de la clasificación",
  "recomendaciones": ["lista", "de", "recomendaciones"],
  "tiempo_espera_estimado": "minutos"
}""",
            "user_prompt_template": """Paciente:
- Nombre: {{nombre}}
- Edad: {{edad}} años
- Síntomas: {{sintomas}}
- Signos vitales: 
  * Presión: {{presion}}
  * Frecuencia cardíaca: {{frecuencia_cardiaca}} bpm
  * Temperatura: {{temperatura}}°C
- Antecedentes: {{antecedentes}}

Por favor, clasifica la urgencia de este paciente.""",
            "role": "triaje",
            "icon": "🏥",
            "color": "#3b82f6",
        }

        # Verificar si el agente ya existe
        check_agent = await db.execute(
            text(
                """
                SELECT COUNT(*) as count 
                FROM ai_agents 
                WHERE workflow_id = :wid AND agent_id = :aid
            """
            ),
            {"wid": workflow_uuid, "aid": agent_data["agent_id"]},
        )
        agent_exists = check_agent.fetchone().count > 0

        if agent_exists:
            # Actualizar agente existente
            await db.execute(
                text(
                    """
                    UPDATE ai_agents 
                    SET name = :name,
                        description = :description,
                        model = :model,
                        temperature = :temperature,
                        max_tokens = :max_tokens,
                        system_prompt = :system_prompt,
                        user_prompt_template = :user_prompt_template,
                        role = :role,
                        icon = :icon,
                        color = :color,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE workflow_id = :workflow_uuid AND agent_id = :agent_id
                """
                ),
                {
                    "workflow_uuid": agent_data["workflow_uuid"],
                    "agent_id": agent_data["agent_id"],
                    "name": agent_data["name"],
                    "description": agent_data["description"],
                    "model": agent_data["model"],
                    "temperature": agent_data["temperature"],
                    "max_tokens": agent_data["max_tokens"],
                    "system_prompt": agent_data["system_prompt"],
                    "user_prompt_template": agent_data["user_prompt_template"],
                    "role": agent_data["role"],
                    "icon": agent_data["icon"],
                    "color": agent_data["color"],
                },
            )
        else:
            # Crear nuevo agente
            await db.execute(
                text(
                    """
                    INSERT INTO ai_agents (
                        id, workflow_id, agent_id, name, description, model,
                        temperature, max_tokens, system_prompt, user_prompt_template,
                        role, icon, color, created_at, updated_at
                    ) VALUES (
                        gen_random_uuid(), :workflow_uuid, :agent_id, :name, :description, :model,
                        :temperature, :max_tokens, :system_prompt, :user_prompt_template,
                        :role, :icon, :color, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                """
                ),
                {
                    "workflow_uuid": agent_data["workflow_uuid"],
                    "agent_id": agent_data["agent_id"],
                    "name": agent_data["name"],
                    "description": agent_data["description"],
                    "model": agent_data["model"],
                    "temperature": agent_data["temperature"],
                    "max_tokens": agent_data["max_tokens"],
                    "system_prompt": agent_data["system_prompt"],
                    "user_prompt_template": agent_data["user_prompt_template"],
                    "role": agent_data["role"],
                    "icon": agent_data["icon"],
                    "color": agent_data["color"],
                },
            )

        await db.commit()

        print("✅ Workflow de ejemplo creado exitosamente!")
        print(f"\n📋 Detalles del Workflow:")
        print(f"   ID: {workflow_data['workflow_id']}")
        print(f"   Nombre: {workflow_data['name']}")
        print(f"   Descripción: {workflow_data['description']}")
        print(f"   Nodos: {len(workflow_data['nodes'])}")
        print(f"   Conexiones: {len(workflow_data['edges'])}")
        print(f"   Agente IA: {agent_data['name']} ({agent_data['model']})")
        print(f"\n🎯 Accede a: http://localhost:3000/workflows")
        print(f"   Verás el workflow '{workflow_data['name']}' listo para usar")
        print(f"\n💡 Puedes:")
        print(f"   - Ver el workflow en el canvas visual")
        print(f"   - Editarlo arrastrando nodos")
        print(f"   - Ejecutarlo con datos de prueba")


if __name__ == "__main__":
    asyncio.run(crear_workflow_ejemplo())
