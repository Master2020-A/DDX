"""
API endpoints para gestión de workflows de N8N
"""

from fastapi import APIRouter, Depends, HTTPException, status
import httpx
import copy

from app.api.dependencies import get_current_user, get_current_admin
from app.models.usuario import Usuario
from app.core.config import settings

router = APIRouter(tags=["N8N Workflows"])


def _normalize_n8n_api_url(raw: str) -> str:
    """
    Asegura que la URL base apunte al API v1 de n8n.
    Ejemplos:
      - http://localhost:5678        -> http://localhost:5678/api/v1
      - http://localhost:5678/api/v1 -> http://localhost:5678/api/v1
    """
    url = (raw or "").strip().rstrip("/")
    if not url:
        return ""
    if not url.endswith("/api/v1"):
        url = f"{url}/api/v1"
    return url


def _n8n_editor_base_from_api_url(api_url: str) -> str:
    """
    Convierte base API -> base UI:
      http://host:5678/api/v1 -> http://host:5678
    """
    return api_url.replace("/api/v1", "").rstrip("/")


@router.post("/create-from-template")
async def crear_workflow_desde_template(
    template_name: str,
    workflow_name: str,
    current_user: Usuario = Depends(get_current_user),
):
    """
    Crear un workflow en N8N desde un template predefinido
    """
    n8n_api_url = _normalize_n8n_api_url(getattr(settings, "N8N_API_URL", "") or "")
    n8n_api_key = (getattr(settings, "N8N_API_KEY", "") or "").strip()

    if not n8n_api_url or not n8n_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="N8N API no configurada (revisa N8N_API_URL y N8N_API_KEY).",
        )

    backend_url = (
        getattr(settings, "BACKEND_URL", "") or "http://localhost:8612"
    ).rstrip("/")

    # Templates de workflows predefinidos
    templates = {
        "alerta_critica": {
            "name": workflow_name,
            "nodes": [
                {
                    "parameters": {
                        # Debe coincidir con tu emisor: laboratorio.resultado_critico -> laboratorio-resultado_critico
                        "path": "laboratorio-resultado_critico",
                        "httpMethod": "POST",
                        "responseMode": "onReceived",
                        "options": {},
                    },
                    "name": "Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [250, 300],
                },
                {
                    "parameters": {
                        # Llega como { event, data, timestamp, source, priority }
                        "functionCode": (
                            "const data = $input.item.json.data;\n\n"
                            "return {\n"
                            "  json: {\n"
                            "    paciente_nombre: data.paciente_nombre,\n"
                            "    parametro: data.parametro,\n"
                            "    valor: data.valor,\n"
                            "    nivel: data.nivel,\n"
                            "    rango_normal: data.rango_normal,\n"
                            "    medico_email: data.medico_email,\n"
                            "    urgencia: 'CRÍTICO'\n"
                            "  }\n"
                            "};"
                        )
                    },
                    "name": "Formatear Datos",
                    "type": "n8n-nodes-base.function",
                    "typeVersion": 1,
                    "position": [450, 300],
                },
                {
                    "parameters": {
                        "fromEmail": "noreply@ddx.com",
                        "toEmail": "={{$json.medico_email}}",
                        "subject": "ALERTA CRÍTICA - {{$json.paciente_nombre}}",
                        "text": (
                            "ALERTA MÉDICA CRÍTICA\n\n"
                            "Paciente: {{$json.paciente_nombre}}\n"
                            "Parámetro: {{$json.parametro}}\n"
                            "Valor: {{$json.valor}}\n"
                            "Nivel: {{$json.nivel}}\n"
                            "Rango normal: {{$json.rango_normal}}\n\n"
                            "Requiere atención inmediata."
                        ),
                    },
                    "name": "Enviar Email",
                    "type": "n8n-nodes-base.emailSend",
                    "typeVersion": 1,
                    "position": [650, 300],
                },
            ],
            "connections": {
                "Webhook": {
                    "main": [[{"node": "Formatear Datos", "type": "main", "index": 0}]]
                },
                "Formatear Datos": {
                    "main": [[{"node": "Enviar Email", "type": "main", "index": 0}]]
                },
            },
            "settings": {},
            # NO "active": False (en tu n8n API v1 da 400 porque es read-only)
        },
        "recordatorio_citas": {
            "name": workflow_name,
            "nodes": [
                {
                    "parameters": {
                        "rule": {
                            "interval": [
                                {"field": "cronExpression", "expression": "0 8 * * *"}
                            ]
                        }
                    },
                    "name": "Schedule Trigger",
                    "type": "n8n-nodes-base.scheduleTrigger",
                    "typeVersion": 1,
                    "position": [250, 300],
                },
                {
                    "parameters": {
                        "url": f"{backend_url}/api/citas/proximas",
                        "authentication": "genericCredentialType",
                        "genericAuthType": "httpHeaderAuth",
                        "options": {
                            "queryParameters": {
                                "parameters": [{"name": "dias", "value": "1"}]
                            }
                        },
                    },
                    "name": "Obtener Citas",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 1,
                    "position": [450, 300],
                },
                {
                    "parameters": {
                        "functionCode": (
                            "const cita = $input.item.json;\n"
                            "const fecha = new Date(cita.fecha_hora);\n"
                            "const fechaFormateada = fecha.toLocaleDateString('es-MX');\n\n"
                            "return {\n"
                            "  json: {\n"
                            "    paciente_nombre: cita.paciente_nombre,\n"
                            "    paciente_email: cita.paciente_email,\n"
                            "    fecha_formateada: fechaFormateada,\n"
                            "    medico_nombre: cita.medico_nombre\n"
                            "  }\n"
                            "};"
                        )
                    },
                    "name": "Formatear Mensaje",
                    "type": "n8n-nodes-base.function",
                    "typeVersion": 1,
                    "position": [650, 300],
                },
                {
                    "parameters": {
                        "fromEmail": "noreply@ddx.com",
                        "toEmail": "={{$json.paciente_email}}",
                        "subject": "Recordatorio de Cita Médica - Mañana",
                        "text": (
                            "Estimado(a) {{$json.paciente_nombre}},\n\n"
                            "Le recordamos su cita médica programada para mañana:\n\n"
                            "Fecha: {{$json.fecha_formateada}}\n"
                            "Médico: {{$json.medico_nombre}}\n\n"
                            "Por favor, llegue 10 minutos antes.\n\n"
                            "Saludos,\n"
                            "Equipo DDX"
                        ),
                    },
                    "name": "Enviar Recordatorio",
                    "type": "n8n-nodes-base.emailSend",
                    "typeVersion": 1,
                    "position": [850, 300],
                },
            ],
            "connections": {
                "Schedule Trigger": {
                    "main": [[{"node": "Obtener Citas", "type": "main", "index": 0}]]
                },
                "Obtener Citas": {
                    "main": [
                        [{"node": "Formatear Mensaje", "type": "main", "index": 0}]
                    ]
                },
                "Formatear Mensaje": {
                    "main": [
                        [{"node": "Enviar Recordatorio", "type": "main", "index": 0}]
                    ]
                },
            },
            "settings": {},
        },
        "notificacion_resultados": {
            "name": workflow_name,
            "nodes": [
                {
                    "parameters": {
                        "path": "laboratorio-completado",
                        "httpMethod": "POST",
                        "responseMode": "onReceived",
                        "options": {},
                    },
                    "name": "Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [250, 300],
                },
                {
                    "parameters": {
                        "functionCode": (
                            "const data = $input.item.json.data;\n"
                            "const enlace = `http://localhost:3000/resultados/${data.resultado_id}`;\n\n"
                            "return {\n"
                            "  json: {\n"
                            "    paciente_id: data.paciente_id,\n"
                            "    paciente_email: data.paciente_email,\n"
                            "    tipo_prueba: data.tipo_prueba,\n"
                            "    enlace_seguro: enlace\n"
                            "  }\n"
                            "};"
                        )
                    },
                    "name": "Crear Enlace",
                    "type": "n8n-nodes-base.function",
                    "typeVersion": 1,
                    "position": [450, 300],
                },
                {
                    "parameters": {
                        "fromEmail": "noreply@ddx.com",
                        "toEmail": "={{$json.paciente_email}}",
                        "subject": "Sus Resultados de Laboratorio están Listos",
                        "text": (
                            "Sus resultados de laboratorio ya están disponibles:\n\n"
                            "Tipo de Prueba: {{$json.tipo_prueba}}\n\n"
                            "Ver Resultados: {{$json.enlace_seguro}}\n\n"
                            "Saludos,\n"
                            "Equipo DDX"
                        ),
                    },
                    "name": "Enviar Notificación",
                    "type": "n8n-nodes-base.emailSend",
                    "typeVersion": 1,
                    "position": [650, 300],
                },
            ],
            "connections": {
                "Webhook": {
                    "main": [[{"node": "Crear Enlace", "type": "main", "index": 0}]]
                },
                "Crear Enlace": {
                    "main": [
                        [{"node": "Enviar Notificación", "type": "main", "index": 0}]
                    ]
                },
            },
            "settings": {},
        },
    }

    if template_name not in templates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Template '{template_name}' no encontrado. "
                f"Templates disponibles: {', '.join(templates.keys())}"
            ),
        )

    # Copia profunda y sanitización (por si alguien reintroduce "active")
    workflow_data = copy.deepcopy(templates[template_name])
    workflow_data.pop("active", None)

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{n8n_api_url}/workflows",
                headers={"X-N8N-API-KEY": n8n_api_key},
                json=workflow_data,
            )
            response.raise_for_status()
            workflow = response.json()

        editor_base = _n8n_editor_base_from_api_url(n8n_api_url)
        workflow_id = workflow.get("id")

        return {
            "success": True,
            "workflow_id": workflow_id,
            "workflow_name": workflow.get("name"),
            "message": f"Workflow '{workflow_name}' creado exitosamente desde template '{template_name}'",
            "edit_url": f"{editor_base}/workflow/{workflow_id}",
        }

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"n8n respondió con error {e.response.status_code}: {e.response.text}",
        )
    except (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout) as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"No se pudo conectar con n8n: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado creando workflow en n8n: {str(e)}",
        )


@router.get("/templates")
async def obtener_templates_disponibles(
    current_user: Usuario = Depends(get_current_user),
):
    return {
        "templates": [
            {
                "id": "alerta_critica",
                "name": "🚨 Alertas Médicas Críticas",
                "description": "Envía alertas cuando hay resultados de laboratorio críticos",
                "category": "Laboratorio",
                "nodes": 3,
                "trigger": "Webhook: laboratorio.resultado_critico → /webhook/laboratorio-resultado_critico",
            },
            {
                "id": "recordatorio_citas",
                "name": "📅 Recordatorios de Citas",
                "description": "Envía recordatorios automáticos 24 horas antes de las citas",
                "category": "Citas",
                "nodes": 4,
                "trigger": "Schedule: Diario a las 8:00 AM",
            },
            {
                "id": "notificacion_resultados",
                "name": "🧪 Notificación de Resultados",
                "description": "Notifica cuando los resultados están listos",
                "category": "Laboratorio",
                "nodes": 3,
                "trigger": "Webhook: laboratorio.completado → /webhook/laboratorio-completado",
            },
        ]
    }


@router.delete("/{workflow_id}")
async def eliminar_workflow(
    workflow_id: str,
    current_admin: Usuario = Depends(get_current_admin),
):
    n8n_api_url = _normalize_n8n_api_url(getattr(settings, "N8N_API_URL", "") or "")
    n8n_api_key = (getattr(settings, "N8N_API_KEY", "") or "").strip()

    if not n8n_api_url or not n8n_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="N8N API no configurada (revisa N8N_API_URL y N8N_API_KEY).",
        )

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.delete(
                f"{n8n_api_url}/workflows/{workflow_id}",
                headers={"X-N8N-API-KEY": n8n_api_key},
            )
            response.raise_for_status()

        return {
            "success": True,
            "message": f"Workflow {workflow_id} eliminado exitosamente",
        }

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"n8n respondió con error {e.response.status_code}: {e.response.text}",
        )
    except (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout) as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"No se pudo conectar con n8n: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado eliminando workflow en n8n: {str(e)}",
        )
